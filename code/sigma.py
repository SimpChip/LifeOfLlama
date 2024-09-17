from settings import *

import math
import time
import threading
import random

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

class Sigma(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = 'down', 0
        self.isThinking = False
        self.image = pygame.image.load(join('images', 'sigma', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(pos[0] * TILE_SIZE + 32 , pos[1] * TILE_SIZE))

        # Movement
        self.direction = pygame.Vector2()
        self.speed = 200
        self.is_moving = False
        self.sigma_pos = pos
        self.directions_queue = []  # Queue to handle multiple movements


        # Initialize last print time
        self.last_print_time = time.time()
    def load_images(self):
        self.frames = {'left': [], 'right': [], 'up': [], 'down': []}

        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('images', 'sigma', state)):
                if file_names:
                    for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    def create_directions_to_point(self, grid, target_pos):
        directions = []

        gridForPath = Grid(matrix=grid , inverse=True)

        start = gridForPath.node(self.sigma_pos[0] , self.sigma_pos[1] )

        end = gridForPath.node(target_pos[0], target_pos[1])
        finder = AStarFinder()
        path, runs = finder.find_path(start, end, gridForPath)

        for i in range(1, len(path)):
            x1, y1 = path[i - 1]
            x2, y2 = path[i]
            
            if x2 > x1:
                directions.append("RIGHT")
            elif x2 < x1:
                directions.append("LEFT")
            elif y2 > y1:
                directions.append("DOWN")
            elif y2 < y1:
                directions.append("UP")

        self.directions_queue.extend(directions)

    def move(self, dt, grid):
        # If not currently moving and there's a queued direction, set a new target
        if not self.is_moving and self.directions_queue:
            move = self.directions_queue.pop(0)
            direction_map = {
                'UP': pygame.Vector2(0, -1),
                'DOWN': pygame.Vector2(0, 1),
                'LEFT': pygame.Vector2(-1, 0),
                'RIGHT': pygame.Vector2(1, 0)
            }
            self.direction = direction_map.get(move, pygame.Vector2(0, 0))
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
                self.target_pos = self.rect.center + self.direction * TILE_SIZE
                self.is_moving = True

                if move == "UP":
                    self.sigma_pos[1] -= 1
                elif move == "DOWN":
                    self.sigma_pos[1] += 1
                elif move == "LEFT":
                    self.sigma_pos[0] -= 1
                elif move == "RIGHT":
                    self.sigma_pos[0] += 1

        # If moving, move towards the target position smoothly
        if self.is_moving:
            distance = self.target_pos - pygame.Vector2(self.rect.center)
            if distance.length() > self.speed * dt:
                self.rect.center += self.direction * self.speed * dt
            else:
                # Snap to target and stop moving
                self.rect.center = self.target_pos
                self.is_moving = False
                
    def animate(self, dt):
        # get state
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        # animate
        if self.is_moving:
            self.frame_index += 5 * dt
            self.frame_index %= len(self.frames[self.state])  # Loop within the frame list
        else:
            # If not moving, keep the last frame index
            self.frame_index = 0

        # Set the current image based on the frame index
        self.image = self.frames[self.state][int(self.frame_index)]

    def think(self, sleep, grid):
        print("Start thinking")

        time.sleep(sleep)
        rand_pos = [random.randint(1,14), random.randint(1,14) ]
        while grid[rand_pos[0], rand_pos[1]] == 1:
            rand_pos = [random.randint(1,14), random.randint(1,14) ]
        self.create_directions_to_point(grid, rand_pos)
        print("i want to got too position ", rand_pos)
        self.isThinking = False

    def update(self, dt, grid):

        current_time = time.time()

        # Check if 10 seconds have passed since the last print
        if current_time - self.last_print_time >= 10:
            print("10 seconds have passed.")
            # Update the last print time
            self.last_print_time = current_time

        if not self.isThinking and not self.directions_queue:
            self.isThinking = True
            x = threading.Thread(target=self.think, daemon = True ,args=(random.randint(5,6), grid,))
            x.start()
            
        self.move(dt, grid)
        self.animate(dt)