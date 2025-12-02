import pygame
import math
import sys
import random
import json
import os

# ============================================================================
# ASSET PATHS - PASTE YOUR FILE PATHS HERE
# ============================================================================

# ===== VIDEO FILE (REQUIRED) =====
# This video will play when you first run the game (before home screen)
# Supported formats: .mp4, .avi, .mov
# Example: set the environment variable SOUND_SHOOT or SOUND_EXPLOSION instead of editing this file
INTRO_VIDEO = "story.mp4"     # <-- your intro video path or leave as fallback

# ===== AUDIO FILES (YOU HAVE 2 SOUNDS) =====
# Sound 1: When player shoots bullets
# Example: SOUND_SHOOT = "C:/Users/YourName/Sounds/bullet_shoot.wav"
# NOTE: If you paste a Windows path into these values use forward slashes
# or a raw string literal (r"C:/path/to/file.mp3") to avoid Python \u escapes
SOUND_SHOOT = "missile.mp3"           # <-- BULLET SOUND PATH or env override

# Sound 2: When enemy dies/explodes
# Example: SOUND_EXPLOSION = "C:/Users/YourName/Sounds/enemy_death.wav"
SOUND_EXPLOSION = "blast.mp3"   # <-- ENEMY DEATH SOUND PATH or env override

# ===== IMAGE FILES (OPTIONAL - Your existing images) =====
IMG_BACKGROUND = "background.jpg"
IMG_PLAYER = "arcade-game.png"
IMG_BULLET = "bullet.png"
IMG_ENEMY_NORMAL = "spaceship.png"
IMG_ENEMY_FAST = "fast_enemy.png"
IMG_ENEMY_STRONG = "strong_enemy.png"
IMG_ENEMY_BOSS = "boss.png"
IMG_ICON = "hacker.png"

# Normalize any user-provided paths (replace backslashes with forward slashes)
def _normalize_path(p):
    if not isinstance(p, str):
        return p
    # Replace escape-prone backslashes with forward slashes
    return p.replace('\\', '/').replace('\\\\', '/')

INTRO_VIDEO = _normalize_path(INTRO_VIDEO)
SOUND_SHOOT = _normalize_path(os.getenv('SOUND_SHOOT', SOUND_SHOOT))
SOUND_EXPLOSION = _normalize_path(os.getenv('SOUND_EXPLOSION', SOUND_EXPLOSION))
IMG_BACKGROUND = _normalize_path(os.getenv('IMG_BACKGROUND', IMG_BACKGROUND))
IMG_PLAYER = _normalize_path(os.getenv('IMG_PLAYER', IMG_PLAYER))
IMG_BULLET = _normalize_path(os.getenv('IMG_BULLET', IMG_BULLET))
IMG_ENEMY_NORMAL = _normalize_path(os.getenv('IMG_ENEMY_NORMAL', IMG_ENEMY_NORMAL))
IMG_ENEMY_FAST = _normalize_path(os.getenv('IMG_ENEMY_FAST', IMG_ENEMY_FAST))
IMG_ENEMY_STRONG = _normalize_path(os.getenv('IMG_ENEMY_STRONG', IMG_ENEMY_STRONG))
IMG_ENEMY_BOSS = _normalize_path(os.getenv('IMG_ENEMY_BOSS', IMG_ENEMY_BOSS))
IMG_ICON = _normalize_path(os.getenv('IMG_ICON', IMG_ICON))

# --- Font loader helper (safe fallback to system font) ---
def load_font(name, size):
    try:
        return pygame.font.Font(name, size)
    except Exception:
        return pygame.font.SysFont(None, size)

# --- Music placeholders and safe player ---
# Allow BGM paths via environment variables; normalize them
BGM_MENU = _normalize_path(os.getenv('BGM_MENU', None))
BGM_GAMEPLAY = _normalize_path(os.getenv('BGM_GAMEPLAY', None))
BGM_BOSS = _normalize_path(os.getenv('BGM_BOSS', None))

def play_music(path, volume=0.3, loops=-1):
    """Safely play background music if path is provided and file exists."""
    if not path:
        return
    try:
        path = _normalize_path(path)
        if not os.path.exists(path):
            # if path is not absolute, try treating it as a resource in working dir
            # print a message but continue without crashing
            print(f"Music file '{path}' not found; skipping music.")
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)
    except Exception as e:
        print(f"Could not play music '{path}': {e}")


# ===== NOTE =====
# Only SOUND_SHOOT and SOUND_EXPLOSION will be used
# All other sounds are disabled (game works without them)
# ============================================================================

# ---------------- Pygame Setup ----------------
pygame.init()
pygame.mixer.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 533
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BLACKDEVIL")

try:
    icon = pygame.image.load(IMG_ICON)
    pygame.display.set_icon(icon)
except:
    print(f"Icon file '{IMG_ICON}' not found - using default.")

clock = pygame.time.Clock()

# ---------------- Save System ----------------
SAVE_FILE = "blackdevil_save.json"

