"""
Home screen for the card game.
"""
import pygame
import os

# Fixed imports
from src.screens.screen import Screen
from src.screens.ui_elements import Button, Label, Panel
from src.utils.resource_loader import ResourceLoader
from src.utils.save_manager import SaveManager


class HomeScreen(Screen):
    """
    Home screen with main menu options.
    
    This screen provides access to:
    - Starting a new game
    - Deck building
    - Shop
    - Game options
    - Exiting the game
    """
    
    def __init__(self, display, manager=None):
        """
        Initialize the home screen.
        
        Args:
            display (pygame.Surface): The main display surface
            manager: The screen manager
        """
        super().__init__(display, manager)
        
        self.background_color = (30, 40, 50)
        
        # Create UI elements
        self._create_ui_elements()
    
    def _create_ui_elements(self):
        """Create the UI elements for the home screen."""
        # Background panel to ensure proper layering
        background_panel = Panel(
            pygame.Rect(0, 0, self.width, self.height),
            color=(30, 40, 50),
            border_color=None,
            border_width=0,
            rounded=False
        )
        
        # Title panel
        title_panel = Panel(
            pygame.Rect(self.width // 2 - 200, 50, 400, 100),
            color=(40, 50, 60),
            border_color=(80, 100, 120),
            border_width=2,
            rounded=True
        )
        
        # Game title
        title_label = Label(
            pygame.Rect(0, 0, 400, 100),
            "Card Battle",
            color=(220, 220, 220),
            font_size=48,
            align='center'
        )
        title_panel.add_element(title_label)
        
        # Subtitle
        subtitle_label = Label(
            pygame.Rect(self.width // 2 - 150, 160, 300, 30),
            "A Strategic Card Game",
            color=(180, 180, 180),
            font_size=20,
            align='center'
        )
        
        # Menu panel
        menu_panel = Panel(
            pygame.Rect(self.width // 2 - 150, 200, 300, 300),
            color=(40, 50, 60),
            border_color=(80, 100, 120),
            border_width=2,
            rounded=True
        )
        
        # Button dimensions
        button_width = 200
        button_height = 40
        button_margin = 20
        button_x = 50  # Relative to panel
        button_y = 30
        
        # Play button
        play_button = Button(
            pygame.Rect(button_x, button_y, button_width, button_height),
            "Play Game",
            self._on_play_button_click,
            color=(60, 120, 60),
            hover_color=(80, 160, 80),
            font_size=20
        )
        menu_panel.add_element(play_button)
        
        # Deck Building button
        deck_button = Button(
            pygame.Rect(button_x, button_y + button_height + button_margin, button_width, button_height),
            "Deck Building",
            self._on_deck_button_click,
            color=(60, 80, 120),
            hover_color=(80, 100, 160),
            font_size=20
        )
        menu_panel.add_element(deck_button)
        
        # Shop button
        shop_button = Button(
            pygame.Rect(button_x, button_y + (button_height + button_margin) * 2, button_width, button_height),
            "Shop",
            self._on_shop_button_click,
            color=(120, 60, 120),
            hover_color=(160, 80, 160),
            font_size=20
        )
        menu_panel.add_element(shop_button)
        
        # Settings button
        settings_button = Button(
            pygame.Rect(button_x, button_y + (button_height + button_margin) * 3, button_width, button_height),
            "Settings",
            self._on_settings_button_click,
            color=(100, 100, 100),
            hover_color=(140, 140, 140),
            font_size=20
        )
        menu_panel.add_element(settings_button)
        
        # Exit button
        exit_button = Button(
            pygame.Rect(button_x, button_y + (button_height + button_margin) * 4, button_width, button_height),
            "Exit Game",
            self._on_exit_button_click,
            color=(120, 60, 60),
            hover_color=(160, 80, 80),
            font_size=20
        )
        menu_panel.add_element(exit_button)
        
        # Add all panels to the UI elements list - order matters for rendering!
        self.ui_elements = [background_panel, title_panel, subtitle_label, menu_panel]
        
        # Initialize popup panels as None
        self.difficulty_panel = None
        self.active_deck_message = None
        
    def _on_play_button_click(self):
        """Handle play button click."""
        # Close any existing popup panels
        self._close_all_popups()
        
        # Create a semi-transparent overlay for better visibility
        overlay = Panel(
            pygame.Rect(0, 0, self.width, self.height),
            color=(0, 0, 0, 128),  # Semi-transparent black
            border_color=None,
            border_width=0,
            rounded=False
        )
        self.ui_elements.append(overlay)
        
        # Open a difficulty selection dialog
        self.difficulty_panel = Panel(
            pygame.Rect(self.width // 2 - 200, self.height // 2 - 150, 400, 300),
            color=(50, 60, 70),
            border_color=(100, 120, 140),
            border_width=2,
            rounded=True
        )
        
        # Difficulty title
        difficulty_title = Label(
            pygame.Rect(0, 20, 400, 40),
            "Select Difficulty",
            color=(220, 220, 220),
            font_size=28,
            align='center'
        )
        self.difficulty_panel.add_element(difficulty_title)
        
        # Difficulty buttons
        button_width = 160
        button_height = 40
        button_x = 120  # Relative to panel
        
        easy_button = Button(
            pygame.Rect(button_x, 80, button_width, button_height),
            "Easy",
            lambda: self._start_game("easy"),
            color=(60, 120, 60),
            hover_color=(80, 160, 80),
            font_size=20
        )
        self.difficulty_panel.add_element(easy_button)
        
        normal_button = Button(
            pygame.Rect(button_x, 130, button_width, button_height),
            "Normal",
            lambda: self._start_game("normal"),
            color=(120, 120, 60),
            hover_color=(160, 160, 80),
            font_size=20
        )
        self.difficulty_panel.add_element(normal_button)
        
        hard_button = Button(
            pygame.Rect(button_x, 180, button_width, button_height),
            "Hard",
            lambda: self._start_game("hard"),
            color=(120, 60, 60),
            hover_color=(160, 80, 80),
            font_size=20
        )
        self.difficulty_panel.add_element(hard_button)
        
        # Cancel button
        cancel_button = Button(
            pygame.Rect(button_x, 230, button_width, button_height),
            "Cancel",
            self._close_all_popups,
            color=(80, 80, 80),
            hover_color=(120, 120, 120),
            font_size=20
        )
        self.difficulty_panel.add_element(cancel_button)
        
        # Add the difficulty panel to UI elements
        self.ui_elements.append(self.difficulty_panel)
        
    def _close_all_popups(self):
        """Close all popup panels."""
        # Remove all popups from UI elements
        if self.difficulty_panel in self.ui_elements:
            self.ui_elements.remove(self.difficulty_panel)
            self.difficulty_panel = None
        
        if self.active_deck_message in self.ui_elements:
            self.ui_elements.remove(self.active_deck_message)
            self.active_deck_message = None
            
        # Remove any overlay that might be present
        self.ui_elements = [e for e in self.ui_elements if not (
            isinstance(e, Panel) and 
            e.rect.width == self.width and 
            e.rect.height == self.height and
            e.rect.x == 0 and
            e.rect.y == 0 and
            e not in self.ui_elements[:1]  # Keep the background panel
        )]
            
    def _start_game(self, difficulty):
        """Start a new game with the selected difficulty."""
        # Close difficulty panel
        self._close_all_popups()
        
        # Load player data if needed
        card_database = ResourceLoader.load_cards()
        if SaveManager.player_exists():
            self.player = SaveManager.load_player(card_database)
        
        # Show active deck message if player exists
        if hasattr(self, 'player') and self.player:
            active_deck_name = self.player.get_active_deck_name()
            self._show_active_deck_message(active_deck_name, difficulty)
        else:
            # Immediately switch to game screen if no player data
            self.switch_to_screen("game", difficulty=difficulty)
        
    def _on_deck_button_click(self):
        """Handle deck building button click."""
        self.switch_to_screen("deck_building")
        
    def _on_shop_button_click(self):
        """Handle shop button click."""
        self.switch_to_screen("shop")
        
    def _on_settings_button_click(self):
        """Handle settings button click."""
        # Settings functionality would go here
        pass
        
    def _on_exit_button_click(self):
        """Handle exit button click."""
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def load_resources(self):
        """Load screen-specific resources."""
        # Load background image if available
        try:
            bg_path = os.path.join("assets", "images", "backgrounds", "menu_bg.jpg")
            self.resources["background"] = pygame.image.load(bg_path)
            self.resources["background"] = pygame.transform.scale(
                self.resources["background"], (self.width, self.height)
            )
        except (pygame.error, FileNotFoundError):
            # Create a gradient background if image loading fails
            self.resources["background"] = pygame.Surface((self.width, self.height))
            for y in range(self.height):
                # Create a blue gradient
                color = (
                    30,
                    40 + int(y / self.height * 20),
                    50 + int(y / self.height * 30)
                )
                pygame.draw.line(self.resources["background"], color, (0, y), (self.width, y))
    
    def render(self):
        """Render the home screen."""
        # Draw background
        if "background" in self.resources:
            self.display.blit(self.resources["background"], (0, 0))
        else:
            self.display.fill(self.background_color)
        
        # Render UI elements
        for element in self.ui_elements:
            element.render(self.display)
    
    def _show_active_deck_message(self, deck_name, difficulty):
        """Show a message with the active deck name before starting the game."""
        # Create a semi-transparent overlay for better visibility
        overlay = Panel(
            pygame.Rect(0, 0, self.width, self.height),
            color=(0, 0, 0, 128),  # Semi-transparent black
            border_color=None,
            border_width=0,
            rounded=False
        )
        self.ui_elements.append(overlay)
        
        # Create message panel
        self.active_deck_message = Panel(
            pygame.Rect(self.width // 2 - 200, self.height // 2 - 100, 400, 200),
            color=(50, 60, 70),
            border_color=(100, 120, 140),
            border_width=2,
            rounded=True
        )
        
        # Message title
        message_title = Label(
            pygame.Rect(0, 20, 400, 40),
            f"Active Deck: {deck_name}",
            color=(220, 220, 220),
            font_size=24,
            align='center'
        )
        self.active_deck_message.add_element(message_title)
        
        # Message description
        message_desc = Label(
            pygame.Rect(0, 70, 400, 60),
            "You are about to play with your active deck. You can change your active deck in the Deck Builder.",
            color=(180, 180, 180),
            font_size=16,
            align='center'
        )
        self.active_deck_message.add_element(message_desc)
        
        # Continue button
        continue_button = Button(
            pygame.Rect(150, 140, 100, 30),
            "Continue",
            lambda: self._continue_to_game(difficulty),
            color=(60, 120, 60),
            hover_color=(80, 160, 80),
            font_size=16
        )
        self.active_deck_message.add_element(continue_button)
        
        # Add to UI elements
        self.ui_elements.append(self.active_deck_message)

    def _continue_to_game(self, difficulty):
        """Continue to the game after showing the active deck message."""
        # Close all popup panels
        self._close_all_popups()
        
        # Switch to game screen
        self.switch_to_screen("game", difficulty=difficulty)