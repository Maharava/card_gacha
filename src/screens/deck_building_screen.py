"""
Enhanced deck building screen for the card game.
"""
import pygame
import os
from typing import List, Dict, Tuple, Optional

# Fixed imports
from src.screens.screen import Screen
from src.screens.ui_elements import Button, Label, Panel, CardRenderer
from src.models.deck import Deck
from src.models.card import Card
from src.utils.resource_loader import ResourceLoader
from src.utils.save_manager import SaveManager


class DeckBuildingScreen(Screen):
    """
    Enhanced deck building screen allowing players to:
    - View their card collection with advanced filtering options
    - Create and modify multiple decks
    - Sort and filter cards by various criteria
    - Get deck statistics and validation feedback
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
        self.current_cost_filter = "all"
        self.sort_method = "name"  # name, cost, rarity
        self.selected_collection_card = None
        
        # Deck view state
        self.deck_page = 0
        self.selected_deck_card = None
        
        # Deck list view
        self.deck_list = []
        self.deck_list_panel = None
        self.showing_deck_list = False
        
        # Status message
        self.status_message = ""
        self.status_message_color = (180, 180, 180)
        self.status_message_timer = 0
        
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
        button_width = 70
        button_spacing = 5
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
        
        rare_button = Button(
            pygame.Rect(100 + (button_width + button_spacing) * 3, button_y, button_width, 25),
            "Rare",
            lambda: self._set_rarity_filter("rare"),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(rare_button)
        
        epic_button = Button(
            pygame.Rect(100 + (button_width + button_spacing) * 4, button_y, button_width, 25),
            "Epic",
            lambda: self._set_rarity_filter("epic"),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(epic_button)

        # Filter by cost buttons
        cost_label = Label(
            pygame.Rect(20, 85, 80, 25),
            "Cost:",
            color=(180, 180, 180),
            font_size=16,
            align='left'
        )
        collection_panel.add_element(cost_label)
        
        cost_all_button = Button(
            pygame.Rect(100, 85, button_width, 25),
            "All",
            lambda: self._set_cost_filter("all"),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(cost_all_button)
        
        cost_0_button = Button(
            pygame.Rect(100 + (button_width + button_spacing), 85, button_width, 25),
            "0",
            lambda: self._set_cost_filter(0),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(cost_0_button)
        
        cost_1_button = Button(
            pygame.Rect(100 + (button_width + button_spacing) * 2, 85, button_width, 25),
            "1",
            lambda: self._set_cost_filter(1),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(cost_1_button)
        
        cost_2_button = Button(
            pygame.Rect(100 + (button_width + button_spacing) * 3, 85, button_width, 25),
            "2",
            lambda: self._set_cost_filter(2),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(cost_2_button)
        
        cost_3_button = Button(
            pygame.Rect(100 + (button_width + button_spacing) * 4, 85, button_width, 25),
            "3",
            lambda: self._set_cost_filter(3),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(cost_3_button)
        
        # Sort buttons
        sort_label = Label(
            pygame.Rect(20, 120, 80, 25),
            "Sort by:",
            color=(180, 180, 180),
            font_size=16,
            align='left'
        )
        collection_panel.add_element(sort_label)
        
        sort_width = 90
        
        name_button = Button(
            pygame.Rect(100, 120, sort_width, 25),
            "Name",
            lambda: self._set_sort_method("name"),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(name_button)
        
        cost_button = Button(
            pygame.Rect(100 + sort_width + button_spacing, 120, sort_width, 25),
            "Cost",
            lambda: self._set_sort_method("cost"),
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        collection_panel.add_element(cost_button)
        
        rarity_button = Button(
            pygame.Rect(100 + (sort_width + button_spacing) * 2, 120, sort_width, 25),
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
        
        # Deck count and validation
        self.deck_count = Label(
            pygame.Rect(deck_panel.rect.width - 120, 10, 100, 30),
            "Cards: 0/30",
            color=(180, 180, 180),
            font_size=18,
            align='right'
        )
        deck_panel.add_element(self.deck_count)
        
        # Deck stats
        self.deck_stats = Label(
            pygame.Rect(20, 50, deck_panel.rect.width - 40, 30),
            "Avg Cost: 0.0 | Common: 0 | Uncommon: 0 | Rare: 0 | Epic: 0",
            color=(180, 180, 180),
            font_size=14,
            align='left'
        )
        deck_panel.add_element(self.deck_stats)
        
        # Deck management buttons (small row beneath stats)
        manage_decks_button = Button(
            pygame.Rect(20, 90, 120, 25),
            "Manage Decks",
            self._show_deck_list,
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        deck_panel.add_element(manage_decks_button)
        
        rename_deck_button = Button(
            pygame.Rect(150, 90, 100, 25),
            "Rename",
            self._rename_current_deck,
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        deck_panel.add_element(rename_deck_button)
        
        duplicate_deck_button = Button(
            pygame.Rect(260, 90, 100, 25),
            "Duplicate",
            self._duplicate_current_deck,
            color=(80, 80, 100),
            hover_color=(100, 100, 130),
            font_size=14
        )
        deck_panel.add_element(duplicate_deck_button)
        
        # Deck validation status
        self.validation_label = Label(
            pygame.Rect(20, 125, deck_panel.rect.width - 40, 25),
            "",
            color=(180, 180, 180),
            font_size=14,
            align='left'
        )
        deck_panel.add_element(self.validation_label)
        
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
        
        # Set as active deck button
        activate_button = Button(
            pygame.Rect(530, 10, 150, 30),
            "Set as Active",
            self._set_as_active_deck,
            color=(120, 120, 60),
            hover_color=(160, 160, 80),
            font_size=18
        )
        control_panel.add_element(activate_button)
        
        # Status message label
        self.status_label = Label(
            pygame.Rect(700, 10, control_panel.rect.width - 870, 30),
            "",
            color=(180, 180, 180),
            font_size=14,
            align='left'
        )
        control_panel.add_element(self.status_label)
        
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
        self.current_cost_filter = "all"
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
        
        # Update deck stats
        self._update_deck_stats()
        
        # Update deck validation
        self._update_deck_validation()
        
        # Update status message
        if self.status_message:
            self.status_label.set_text(self.status_message)
            self.status_label.color = self.status_message_color
    
    def _update_deck_stats(self):
        """Update the deck statistics display."""
        if not self.current_deck:
            return
        
        # Get deck stats
        stats = self.current_deck.get_stats()
        
        # Calculate average cost
        total_cost = sum(card.cost for card in self.current_deck.cards)
        avg_cost = total_cost / max(1, len(self.current_deck.cards))
        
        # Format stats
        stats_text = f"Avg Cost: {avg_cost:.1f} | "
        stats_text += f"Common: {stats['rarity_distribution'].get('common', 0)} | "
        stats_text += f"Uncommon: {stats['rarity_distribution'].get('uncommon', 0)} | "
        stats_text += f"Rare: {stats['rarity_distribution'].get('rare', 0)} | "
        stats_text += f"Epic: {stats['rarity_distribution'].get('epic', 0)}"
        
        self.deck_stats.set_text(stats_text)
    
    def _update_deck_validation(self):
        """Update the deck validation status."""
        if not self.current_deck:
            return
        
        # Validate the deck
        is_valid, message = self.current_deck.validate()
        
        if is_valid:
            self.validation_label.set_text(message)
            self.validation_label.color = (100, 255, 100)  # Green for valid
        else:
            self.validation_label.set_text(message)
            self.validation_label.color = (255, 100, 100)  # Red for invalid
    
    def _get_filtered_cards(self) -> List[Tuple[Card, int]]:
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
                rarity_match = (self.current_rarity_filter == "all" or 
                               card.rarity == self.current_rarity_filter)
                
                # Apply cost filter
                cost_match = (self.current_cost_filter == "all" or 
                             card.cost == self.current_cost_filter)
                
                if rarity_match and cost_match:
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
    
    def _set_cost_filter(self, cost):
        """
        Set the cost filter.
        
        Args:
            cost (int or str): Cost to filter by (or "all")
        """
        self.current_cost_filter = cost
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
        
        # Validate the deck first
        is_valid, message = self.current_deck.validate()
        if not is_valid:
            self._set_status_message(f"Cannot save: {message}", (255, 100, 100))
            return
        
        # Save the deck to player's collection
        success, message = self.player.save_deck(self.current_deck)
        
        if success:
            # Save player data
            SaveManager.save_player(self.player)
            self._set_status_message(message, (100, 255, 100))
        else:
            self._set_status_message(message, (255, 100, 100))
    
    def _set_as_active_deck(self):
        """Set the current deck as the player's active deck."""
        if not self.player or not self.current_deck:
            return
        
        # Validate the deck first
        is_valid, message = self.current_deck.validate()
        if not is_valid:
            self._set_status_message(f"Cannot set as active: {message}", (255, 100, 100))
            return
        
        # Set as active deck
        success, message = self.player.set_active_deck(self.current_deck.name)
        
        if success:
            # Save player data
            SaveManager.save_player(self.player)
            self._set_status_message(message, (100, 255, 100))
        else:
            self._set_status_message(message, (255, 100, 100))
    
    def _new_deck(self):
        """Create a new empty deck."""
        if not self.player:
            return
        
        # Create a deck name input dialog
        self._show_deck_name_dialog(create_new=True)
    
    def _show_deck_name_dialog(self, create_new=True, old_name=None):
        """
        Show a dialog to input the deck name.
        
        Args:
            create_new (bool): Whether to create a new deck or rename an existing one
            old_name (str, optional): Name of the deck to rename
        """
        # Create dialog panel
        dialog_panel = Panel(
            pygame.Rect(self.width // 2 - 150, self.height // 2 - 100, 300, 200),
            color=(50, 55, 70),
            border_color=(100, 110, 140),
            border_width=2,
            rounded=True
        )
        
        # Dialog title
        title_text = "New Deck" if create_new else "Rename Deck"
        dialog_title = Label(
            pygame.Rect(0, 20, 300, 30),
            title_text,
            color=(220, 220, 220),
            font_size=22,
            align='center'
        )
        dialog_panel.add_element(dialog_title)
        
        # Input field (simulated with a label)
        self.deck_name_input = "New Deck" if create_new else old_name
        self.rename_old_name = old_name
        
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
        button_text = "Create" if create_new else "Rename"
        callback = self._create_new_deck if create_new else self._finish_rename_deck
        
        confirm_button = Button(
            pygame.Rect(50, 120, 90, 30),
            button_text,
            callback,
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
        # Check if name already exists
        if self.player and self.deck_name_input in self.player.decks:
            self._set_status_message(f"A deck named '{self.deck_name_input}' already exists", (255, 100, 100))
            self._close_deck_name_dialog()
            return
        
        # Create a new deck
        self.current_deck = Deck(name=self.deck_name_input)
        
        # Close the dialog
        self._close_deck_name_dialog()
        
        # Update UI
        self._update_ui()
        self._set_status_message(f"Created new deck: {self.deck_name_input}", (100, 255, 100))
    
    def _finish_rename_deck(self):
        """Finish renaming the current deck."""
        if not self.player or not self.current_deck:
            self._close_deck_name_dialog()
            return
        
        # Check if name already exists and is different from current
        if (self.deck_name_input != self.rename_old_name and 
            self.deck_name_input in self.player.decks):
            self._set_status_message(f"A deck named '{self.deck_name_input}' already exists", (255, 100, 100))
            self._close_deck_name_dialog()
            return
        
        # Rename the deck
        success, message = self.player.rename_deck(self.rename_old_name, self.deck_name_input)
        
        if success:
            # Update current deck reference
            self.current_deck = self.player.decks[self.deck_name_input]
            
            # Save player data
            SaveManager.save_player(self.player)
            self._set_status_message(message, (100, 255, 100))
        else:
            self._set_status_message(message, (255, 100, 100))
        
        # Close the dialog
        self._close_deck_name_dialog()
        
        # Update UI
        self._update_ui()
    
    def _rename_current_deck(self):
        """Rename the current deck."""
        if not self.player or not self.current_deck:
            return
        
        self._show_deck_name_dialog(create_new=False, old_name=self.current_deck.name)
    
    def _duplicate_current_deck(self):
        """Create a duplicate of the current deck."""
        if not self.player or not self.current_deck:
            return
        
        # Generate a new name
        base_name = f"{self.current_deck.name} Copy"
        new_name = base_name
        counter = 1
        
        while new_name in self.player.decks:
            counter += 1
            new_name = f"{base_name} {counter}"
        
        # Create the duplicate
        success, message = self.player.duplicate_deck(self.current_deck.name, new_name)
        
        if success:
            # Set current deck to the duplicate
            self.current_deck = self.player.decks[new_name]
            
            # Save player data
            SaveManager.save_player(self.player)
            self._set_status_message(message, (100, 255, 100))
            
            # Update UI
            self._update_ui()
        else:
            self._set_status_message(message, (255, 100, 100))
    
    def _close_deck_name_dialog(self):
        """Close the deck name dialog."""
        if hasattr(self, 'deck_name_dialog') and self.deck_name_dialog in self.ui_elements:
            self.ui_elements.remove(self.deck_name_dialog)
            del self.deck_name_dialog
    
    def _show_deck_list(self):
        """Show the list of saved decks."""
        if not self.player:
            return
        
        # Create deck list panel
        deck_list_panel = Panel(
            pygame.Rect(self.width // 2 - 200, self.height // 2 - 200, 400, 400),
            color=(50, 55, 70),
            border_color=(100, 110, 140),
            border_width=2,
            rounded=True
        )
        
        # Panel title
        list_title = Label(
            pygame.Rect(0, 20, 400, 30),
            "Your Decks",
            color=(220, 220, 220),
            font_size=24,
            align='center'
        )
        deck_list_panel.add_element(list_title)
        
        # Get list of decks
        deck_names = self.player.get_deck_list()
        active_deck_name = self.player.get_active_deck_name()
        
        # Create deck buttons
        button_height = 30
        button_margin = 5
        button_y = 70
        
        for i, deck_name in enumerate(deck_names):
            # Highlight active deck
            if deck_name == active_deck_name:
                deck_color = (60, 120, 60)
                hover_color = (80, 160, 80)
                text = f"{deck_name} (Active)"
            else:
                deck_color = (80, 80, 100)
                hover_color = (100, 100, 130)
                text = deck_name
            
            # Create closure to capture the current deck name
            def make_load_callback(name):
                return lambda: self._load_deck(name)
            
            deck_button = Button(
                pygame.Rect(50, button_y + i * (button_height + button_margin), 300, button_height),
                text,
                make_load_callback(deck_name),
                color=deck_color,
                hover_color=hover_color,
                font_size=16
            )
            deck_list_panel.add_element(deck_button)
        
        # Close button
        close_button = Button(
            pygame.Rect(150, 350, 100, 30),
            "Close",
            self._close_deck_list,
            color=(100, 100, 100),
            hover_color=(140, 140, 140),
            font_size=16
        )
        deck_list_panel.add_element(close_button)
        
        # Store the panel
        self.deck_list_panel = deck_list_panel
        self.showing_deck_list = True
        
        # Add to UI elements
        self.ui_elements.append(deck_list_panel)
    
    def _close_deck_list(self):
        """Close the deck list panel."""
        if self.deck_list_panel in self.ui_elements:
            self.ui_elements.remove(self.deck_list_panel)
            self.showing_deck_list = False
    
    def _load_deck(self, deck_name):
        """
        Load a deck from the player's saved decks.
        
        Args:
            deck_name (str): Name of the deck to load
        """
        if not self.player or deck_name not in self.player.decks:
            return
        
        # Set current deck
        self.current_deck = self.player.decks[deck_name]
        
        # Close deck list
        self._close_deck_list()
        
        # Reset deck page
        self.deck_page = 0
        
        # Update UI
        self._update_ui()
        self._set_status_message(f"Loaded deck: {deck_name}", (100, 255, 100))
    
    def _clear_deck(self):
        """Clear the current deck."""
        if not self.current_deck:
            return
        
        # Keep the name but clear the cards
        self.current_deck.cards = []
        
        # Update UI
        self._update_ui()
        self._set_status_message("Deck cleared", (255, 200, 100))
    
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
        
        # Try to add the card
        if self.current_deck.add_card(card):
            self._set_status_message(f"Added {card.name} to deck", (100, 255, 100))
        else:
            # Check why it failed
            if len(self.current_deck.cards) >= Deck.MAX_DECK_SIZE:
                self._set_status_message(f"Deck is full (max {Deck.MAX_DECK_SIZE} cards)", (255, 100, 100))
            else:
                # Count how many of this card are already in the deck
                count = sum(1 for c in self.current_deck.cards if c.id == card.id)
                self._set_status_message(
                    f"Max {Deck.MAX_COPIES_PER_CARD} copies of {card.name} allowed", (255, 100, 100)
                )
        
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
            # Get the card before removing it
            card = self.current_deck.cards[actual_index]
            
            # Remove the card
            self.current_deck.remove_card(actual_index)
            
            self._set_status_message(f"Removed {card.name} from deck", (255, 200, 100))
            
            # Update UI
            self._update_ui()
    
    def _set_status_message(self, message, color=(180, 180, 180)):
        """
        Set a status message to display to the user.
        
        Args:
            message (str): Message to display
            color (tuple): RGB color of the message
        """
        self.status_message = message
        self.status_message_color = color
        self.status_message_timer = 3.0  # Show for 3 seconds
        
        # Update status label
        self.status_label.set_text(message)
        self.status_label.color = color
    
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
                if hasattr(self, 'rename_old_name'):
                    self._finish_rename_deck()
                else:
                    self._create_new_deck()
            elif event.unicode.isprintable():
                # Limit the name length
                if len(self.deck_name_input) < 20:
                    self.deck_name_input += event.unicode
            
            # Update the displayed name
            if hasattr(self, 'name_label'):
                self.name_label.set_text(self.deck_name_input)
            
            return True
        
        # Don't handle clicks if a dialog is open
        if hasattr(self, 'deck_name_dialog') or self.showing_deck_list:
            return False
        
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
        y = panel_rect.top + 160 + row * (card_height + margin)
        
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
        y = panel_rect.top + 160 + row * (card_height + margin)
        
        return pygame.Rect(x, y, card_width, card_height)
    
    def update(self, dt):
        """
        Update logic for the deck building screen.
        
        Args:
            dt (float): Time delta in seconds
        """
        super().update(dt)
        
        # Update status message timer
        if self.status_message and self.status_message_timer > 0:
            self.status_message_timer -= dt
            if self.status_message_timer <= 0:
                self.status_message = ""
                self.status_label.set_text("")
    
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
            
            # Add "Add to Deck" hint for cards that can be added
            if self.current_deck:
                card_count = sum(1 for c in self.current_deck.cards if c.id == card.id)
                can_add = (len(self.current_deck.cards) < Deck.MAX_DECK_SIZE and 
                          card_count < Deck.MAX_COPIES_PER_CARD)
                
                if can_add:
                    hint_font = pygame.freetype.SysFont('Arial', 10)
                    hint_surf, hint_rect = hint_font.render("Click to add", (180, 180, 180))
                    hint_rect.centerx = card_rect.centerx
                    hint_rect.bottom = card_rect.bottom - 5
                    self.display.blit(hint_surf, hint_rect)
    
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
            
            # Draw "Remove" hint
            hint_font = pygame.freetype.SysFont('Arial', 10)
            hint_surf, hint_rect = hint_font.render("Click to remove", (180, 180, 180))
            hint_rect.centerx = card_rect.centerx
            hint_rect.bottom = card_rect.bottom - 5
            self.display.blit(hint_surf, hint_rect)
            
            # Draw card count indicator (how many of this card in the deck)
            card_count = sum(1 for c in self.current_deck.cards if c.id == card.id)
            
            count_bg = pygame.Rect(card_rect.right - 25, card_rect.top + 5, 20, 20)
            pygame.draw.rect(self.display, (50, 50, 70), count_bg, border_radius=10)
            pygame.draw.rect(self.display, (100, 100, 130), count_bg, width=1, border_radius=10)
            
            count_font = pygame.freetype.SysFont('Arial', 14)
            count_surf, count_rect = count_font.render(f"{card_count}/{Deck.MAX_COPIES_PER_CARD}", (220, 220, 220))
            count_rect.center = count_bg.center
            self.display.blit(count_surf, count_rect)
    
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