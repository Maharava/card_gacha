"""
Main entry point for the card game.
"""
import os
import sys
from models.card import Card
from models.player import Player
from models.deck import Deck
from models.game_state import GameState, GamePhase
from utils.resource_loader import ResourceLoader
from utils.save_manager import SaveManager
from constants import PLAYER_STARTING_HAND_SIZE


def initialize_game():
    """
    Initialize the game by loading resources and setting up players.
    
    Returns:
        tuple: Containing game_state, card_database
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
    
    # Draw starting hands
    player.draw_starting_hand(PLAYER_STARTING_HAND_SIZE)
    opponent.draw_starting_hand(PLAYER_STARTING_HAND_SIZE)
    
    print("Game initialized!")
    return game_state, card_database


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


def simple_game_loop(game_state, card_database):
    """
    Run a simple game loop for demonstration purposes.
    
    Args:
        game_state (GameState): The game state
        card_database (dict): Dictionary of all cards
    """
    max_turns = 3  # Just run a few turns for demo
    
    for _ in range(max_turns):
        if game_state.game_over:
            break
            
        # Display current state
        display_game_state(game_state)
        
        # For demo purposes, just auto-play first card to first empty slot
        if game_state.current_phase == GamePhase.PLAY and game_state.current_player.hand:
            for field_index in range(len(game_state.current_player.field)):
                if game_state.current_player.field[field_index] is None:
                    success, message = game_state.current_player.play_card(0, field_index)
                    print(f"Playing card: {message}")
                    if success:
                        break
        
        # Move to next phase
        print(f"Moving to next phase: {game_state.next_phase().name}")
        
        # If in attack phase, simulate attacks
        if game_state.current_phase == GamePhase.ATTACK:
            # In a real game, this would be more complex with card interactions
            print("Simulating attacks...")
            attacker = game_state.current_player
            defender = game_state.other_player
            
            for slot, card in enumerate(attacker.field):
                if card:
                    # If there's a card in the same slot for the defender, attack it
                    if defender.field[slot]:
                        defender_card = defender.field[slot]
                        print(f"{card.name} attacks {defender_card.name}")
                        excess = defender_card.take_damage(card.attack)
                        if not defender_card.is_alive():
                            print(f"{defender_card.name} is destroyed!")
                            defender.field[slot] = None
                            
                            # Apply excess damage to player
                            if excess > 0:
                                defender.take_damage(excess)
                                print(f"{excess} damage goes through to {defender.name}")
                    else:
                        # Direct attack
                        defender.take_damage(card.attack)
                        print(f"{card.name} attacks {defender.name} directly for {card.attack} damage!")
            
            # Check if game is over
            if game_state.check_game_over():
                print(f"Game over! Winner: {game_state.winner.name}")
                break
    
    print("\nDemo game loop completed.")


def main():
    """
    Main function to run the game.
    """
    try:
        # Initialize the game
        game_state, card_database = initialize_game()
        
        # Run a simple game loop for demonstration
        simple_game_loop(game_state, card_database)
        
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
