"""
UI elements for the card game.
"""
import pygame
import pygame.freetype

# No relative imports to fix in this file


class Button:
    """
    Interactive button UI element.
    
    Attributes:
        rect (pygame.Rect): The button's rectangle
        text (str): Text to display on the button
        callback: Function to call when the button is clicked
        color (tuple): RGB color of the button
        hover_color (tuple): RGB color when the button is hovered
        text_color (tuple): RGB color of the text
        font: Font used for the text
        enabled (bool): Whether the button is enabled
    """
    
    def __init__(self, rect, text, callback, color=(100, 100, 100), 
                 hover_color=(150, 150, 150), text_color=(255, 255, 255),
                 font_size=20, enabled=True):
        """
        Initialize a new button.
        
        Args:
            rect (pygame.Rect): The button's rectangle
            text (str): Text to display on the button
            callback: Function to call when the button is clicked
            color (tuple): RGB color of the button
            hover_color (tuple): RGB color when the button is hovered
            text_color (tuple): RGB color of the text
            font_size (int): Size of the font
            enabled (bool): Whether the button is enabled
        """
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.enabled = enabled
        
        # Initialize font
        self.font = pygame.freetype.SysFont('Arial', self.font_size)
        
        # State
        self.hovered = False
        self.pressed = False
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event (pygame.event.Event): The event to handle
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        if not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            # Update hover state
            self.hovered = self.rect.collidepoint(event.pos)
            return self.hovered
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Left mouse button pressed
            if self.rect.collidepoint(event.pos):
                self.hovered = True
                self.pressed = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Left mouse button released
            was_pressed = self.pressed
            self.pressed = False
            
            if was_pressed and self.rect.collidepoint(event.pos) and self.callback:
                self.callback()
                return True
        
        return False
    
    def update(self, dt):
        """
        Update the button logic.
        
        Args:
            dt (float): Time delta in seconds since the last update
        """
        # Update hover state
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def render(self, surface):
        """
        Render the button.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Choose color based on state
        if not self.enabled:
            color = (70, 70, 70)
        elif self.pressed and self.hovered:
            color = (80, 80, 80)
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.color
        
        # Draw button background
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        
        # Draw button border
        border_color = (200, 200, 200) if self.hovered else (50, 50, 50)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=5)
        
        # Render text
        text_surface, text_rect = self.font.render(self.text, self.text_color)
        text_rect.center = self.rect.center
        surface.blit(text_surface, text_rect)


class Label:
    """
    Text label UI element.
    
    Attributes:
        rect (pygame.Rect): The label's rectangle
        text (str): Text to display
        color (tuple): RGB color of the text
        font: Font used for the text
        align (str): Text alignment ('left', 'center', 'right')
    """
    
    def __init__(self, rect, text, color=(255, 255, 255), font_size=20, align='left'):
        """
        Initialize a new label.
        
        Args:
            rect (pygame.Rect): The label's rectangle
            text (str): Text to display
            color (tuple): RGB color of the text
            font_size (int): Size of the font
            align (str): Text alignment ('left', 'center', 'right')
        """
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.font_size = font_size
        self.align = align
        
        # Initialize font
        self.font = pygame.freetype.SysFont('Arial', self.font_size)
    
    def set_text(self, text):
        """
        Set the label text.
        
        Args:
            text (str): New text to display
        """
        self.text = text
    
    def render(self, surface):
        """
        Render the label.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Render text
        text_surface, text_rect = self.font.render(self.text, self.color)
        
        # Position based on alignment
        if self.align == 'left':
            text_rect.topleft = self.rect.topleft
        elif self.align == 'center':
            text_rect.center = self.rect.center
        elif self.align == 'right':
            text_rect.topright = self.rect.topright
        
        surface.blit(text_surface, text_rect)


