import matplotlib.pyplot as plt
import os
import pygame
import random
import math
import sys
import collections
import argparse


# Parse command-line arguments
parser = argparse.ArgumentParser(description="Ant Colonies Simulation")
parser.add_argument('--num_ants', type=int, default=80, help='Number of ants (default: 80)')
parser.add_argument('--num_food', type=int, default=20, help='Number of food items (default: 20)')
parser.add_argument('--output_mode', choices=['display', 'files', 'dummy'], default='dummy',
                    help='Output mode: "display" for window, "files" for image files, or "dummy" for no output (default: dummy)')
parser.add_argument('--stats', action='store_true', default=False,
                    help='Save detailed statistics to stats.txt file (default: False)')
parser.add_argument('--no_stop_on_divergence', action='store_true', default=False,
                    help='Continue simulation even if colonies diverge in food preference')
args = parser.parse_args()

# Environment setup for Pygame
if args.output_mode in ['dummy', 'files']:
    os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Use dummy by default for headless runs; can be overridden

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600

NUM_ANTS = args.num_ants
NUM_FOOD = args.num_food

# Set up screen based on output mode
if args.output_mode == 'display':
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ant Colonies Simulation")
    use_display = True
    use_dummy = False
    use_files = False
elif args.output_mode == 'dummy':
    screen = pygame.Surface((WIDTH, HEIGHT))
    use_display = False
    use_dummy = True
    use_files = False
else:  # files mode
    screen = pygame.Surface((WIDTH, HEIGHT))
    use_display = False
    use_dummy = False
    use_files = True

# Colors as constants
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_ORANGE = (254, 183, 42)

# Simulation constants
ANT_RADIUS = 7
FOOD_RADIUS = 9
VISION_RADIUS = 50
COLONY_RADIUS = 30
ANT_SPEED = 10
INITIAL_LIFE = 100
LEARNING_RATE = 0.1
MAX_STEPS = 500000
FRAME_INTERVAL = 100  # Save every 100 steps in 'files' mode

# Colony positions
COLONY_A_POS = (100, 100)
COLONY_B_POS = (WIDTH - 100, HEIGHT - 100)

# Food namedtuple
Food = collections.namedtuple('Food', ['x', 'y', 'color'])

class Colony:
    def __init__(self, pos, color, capacity, initial_preference=0.5):
        self.pos = pos
        self.color = color
        self.capacity = capacity
        self.food_preference = initial_preference
        self.food_preference_stats = []
        self.ants = []
        self.is_alive = capacity > 0

    def spawn_ant(self, food_preference=None):
        """Spawn a new ant if under capacity."""
        if len(self.ants) >= self.capacity:
            return
        if food_preference is None:
            food_preference = self.food_preference
        ant = Ant(self, food_preference)
        self.ants.append(ant)

    def remove_ant(self, ant):
        """Remove an ant from the colony."""
        if ant in self.ants:
            self.ants.remove(ant)
        if not self.ants:
            self.is_alive = False

    def refresh(self):
        """Remove dead ants and update average food preference."""
        self.ants = [ant for ant in self.ants if ant.is_alive]
        if not self.ants:
            self.is_alive = False
            return
        preferences = [ant.food_preference for ant in self.ants]
        self.food_preference = sum(preferences) / len(preferences)
        self.food_preference_stats.append(self.food_preference)

    def draw(self):
        """Draw the colony and preference bar."""
        if not self.is_alive:
            return
        pygame.draw.circle(screen, self.color, self.pos, COLONY_RADIUS)
        # Preference bar: green for green preference, orange for orange
        bar_x = self.pos[0] - 2 * COLONY_RADIUS
        bar_y = self.pos[1] - 2 * COLONY_RADIUS
        bar_width = 8
        green_height = COLONY_RADIUS * 4 * self.food_preference
        orange_height = COLONY_RADIUS * 4 * (1 - self.food_preference)
        pygame.draw.rect(screen, COLOR_GREEN, (bar_x, bar_y, bar_width, green_height))
        pygame.draw.rect(screen, COLOR_ORANGE, (bar_x, bar_y + green_height, bar_width, orange_height))

class Board:
    def __init__(self):
        self.colonies = []
        self.food_items = []  # Renamed for clarity
        self.death_count = 0
        self.death_count_stats = []
        self.step = 0

    def spawn_colony(self, pos, color, capacity):
        """Add a new colony to the board."""
        colony = Colony(pos, color, capacity)
        self.colonies.append(colony)
        return colony

    def register_death(self):
        """Increment the death counter."""
        self.death_count += 1

    def tick(self):
        """Advance the simulation step and record stats."""
        self.death_count_stats.append(self.death_count)
        self.step += 1

