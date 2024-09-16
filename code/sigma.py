from settings import *

class Sigma(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = 'down', 0
        self.image = pygame.image.load(join('images', 'sigma', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_frect(center=pos)

        # Movement
        self.direction = pygame.Vector2()
        self.speed = 200
        self.is_moving = False
        self.target_pos = self.rect.center
        self.directions_queue = []  # Queue to handle multiple movements

    def load_images(self):
        self.frames = {'left': [], 'right': [], 'up': [], 'down': []}

        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('images', 'sigma', state)):
                if file_names:
                    for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    def set_directions(self, directions):
        if not self.is_moving:
            # Add directions to the queue
            self.directions_queue.extend(directions)
            self.update_target_position()
        return True
    def update_target_position(self):
        if self.directions_queue:
            move = self.directions_queue.pop(0)
            if move == 'UP':
                self.direction = pygame.Vector2(0, -1)
            elif move == 'DOWN':
                self.direction = pygame.Vector2(0, 1)
            elif move == 'LEFT':
                self.direction = pygame.Vector2(-1, 0)
            elif move == 'RIGHT':
                self.direction = pygame.Vector2(1, 0)
            
            # Set target position and start moving
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
                self.target_pos = self.rect.center + self.direction * TILE_SIZE # Move one tile (64 pixels)
                self.is_moving = True

    def move(self, dt):
        if self.is_moving:
            # Move towards the target position smoothly
            distance = self.target_pos - pygame.Vector2(self.rect.center)
            if distance.length() > self.speed * dt:
                self.rect.center += self.direction * self.speed * dt
            else:
                # Snap to target and stop moving
                self.rect.center = self.target_pos
                self.is_moving = False
                # Update target position if there are more directions
                self.update_target_position()

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

    def update(self, dt):
        self.move(dt)
        self.animate(dt)