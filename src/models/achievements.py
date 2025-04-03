from dataclasses import dataclass
from typing import Dict, List, Callable, Optional
import json
import os

@dataclass
class Achievement:
    """Achievement model for the game."""
    id: str
    name: str
    description: str
    icon: str
    reward_coins: int = 0
    reward_gems: int = 0
    reward_experience: int = 0
    reward_cards: List[str] = None
    
    def __post_init__(self):
        if self.reward_cards is None:
            self.reward_cards = []


class AchievementManager:
    """Manages achievements and their tracking."""
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.trackers: Dict[str, Callable] = {}
        self._load_achievements()
    
    def _load_achievements(self):
        """Load achievements from file."""
        try:
            file_path = os.path.join("data", "achievements.json")
            if not os.path.exists(file_path):
                self._create_default_achievements()
                return
            
            with open(file_path, 'r') as f:
                data = json.load(f)
                for achievement_data in data:
                    achievement = Achievement(
                        id=achievement_data.get("id"),
                        name=achievement_data.get("name"),
                        description=achievement_data.get("description"),
                        icon=achievement_data.get("icon"),
                        reward_coins=achievement_data.get("reward_coins", 0),
                        reward_gems=achievement_data.get("reward_gems", 0),
                        reward_experience=achievement_data.get("reward_experience", 0),
                        reward_cards=achievement_data.get("reward_cards", [])
                    )
                    self.achievements[achievement.id] = achievement
        except Exception as e:
            print(f"Error loading achievements: {e}")
            self._create_default_achievements()
    
    def _create_default_achievements(self):
        """Create and save default achievements."""
        default_achievements = [
            Achievement(
                id="first_win",
                name="First Victory",
                description="Win your first game",
                icon="trophy.png",
                reward_coins=50,
                reward_experience=20
            ),
            Achievement(
                id="win_streak_3",
                name="Hat Trick",
                description="Win 3 games in a row",
                icon="streak.png",
                reward_coins=100,
                reward_experience=50
            ),
            Achievement(
                id="collect_10_cards",
                name="Collector",
                description="Collect 10 different cards",
                icon="collection.png",
                reward_gems=5,
                reward_experience=30
            ),
            Achievement(
                id="reach_level_5",
                name="Rising Star",
                description="Reach player level 5",
                icon="star.png",
                reward_gems=10,
                reward_coins=200
            ),
        ]
        
        for achievement in default_achievements:
            self.achievements[achievement.id] = achievement
        
        try:
            os.makedirs("data", exist_ok=True)
            with open(os.path.join("data", "achievements.json"), 'w') as f:
                json.dump([{
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "icon": a.icon,
                    "reward_coins": a.reward_coins,
                    "reward_gems": a.reward_gems,
                    "reward_experience": a.reward_experience,
                    "reward_cards": a.reward_cards
                } for a in default_achievements], f)
        except Exception as e:
            print(f"Error saving default achievements: {e}")
    
    def register_tracker(self, achievement_id: str, tracker: Callable):
        """Register a tracker function for an achievement."""
        self.trackers[achievement_id] = tracker
    
    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get achievement by ID."""
        return self.achievements.get(achievement_id)
    
    def get_all_achievements(self) -> List[Achievement]:
        """Get a list of all achievements."""
        return list(self.achievements.values())