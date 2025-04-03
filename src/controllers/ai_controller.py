"""
AI controller for managing the computer opponent's actions.
"""
from typing import Tuple, List, Dict, Any, Optional
from ..models.game_state import GameState, GamePhase
from ..models.player import Player
from ..models.card import Card


class AIController:
    """
    Controls the AI opponent's decisions during the game.
    
    This controller is responsible for:
    - Deciding which cards to play
    - Choosing card placements
    - Managing AI's turn phases
    """
    
    def __init__(self, game_state: GameState):
        """
        Initialize the AI controller.
        
        Args:
            game_state (GameState): The current game state
        """
        self.game_state = game_state
    
    def take_turn(self) -> Dict[str, Any]:
        """
        Execute the AI's turn.
        
        Returns:
            Dict[str, Any]: Results of the AI's actions during its turn
        """
        result = {
            "events": []
        }
        
        # Only process if it's the AI's turn
        if self.game_state.current_player != self.game_state.opponent:
            return result
        
        # Process based on current phase
        if self.game_state.current_phase == GamePhase.PLAY:
            # Try to play cards during the play phase
            play_results = self._play_cards()
            result["events"].extend(play_results["events"])
        
        return result
    
    def _play_cards(self) -> Dict[str, Any]:
        """
        AI attempts to play cards from its hand to the field.
        
        Returns:
            Dict[str, Any]: Results of the AI's card plays
        """
        ai_player = self.game_state.opponent
        result = {"events": []}
        
        # Simple greedy AI: play the most expensive cards first
        # that the AI can afford with its current energy
        playable_cards = self._get_sorted_playable_cards(ai_player)
        
        # For each playable card, find a valid field position
        for card_idx in playable_cards:
            # Find an empty field position
            for field_idx, field_card in enumerate(ai_player.field):
                if field_card is None:
                    # Try to play the card
                    success, message = ai_player.play_card(card_idx, field_idx)
                    
                    if success:
                        # Adjust the card indices for remaining playable cards
                        playable_cards = [idx - 1 if idx > card_idx else idx for idx in playable_cards]
                        
                        # Record the event
                        card_played = ai_player.field[field_idx]
                        result["events"].append({
                            "type": "ai_card_played",
                            "card": card_played.name,
                            "field_position": field_idx,
                            "energy_remaining": ai_player.energy
                        })
                        
                        break  # Move on to the next card
        
        return result
    
    def _get_sorted_playable_cards(self, player: Player) -> List[int]:
        """
        Get indices of cards in the AI's hand that can be played, sorted by priority.
        
        Args:
            player (Player): The AI player
            
        Returns:
            List[int]: Indices of playable cards in priority order
        """
        # Collect cards that the AI can afford to play
        playable_cards = []
        
        for idx, card in enumerate(player.hand):
            if card.cost <= player.energy:
                playable_cards.append((idx, card))
        
        # Sort cards by priority (currently by cost, highest first)
        # This is a simple strategy - could be enhanced with more sophisticated logic
        sorted_cards = sorted(playable_cards, key=lambda x: x[1].cost, reverse=True)
        
        # Return just the indices
        return [idx for idx, _ in sorted_cards]
    
    def _calculate_card_priority(self, card: Card, player: Player, opponent: Player) -> float:
        """
        Calculate the priority score for playing a card based on game state.
        
        Args:
            card (Card): The card to evaluate
            player (Player): The AI player
            opponent (Player): The human player
            
        Returns:
            float: Priority score (higher is better)
        """
        # This is a placeholder for more sophisticated AI decision-making
        # It could consider factors like:
        # - Card stats (attack/health ratio)
        # - Board state (what cards are already in play)
        # - Player health
        # - Synergies with other cards
        
        # For now, use a simple formula:
        priority = card.attack * 1.5 + card.hp
        
        # Adjust based on remaining field slots
        empty_slots = sum(1 for slot in player.field if slot is None)
        if empty_slots <= 1:
            # Higher priority for cards that can have immediate impact if few slots left
            priority += card.attack * 0.5
        
        return priority
