from settings import *
import random
import math
from sigma import Sigma
from pytmx.util_pygame import load_pygame
from sprites import Sprite

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT - 128))
        pygame.display.set_caption("WHat is LLAMA")
        self.clock = pygame.time.Clock()

        # Zoom
        self.zoom_level = -12  # Start with normal size (100% zoom)
        self.zoom_increment = 1  # Amount to zoom in or out per key press
        self.max_zoom_level = 12  # Define maximum zoom level
        self.min_zoom_level = -16  # Define minimum zoom level to prevent excessive zoom out


        self.running = True

        self.all_sprites = pygame.sprite.Group()
        self.tile_border_enabled = False
        self.setup()
        self.sigma = Sigma((96,64), self.all_sprites)

        self.sigma2 = Sigma((96,256), self.all_sprites)
        self.world_surface = pygame.Surface((WINDOW_WIDTH , WINDOW_HEIGHT))

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

    def handle_zoom(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:  # Zoom in
            self.zoom_level = min(self.max_zoom_level, self.zoom_level + self.zoom_increment)
        elif keys[pygame.K_MINUS]:  # Zoom out
            self.zoom_level = max(self.min_zoom_level, self.zoom_level - self.zoom_increment)

    def get_directions_from_positions(self, current_pos, target_pos):
        directions = []
        print(current_pos)
        print(target_pos)
        
        # Calculate the difference in grid coordinates
        dx = math.ceil(target_pos[0] - current_pos[0]/ 64 )
        dy = math.ceil(target_pos[1] - current_pos[1] / 64 )
        print(dx)
        print(dy)
        # Determine horizontal directions
        if dx > 0:
            directions.extend(['RIGHT'] * dx)
        elif dx < 0:
            directions.extend(['LEFT'] * abs(dx))
        # Determine vertical directions

        if dy > 0:
            directions.extend(['DOWN'] * dy)
        elif dy < 0:
            directions.extend(['UP'] * abs(dy))

        # Shuffle directions for randomness (optional)
        random.shuffle(directions)

        return directions

    def run(self):
        while self.running:
            
            #dt
            dt = self.clock.tick() / 1000

            #event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_zoom()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_t]:
                target_pos = self.target_pos = (3, 11)
                current_pos = self.sigma.rect.center
                directions = self.get_directions_from_positions(current_pos, target_pos)
                self.sigma.set_directions(directions)
                

            if keys[pygame.K_o]:
                target_pos = self.target_pos = (7, 6)
                current_pos = self.sigma2.rect.center
                directions = self.get_directions_from_positions(current_pos, target_pos)
                self.sigma2.set_directions(directions)

            if keys[pygame.K_r]:
                target_pos = self.target_pos = (random.randint(3, WINDOW_WIDTH/64)-2, random.randint(3,  WINDOW_HEIGHT/64 )-2)
                current_pos = self.sigma.rect.center
                directions = self.get_directions_from_positions(current_pos, target_pos)
                self.sigma.set_directions(directions)

                target_pos2 = self.target_pos = (random.randint(3, WINDOW_WIDTH/64)-2, random.randint(3, WINDOW_HEIGHT/64)-2)
                current_pos2 = self.sigma2.rect.center
                directions = self.get_directions_from_positions(current_pos2, target_pos2)
                self.sigma2.set_directions(directions)


            #updatet
            self.all_sprites.update(dt)

            #draw
            self.world_surface.fill('black')
            self.all_sprites.draw(self.world_surface)
            
            #zoom
            scaled_width = int(WINDOW_WIDTH + 16 * self.zoom_level)
            scaled_height = int(WINDOW_HEIGHT + 16 * self.zoom_level)
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