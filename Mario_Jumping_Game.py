import pygame
import random
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()  # For sound effects

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Jumper")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 215, 0)

# Clock for controlling game speed
clock = pygame.time.Clock()

# Load images
# Make sure mario.png exists in the same directory as your script
current_path = os.path.dirname(__file__)  # Get the directory where the script is located

# Load Mario sprite or create a fallback
try:
    mario_img = pygame.image.load(os.path.join(current_path, "mario.png"))
    mario_img = pygame.transform.scale(mario_img, (40, 60))
except pygame.error:
    print("Warning: mario.png not found! Using colored rectangle instead.")
    mario_img = None

# Try to load other game assets, use fallbacks if not found
try:
    pipe_img = pygame.image.load(os.path.join(current_path, "pipe.png"))
except pygame.error:
    pipe_img = None

try:
    coin_img = pygame.image.load(os.path.join(current_path, "coin.png"))
    coin_img = pygame.transform.scale(coin_img, (25, 25))
except pygame.error:
    coin_img = None

# Try to load sound effects with MP3 format
try:
    jump_sound = pygame.mixer.Sound(os.path.join(current_path, "jump.mp3"))
except pygame.error:
    jump_sound = None

try:
    coin_sound = pygame.mixer.Sound(os.path.join(current_path, "coin.mp3"))
except pygame.error:
    coin_sound = None

try:
    game_over_sound = pygame.mixer.Sound(os.path.join(current_path, "gameover.mp3"))
except pygame.error:
    game_over_sound = None

# Mario class
class Mario:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = 100
        self.y = SCREEN_HEIGHT - self.height - 40  # Above ground level
        self.jump_velocity = 0
        self.is_jumping = False
        self.gravity = 1
        self.jump_height = 15
        self.color = RED
        self.animation_count = 0

    def draw(self):
        if mario_img:
            screen.blit(mario_img, (self.x, self.y))
        else:
            # Fallback to original rectangle Mario
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLUE, (self.x + 25, self.y + 10, 10, 5))  # Eye
            pygame.draw.rect(screen, BROWN, (self.x + 10, self.y + 30, 20, 5))  # Mustache

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = -self.jump_height
            # Play jump sound if available
            if jump_sound:
                jump_sound.play()

    def update(self):
        # Apply gravity
        if self.is_jumping:
            self.y += self.jump_velocity
            self.jump_velocity += self.gravity
            
            # Check if landed
            if self.y >= SCREEN_HEIGHT - self.height - 40:
                self.y = SCREEN_HEIGHT - self.height - 40
                self.is_jumping = False
                self.jump_velocity = 0

# Obstacle class
class Obstacle:
    def __init__(self, x):
        self.width = 50
        self.height = random.randint(50, 90)
        self.x = x
        self.y = SCREEN_HEIGHT - self.height - 40  # Above ground level
        self.velocity = 5
        self.color = GREEN

    def draw(self):
        if pipe_img:
            scaled_pipe = pygame.transform.scale(pipe_img, (self.width, self.height))
            screen.blit(scaled_pipe, (self.x, self.y))
        else:
            # Fallback to pipe-like rectangle
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            # Pipe top
            pygame.draw.rect(screen, self.color, (self.x - 5, self.y, self.width + 10, 10))

    def update(self):
        self.x -= self.velocity
        
    def off_screen(self):
        return self.x < -self.width

# Coin class
class Coin:
    def __init__(self, x):
        self.width = 25
        self.height = 25
        self.x = x
        # Position coins in the air at different heights
        self.y = random.randint(SCREEN_HEIGHT - 150, SCREEN_HEIGHT - 80)
        self.velocity = 5
        self.color = YELLOW
        self.collected = False
        self.animation_frame = 0

    def draw(self):
        if not self.collected:
            if coin_img:
                screen.blit(coin_img, (self.x, self.y))
            else:
                # Fallback to simple circle coin
                pygame.draw.circle(screen, self.color, (self.x + self.width//2, self.y + self.height//2), self.width//2)

    def update(self):
        self.x -= self.velocity
        # Simple animation
        self.animation_frame = (self.animation_frame + 0.1) % 4
        
    def off_screen(self):
        return self.x < -self.width

# Game setup
mario = Mario()
obstacles = []
coins = []
obstacle_timer = 0
coin_timer = 0
obstacle_frequency = 120  # Frames between obstacles
coin_frequency = 180      # Frames between coins
score = 0
high_score = 0
game_over = False
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Game loop
sound_played = False
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                mario.jump()
            if event.key == pygame.K_r and game_over:
                # Reset game
                mario = Mario()
                obstacles = []
                coins = []
                obstacle_timer = 0
                coin_timer = 0
                if score > high_score:
                    high_score = score
                score = 0
                game_over = False
                sound_played = False

    if not game_over:
        # Update Mario
        mario.update()
        
        # Spawn obstacles
        obstacle_timer += 1
        if obstacle_timer >= obstacle_frequency:
            obstacles.append(Obstacle(SCREEN_WIDTH))
            obstacle_timer = 0
            # Increase difficulty
            obstacle_frequency = max(60, obstacle_frequency - 1)
        
        # Spawn coins
        coin_timer += 1
        if coin_timer >= coin_frequency:
            coins.append(Coin(SCREEN_WIDTH))
            coin_timer = 0
        
        # Update obstacles
        for obstacle in obstacles[:]:
            obstacle.update()
            # Check collision
            if (mario.x < obstacle.x + obstacle.width and 
                mario.x + mario.width > obstacle.x and 
                mario.y < obstacle.y + obstacle.height and 
                mario.y + mario.height > obstacle.y):
                game_over = True
                if game_over_sound and not sound_played:
                    game_over_sound.play()
                    sound_played = True
            
            # Remove off-screen obstacles
            if obstacle.off_screen():
                obstacles.remove(obstacle)
                score += 1
        
        # Update coins
        for coin in coins[:]:
            coin.update()
            # Check collision with Mario
            if (not coin.collected and
                mario.x < coin.x + coin.width and 
                mario.x + mario.width > coin.x and 
                mario.y < coin.y + coin.height and 
                mario.y + mario.height > coin.y):
                coin.collected = True
                score += 5  # Bonus points for coins
                if coin_sound:
                    coin_sound.play()
            
            # Remove off-screen or collected coins
            if coin.off_screen() or coin.collected:
                coins.remove(coin)
    
    # Draw

    screen.fill(SKY_BLUE)
    
    # Draw ground
    pygame.draw.rect(screen, BROWN, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
    
    # Draw game elements
    for coin in coins:
        coin.draw()
    
    for obstacle in obstacles:
        obstacle.draw()
    
    mario.draw()
    
    # Draw score and high score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    high_score_text = small_font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(high_score_text, (10, 40))
    
    # Draw game over
    if game_over:
        game_over_text = font.render("Game Over! Press R to restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 18))
    
    # Draw instructions at the beginning
    if len(obstacles) == 0 and not game_over:
        instructions = small_font.render("Press SPACE to jump over obstacles and collect coins!", True, WHITE)
        screen.blit(instructions, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
    
    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

pygame.quit()


