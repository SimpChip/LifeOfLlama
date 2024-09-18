from settings import *

import math
from sigma import Sigma
from pytmx.util_pygame import load_pygame
from sprites import Sprite

import threading

from llm import Llama

import numpy as np

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("WHat is LLAMA")
        self.clock = pygame.time.Clock()
        self.tick = 0


        self.current_room_index = 0
        self.room_maps = ["map1.tmx", "map2.tmx", "map3.tmx" , "house.tmx"]
        self.rooms = []
        self.rooms_exits = {
            0: {1: [15, 4]},
            1: {0: [0, 4], 2: [15, 4]},
            2: {1: [0, 4], 3: [10,6]},
            3: {2: [4, 15]}
        }

        
        self.set_up_rooms()

        
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
        
        self.draw_room(self.room_maps[self.current_room_index])

        self.sigma = Sigma("sigma1.csv", self.all_sprites)
        self.sigma_sprites.add(self.sigma)


        self.llm = Llama(self)
        self.llm.add_sigma(self.sigma)

        self.cumulative_time = 0

        self.world_surface = pygame.Surface((TILE_SIZE * 16 ,  TILE_SIZE * 16))


    def set_up_rooms(self):
        # Load each map and prepare rooms
        for map_file in self.room_maps:
            self.set_up_room(map_file)


    def set_up_room(self, map_file):
        map = load_pygame(join('data', 'maps', map_file))
        grid = np.ones((16, 16))
        for x, y, image in map.get_layer_by_name('OBJECT').tiles():
            grid[y, x] = 0
        self.rooms.append(grid)

    def draw_room(self, map_file):
        # Clear current sprites
        self.all_sprites.empty()

        # Draw room from map file
        map = load_pygame(join('data', 'maps', map_file))
        self.draw_tiles("GROUND", map)
        self.draw_tiles("OBJECT", map)




    def draw_tiles(self, type, map):
        for x, y, image in map.get_layer_by_name(type).tiles():
            tile_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            tile_surface.blit(image, (0, 0))

            if self.tile_border_enabled:
                border_color = (0, 0, 0, 255)
                border_thickness = 1
                pygame.draw.rect(tile_surface, border_color, tile_surface.get_rect(), border_thickness)
      
            Sprite((x * TILE_SIZE + 32, y * TILE_SIZE + 32), tile_surface, self.all_sprites)

    def switch_room(self, direction):
        # Switch to the next or previous room based on direction
        if direction == "next":
            self.current_room_index = (self.current_room_index + 1) % len(self.room_maps)
        elif direction == "previous":
            self.current_room_index = (self.current_room_index - 1) % len(self.room_maps)

        # Draw the new room
        self.draw_room(self.room_maps[self.current_room_index])


    def handle_zoom(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:  # Zoom in
            self.zoom_level = min(self.max_zoom_level, self.zoom_level + self.zoom_increment)
        elif keys[pygame.K_MINUS]:  # Zoom out
            self.zoom_level = max(self.min_zoom_level, self.zoom_level - self.zoom_increment)


    def describe_room(self):
        description = ""

        description += f"You are inside a room with 16x16 tiles, that means there are 16 x-tiles and 16 y-tiles, in total there are {len(self.room_maps)} rooms."
        description += f"\nYou are currently standing on the tile {self.sigma.sigma_pos} in {self.sigma.current_room}."

        return description


    def run(self):
        while self.running:
            
            #dt (in seconds)
            dt = self.clock.tick() / 1000

            #event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        # Get the global mouse position
                        global_mouse_pos = pygame.mouse.get_pos()
                        
                        # Calculate the position to center the scaled surface on the screen
                        scaled_width = int(TILE_SIZE * 16 + 64 * self.zoom_level)
                        scaled_height = int(TILE_SIZE * 16 + 64 * self.zoom_level)
                        scaled_surface = pygame.transform.smoothscale(
                            self.world_surface,
                            (scaled_width, scaled_height)
                        )
                        scaled_rect = scaled_surface.get_rect(center=self.screen.get_rect().center)

                        # Calculate the mouse position relative to the world_surface
                        relative_x = (global_mouse_pos[0] - scaled_rect.x) * (self.world_surface.get_width() / scaled_rect.width)
                        relative_y = (global_mouse_pos[1] - scaled_rect.y) * (self.world_surface.get_height() / scaled_rect.height)
                

                        # Use relative coordinates for whatever action you want
                        self.sigma.create_directions_to_point(self.rooms, self.rooms_exits, self.current_room_index, [math.floor(relative_x/64), math.floor(relative_y/64)])

                elif event.type == pygame.KEYDOWN:        
                    if event.key == pygame.K_n:  # Press 'N' to go to the next room
                        self.switch_room("next")
                    elif event.key == pygame.K_p:  # Press 'P' to go to the previous room
                        self.switch_room("previous")
                    elif event.key == pygame.K_l: # Press 'L' to move with LLaMa
                        x = threading.Thread(target=self.llm.step, daemon = True, args=[self.describe_room()])
                        x.start()
                        #self.llm.step(self.describe_room())

            
            
            self.cumulative_time += dt
            # Check if 10 seconds have passed since the last print
            if self.cumulative_time > 15 and not self.sigma.is_moving:
                # Update the last print time
                #print(f"{'-'*15}CUMTIME OVER 15{'-'*15}")
                self.cumulative_time = 0
                x = threading.Thread(target=self.llm.step, daemon = True, args=[self.describe_room()])
                x.start()

            self.handle_zoom()

            #updatet
            self.all_sprites.update(dt, self.rooms[self.current_room_index])
            self.sigma_sprites.update(dt, self.rooms[self.current_room_index])

            #draw
            self.world_surface.fill('black')



            for sprite in self.all_sprites:
                if sprite not in self.sigma_sprites:
                    self.world_surface.blit(sprite.image, sprite.rect)

            sorted_sigma_sprites = sorted(self.sigma_sprites, key=lambda sprite: sprite.rect.y)
            for sprite in sorted_sigma_sprites:
                if sprite.current_room == self.current_room_index:
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