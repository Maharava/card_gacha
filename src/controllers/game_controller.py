"""
Game controller for managing the overall game flow.
"""
from typing import Tuple, List, Optional, Dict, Any
from ..models.game_state import GameState, GamePhase
from ..models.player import Player
from ..models.card import Card
from ..constants import (
    VICTORY_REWARD_EASY, VICTORY_REWARD_NORMAL, VICTORY_REWARD_HARD
)


class GameController:
    """
    Controls the overall flow of the game.
    
    This controller is responsible for:
    - Managing phase transitions
    - Handling card combat resolution
    - Determining victory/defeat conditions
    - Awarding rewards after game completion
    """
    
    def __init__(self, game_state: GameState):
        """
        Initialize the game controller.
        
        Args:
            game_state (GameState): The current game state
        """
        self.game_state = game_state
        
    def start_game(self) -> None:
        """
        Set up the game state at the beginning of a new game.
        """
        # Make sure the game starts on the first player's turn in the draw phase
        self.game_state.current_player_index = 0
        self.game_state.current_phase = GamePhase.DRAW
        self.game_state.turn_number = 1
        self.game_state.game_over = False
        self.game_state.winner = None
        
        # Reset player states
        for player in self.game_state.players:
            player.reset_energy()
            player.health = player.max_health
            player.hand.clear()
            player.field = [None] * len(player.field)
            
            # Shuffle decks
            player.deck.shuffle()
        
    def process_turn(self) -> Dict[str, Any]:
        """
        Process the current phase of the turn and update the game state.
        
        Returns:
            Dict[str, Any]: Events that occurred during the phase
        """
        events = {"phase": self.game_state.current_phase.name, "events": []}
        
        if self.game_state.current_phase == GamePhase.DRAW:
            events["events"].extend(self._handle_draw_phase())
        elif self.game_state.current_phase == GamePhase.PLAY:
            # Play phase is handled by player/AI controllers
            pass
        elif self.game_state.current_phase == GamePhase.ATTACK:
            events["events"].extend(self._handle_attack_phase())
        elif self.game_state.current_phase == GamePhase.END:
            events["events"].extend(self._handle_end_phase())
            
        return events
    
    def advance_phase(self) -> GamePhase:
        """
        Advance to the next phase of the turn.
        
        Returns:
            GamePhase: The new phase
        """
        return self.game_state.next_phase()
    
    def _handle_draw_phase(self) -> List[Dict[str, Any]]:
        """
        Handle the draw phase for the current player.
        
        Returns:
            List[Dict[str, Any]]: Events that occurred during the phase
        """
        events = []
        
        # Current player draws a card
        current_player = self.game_state.current_player
        card = current_player.draw_card()
        
        if card:
            events.append({
                "type": "draw",
                "player": current_player.name,
                "card": card.name
            })
        else:
            events.append({
                "type": "deck_empty",
                "player": current_player.name
            })
            
        return events
    
    def _handle_attack_phase(self) -> List[Dict[str, Any]]:
        """
        Handle the attack phase, resolving combat between cards.
        
        Returns:
            List[Dict[str, Any]]: Events that occurred during the phase
        """
        events = []
        
        attacker = self.game_state.current_player
        defender = self.game_state.other_player
        
        for slot, card in enumerate(attacker.field):
            if card:
                # If there's a card in the same slot for the defender, attack it
                if defender.field[slot]:
                    defender_card = defender.field[slot]
                    
                    # Cards deal damage to each other simultaneously
                    events.append({
                        "type": "card_attack",
                        "attacker": card.name,
                        "defender": defender_card.name,
                        "attack_damage": card.attack,
                        "slot": slot
                    })
                    
                    # Calculate damage
                    excess_damage = defender_card.take_damage(card.attack)
                    
                    # Check if defender card is destroyed
                    if not defender_card.is_alive():
                        events.append({
                            "type": "card_destroyed",
                            "card": defender_card.name,
                            "slot": slot
                        })
                        defender.field[slot] = None
                        
                        # Apply excess damage to player
                        if excess_damage > 0:
                            defender.take_damage(excess_damage)
                            events.append({
                                "type": "player_damage",
                                "player": defender.name,
                                "damage": excess_damage,
                                "source": f"Excess from {card.name}"
                            })
                    
                    # Defender card counter-attacks if it's still alive
                    if defender_card.is_alive():
                        card.take_damage(defender_card.attack)
                        events.append({
                            "type": "card_counter_attack",
                            "attacker": defender_card.name,
                            "defender": card.name,
                            "attack_damage": defender_card.attack,
                            "slot": slot
                        })
                        
                        # Check if attacker card is destroyed
                        if not card.is_alive():
                            events.append({
                                "type": "card_destroyed",
                                "card": card.name,
                                "slot": slot
                            })
                            attacker.field[slot] = None
                else:
                    # Direct attack on player
                    defender.take_damage(card.attack)
                    events.append({
                        "type": "player_damage",
                        "player": defender.name,
                        "damage": card.attack,
                        "source": card.name
                    })
        
        # Check if game is over after attack phase
        if self._check_game_over():
            if self.game_state.winner == self.game_state.player:
                # Determine reward based on difficulty
                difficulty = "normal"  # Default
                
                # Extract difficulty from opponent name
                opponent_name = self.game_state.opponent.name.lower()
                if "easy" in opponent_name:
                    difficulty = "easy"
                elif "hard" in opponent_name:
                    difficulty = "hard"
                
                # Award difficulty-based rewards
                reward = VICTORY_REWARD_NORMAL
                if difficulty == "easy":
                    reward = VICTORY_REWARD_EASY
                elif difficulty == "hard":
                    reward = VICTORY_REWARD_HARD
                    
                self.game_state.player.add_credits(reward)
                events.append({
                    "type": "credits_awarded",
                    "player": self.game_state.player.name,
                    "amount": reward,
                    "difficulty": difficulty
                })
            
            events.append({
                "type": "game_over",
                "winner": self.game_state.winner.name
            })
            
        return events
    
    def _handle_end_phase(self) -> List[Dict[str, Any]]:
        """
        Handle the end phase of the turn.
        
        Returns:
            List[Dict[str, Any]]: Events that occurred during the phase
        """
        # Nothing special happens in the end phase for now,
        # but this could include effects that trigger at end of turn
        return []
    
    def _check_game_over(self) -> bool:
        """
        Check if the game is over and set the winner accordingly.
        
        Returns:
            bool: True if game is over, False otherwise
        """
        return self.game_state.check_game_over()