class Panel:
    """
    Container panel for grouping UI elements.
    
    Attributes:
        rect (pygame.Rect): The panel's rectangle
        color (tuple): RGB color of the panel
        border_color (tuple): RGB color of the border
        border_width (int): Width of the border
        elements (list): UI elements contained in the panel
    """
    
    def __init__(self, rect, color=(50, 50, 50), border_color=(100, 100, 100), 
                 border_width=1, rounded=False):
        """
        Initialize a new panel.
        
        Args:
            rect (pygame.Rect): The panel's rectangle
            color (tuple): RGB or RGBA color of the panel
            border_color (tuple): RGB color of the border, or None for no border
            border_width (int): Width of the border
            rounded (bool): Whether to round the corners
        """
        self.rect = pygame.Rect(rect)
        self.color = color
        self.border_color = border_color
        self.border_width = border_width
        self.rounded = rounded
        
        # UI elements in the panel
        self.elements = []
        
        # Create surface for semi-transparent panels
        self.has_alpha = len(self.color) == 4 and self.color[3] < 255
        if self.has_alpha:
            self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
    
    def add_element(self, element):
        """
        Add a UI element to the panel.
        
        Args:
            element: UI element to add
        """
        self.elements.append(element)
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event (pygame.event.Event): The event to handle
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        # Pass the event to contained elements
        for element in self.elements:
            if hasattr(element, 'handle_event') and element.handle_event(event):
                return True
        
        return False
    
    def update(self, dt):
        """
        Update the panel logic.
        
        Args:
            dt (float): Time delta in seconds since the last update
        """
        # Update contained elements
        for element in self.elements:
            if hasattr(element, 'update'):
                element.update(dt)
    
    def render(self, surface):
        """
        Render the panel and its elements.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Handle semi-transparent panels
        if self.has_alpha:
            # Fill the panel surface with the transparent color
            self.surface.fill(self.color)
            
            # Render contained elements to the panel surface
            for element in self.elements:
                if hasattr(element, 'render'):
                    # Adjust element position to be relative to panel
                    original_rect = element.rect.copy()
                    element.rect.x -= self.rect.x
                    element.rect.y -= self.rect.y
                    
                    # Render element to panel surface
                    element.render(self.surface)
                    
                    # Restore original position
                    element.rect = original_rect
            
            # Blit panel surface to main surface
            surface.blit(self.surface, self.rect)
            
            # Draw border if needed
            if self.border_color and self.border_width > 0:
                if self.rounded:
                    pygame.draw.rect(surface, self.border_color, self.rect, 
                                   width=self.border_width, border_radius=10)
                else:
                    pygame.draw.rect(surface, self.border_color, self.rect, 
                                   width=self.border_width)
        else:
            # Draw panel background
            if self.rounded:
                pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
                if self.border_color and self.border_width > 0:
                    pygame.draw.rect(surface, self.border_color, self.rect, 
                                   width=self.border_width, border_radius=10)
            else:
                pygame.draw.rect(surface, self.color, self.rect)
                if self.border_color and self.border_width > 0:
                    pygame.draw.rect(surface, self.border_color, self.rect, 
                                   width=self.border_width)
            
            # Render contained elements
            for element in self.elements:
                if hasattr(element, 'render'):
                    element.render(surface)


class ProgressBar:
    """
    Progress bar UI element.
    
    Attributes:
        rect (pygame.Rect): The progress bar's rectangle
        value (float): Current value (0.0 to 1.0)
        bg_color (tuple): RGB color of the background
        fill_color (tuple): RGB color of the fill
        border_color (tuple): RGB color of the border
    """
    
    def __init__(self, rect, value=1.0, bg_color=(50, 50, 50), 
                 fill_color=(0, 200, 0), border_color=(100, 100, 100)):
        """
        Initialize a new progress bar.
        
        Args:
            rect (pygame.Rect): The progress bar's rectangle
            value (float): Initial value (0.0 to 1.0)
            bg_color (tuple): RGB color of the background
            fill_color (tuple): RGB color of the fill
            border_color (tuple): RGB color of the border
        """
        self.rect = pygame.Rect(rect)
        self.value = max(0.0, min(1.0, value))  # Clamp to [0, 1]
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
    
    def set_value(self, value):
        """
        Set the progress bar value.
        
        Args:
            value (float): New value (0.0 to 1.0)
        """
        self.value = max(0.0, min(1.0, value))  # Clamp to [0, 1]
    
    def render(self, surface):
        """
        Render the progress bar.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Draw background
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=3)
        
        # Draw fill
        fill_width = int(self.rect.width * self.value)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.left, self.rect.top, fill_width, self.rect.height)
            pygame.draw.rect(surface, self.fill_color, fill_rect, border_radius=3)
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, self.rect, width=1, border_radius=3)


