"""
Main entry point for the card game with graphical user interface.
"""
import pygame
import pygame.freetype
import os
import sys
import time

# Fix imports to use the correct package structure
from src.screens.screen_manager import ScreenManager
from src.screens.home_screen import HomeScreen
from src.screens.game_screen import GameScreen
from src.screens.deck_building_screen import DeckBuildingScreen
from src.screens.shop_screen import ShopScreen


def main():
    """Main function to run the game with GUI."""
    # Initialize pygame
    pygame.init()
    pygame.freetype.init()
    
    # Set up the display
    width, height = 1024, 768
    display = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Card Battle")
    
    # Create directories if they don't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs(os.path.join("assets", "images", "cards", "common"), exist_ok=True)
    os.makedirs(os.path.join("assets", "images", "cards", "uncommon"), exist_ok=True)
    os.makedirs(os.path.join("assets", "images", "cards", "rare"), exist_ok=True)
    os.makedirs(os.path.join("assets", "images", "cards", "epic"), exist_ok=True)
    os.makedirs(os.path.join("assets", "images", "ui"), exist_ok=True)
    os.makedirs(os.path.join("assets", "images", "backgrounds"), exist_ok=True)
    os.makedirs(os.path.join("assets", "sounds"), exist_ok=True)
    
    # Create a screen manager
    screen_manager = ScreenManager(display)
    
    # Register screens
    screen_manager.register_screen("home", HomeScreen)
    screen_manager.register_screen("game", GameScreen)
    screen_manager.register_screen("deck_building", DeckBuildingScreen)
    screen_manager.register_screen("shop", ShopScreen)
    
    # Set the active screen to home
    screen_manager.switch_to("home")
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Calculate time delta
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                screen_manager.handle_event(event)
        
        # Update the current screen
        screen_manager.update(dt)
        
        # Render the current screen
        screen_manager.render()
        
        # Update the display
        pygame.display.flip()
    
    # Clean up
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())