class Ant:
    def __init__(self, colony, food_preference=0.5):
        self.colony = colony
        self.x, self.y = colony.pos
        self.angle = random.uniform(0, 2 * math.pi)
        self.has_food = False
        self.food_color = None
        self.food_preference = max(0.0, min(1.0, food_preference))  # Clamp to [0,1]
        self.target_food = None
        self.target_ant = None
        self.life = INITIAL_LIFE
        self.is_alive = True

    def move(self):
        """Handle ant movement based on state."""
        if not self.is_alive:
            return

        if self.has_food:
            # Move back to colony at half speed
            dx = self.colony.pos[0] - self.x
            dy = self.colony.pos[1] - self.y
            dist = math.hypot(dx, dy)
            if dist < 3:  # Close enough to drop food
                self.has_food = False
                self.food_color = None
                self.angle = random.uniform(0, 2 * math.pi)
                add_food()  # Respawn food randomly
                self.colony.spawn_ant(self.food_preference + random.uniform(-LEARNING_RATE, LEARNING_RATE))
            elif dist > 0:
                self.x += (ANT_SPEED / 2) * (dx / dist)
                self.y += (ANT_SPEED / 2) * (dy / dist)
        else:
            if self.target_food:
                # Move to target food
                dx = self.target_food.x - self.x  # Use .x, .y since Food is namedtuple
                dy = self.target_food.y - self.y
                dist = math.hypot(dx, dy)
                if dist <= ANT_SPEED:
                    # Pick up food if still available
                    if self.target_food in board.food_items:
                        board.food_items.remove(self.target_food)
                        self.has_food = True
                        self.food_color = self.target_food.color
                    self.target_food = None
                else:
                    self.x += ANT_SPEED * (dx / dist)
                    self.y += ANT_SPEED * (dy / dist)
            elif self.target_ant:
                # Move to target ant
                if not self.target_ant.is_alive or not self.target_ant.has_food:
                    self.target_ant = None
                    return
                dx = self.target_ant.x - self.x
                dy = self.target_ant.y - self.y
                dist = math.hypot(dx, dy)
                if dist > ANT_SPEED:
                    self.x += ANT_SPEED * (dx / dist)
                    self.y += ANT_SPEED * (dy / dist)
            else:
                # Random walk
                self.x += ANT_SPEED * math.cos(self.angle)
                self.y += ANT_SPEED * math.sin(self.angle)

        # Wall bouncing
        if self.x <= 0 or self.x >= WIDTH:
            self.angle = math.pi - self.angle
            self.x = max(0, min(WIDTH, self.x))  # Clamp position
        if self.y <= 0 or self.y >= HEIGHT:
            self.angle = -self.angle
            self.y = max(0, min(HEIGHT, self.y))  # Clamp position

    def look_for_targets(self):
        """Search for food or enemy ants with desirable food."""
        if not self.is_alive or self.has_food or self.target_food or self.target_ant:
            return

        # Probabilistic choice of desired color
        def desired_color():
            return random.choices([COLOR_GREEN, COLOR_ORANGE], weights=[self.food_preference, 1 - self.food_preference], k=1)[0]

        # Look for food
        for food in board.food_items:
            if math.hypot(self.x - food.x, self.y - food.y) < VISION_RADIUS and food.color == desired_color():
                self.target_food = food
                break

        # If no food, look for enemy ants with food
        if not self.target_food:
            for ant in all_ants():
                if ant != self and ant.is_alive and ant.has_food and ant.colony.color != self.colony.color:
                    if math.hypot(self.x - ant.x, self.y - ant.y) < VISION_RADIUS and ant.food_color == desired_color():
                        self.target_ant = ant
                        break

    def check_collisions(self):
        """Check for collisions with enemy ants and apply damage."""
        if not self.is_alive or not self.has_food:
            return

        for ant in all_ants():
            if ant == self or not ant.is_alive or ant.colony.color == self.colony.color:
                continue
            dist = math.hypot(self.x - ant.x, self.y - ant.y)
            if dist < ANT_RADIUS * 2:
                self.life -= 1
                ant.life -= 1
                if self.life <= 0:
                    self.die()
                if ant.life <= 0:
                    ant.die()

    def die(self):
        """Handle ant death: drop food and register."""
        self.is_alive = False
        if self.has_food:
            add_food(self.x, self.y, self.food_color)
            self.has_food = False
            self.food_color = None
        board.register_death()
        self.colony.remove_ant(self)

    def draw(self):
        """Draw the ant, health bar, and carried food."""
        if not self.is_alive:
            return
        pygame.draw.circle(screen, self.colony.color, (int(self.x), int(self.y)), ANT_RADIUS)
        # Health bar
        health_width = ANT_RADIUS * 4 * (self.life / INITIAL_LIFE)
        pygame.draw.rect(screen, self.colony.color, (int(self.x) - 2 * ANT_RADIUS, int(self.y) - 2 * ANT_RADIUS, health_width, 3))
        if self.has_food:
            food_offset_x = self.x + math.cos(self.angle) * 10
            food_offset_y = self.y + math.sin(self.angle) * 10
            pygame.draw.circle(screen, self.food_color, (int(food_offset_x), int(food_offset_y)), FOOD_RADIUS)

