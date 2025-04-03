"""
Utility for saving and loading player progress.
"""
import os
from typing import Optional, Dict
from ..models.player import Player
from ..models.card import Card
from .resource_loader import ResourceLoader
from ..constants import PLAYER_DATA_PATH


class SaveManager:
    """
    Handles saving and loading player progress.
    """
    
    @staticmethod
    def save_player(player: Player) -> bool:
        """
        Save player data to file.
        
        Args:
            player (Player): Player to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        player_data = player.to_dict()
        return ResourceLoader.save_json(player_data, PLAYER_DATA_PATH)
    
    @staticmethod
    def load_player(card_database: Dict[str, Card]) -> Optional[Player]:
        """
        Load player data from file.
        
        Args:
            card_database (Dict[str, Card]): Dictionary of all available cards
            
        Returns:
            Optional[Player]: Loaded player or None if error occurs
        """
        player_data = ResourceLoader.load_json(PLAYER_DATA_PATH)
        
        if player_data:
            try:
                return Player.from_dict(player_data, card_database)
            except Exception as e:
                print(f"Error creating player from data: {str(e)}")
        
        return None
    
    @staticmethod
    def player_exists() -> bool:
        """
        Check if player save data exists.
        
        Returns:
            bool: True if player data exists, False otherwise
        """
        return os.path.exists(PLAYER_DATA_PATH)
