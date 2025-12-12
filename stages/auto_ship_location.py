"""
Auto Ship Location Stage
Ships are randomly placed automatically
"""
import random
import pygame
from networking.room_client import RoomClient
from networking.network import SHIPS_NAMES


class AutoShipLocation:
    """Automatic ship placement with random positions"""
    
    def __init__(self):
        self.states = {
            'ship_locked': False
        }
        
        self.client: RoomClient = None
        self.grid_size = 10
        self.game_grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ships_placed = False
        
        # Ship sizes: 1 tàu 5 (battleship), 1 tàu 4 (cruiser), 2 tàu 3 (destroyer), 1 tàu 2 (plane)
        self.ships = {
            'battleship': 5,
            'cruiser': 4,
            'destroyer1': 3,
            'destroyer2': 3,
            'plane': 2
        }
        
        self.background_color = (231, 231, 219)
    
    def load_client(self, client: RoomClient):
        """Load network client"""
        self.client = client
        self.place_ships_randomly()
    
    def place_ships_randomly(self):
        """Randomly place all ships on grid"""
        for ship_name, ship_size in self.ships.items():
            placed = False
            attempts = 0
            
            while not placed and attempts < 100:
                # Random position and orientation
                row = random.randint(0, self.grid_size - 1)
                col = random.randint(0, self.grid_size - 1)
                horizontal = random.choice([True, False])
                
                if self.can_place_ship(row, col, ship_size, horizontal):
                    self.place_ship(row, col, ship_size, ship_name, horizontal)
                    placed = True
                
                attempts += 1
        
        self.ships_placed = True
        print(f"[DEBUG] Ships placed randomly on grid")
    
    def can_place_ship(self, row, col, size, horizontal):
        """Check if ship can be placed at position"""
        if horizontal:
            if col + size > self.grid_size:
                return False
            for c in range(col, col + size):
                if self.game_grid[row][c] is not None:
                    return False
        else:
            if row + size > self.grid_size:
                return False
            for r in range(row, row + size):
                if self.game_grid[r][col] is not None:
                    return False
        return True
    
    def place_ship(self, row, col, size, ship_name, horizontal):
        """Place ship on grid"""
        if horizontal:
            for c in range(col, col + size):
                self.game_grid[row][c] = ship_name
        else:
            for r in range(row, row + size):
                self.game_grid[r][col] = ship_name
    
    def draw(self, window: pygame.display):
        """Draw placement screen"""
        window.fill(self.background_color)
        
        # Draw title
        font = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 24)
        text = font.render('Ships Placed Automatically!', True, (71, 95, 119))
        window.blit(text, (100, 200))
        
        # Draw status
        font2 = pygame.font.Font('assets/fonts/CascadiaCode-SemiBold.ttf', 18)
        text2 = font2.render('Waiting for opponent...', True, (71, 95, 119))
        window.blit(text2, (130, 250))
        
        pygame.display.update()
    
    def process_events(self):
        """Handle events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
        
        # Auto lock ships after placement
        if self.ships_placed and not self.states['ship_locked']:
            if self.client:
                self.client.lock_ships(self.game_grid)
                print("[DEBUG] Ships locked and sent to server")
            self.states['ship_locked'] = True
        
        return self.states
    
    def get_grid(self):
        """Return the game grid"""
        return self.game_grid
