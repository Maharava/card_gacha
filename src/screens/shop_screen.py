"""
Shop screen for the card game.
"""
import pygame
import os
import random

# Fixed imports
from src.screens.screen import Screen
from src.screens.ui_elements import Button, Label, Panel, CardRenderer
from src.utils.resource_loader import ResourceLoader
from src.utils.save_manager import SaveManager
from src.constants import (
    CARD_PACK_SIZE, CARD_PACK_COST, RARITY_PROBABILITIES,
    RARITY_COMMON, RARITY_UNCOMMON, RARITY_RARE, RARITY_EPIC
)


class ShopScreen(Screen):
    """
    Shop screen allowing players to:
    - Buy card packs with credits
    - View their current credit balance
    - See pack contents after purchase
    """
    
    def __init__(self, display, manager=None):
        """
        Initialize the shop screen.
        
        Args:
            display (pygame.Surface): The main display surface
            manager: The screen manager
        """
        super().__init__(display, manager)
        
        self.background_color = (30, 35, 45)
        
        # Card data
        self.card_database = {}
        self.player = None
        
        # Pack state
        self.generated_pack = []  # Cards currently offered in the pack
        self.show_pack_contents = False
        self.last_purchased_pack = []
        
        # Card renderer
        self.card_renderer = CardRenderer(card_size=(120, 180))
        
        # Create UI elements
        self._create_ui_elements()
    
    def _create_ui_elements(self):
        """Create the UI elements for the shop screen."""
        # Title
        title_panel = Panel(
            pygame.Rect(10, 10, self.width - 20, 60),
            color=(40, 45, 60),
            border_color=(80, 90, 120),
            border_width=2,
            rounded=True
        )
        
        title_label = Label(
            pygame.Rect(20, 0, 200, 60),
            "Card Shop",
            color=(220, 220, 220),
            font_size=32,
            align='left'
        )
        title_panel.add_element(title_label)
        
        # Credits display
        self.credits_label = Label(
            pygame.Rect(title_panel.rect.width - 220, 0, 200, 60),
            "Credits: 0",
            color=(255, 215, 0),  # Gold color
            font_size=24,
            align='right'
        )
        title_panel.add_element(self.credits_label)
        
        # Shop panel for displaying cards/packs
        shop_panel = Panel(
            pygame.Rect(10, 80, self.width - 20, self.height - 160),
            color=(40, 45, 60),
            border_color=(80, 90, 120),
            border_width=2,
            rounded=True
        )
        
        # Pack title
        self.pack_title = Label(
            pygame.Rect(0, 20, shop_panel.rect.width, 40),
            "Card Pack",
            color=(255, 215, 0),  # Gold color
            font_size=28,
            align='center'
        )
        shop_panel.add_element(self.pack_title)
        
        # Pack description
        self.pack_description = Label(
            pygame.Rect(0, 70, shop_panel.rect.width, 30),
            f"Contains {CARD_PACK_SIZE} random cards based on rarity distribution",
            color=(180, 180, 180),
            font_size=16,
            align='center'
        )
        shop_panel.add_element(self.pack_description)
        
        # Message label for displaying success/failure messages
        self.message_label = Label(
            pygame.Rect(0, shop_panel.rect.height - 40, shop_panel.rect.width, 30),
            "",
            color=(180, 180, 180),
            font_size=16,
            align='center'
        )
        shop_panel.add_element(self.message_label)
        
        # Buy button - centered on the screen
        self.buy_button = Button(
            pygame.Rect(shop_panel.rect.width // 2 - 125, shop_panel.rect.height - 100, 250, 50),
            f"Buy Pack ({CARD_PACK_COST} Credits)",
            self._buy_pack,
            color=(60, 120, 60),
            hover_color=(80, 160, 80),
            font_size=20
        )
        shop_panel.add_element(self.buy_button)
        
        # Back button
        back_button = Button(
            pygame.Rect(shop_panel.rect.width - 150, shop_panel.rect.height - 50, 120, 40),
            "Back to Menu",
            self._back_to_menu,
            color=(100, 100, 100),
            hover_color=(140, 140, 140),
            font_size=16
        )
        shop_panel.add_element(back_button)
        
        # Bottom panel for shop info
        info_panel = Panel(
            pygame.Rect(10, self.height - 70, self.width - 20, 60),
            color=(40, 45, 60),
            border_color=(80, 90, 120),
            border_width=2,
            rounded=True
        )
        
        # Shop info text
        shop_info = Label(
            pygame.Rect(20, 0, info_panel.rect.width - 40, 60),
            f"Each pack costs {CARD_PACK_COST} credits and contains {CARD_PACK_SIZE} cards. "
            f"Card rarities: Common (60%), Uncommon (25%), Rare (10%), Epic (5%). "
            f"Excess cards (beyond 3 copies) are automatically converted to credits.",
            color=(180, 180, 180),
            font_size=14,
            align='center'
        )
        info_panel.add_element(shop_info)
        
        # Add all panels to UI elements
        self.ui_elements = [title_panel, shop_panel, info_panel]
    
    def on_enter(self, previous_screen=None, **kwargs):
        """
        Called when this screen becomes active.
        
        Args:
            previous_screen: The screen that was active before
            **kwargs: Additional arguments
        """
        super().on_enter(previous_screen)
        
        # Load cards and player data
        self._load_data()
        
        # Generate a card pack
        self._generate_pack()
        
        # Reset view state
        self.show_pack_contents = False
        self.last_purchased_pack = []
        
        # Update UI
        self._update_ui()
    
    def _load_data(self):
        """Load card database and player data."""
        # Load card database
        self.card_database = ResourceLoader.load_cards()
        
        # Load player data
        if SaveManager.player_exists():
            self.player = SaveManager.load_player(self.card_database)
        
        # Load card images for renderer
        for card_id, card in self.card_database.items():
            self.card_renderer.load_card_image(card_id, card.image_path)
    
    def _update_ui(self):
        """Update UI elements based on the current state."""
        if not self.player:
            return
        
        # Update credits display
        self.credits_label.set_text(f"Credits: {self.player.credits}")
        
        # Update buy button state
        if self.player.credits >= CARD_PACK_COST:
            self.buy_button.enabled = True
        else:
            self.buy_button.enabled = False
            
        # Update UI based on whether we're showing pack contents
        if self.show_pack_contents:
            self.pack_title.set_text("Pack Contents")
            self.pack_description.set_text("You got these cards!")
            self.buy_button.text = "Buy Another Pack"
        else:
            self.pack_title.set_text("Card Pack")
            self.pack_description.set_text(f"Contains {CARD_PACK_SIZE} random cards based on rarity distribution")
            self.buy_button.text = f"Buy Pack ({CARD_PACK_COST} Credits)"
    
    def _generate_pack(self):
        """Generate a new card pack with random cards."""
        if not self.card_database:
            return
        
        self.generated_pack = []
        
        # Group cards by rarity
        cards_by_rarity = {
            RARITY_COMMON: [],
            RARITY_UNCOMMON: [],
            RARITY_RARE: [],
            RARITY_EPIC: []
        }
        
        for card_id, card in self.card_database.items():
            if card.rarity in cards_by_rarity:
                cards_by_rarity[card.rarity].append(card)
        
        # Generate pack cards
        for _ in range(CARD_PACK_SIZE):
            # Determine rarity based on probabilities
            rarity = self._select_random_rarity()
            
            # Get cards of this rarity
            rarity_cards = cards_by_rarity.get(rarity, [])
            
            # If no cards of this rarity, pick from common
            if not rarity_cards:
                rarity_cards = cards_by_rarity.get(RARITY_COMMON, [])
            
            # If still no cards, skip
            if not rarity_cards:
                continue
            
            # Pick a random card
            card = random.choice(rarity_cards)
            self.generated_pack.append(card)
    
    def _select_random_rarity(self):
        """
        Select a random rarity based on probabilities.
        
        Returns:
            str: Selected rarity
        """
        roll = random.random()
        cumulative = 0
        
        # Check each rarity probability
        for rarity, probability in RARITY_PROBABILITIES.items():
            cumulative += probability
            if roll <= cumulative:
                return rarity
        
        # Default to common if something goes wrong
        return RARITY_COMMON
    
    def _buy_pack(self):
        """Buy the current card pack."""
        if not self.player:
            return
        
        # If showing pack contents, generate a new pack and reset view
        if self.show_pack_contents:
            self._generate_pack()
            self.show_pack_contents = False
            self._update_ui()
            return
        
        # Check if player has enough credits
        if self.player.credits < CARD_PACK_COST:
            self.message_label.set_text("Not enough credits!")
            self.message_label.color = (255, 100, 100)  # Red for error
            return
        
        # Subtract credits
        self.player.credits -= CARD_PACK_COST
        
        # Process the cards from the pack
        self.last_purchased_pack = []
        cards_added = []
        cards_converted = []
        total_credits_from_conversion = 0
        
        for card in self.generated_pack:
            # Add to collection, handling potential conversion
            added, credits = self.player.add_to_collection(card.id)
            
            if added > 0:
                cards_added.append(card.name)
            
            if credits > 0:
                cards_converted.append((card.name, credits))
                total_credits_from_conversion += credits
                
            # Remember the card for display
            self.last_purchased_pack.append(card)
        
        # Prepare success message
        if cards_added and cards_converted:
            message = f"Pack purchased! Added {len(cards_added)} cards to collection. "
            message += f"Converted {len(cards_converted)} excess cards for {total_credits_from_conversion} credits."
            self.message_label.color = (100, 255, 100)  # Green for success
        elif cards_added:
            message = f"Pack purchased! Added {len(cards_added)} new cards to your collection."
            self.message_label.color = (100, 255, 100)  # Green for success
        elif cards_converted:
            message = f"Pack purchased! All cards were duplicates and converted to {total_credits_from_conversion} credits."
            self.message_label.color = (255, 215, 0)  # Gold for conversion
        else:
            message = "Pack purchased!"
            self.message_label.color = (100, 255, 100)  # Green for success
        
        self.message_label.set_text(message)
        
        # Show pack contents
        self.show_pack_contents = True
        
        # Save player data
        SaveManager.save_player(self.player)
        
        # Update UI
        self._update_ui()
    
    def _back_to_menu(self):
        """Return to the main menu."""
        # Save player data before leaving
        if self.player:
            SaveManager.save_player(self.player)
        
        # Return to home screen
        self.switch_to_screen("home")
    
    def render(self):
        """Render the shop screen."""
        # Draw background
        self.display.fill(self.background_color)
        
        # Render UI elements
        for element in self.ui_elements:
            element.render(self.display)
        
        # Render the card pack or its contents
        self._render_pack()
    
    def _render_pack(self):
        """Render either the card pack or its contents after purchase."""
        # Shop panel is the main panel
        panel_rect = self.ui_elements[1].rect  # 1 is the shop panel
        
        if self.show_pack_contents and self.last_purchased_pack:
            # Show the cards that were in the pack
            self._render_pack_contents(panel_rect)
        else:
            # Show a pack visual
            self._render_pack_visual(panel_rect)
    
    def _render_pack_contents(self, panel_rect):
        """Render the contents of a purchased pack."""
        # Arrange cards in a row
        num_cards = len(self.last_purchased_pack)
        card_width, card_height = self.card_renderer.card_size
        
        total_width = num_cards * (card_width + 20) - 20
        start_x = (panel_rect.width - total_width) // 2 + panel_rect.left
        y = panel_rect.top + 120
        
        for i, card in enumerate(self.last_purchased_pack):
            x = start_x + i * (card_width + 20)
            self.card_renderer.render_card(self.display, card, (x, y))
    
    def _render_pack_visual(self, panel_rect):
        """Render a visual representation of a card pack."""
        # Draw a pack rectangle
        pack_rect = pygame.Rect(
            panel_rect.centerx - 100,
            panel_rect.top + 120,
            200,
            250
        )
        
        # Draw pack background
        pygame.draw.rect(self.display, (60, 50, 80), pack_rect, border_radius=10)
        pygame.draw.rect(self.display, (120, 100, 160), pack_rect, width=3, border_radius=10)
        
        # Draw pack design
        inner_rect = pygame.Rect(
            pack_rect.left + 20,
            pack_rect.top + 20,
            pack_rect.width - 40,
            pack_rect.height - 40
        )
        pygame.draw.rect(self.display, (80, 70, 100), inner_rect, border_radius=5)
        
        # Draw pack title
        font = pygame.freetype.SysFont('Arial', 24, bold=True)
        pack_text, pack_rect = font.render("CARD PACK", (255, 220, 120))
        pack_rect.center = (panel_rect.centerx, panel_rect.top + 170)
        self.display.blit(pack_text, pack_rect)
        
        # Draw card count
        count_text, count_rect = font.render(f"{CARD_PACK_SIZE} CARDS", (220, 220, 220))
        count_rect.center = (panel_rect.centerx, panel_rect.top + 210)
        self.display.blit(count_text, count_rect)
        
        # Draw some decorative elements
        pygame.draw.rect(
            self.display, 
            (180, 160, 200),
            (panel_rect.centerx - 80, panel_rect.top + 250, 160, 3),
            border_radius=1
        )
        
        pygame.draw.rect(
            self.display, 
            (180, 160, 200),
            (panel_rect.centerx - 80, panel_rect.top + 290, 160, 3),
            border_radius=1
        )
        
        # Draw rarity indicators
        rarity_font = pygame.freetype.SysFont('Arial', 14)
        rarities = [
            ("Common: 60%", (255, 255, 255)),
            ("Uncommon: 25%", (100, 255, 100)),
            ("Rare: 10%", (100, 100, 255)),
            ("Epic: 5%", (255, 100, 255))
        ]
        
        for i, (text, color) in enumerate(rarities):
            rarity_text, rarity_rect = rarity_font.render(text, color)
            rarity_rect.center = (panel_rect.centerx, panel_rect.top + 320 + i * 20)
            self.display.blit(rarity_text, rarity_rect)
    
    def load_resources(self):
        """Load screen-specific resources."""
        # Load background image if available
        try:
            bg_path = os.path.join("assets", "images", "backgrounds", "shop_bg.jpg")
            self.resources["background"] = pygame.image.load(bg_path)
            self.resources["background"] = pygame.transform.scale(
                self.resources["background"], (self.width, self.height)
            )
        except (pygame.error, FileNotFoundError):
            # No specific handling needed, we'll use the solid color background
            pass