def save_game(level, score, lives, unlocked):
    data = {
        "level": level,
        "score": score,
        "lives": lives,
        "unlocked_levels": unlocked
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

def load_game():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def delete_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

# ---------------- Assets ----------------
def load_image_safe(path, size=None):
    """Load image with fallback to colored surface"""
    try:
        img = pygame.image.load(path)
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except:
        print(f"Image '{path}' not found - using placeholder.")
        surf = pygame.Surface(size if size else (64, 64))
        surf.fill((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
        return surf

background = load_image_safe(IMG_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
player_image = load_image_safe(IMG_PLAYER)
bullet_image = load_image_safe(IMG_BULLET)

ENEMY_WIDTH = ENEMY_HEIGHT = 64
raw_enemy_images = {
    "normal": load_image_safe(IMG_ENEMY_NORMAL, (ENEMY_WIDTH, ENEMY_HEIGHT)),
    "fast": load_image_safe(IMG_ENEMY_FAST, (ENEMY_WIDTH, ENEMY_HEIGHT)),
    "strong": load_image_safe(IMG_ENEMY_STRONG, (ENEMY_WIDTH, ENEMY_HEIGHT)),
    "boss": load_image_safe(IMG_ENEMY_BOSS, (ENEMY_WIDTH * 2, ENEMY_HEIGHT * 2))
}
enemy_images_dict = raw_enemy_images

# Power-up images with distinct colors
powerup_images = {
    "life": pygame.Surface((20, 20)),
    "fast_bullet": pygame.Surface((20, 20)),
    "shield": pygame.Surface((20, 20)),
    "multi_shot": pygame.Surface((20, 20)),
    "speed_boost": pygame.Surface((20, 20)),  # NEW
    "spread_fire": pygame.Surface((20, 20))   # NEW
}
powerup_images["life"].fill((255, 0, 0))
powerup_images["fast_bullet"].fill((0, 255, 0))
powerup_images["shield"].fill((0, 200, 255))
powerup_images["multi_shot"].fill((255, 165, 0))
powerup_images["speed_boost"].fill((255, 255, 0))     # Yellow
powerup_images["spread_fire"].fill((255, 0, 255))     # Magenta

# ---------------- Sound Setup ----------------
# Only load the 2 sounds you have
def load_sound_safe(path, volume=0.4):
    """Load sound with error handling"""
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except:
        print(f"Sound '{path}' not found.")
        return None

# Load only the 2 sounds you have
sounds = {
    'shoot': load_sound_safe(SOUND_SHOOT, 0.5),      # Bullet sound
    'explosion': load_sound_safe(SOUND_EXPLOSION, 0.6)  # Enemy death sound
}

def play_sound(sound_name):
    """Play sound effect safely - only works for 'shoot' and 'explosion'"""
    if sound_name in sounds and sounds[sound_name]:
        sounds[sound_name].play()

# ---------------- Level Configuration ----------------
LEVEL_CONFIGS = {
    1: {
        "name": "ROOKIE MISSION",
        "bg_color": (10, 10, 30),
        "enemy_shoot_chance": 0,
        "enemy_speed_mult": 1.0,
        "enemy_patterns": ["line"],
        "special": None,
        "num_enemies": 5
    },
    2: {
        "name": "WARMING UP",
        "bg_color": (20, 10, 30),
        "enemy_shoot_chance": 0.002,
        "enemy_speed_mult": 1.1,
        "enemy_patterns": ["line", "wave"],
        "special": None,
        "num_enemies": 7
    },
    3: {
        "name": "HEAT RISING",
        "bg_color": (30, 10, 30),
        "enemy_shoot_chance": 0.003,
        "enemy_speed_mult": 1.2,
        "enemy_patterns": ["line", "wave", "zigzag"],
        "special": "asteroids",
        "num_enemies": 9
    },
    4: {
        "name": "INTENSE COMBAT",
        "bg_color": (40, 10, 30),
        "enemy_shoot_chance": 0.004,
        "enemy_speed_mult": 1.3,
        "enemy_patterns": ["wave", "zigzag", "circle"],
        "special": "asteroids",
        "num_enemies": 12
    },
    5: {
        "name": "BOSS BATTLE I",
        "bg_color": (50, 0, 0),
        "enemy_shoot_chance": 0.01,
        "enemy_speed_mult": 1.0,
        "enemy_patterns": ["boss"],
        "special": "boss_minions",
        "num_enemies": 1
    },
    6: {
        "name": "DANGER ZONE",
        "bg_color": (10, 30, 30),
        "enemy_shoot_chance": 0.005,
        "enemy_speed_mult": 1.4,
        "enemy_patterns": ["circle", "spiral"],
        "special": "fast_enemies",
        "num_enemies": 10
    },
    7: {
        "name": "CHAOS REIGN",
        "bg_color": (30, 30, 10),
        "enemy_shoot_chance": 0.006,
        "enemy_speed_mult": 1.5,
        "enemy_patterns": ["spiral", "cross"],
        "special": "shield_enemies",
        "num_enemies": 13
    },
    8: {
        "name": "HELL FIRE",
        "bg_color": (50, 20, 0),
        "enemy_shoot_chance": 0.007,
        "enemy_speed_mult": 1.6,
        "enemy_patterns": ["cross", "diamond"],
        "special": "bullets_everywhere",
        "num_enemies": 15
    },
    9: {
        "name": "NIGHTMARE MODE",
        "bg_color": (40, 0, 40),
        "enemy_shoot_chance": 0.008,
        "enemy_speed_mult": 1.7,
        "enemy_patterns": ["diamond", "vortex"],
        "special": "fast_bullets",
        "num_enemies": 18
    },
    10: {
        "name": "FINAL BOSS",
        "bg_color": (60, 0, 0),
        "enemy_shoot_chance": 0.015,
        "enemy_speed_mult": 1.2,
        "enemy_patterns": ["boss"],
        "special": "ultimate_boss",
        "num_enemies": 1
    }
}

def get_level_config(level):
    # Base mapping (wrap every 10 levels)
    base_level = ((level - 1) % 10) + 1
    config = LEVEL_CONFIGS.get(base_level, LEVEL_CONFIGS[1]).copy()

    # Difficulty scaling: small incremental increases per level
    # scale increases by 5% per level (compounded)
    difficulty_scale = 1.0 + (level - 1) * 0.05

    # Increase shoot chance and speed with progression
    config["enemy_shoot_chance"] = min(0.2, config.get("enemy_shoot_chance", 0.002) * difficulty_scale)
    config["enemy_speed_mult"] = config.get("enemy_speed_mult", 1.0) * difficulty_scale

    # Increase number of enemies gradually
    base_num = config.get("num_enemies", 5)
    extra = int((level - 1) * 0.5)
    config["num_enemies"] = max(1, base_num + extra)

    # Make some levels more distinct: rotate/add patterns based on level
    patterns = list(config.get("enemy_patterns", []))
    if level >= 3 and "zigzag" not in patterns:
        patterns.append("zigzag")
    if level >= 5 and "spiral" not in patterns:
        patterns.append("spiral")
    if level >= 7 and "vortex" not in patterns:
        patterns.append("vortex")
    config["enemy_patterns"] = patterns

    # Give stronger enemies more HP on higher levels
    # We'll interpret 'special' config in init_enemies
    return config

# ---------------- Particle System ----------------
class Particle:
    def __init__(self, x, y, color, speed=None, size=3):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = speed or random.uniform(50, 200)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = size
        self.lifetime = random.uniform(0.5, 1.5)
        self.age = 0
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 200 * dt
        self.age += dt
        
    def draw(self, screen):
        alpha = max(0, 1 - self.age / self.lifetime)
        size = max(1, int(self.size * alpha))
        color = tuple(int(c * alpha) for c in self.color)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)
        
    def is_alive(self):
        return self.age < self.lifetime

particles = []

def create_explosion(x, y, color=(255, 100, 0), count=20, size=4):
    for _ in range(count):
        particles.append(Particle(x, y, color, size=size))

def create_trail(x, y, color=(100, 200, 255), count=3):
    for _ in range(count):
        particles.append(Particle(x, y, color, speed=random.uniform(20, 50), size=2))

# ---------------- Asteroid System ----------------
class Asteroid:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = -30
        self.size = random.randint(15, 35)
        self.speed = random.uniform(50, 150)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-180, 180)
        
    def update(self, dt):
        self.y += self.speed * dt
        self.rotation += self.rotation_speed * dt
        
    def draw(self, screen):
        points = []
        for i in range(8):
            angle = math.radians(self.rotation + i * 45)
            offset = random.uniform(0.8, 1.0) * self.size
            px = self.x + math.cos(angle) * offset
            py = self.y + math.sin(angle) * offset
            points.append((px, py))
        pygame.draw.polygon(screen, (100, 100, 100), points)
        pygame.draw.polygon(screen, (150, 150, 150), points, 2)
        
    def is_offscreen(self):
        return self.y > SCREEN_HEIGHT + 50

asteroids = []

# ---------------- Animation System ----------------
class Animation:
    def __init__(self, x, y, duration, anim_type="explosion"):
        self.x = x
        self.y = y
        self.duration = duration
        self.elapsed = 0
        self.type = anim_type
        self.radius = 0
        self.max_radius = 50 if anim_type == "explosion" else 30
        
    def update(self, dt):
        self.elapsed += dt
        progress = self.elapsed / self.duration
        if self.type == "explosion":
            self.radius = self.max_radius * math.sin(progress * math.pi)
        elif self.type == "powerup":
            self.radius = self.max_radius * progress
            
    def draw(self, screen):
        alpha = max(0, 1 - self.elapsed / self.duration)
        if self.type == "explosion":
            for i in range(3):
                radius = int(self.radius - i * 10)
                if radius > 0:
                    color = (int(255 * alpha), int(100 * alpha), 0)
                    pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius, 2)
        elif self.type == "powerup":
            color = (int(255 * alpha), int(255 * alpha), 0)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.radius), 2)
            
    def is_alive(self):
        return self.elapsed < self.duration

animations = []

# ---------------- Screen Shake ----------------
class ScreenShake:
    def __init__(self):
        self.duration = 0
        self.intensity = 0
        
    def start(self, duration, intensity):
        self.duration = duration
        self.intensity = intensity
        
    def update(self, dt):
        if self.duration > 0:
            self.duration -= dt
            
    def get_offset(self):
        if self.duration > 0:
            return (random.randint(-int(self.intensity), int(self.intensity)),
                    random.randint(-int(self.intensity), int(self.intensity)))
        return (0, 0)

screen_shake = ScreenShake()

# ---------------- Star Field Background ----------------
class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(20, 100)
        self.size = random.randint(1, 3)
        
    def update(self, dt):
        self.y += self.speed * dt
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, screen):
        brightness = int(255 * (self.speed / 100))
        pygame.draw.circle(screen, (brightness, brightness, brightness), 
                         (int(self.x), int(self.y)), self.size)

stars = [Star() for _ in range(100)]

# ---------------- Button Class ----------------
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.scale = 1.0
        self.glow_alpha = 0
        
    def update(self, mouse_pos, dt):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.is_hovered and not was_hovered:
            play_sound('menu_hover')
            
        if self.is_hovered:
            self.scale = min(1.1, self.scale + dt * 3)
            self.glow_alpha = min(100, self.glow_alpha + dt * 300)
        else:
            self.scale = max(1.0, self.scale - dt * 3)
            self.glow_alpha = max(0, self.glow_alpha - dt * 300)
            
    def draw(self, screen, font):
        if self.glow_alpha > 0:
            glow_surf = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.hover_color, int(self.glow_alpha)), 
                           (0, 0, self.rect.width + 20, self.rect.height + 20), border_radius=15)
            screen.blit(glow_surf, (self.rect.x - 10, self.rect.y - 10))
        
        color = self.hover_color if self.is_hovered else self.color
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_width // 2,
            self.rect.centery - scaled_height // 2,
            scaled_width, scaled_height
        )
        
        pygame.draw.rect(screen, color, scaled_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), scaled_rect, 3, border_radius=10)
        
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        screen.blit(text_surf, text_rect)
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            play_sound('menu_select')
            return True
        return False

