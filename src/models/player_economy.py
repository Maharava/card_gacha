from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os

@dataclass
class PlayerEconomy:
    """Player economy data including currencies and card collection."""
    player_id: str
    coins: int = 100  # Basic currency
    unlocked_cards: List[str] = field(default_factory=list)

    def add_coins(self, amount: int) -> int:
        """Add coins to player balance and return new balance."""
        self.coins += amount
        return self.coins
    
    def remove_coins(self, amount: int) -> bool:
        """Remove coins if player has enough. Returns True if successful."""
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False
    
    def unlock_card(self, card_id: str) -> bool:
        """Unlock a card for the player."""
        if card_id not in self.unlocked_cards:
            self.unlocked_cards.append(card_id)
            return True
        return False
    
    def save(self) -> bool:
        """Save player economy data to file."""
        try:
            save_dir = os.path.join("data", "players")
            os.makedirs(save_dir, exist_ok=True)
            
            file_path = os.path.join(save_dir, f"{self.player_id}_economy.json")
            with open(file_path, 'w') as f:
                json.dump({
                    "coins": self.coins,
                    "gems": self.gems,
                    "unlocked_cards": self.unlocked_cards
                }, f)
            return True
        except Exception as e:
            print(f"Error saving player economy: {e}")
            return False
    
    @classmethod
    def load(cls, player_id: str) -> Optional['PlayerEconomy']:
        """Load player economy data from file."""
        try:
            file_path = os.path.join("data", "players", f"{player_id}_economy.json")
            if not os.path.exists(file_path):
                return cls(player_id=player_id)
            
            with open(file_path, 'r') as f:
                data = json.load(f)
                return cls(
                    player_id=player_id,
                    coins=data.get("coins", 100),
                    unlocked_cards=data.get("unlocked_cards", [])
                )
        except Exception as e:
            print(f"Error loading player economy: {e}")
            return cls(player_id=player_id)