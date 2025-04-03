"""
Deck model for the card game.
"""
import random
from typing import List, Optional, Dict
from .card import Card


class Deck:
    """
    Represents a deck of cards in the game.
    
    Attributes:
        cards (List[Card]): List of cards in the deck
        name (str): Name of the deck
    """
    
    def __init__(self, name: str = "Default Deck", cards: Optional[List[Card]] = None):
        """
        Initialize a new deck.
        
        Args:
            name (str, optional): Name of the deck. Defaults to "Default Deck".
            cards (List[Card], optional): Initial list of cards. Defaults to None.
        """
        self.name = name
        self.cards = cards if cards is not None else []
    
    def add_card(self, card: Card) -> None:
        """
        Add a card to the deck.
        
        Args:
            card (Card): Card to add
        """
        self.cards.append(card)
    
    def remove_card(self, card_index: int) -> Optional[Card]:
        """
        Remove a card from the deck by index.
        
        Args:
            card_index (int): Index of the card to remove
            
        Returns:
            Optional[Card]: Removed card or None if index is invalid
        """
        if 0 <= card_index < len(self.cards):
            return self.cards.pop(card_index)
        return None
    
    def shuffle(self) -> None:
        """
        Shuffle the deck.
        """
        random.shuffle(self.cards)
    
    def draw(self) -> Optional[Card]:
        """
        Draw a card from the top of the deck.
        
        Returns:
            Optional[Card]: Drawn card or None if deck is empty
        """
        if not self.cards:
            return None
        return self.cards.pop(0)
    
    def draw_hand(self, count: int) -> List[Card]:
        """
        Draw multiple cards from the deck.
        
        Args:
            count (int): Number of cards to draw
            
        Returns:
            List[Card]: List of drawn cards
        """
        hand = []
        for _ in range(min(count, len(self.cards))):
            card = self.draw()
            if card:
                hand.append(card)
        return hand
    
    def is_empty(self) -> bool:
        """
        Check if the deck is empty.
        
        Returns:
            bool: True if deck is empty, False otherwise
        """
        return len(self.cards) == 0
    
    def size(self) -> int:
        """
        Get the number of cards in the deck.
        
        Returns:
            int: Number of cards
        """
        return len(self.cards)
    
    def to_dict(self) -> dict:
        """
        Convert the deck to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the deck
        """
        return {
            "name": self.name,
            "cards": [card.id for card in self.cards]
        }
    
    @classmethod
    def from_dict(cls, deck_data: dict, card_database: Dict[str, Card]) -> 'Deck':
        """
        Create a Deck instance from a dictionary.
        
        Args:
            deck_data (dict): Dictionary containing deck attributes
            card_database (Dict[str, Card]): Dictionary of all available cards
            
        Returns:
            Deck: New Deck instance
        """
        name = deck_data.get("name", "Imported Deck")
        card_ids = deck_data.get("cards", [])
        
        cards = []
        for card_id in card_ids:
            if card_id in card_database:
                cards.append(card_database[card_id])
        
        return cls(name=name, cards=cards)
    
    @classmethod
    def create_starter_deck(cls, card_database: Dict[str, Card]) -> 'Deck':
        """
        Create a balanced starter deck for new players.
        
        Args:
            card_database (Dict[str, Card]): Dictionary of all available cards
            
        Returns:
            Deck: Starter deck with balanced card selection
        """
        # This is a simplified implementation - in a real game, you'd have
        # a more sophisticated algorithm for creating a balanced starter deck
        
        # Filter cards by rarity for starter deck
        common_cards = [card for card in card_database.values() 
                        if card.rarity == "common"]
        uncommon_cards = [card for card in card_database.values() 
                         if card.rarity == "uncommon"]
        
        # Create a simple 30-card deck with 70% common and 30% uncommon cards
        starter_cards = []
        
        # Add common cards
        if common_cards:
            for _ in range(21):  # 70% common
                starter_cards.append(random.choice(common_cards))
        
        # Add uncommon cards
        if uncommon_cards:
            for _ in range(9):  # 30% uncommon
                starter_cards.append(random.choice(uncommon_cards))
        
        starter_deck = cls(name="Starter Deck", cards=starter_cards)
        starter_deck.shuffle()
        
        return starter_deck
