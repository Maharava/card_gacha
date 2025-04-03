"""
Game state model for the card game.
"""
from enum import Enum, auto
from typing import Optional, List, Dict, Any
from .player import Player


class GamePhase(Enum):
    """
    Enum representing the different phases of a turn.
    """
    DRAW = auto()
    PLAY = auto()
    ATTACK = auto()
    END = auto()


class GameState:
    """
    Represents the current state of the game.
    
    Attributes:
        player (Player): The human player
        opponent (Player): The AI opponent
        current_player_index (int): Index of the current player (0 for player, 1 for opponent)
        current_phase (GamePhase): Current phase of the turn
        turn_number (int): Current turn number
        game_over (bool): Whether the game has ended
        winner (Optional[Player]): The winner of the game, if any
    """
    
    def __init__(self, player: Player, opponent: Player):
        """
        Initialize a new game state.
        
        Args:
            player (Player): The human player
            opponent (Player): The AI opponent
        """
        self.player = player
        self.opponent = opponent
        self.players = [player, opponent]  # For easier indexing
        self.current_player_index = 0  # Player goes first
        self.current_phase = GamePhase.DRAW
        self.turn_number = 1
        self.game_over = False
        self.winner = None
    
    @property
    def current_player(self) -> Player:
        """
        Get the current player.
        
        Returns:
            Player: Current player
        """
        return self.players[self.current_player_index]
    
    @property
    def other_player(self) -> Player:
        """
        Get the player who's not currently active.
        
        Returns:
            Player: Other player
        """
        return self.players[1 - self.current_player_index]
    
    def next_phase(self) -> GamePhase:
        """
        Advance to the next phase of the turn.
        
        Returns:
            GamePhase: The new phase
        """
        phases = list(GamePhase)
        current_index = phases.index(self.current_phase)
        next_index = (current_index + 1) % len(phases)
        self.current_phase = phases[next_index]
        
        # If we've reached the end phase, check for next turn
        if self.current_phase == GamePhase.DRAW:
            self.next_turn()
            
        return self.current_phase
    
    def next_turn(self) -> None:
        """
        Advance to the next turn.
        """
        self.current_player_index = 1 - self.current_player_index
        
        # If it's the first player's turn again, increment turn number
        if self.current_player_index == 0:
            self.turn_number += 1
        
        # Reset energy for the new current player
        self.current_player.reset_energy()
    
    def check_game_over(self) -> bool:
        """
        Check if the game is over.
        
        Returns:
            bool: True if game is over, False otherwise
        """
        if not self.player.is_alive():
            self.game_over = True
            self.winner = self.opponent
            return True
        
        if not self.opponent.is_alive():
            self.game_over = True
            self.winner = self.player
            return True
        
        return False
    
    def to_dict(self) -> dict:
        """
        Convert the game state to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the game state
        """
        return {
            "player": self.player.to_dict(),
            "opponent": self.opponent.to_dict(),
            "current_player_index": self.current_player_index,
            "current_phase": self.current_phase.name,
            "turn_number": self.turn_number,
            "game_over": self.game_over,
            "winner": self.winner.name if self.winner else None
        }
