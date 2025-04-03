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
        
        # [Combat logic remains the same]
        
        # Check if game is over after attack phase
        if self._check_game_over():
            if self.game_state.winner == self.game_state.player:
                # Determine reward based on difficulty
                difficulty = self._get_opponent_difficulty()
                
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

    def _get_opponent_difficulty(self) -> str:
        """
        Determine the difficulty of the opponent in a more reliable way.
        
        Returns:
            str: Difficulty level ('easy', 'normal', or 'hard')
        """
        opponent_name = self.game_state.opponent.name.lower()
        
        # First look for explicit difficulty indicators in the name
        if "easy" in opponent_name:
            return "easy"
        elif "hard" in opponent_name:
            return "hard"
        
        # If no explicit indicator, check the deck strength
        opponent_deck = self.game_state.opponent.deck
        
        # Count rarity distribution
        rarity_counts = {
            "common": 0,
            "uncommon": 0,
            "rare": 0,
            "epic": 0
        }
        
        for card in opponent_deck.cards:
            if card.rarity in rarity_counts:
                rarity_counts[card.rarity] += 1
        
        # Determine difficulty based on deck composition
        if rarity_counts["rare"] + rarity_counts["epic"] > 8:
            return "hard"
        elif rarity_counts["rare"] + rarity_counts["epic"] < 3:
            return "easy"
        
        # Default to normal
        return "normal"
    
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