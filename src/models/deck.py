"""
Enhanced Deck model for the card game with validation features.
"""
import random
from typing import List, Optional, Dict, Tuple
from collections import Counter
from .card import Card

class Deck:
    """
    Represents a deck of cards in the game.
    
    Attributes:
        cards (List[Card]): List of cards in the deck
        name (str): Name of the deck
    """
    
    MAX_DECK_SIZE = 30
    MAX_COPIES_PER_CARD = 3
    
    def __init__(self, name: str = "Default Deck", cards: Optional[List[Card]] = None):
        """
        Initialize a new deck.
        
        Args:
            name (str, optional): Name of the deck. Defaults to "Default Deck".
            cards (List[Card], optional): Initial list of cards. Defaults to None.
        """
        self.name = name
        self.cards = cards if cards is not None else []
    
    def add_card(self, card: Card) -> bool:
        """
        Add a card to the deck if it passes validation rules.
        
        Args:
            card (Card): Card to add
            
        Returns:
            bool: True if card was added, False if validation failed
        """
        # Check deck size limit
        if len(self.cards) >= self.MAX_DECK_SIZE:
            return False
        
        # Check number of copies of this card
        copies = sum(1 for c in self.cards if c.id == card.id)
        if copies >= self.MAX_COPIES_PER_CARD:
            return False
        
        self.cards.append(card)
        return True
    
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
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate the deck against game rules.
        
        Returns:
            Tuple[bool, str]: (is_valid, message) 
        """
        # Check deck size
        if len(self.cards) < 1:
            return False, "Deck must contain at least 1 card"
        
        if len(self.cards) > self.MAX_DECK_SIZE:
            return False, f"Deck cannot contain more than {self.MAX_DECK_SIZE} cards"
        
        # Check for too many copies of a card
        card_counts = Counter(card.id for card in self.cards)
        for card_id, count in card_counts.items():
            if count > self.MAX_COPIES_PER_CARD:
                return False, f"Deck cannot contain more than {self.MAX_COPIES_PER_CARD} copies of a card"
        
        return True, "Deck is valid"
    
    def get_card_counts(self) -> Dict[str, int]:
        """
        Get counts of each card in the deck.
        
        Returns:
            Dict[str, int]: Mapping of card IDs to counts
        """
        return Counter(card.id for card in self.cards)
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about the deck.
        
        Returns:
            Dict[str, any]: Deck statistics including rarity distribution, cost curve, etc.
        """
        stats = {
            "size": len(self.cards),
            "rarity_distribution": {},
            "cost_distribution": {},
            "attack_distribution": {},
            "health_distribution": {}
        }
        
        # Initialize distributions
        for rarity in ["common", "uncommon", "rare", "epic"]:
            stats["rarity_distribution"][rarity] = 0
        
        for cost in range(0, 4):  # 0-3 cost
            stats["cost_distribution"][cost] = 0
        
        # Calculate distributions
        for card in self.cards:
            # Rarity distribution
            if card.rarity in stats["rarity_distribution"]:
                stats["rarity_distribution"][card.rarity] += 1
            
            # Cost distribution
            if card.cost in stats["cost_distribution"]:
                stats["cost_distribution"][card.cost] += 1
            
            # Attack and health
            stats["attack_distribution"][card.attack] = stats["attack_distribution"].get(card.attack, 0) + 1
            stats["health_distribution"][card.hp] = stats["health_distribution"].get(card.hp, 0) + 1
        
        return stats
    
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