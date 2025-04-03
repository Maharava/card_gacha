"""
Base screen class for the card game UI.
"""
import pygame


class Screen:
    """
    Base class for all game screens.
    
    Attributes:
        display (pygame.Surface): The main display surface
        manager: The screen manager responsible for screen transitions
        width (int): Screen width
        height (int): Screen height
    """
    
    def __init__(self, display, manager=None):
        """
        Initialize a new screen.
        
        Args:
            display (pygame.Surface): The main display surface
            manager: The screen manager responsible for switching screens
        """
        self.display = display
        self.manager = manager
        self.width, self.height = self.display.get_size()
        
        # Store for screen-specific resources
        self.resources = {}
        
        # UI elements (buttons, text fields, etc.)
        self.ui_elements = []
        
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event (pygame.event.Event): The event to handle
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        # Pass the event to UI elements
        for element in self.ui_elements:
            if hasattr(element, 'handle_event') and element.handle_event(event):
                return True
        
        return False
    
    def update(self, dt):
        """
        Update the screen logic.
        
        Args:
            dt (float): Time delta in seconds since the last update
        """
        # Update UI elements
        for element in self.ui_elements:
            if hasattr(element, 'update'):
                element.update(dt)
    
    def render(self):
        """
        Render the screen.
        
        This method should be overridden by subclasses.
        """
        # Clear the screen
        self.display.fill((0, 0, 0))
        
        # Render UI elements
        for element in self.ui_elements:
            if hasattr(element, 'render'):
                element.render(self.display)
    
    def load_resources(self):
        """
        Load screen-specific resources.
        
        This method should be overridden by subclasses that need to load resources.
        """
        pass
    
    def unload_resources(self):
        """
        Unload screen-specific resources to free memory.
        
        This method should be overridden by subclasses that loaded resources.
        """
        self.resources.clear()
    
    def on_enter(self, previous_screen=None, **kwargs):
        """
        Called when this screen becomes active.
        
        Args:
            previous_screen: The screen that was active before
            **kwargs: Additional arguments
        """
        # Load resources when the screen becomes active
        self.load_resources()
    
    def on_exit(self, next_screen=None):
        """
        Called when this screen is no longer active.
        
        Args:
            next_screen: The screen that will become active
        """
        # Unload resources when the screen is no longer active
        self.unload_resources()
        
    def switch_to_screen(self, screen_name, **kwargs):
        """
        Switch to a different screen.
        
        Args:
            screen_name (str): Name of the screen to switch to
            **kwargs: Additional arguments to pass to the new screen
        """
        if self.manager:
            self.manager.switch_to(screen_name, **kwargs)
