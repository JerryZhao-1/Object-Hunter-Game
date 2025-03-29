"""
Pygame Window Manager - Replaces OpenCV window system
"""
import pygame
import numpy as np
import cv2
import time
import sys
import os

class PygameWindow:
    """Pygame-based window manager"""
    
    def __init__(self, window_name, width=1280, height=720):
        """Initialize Pygame window
        
        Args:
            window_name: Window title
            width: Window width
            height: Window height
        """
        self.window_name = window_name
        self.width = width
        self.height = height
        self.created = False
        self.screen = None
        self.clock = None
        self.mouse_callback_fn = None
        self.mouse_move_callback_fn = None  # Add mouse move callback
        self.last_key = -1  # Store last key pressed
        self.font = None    # Font property
    
    def _init_font(self):
        """Initialize font"""
        try:
            # Use default pygame font
            self.font = pygame.font.Font(None, 36)
        except Exception as e:
            print(f"Font initialization error: {e}")
            self.font = None
    
    def create(self):
        """Create Pygame window
        
        Returns:
            bool: Success status
        """
        try:
            # Initialize Pygame
            pygame.init()
            
            # Initialize audio system
            pygame.mixer.init()
            
            # Create window
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption(self.window_name)
            
            # Initialize clock
            self.clock = pygame.time.Clock()
            
            # Initialize font
            self._init_font()
            
            # Create initial frame
            self.screen.fill((40, 40, 40))  # Dark gray background
            
            # Show "Loading" message
            if self.font:
                text = self.font.render("Loading...", True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.width//2, self.height//2))
                self.screen.blit(text, text_rect)
                pygame.display.flip()
            
            self.created = True
            return True
            
        except Exception as e:
            print(f"Failed to create Pygame window: {e}")
            self.created = False
            return False
    
    def set_mouse_callback(self, callback_fn):
        """Set mouse click callback function
        
        Args:
            callback_fn: Callback function with format callback(event, x, y, flags, param)
            
        Returns:
            bool: Success status
        """
        self.mouse_callback_fn = callback_fn
        return True
    
    def set_mouse_move_callback(self, callback_fn):
        """Set mouse move callback function
        
        Args:
            callback_fn: Callback function with format callback(event, x, y, flags, param)
            
        Returns:
            bool: Success status
        """
        self.mouse_move_callback_fn = callback_fn
        return True
    
    def _convert_cv_to_pygame(self, cv_frame):
        """Convert OpenCV image to Pygame format
        
        Args:
            cv_frame: OpenCV image
        
        Returns:
            pygame.Surface: Pygame image
        """
        # Convert BGR to RGB
        cv_frame_rgb = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2RGB)
        
        # Create pygame surface
        pygame_frame = pygame.surfarray.make_surface(cv_frame_rgb.swapaxes(0, 1))
        
        return pygame_frame
    
    def show(self, frame):
        """Display frame
        
        Args:
            frame: OpenCV image to display
            
        Returns:
            bool: Success status
        """
        if not self.created:
            if not self.create():
                return False
        
        try:
            # Convert OpenCV image to Pygame image
            pygame_frame = self._convert_cv_to_pygame(frame)
            
            # Display image
            self.screen.blit(pygame_frame, (0, 0))
            pygame.display.flip()
            
            # Process events
            self._process_events()
            
            # Control frame rate
            self.clock.tick(30)
            
            return True
        except Exception as e:
            print(f"Failed to display frame: {e}")
            return False
    
    def _process_events(self):
        """Process Pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.destroy()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                # Store key pressed
                if event.key == pygame.K_ESCAPE:
                    self.last_key = 27  # ESC key
                else:
                    self.last_key = event.key
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Call mouse callback function
                x, y = event.pos
                if self.mouse_callback_fn:
                    self.mouse_callback_fn(cv2.EVENT_LBUTTONDOWN, x, y, 0, None)
                # Also handle menu input if needed
                if hasattr(self, 'game') and self.game:
                    try:
                        self.game.handle_menu_input(cv2.EVENT_LBUTTONDOWN, x, y, 0, None)
                    except Exception as e:
                        print(f"Error in menu input handler: {e}")
            
            elif event.type == pygame.MOUSEMOTION:
                # Call mouse move callback function
                x, y = event.pos
                if self.mouse_move_callback_fn:
                    self.mouse_move_callback_fn(cv2.EVENT_MOUSEMOVE, x, y, 0, None)
                # Also handle menu hover if needed
                if hasattr(self, 'game') and self.game:
                    try:
                        self.game.handle_mouse_move(cv2.EVENT_MOUSEMOVE, x, y, 0, None)
                    except Exception as e:
                        print(f"Error in mouse move handler: {e}")
    
    def wait_key(self, delay=1):
        """Wait for keyboard input
        
        Args:
            delay: Wait time (milliseconds)
            
        Returns:
            int: Key code
        """
        try:
            # Process events
            self._process_events()
            
            # Pause for specified time
            pygame.time.wait(delay)
            
            # Return and reset last key
            key = self.last_key
            self.last_key = -1
            return key
        except Exception as e:
            print(f"Failed to wait for key input: {e}")
            return -1
    
    def destroy(self):
        """Destroy window"""
        try:
            if self.created:
                pygame.quit()
                self.created = False
        except Exception as e:
            print(f"Failed to destroy window: {e}")
    
    def __del__(self):
        """Destructor, ensure resources are released"""
        self.destroy()

def create_pygame_window(window_name, width=1280, height=720):
    """Create Pygame window (factory function)
    
    Args:
        window_name: Window name
        width: Window width
        height: Window height
        
    Returns:
        PygameWindow: Window manager instance
    """
    manager = PygameWindow(window_name, width, height)
    manager.create()
    return manager
