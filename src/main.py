"""
Main entry point for the card game.
"""
import os
import sys
from models.card import Card
from models.player import Player
from models.deck import Deck
from models.game_state import GameState, GamePhase
from controllers.game_controller import GameController
from controllers.player_controller import PlayerController
from controllers.ai_controller import AIController
from utils.resource_loader import ResourceLoader
from utils.save_manager import SaveManager
from constants import PLAYER_STARTING_HAND_SIZE


def initialize_game():
    """
    Initialize the game by loading resources and setting up players.
    
    Returns:
        tuple: Containing game controllers and card database
    """
    print("Initializing game...")
    
    # Load cards
    card_database = ResourceLoader.load_cards()
    print(f"Loaded {len(card_database)} cards.")
    
    # Check if we have a saved player
    player = None
    if SaveManager.player_exists():
        player = SaveManager.load_player(card_database)
        print(f"Loaded player: {player.name}")
    
    if player is None:
        # Create a new player with a starter deck
        print("Creating new player...")
        starter_deck = Deck.create_starter_deck(card_database)
        player = Player("Player", starter_deck)
        player.credits = 50  # Give some starting credits
        SaveManager.save_player(player)
    
    # Create an AI opponent
    ai_deck = Deck.create_starter_deck(card_database)
    opponent = Player("AI Opponent", ai_deck)
    
    # Create game state
    game_state = GameState(player, opponent)
    
    # Initialize controllers
    game_controller = GameController(game_state)
    player_controller = PlayerController(game_state)
    ai_controller = AIController(game_state)
    
    # Start a new game
    game_controller.start_game()
    
    # Draw starting hands
    player.draw_starting_hand(PLAYER_STARTING_HAND_SIZE)
    opponent.draw_starting_hand(PLAYER_STARTING_HAND_SIZE)
    
    print("Game initialized!")
    return game_state, game_controller, player_controller, ai_controller, card_database


def display_game_state(game_state):
    """
    Display the current game state (simplified text version).
    
    Args:
        game_state (GameState): Current game state
    """
    print("\n" + "=" * 50)
    print(f"Turn {game_state.turn_number} | Phase: {game_state.current_phase.name}")
    print(f"Current Player: {game_state.current_player.name}")
    print("=" * 50)
    
    # Display player info
    print(f"\nPlayer: {game_state.player.name}")
    print(f"Health: {game_state.player.health}/{game_state.player.max_health} | Energy: {game_state.player.energy}/{game_state.player.max_energy}")
    
    # Display player hand
    print("\nHand:")
    for i, card in enumerate(game_state.player.hand):
        print(f"  {i}: {card.name} (Cost: {card.cost}, ATK: {card.attack}, HP: {card.hp})")
    
    # Display player field
    print("\nField:")
    for i, card in enumerate(game_state.player.field):
        if card:
            print(f"  {i}: {card.name} (ATK: {card.attack}, HP: {card.hp})")
        else:
            print(f"  {i}: Empty")
    
    print("\n" + "-" * 50)
    
    # Display opponent info
    print(f"\nOpponent: {game_state.opponent.name}")
    print(f"Health: {game_state.opponent.health}/{game_state.opponent.max_health} | Energy: {game_state.opponent.energy}/{game_state.opponent.max_energy}")
    
    # Display opponent field
    print("\nField:")
    for i, card in enumerate(game_state.opponent.field):
        if card:
            print(f"  {i}: {card.name} (ATK: {card.attack}, HP: {card.hp})")
        else:
            print(f"  {i}: Empty")
    
    print("\n" + "=" * 50)


