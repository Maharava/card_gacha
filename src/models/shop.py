from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random
import json
import os
import time
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
    item_type: str = "card"  # card, pack, cosmetic, etc.
    rarity: str = "common"   # common, uncommon, rare, epic
    
    def can_afford(self, economy: PlayerEconomy) -> bool:
        """Check if player can afford this item."""
        return economy.coins >= self.price_coins


class ShopManager:
    """Manages the shop and its inventory."""
    
    def __init__(self):
        self.all_items: Dict[str, ShopItem] = {}
        self.current_inventory: List[ShopItem] = []
        self.last_refresh = datetime.now() - timedelta(days=1)  # Force refresh on start
        self.last_pack_purchase_time = 0  # Track time of last pack purchase
        self.card_data = {}  # Will store cards from cards.json
        self.cards_by_rarity = {
            "common": [],
            "uncommon": [],
            "rare": [],
            "epic": []
        }
        self._load_card_data()
        self._load_shop_items()
    
    def _load_card_data(self):
        """Load all card data from cards.json"""
        try:
            file_path = os.path.join("data", "cards.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.card_data = json.load(f)
                    
                # Organize cards by rarity
                for card_id, card_info in self.card_data.items():
                    rarity = card_info.get("rarity", "common")
                    if rarity in self.cards_by_rarity:
                        self.cards_by_rarity[rarity].append(card_id)
                        
                print(f"Loaded {len(self.card_data)} cards from cards.json")
                for rarity, cards in self.cards_by_rarity.items():
                    print(f"  {rarity}: {len(cards)} cards")
            else:
                print("Warning: cards.json not found!")
        except Exception as e:
            print(f"Error loading card data: {e}")
    
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
        # Generate three identical packs but with different IDs
        default_items = []
        
        for i in range(3):
            # Random pack image from pack_1.png to pack_6.png
            random_pack_num = random.randint(1, 6)
            pack_image = f"data/assets/gui/pack_{random_pack_num}.png"
            
            default_items.append(ShopItem(
                id=f"pack_{i+1}",
                name="Card Pack",
                description="Contains 5 cards of random rarities",
                image=pack_image,
                price_coins=30,  # All packs cost 30 credits
                item_type="pack",
                rarity="common"
            ))
        
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
        
        # Update pack images with random ones
        for item in self.all_items.values():
            if item.item_type == "pack":
                random_pack_num = random.randint(1, 6)
                item.image = f"data/assets/gui/pack_{random_pack_num}.png"
        
        # Just select all packs for the inventory
        self.current_inventory = [item for item in self.all_items.values() if item.item_type == "pack"]
        
        return True
    
    def _refresh_pack(self, pack_id: str) -> None:
        """Refresh a specific pack after purchase."""
        # Find the pack in inventory
        for i, item in enumerate(self.current_inventory):
            if item.id == pack_id:
                # Choose a new random pack image
                random_pack_num = random.randint(1, 6)
                item.image = f"data/assets/gui/pack_{random_pack_num}.png"
                return
    
    def purchase_item(self, item_id: str, economy: PlayerEconomy) -> Dict:
        """Process a purchase. Returns result information."""
        # Find the item in current inventory
        item = next((i for i in self.current_inventory if i.id == item_id), None)
        
        if not item:
            return {"success": False, "message": "Item not found in shop"}
        
        if not item.can_afford(economy):
            return {"success": False, "message": "Not enough coins"}
        
        # Check cooldown for packs
        current_time = time.time()
        if (current_time - self.last_pack_purchase_time) < 2:
            return {"success": False, "message": "Please wait before purchasing another pack"}
        
        # Process the purchase
        economy.remove_coins(item.price_coins)
        
        # Update last purchase time for cooldown
        self.last_pack_purchase_time = current_time
        
        # Generate random cards based on rarity probabilities
        cards = self._generate_pack_contents()
        for card_id in cards:
            economy.unlock_card(card_id)
            
        # Refresh this pack immediately
        self._refresh_pack(item.id)
            
        return {
            "success": True,
            "message": f"You opened a {item.name}!",
            "item_type": "pack",
            "cards": cards
        }
    
    def _generate_pack_contents(self) -> List[str]:
        """Generate contents for a card pack using rarity probabilities."""
        cards = []
        
        # Check if we have card data
        if not self.card_data:
            print("Warning: No card data available for pack generation")
            return cards
        
        # Generate 5 cards with probability distribution
        for _ in range(5):
            rng = random.random() * 100
            
            if rng < 55 and self.cards_by_rarity["common"]:  # 55% common
                card_id = random.choice(self.cards_by_rarity["common"])
            elif rng < 80 and self.cards_by_rarity["uncommon"]:  # 25% uncommon
                card_id = random.choice(self.cards_by_rarity["uncommon"])
            elif rng < 95 and self.cards_by_rarity["rare"]:  # 15% rare
                card_id = random.choice(self.cards_by_rarity["rare"])
            elif self.cards_by_rarity["epic"]:  # 5% epic
                card_id = random.choice(self.cards_by_rarity["epic"])
            elif self.cards_by_rarity["rare"]:  # Fallback if no epic cards
                card_id = random.choice(self.cards_by_rarity["rare"])
            elif self.cards_by_rarity["uncommon"]:  # Fallback if no rare cards
                card_id = random.choice(self.cards_by_rarity["uncommon"])
            elif self.cards_by_rarity["common"]:  # Fallback if no uncommon cards
                card_id = random.choice(self.cards_by_rarity["common"])
            else:
                print("Warning: No cards found for pack generation")
                continue
                
            cards.append(card_id)
        
        return cards