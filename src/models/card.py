"""
Card model for the card game.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Card:
    """
    Represents a card in the game.
    
    Attributes:
        id (str): Unique identifier for the card
        name (str): Display name of the card
        hp (int): Health points of the card
        cost (int): Energy cost to play the card
        attack (int): Attack power of the card
        image_path (str): Path to the card's image file
        flavor_text (str): Descriptive text for the card
        rarity (str): Rarity level of the card (common, uncommon, rare, epic)
    """
    id: str
    name: str
    hp: int
    cost: int
    attack: int
    image_path: str
    flavor_text: str
    rarity: str
    
    def is_alive(self) -> bool:
        """
        Check if the card is still alive (has HP greater than 0).
        
        Returns:
            bool: True if the card is alive, False otherwise
        """
        return self.hp > 0
    
    def take_damage(self, damage: int) -> int:
        """
        Apply damage to the card and return any excess damage.
        
        Args:
            damage (int): Amount of damage to apply
            
        Returns:
            int: Excess damage (if card's HP goes below 0)
        """
        self.hp -= damage
        if self.hp < 0:
            excess = abs(self.hp)
            self.hp = 0
            return excess
        return 0
    
    def to_dict(self) -> dict:
        """
        Convert the card to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the card
        """
        return {
            "id": self.id,
            "name": self.name,
            "hp": self.hp,
            "cost": self.cost,
            "attack": self.attack,
            "image_path": self.image_path,
            "flavor_text": self.flavor_text,
            "rarity": self.rarity
        }
    
    @classmethod
    def from_dict(cls, card_id: str, card_data: dict) -> 'Card':
        """
        Create a Card instance from a dictionary.
        
        Args:
            card_id (str): The ID of the card
            card_data (dict): Dictionary containing card attributes
            
        Returns:
            Card: New Card instance
        """
        return cls(
            id=card_id,
            name=card_data.get("name", "Unknown Card"),
            hp=card_data.get("hp", 1),
            cost=card_data.get("cost", 1),
            attack=card_data.get("attack", 1),
            image_path=card_data.get("image", ""),
            flavor_text=card_data.get("flavor_text", ""),
            rarity=card_data.get("rarity", "common")
        )