def game_loop_with_controllers(
    game_state: GameState,
    game_controller: GameController,
    player_controller: PlayerController,
    ai_controller: AIController
):
    """
    Run the game loop using the controller pattern.
    
    Args:
        game_state (GameState): The game state
        game_controller (GameController): The game controller
        player_controller (PlayerController): The player controller
        ai_controller (AIController): The AI controller
    """
    max_turns = 10  # Set a reasonable limit for demo purposes
    
    # Main game loop
    while not game_state.game_over and game_state.turn_number <= max_turns:
        # Display current state
        display_game_state(game_state)
        
        # Process current phase
        events = game_controller.process_turn()
        
        # Handle events based on current phase
        if game_state.current_phase == GamePhase.DRAW:
            # Just show what happened in draw phase
            for event in events["events"]:
                if event["type"] == "draw":
                    print(f"{event['player']} drew {event['card']}")
                elif event["type"] == "deck_empty":
                    print(f"{event['player']} has no more cards to draw!")
                    
            # Move to play phase
            print(f"Moving to {game_controller.advance_phase().name} phase")
            
        elif game_state.current_phase == GamePhase.PLAY:
            # If AI's turn, let AI play cards
            if game_state.current_player == game_state.opponent:
                ai_results = ai_controller.take_turn()
                
                for event in ai_results["events"]:
                    if event["type"] == "ai_card_played":
                        print(f"AI plays {event['card']} to position {event['field_position']}")
                
                # AI automatically ends play phase
                print(f"AI ends play phase")
                print(f"Moving to {game_controller.advance_phase().name} phase")
            else:
                # Human player's turn - let them play cards
                play_phase_done = False
                
                while not play_phase_done:
                    # Show playable cards
                    playable_cards = player_controller.get_playable_cards(game_state.player)
                    placement_options = player_controller.get_card_placement_options(game_state.player)
                    
                    print("\nPlayable Cards:")
                    for card in playable_cards:
                        status = "✓" if card["playable"] else "✗"
                        print(f"  [{card['index']}] {card['card']} (Cost: {card['cost']}) {status}")
                    
                    print("\nPlacement Options:")
                    for option in placement_options:
                        status = "Empty" if option["available"] else f"Occupied by {option['current_card']}"
                        print(f"  Position {option['index']}: {status}")
                    
                    # Get player input
                    action = input("\nEnter action (p = play card, e = end phase): ").strip().lower()
                    
                    if action == 'p':
                        try:
                            hand_idx = int(input("Enter card index from hand: "))
                            field_idx = int(input("Enter field position: "))
                            
                            result = player_controller.play_card(game_state.player, hand_idx, field_idx)
                            
                            if result["success"]:
                                print(f"Played card successfully: {result['message']}")
                            else:
                                print(f"Failed to play card: {result['message']}")
                                
                        except ValueError:
                            print("Please enter valid numbers")
                    
                    elif action == 'e':
                        result = player_controller.end_play_phase(game_state.player)
                        if result["success"]:
                            play_phase_done = True
                            print(f"Moving to {game_controller.advance_phase().name} phase")
                        else:
                            print(result["message"])
                    
                    else:
                        print("Invalid action")
        
        elif game_state.current_phase == GamePhase.ATTACK:
            # Show attack results
            for event in events["events"]:
                if event["type"] == "card_attack":
                    print(f"{event['attacker']} attacks {event['defender']} for {event['attack_damage']} damage")
                elif event["type"] == "card_counter_attack":
                    print(f"{event['attacker']} counter-attacks {event['defender']} for {event['attack_damage']} damage")
                elif event["type"] == "card_destroyed":
                    print(f"{event['card']} was destroyed!")
                elif event["type"] == "player_damage":
                    print(f"{event['player']} takes {event['damage']} damage from {event['source']}")
                elif event["type"] == "game_over":
                    print(f"Game Over! Winner: {event['winner']}")
                    if "credits_awarded" in event:
                        print(f"{event['player']} received {event['amount']} credits")
            
            # Move to end phase
            if not game_state.game_over:
                print(f"Moving to {game_controller.advance_phase().name} phase")
        
        elif game_state.current_phase == GamePhase.END:
            # End phase is mostly bookkeeping
            print(f"End of turn {game_state.turn_number}")
            print(f"Moving to {game_controller.advance_phase().name} phase")
            
            # Check for game over after turn change
            if game_state.game_over:
                print(f"Game Over! Winner: {game_state.winner.name}")
                break
                
            # Pause between turns for readability
            input("Press Enter to continue to next turn...")
    
    # End of game
    if game_state.turn_number > max_turns:
        print(f"\nReached maximum turns ({max_turns}).")
    
    print("\nFinal game state:")
    display_game_state(game_state)
    print("\nGame complete!")


def main():
    """
    Main function to run the game.
    """
    try:
        # Initialize the game
        game_state, game_controller, player_controller, ai_controller, card_database = initialize_game()
        
        # Run the game
        game_loop_with_controllers(game_state, game_controller, player_controller, ai_controller)
        
        # Save player state
        SaveManager.save_player(game_state.player)
        print("Player progress saved.")
        
    except Exception as e:
        print(f"Error running the game: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())