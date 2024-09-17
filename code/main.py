from settings import *


from sigma import Sigma
from pytmx.util_pygame import load_pygame
from sprites import Sprite


import numpy as np

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("WHat is LLAMA")
        self.clock = pygame.time.Clock()
        self.tick = 0


        self.grid = np.zeros((16,16), dtype=int)
        
        # Zoom
        self.zoom_level = -6  # Start with normal size (100% zoom)
        self.zoom_increment = 1  # Amount to zoom in or out per key press
        self.max_zoom_level = 2  # Define maximum zoom level
        self.min_zoom_level = -6 # Define minimum zoom level to prevent excessive zoom out

        self.next = True
        self.running = True

        self.all_sprites = pygame.sprite.Group()
        self.sigma_sprites = pygame.sprite.Group()

        
        self.tile_border_enabled = True

        self.players = []
        self.setup()
        

        

        self.world_surface = pygame.Surface((TILE_SIZE * 16 ,  TILE_SIZE * 16))

    def setup(self):
        map = load_pygame(join('data', 'maps', 'map.tmx'))

        for x, y, image in map.get_layer_by_name('GROUND').tiles():
            tile_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            tile_surface.blit(image, (0, 0))
            
            # Conditionally draw the border around the tile based on the flag
            if self.tile_border_enabled:
                border_color = (0, 0, 0, 255)  # Black color for the border
                border_thickness = 1  # Thickness of the border
                pygame.draw.rect(tile_surface, border_color, tile_surface.get_rect(), border_thickness)
            
            # Create the sprite using this surface
            Sprite((x * TILE_SIZE + 32, y * TILE_SIZE + 32), tile_surface, self.all_sprites)

        for x, y, image in map.get_layer_by_name('OBJECT').tiles():

            self.grid[y,x] = 1
            tile_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            tile_surface.blit(image, (0, 0))

            if self.tile_border_enabled:
                border_color = (0, 0, 0, 255)  # Black color for the border
                border_thickness = 1  # Thickness of the border
                pygame.draw.rect(tile_surface, border_color, tile_surface.get_rect(), border_thickness)
      
            # Create the sprite using this surface
            Sprite((x * TILE_SIZE + 32, y * TILE_SIZE + 32), tile_surface, self.all_sprites)


        for _ in range(100):  # Example: creating 20 Sigma objects
            sigma = Sigma([1,1] , self.all_sprites)
            self.sigma_sprites.add(sigma)


        print(self.grid)

    def handle_zoom(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:  # Zoom in
            self.zoom_level = min(self.max_zoom_level, self.zoom_level + self.zoom_increment)
        elif keys[pygame.K_MINUS]:  # Zoom out
            self.zoom_level = max(self.min_zoom_level, self.zoom_level - self.zoom_increment)



    def run(self):
        while self.running:
            
            #dt
            dt = self.clock.tick() / 1000

            #event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_zoom()

            #updatet
            self.all_sprites.update(dt, self.grid)

            #draw
            self.world_surface.fill('black')


            for sprite in self.all_sprites:
                if sprite not in self.sigma_sprites:
                    self.world_surface.blit(sprite.image, sprite.rect)

            sorted_sigma_sprites = sorted(self.sigma_sprites, key=lambda sprite: sprite.rect.y)
            for sprite in sorted_sigma_sprites:
                self.world_surface.blit(sprite.image, sprite.rect)


                
            #zoom
            scaled_width = int(TILE_SIZE * 16 + 64 * self.zoom_level)
            scaled_height = int(TILE_SIZE * 16 + 64 * self.zoom_level)
            scaled_surface = pygame.transform.smoothscale(
                self.world_surface,
                (scaled_width, scaled_height)
            )

            # Calculate the position to center the scaled surface on the screen
            scaled_rect = scaled_surface.get_rect(center=self.screen.get_rect().center)
            

            # Draw the scaled surface onto the screen
            self.screen.fill((0, 0, 0))  # Clear the screen
            self.screen.blit(scaled_surface, scaled_rect.topleft)

            pygame.display.update()
        pygame.quit()

game = Game()

game.run()