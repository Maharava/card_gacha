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
from src.constants import SHOP_CARDS_OFFERED, SHOP_COST, RARITY_PROBABILITIES


class ShopScreen(Screen):
    """
    Shop screen allowing players to:
    - Buy new cards with credits
    - View cards before purchasing
    - See their current credit balance
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
        
        # Shop state
        self.shop_cards = []  # Cards currently offered in the shop
        self.selected_card = None
        
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
        
        # Shop panel for displaying cards
        shop_panel = Panel(
            pygame.Rect(10, 80, self.width - 220, self.height - 160),
            color=(40, 45, 60),
            border_color=(80, 90, 120),
            border_width=2,
            rounded=True
        )
        
        # Instruction label
        instruction_label = Label(
            pygame.Rect(20, 10, shop_panel.rect.width - 40, 30),
            "Click on a card to select it, then click 'Buy' to purchase.",
            color=(180, 180, 180),
            font_size=16,
            align='center'
        )
        shop_panel.add_element(instruction_label)
        
        # Message label for displaying success/failure messages
        self.message_label = Label(
            pygame.Rect(20, shop_panel.rect.height - 40, shop_panel.rect.width - 40, 30),
            "",
            color=(180, 180, 180),
            font_size=16,
            align='center'
        )
        shop_panel.add_element(self.message_label)
        
        # Right panel for card details and controls
        detail_panel = Panel(
            pygame.Rect(self.width - 200, 80, 190, self.height - 160),
            color=(40, 45, 60),
            border_color=(80, 90, 120),
            border_width=2,
            rounded=True
        )
        
        # Card details (will be rendered directly)
        detail_label = Label(
            pygame.Rect(0, 10, 190, 30),
            "Card Details",
            color=(220, 220, 220),
            font_size=20,
            align='center'
        )
        detail_panel.add_element(detail_label)
        
        # Buy button
        self.buy_button = Button(
            pygame.Rect(20, detail_panel.rect.height - 160, 150, 40),
            f"Buy ({SHOP_COST} Credits)",
            self._buy_selected_card,
            color=(60, 120, 60),
            hover_color=(80, 160, 80),
            font_size=16
        )
        detail_panel.add_element(self.buy_button)
        
        # Refresh button
        self.refresh_button = Button(
            pygame.Rect(20, detail_panel.rect.height - 110, 150, 40),
            f"Refresh Shop",
            self._refresh_shop,
            color=(60, 60, 120),
            hover_color=(80, 80, 160),
            font_size=16
        )
        detail_panel.add_element(self.refresh_button)
        
        # Back button
        back_button = Button(
            pygame.Rect(20, detail_panel.rect.height - 60, 150, 40),
            "Back to Menu",
            self._back_to_menu,
            color=(100, 100, 100),
            hover_color=(140, 140, 140),
            font_size=16
        )
        detail_panel.add_element(back_button)
        
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
            f"The shop offers {SHOP_CARDS_OFFERED} random cards. "
            f"Each purchase costs {SHOP_COST} credits. "
            f"Card rarities: Common (60%), Uncommon (25%), Rare (10%), Epic (5%)",
            color=(180, 180, 180),
            font_size=14,
            align='center'
        )
        info_panel.add_element(shop_info)
        
        # Add all panels to UI elements
        self.ui_elements = [title_panel, shop_panel, detail_panel, info_panel]
    
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
        
        # Generate shop offerings
        self._generate_shop_cards()
        
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
        if self.selected_card and self.player.credits >= SHOP_COST:
            self.buy_button.enabled = True
        else:
            self.buy_button.enabled = False
    
    def _generate_shop_cards(self):
        """Generate random cards for the shop."""
        if not self.card_database:
            return
        
        self.shop_cards = []
        
        # Group cards by rarity
        cards_by_rarity = {
            "common": [],
            "uncommon": [],
            "rare": [],
            "epic": []
        }
        
        for card_id, card in self.card_database.items():
            if card.rarity in cards_by_rarity:
                cards_by_rarity[card.rarity].append(card)
        
        # Generate shop cards
        for _ in range(SHOP_CARDS_OFFERED):
            # Determine rarity based on probabilities
            rarity = self._select_random_rarity()
            
            # Get cards of this rarity
            rarity_cards = cards_by_rarity.get(rarity, [])
            
            # If no cards of this rarity, pick from common
            if not rarity_cards:
                rarity_cards = cards_by_rarity.get("common", [])
            
            # If still no cards, skip
            if not rarity_cards:
                continue
            
            # Pick a random card
            card = random.choice(rarity_cards)
            self.shop_cards.append(card)
    
    def _select_random_rarity(self):
        """
        Select a random rarity based on probabilities.
        
        Returns:
            str: Selected rarity
        """
        """
        Select a random rarity based on probabilities.
        
        Returns:
            str: Selected rarity
        """
        roll = random.random()
        cumulative = 0
        
        # Sort probabilities in descending order
        for rarity, probability in sorted(RARITY_PROBABILITIES.items(), key=lambda x: x[1], reverse=True):
            cumulative += probability
            if roll <= cumulative:
                return rarity
        
        # Default to common if something goes wrong
        return "common"
    
    def _buy_selected_card(self):
        """Buy the currently selected card."""
        if not self.player or not self.selected_card:
            return
        
        # Check if player has enough credits
        if self.player.credits < SHOP_COST:
            self.message_label.set_text("Not enough credits!")
            return
        
        # Subtract credits
        self.player.credits -= SHOP_COST
        
        # Add card to collection
        self.player.add_to_collection(self.selected_card.id)
        
        # Show success message
        self.message_label.set_text(f"Successfully purchased {self.selected_card.name}!")
        
        # Remove the card from the shop
        if self.selected_card in self.shop_cards:
            self.shop_cards.remove(self.selected_card)
        
        # Clear selection
        self.selected_card = None
        
        # Save player data
        SaveManager.save_player(self.player)
        
        # Update UI
        self._update_ui()
        
        # If shop is empty, generate new cards
        if not self.shop_cards:
            self._generate_shop_cards()
    
    def _refresh_shop(self):
        """Refresh the shop with new cards."""
        self._generate_shop_cards()
        self.selected_card = None
        self.message_label.set_text("Shop refreshed with new cards!")
    
    def _back_to_menu(self):
        """Return to the main menu."""
        # Save player data before leaving
        if self.player:
            SaveManager.save_player(self.player)
        
        # Return to home screen
        self.switch_to_screen("home")
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event (pygame.event.Event): The event to handle
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        # First check if UI elements handle the event
        if super().handle_event(event):
            return True
        
        # Handle mouse clicks on shop cards
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicked on a shop card
            for i, card in enumerate(self.shop_cards):
                card_rect = self._get_shop_card_rect(i)
                
                if card_rect.collidepoint(event.pos):
                    # Select this card
                    self.selected_card = card
                    self._update_ui()
                    return True
        
        return False
    
    def _get_shop_card_rect(self, index):
        """
        Get the rectangle for a card in the shop.
        
        Args:
            index (int): Index of the card
            
        Returns:
            pygame.Rect: Rectangle for the card
        """
        # Card size
        card_width, card_height = self.card_renderer.card_size
        
        # Shop panel position and size
        panel_rect = self.ui_elements[1].rect  # 1 is the shop panel
        
        # Layout: 5 cards in a row, possibly multiple rows
        cols = 5
        col = index % cols
        row = index // cols
        
        # Calculate position
        margin_x = (panel_rect.width - (cols * card_width)) // (cols + 1)
        margin_y = 30
        x = panel_rect.left + margin_x + col * (card_width + margin_x)
        y = panel_rect.top + 50 + row * (card_height + margin_y)
        
        return pygame.Rect(x, y, card_width, card_height)
    
    def render(self):
        """Render the shop screen."""
        # Draw background
        self.display.fill(self.background_color)
        
        # Render UI elements
        for element in self.ui_elements:
            element.render(self.display)
        
        # Render shop cards
        self._render_shop_cards()
        
        # Render selected card details
        self._render_card_details()
    
    def _render_shop_cards(self):
        """Render the cards offered in the shop."""
        for i, card in enumerate(self.shop_cards):
            card_rect = self._get_shop_card_rect(i)
            
            # Draw the card
            self.card_renderer.render_card(
                self.display, 
                card, 
                (card_rect.left, card_rect.top),
                selectable=True,
                selected=card == self.selected_card
            )
    
    def _render_card_details(self):
        """Render details of the selected card."""
        if not self.selected_card:
            return
        
        # Detail panel
        detail_panel = self.ui_elements[2].rect  # 2 is the detail panel
        
        # Card preview at the top of the detail panel
        card_x = detail_panel.left + (detail_panel.width - self.card_renderer.card_size[0]) // 2
        card_y = detail_panel.top + 50
        
        self.card_renderer.render_card(
            self.display,
            self.selected_card,
            (card_x, card_y)
        )
        
        # Card stats below the preview
        stats_y = card_y + self.card_renderer.card_size[1] + 10
        
        font = pygame.freetype.SysFont('Arial', 14)
        
        # Card name
        name_surf, name_rect = font.render(f"Name: {self.selected_card.name}", (220, 220, 220))
        name_rect.midtop = (detail_panel.centerx, stats_y)
        self.display.blit(name_surf, name_rect)
        
        # Card rarity
        rarity_surf, rarity_rect = font.render(f"Rarity: {self.selected_card.rarity.capitalize()}", (220, 220, 220))
        rarity_rect.midtop = (detail_panel.centerx, stats_y + 20)
        self.display.blit(rarity_surf, rarity_rect)
        
        # Card stats
        stats_surf, stats_rect = font.render(f"Cost: {self.selected_card.cost} | ATK: {self.selected_card.attack} | HP: {self.selected_card.hp}", (220, 220, 220))
        stats_rect.midtop = (detail_panel.centerx, stats_y + 40)
        self.display.blit(stats_surf, stats_rect)
        
        # Card flavor text (wrapped)
        flavor_y = stats_y + 70
        flavor_font = pygame.freetype.SysFont('Arial', 12, italic=True)
        
        wrapped_flavor = self._wrap_text(self.selected_card.flavor_text, flavor_font, detail_panel.width - 20)
        
        for i, line in enumerate(wrapped_flavor):
            flavor_surf, flavor_rect = flavor_font.render(line, (180, 180, 180))
            flavor_rect.midtop = (detail_panel.centerx, flavor_y + i * 20)
            self.display.blit(flavor_surf, flavor_rect)
    
    def _wrap_text(self, text, font, max_width):
        """
        Wrap text to fit within a given width.
        
        Args:
            text (str): Text to wrap
            font: Font to use for measuring
            max_width (int): Maximum width in pixels
            
        Returns:
            list: List of wrapped text lines
        """
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Test width with this word added
            test_line = ' '.join(current_line + [word])
            test_surf, test_rect = font.render(test_line, (0, 0, 0))
            
            if test_rect.width <= max_width:
                current_line.append(word)
            else:
                # Add the current line to lines and start a new line
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
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