from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os

@dataclass
class PlayerEconomy:
    """Player economy data including currencies and progression."""
    player_id: str
    coins: int = 100  # Basic currency
    gems: int = 10    # Premium currency
    experience: int = 0
    level: int = 1
    completed_achievements: List[str] = field(default_factory=list)
    unlocked_cards: List[str] = field(default_factory=list)
    
    # Experience required for each level (index 0 = level 1)
    level_thresholds = [
        0, 100, 250, 450, 700, 1000, 1350, 1750, 2200, 2700,  # Levels 1-10
        3250, 3850, 4500, 5200, 5950, 6750, 7600, 8500, 9450, 10450  # Levels 11-20
    ]

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
    
    def add_gems(self, amount: int) -> int:
        """Add gems to player balance and return new balance."""
        self.gems += amount
        return self.gems
    
    def remove_gems(self, amount: int) -> bool:
        """Remove gems if player has enough. Returns True if successful."""
        if self.gems >= amount:
            self.gems -= amount
            return True
        return False
    
    def add_experience(self, amount: int) -> Dict:
        """Add experience points and handle level-ups."""
        self.experience += amount
        old_level = self.level
        
        # Check for level up
        while (self.level < len(self.level_thresholds) and 
               self.experience >= self.level_thresholds[self.level]):
            self.level += 1
        
        return {
            "new_exp": self.experience,
            "old_level": old_level,
            "new_level": self.level,
            "leveled_up": self.level > old_level
        }
    
    def unlock_card(self, card_id: str) -> bool:
        """Unlock a card for the player."""
        if card_id not in self.unlocked_cards:
            self.unlocked_cards.append(card_id)
            return True
        return False
    
    def complete_achievement(self, achievement_id: str) -> bool:
        """Mark an achievement as completed."""
        if achievement_id not in self.completed_achievements:
            self.completed_achievements.append(achievement_id)
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
                    "experience": self.experience,
                    "level": self.level,
                    "completed_achievements": self.completed_achievements,
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
                    gems=data.get("gems", 10),
                    experience=data.get("experience", 0),
                    level=data.get("level", 1),
                    completed_achievements=data.get("completed_achievements", []),
                    unlocked_cards=data.get("unlocked_cards", [])
                )
        except Exception as e:
            print(f"Error loading player economy: {e}")
            return cls(player_id=player_id)