"""
Player controller for managing player actions.
"""
from typing import Tuple, List, Dict, Any, Optional
from ..models.game_state import GameState, GamePhase
from ..models.player import Player
from ..models.card import Card
from ..constants import PLAYER_FIELD_SIZE  # Add this import


class PlayerController:
    """
    Controls player actions during the game.
    
    This controller is responsible for:
    - Validating player actions
    - Executing player actions on the game state
    - Managing player resources (energy, cards)
    """
    
    def __init__(self, game_state: GameState):
        """
        Initialize the player controller.
        
        Args:
            game_state (GameState): The current game state
        """
        self.game_state = game_state
    
    def can_play_card(self, player: Player, hand_index: int, field_index: int) -> Tuple[bool, str]:
        """
        Check if a card can be played from hand to a field position.
        
        Args:
            player (Player): The player who wants to play a card
            hand_index (int): Index of the card in hand
            field_index (int): Index of the field position
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        # Check if it's the play phase
        if self.game_state.current_phase != GamePhase.PLAY:
            return False, "You can only play cards during the play phase"
        
        # Check if it's the player's turn
        if self.game_state.current_player != player:
            return False, "It's not your turn"
        
        # Validate indices
        if not (0 <= hand_index < len(player.hand)):
            return False, "Invalid hand index"
        
        if not (0 <= field_index < PLAYER_FIELD_SIZE):
            return False, "Invalid field index"
        
        # Check if the field position is occupied
        if player.field[field_index] is not None:
            return False, "Field position already occupied"
        
        # Check energy
        card = player.hand[hand_index]
        if player.energy < card.cost:
            return False, "Not enough energy"
        
        return True, "Card can be played"
    
    def play_card(self, player: Player, hand_index: int, field_index: int) -> Dict[str, Any]:
        """
        Play a card from the player's hand to their field.
        
        Args:
            player (Player): The player who wants to play a card
            hand_index (int): Index of the card in hand
            field_index (int): Index of the field position
            
        Returns:
            Dict[str, Any]: Result of the action including success flag and events
        """
        # First check game-state specific conditions
        if self.game_state.current_phase != GamePhase.PLAY:
            return {
                "success": False,
                "message": "You can only play cards during the play phase",
                "events": []
            }
        
        if self.game_state.current_player != player:
            return {
                "success": False,
                "message": "It's not your turn",
                "events": []
            }
        
        # Use player's own validation and card playing logic
        card_name = player.hand[hand_index].name if 0 <= hand_index < len(player.hand) else "Unknown"
        success, message = player.play_card(hand_index, field_index)
        
        result = {
            "success": success,
            "message": message,
            "events": []
        }
        
        if success:
            # Record the event
            result["events"].append({
                "type": "card_played",
                "player": player.name,
                "card": card_name,
                "field_position": field_index,
                "energy_remaining": player.energy
            })
        
        return result
    
    def end_play_phase(self, player: Player) -> Dict[str, Any]:
        """
        End the play phase for the player.
        
        Args:
            player (Player): The player who wants to end their play phase
            
        Returns:
            Dict[str, Any]: Result of the action
        """
        result = {
            "success": False,
            "message": "Cannot end play phase now",
            "events": []
        }
        
        # Check if it's the play phase and the player's turn
        if (self.game_state.current_phase == GamePhase.PLAY and 
            self.game_state.current_player == player):
            result["success"] = True
            result["message"] = "Play phase ended"
            result["events"].append({
                "type": "phase_ended",
                "player": player.name,
                "phase": "PLAY"
            })
        
        return result
    
    def get_playable_cards(self, player: Player) -> List[Dict[str, Any]]:
        """
        Get a list of cards in the player's hand that can be played.
        
        Args:
            player (Player): The player whose hand to check
            
        Returns:
            List[Dict[str, Any]]: Information about playable cards
        """
        playable_cards = []
        
        # Check if it's the play phase and the player's turn
        if (self.game_state.current_phase == GamePhase.PLAY and 
            self.game_state.current_player == player):
            
            for index, card in enumerate(player.hand):
                playable = card.cost <= player.energy
                
                playable_cards.append({
                    "index": index,
                    "card": card.name,
                    "cost": card.cost,
                    "playable": playable,
                    "reason": "" if playable else "Not enough energy"
                })
        
        return playable_cards
    
    def get_card_placement_options(self, player: Player) -> List[Dict[str, Any]]:
        """
        Get a list of field positions where a card can be placed.
        
        Args:
            player (Player): The player whose field to check
            
        Returns:
            List[Dict[str, Any]]: Information about available field positions
        """
        placement_options = []
        
        # Check if it's the play phase and the player's turn
        if (self.game_state.current_phase == GamePhase.PLAY and 
            self.game_state.current_player == player):
            
            for index, card in enumerate(player.field):
                available = card is None
                
                placement_options.append({
                    "index": index,
                    "available": available,
                    "current_card": card.name if card else None
                })
        
        return placement_options