def add_food(x=None, y=None, color=None):
    """Add a new food item at random or specified position."""
    if color is None:
        color = random.choice([COLOR_GREEN, COLOR_ORANGE])
    if x is None:
        x = random.randint(0, WIDTH)
    if y is None:
        y = random.randint(0, HEIGHT)
    board.food_items.append(Food(x, y, color))

def all_ants():
    """Generator for all ants across colonies."""
    for colony in board.colonies:
        for ant in colony.ants:
            yield ant

def wanted_state():
    """Check if colonies have diverged in preferences."""
    if len(board.colonies) < 2:
        return False
    pref_a, pref_b = board.colonies[0].food_preference, board.colonies[1].food_preference
    return (pref_a > 0.95 and pref_b < 0.05) or (pref_a < 0.05 and pref_b > 0.95)

# Initialize board
board = Board()
colony_a = board.spawn_colony(COLONY_A_POS, COLOR_RED, NUM_ANTS // 2 + NUM_ANTS % 2)  # Even split
colony_b = board.spawn_colony(COLONY_B_POS, COLOR_BLACK, NUM_ANTS // 2)

# Spawn initial ants
for colony in board.colonies:
    for _ in range(colony.capacity):
        colony.spawn_ant()

# Spawn initial food
for _ in range(NUM_FOOD):
    add_food()

# Remove stats.txt if stats is enabled, to avoid appending to an old file
stats_file_handler = None
if getattr(args, 'stats', False):
    stats_file_handler = open('stats.txt', 'w')

# Main simulation loop
running = True
while running:
    screen.fill(COLOR_WHITE)

    # Draw colonies
    for colony in board.colonies:
        colony.draw()

    # Draw food
    for food in board.food_items:
        pygame.draw.circle(screen, food.color, (food.x, food.y), FOOD_RADIUS)

    # Update ants
    for ant in list(all_ants()):  # Use list to avoid modification issues
        ant.move()
        ant.look_for_targets()
        ant.check_collisions()
        ant.draw()

    # Refresh colonies
    for colony in board.colonies:
        colony.refresh()

    # Save frame if in 'files' mode
    if use_files and board.step % FRAME_INTERVAL == 0:
        os.makedirs('frames', exist_ok=True)
        pygame.image.save(screen, f"frames/frame_{board.step:06d}.png")
        print(f"Saved frame at step {board.step}")

    # Tick and check end conditions
    board.tick()
    
    # Save stats if enabled
    if stats_file_handler and board.step % FRAME_INTERVAL == 0:
        colony_0_pref = board.colonies[0].food_preference if board.colonies[0].is_alive else 0.0
        colony_1_pref = board.colonies[1].food_preference if board.colonies[1].is_alive else 0.0
        stats_file_handler.write(f"{board.step},{colony_0_pref:.6f},{colony_1_pref:.6f}\n")
    
    stop_on_divergence = not getattr(args, 'no_stop_on_divergence', False)
    divergence = wanted_state()
    if (board.step >= MAX_STEPS or (divergence and stop_on_divergence) or not board.colonies[0].is_alive or not board.colonies[1].is_alive):
        print('Simulation ended. Exiting.')
        with open('results.txt', 'a') as out:
            out.write(f"{NUM_ANTS},{NUM_FOOD},{board.step},{int(board.colonies[0].is_alive)},{int(board.colonies[1].is_alive)}\n")
        
        # Save final frame if in 'files' mode
        if use_files:
            pygame.image.save(screen, "frames/final_frame.png")
        break

    # Handle events if in 'display' mode
    if use_display:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()

# Clean up
if stats_file_handler:
    stats_file_handler.close()
pygame.quit()

# Optional plotting (commented out)
# plt.figure()
# plt.plot(board.colonies[0].food_preference_stats, color=[c/255 for c in COLOR_RED], label='Red colony')
# plt.plot(board.colonies[1].food_preference_stats, color=[c/255 for c in COLOR_BLACK], label='Black colony')
# plt.xlabel('Step')
# plt.ylabel('Food preference')
# plt.legend()
# plt.show()

# plt.figure()
# plt.plot(board.death_count_stats, color='gray', label='Death count')
# plt.xlabel('Step')
# plt.ylabel('Death count')
# plt.legend()
# plt.show()