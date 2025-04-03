from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random
import json
import os
from datetime import datetime, timedelta

from src.models.player_economy import PlayerEconomy

@dataclass
class ShopItem:
    """Item for sale in the shop."""
    id: str
    name: str
    description: str
    image: str
    price_coins: int = 0
    price_gems: int = 0
    item_type: str = "card"  # card, pack, cosmetic, etc.
    rarity: str = "common"   # common, uncommon, rare, epic
    
    def can_afford(self, economy: PlayerEconomy) -> bool:
        """Check if player can afford this item."""
        return (economy.coins >= self.price_coins and 
                economy.gems >= self.price_gems)


class ShopManager:
    """Manages the shop and its inventory."""
    
    def __init__(self):
        self.all_items: Dict[str, ShopItem] = {}
        self.current_inventory: List[ShopItem] = []
        self.special_deals: List[ShopItem] = []
        self.last_refresh = datetime.now() - timedelta(days=1)  # Force refresh on start
        self._load_shop_items()
    
    def _load_shop_items(self):
        """Load all potential shop items from file."""
        try:
            file_path = os.path.join("data", "shop_items.json")
            if not os.path.exists(file_path):
                self._create_default_shop_items()
                return
            
            with open(file_path, 'r') as f:
                data = json.load(f)
                for item_data in data:
                    item = ShopItem(
                        id=item_data.get("id"),
                        name=item_data.get("name"),
                        description=item_data.get("description"),
                        image=item_data.get("image"),
                        price_coins=item_data.get("price_coins", 0),
                        price_gems=item_data.get("price_gems", 0),
                        item_type=item_data.get("item_type", "card"),
                        rarity=item_data.get("rarity", "common")
                    )
                    self.all_items[item.id] = item
            
            self.refresh_inventory()
        except Exception as e:
            print(f"Error loading shop items: {e}")
            self._create_default_shop_items()
    
    def _create_default_shop_items(self):
        """Create and save default shop items."""
        default_items = [
            ShopItem(
                id="card_fireball",
                name="Fireball",
                description="Deal 3 damage to a target",
                image="fireball.png",
                price_coins=100,
                price_gems=0,
                item_type="card",
                rarity="common"
            ),
            ShopItem(
                id="card_heal",
                name="Healing Touch",
                description="Restore 3 health to a target",
                image="heal.png",
                price_coins=100,
                price_gems=0,
                item_type="card",
                rarity="common"
            ),
            ShopItem(
                id="card_shield",
                name="Shield",
                description="Give a target +2 defense",
                image="shield.png",
                price_coins=150,
                price_gems=0,
                item_type="card",
                rarity="uncommon"
            ),
            ShopItem(
                id="pack_basic",
                name="Basic Pack",
                description="Contains 5 common or uncommon cards",
                image="basic_pack.png",
                price_coins=250,
                price_gems=0,
                item_type="pack",
                rarity="common"
            ),
            ShopItem(
                id="pack_premium",
                name="Premium Pack",
                description="Contains 5 cards with at least 1 rare",
                image="premium_pack.png",
                price_coins=0,
                price_gems=50,
                item_type="pack",
                rarity="rare"
            ),
        ]
        
        for item in default_items:
            self.all_items[item.id] = item
        
        try:
            os.makedirs("data", exist_ok=True)
            with open(os.path.join("data", "shop_items.json"), 'w') as f:
                json.dump([{
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "image": item.image,
                    "price_coins": item.price_coins,
                    "price_gems": item.price_gems,
                    "item_type": item.item_type,
                    "rarity": item.rarity
                } for item in default_items], f)
            
            self.refresh_inventory()
        except Exception as e:
            print(f"Error saving default shop items: {e}")
    
    def refresh_inventory(self) -> bool:
        """Refresh the shop inventory. Returns True if refreshed."""
        now = datetime.now()
        
        # Only refresh once per day (or if forced)
        if (now - self.last_refresh).days < 1:
            return False
        
        self.last_refresh = now
        
        # Pick a random selection for the main inventory
        all_items = list(self.all_items.values())
        self.current_inventory = random.sample(
            all_items, 
            min(6, len(all_items))
        )
        
        # Create special deals (discounted items)
        special_candidates = [item for item in all_items if item not in self.current_inventory]
        if special_candidates:
            self.special_deals = random.sample(
                special_candidates,
                min(2, len(special_candidates))
            )
            
            # Apply a discount to special deals
            for item in self.special_deals:
                discounted_item = ShopItem(
                    id=f"deal_{item.id}",
                    name=f"Special: {item.name}",
                    description=item.description,
                    image=item.image,
                    price_coins=int(item.price_coins * 0.7) if item.price_coins else 0,
                    price_gems=int(item.price_gems * 0.7) if item.price_gems else 0,
                    item_type=item.item_type,
                    rarity=item.rarity
                )
                self.special_deals.append(discounted_item)
        
        return True
    
    def purchase_item(self, item_id: str, economy: PlayerEconomy) -> Dict:
        """Process a purchase. Returns result information."""
        # Find the item in current inventory or special deals
        item = next((i for i in self.current_inventory + self.special_deals if i.id == item_id), None)
        
        if not item:
            return {"success": False, "message": "Item not found in shop"}
        
        if not item.can_afford(economy):
            return {"success": False, "message": "Not enough currency"}
        
        # Process the purchase
        if item.price_coins > 0:
            economy.remove_coins(item.price_coins)
            
        if item.price_gems > 0:
            economy.remove_gems(item.price_gems)
        
        # Handle different item types
        if item.item_type == "card":
            economy.unlock_card(item.id.replace("deal_", ""))
            return {
                "success": True, 
                "message": f"You purchased {item.name}!",
                "item_type": "card",
                "card_id": item.id.replace("deal_", "")
            }
        elif item.item_type == "pack":
            # For packs, generate random cards based on pack type
            cards = self._generate_pack_contents(item)
            for card_id in cards:
                economy.unlock_card(card_id)
                
            return {
                "success": True,
                "message": f"You opened a {item.name}!",
                "item_type": "pack",
                "cards": cards
            }
        
        return {"success": True, "message": f"You purchased {item.name}!"}
    
    def _generate_pack_contents(self, pack_item: ShopItem) -> List[str]:
        """Generate contents for a card pack."""
        # This is a simplified implementation - you would expand this
        # to actually generate cards based on the pack type
        cards = []
        
        # Filter items to just cards
        card_items = [item for item in self.all_items.values() if item.item_type == "card"]
        
        if not card_items:
            return cards
            
        # Basic pack: 5 common/uncommon cards
        if pack_item.id == "pack_basic":
            common_uncommon = [c for c in card_items if c.rarity in ["common", "uncommon"]]
            if common_uncommon:
                cards = [c.id for c in random.sample(
                    common_uncommon, 
                    min(5, len(common_uncommon))
                )]
        
        # Premium pack: 5 cards with at least 1 rare
        elif pack_item.id == "pack_premium":
            rare_plus = [c for c in card_items if c.rarity in ["rare", "epic"]]
            common_uncommon = [c for c in card_items if c.rarity in ["common", "uncommon"]]
            
            if rare_plus and common_uncommon:
                rare_cards = [c.id for c in random.sample(
                    rare_plus,
                    min(1, len(rare_plus))
                )]
                
                remaining = 5 - len(rare_cards)
                if remaining > 0:
                    common_cards = [c.id for c in random.sample(
                        common_uncommon,
                        min(remaining, len(common_uncommon))
                    )]
                    cards = rare_cards + common_cards
        
        return cards