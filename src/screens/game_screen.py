"""
Game screen for the card game, displaying the game board and handling user interactions.
"""
import pygame
import os

# Fixed imports
from src.screens.screen import Screen
from src.screens.ui_elements import Button, Label, Panel, ProgressBar, CardRenderer
from src.models.game_state import GameState, GamePhase
from src.controllers.game_controller import GameController
from src.controllers.player_controller import PlayerController
from src.controllers.ai_controller import AIController, create_ai_opponent
from src.utils.resource_loader import ResourceLoader
from src.utils.save_manager import SaveManager
from src.constants import PLAYER_FIELD_SIZE, PLAYER_STARTING_HAND_SIZE



class GameScreen(Screen):
    """
    Game screen displaying the game board and handling gameplay.
    
    This screen visualizes:
    - Player and opponent fields
    - Cards in hand
    - Player and opponent stats (health, energy)
    - Turn and phase indicators
    - Game controls
    """
    
    def __init__(self, display, manager=None):
        """
        Initialize the game screen.
        
        Args:
            display (pygame.Surface): The main display surface
            manager: The screen manager
        """
        super().__init__(display, manager)
        
        self.background_color = (30, 40, 50)
        
        # Game objects (initialized in on_enter)
        self.game_state = None
        self.game_controller = None
        self.player_controller = None
        self.ai_controller = None
        
        # UI state
        self.selected_card_index = None
        self.selected_field_index = None
        self.game_log = []  # Store recent game events for display
        self.card_animations = []  # Store active card animations
        
        # Card renderer
        self.card_renderer = CardRenderer(card_size=(100, 150))
        
        # Card positions
        self.card_margin = 10
        self.hand_y = self.height - 170
        self.player_field_y = self.height - 340
        self.opponent_field_y = 140
        
        # Create UI elements
        self._create_ui_elements()
    
    def _create_ui_elements(self):
        """Create the UI elements for the game screen."""
        # Top panel for opponent info
        opponent_panel = Panel(
            pygame.Rect(10, 10, self.width - 20, 100),
            color=(40, 40, 50),
            border_color=(80, 80, 100),
            border_width=2,
            rounded=True
        )
        
        # Opponent name
        self.opponent_name_label = Label(
            pygame.Rect(20, 20, 200, 30),
            "Opponent",
            color=(220, 220, 220),
            font_size=20,
            align='left'
        )
        opponent_panel.add_element(self.opponent_name_label)
        
        # Opponent health bar
        self.opponent_health_label = Label(
            pygame.Rect(20, 50, 80, 20),
            "Health:",
            color=(220, 220, 220),
            font_size=16,
            align='left'
        )
        opponent_panel.add_element(self.opponent_health_label)
        
        self.opponent_health_bar = ProgressBar(
            pygame.Rect(100, 50, 150, 20),
            value=1.0,
            fill_color=(200, 60, 60)
        )
        opponent_panel.add_element(self.opponent_health_bar)
        
        self.opponent_health_value = Label(
            pygame.Rect(260, 50, 80, 20),
            "10/10",
            color=(220, 220, 220),
            font_size=16,
            align='left'
        )
        opponent_panel.add_element(self.opponent_health_value)
        
        # Opponent energy
        self.opponent_energy_label = Label(
            pygame.Rect(20, 75, 80, 20),
            "Energy:",
            color=(220, 220, 220),
            font_size=16,
            align='left'
        )
        opponent_panel.add_element(self.opponent_energy_label)
        
        self.opponent_energy_bar = ProgressBar(
            pygame.Rect(100, 75, 150, 20),
            value=1.0,
            fill_color=(60, 120, 200)
        )
        opponent_panel.add_element(self.opponent_energy_bar)
        
        self.opponent_energy_value = Label(
            pygame.Rect(260, 75, 80, 20),
            "3/3",
            color=(220, 220, 220),
            font_size=16,
            align='left'
        )
        opponent_panel.add_element(self.opponent_energy_value)
        
        # Bottom panel for player info
        player_panel = Panel(
            pygame.Rect(10, self.height - 110, self.width - 20, 100),
            color=(40, 40, 50),
            border_color=(80, 80, 100),
            border_width=2,
            rounded=True
        )
        
        # Player name
        self.player_name_label = Label(
            pygame.Rect(20, 20, 200, 30),
            "Player",
            color=(220, 220, 220),
            font_size=20,
            align='left'
        )
        player_panel.add_element(self.player_name_label)
        
        # Player health bar
        self.player_health_label = Label(
            pygame.Rect(20, 50, 80, 20),
            "Health:",
            color=(220, 220, 220),
            font_size=16,
            align='left'
        )
        player_panel.add_element(self.player_health_label)
        
        self.player_health_bar = ProgressBar(
            pygame.Rect(100, 50, 150, 20),
            value=1.0,
            fill_color=(200, 60, 60)
        )
        player_panel.add_element(self.player_health_bar)
        
        self.player_health_value = Label(
            pygame.Rect(260, 50, 80, 20),
            "10/10",
            color=(220, 220, 220),
            font_size=16,
            align='left'
        )
        player_panel.add_element(self.player_health_value)
        
        # Player energy
        self.player_energy_label = Label(
            pygame.Rect(20, 75, 80, 20),
            "Energy:",
            color=(220, 220, 220),
            font_size=16,
            align='left'
        )
        player_panel.add_element(self.player_energy_label)
        
        self.player_energy_bar = ProgressBar(
            pygame.Rect(100, 75, 150, 20),
            value=1.0,
            fill_color=(60, 120, 200)
        )
        player_panel.add_element(self.player_energy_bar)
        
        self.player_energy_value = Label(
            pygame.Rect(260, 75, 80, 20),
            "3/3",
            color=(220, 220, 220),
            font_size=16,
            align='left'
        )
        player_panel.add_element(self.player_energy_value)
        
        # Right panel for game info and controls
        game_panel = Panel(
            pygame.Rect(self.width - 210, 120, 200, self.height - 240),
            color=(40, 40, 50),
            border_color=(80, 80, 100),
            border_width=2,
            rounded=True
        )
        
        # Turn counter
        self.turn_label = Label(
            pygame.Rect(20, 20, 160, 30),
            "Turn: 1",
            color=(220, 220, 220),
            font_size=20,
            align='center'
        )
        game_panel.add_element(self.turn_label)
        
        # Current phase
        self.phase_label = Label(
            pygame.Rect(20, 50, 160, 30),
            "Phase: Draw",
            color=(220, 220, 220),
            font_size=16,
            align='center'
        )
        game_panel.add_element(self.phase_label)
        
        # Current player
        self.current_player_label = Label(
            pygame.Rect(20, 80, 160, 30),
            "Current: Player",
            color=(220, 220, 220),
            font_size=16,
            align='center'
        )
        game_panel.add_element(self.current_player_label)
        
        # Divider
        game_panel.add_element(Label(
            pygame.Rect(20, 120, 160, 20),
            "──────────────",
            color=(150, 150, 150),
            font_size=16,
            align='center'
        ))
        
        # Game log label
        game_panel.add_element(Label(
            pygame.Rect(20, 140, 160, 30),
            "Game Log",
            color=(220, 220, 220),
            font_size=18,
            align='center'
        ))
        
        # Game log will be rendered directly in render method
        
        # Control buttons at the bottom
        # End phase button
        self.end_phase_button = Button(
            pygame.Rect(20, game_panel.rect.height - 120, 160, 40),
            "End Phase",
            self._on_end_phase_button_click,
            color=(80, 80, 120),
            hover_color=(100, 100, 160),
            font_size=18
        )
        game_panel.add_element(self.end_phase_button)
        
        # Concede button
        self.concede_button = Button(
            pygame.Rect(20, game_panel.rect.height - 70, 160, 40),
            "Concede",
            self._on_concede_button_click,
            color=(120, 60, 60),
            hover_color=(160, 80, 80),
            font_size=18
        )
        game_panel.add_element(self.concede_button)
        
        # Add all panels to the UI elements list
        self.ui_elements = [opponent_panel, player_panel, game_panel]
        
        # When game is over, show this panel
        self.game_over_panel = None
    
    def on_enter(self, previous_screen=None, **kwargs):
        """
        Called when this screen becomes active.
        
        Args:
            previous_screen: The screen that was active before
            **kwargs: Additional arguments
        """
        super().on_enter(previous_screen)
        
        # Get the difficulty from kwargs
        difficulty = kwargs.get('difficulty', 'normal')
        
        # Initialize game
        self._initialize_game(difficulty)
        
        # Update UI with initial state
        self._update_ui_from_game_state()
    
    def _initialize_game(self, difficulty):
        """
        Initialize the game by loading resources and setting up players.
        
        Args:
            difficulty (str): AI difficulty level ('easy', 'normal', 'hard')
        """
        # Load cards
        card_database = ResourceLoader.load_cards()
        
        # Load player data
        player = None
        if SaveManager.player_exists():
            player = SaveManager.load_player(card_database)
        
        if player is None:
            # Create a new player with a starter deck if no save exists
            from ..models.deck import Deck
            from ..models.player import Player
            starter_deck = Deck.create_starter_deck(card_database)
            player = Player("Player", starter_deck)
            player.credits = 50  # Give some starting credits
            SaveManager.save_player(player)
        
        # Create AI opponent
        opponent = create_ai_opponent(card_database, difficulty)
        
        # Create game state
        self.game_state = GameState(player, opponent)
        
        # Create controllers
        self.game_controller = GameController(self.game_state)
        self.player_controller = PlayerController(self.game_state)
        self.ai_controller = AIController.create_for_difficulty(self.game_state, difficulty)
        
        # Start a new game
        self.game_controller.start_game()
        
        # Draw starting hands
        player.draw_starting_hand(PLAYER_STARTING_HAND_SIZE)
        opponent.draw_starting_hand(PLAYER_STARTING_HAND_SIZE)
        
        # Load card images
        for card_id, card in card_database.items():
            self.card_renderer.load_card_image(card_id, card.image_path)
        
        # Clear game log
        self.game_log = ["Game started", f"Opponent: {opponent.name}", "Draw your cards"]
    
    def _update_ui_from_game_state(self):
        """Update UI elements based on the current game state."""
        if not self.game_state:
            return
        
        # Update player info
        player = self.game_state.player
        self.player_name_label.set_text(player.name)
        self.player_health_value.set_text(f"{player.health}/{player.max_health}")
        self.player_health_bar.set_value(player.health / player.max_health)
        self.player_energy_value.set_text(f"{player.energy}/{player.max_energy}")
        self.player_energy_bar.set_value(player.energy / player.max_energy)
        
        # Update opponent info
        opponent = self.game_state.opponent
        self.opponent_name_label.set_text(opponent.name)
        self.opponent_health_value.set_text(f"{opponent.health}/{opponent.max_health}")
        self.opponent_health_bar.set_value(opponent.health / opponent.max_health)
        self.opponent_energy_value.set_text(f"{opponent.energy}/{opponent.max_energy}")
        self.opponent_energy_bar.set_value(opponent.energy / opponent.max_energy)
        
        # Update game info
        self.turn_label.set_text(f"Turn: {self.game_state.turn_number}")
        self.phase_label.set_text(f"Phase: {self.game_state.current_phase.name}")
        
        current_player_name = self.game_state.current_player.name
        self.current_player_label.set_text(f"Current: {current_player_name}")
        
        # Update button states based on game phase
        is_play_phase = self.game_state.current_phase == GamePhase.PLAY
        is_player_turn = self.game_state.current_player == player
        
        self.end_phase_button.enabled = is_play_phase and is_player_turn
        
        # If game is over, show game over panel
        if self.game_state.game_over and not self.game_over_panel:
            self._show_game_over_panel()
    
    def _show_game_over_panel(self):
        """Show the game over panel."""
        winner = self.game_state.winner
        
        # Create game over panel
        self.game_over_panel = Panel(
            pygame.Rect(self.width // 2 - 200, self.height // 2 - 150, 400, 300),
            color=(40, 40, 60),
            border_color=(100, 100, 140),
            border_width=3,
            rounded=True
        )
        
        # Game over title
        game_over_title = Label(
            pygame.Rect(0, 30, 400, 40),
            "Game Over",
            color=(220, 220, 220),
            font_size=32,
            align='center'
        )
        self.game_over_panel.add_element(game_over_title)
        
        # Winner
        winner_text = f"{winner.name} Wins!" if winner else "Draw!"
        winner_label = Label(
            pygame.Rect(0, 90, 400, 40),
            winner_text,
            color=(255, 220, 100) if winner == self.game_state.player else (200, 200, 200),
            font_size=28,
            align='center'
        )
        self.game_over_panel.add_element(winner_label)
        
        # Reward message if player won
        if winner == self.game_state.player:
            from ..constants import VICTORY_REWARD
            reward_label = Label(
                pygame.Rect(0, 140, 400, 30),
                f"You earned {VICTORY_REWARD} credits!",
                color=(100, 255, 100),
                font_size=20,
                align='center'
            )
            self.game_over_panel.add_element(reward_label)
        
        # Buttons
        # Play again button
        play_again_button = Button(
            pygame.Rect(100, 190, 200, 40),
            "Play Again",
            self._on_play_again_button_click,
            color=(60, 120, 60),
            hover_color=(80, 160, 80),
            font_size=20
        )
        self.game_over_panel.add_element(play_again_button)
        
        # Return to main menu button
        main_menu_button = Button(
            pygame.Rect(100, 240, 200, 40),
            "Main Menu",
            self._on_main_menu_button_click,
            color=(80, 80, 120),
            hover_color=(100, 100, 160),
            font_size=20
        )
        self.game_over_panel.add_element(main_menu_button)
        
        # Add to UI elements
        self.ui_elements.append(self.game_over_panel)
    
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
        
        # If game is over, don't handle gameplay events
        if self.game_state.game_over:
            return False
        
        # Only handle these events if it's the player's turn and the play phase
        if (self.game_state.current_player == self.game_state.player and 
            self.game_state.current_phase == GamePhase.PLAY):
            
            # Handle card selection from hand
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if clicked on a card in hand
                for i, card in enumerate(self.game_state.player.hand):
                    card_x = self._get_hand_card_x(i)
                    card_rect = pygame.Rect(card_x, self.hand_y, 
                                         self.card_renderer.card_size[0], 
                                         self.card_renderer.card_size[1])
                    
                    if card_rect.collidepoint(event.pos):
                        # Select this card if it's playable
                        if card.cost <= self.game_state.player.energy:
                            self.selected_card_index = i
                        return True
                
                # Check if clicked on a field position
                if self.selected_card_index is not None:
                    for i in range(PLAYER_FIELD_SIZE):
                        field_x = self._get_field_card_x(i)
                        field_rect = pygame.Rect(field_x, self.player_field_y, 
                                             self.card_renderer.card_size[0], 
                                             self.card_renderer.card_size[1])
                        
                        if field_rect.collidepoint(event.pos):
                            # Try to play the card here
                            if self.game_state.player.field[i] is None:
                                self._play_card_to_field(self.selected_card_index, i)
                            self.selected_card_index = None
                            return True
            
            # Clear selection on right click
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.selected_card_index = None
                return True
        
        return False
    
    def update(self, dt):
        """
        Update the game screen logic.
        
        Args:
            dt (float): Time delta in seconds since the last update
        """
        super().update(dt)
        
        # If AI's turn, let it play
        if not self.game_state.game_over and self.game_state.current_player == self.game_state.opponent:
            # Process the turn based on current phase
            if self.game_state.current_phase == GamePhase.DRAW:
                events = self.game_controller.process_turn()
                self._handle_game_events(events)
                self.game_controller.advance_phase()
                self._update_ui_from_game_state()
                
            elif self.game_state.current_phase == GamePhase.PLAY:
                # Let AI make its play decisions
                ai_results = self.ai_controller.take_turn()
                self._handle_game_events({"events": ai_results["events"]})
                
                # AI automatically ends its play phase
                self.game_controller.advance_phase()
                self._update_ui_from_game_state()
                
            elif self.game_state.current_phase == GamePhase.ATTACK:
                events = self.game_controller.process_turn()
                self._handle_game_events(events)
                self.game_controller.advance_phase()
                self._update_ui_from_game_state()
                
            elif self.game_state.current_phase == GamePhase.END:
                events = self.game_controller.process_turn()
                self._handle_game_events(events)
                self.game_controller.advance_phase()
                self._update_ui_from_game_state()
        
        # If it's player's turn but not play phase, auto-progress
        elif not self.game_state.game_over and self.game_state.current_player == self.game_state.player:
            if self.game_state.current_phase == GamePhase.DRAW:
                events = self.game_controller.process_turn()
                self._handle_game_events(events)
                self.game_controller.advance_phase()
                self._update_ui_from_game_state()
                
            elif self.game_state.current_phase == GamePhase.ATTACK:
                events = self.game_controller.process_turn()
                self._handle_game_events(events)
                self.game_controller.advance_phase()
                self._update_ui_from_game_state()
                
            elif self.game_state.current_phase == GamePhase.END:
                events = self.game_controller.process_turn()
                self._handle_game_events(events)
                self.game_controller.advance_phase()
                self._update_ui_from_game_state()
                
        # Update animations
        self._update_animations(dt)
    
    def _update_animations(self, dt):
        """Update card animations."""
        # Animation handling would go here
        # For now just placeholder
        pass
    
    def _handle_game_events(self, events_data):
        """
        Handle game events and update the game log.
        
        Args:
            events_data (dict): Events data from the game controller
        """
        if "events" not in events_data:
            return
        
        for event in events_data["events"]:
            event_type = event.get("type", "")
            
            if event_type == "draw":
                message = f"{event['player']} drew {event['card']}"
                self.game_log.append(message)
            
            elif event_type == "deck_empty":
                message = f"{event['player']} has no more cards to draw!"
                self.game_log.append(message)
            
            elif event_type == "card_played" or event_type == "ai_card_played":
                if event_type == "card_played":
                    message = f"You played {event['card']} to position {event['field_position']}"
                else:
                    message = f"AI played {event['card']} to position {event['field_position']}"
                self.game_log.append(message)
            
            elif event_type == "card_attack":
                message = f"{event['attacker']} attacks {event['defender']} for {event['attack_damage']}"
                self.game_log.append(message)
            
            elif event_type == "card_counter_attack":
                message = f"{event['attacker']} counter-attacks {event['defender']} for {event['attack_damage']}"
                self.game_log.append(message)
            
            elif event_type == "card_destroyed":
                message = f"{event['card']} was destroyed!"
                self.game_log.append(message)
            
            elif event_type == "player_damage":
                message = f"{event['player']} takes {event['damage']} damage from {event['source']}"
                self.game_log.append(message)
            
            elif event_type == "game_over":
                message = f"Game over! {event['winner']} wins!"
                self.game_log.append(message)
            
            elif event_type == "credits_awarded":
                message = f"{event['player']} received {event['amount']} credits"
                self.game_log.append(message)
            
            elif event_type == "phase_ended":
                message = f"{event['player']} ended {event['phase']} phase"
                self.game_log.append(message)
        
        # Keep log at a reasonable size
        if len(self.game_log) > 10:
            self.game_log = self.game_log[-10:]
    
    def _get_hand_card_x(self, index):
        """
        Calculate the x-coordinate for a card in hand.
        
        Args:
            index (int): Index of the card in hand
            
        Returns:
            int: X-coordinate for the card
        """
        hand_size = len(self.game_state.player.hand)
        total_width = hand_size * (self.card_renderer.card_size[0] + self.card_margin) - self.card_margin
        start_x = (self.width - 220) // 2 - total_width // 2
        return start_x + index * (self.card_renderer.card_size[0] + self.card_margin)
    
    def _get_field_card_x(self, index):
        """
        Calculate the x-coordinate for a card on the field.
        
        Args:
            index (int): Index of the field position
            
        Returns:
            int: X-coordinate for the card
        """
        total_width = PLAYER_FIELD_SIZE * (self.card_renderer.card_size[0] + self.card_margin) - self.card_margin
        start_x = (self.width - 220) // 2 - total_width // 2
        return start_x + index * (self.card_renderer.card_size[0] + self.card_margin)
    
    def _play_card_to_field(self, hand_index, field_index):
        """
        Play a card from hand to the field.
        
        Args:
            hand_index (int): Index of the card in hand
            field_index (int): Index of the field position
        """
        result = self.player_controller.play_card(self.game_state.player, hand_index, field_index)
        
        if result["success"]:
            # Handle the played card events
            self._handle_game_events(result)
            self._update_ui_from_game_state()
        else:
            # Add the error message to the game log
            self.game_log.append(f"Error: {result['message']}")
    
    def _on_end_phase_button_click(self):
        """Handle end phase button click."""
        if (self.game_state.current_player == self.game_state.player and 
            self.game_state.current_phase == GamePhase.PLAY):
            
            result = self.player_controller.end_play_phase(self.game_state.player)
            
            if result["success"]:
                self._handle_game_events(result)
                self.game_controller.advance_phase()
                self._update_ui_from_game_state()
    
    def _on_concede_button_click(self):
        """Handle concede button click."""
        # Set the opponent as the winner
        self.game_state.game_over = True
        self.game_state.winner = self.game_state.opponent
        
        # Add to game log
        self.game_log.append("You conceded the game")
        
        # Show game over panel
        self._show_game_over_panel()
    
    def _on_play_again_button_click(self):
        """Handle play again button click."""
        # Save player progress
        SaveManager.save_player(self.game_state.player)
        
        # Get current difficulty
        difficulty = 'normal'
        opponent_name = self.game_state.opponent.name.lower()
        if 'easy' in opponent_name:
            difficulty = 'easy'
        elif 'hard' in opponent_name:
            difficulty = 'hard'
        
        # Remove game over panel
        if self.game_over_panel in self.ui_elements:
            self.ui_elements.remove(self.game_over_panel)
            self.game_over_panel = None
        
        # Reinitialize the game
        self._initialize_game(difficulty)
        self._update_ui_from_game_state()
    
    def _on_main_menu_button_click(self):
        """Handle main menu button click."""
        # Save player progress
        SaveManager.save_player(self.game_state.player)
        
        # Return to main menu
        self.switch_to_screen("home")
    
    def load_resources(self):
        """Load screen-specific resources."""
        # Load background image if available
        try:
            bg_path = os.path.join("assets", "images", "backgrounds", "game_bg.jpg")
            self.resources["background"] = pygame.image.load(bg_path)
            self.resources["background"] = pygame.transform.scale(
                self.resources["background"], (self.width, self.height)
            )
        except (pygame.error, FileNotFoundError):
            # Create a gradient background if image loading fails
            self.resources["background"] = pygame.Surface((self.width, self.height))
            for y in range(self.height):
                # Create a dark blue gradient
                color = (
                    20 + int(y / self.height * 10),
                    30 + int(y / self.height * 10),
                    40 + int(y / self.height * 15)
                )
                pygame.draw.line(self.resources["background"], color, (0, y), (self.width, y))
    
    def render(self):
        """Render the game screen."""
        # Draw background
        if "background" in self.resources:
            self.display.blit(self.resources["background"], (0, 0))
        else:
            self.display.fill(self.background_color)
        
        # Draw the game board
        self._render_game_board()
        
        # Draw the cards in hand
        self._render_hand()
        
        # Render UI elements
        for element in self.ui_elements:
            element.render(self.display)
        
        # Render game log in the game panel (right side panel)
        self._render_game_log()
    
    def _render_game_board(self):
        """Render the game board including player and opponent fields."""
        if not self.game_state:
            return
        
        # Draw field positions for player
        for i in range(PLAYER_FIELD_SIZE):
            x = self._get_field_card_x(i)
            
            # Draw field position outline
            field_rect = pygame.Rect(x, self.player_field_y, 
                                   self.card_renderer.card_size[0], 
                                   self.card_renderer.card_size[1])
            
            # Different color if a card can be played here
            if (self.selected_card_index is not None and 
                self.game_state.current_phase == GamePhase.PLAY and
                self.game_state.current_player == self.game_state.player and
                self.game_state.player.field[i] is None):
                pygame.draw.rect(self.display, (100, 100, 150), field_rect, width=2, border_radius=5)
            else:
                pygame.draw.rect(self.display, (80, 80, 80), field_rect, width=1, border_radius=5)
            
            # Draw card if one is present
            if self.game_state.player.field[i]:
                card = self.game_state.player.field[i]
                self.card_renderer.render_card(self.display, card, (x, self.player_field_y))
        
        # Draw field positions for opponent
        for i in range(PLAYER_FIELD_SIZE):
            x = self._get_field_card_x(i)
            
            # Draw field position outline
            field_rect = pygame.Rect(x, self.opponent_field_y, 
                                   self.card_renderer.card_size[0], 
                                   self.card_renderer.card_size[1])
            pygame.draw.rect(self.display, (80, 80, 80), field_rect, width=1, border_radius=5)
            
            # Draw card if one is present
            if self.game_state.opponent.field[i]:
                card = self.game_state.opponent.field[i]
                self.card_renderer.render_card(self.display, card, (x, self.opponent_field_y))
        
        # Draw battlefield connection lines
        for i in range(PLAYER_FIELD_SIZE):
            player_x = self._get_field_card_x(i) + self.card_renderer.card_size[0] // 2
            player_y = self.player_field_y
            opponent_x = self._get_field_card_x(i) + self.card_renderer.card_size[0] // 2
            opponent_y = self.opponent_field_y + self.card_renderer.card_size[1]
            
            # Draw a dashed line connecting the positions
            dash_length = 5
            gap_length = 5
            distance = opponent_y - player_y
            num_dashes = distance // (dash_length + gap_length)
            
            for j in range(num_dashes):
                start_y = player_y + j * (dash_length + gap_length)
                end_y = start_y + dash_length
                if end_y > opponent_y:
                    end_y = opponent_y
                
                pygame.draw.line(self.display, (100, 100, 120), 
                               (player_x, start_y), (player_x, end_y), 1)
    
    def _render_hand(self):
        """Render the player's hand."""
        if not self.game_state:
            return
        
        # Draw each card in hand
        for i, card in enumerate(self.game_state.player.hand):
            x = self._get_hand_card_x(i)
            
            # Determine if card is selectable (can be played)
            selectable = (self.game_state.current_phase == GamePhase.PLAY and
                         self.game_state.current_player == self.game_state.player and
                         card.cost <= self.game_state.player.energy)
            
            # Determine if card is selected
            selected = i == self.selected_card_index
            
            # Draw the card
            self.card_renderer.render_card(self.display, card, (x, self.hand_y), 
                                        selectable=selectable, selected=selected)
    
    def _render_game_log(self):
        """Render the game log in the game panel."""
        if not self.game_state:
            return
        
        # Log area in the game panel
        log_rect = pygame.Rect(self.width - 200, 170, 180, 300)
        log_y = log_rect.y + 10
        
        # Draw each log entry
        font = pygame.freetype.SysFont('Arial', 12)
        line_height = 20
        
        for i, message in enumerate(self.game_log):
            # Skip if too many messages to fit
            if i >= 10:
                break
            
            # Wrap text to fit in the panel
            wrapped_text = self._wrap_text(message, font, log_rect.width - 20)
            
            for line in wrapped_text:
                log_surf, log_rect = font.render(line, (200, 200, 200))
                log_rect.x = self.width - 190
                log_rect.y = log_y
                self.display.blit(log_surf, log_rect)
                log_y += line_height
    
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