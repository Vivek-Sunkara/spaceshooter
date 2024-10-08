import pygame
import random
import math
import sys

# Initialize the pygame library9
pygame.init()

# Create a window
screen = pygame.display.set_mode((800, 533))
# Background
background = pygame.image.load("background.jpg")

# Rename the game and set the logo
pygame.display.set_caption("BLACKDEVIL")
icon = pygame.image.load("hacker.png")
pygame.display.set_icon(icon)

# Player
player_image = pygame.image.load("arcade-game.png")
playerX = 370
playerY = 480
playerX_change = 0

# Enemy
enemy_image = pygame.image.load("spaceship.png")
enemy_images = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []

# Bullet
bullet_image = pygame.image.load("bullet.png")
bulletX = 0
bulletY = 480
bulletY_change = 5  # Slow down the bullet speed
bullet_state = "ready"

def draw_player(x, y):
    screen.blit(player_image, (x, y))

def draw_enemy(x, y, i):
    screen.blit(enemy_images[i], (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bullet_image, (x + 16, y + 10))

def is_collision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + math.pow(enemyY - bulletY, 2))
    if distance < 27:  # Adjust this value as needed
        return True
    return False

def show_message(message):
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(400, 200))
    screen.blit(text, text_rect)

    yes_button = pygame.Rect(250, 300, 100, 50)
    no_button = pygame.Rect(450, 300, 100, 50)

    pygame.draw.rect(screen, (0, 255, 0), yes_button)
    pygame.draw.rect(screen, (255, 0, 0), no_button)

    yes_text = font.render("Yes", True, (0, 0, 0))
    no_text = font.render("No", True, (0, 0, 0))

    screen.blit(yes_text, (275, 310))
    screen.blit(no_text, (475, 310))

    pygame.display.update()

    return yes_button, no_button

def end_game(message):
    yes_button, no_button = show_message(message)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_button.collidepoint(event.pos):
                    start_screen()
                elif no_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

def start_screen():
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render("Press SPACEBAR to start the game", True, (255, 255, 255))
    text_rect = text.get_rect(center=(400, 250))
    
    while True:
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        screen.blit(text, text_rect)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_loop()

def game_loop():
    global playerX, playerY, playerX_change
    global bulletX, bulletY, bulletY_change, bullet_state
    global enemy_images, enemyX, enemyY, enemyX_change, enemyY_change

    playerX = 370
    playerY = 480
    playerX_change = 0

    bulletX = 0
    bulletY = 480
    bulletY_change = 5  # Slow down the bullet speed
    bullet_state = "ready"

    num_of_enemies = random.randint(2, 8)
    enemy_images = []
    enemyX = []
    enemyY = []
    enemyX_change = []
    enemyY_change = []

    for i in range(num_of_enemies):
        enemy_images.append(enemy_image)
        enemyX.append(random.randint(0, 736))
        enemyY.append(random.randint(50, 100))
        enemyX_change.append(0.3)
        enemyY_change.append(40)

    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            # Keyboard controls    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    playerX_change = -0.3
                if event.key == pygame.K_RIGHT:
                    playerX_change = 0.3
                if event.key == pygame.K_SPACE:
                    if bullet_state == "ready":
                        bulletX = playerX
                        fire_bullet(bulletX, bulletY)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0
        
        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736
        
        # Enemy movement and collision detection
        for i in range(len(enemyX) - 1, -1, -1):
            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = 0.3
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= 736:
                enemyX_change[i] = -0.3
                enemyY[i] += enemyY_change[i]

            # Check for collision
            collision = is_collision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                bulletY = 480
                bullet_state = "ready"
                enemyX.pop(i)
                enemyY.pop(i)
                enemy_images.pop(i)
                enemyX_change.pop(i)
                enemyY_change.pop(i)

        # Draw remaining enemies
        for i in range(len(enemyX)):
            draw_enemy(enemyX[i], enemyY[i], i)
        
        # Bullet movement
        if bullet_state == "fire":
            fire_bullet(bulletX, bulletY)
            bulletY -= bulletY_change
        if bulletY <= 0:
            bulletY = 480
            bullet_state = "ready"
        
        # Check for victory or loss
        if len(enemyX) == 0:
            end_game("You Have Won! Restart?")
        if playerY <= min(enemyY, default=533):
            end_game(random.choice(["Better Luck Next Time!", "Try Again!"]))

        draw_player(playerX, playerY)
        pygame.display.update()

# Start the game with the start screen
start_screen()