# ---------------- Constants ----------------
PLAYER_SPEED = 200.0
PLAYER_SPEED_BOOSTED = 320.0  # NEW: Speed with boost
PLAYER_START_X = 370
PLAYER_START_Y = 480
PLAYER_INVULN_TIME = 1.5
PLAYER_MAX_HEALTH = 100  # NEW: Health system

BULLET_SPEED = 500.0
ENEMY_NORMAL_SPEED = 80.0
ENEMY_FAST_SPEED = 140.0
ENEMY_DESCEND_NORMAL = 40
ENEMY_DESCEND_STRONG = 60
ENEMY_DESCEND_BOSS = 30
ENEMY_BULLET_SPEED = 200.0

FAST_BULLET_DURATION = 5.0
SPEED_BOOST_DURATION = 8.0  # NEW
SPREAD_FIRE_DURATION = 10.0  # NEW

# ---------------- Game State ----------------
player_x = PLAYER_START_X
player_y = PLAYER_START_Y
player_dx = 0.0
player_lives = 3
player_health = PLAYER_MAX_HEALTH  # NEW
player_speed = PLAYER_SPEED  # NEW
player_invuln_timer = 0.0
player_shield = False
player_shield_timer = 0.0

bullet_x = 0.0
bullet_y = player_y
bullet_state = "ready"
bullet_speed = BULLET_SPEED
bullet_count = 1  # NEW: Number of bullets per shot

enemies = []
enemy_bullets = []
powerups = []
active_powerups = {
    "fast_bullet": 0.0, 
    "multi_shot": 0.0, 
    "shield": 0.0,
    "speed_boost": 0.0,  # NEW
    "spread_fire": 0.0,  # NEW
    "speed_debuff": 0.0  # NEW: debuff applied by enemy EMP bullets
}

score = 0
level = 1
unlocked_levels = 1
current_level_config = {}
powerups_to_drop = 0  # NEW: Track powerups to drop

font = load_font('freesandbold.ttf', 24)

# ---------------- Multi-Bullet System (NEW) ----------------
player_bullets = []  # NEW: List to track all player bullets

class Bullet:
    """Player bullet class"""
    def __init__(self, x, y, vx=0, vy=-1):
        self.x = x
        self.y = y
        self.vx = vx * bullet_speed * 0.3  # Horizontal velocity
        self.vy = vy * bullet_speed  # Vertical velocity
        self.active = True
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.y < -10 or self.x < -10 or self.x > SCREEN_WIDTH + 10:
            self.active = False
            
    def draw(self, screen):
        create_trail(self.x, self.y, (100, 200, 255), count=2)
        screen.blit(bullet_image, (self.x - 8, self.y - 8))
        
    def get_rect(self):
        return pygame.Rect(self.x - 8, self.y - 8, 16, 16)

def fire_bullets():
    """Fire bullets based on current powerup state"""
    global bullet_count
    
    play_sound('shoot')
    
    # Determine bullet pattern
    if active_powerups['spread_fire'] > 0:
        # Spread fire pattern (5 bullets in fan)
        angles = [-0.4, -0.2, 0, 0.2, 0.4]
        for angle in angles:
            vx = math.sin(angle)
            vy = -math.cos(angle)
            player_bullets.append(Bullet(player_x + 16, player_y, vx, vy))
    elif active_powerups['multi_shot'] > 0:
        # Multi-shot (3 parallel bullets)
        player_bullets.append(Bullet(player_x + 16, player_y))
        player_bullets.append(Bullet(player_x, player_y))
        player_bullets.append(Bullet(player_x + 32, player_y))
    else:
        # Single bullet
        player_bullets.append(Bullet(player_x + 16, player_y))

