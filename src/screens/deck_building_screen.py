"""
Deck building screen for the card game.
"""
import pygame
import os

# Fixed imports
from src.screens.screen import Screen
from src.screens.ui_elements import Button, Label, Panel, CardRenderer
from src.models.deck import Deck
from src.utils.resource_loader import ResourceLoader
from src.utils.save_manager import SaveManager


class DeckBuildingScreen(Screen):
    """
    Deck building screen allowing players to:
    - View their card collection
    - Create and modify decks
    - Sort and filter cards
    """
    
    def __init__(self, display, manager=None):
        """
        Initialize the deck building screen.
        
        Args:
            display (pygame.Surface): The main display surface
            manager: The screen manager
        """
        super().__init__(display, manager)
        
        self.background_color = (30, 35, 45)
        
        # Card data
        self.card_database = {}
        self.player = None
        self.current_deck = None
        
        # Collection view state
        self.collection_page = 0
        self.cards_per_page = 8
        self.current_rarity_filter = "all"
        self.sort_method = "name"  # name, cost, rarity
        self.selected_collection_card = None
        
        # Deck view state
        self.deck_page = 0
        self.selected_deck_card = None
        
        # Card renderer
        self.card_renderer = CardRenderer(card_size=(100, 150))
        
        # Create UI elements
        self._create_ui_elements()
    
    def _create_ui_elements(self):
        """Create the UI elements for the deck building screen."""
        # Title
        title_panel = Panel(
            pygame.Rect(10, 10, self.width - 20, 60),
            color=(40, 45, 60),
            border_color=(80, 90, 120),
            border_width=2,
            rounded=True
        )
        
        title_label = Label(
            pygame.Rect(0, 0, self.width - 20, 60),
            "Deck Builder",
            color=(220, 220, 220),
            font_size=32,
            align='center'
        )
        title_panel.add_element(title_label)
        
        # Left panel for collection
        collection_panel = Panel(
            pygame.Rect(10, 80, (self.width - 30) // 2, self.height - 150),
            color=(40, 45, 60),
            border_color=(80, 90, 120),
            border_width=2,
            rounded=True
        )
        
        # Collection title
        collection_title = Label(
            pygame.Rect(20, 10, 200, 30),
            "Your Collection",
            color=(220, 220, 220),
            font_size=22,
            align='left'
        )
        collection_panel.add_element(collection_title)
        
        # Collection count
        self.collection_count = Label(
            pygame.Rect(collection_panel.rect.width - 120, 10, 100, 30),
            "Cards: 0",
            color=(180, 180, 180),
            font_size=18,
            align='right'
        )
        collection_panel.add_element(self.collection_count)
        
        # Filter buttons
        filter_label = Label(
            pygame.Rect(20, 50, 80, 25),
            "Filter:",
            color=(180, 180, 180),
            font_size=16,
            align='left'
        )
        collection_panel.add_element(filter_label)
        
        # Filter by rarity buttons
        button_width = 80
        button_spacing = 10
        button_y = 50
        
        all_button = Button(
            pygame.Rect(100, button_y, button_width, 25),
            "All",
            lambda: self._set_rarity_filter("all"),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(all_button)
        
        common_button = Button(
            pygame.Rect(100 + (button_width + button_spacing), button_y, button_width, 25),
            "Common",
            lambda: self._set_rarity_filter("common"),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(common_button)
        
        uncommon_button = Button(
            pygame.Rect(100 + (button_width + button_spacing) * 2, button_y, button_width, 25),
            "Uncommon",
            lambda: self._set_rarity_filter("uncommon"),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(uncommon_button)
        
        # Sort buttons
        sort_label = Label(
            pygame.Rect(20, 85, 80, 25),
            "Sort by:",
            color=(180, 180, 180),
            font_size=16,
            align='left'
        )
        collection_panel.add_element(sort_label)
        
        name_button = Button(
            pygame.Rect(100, 85, button_width, 25),
            "Name",
            lambda: self._set_sort_method("name"),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(name_button)
        
        cost_button = Button(
            pygame.Rect(100 + (button_width + button_spacing), 85, button_width, 25),
            "Cost",
            lambda: self._set_sort_method("cost"),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(cost_button)
        
        rarity_button = Button(
            pygame.Rect(100 + (button_width + button_spacing) * 2, 85, button_width, 25),
            "Rarity",
            lambda: self._set_sort_method("rarity"),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(rarity_button)
        
        # Page navigation
        prev_page_button = Button(
            pygame.Rect(20, collection_panel.rect.height - 40, 120, 30),
            "< Previous",
            self._prev_collection_page,
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=16
        )
        collection_panel.add_element(prev_page_button)
        
        next_page_button = Button(
            pygame.Rect(collection_panel.rect.width - 140, collection_panel.rect.height - 40, 120, 30),
            "Next >",
            self._next_collection_page,
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=16
        )
        collection_panel.add_element(next_page_button)
        
        self.page_label = Label(
            pygame.Rect(0, collection_panel.rect.height - 40, collection_panel.rect.width, 30),
            "Page 1",
            color=(180, 180, 180),
            font_size=16,
            align='center'
        )
        collection_panel.add_element(self.page_label)
        
        # Right panel for deck
        deck_panel = Panel(
            pygame.Rect(10 + (self.width - 30) // 2 + 10, 80, (self.width - 30) // 2, self.height - 150),
            color=(40, 45, 60),
            border_color=(80, 90, 120),
            border_width=2,
            rounded=True
        )
        
        # Deck title
        self.deck_title = Label(
            pygame.Rect(20, 10, 200, 30),
            "Current Deck",
            color=(220, 220, 220),
            font_size=22,
            align='left'
        )
        deck_panel.add_element(self.deck_title)
        
        # Deck count
        self.deck_count = Label(
            pygame.Rect(deck_panel.rect.width - 120, 10, 100, 30),
            "Cards: 0/30",
            color=(180, 180, 180),
            font_size=18,
            align='right'
        )
        deck_panel.add_element(self.deck_count)
        
        # Deck page navigation
        prev_deck_page_button = Button(
            pygame.Rect(20, deck_panel.rect.height - 40, 120, 30),
            "< Previous",
            self._prev_deck_page,
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=16
        )
        deck_panel.add_element(prev_deck_page_button)
        
        next_deck_page_button = Button(
            pygame.Rect(deck_panel.rect.width - 140, deck_panel.rect.height - 40, 120, 30),
            "Next >",
            self._next_deck_page,
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=16
        )
        deck_panel.add_element(next_deck_page_button)
        
        self.deck_page_label = Label(
            pygame.Rect(0, deck_panel.rect.height - 40, deck_panel.rect.width, 30),
            "Page 1",
            color=(180, 180, 180),
            font_size=16,
            align='center'
        )
        deck_panel.add_element(self.deck_page_label)
        
        # Bottom panel for controls
        control_panel = Panel(
            pygame.Rect(10, self.height - 60, self.width - 20, 50),
            color=(40, 45, 60),
            border_color=(80, 90, 120),
            border_width=2,
            rounded=True
        )
        
        # Save button
        save_button = Button(
            pygame.Rect(20, 10, 150, 30),
            "Save Deck",
            self._save_deck,
            color=(60, 120, 60),
            hover_color=(80, 160, 80),
            font_size=18
        )
        control_panel.add_element(save_button)
        
        # New deck button
        new_deck_button = Button(
            pygame.Rect(190, 10, 150, 30),
            "New Deck",
            self._new_deck,
            color=(60, 60, 120),
            hover_color=(80, 80, 160),
            font_size=18
        )
        control_panel.add_element(new_deck_button)
        
        # Clear deck button
        clear_deck_button = Button(
            pygame.Rect(360, 10, 150, 30),
            "Clear Deck",
            self._clear_deck,
            color=(120, 60, 60),
            hover_color=(160, 80, 80),
            font_size=18
        )
        control_panel.add_element(clear_deck_button)
        
        # Back button
        back_button = Button(
            pygame.Rect(control_panel.rect.width - 170, 10, 150, 30),
            "Back to Menu",
            self._back_to_menu,
            color=(100, 100, 100),
            hover_color=(140, 140, 140),
            font_size=18
        )
        control_panel.add_element(back_button)
        
        # Add all panels to UI elements
        self.ui_elements = [title_panel, collection_panel, deck_panel, control_panel]
    
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
        
        # Reset view state
        self.collection_page = 0
        self.deck_page = 0
        self.current_rarity_filter = "all"
        self.sort_method = "name"
        self.selected_collection_card = None
        self.selected_deck_card = None
        
        # Update UI
        self._update_ui()
    
    def _load_data(self):
        """Load card database and player data."""
        # Load card database
        self.card_database = ResourceLoader.load_cards()
        
        # Load player data
        if SaveManager.player_exists():
            self.player = SaveManager.load_player(self.card_database)
            
            # Set current deck to player's deck
            if self.player:
                self.current_deck = self.player.deck
        
        # Load card images for renderer
        for card_id, card in self.card_database.items():
            self.card_renderer.load_card_image(card_id, card.image_path)
    
    def _update_ui(self):
        """Update UI elements based on the current state."""
        if not self.player or not self.current_deck:
            return
        
        # Update collection count
        total_cards = sum(self.player.collection.values())
        self.collection_count.set_text(f"Cards: {total_cards}")
        
        # Update deck info
        self.deck_title.set_text(f"Deck: {self.current_deck.name}")
        self.deck_count.set_text(f"Cards: {self.current_deck.size()}/30")
        
        # Update page labels
        filtered_cards = self._get_filtered_cards()
        total_collection_pages = max(1, (len(filtered_cards) + self.cards_per_page - 1) // self.cards_per_page)
        self.page_label.set_text(f"Page {self.collection_page + 1}/{total_collection_pages}")
        
        total_deck_pages = max(1, (self.current_deck.size() + self.cards_per_page - 1) // self.cards_per_page)
        self.deck_page_label.set_text(f"Page {self.deck_page + 1}/{total_deck_pages}")
    
    def _get_filtered_cards(self):
        """
        Get the filtered and sorted list of cards from the player's collection.
        
        Returns:
            list: List of (card, quantity) tuples
        """
        if not self.player:
            return []
        
        filtered_cards = []
        
        for card_id, quantity in self.player.collection.items():
            if card_id in self.card_database:
                card = self.card_database[card_id]
                
                # Apply rarity filter
                if self.current_rarity_filter == "all" or card.rarity == self.current_rarity_filter:
                    filtered_cards.append((card, quantity))
        
        # Apply sorting
        if self.sort_method == "name":
            filtered_cards.sort(key=lambda x: x[0].name)
        elif self.sort_method == "cost":
            filtered_cards.sort(key=lambda x: x[0].cost)
        elif self.sort_method == "rarity":
            rarity_order = {"common": 0, "uncommon": 1, "rare": 2, "epic": 3}
            filtered_cards.sort(key=lambda x: rarity_order.get(x[0].rarity, 0))
        
        return filtered_cards
    
    def _set_rarity_filter(self, rarity):
        """
        Set the rarity filter.
        
        Args:
            rarity (str): Rarity to filter by
        """
        self.current_rarity_filter = rarity
        self.collection_page = 0  # Reset to first page
        self._update_ui()
    
    def _set_sort_method(self, method):
        """
        Set the sort method.
        
        Args:
            method (str): Sort method to use
        """
        self.sort_method = method
        self._update_ui()
    
    def _prev_collection_page(self):
        """Go to the previous page of the collection."""
        if self.collection_page > 0:
            self.collection_page -= 1
            self._update_ui()
    
    def _next_collection_page(self):
        """Go to the next page of the collection."""
        filtered_cards = self._get_filtered_cards()
        total_pages = max(1, (len(filtered_cards) + self.cards_per_page - 1) // self.cards_per_page)
        
        if self.collection_page < total_pages - 1:
            self.collection_page += 1
            self._update_ui()
    
    def _prev_deck_page(self):
        """Go to the previous page of the deck."""
        if self.deck_page > 0:
            self.deck_page -= 1
            self._update_ui()
    
    def _next_deck_page(self):
        """Go to the next page of the deck."""
        if not self.current_deck:
            return
        
        total_pages = max(1, (self.current_deck.size() + self.cards_per_page - 1) // self.cards_per_page)
        
        if self.deck_page < total_pages - 1:
            self.deck_page += 1
            self._update_ui()
    
    def _save_deck(self):
        """Save the current deck to the player's data."""
        if not self.player or not self.current_deck:
            return
        
        # Update the player's deck
        self.player.deck = self.current_deck
        
        # Save player data
        SaveManager.save_player(self.player)
    
    def _new_deck(self):
        """Create a new empty deck."""
        if not self.player:
            return
        
        # Create a deck name input dialog
        self._show_deck_name_dialog()
    
    def _show_deck_name_dialog(self):
        """Show a dialog to input the new deck name."""
        # Create dialog panel
        dialog_panel = Panel(
            pygame.Rect(self.width // 2 - 150, self.height // 2 - 100, 300, 200),
            color=(50, 55, 70),
            border_color=(100, 110, 140),
            border_width=2,
            rounded=True
        )
        
        # Dialog title
        dialog_title = Label(
            pygame.Rect(0, 20, 300, 30),
            "New Deck",
            color=(220, 220, 220),
            font_size=22,
            align='center'
        )
        dialog_panel.add_element(dialog_title)
        
        # Input field (simulated with a label)
        self.deck_name_input = "New Deck"
        
        self.name_label = Label(
            pygame.Rect(50, 70, 200, 30),
            self.deck_name_input,
            color=(255, 255, 255),
            font_size=18,
            align='center'
        )
        dialog_panel.add_element(self.name_label)
        
        # Input field border
        input_border_rect = pygame.Rect(50, 70, 200, 30)
        
        # Create buttons
        confirm_button = Button(
            pygame.Rect(50, 120, 90, 30),
            "Create",
            self._create_new_deck,
            color=(60, 120, 60),
            hover_color=(80, 160, 80),
            font_size=16
        )
        dialog_panel.add_element(confirm_button)
        
        cancel_button = Button(
            pygame.Rect(160, 120, 90, 30),
            "Cancel",
            self._close_deck_name_dialog,
            color=(120, 60, 60),
            hover_color=(160, 80, 80),
            font_size=16
        )
        dialog_panel.add_element(cancel_button)
        
        # Store the dialog
        self.deck_name_dialog = dialog_panel
        self.deck_name_input_border = input_border_rect
        
        # Add to UI elements
        self.ui_elements.append(dialog_panel)
    
    def _create_new_deck(self):
        """Create a new deck with the entered name."""
        # Create a new deck
        from ..models.deck import Deck
        self.current_deck = Deck(name=self.deck_name_input)
        
        # Close the dialog
        self._close_deck_name_dialog()
        
        # Update UI
        self._update_ui()
    
    def _close_deck_name_dialog(self):
        """Close the deck name dialog."""
        if hasattr(self, 'deck_name_dialog') and self.deck_name_dialog in self.ui_elements:
            self.ui_elements.remove(self.deck_name_dialog)
            del self.deck_name_dialog
    
    def _clear_deck(self):
        """Clear the current deck."""
        if not self.current_deck:
            return
        
        # Keep the name but clear the cards
        self.current_deck.cards = []
        
        # Update UI
        self._update_ui()
    
    def _back_to_menu(self):
        """Return to the main menu."""
        # Save player data before leaving
        if self.player:
            SaveManager.save_player(self.player)
        
        # Return to home screen
        self.switch_to_screen("home")
    
    def _add_card_to_deck(self, card):
        """
        Add a card to the current deck.
        
        Args:
            card: Card to add
        """
        if not self.current_deck:
            return
        
        # Check if the deck is already full
        if self.current_deck.size() >= 30:
            return
        
        # Check if we already have 3 of this card in the deck
        card_count = sum(1 for c in self.current_deck.cards if c.id == card.id)
        if card_count >= 3:
            return
        
        # Add the card to the deck
        self.current_deck.add_card(card)
        
        # Update UI
        self._update_ui()
    
    def _remove_card_from_deck(self, card_index):
        """
        Remove a card from the current deck.
        
        Args:
            card_index (int): Index of the card in the deck
        """
        if not self.current_deck:
            return
        
        # Adjust the index based on the current page
        actual_index = self.deck_page * self.cards_per_page + card_index
        
        # Check if the index is valid
        if 0 <= actual_index < self.current_deck.size():
            # Remove the card
            self.current_deck.remove_card(actual_index)
            
            # Update UI
            self._update_ui()
    
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
        
        # Special handling for deck name input
        if hasattr(self, 'deck_name_dialog') and event.type == pygame.KEYDOWN:
            # Handle typing in the deck name
            if event.key == pygame.K_BACKSPACE:
                self.deck_name_input = self.deck_name_input[:-1]
            elif event.key == pygame.K_RETURN:
                self._create_new_deck()
            elif event.unicode.isprintable():
                # Limit the name length
                if len(self.deck_name_input) < 20:
                    self.deck_name_input += event.unicode
            
            # Update the displayed name
            if hasattr(self, 'name_label'):
                self.name_label.set_text(self.deck_name_input)
            
            return True
        
        # Handle mouse clicks on cards in collection or deck
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Handle collection card clicks
            collection_card_clicked = self._handle_collection_click(event.pos)
            if collection_card_clicked:
                return True
            
            # Handle deck card clicks
            deck_card_clicked = self._handle_deck_click(event.pos)
            if deck_card_clicked:
                return True
        
        return False
    
    def _handle_collection_click(self, pos):
        """
        Handle clicks on cards in the collection.
        
        Args:
            pos (tuple): Mouse position
            
        Returns:
            bool: True if a card was clicked, False otherwise
        """
        if not self.player:
            return False
        
        # Get filtered cards
        filtered_cards = self._get_filtered_cards()
        
        # Calculate the cards on the current page
        start_idx = self.collection_page * self.cards_per_page
        end_idx = min(start_idx + self.cards_per_page, len(filtered_cards))
        page_cards = filtered_cards[start_idx:end_idx]
        
        # Check if a card was clicked
        for i, (card, quantity) in enumerate(page_cards):
            card_rect = self._get_collection_card_rect(i)
            
            if card_rect.collidepoint(pos):
                # Select this card
                self.selected_collection_card = card
                
                # If clicked with left button, try to add to deck
                self._add_card_to_deck(card)
                
                return True
        
        return False
    
    def _handle_deck_click(self, pos):
        """
        Handle clicks on cards in the deck.
        
        Args:
            pos (tuple): Mouse position
            
        Returns:
            bool: True if a card was clicked, False otherwise
        """
        if not self.current_deck:
            return False
        
        # Calculate the cards on the current page
        start_idx = self.deck_page * self.cards_per_page
        end_idx = min(start_idx + self.cards_per_page, self.current_deck.size())
        
        # Check if a card was clicked
        for i in range(end_idx - start_idx):
            card_rect = self._get_deck_card_rect(i)
            
            if card_rect.collidepoint(pos):
                # Get the actual index in the deck
                actual_index = i
                
                # Select this card
                card_index = start_idx + i
                if card_index < self.current_deck.size():
                    self.selected_deck_card = card_index
                
                # If clicked with left button, remove from deck
                self._remove_card_from_deck(actual_index)
                
                return True
        
        return False
    
    def _get_collection_card_rect(self, index):
        """
        Get the rectangle for a card in the collection.
        
        Args:
            index (int): Index of the card on the current page
            
        Returns:
            pygame.Rect: Rectangle for the card
        """
        # Card size
        card_width, card_height = self.card_renderer.card_size
        
        # Collection panel position and size
        panel_rect = self.ui_elements[1].rect  # 1 is the collection panel
        
        # Layout: 2 columns, 4 rows
        col = index % 2
        row = index // 2
        
        # Calculate position
        margin = 20
        x = panel_rect.left + margin + col * (card_width + margin)
        y = panel_rect.top + 120 + row * (card_height + margin)
        
        return pygame.Rect(x, y, card_width, card_height)
    
    def _get_deck_card_rect(self, index):
        """
        Get the rectangle for a card in the deck.
        
        Args:
            index (int): Index of the card on the current page
            
        Returns:
            pygame.Rect: Rectangle for the card
        """
        # Card size
        card_width, card_height = self.card_renderer.card_size
        
        # Deck panel position and size
        panel_rect = self.ui_elements[2].rect  # 2 is the deck panel
        
        # Layout: 2 columns, 4 rows
        col = index % 2
        row = index // 2
        
        # Calculate position
        margin = 20
        x = panel_rect.left + margin + col * (card_width + margin)
        y = panel_rect.top + 120 + row * (card_height + margin)
        
        return pygame.Rect(x, y, card_width, card_height)
    
    def render(self):
        """Render the deck building screen."""
        # Draw background
        self.display.fill(self.background_color)
        
        # Render UI elements
        for element in self.ui_elements:
            element.render(self.display)
        
        # Render collection cards
        self._render_collection()
        
        # Render deck cards
        self._render_deck()
        
        # Render deck name dialog input field
        if hasattr(self, 'deck_name_dialog') and hasattr(self, 'deck_name_input_border'):
            pygame.draw.rect(self.display, (80, 80, 100), self.deck_name_input_border, width=2)
    
    def _render_collection(self):
        """Render the player's card collection."""
        if not self.player:
            return
        
        # Get filtered cards
        filtered_cards = self._get_filtered_cards()
        
        # Calculate the cards on the current page
        start_idx = self.collection_page * self.cards_per_page
        end_idx = min(start_idx + self.cards_per_page, len(filtered_cards))
        page_cards = filtered_cards[start_idx:end_idx]
        
        # Draw each card
        for i, (card, quantity) in enumerate(page_cards):
            card_rect = self._get_collection_card_rect(i)
            
            # Draw the card
            self.card_renderer.render_card(
                self.display, 
                card, 
                (card_rect.left, card_rect.top),
                selectable=True,
                selected=card == self.selected_collection_card
            )
            
            # Draw quantity indicator
            quantity_bg = pygame.Rect(card_rect.right - 25, card_rect.top + 5, 20, 20)
            pygame.draw.rect(self.display, (50, 50, 70), quantity_bg, border_radius=10)
            pygame.draw.rect(self.display, (100, 100, 130), quantity_bg, width=1, border_radius=10)
            
            font = pygame.freetype.SysFont('Arial', 14)
            qty_surf, qty_rect = font.render(str(quantity), (220, 220, 220))
            qty_rect.center = quantity_bg.center
            self.display.blit(qty_surf, qty_rect)
    
    def _render_deck(self):
        """Render the current deck."""
        if not self.current_deck:
            return
        
        # Calculate the cards on the current page
        start_idx = self.deck_page * self.cards_per_page
        end_idx = min(start_idx + self.cards_per_page, self.current_deck.size())
        page_cards = self.current_deck.cards[start_idx:end_idx]
        
        # Draw each card
        for i, card in enumerate(page_cards):
            card_rect = self._get_deck_card_rect(i)
            
            # Draw the card
            self.card_renderer.render_card(
                self.display, 
                card, 
                (card_rect.left, card_rect.top),
                selectable=True,
                selected=(start_idx + i) == self.selected_deck_card
            )
    
    def load_resources(self):
        """Load screen-specific resources."""
        # Load background image if available
        try:
            bg_path = os.path.join("assets", "images", "backgrounds", "deck_bg.jpg")
            self.resources["background"] = pygame.image.load(bg_path)
            self.resources["background"] = pygame.transform.scale(
                self.resources["background"], (self.width, self.height)
            )
        except (pygame.error, FileNotFoundError):
            # No specific handling needed, we'll use the solid color background
            pass