class CardRenderer:
    """
    Utility class for rendering card visuals.
    
    Attributes:
        card_size (tuple): Width and height of cards
        card_images (dict): Dictionary of card images
        default_image: Default image to use when a specific card image is not available
    """
    
    def __init__(self, card_size=(120, 180)):
        """
        Initialize the card renderer.
        
        Args:
            card_size (tuple): Width and height of cards
        """
        self.card_size = card_size
        self.card_images = {}
        self.default_image = None
        
        # Font for card text
        self.name_font = pygame.freetype.SysFont('Arial', 14)
        self.stats_font = pygame.freetype.SysFont('Arial', 16, bold=True)
        self.flavor_font = pygame.freetype.SysFont('Arial', 10, italic=True)
        
        # Colors based on rarity
        self.rarity_colors = {
            "common": (200, 200, 200),
            "uncommon": (100, 200, 100),
            "rare": (100, 100, 240),
            "epic": (200, 100, 200)
        }
        
        # Background colors
        self.bg_color = (40, 40, 40)
        self.border_color = (100, 100, 100)
    
    def load_card_image(self, card_id, image_path):
        """
        Load a card image.
        
        Args:
            card_id (str): ID of the card
            image_path (str): Path to the image file
        """
        try:
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(image, self.card_size)
            self.card_images[card_id] = image
        except pygame.error:
            print(f"Warning: Could not load image for card {card_id}: {image_path}")
            
            # If no default image exists, create one
            if self.default_image is None:
                self.default_image = pygame.Surface(self.card_size)
                self.default_image.fill((70, 70, 70))
    
    def render_card(self, surface, card, position, face_up=True, selectable=False, selected=False):
        """
        Render a card.
        
        Args:
            surface (pygame.Surface): Surface to render on
            card: Card object to render
            position (tuple): Position (x, y) to render the card
            face_up (bool): Whether the card is face up
            selectable (bool): Whether the card is selectable
            selected (bool): Whether the card is selected
        
        Returns:
            pygame.Rect: Rectangle containing the card
        """
        # Create card rectangle
        card_rect = pygame.Rect(position[0], position[1], self.card_size[0], self.card_size[1])
        
        # If card is face down, render the back
        if not face_up:
            pygame.draw.rect(surface, (60, 40, 40), card_rect, border_radius=5)
            pygame.draw.rect(surface, (100, 80, 80), card_rect, width=2, border_radius=5)
            
            # Draw a pattern on the back
            pygame.draw.rect(surface, (80, 60, 60), 
                            (card_rect.left + 10, card_rect.top + 10, 
                            card_rect.width - 20, card_rect.height - 20), 
                            border_radius=3)
            
            return card_rect
        
        # Render card front
        # Get border color based on rarity
        border_color = self.rarity_colors.get(card.rarity, (150, 150, 150))
        
        # Adjust color if selected or selectable
        if selected:
            border_color = (255, 215, 0)  # Gold for selected
        elif selectable:
            # Make the border pulse
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            if pulse > 0.5:
                pulse = 1.0 - pulse
            pulse = pulse * 2.0  # Scale to [0, 1]
            
            # Interpolate between normal and highlighted color
            r = int(border_color[0] * (1 - pulse) + 255 * pulse)
            g = int(border_color[1] * (1 - pulse) + 255 * pulse)
            b = int(border_color[2] * (1 - pulse) + 255 * pulse)
            border_color = (r, g, b)
        
        # Draw card background
        pygame.draw.rect(surface, self.bg_color, card_rect, border_radius=5)
        
        # Draw border
        border_width = 3 if selected or selectable else 2
        pygame.draw.rect(surface, border_color, card_rect, width=border_width, border_radius=5)
        
        # Draw card image if available
        if card.id in self.card_images:
            image = self.card_images[card.id]
            surface.blit(image, (card_rect.left + 5, card_rect.top + 25))
        elif self.default_image:
            surface.blit(self.default_image, (card_rect.left + 5, card_rect.top + 25))
        else:
            # Draw a placeholder
            img_rect = pygame.Rect(card_rect.left + 5, card_rect.top + 25, 
                                card_rect.width - 10, card_rect.height - 70)
            pygame.draw.rect(surface, (60, 60, 60), img_rect, border_radius=3)
            
            # Draw card name as placeholder
            name_surf, name_rect = self.name_font.render(card.name, (200, 200, 200))
            name_rect.center = img_rect.center
            surface.blit(name_surf, name_rect)
        
        # Draw card name
        name_surf, name_rect = self.name_font.render(card.name, (255, 255, 255))
        name_rect.midtop = (card_rect.centerx, card_rect.top + 5)
        surface.blit(name_surf, name_rect)
        
        # Draw card stats
        # Cost (top left)
        cost_bg = pygame.Rect(card_rect.left + 5, card_rect.top + 5, 20, 20)
        pygame.draw.rect(surface, (50, 50, 150), cost_bg, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 200), cost_bg, width=1, border_radius=10)
        
        cost_surf, cost_rect = self.stats_font.render(str(card.cost), (255, 255, 255))
        cost_rect.center = cost_bg.center
        surface.blit(cost_surf, cost_rect)
        
        # Attack (bottom left)
        attack_bg = pygame.Rect(card_rect.left + 5, card_rect.bottom - 25, 20, 20)
        pygame.draw.rect(surface, (150, 50, 50), attack_bg, border_radius=10)
        pygame.draw.rect(surface, (200, 100, 100), attack_bg, width=1, border_radius=10)
        
        attack_surf, attack_rect = self.stats_font.render(str(card.attack), (255, 255, 255))
        attack_rect.center = attack_bg.center
        surface.blit(attack_surf, attack_rect)
        
        # Health (bottom right)
        health_bg = pygame.Rect(card_rect.right - 25, card_rect.bottom - 25, 20, 20)
        pygame.draw.rect(surface, (50, 150, 50), health_bg, border_radius=10)
        pygame.draw.rect(surface, (100, 200, 100), health_bg, width=1, border_radius=10)
        
        health_surf, health_rect = self.stats_font.render(str(card.hp), (255, 255, 255))
        health_rect.center = health_bg.center
        surface.blit(health_surf, health_rect)
        
        # Draw rarity indicator
        rarity_color = self.rarity_colors.get(card.rarity, (150, 150, 150))
        pygame.draw.rect(surface, rarity_color, (card_rect.right - 25, card_rect.top + 5, 20, 5), border_radius=2)
        
        return card_rect