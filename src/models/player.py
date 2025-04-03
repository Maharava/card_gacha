"""
Player model for the card game.
"""
from typing import List, Optional, Dict, Tuple
from .card import Card
from .deck import Deck
from ..constants import (
    PLAYER_STARTING_HEALTH, PLAYER_MAX_ENERGY, PLAYER_FIELD_SIZE,
    CARD_CONVERSION_COMMON, CARD_CONVERSION_UNCOMMON, 
    CARD_CONVERSION_RARE, CARD_CONVERSION_EPIC
)


class Player:
    """
    Represents a player in the game.
    
    Attributes:
        name (str): Player's name
        health (int): Current health points
        energy (int): Current energy points
        max_energy (int): Maximum energy points
        deck (Deck): Player's current deck
        hand (List[Card]): Cards in hand
        field (List[Optional[Card]]): Cards on the field
        collection (Dict[str, int]): Cards owned by the player and their quantities
        credits (int): Currency for buying cards
    """
    
    def __init__(self, name: str, deck: Deck, starting_health: int = PLAYER_STARTING_HEALTH,
                 max_energy: int = PLAYER_MAX_ENERGY):
        """
        Initialize a new player.
        
        Args:
            name (str): Player's name
            deck (Deck): Player's deck
            starting_health (int, optional): Initial health. Defaults to PLAYER_STARTING_HEALTH.
            max_energy (int, optional): Maximum energy. Defaults to PLAYER_MAX_ENERGY.
        """
        self.name = name
        self.health = starting_health
        self.max_health = starting_health
        self.energy = max_energy
        self.max_energy = max_energy
        self.deck = deck
        self.hand = []
        self.field = [None] * PLAYER_FIELD_SIZE  # Initialize empty field slots
        self.collection = {}  # Card ID -> quantity
        self.credits = 0
    
    def draw_card(self) -> Optional[Card]:
        """
        Draw a card from the player's deck into their hand.
        
        Returns:
            Optional[Card]: The drawn card or None if deck is empty
        """
        card = self.deck.draw()
        if card:
            self.hand.append(card)
        return card
    
    def draw_starting_hand(self, size: int) -> List[Card]:
        """
        Draw the initial hand for the player.
        
        Args:
            size (int): Number of cards to draw
            
        Returns:
            List[Card]: List of drawn cards
        """
        cards = self.deck.draw_hand(size)
        self.hand.extend(cards)
        return cards
    
    def play_card(self, hand_index: int, field_index: int) -> Tuple[bool, str]:
        """
        Play a card from hand to a field position.
        
        Args:
            hand_index (int): Index of the card in hand
            field_index (int): Index of the field position
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        # Check if indices are valid
        if not (0 <= hand_index < len(self.hand)):
            return False, "Invalid hand index"
        
        if not (0 <= field_index < PLAYER_FIELD_SIZE):
            return False, "Invalid field index"
        
        # Check if the field position is occupied
        if self.field[field_index] is not None:
            return False, "Field position already occupied"
        
        # Get the card and check if we have enough energy
        card = self.hand[hand_index]
        if self.energy < card.cost:
            return False, "Not enough energy"
        
        # Play the card
        self.energy -= card.cost
        self.field[field_index] = self.hand.pop(hand_index)
        
        return True, "Card played successfully"
    
    def take_damage(self, damage: int) -> None:
        """
        Apply damage to the player.
        
        Args:
            damage (int): Amount of damage to apply
        """
        self.health = max(0, self.health - damage)
    
    def is_alive(self) -> bool:
        """
        Check if the player is still alive.
        
        Returns:
            bool: True if the player is alive, False otherwise
        """
        return self.health > 0
    
    def reset_energy(self) -> None:
        """
        Reset the player's energy to maximum at the start of their turn.
        """
        self.energy = self.max_energy
    
    def add_to_collection(self, card_id: str, quantity: int = 1) -> Tuple[int, int]:
        """
        Add cards to the player's collection. If player already has 3 copies,
        excess cards are converted to credits.
        
        Args:
            card_id (str): ID of the card to add
            quantity (int, optional): Quantity to add. Defaults to 1.
            
        Returns:
            Tuple[int, int]: (Added cards, Credits from conversion)
        """
        current_quantity = self.collection.get(card_id, 0)
        max_copies = 3
        
        # Calculate how many cards to add and how many to convert
        can_add = max(0, max_copies - current_quantity)
        to_add = min(quantity, can_add)
        to_convert = quantity - to_add
        
        # Add cards to collection
        if to_add > 0:
            self.collection[card_id] = current_quantity + to_add
        
        # Convert excess cards to credits
        credits_earned = 0
        if to_convert > 0:
            # Get card rarity to determine conversion rate
            # We need to check if this card exists in the deck or other places
            # since we don't have direct access to card_database here
            from ..utils.resource_loader import ResourceLoader
            card_database = ResourceLoader.load_cards()
            
            if card_id in card_database:
                card = card_database[card_id]
                # Determine conversion rate based on rarity
                if card.rarity == "common":
                    conversion_rate = CARD_CONVERSION_COMMON
                elif card.rarity == "uncommon":
                    conversion_rate = CARD_CONVERSION_UNCOMMON
                elif card.rarity == "rare":
                    conversion_rate = CARD_CONVERSION_RARE
                elif card.rarity == "epic":
                    conversion_rate = CARD_CONVERSION_EPIC
                else:
                    conversion_rate = 1  # Default fallback
                
                credits_earned = to_convert * conversion_rate
                self.add_credits(credits_earned)
        
        return to_add, credits_earned
    
    def add_credits(self, amount: int) -> None:
        """
        Add credits to the player's account.
        
        Args:
            amount (int): Amount of credits to add
        """
        self.credits += amount
    
    def to_dict(self) -> dict:
        """
        Convert the player to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the player
        """
        return {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "energy": self.energy,
            "max_energy": self.max_energy,
            "deck": self.deck.to_dict(),
            "collection": self.collection,
            "credits": self.credits
        }
    
    @classmethod
    def from_dict(cls, player_data: dict, card_database: Dict[str, Card]) -> 'Player':
        """
        Create a Player instance from a dictionary.
        
        Args:
            player_data (dict): Dictionary containing player attributes
            card_database (Dict[str, Card]): Dictionary of all available cards
            
        Returns:
            Player: New Player instance
        """
        name = player_data.get("name", "Player")
        deck_data = player_data.get("deck", {"name": "Default Deck", "cards": []})
        deck = Deck.from_dict(deck_data, card_database)
        
        player = cls(
            name=name,
            deck=deck,
            starting_health=player_data.get("max_health", PLAYER_STARTING_HEALTH),
            max_energy=player_data.get("max_energy", PLAYER_MAX_ENERGY)
        )
        
        player.health = player_data.get("health", player.max_health)
        player.energy = player_data.get("energy", player.max_energy)
        player.collection = player_data.get("collection", {})
        player.credits = player_data.get("credits", 0)
        
        return player