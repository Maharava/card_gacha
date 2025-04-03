"""
Utility for loading game resources from files.
"""
import json
import os
from typing import Dict, Any, Optional
from ..models.card import Card
from ..constants import CARDS_DATA_PATH


class ResourceLoader:
    """
    Utility class for loading game resources.
    """
    
    @staticmethod
    def load_cards() -> Dict[str, Card]:
        """
        Load cards from the JSON data file.
        
        Returns:
            Dict[str, Card]: Dictionary of Card objects indexed by card ID
        """
        cards = {}
        
        try:
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(CARDS_DATA_PATH), exist_ok=True)
            
            # Try to load the cards file
            if os.path.exists(CARDS_DATA_PATH):
                with open(CARDS_DATA_PATH, 'r') as file:
                    cards_data = json.load(file)
                    
                    for card_id, card_info in cards_data.items():
                        cards[card_id] = Card.from_dict(card_id, card_info)
            else:
                print(f"Warning: Cards data file not found at {CARDS_DATA_PATH}")
        except Exception as e:
            print(f"Error loading cards: {str(e)}")
        
        return cards
    
    @staticmethod
    def save_cards(cards: Dict[str, Card]) -> bool:
        """
        Save cards to the JSON data file.
        
        Args:
            cards (Dict[str, Card]): Dictionary of Card objects
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(CARDS_DATA_PATH), exist_ok=True)
            
            # Convert cards to dictionary format for JSON serialization
            cards_data = {}
            for card_id, card in cards.items():
                cards_data[card_id] = {
                    "name": card.name,
                    "hp": card.hp,
                    "cost": card.cost,
                    "attack": card.attack,
                    "image": card.image_path,
                    "flavor_text": card.flavor_text,
                    "rarity": card.rarity
                }
            
            # Write to file
            with open(CARDS_DATA_PATH, 'w') as file:
                json.dump(cards_data, file, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving cards: {str(e)}")
            return False
    
    @staticmethod
    def load_json(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load any JSON file.
        
        Args:
            file_path (str): Path to the JSON file
            
        Returns:
            Optional[Dict[str, Any]]: Loaded JSON data or None if error occurs
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    return json.load(file)
            else:
                print(f"Warning: File not found at {file_path}")
        except Exception as e:
            print(f"Error loading JSON file {file_path}: {str(e)}")
        
        return None
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            data (Dict[str, Any]): Data to save
            file_path (str): Path to save the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write to file
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving to {file_path}: {str(e)}")
            return False