# ---------------- Health Bar Drawing (NEW) ----------------
def draw_health_bar(x, y, width, height, current, maximum, color=(0, 255, 0), bg_color=(100, 0, 0)):
    """Draw a health bar"""
    ratio = max(0, current / maximum)
    
    # Background
    pygame.draw.rect(screen, bg_color, (x, y, width, height))
    
    # Health bar
    pygame.draw.rect(screen, color, (x, y, int(width * ratio), height))
    
    # Border
    pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)
    
    # Health text
    health_font = load_font('freesansbold.ttf', 16)
    health_text = health_font.render(f"{int(current)}/{int(maximum)}", True, (255, 255, 255))
    screen.blit(health_text, (x + width // 2 - health_text.get_width() // 2, y + 2))

def draw_boss_health_bar(boss):
    """Draw boss health bar at top of screen"""
    bar_width = SCREEN_WIDTH - 100
    bar_height = 20
    x = 50
    y = 70
    
    draw_health_bar(x, y, bar_width, bar_height, boss['hp'], boss['max_hp'], 
                    color=(255, 0, 0), bg_color=(50, 0, 0))
    
    # Boss name
    boss_font = load_font('freesansbold.ttf', 18)
    boss_text = boss_font.render("BOSS", True, (255, 0, 0))
    screen.blit(boss_text, (x - 40, y + 2))

# ---------------- Victory Animation ----------------
def victory_animation():
    """Animate ship going up and coming back down"""
    play_sound('level_complete')
    play_sound('victory')
        
    anim_time = 0
    ship_y = player_y
    
    while anim_time < 1.0:
        dt = clock.tick(60) / 1000.0
        anim_time += dt
        
        screen.fill((0, 0, 0))
        for star in stars:
            star.update(dt)
            star.draw(screen)
        screen.blit(background, (0, 0))
        
        ship_y -= 600 * dt
        
        create_trail(player_x + 16, ship_y + 32, (255, 200, 0), count=8)
        create_trail(player_x + 16, ship_y + 32, (100, 200, 255), count=5)
        
        for p in particles[:]:
            p.update(dt)
            p.draw(screen)
            if not p.is_alive():
                particles.remove(p)
        
        glow_surface = pygame.Surface((player_image.get_width() + 40, player_image.get_height() + 40), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 200, 0, 150), 
                          (glow_surface.get_width()//2, glow_surface.get_height()//2), 60)
        screen.blit(glow_surface, (player_x - 20, ship_y - 20))
        screen.blit(player_image, (player_x, ship_y))
        
        progress = min(1.0, anim_time)
        big_font = load_font('freesansbold.ttf', 48)
        text = big_font.render("LEVEL COMPLETE!", True, (255, 255, 0))
        text_alpha = int(255 * progress)
        text.set_alpha(text_alpha)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow = big_font.render("LEVEL COMPLETE!", True, (255, 150, 0))
            glow.set_alpha(text_alpha // 2)
            screen.blit(glow, (text_rect.x + offset[0], text_rect.y + offset[1]))

        screen.blit(text, text_rect)
        pygame.display.update()
    
    pygame.time.wait(500)
    
    ship_y = SCREEN_HEIGHT + 50
    anim_time = 0
    
    while anim_time < 1.5:
        dt = clock.tick(60) / 1000.0
        anim_time += dt
        
        screen.fill((0, 0, 0))
        for star in stars:
            star.update(dt)
            star.draw(screen)
        screen.blit(background, (0, 0))
        
        target_y = PLAYER_START_Y
        ship_y += (target_y - ship_y) * 3 * dt
        
        create_trail(player_x + 16, ship_y + 32, (100, 200, 255), count=5)
        
        for p in particles[:]:
            p.update(dt)
            p.draw(screen)
            if not p.is_alive():
                particles.remove(p)
        
        glow_surface = pygame.Surface((player_image.get_width() + 30, player_image.get_height() + 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (100, 150, 255, 100), 
                          (glow_surface.get_width()//2, glow_surface.get_height()//2), 50)
        screen.blit(glow_surface, (player_x - 15, ship_y - 15))
        screen.blit(player_image, (player_x, ship_y))
        
        if anim_time > 0.7:
            next_config = get_level_config(level + 1)
            ready_font = load_font('freesansbold.ttf', 36)
            ready_text = ready_font.render(next_config["name"], True, (0, 255, 255))
            ready_alpha = int(255 * (anim_time - 0.7) / 0.8)
            ready_text.set_alpha(ready_alpha)
            ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(ready_text, ready_rect)
        
        pygame.display.update()
    
    particles.clear()

# ---------------- Player Drawing ----------------
def draw_player(x, y, invuln=False):
    if invuln and int(pygame.time.get_ticks() / 150) % 2 == 0:
        return
    
    # Shield effect
    if player_shield and player_shield_timer > 0:
        shield_surf = pygame.Surface((player_image.get_width() + 40, player_image.get_height() + 40), pygame.SRCALPHA)
        alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() / 100))
        pygame.draw.circle(shield_surf, (0, 200, 255, alpha), 
                          (shield_surf.get_width()//2, shield_surf.get_height()//2), 45, 3)
        screen.blit(shield_surf, (x - 20, y - 20))
    
    # Speed boost effect
    if active_powerups['speed_boost'] > 0:
        speed_surf = pygame.Surface((player_image.get_width() + 30, player_image.get_height() + 30), pygame.SRCALPHA)
        alpha = int(80 + 40 * math.sin(pygame.time.get_ticks() / 80))
        pygame.draw.circle(speed_surf, (255, 255, 0, alpha), 
                          (speed_surf.get_width()//2, speed_surf.get_height()//2), 40, 2)
        screen.blit(speed_surf, (x - 15, y - 15))
    
    glow_surface = pygame.Surface((player_image.get_width() + 20, player_image.get_height() + 20), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (100, 150, 255, 50), 
                      (glow_surface.get_width()//2, glow_surface.get_height()//2), 40)
    screen.blit(glow_surface, (x - 10, y - 10))
    screen.blit(player_image, (x, y))

def draw_enemy(e):
    if e['type'] == 'boss':
        glow_color = (255, 0, 0, 80)
        glow_size = 70
    elif e['type'] == 'strong':
        glow_color = (255, 165, 0, 60)
        glow_size = 40
    else:
        glow_color = (200, 200, 255, 40)
        glow_size = 35
        
    glow_surface = pygame.Surface((ENEMY_WIDTH + 30, ENEMY_HEIGHT + 30), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, glow_color, 
                      (glow_surface.get_width()//2, glow_surface.get_height()//2), glow_size)
    screen.blit(glow_surface, (e['x'] - 15, e['y'] - 15))
    screen.blit(e['img'], (e['x'], e['y']))
    
    # Health bar for strong enemies and bosses
    if e['type'] in ['strong', 'boss']:
        bar_y = e['y'] - 10
        bar_width = ENEMY_WIDTH if e['type'] != 'boss' else ENEMY_WIDTH * 2
        draw_health_bar(e['x'], bar_y, bar_width, 5, e['hp'], e['max_hp'], 
                       color=(0, 255, 0), bg_color=(255, 0, 0))

def spawn_enemy_bullet(ex, ey, vx, vy, kind="normal"):
    """Spawn an enemy bullet. kind can be 'normal' or 'emp' for special debuff bullets."""
    enemy_bullets.append({"x": ex, "y": ey, "vx": vx, "vy": vy, "kind": kind})

def is_collision(ax, ay, bx, by, radius=27):
    distance = math.hypot(ax - bx, ay - by)
    return distance < radius

def spawn_powerup(x, y):
    """Spawn a random powerup"""
    global powerups_to_drop
    
    if powerups_to_drop <= 0:
        return
        
    powerups_to_drop -= 1
    
    # Weighted random selection
    rand = random.random()
    
    # Priority to health if low
    if player_health < 50 and rand < 0.25:
        ptype = "life"
    elif player_lives < 3 and rand < 0.35:
        ptype = "life"
    elif rand < 0.45:
        ptype = "spread_fire"
    elif rand < 0.60:
        ptype = "multi_shot"
    elif rand < 0.73:
        ptype = "speed_boost"
    elif rand < 0.85:
        ptype = "fast_bullet"
    else:
        ptype = "shield"
    
    powerups.append({"type": ptype, "x": x, "y": y, "pulse": 0})

def draw_powerups(dt):
    global player_lives, bullet_speed, player_shield, player_shield_timer, player_speed, player_health
    
    for p in powerups[:]:
        p['pulse'] += dt * 5
        scale = 1 + 0.2 * math.sin(p['pulse'])
        size = int(20 * scale)
        scaled_img = pygame.transform.scale(powerup_images[p['type']], (size, size))
        offset = (20 - size) // 2
        screen.blit(scaled_img, (p['x'] + offset, p['y'] + offset))
        
        ring_radius = int(15 + 5 * math.sin(p['pulse']))
        colors = {
            "life": (255, 0, 0),
            "fast_bullet": (0, 255, 0),
            "shield": (0, 200, 255),
            "multi_shot": (255, 165, 0),
            "speed_boost": (255, 255, 0),
            "spread_fire": (255, 0, 255)
        }
        color = colors.get(p['type'], (255, 255, 255))
        pygame.draw.circle(screen, color, (int(p['x'] + 10), int(p['y'] + 10)), ring_radius, 2)
        
        p['y'] += 100 * dt
        if is_collision(p['x'] + 10, p['y'] + 10, player_x + 16, player_y + 16, 30):
            # Apply powerup effect
            if p['type'] == 'life':
                player_lives = min(5, player_lives + 1)
                player_health = min(PLAYER_MAX_HEALTH, player_health + 30)
            elif p['type'] == 'fast_bullet':
                active_powerups['fast_bullet'] = FAST_BULLET_DURATION
                bullet_speed = BULLET_SPEED * 1.8
            elif p['type'] == 'shield':
                player_shield = True
                player_shield_timer = 8.0
                active_powerups['shield'] = 8.0
            elif p['type'] == 'multi_shot':
                active_powerups['multi_shot'] = 10.0
            elif p['type'] == 'speed_boost':
                active_powerups['speed_boost'] = SPEED_BOOST_DURATION
                player_speed = PLAYER_SPEED_BOOSTED
            elif p['type'] == 'spread_fire':
                active_powerups['spread_fire'] = SPREAD_FIRE_DURATION
                
            play_sound('powerup')
            animations.append(Animation(p['x'], p['y'], 0.5, "powerup"))
            create_explosion(p['x'], p['y'], color, count=15, size=3)
            powerups.remove(p)
        elif p['y'] > SCREEN_HEIGHT:
            powerups.remove(p)

def show_score():
    """Display score, lives, health, and active powerups"""
    # Top bar background
    bar_surf = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
    bar_surf.fill((0, 0, 0, 180))
    screen.blit(bar_surf, (0, 0))
    
    # Score and Level
    info_font = load_font('freesansbold.ttf', 20)
    score_text = info_font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    
    level_text = info_font.render(f"Level: {level}", True, (255, 255, 255))
    screen.blit(level_text, (10, 30))
    
    # Lives
    lives_text = info_font.render(f"Lives: {player_lives}", True, (255, 0, 0))
    screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
    
    # Player health bar (top right)
    draw_health_bar(SCREEN_WIDTH - 220, 30, 200, 15, player_health, PLAYER_MAX_HEALTH,
                    color=(0, 255, 0), bg_color=(100, 0, 0))
    
    # Active powerups display
    active_text = ""
    if active_powerups['fast_bullet'] > 0:
        active_text += f"⚡{int(active_powerups['fast_bullet'])}s "
    if active_powerups['shield'] > 0:
        active_text += f"🛡{int(active_powerups['shield'])}s "
    if active_powerups['multi_shot'] > 0:
        active_text += f"🔥{int(active_powerups['multi_shot'])}s "
    if active_powerups['speed_boost'] > 0:
        active_text += f"💨{int(active_powerups['speed_boost'])}s "
    if active_powerups['spread_fire'] > 0:
        active_text += f"🌟{int(active_powerups['spread_fire'])}s "

    # EMP debuff indicator
    if active_powerups.get('speed_debuff', 0) > 0:
        active_text += f"⚠{int(active_powerups['speed_debuff'])}s "
    
    if active_text:
        powerup_font = load_font('freesansbold.ttf', 16)
        powerup_display = powerup_font.render(active_text, True, (255, 255, 0))
        screen.blit(powerup_display, (SCREEN_WIDTH // 2 - powerup_display.get_width() // 2, 30))
    
    # Level name
    if current_level_config:
        name_font = load_font('freesansbold.ttf', 18)
        name_text = name_font.render(current_level_config["name"], True, (0, 255, 255))
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, 12))
        screen.blit(name_text, name_rect)

def end_game(message):
    """Display game over screen"""
    global score, level, unlocked_levels, player_health, player_lives
    
    delete_save()
    
    # Fade out music and play game over sound
    pygame.mixer.music.fadeout(1000)
    play_sound('game_over')
    
    screen.fill((0, 0, 0))
    
    for star in stars:
        star.draw(screen)
    
    big_font = load_font('freesansbold.ttf', 48)
    text = big_font.render(message, True, (255, 0, 0) if "Over" in message else (0, 255, 0))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
    
    shadow = big_font.render(message, True, (0, 0, 0))
    screen.blit(shadow, (text_rect.x + 3, text_rect.y + 3))
    screen.blit(text, text_rect)
    
    score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(score_text, score_rect)
    
    hint = font.render("Press R to restart or Q to quit", True, (200, 200, 200))
    hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    screen.blit(hint, hint_rect)
    
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    level = 1
                    unlocked_levels = 1
                    score = 0
                    player_health = PLAYER_MAX_HEALTH
                    player_lives = 3
                    start_screen()
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def play_intro_video():
    """Play intro video using moviepy inside the pygame window."""
    # Resolve possible video file locations (relative to script dir, absolute, working dir)
    candidates = []
    if INTRO_VIDEO:
        candidates.append(INTRO_VIDEO)
        try:
            base = os.path.dirname(__file__)
            candidates.append(os.path.join(base, INTRO_VIDEO))
        except Exception:
            pass
        candidates.append(os.path.abspath(INTRO_VIDEO))

    video_path = None
    print("[play_intro_video] candidate paths:")
    for c in candidates:
        print("  ", c)
    for c in candidates:
        if not c:
            continue
        c = _normalize_path(c)
        exists = os.path.exists(c)
        print(f"[play_intro_video] checking: {c} exists={exists}")
        if exists:
            video_path = c
            break

    if not video_path:
        print(f"Intro video not found (tried: {candidates}). Skipping video.")
        return False

    print(f"[play_intro_video] found video_path: {video_path}")

    # Try to import moviepy
    try:
        print("[play_intro_video] attempting embedded moviepy playback (in-window with audio)")
        from moviepy.editor import VideoFileClip
    except Exception as e:
        print(f"moviepy not available or import failed: {e}")
        print("To enable embedded playback (video+audio inside the game window) run:\n  pip install moviepy imageio-ffmpeg")
        return False

    # Try quick preview first (moviepy handles audio if ffmpeg is available)
    try:
        clip = VideoFileClip(video_path)
    except Exception as e:
        import traceback
        print(f"Failed to open video with moviepy: {e}\n" + traceback.format_exc())
        return False

    try:
        try:
            # Preview is the simplest path; it may block but usually works when ffmpeg/imageio-ffmpeg are present
            print("[play_intro_video] calling clip.preview() - press ESC/SPACE to skip if supported by preview")
            clip.preview(fps=clip.fps or 24)
            clip.close()
            return True
        except Exception as preview_exc:
            print(f"moviepy.preview failed or blocked: {preview_exc}")
            # Fall back to manual playback using exported audio + iter_frames

            import tempfile, threading, traceback

            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_audio.close()
            temp_path = temp_audio.name

            export_exc = None

            def export_audio():
                nonlocal export_exc
                try:
                    if clip.audio is None:
                        # No audio track
                        return
                    # Write audio to temp file; suppress verbose logging
                    clip.audio.write_audiofile(temp_path, fps=44100, logger=None)
                except Exception as ex:
                    export_exc = ex

            export_thread = threading.Thread(target=export_audio, daemon=True)
            export_thread.start()

            # Show loading overlay while exporting audio
            loading_font = load_font('freesansbold.ttf', 28)
            while export_thread.is_alive():
                dt = clock.tick(30) / 1000.0
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        try:
                            pygame.mixer.music.stop()
                        except:
                            pass
                        pygame.quit()
                        sys.exit()

                screen.fill((0, 0, 0))
                for s in stars:
                    s.update(dt)
                    s.draw(screen)

                loading_text = loading_font.render("Loading cinematic...", True, (255, 255, 255))
                loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(loading_text, loading_rect)
                pygame.display.update()

            if export_exc:
                print(f"Audio export failed: {export_exc}\n" + traceback.format_exc())
                try:
                    os.remove(temp_path)
                except:
                    pass
                clip.close()
                return False

            # Play exported audio if present
            try:
                if os.path.exists(temp_path) and (clip.audio is not None):
                    try:
                        pygame.mixer.music.load(temp_path)
                        pygame.mixer.music.play()
                    except Exception as e:
                        print(f"Could not play exported audio via pygame: {e}")
                else:
                    # No audio - just proceed with frames
                    pass
            except Exception as e:
                print(f"Error starting audio playback: {e}")

            # Iterate frames and blit to pygame surface
            try:
                fps = int(clip.fps or 24)
                frame_gen = clip.iter_frames(fps=fps, dtype='uint8')
                for frame in frame_gen:
                    dt = clock.tick(fps) / 1000.0
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            try:
                                pygame.mixer.music.stop()
                            except:
                                pass
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                            # Skip the cinematic
                            try:
                                pygame.mixer.music.stop()
                            except:
                                pass
                            try:
                                clip.close()
                            except:
                                pass
                            try:
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                            except:
                                pass
                            return True

                    # Convert numpy frame (H x W x 3) to pygame surface
                    try:
                        surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                        surf = pygame.transform.scale(surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
                        screen.blit(surf, (0, 0))
                    except Exception as fb_err:
                        # If converting frame fails, fill black and continue
                        print(f"Frame blit error: {fb_err}")
                        screen.fill((0, 0, 0))

                    pygame.display.update()

                # Finished playback
                try:
                    pygame.mixer.music.stop()
                except:
                    pass
                try:
                    clip.close()
                except:
                    pass
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
                return True
            except Exception as frames_exc:
                import traceback
                print(f"Error during manual frame playback: {frames_exc}\n" + traceback.format_exc())
                try:
                    clip.close()
                except:
                    pass
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
                return False
    except Exception as e:
        import traceback
        print(f"Unexpected error in play_intro_video: {e}\n" + traceback.format_exc())
        try:
            clip.close()
        except:
            pass
        return False

def show_text_intro():
    """Show text-based intro story (fallback for video)"""
    story_lines = [
        "In the year 2157...",
        "The galaxy is under siege by an alien armada.",
        "You are the last hope of humanity.",
        "Pilot the legendary SPACE WARRIOR spacecraft",
        "and save the universe from total annihilation!",
        "",
        "Press any key to begin your mission..."
    ]
    
    intro_font_big = load_font('freesandbold.ttf', 36)
    intro_font = load_font('freesansbold.ttf', 24)
    
    line_delays = [1.0, 2.5, 4.0, 5.5, 7.0, 8.5, 10.0]
    
    skipped = False
    start_time = pygame.time.get_ticks() / 1000.0
    
    while not skipped:
        current_time = pygame.time.get_ticks() / 1000.0 - start_time
        dt = clock.tick(60) / 1000.0
        
        # Check for skip
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                skipped = True
        
        # Draw
        screen.fill((0, 0, 0))
        
        for star in stars:
            star.update(dt)
            star.draw(screen)
        
        # Display lines based on timing
        y_offset = 150
        for i, line in enumerate(story_lines):
            if i < len(line_delays) and current_time >= line_delays[i]:
                alpha = min(255, int((current_time - line_delays[i]) * 200))
                
                if i == 0:
                    text = intro_font_big.render(line, True, (255, 0, 0))
                else:
                    text = intro_font.render(line, True, (200, 200, 255))
                
                text.set_alpha(alpha)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 40))
                screen.blit(text, text_rect)
        
        # Auto-skip after all text shown
        if current_time > 12.0:
            skipped = True
        
        pygame.display.update()

# ---------------- Home Screen ----------------
def home_screen():
    """Main menu with cinematic feel"""
    # Globals used/modified in this menu
    global unlocked_levels, level, score, player_lives, player_health
    play_music(BGM_MENU, volume=0.25)
    
    title_font = load_font('freesansbold.ttf', 72)
    button_font = load_font('freesandbold.ttf', 28)
    
    saved_data = load_game()
    
    buttons = []
    if saved_data:
        buttons.append(Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 80, 200, 50, 
                             "RESUME GAME", (0, 200, 0), (0, 255, 0), (255, 255, 255)))
        buttons.append(Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 10, 200, 50, 
                             "NEW GAME", (200, 100, 0), (255, 150, 0), (255, 255, 255)))
        buttons.append(Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 60, 200, 50, 
                             "LEVEL MAP", (0, 100, 200), (0, 150, 255), (255, 255, 255)))
        buttons.append(Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 130, 200, 50, 
                             "EXIT", (150, 0, 0), (255, 0, 0), (255, 255, 255)))
    else:
        buttons.append(Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 40, 200, 50, 
                             "START GAME", (0, 200, 0), (0, 255, 0), (255, 255, 255)))
        buttons.append(Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 30, 200, 50, 
                             "LEVEL MAP", (0, 100, 200), (0, 150, 255), (255, 255, 255)))
        buttons.append(Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50, 
                             "EXIT", (150, 0, 0), (255, 0, 0), (255, 255, 255)))
    
    pulse = 0
    while True:
        dt = clock.tick(60) / 1000.0
        pulse += dt
        mouse_pos = pygame.mouse.get_pos()
        
        screen.fill((0, 0, 0))
        
        for star in stars:
            star.update(dt)
            star.draw(screen)
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 50, 100))
        screen.blit(overlay, (0, 0))
        
        title_scale = 1 + 0.05 * math.sin(pulse * 2)
        title_text = title_font.render("SPACE WARRIOR", True, (255, 0, 0))
        scaled_title = pygame.transform.scale(title_text, 
                                             (int(title_text.get_width() * title_scale), 
                                              int(title_text.get_height() * title_scale)))
        title_rect = scaled_title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        
        for i in range(3):
            glow = title_font.render("SPACE WARRIOR", True, (100, 0, 0))
            glow.set_alpha(50)
            glow_scaled = pygame.transform.scale(glow, 
                                                 (int(glow.get_width() * title_scale * (1 + i * 0.1)), 
                                                  int(glow.get_height() * title_scale * (1 + i * 0.1))))
            glow_rect = glow_scaled.get_rect(center=title_rect.center)
            screen.blit(glow_scaled, glow_rect)

        screen.blit(scaled_title, title_rect)
        
        for button in buttons:
            button.update(mouse_pos, dt)
            button.draw(screen, button_font)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Developer/testing shortcut: press 'U' to unlock all levels and save progress
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    max_levels = max(LEVEL_CONFIGS.keys())
                    unlocked_levels = max_levels
                    # Save the unlocked state
                    save_game(level, score, player_lives, unlocked_levels)
                    print(f"All levels unlocked (1..{max_levels})")
            
            if saved_data:
                if buttons[0].is_clicked(event):  # Resume
                    level = saved_data['level']
                    score = saved_data['score']
                    player_lives = saved_data['lives']
                    player_health = PLAYER_MAX_HEALTH
                    unlocked_levels = saved_data['unlocked_levels']
                    game_loop()
                elif buttons[1].is_clicked(event):  # New Game
                    delete_save()
                    level = 1
                    unlocked_levels = 1
                    score = 0
                    player_lives = 3
                    player_health = PLAYER_MAX_HEALTH
                    game_loop()
                elif buttons[2].is_clicked(event):  # Level Map
                    level_map_screen()
                elif buttons[3].is_clicked(event):  # Exit
                    pygame.quit()
                    sys.exit()
            else:
                if buttons[0].is_clicked(event):  # Start
                    level = 1
                    unlocked_levels = 1
                    score = 0
                    player_lives = 3
                    player_health = PLAYER_MAX_HEALTH
                    game_loop()
                elif buttons[1].is_clicked(event):  # Level Map
                    level_map_screen()
                elif buttons[2].is_clicked(event):  # Exit
                    pygame.quit()
                    sys.exit()

# ---------------- Level Map ----------------
def level_map_screen():
    global unlocked_levels, level
    
    play_music(BGM_MENU, volume=0.25)
    
    title_font = load_font('freesansbold.ttf', 48)
    button_font = load_font('freesansbold.ttf', 16)
    
    back_button = Button(20, 20, 120, 40, "BACK", (100, 0, 0), (200, 0, 0), (255, 255, 255))
    
    level_buttons = []
    cols = 5
    start_x = 100
    start_y = 150
    spacing = 120
    # Show all defined levels on the map; locked levels are shown but disabled
    max_levels = max(LEVEL_CONFIGS.keys())
    for i in range(1, max_levels + 1):
        row = (i - 1) // cols
        col = (i - 1) % cols
        x = start_x + col * spacing
        y = start_y + row * spacing
        is_boss = (i % 5 == 0)
        # Show all levels as unlocked when viewing the level map (user requested)
        locked = False
        if locked:
            color = (70, 70, 70)
            hover_color = (120, 120, 120)
            text_color = (180, 180, 180)
        else:
            color = (150, 0, 150) if is_boss else (0, 150, 0)
            hover_color = (255, 0, 255) if is_boss else (0, 255, 0)
            text_color = (255, 255, 255)

        level_buttons.append({
            'button': Button(x, y, 80, 60, f"{i}", color, hover_color, text_color),
            'level': i,
            'is_boss': is_boss,
            'config': get_level_config(i),
            'locked': locked
        })
    
    pulse = 0
    
    while True:
        dt = clock.tick(60) / 1000.0
        pulse += dt
        mouse_pos = pygame.mouse.get_pos()
        
        screen.fill((0, 0, 0))
        
        for star in stars:
            star.update(dt)
            star.draw(screen)
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 20, 40, 150))
        screen.blit(overlay, (0, 0))
        
        title_text = title_font.render("MISSION SELECT", True, (0, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        
        shadow = title_font.render("MISSION SELECT", True, (0, 0, 0))
        screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title_text, title_rect)
        
        for lb in level_buttons:
            lb['button'].update(mouse_pos, dt)
            lb['button'].draw(screen, button_font)
            
            if lb['is_boss']:
                crown_y = lb['button'].rect.y - 15 + 3 * math.sin(pulse * 3 + lb['level'])
                crown_font = load_font('freesansbold.ttf', 20)
                crown = crown_font.render("👑", True, (255, 215, 0))
                crown_rect = crown.get_rect(center=(lb['button'].rect.centerx, crown_y))
                screen.blit(crown, crown_rect)
            
            if lb['button'].is_hovered:
                name_font = load_font('freesandbold.ttf', 18)
                if lb.get('locked'):
                    name_text = name_font.render("LOCKED", True, (180, 180, 180))
                else:
                    name_text = name_font.render(lb['config']['name'], True, (255, 255, 0))
                name_rect = name_text.get_rect(center=(lb['button'].rect.centerx, lb['button'].rect.bottom + 20))
                screen.blit(name_text, name_rect)
        
        back_button.update(mouse_pos, dt)
        back_button.draw(screen, button_font)
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if back_button.is_clicked(event):
                home_screen()
            
            for lb in level_buttons:
                if lb.get('locked'):
                    continue
                if lb['button'].is_clicked(event):
                    level = lb['level']
                    game_loop()

# ---------------- Enemy Initialization ----------------
def init_enemies(lvl):
    """Initialize enemies for the current level"""
    global powerups_to_drop
    
    enemies.clear()
    config = get_level_config(lvl)
    speed_mult = config['enemy_speed_mult']
    num_enemies = config.get('num_enemies', 5 + lvl)
    
    # Calculate powerups to drop (1/3 of enemies)
    powerups_to_drop = max(1, num_enemies // 3)
    
    if lvl % 5 == 0:  # Boss level
        boss_hp = 20 + lvl * 2
        if config['special'] == 'ultimate_boss':
            boss_hp = 50 + lvl * 3
        
        enemies.append({
            'x': SCREEN_WIDTH/2 - ENEMY_WIDTH,
            'y': 50,
            'vx': ENEMY_NORMAL_SPEED/2 * speed_mult,
            'type': 'boss',
            'hp': boss_hp,
            'max_hp': boss_hp,
            'img': enemy_images_dict['boss'],
            'shoot_timer': 0
        })
        
        # Switch to boss music
        play_music(BGM_BOSS, volume=0.35)
    else:
        pattern = random.choice(config['enemy_patterns'])
        # helper to choose type per enemy with level-based chance for 'strong'
        def choose_enemy_type(i, lvl):
            if random.random() < min(0.2, lvl * 0.02):
                return 'strong'
            return 'fast' if i % 3 == 0 else 'normal'
        
        # Different spawn patterns
        if pattern == 'line':
            for i in range(num_enemies):
                etype = choose_enemy_type(i, lvl)
                x = 50 + i * (SCREEN_WIDTH - 100) / num_enemies
                y = 50
                base_speed = ENEMY_FAST_SPEED if etype == 'fast' else ENEMY_NORMAL_SPEED
                vx = base_speed * speed_mult
                if i % 2 == 0: vx = -vx
                if etype == 'fast':
                    hp = 2
                elif etype == 'strong':
                    hp = 3 + lvl // 5
                else:
                    hp = 1
                enemies.append({'x': x, 'y': y, 'vx': vx, 'type': etype, 'hp': hp, 'max_hp': hp,
                              'img': enemy_images_dict.get(etype, enemy_images_dict['normal']), 'shoot_timer': 0})
        
        elif pattern == 'wave':
            for i in range(num_enemies):
                etype = choose_enemy_type(i, lvl)
                x = 50 + i * (SCREEN_WIDTH - 100) / num_enemies
                y = 50 + 30 * math.sin(i)
                base_speed = ENEMY_FAST_SPEED if etype == 'fast' else ENEMY_NORMAL_SPEED
                vx = base_speed * speed_mult
                if i % 2 == 0: vx = -vx
                if etype == 'fast':
                    hp = 2
                elif etype == 'strong':
                    hp = 3 + lvl // 5
                else:
                    hp = 1
                enemies.append({'x': x, 'y': y, 'vx': vx, 'type': etype, 'hp': hp, 'max_hp': hp,
                              'img': enemy_images_dict.get(etype, enemy_images_dict['normal']), 'shoot_timer': 0})
        
        elif pattern == 'circle':
            for i in range(num_enemies):
                angle = (2 * math.pi / num_enemies) * i
                radius = 100
                x = SCREEN_WIDTH/2 + radius * math.cos(angle)
                y = 100 + radius * math.sin(angle)
                etype = choose_enemy_type(i, lvl)
                vx = ENEMY_NORMAL_SPEED * speed_mult
                if etype == 'fast':
                    hp = 2
                elif etype == 'strong':
                    hp = 3 + lvl // 5
                else:
                    hp = 1
                enemies.append({'x': x, 'y': y, 'vx': vx, 'type': etype, 'hp': hp, 'max_hp': hp,
                              'img': enemy_images_dict.get(etype, enemy_images_dict['normal']), 'shoot_timer': 0, 'angle': angle})
        
        elif pattern == 'zigzag':
            for i in range(num_enemies):
                etype = choose_enemy_type(i, lvl)
                x = 50 + i * (SCREEN_WIDTH - 100) / num_enemies
                y = 50 if i % 2 == 0 else 100
                base_speed = ENEMY_FAST_SPEED if etype == 'fast' else ENEMY_NORMAL_SPEED
                vx = base_speed * speed_mult
                if i % 2 == 0: vx = -vx
                if etype == 'fast':
                    hp = 2
                elif etype == 'strong':
                    hp = 3 + lvl // 5
                else:
                    hp = 1
                enemies.append({'x': x, 'y': y, 'vx': vx, 'type': etype, 'hp': hp, 'max_hp': hp,
                              'img': enemy_images_dict.get(etype, enemy_images_dict['normal']), 'shoot_timer': 0})
        
        else:  # Default pattern
            for i in range(num_enemies):
                etype = choose_enemy_type(i, lvl)
                x = 100 + i * 100
                y = 50
                vx = ENEMY_NORMAL_SPEED * speed_mult
                if i % 2 == 0: vx = -vx
                if etype == 'fast':
                    hp = 2
                elif etype == 'strong':
                    hp = 3 + lvl // 5
                else:
                    hp = 1
                enemies.append({'x': x, 'y': y, 'vx': vx, 'type': etype, 'hp': hp, 'max_hp': hp,
                              'img': enemy_images_dict.get(etype, enemy_images_dict['normal']), 'shoot_timer': 0})
        
        # Switch to gameplay music
        play_music(BGM_GAMEPLAY, volume=0.3)

# ---------------- Main Game Loop ----------------
def game_loop():
    global player_x, player_y, player_dx, player_speed
    global bullet_x, bullet_y, bullet_state, bullet_speed, bullet_count, player_bullets
    global score, player_lives, player_health, player_invuln_timer, level, unlocked_levels
    global particles, animations, asteroids, current_level_config
    global player_shield, player_shield_timer
    
    player_x, player_y = PLAYER_START_X, PLAYER_START_Y
    player_dx = 0.0
    player_speed = PLAYER_SPEED
    player_bullets.clear()
    bullet_x, bullet_y, bullet_state = 0.0, player_y, 'ready'
    bullet_speed = BULLET_SPEED
    bullet_count = 1
    player_invuln_timer = 0.0
    player_shield = False
    player_shield_timer = 0.0
    enemy_bullets.clear()
    powerups.clear()
    particles.clear()
    animations.clear()
    asteroids.clear()
    active_powerups['fast_bullet'] = 0.0
    active_powerups['multi_shot'] = 0.0
    active_powerups['shield'] = 0.0
    active_powerups['speed_boost'] = 0.0
    active_powerups['spread_fire'] = 0.0
    active_powerups['speed_debuff'] = 0.0
    
    current_level_config = get_level_config(level)
    init_enemies(level)

    running = True
    paused = False
    asteroid_spawn_timer = 0
    shoot_cooldown = 0  # Prevent spam shooting

    while running:
        dt = clock.tick(60)/1000.0
        shoot_cooldown = max(0, shoot_cooldown - dt)
        
        screen_shake.update(dt)
        shake_offset = screen_shake.get_offset()
        
        # Draw background with level-specific color
        bg_color = current_level_config.get('bg_color', (0, 0, 0))
        screen.fill(bg_color)
        
        for star in stars:
            star.update(dt)
            star.draw(screen)
        
        screen.blit(background, shake_offset)
        show_score()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                save_game(level, score, player_lives, unlocked_levels)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: player_dx = -1
                if event.key == pygame.K_RIGHT: player_dx = 1
                if event.key == pygame.K_SPACE:
                    if shoot_cooldown <= 0:
                        fire_bullets()
                        shoot_cooldown = 0.2  # Cooldown between shots
                if event.key == pygame.K_p: 
                    paused = not paused
                    if paused:
                        save_game(level, score, player_lives, unlocked_levels)
                if event.key == pygame.K_r:
                    level = 1
                    unlocked_levels = 1
                    score = 0
                    player_lives = 3
                    player_health = PLAYER_MAX_HEALTH
                    delete_save()
                    init_enemies(level)
                if event.key == pygame.K_ESCAPE: 
                    save_game(level, score, player_lives, unlocked_levels)
                    home_screen()
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]: 
                    player_dx = 0

        if paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            pause_font = load_font('freesansbold.ttf', 48)
            pause_text = pause_font.render("PAUSED", True, (255, 255, 0))
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            
            shadow = pause_font.render("PAUSED", True, (0, 0, 0))
            screen.blit(shadow, (pause_rect.x + 3, pause_rect.y + 3))
            screen.blit(pause_text, pause_rect)
            
            hint_text = font.render("Press P to resume | ESC for menu", True, (200, 200, 200))
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            screen.blit(hint_text, hint_rect)
            
            pygame.display.update()
            continue

        # Spawn asteroids for certain levels
        if current_level_config.get('special') == 'asteroids':
            asteroid_spawn_timer += dt
            if asteroid_spawn_timer > 2.0:
                asteroids.append(Asteroid())
                asteroid_spawn_timer = 0
        
        # Update asteroids
        for ast in asteroids[:]:
            ast.update(dt)
            ast.draw(screen)
            if ast.is_offscreen():
                asteroids.remove(ast)
            elif is_collision(ast.x, ast.y, player_x + 16, player_y + 16, ast.size + 16):
                if player_shield:
                    player_shield = False
                    player_shield_timer = 0
                    active_powerups['shield'] = 0
                elif player_invuln_timer <= 0:
                    player_health -= 20
                    if player_health <= 0:
                        player_lives -= 1
                        player_health = PLAYER_MAX_HEALTH
                    player_invuln_timer = PLAYER_INVULN_TIME
                    create_explosion(player_x + 16, player_y + 16, (255, 0, 0), count=15, size=4)
                    screen_shake.start(0.3, 8)
                    play_sound('hit')
                asteroids.remove(ast)

        # Player movement
        if player_dx != 0: 
            player_x += player_dx * player_speed * dt
        player_x = max(0, min(player_x, SCREEN_WIDTH - player_image.get_width()))
        
        if player_invuln_timer > 0: 
            player_invuln_timer -= dt
        
        # Update powerup timers
        if active_powerups['fast_bullet'] > 0:
            active_powerups['fast_bullet'] -= dt
            if active_powerups['fast_bullet'] <= 0: 
                bullet_speed = BULLET_SPEED
        
        if active_powerups['shield'] > 0:
            active_powerups['shield'] -= dt
            player_shield_timer = active_powerups['shield']
            if active_powerups['shield'] <= 0:
                player_shield = False
                player_shield_timer = 0
        
        if active_powerups['multi_shot'] > 0:
            active_powerups['multi_shot'] -= dt
            
        if active_powerups['speed_boost'] > 0:
            active_powerups['speed_boost'] -= dt
            if active_powerups['speed_boost'] <= 0:
                player_speed = PLAYER_SPEED
                
        if active_powerups['spread_fire'] > 0:
            active_powerups['spread_fire'] -= dt

        # Debuff from enemy EMP bullets (separate timer from player powerups)
        if active_powerups.get('speed_debuff', 0) > 0:
            active_powerups['speed_debuff'] -= dt
            # Reduce player speed while debuffed, ensure we don't go below a sensible minimum
            player_speed = max(80, PLAYER_SPEED * 0.5)
            # When debuff ends restore speed
            if active_powerups['speed_debuff'] <= 0:
                player_speed = PLAYER_SPEED

        # Update player bullets
        for bullet in player_bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                player_bullets.remove(bullet)
            else:
                bullet.draw(screen)

        # Enemy movement and shooting
        for e in enemies[:]:
            if 'angle' in e:  # Circular pattern
                e['angle'] += e['vx'] * dt / 50
                radius = 100
                e['x'] = SCREEN_WIDTH/2 + radius * math.cos(e['angle'])
                e['y'] = 100 + radius * math.sin(e['angle'])
            else:
                e['x'] += e['vx'] * dt
                
            if e['x'] <= 0 or e['x'] >= SCREEN_WIDTH - ENEMY_WIDTH:
                e['vx'] *= -1
                if e['type'] == 'boss': 
                    e['y'] += ENEMY_DESCEND_BOSS
                elif e['type'] == 'strong': 
                    e['y'] += ENEMY_DESCEND_STRONG
                else: 
                    e['y'] += ENEMY_DESCEND_NORMAL
            
            # Enemy shooting
            e['shoot_timer'] += dt
            shoot_chance = current_level_config.get('enemy_shoot_chance', 0.002)
            if e['shoot_timer'] > 0.5 and random.random() < shoot_chance:
                # Aim at player
                dx = player_x - e['x']
                dy = player_y - e['y']
                dist = math.hypot(dx, dy)
                if dist > 0:
                        # Strong enemies have chance to fire an EMP debuff bullet
                        if e.get('type') == 'strong' and random.random() < min(0.15, 0.02 + level * 0.01):
                            spawn_enemy_bullet(e['x'] + ENEMY_WIDTH/2, e['y'] + ENEMY_HEIGHT,
                                               (dx/dist) * ENEMY_BULLET_SPEED,
                                               (dy/dist) * ENEMY_BULLET_SPEED, kind='emp')
                        else:
                            spawn_enemy_bullet(e['x'] + ENEMY_WIDTH/2, e['y'] + ENEMY_HEIGHT,
                                               (dx/dist) * ENEMY_BULLET_SPEED,
                                               (dy/dist) * ENEMY_BULLET_SPEED)
                e['shoot_timer'] = 0
            
            # Check if enemy reached bottom (game over condition)
            if e['y'] > SCREEN_HEIGHT - 100:
                player_lives = 0

        # Draw enemies and check bullet collisions
        for e in enemies[:]:
            draw_enemy(e)
            
            # Draw boss health bar
            if e['type'] == 'boss':
                draw_boss_health_bar(e)
            
            radius = 50 if e['type'] == 'boss' else (40 if e['type'] == 'strong' else 27)
            
            # Check collision with player bullets
            for bullet in player_bullets[:]:
                if is_collision(e['x'] + ENEMY_WIDTH/2, e['y'] + ENEMY_HEIGHT/2, 
                              bullet.x, bullet.y, radius):
                    bullet.active = False
                    
                    play_sound('hit')
                    create_explosion(e['x'] + ENEMY_WIDTH/2, e['y'] + ENEMY_HEIGHT/2, 
                                   (255, 200, 0), count=10, size=3)
                    
                    e['hp'] -= 1
                    if e['hp'] <= 0:
                        if e['type'] == 'boss':
                            play_sound('boss_explosion')
                            create_explosion(e['x'] + ENEMY_WIDTH/2, e['y'] + ENEMY_HEIGHT/2, 
                                           (255, 0, 0), count=40, size=6)
                            screen_shake.start(0.5, 10)
                            score += 50
                        else:
                            play_sound('explosion')
                            create_explosion(e['x'] + ENEMY_WIDTH/2, e['y'] + ENEMY_HEIGHT/2, 
                                           (255, 100, 0), count=20, size=4)
                            screen_shake.start(0.2, 5)
                            score += 10
                        
                        animations.append(Animation(e['x'] + ENEMY_WIDTH/2, 
                                                   e['y'] + ENEMY_HEIGHT/2, 0.8, "explosion"))
                        spawn_powerup(e['x'], e['y'])
                        enemies.remove(e)
                        break
                    else:
                        if e['type'] == 'strong': 
                            e['img'] = enemy_images_dict['normal']

        # Update and draw enemy bullets
        for b in enemy_bullets[:]:
            b['x'] += b['vx'] * dt
            b['y'] += b['vy'] * dt
            pygame.draw.circle(screen, (255, 255, 0), (int(b['x']), int(b['y'])), 4)
            pygame.draw.circle(screen, (255, 200, 0), (int(b['x']), int(b['y'])), 2)
            
            if is_collision(player_x + 16, player_y + 16, b['x'], b['y'], 20):
                if player_shield:
                    player_shield = False
                    player_shield_timer = 0
                    active_powerups['shield'] = 0
                elif player_invuln_timer <= 0:
                    player_health -= 15
                    if player_health <= 0:
                        player_lives -= 1
                        player_health = PLAYER_MAX_HEALTH
                    player_invuln_timer = PLAYER_INVULN_TIME
                    create_explosion(player_x + 16, player_y + 16, (255, 0, 0), count=15, size=4)
                    screen_shake.start(0.3, 8)
                    play_sound('hit')
                    # If this bullet is an EMP type, apply speed debuff to the player
                    try:
                        if b.get('kind') == 'emp':
                            # Debuff duration scales a bit with level (capped)
                            debuff_dur = min(6.0, 3.0 + level * 0.2)
                            active_powerups['speed_debuff'] = debuff_dur
                            # small visual/audio feedback
                            try:
                                play_sound('hit')
                            except:
                                pass
                            try:
                                create_explosion(player_x + 16, player_y + 16, (0, 200, 255), count=8, size=2)
                            except:
                                pass
                    except Exception:
                        pass
                try: 
                    enemy_bullets.remove(b)
                except: 
                    pass
            elif b['y'] > SCREEN_HEIGHT or b['x'] < 0 or b['x'] > SCREEN_WIDTH:
                try: 
                    enemy_bullets.remove(b)
                except: 
                    pass

        # Update particles and animations
        for p in particles[:]:
            p.update(dt)
            p.draw(screen)
            if not p.is_alive():
                particles.remove(p)
                
        for a in animations[:]:
            a.update(dt)
            a.draw(screen)
            if not a.is_alive():
                animations.remove(a)

        draw_powerups(dt)

        # Check game over
        if player_lives <= 0: 
            end_game("GAME OVER!")

        # Level complete check
        if len(enemies) == 0:
            # Update level progress BEFORE saving
            level += 1
            if level > unlocked_levels:
                unlocked_levels = level
            
            # Save the updated progress
            save_game(level, score, player_lives, unlocked_levels)
            
            # Show victory animation
            victory_animation()
            
            # Initialize next level
            current_level_config = get_level_config(level)
            init_enemies(level)
            player_x, player_y = PLAYER_START_X, PLAYER_START_Y
            player_bullets.clear()
            asteroids.clear()

        draw_player(player_x, player_y, invuln=(player_invuln_timer > 0))
        pygame.display.update()

# ---------------- Start Game ----------------
def start_screen():
    """Entry point - show intro then menu"""
    # Always show the textual intro first so the player sees the story immediately
    try:
        show_text_intro()
    except Exception as e:
        print(f"show_text_intro raised an exception: {e}")

    # Then try the cinematic (best-effort). If it fails, we already showed the text.
    try:
        _ = play_intro_video()
    except Exception as e:
        print(f"play_intro_video raised an exception: {e}")

    # Finally show main menu
    home_screen()

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    start_screen()