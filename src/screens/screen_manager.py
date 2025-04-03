"""
Screen manager for handling screen transitions and management.
"""
import pygame

# Fixed imports
from src.screens.screen import Screen


class ScreenManager:
    """
    Manages screen transitions and the active screen.
    
    Attributes:
        display (pygame.Surface): The main display surface
        screens (dict): Dictionary of screen instances
        active_screen (str): Name of the currently active screen
        transitions (dict): Dictionary of transition effects
    """
    
    def __init__(self, display):
        """
        Initialize the screen manager.
        
        Args:
            display (pygame.Surface): The main display surface
        """
        self.display = display
        self.screens = {}
        self.active_screen = None
        self.previous_screen = None
        
        # For transition effects
        self.transition_active = False
        self.transition_progress = 0
        self.transition_from = None
        self.transition_to = None
        self.transition_duration = 0.5  # seconds
        self.transition_time = 0
        
    def register_screen(self, name, screen_class, *args, **kwargs):
        """
        Register a screen with the manager.
        
        Args:
            name (str): Name of the screen
            screen_class: Screen class
            *args: Additional arguments for the screen class
            **kwargs: Additional keyword arguments for the screen class
        """
        # Create an instance of the screen
        screen = screen_class(self.display, self, *args, **kwargs)
        self.screens[name] = screen
        
        # If this is the first screen, make it active
        if self.active_screen is None:
            self.active_screen = name
            screen.on_enter()
    
    def switch_to(self, screen_name, **kwargs):
        """
        Switch to a different screen.
        
        Args:
            screen_name (str): Name of the screen to switch to
            **kwargs: Additional arguments to pass to the new screen
        """
        if screen_name not in self.screens:
            raise ValueError(f"No screen named {screen_name}")
        
        # Store the previous screen
        self.previous_screen = self.active_screen
        
        # Call on_exit for the current screen
        if self.active_screen:
            current_screen = self.screens[self.active_screen]
            current_screen.on_exit(screen_name)
        
        # Update the active screen
        self.active_screen = screen_name
        
        # Call on_enter for the new screen
        new_screen = self.screens[screen_name]
        previous_screen = self.screens[self.previous_screen] if self.previous_screen else None
        new_screen.on_enter(previous_screen, **kwargs)
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event (pygame.event.Event): The event to handle
        """
        # Pass the event to the active screen
        if self.active_screen:
            self.screens[self.active_screen].handle_event(event)
    
    def update(self, dt):
        """
        Update the active screen.
        
        Args:
            dt (float): Time delta in seconds since the last update
        """
        # Update the active screen
        if self.active_screen:
            self.screens[self.active_screen].update(dt)
    
    def render(self):
        """
        Render the active screen.
        """
        # Render the active screen
        if self.active_screen:
            self.screens[self.active_screen].render()
