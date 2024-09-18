from settings import *

import math
import time
import threading
import random
import os
import csv

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from collections import deque

class Sigma(pygame.sprite.Sprite):
    def __init__(self, file, groups):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = 'down', 0
        self.isThinking = False
        self.image = pygame.image.load(join('images', 'sigma', 'down', '0.png')).convert_alpha()

         # Load positions from the CSV file
        script_dir = os.path.dirname(__file__)
        self.csv_file_path = os.path.join(script_dir, file)

        self.current_room = 0
        self.sigma_pos = [1,1]
        self.rect = self.image.get_frect(center=(self.sigma_pos[0] * TILE_SIZE + 32 , self.sigma_pos[0] * TILE_SIZE))

        self.read_sigma_positions_from_csv(self.csv_file_path)

        
        # Movement
        self.direction = pygame.Vector2()
        self.speed = 200
        self.is_moving = False
        
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

    def read_sigma_positions_from_csv(self, file_path):
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) == 1:
                    self.current_room = int(row[0])
                if len(row) == 2:
                    try:
                        x_pos = int(row[0])
                        y_pos = int(row[1])
                        self.sigma_pos = [x_pos, y_pos]
                        # Update the rect's position based on the read coordinates
                        self.rect.center = [x_pos * TILE_SIZE + 32, y_pos * TILE_SIZE]
                    except ValueError:
                        print(f"Invalid data in CSV: {row}")


    def write_sigma_position_to_file(self):
        # Overwrite the file with the current position
        pos_string = f"{self.sigma_pos[0]},{self.sigma_pos[1]}"
        with open(self.csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.sigma_pos)
            writer.writerow(str(self.current_room))

    def find_path_between_rooms(self, current_room, target_room, exits):
        # Initialize the queue with the starting room
        queue = deque([(current_room, [current_room])])
        # Initialize a set to keep track of visited rooms
        visited = set()
        
        while queue:
            room, path = queue.popleft()
            
            # If the target room is reached, return the path
            if room == target_room:
                return path
            
            # Mark the room as visited
            visited.add(room)
            
            # Check all possible exits from the current room
            for next_room in exits.get(room, {}):
                if next_room not in visited:
                    # Append the new room and path to the queue
                    queue.append((next_room, path + [next_room]))
        
        # Return an empty list if no path is found
        return []

    def get_directions_from_path(self, path):
        directions = []
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
    
        return directions 

    def create_directions_to_point(self, rooms, exits, target_room, target_pos):
        if not self.is_moving:
            directions = []
            c_pos = self.sigma_pos
            c_room = self.current_room
            if c_room != target_room:
                room_path = self.find_path_between_rooms(self.current_room, target_room, exits)
                print(room_path)
                for i in range(len(room_path) - 1):
                    room = room_path[i]  
                    next_room = room_path[i + 1]

                    end_pos = exits[room][next_room]
                    
                    out_pos = exits[next_room][room]
                    print("i am:")
                    print(c_pos)
                    print("i go out:")
                    print(end_pos)
                    print("i come out:")
                    print(out_pos)

                    gridForPath = Grid(matrix=rooms[c_room])

                    start = gridForPath.node(c_pos[0] , c_pos[1] )
                    end = gridForPath.node(end_pos[0], end_pos[1])
                    finder = AStarFinder()
                    path, runs = finder.find_path(start, end, gridForPath)

                    c_pos = out_pos
                    c_room = next_room
                    room_directions = self.get_directions_from_path(path)
                    directions.extend(room_directions)
                    directions.append(f"E{c_room},{c_pos[0]},{c_pos[1]}")
                
           
            

            gridForPath = Grid(matrix=rooms[c_room])
            start = gridForPath.node(c_pos[0] , c_pos[1] )
            end = gridForPath.node(target_pos[0], target_pos[1])

            finder = AStarFinder()
            path, runs = finder.find_path(start, end, gridForPath)
            room_directions = self.get_directions_from_path(path)
            directions.extend(room_directions)

            self.directions_queue.extend(directions)

    def move(self, dt, grid):
        # If not currently moving and there's a queued direction, set a new target
        if not self.is_moving and self.directions_queue:
            move = self.directions_queue.pop(0)
            if move.startswith("E"):
                room_data = move[1:].split(',')
                self.current_room = int(room_data[0])  # Room number
                x_pos, y_pos = map(int, room_data[1:])  # Coordinates
                self.rect.center = [x_pos * TILE_SIZE + 32, y_pos * TILE_SIZE]
                self.sigma_pos = [x_pos, y_pos]

            else:
                direction_map = {
                    'UP': pygame.Vector2(0, -1),
                    'DOWN': pygame.Vector2(0, 1),
                    'LEFT': pygame.Vector2(-1, 0),
                    'RIGHT': pygame.Vector2(1, 0),
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
            self.write_sigma_position_to_file()

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
        self.create_directions_to_point(grid,  rand_pos)
        print("i want to got too position ", rand_pos)
        self.isThinking = False

    def update(self, dt, grid):

        current_time = time.time()

        # Check if 10 seconds have passed since the last print
        if current_time - self.last_print_time >= 30:
            print(current_time)
            # Update the last print time
            self.last_print_time = current_time


        if not self.isThinking and not self.directions_queue and False:
            self.isThinking = True
            x = threading.Thread(target=self.think, daemon = True ,args=(random.randint(8,10), grid,))
            x.start()
            
        self.move(dt, grid)
        self.animate(dt)