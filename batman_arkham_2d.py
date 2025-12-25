#!/usr/bin/env python3
"""
=============================================================================
BATMAN: ARKHAM SHADOWS - 2D Side-Scrolling Beat 'Em Up
=============================================================================

A 2D action game inspired by the Batman Arkham series.
Navigate through Gotham City, fight iconic villains and their henchmen!

CONTROLS:
---------
    Arrow Keys / WASD  : Move Batman
    SPACE              : Jump
    Z / J              : Punch
    X / K              : Kick
    C / L              : Throw Batarang
    P                  : Pause Game
    R                  : Restart (when game over)
    ESC                : Quit

CUSTOMIZATION GUIDE:
--------------------
This code is heavily commented to allow easy modifications:
    1. GAME SETTINGS: Adjust window size, FPS, colors (line ~50)
    2. PLAYER STATS: Modify Batman's health, speed, damage (line ~80)
    3. ENEMY CONFIGURATION: Add/modify enemies and their stats (line ~120)
    4. LEVEL DESIGN: Change level layout and backgrounds (line ~180)
    5. GRAPHICS: Replace placeholder graphics with images (line ~250)

Author: Claude (Anthropic AI)
License: Free to use and modify
=============================================================================
"""

import pygame
import random
import math
import os
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# Initialize Pygame
pygame.init()
# Initialize audio (optional - may fail in headless environments)
AUDIO_AVAILABLE = False
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    AUDIO_AVAILABLE = True
except pygame.error:
    print("Note: Audio not available in this environment")

# =============================================================================
# DARK KNIGHT INSPIRED MUSIC SYSTEM
# =============================================================================
# Generates dark, atmospheric music similar to Hans Zimmer's Dark Knight score

class DarkKnightMusic:
    """
    Generates and plays dark atmospheric music inspired by The Dark Knight.
    Uses procedurally generated tones for a brooding, intense atmosphere.
    """
    
    def __init__(self):
        self.enabled = AUDIO_AVAILABLE
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_music = None
        self.music_volume = 0.4  # Adjust music volume (0.0 - 1.0)
        self.sfx_volume = 0.6    # Adjust sound effects volume
        
        if self.enabled:
            self._generate_sounds()
    
    def _generate_tone(self, frequency: float, duration: float, 
                       volume: float = 0.3, fade_in: float = 0.1,
                       fade_out: float = 0.2) -> Optional[pygame.mixer.Sound]:
        """Generate a dark, atmospheric tone."""
        if not self.enabled:
            return None
        
        try:
            sample_rate = 44100
            n_samples = int(sample_rate * duration)
            
            # Create buffer
            import array
            buf = array.array('h')  # signed short integers
            
            max_amplitude = int(32767 * volume)
            
            for i in range(n_samples):
                t = i / sample_rate
                progress = i / n_samples
                
                # Main tone with slight detuning for richness
                wave = math.sin(2 * math.pi * frequency * t)
                wave += 0.5 * math.sin(2 * math.pi * (frequency * 1.01) * t)  # Slight detune
                wave += 0.3 * math.sin(2 * math.pi * (frequency * 0.5) * t)   # Sub octave
                wave += 0.2 * math.sin(2 * math.pi * (frequency * 2) * t)     # Overtone
                
                # Add some grit/texture
                wave += 0.1 * math.sin(2 * math.pi * (frequency * 3.01) * t)
                
                # Normalize
                wave = wave / 2.1
                
                # Apply envelope (fade in/out)
                envelope = 1.0
                if progress < fade_in:
                    envelope = progress / fade_in
                elif progress > (1 - fade_out):
                    envelope = (1 - progress) / fade_out
                
                # Add slow tremolo for tension
                tremolo = 1 + 0.1 * math.sin(2 * math.pi * 0.5 * t)
                
                sample = int(wave * envelope * tremolo * max_amplitude)
                buf.append(sample)  # Left channel
                buf.append(sample)  # Right channel
            
            sound = pygame.mixer.Sound(buffer=buf)
            return sound
        except Exception as e:
            print(f"Could not generate tone: {e}")
            return None
    
    def _generate_sounds(self):
        """Generate all game sounds."""
        print("Generating Dark Knight atmospheric audio...")
        
        # Dark ambient drone (low frequency, long duration)
        # Similar to the "BWAAAA" from Dark Knight
        self.sounds['ambient_drone'] = self._generate_tone(
            frequency=55,      # Low A note
            duration=8.0,      # Long drone
            volume=0.25,
            fade_in=0.5,
            fade_out=1.0
        )
        
        # Tension builder (rising tone)
        self.sounds['tension'] = self._generate_tone(
            frequency=110,     # A2
            duration=4.0,
            volume=0.2,
            fade_in=0.3,
            fade_out=0.5
        )
        
        # Combat hit sound
        self.sounds['hit'] = self._generate_tone(
            frequency=80,
            duration=0.15,
            volume=0.5,
            fade_in=0.01,
            fade_out=0.1
        )
        
        # Punch sound
        self.sounds['punch'] = self._generate_tone(
            frequency=100,
            duration=0.1,
            volume=0.4,
            fade_in=0.01,
            fade_out=0.05
        )
        
        # Kick sound (deeper)
        self.sounds['kick'] = self._generate_tone(
            frequency=60,
            duration=0.15,
            volume=0.45,
            fade_in=0.01,
            fade_out=0.08
        )
        
        # Batarang whoosh
        self.sounds['batarang'] = self._generate_tone(
            frequency=400,
            duration=0.2,
            volume=0.3,
            fade_in=0.02,
            fade_out=0.15
        )
        
        # Enemy death
        self.sounds['enemy_death'] = self._generate_tone(
            frequency=40,
            duration=0.5,
            volume=0.35,
            fade_in=0.01,
            fade_out=0.4
        )
        
        # Boss music drone (more intense)
        self.sounds['boss_drone'] = self._generate_tone(
            frequency=45,      # Even lower
            duration=6.0,
            volume=0.3,
            fade_in=0.3,
            fade_out=0.8
        )
        
        # Player hurt
        self.sounds['player_hurt'] = self._generate_tone(
            frequency=150,
            duration=0.2,
            volume=0.35,
            fade_in=0.01,
            fade_out=0.15
        )
        
        print("Audio generation complete!")
    
    def play_ambient(self, boss_fight: bool = False):
        """Start playing ambient music loop."""
        if not self.enabled:
            return
        
        sound_key = 'boss_drone' if boss_fight else 'ambient_drone'
        if sound_key in self.sounds and self.sounds[sound_key]:
            self.sounds[sound_key].set_volume(self.music_volume)
            self.sounds[sound_key].play(loops=-1)  # Loop indefinitely
            self.current_music = sound_key
    
    def stop_ambient(self):
        """Stop ambient music."""
        if not self.enabled:
            return
        
        if self.current_music and self.current_music in self.sounds:
            self.sounds[self.current_music].stop()
            self.current_music = None
    
    def play_sfx(self, sound_name: str):
        """Play a sound effect."""
        if not self.enabled:
            return
        
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].set_volume(self.sfx_volume)
            self.sounds[sound_name].play()
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.current_music and self.current_music in self.sounds:
            self.sounds[self.current_music].set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))

# Create global music instance
MUSIC = DarkKnightMusic()

# =============================================================================
# SECTION 1: GAME CONFIGURATION
# =============================================================================
# Modify these values to customize the game's basic settings

@dataclass
class GameConfig:
    """
    Central configuration class for game settings.
    Modify these values to change core game behavior.
    """
    # --- WINDOW SETTINGS ---
    SCREEN_WIDTH: int = 1200       # Game window width in pixels
    SCREEN_HEIGHT: int = 700       # Game window height in pixels
    FPS: int = 60                  # Frames per second (higher = smoother)
    TITLE: str = "BATMAN: ARKHAM SHADOWS"
    
    # --- GAMEPLAY SETTINGS ---
    GRAVITY: float = 0.8           # How fast entities fall (higher = heavier)
    GROUND_LEVEL: int = 550        # Y-coordinate of the ground
    SCROLL_THRESHOLD: int = 400    # When camera starts scrolling
    
    # --- LEVEL SETTINGS ---
    LEVEL_WIDTH: int = 8000        # Total level width in pixels
    NUM_LEVELS: int = 5            # Number of levels (one per boss)

# Create global config instance
CONFIG = GameConfig()

# =============================================================================
# SECTION 2: COLOR PALETTE
# =============================================================================
# Customize colors here. Format: (Red, Green, Blue) - values 0-255

class Colors:
    """
    Game color palette. Modify these to change the game's visual theme.
    """
    # Background colors
    NIGHT_SKY = (15, 15, 35)           # Dark blue night sky
    CITY_DARK = (25, 25, 45)           # Building silhouettes
    CITY_MID = (35, 35, 55)            # Mid-ground buildings
    CITY_LIGHT = (45, 45, 65)          # Foreground buildings
    
    # Character colors
    BATMAN_PRIMARY = (30, 30, 30)       # Batman's suit (dark grey)
    BATMAN_SECONDARY = (50, 50, 50)     # Batman's cape
    BATMAN_ACCENT = (255, 215, 0)       # Batman's belt (gold)
    
    # Enemy colors (customize per villain)
    JOKER_PRIMARY = (128, 0, 128)       # Purple suit
    JOKER_SECONDARY = (0, 255, 0)       # Green hair
    BANE_PRIMARY = (50, 50, 50)         # Dark outfit
    BANE_SECONDARY = (0, 200, 0)        # Venom tubes
    SCARFACE_PRIMARY = (139, 69, 19)    # Brown suit
    TWOFACE_PRIMARY = (255, 255, 255)   # White side
    TWOFACE_SECONDARY = (0, 0, 0)       # Black side
    RASALGHUL_PRIMARY = (0, 100, 0)     # Green robes
    
    # Henchmen colors
    HENCHMAN_COLORS = [
        (100, 50, 50),   # Joker thugs (maroon)
        (60, 60, 60),    # Bane thugs (dark grey)
        (80, 60, 40),    # Scarface thugs (brown)
        (70, 70, 70),    # Two-Face thugs
        (40, 80, 40),    # Ra's al Ghul assassins (green)
    ]
    
    # UI Colors
    HEALTH_BAR = (220, 20, 60)          # Red health bar
    HEALTH_BAR_BG = (50, 50, 50)        # Health bar background
    STAMINA_BAR = (30, 144, 255)        # Blue stamina bar
    TEXT_PRIMARY = (255, 255, 255)      # White text
    TEXT_SECONDARY = (200, 200, 200)    # Grey text
    BATARANG_COLOR = (50, 50, 50)       # Dark batarang
    
    # Effect colors
    HIT_FLASH = (255, 255, 255)         # Flash when hit
    COMBO_TEXT = (255, 215, 0)          # Gold combo counter

# =============================================================================
# SECTION 3: PLAYER CONFIGURATION (BATMAN)
# =============================================================================
# Modify these values to change Batman's abilities

@dataclass
class PlayerStats:
    """
    Batman's statistics. Adjust these to make Batman stronger or weaker.
    """
    # --- HEALTH ---
    MAX_HEALTH: int = 120              # Increased health
    
    # --- MOVEMENT ---
    MOVE_SPEED: float = 7.0            # Faster movement
    JUMP_POWER: float = -19.0          # Stronger jump
    DOUBLE_JUMP_POWER: float = -16.0   # Better double jump
    MAX_JUMPS: int = 2                 # Number of jumps allowed
    
    # --- COMBAT (BUFFED!) ---
    PUNCH_DAMAGE: int = 35             # INCREASED from 15 - powerful punch!
    KICK_DAMAGE: int = 45              # INCREASED from 20 - devastating kick!
    BATARANG_DAMAGE: int = 20          # INCREASED from 10 - sharper batarangs!
    
    # --- ATTACK PROPERTIES ---
    PUNCH_RANGE: int = 70              # Increased punch reach
    KICK_RANGE: int = 85               # Increased kick reach
    BATARANG_SPEED: float = 18.0       # Faster batarang
    BATARANG_MAX_DISTANCE: int = 600   # Longer range
    
    # --- COOLDOWNS (in frames, 60 frames = 1 second) ---
    PUNCH_COOLDOWN: int = 12           # Faster punching
    KICK_COOLDOWN: int = 20            # Faster kicking
    BATARANG_COOLDOWN: int = 35        # Faster batarang throwing
    
    # --- INVINCIBILITY ---
    HIT_INVINCIBILITY: int = 60        # Frames of invincibility after hit
    
    # --- COMBO SYSTEM ---
    COMBO_WINDOW: int = 100            # Longer combo window
    COMBO_DAMAGE_BONUS: float = 0.15   # 15% damage increase per combo hit
    MAX_COMBO_MULTIPLIER: float = 2.5  # Higher max combo multiplier

# Create player stats instance
PLAYER_STATS = PlayerStats()

# =============================================================================
# SECTION 4: ENEMY CONFIGURATION
# =============================================================================
# This is where you define all enemies and their properties.
# To add a new enemy, simply add a new entry to the ENEMY_CONFIGS dictionary.

@dataclass
class EnemyConfig:
    """
    Configuration for a single enemy type.
    All enemies (bosses and henchmen) use this structure.
    """
    name: str                          # Display name
    is_boss: bool                      # True = boss, False = henchman
    health: int                        # Maximum health points
    damage: int                        # Damage dealt per hit
    speed: float                       # Movement speed
    attack_range: int                  # Attack reach in pixels
    attack_cooldown: int               # Frames between attacks
    color_primary: Tuple[int, int, int]    # Main color
    color_secondary: Tuple[int, int, int]  # Accent color
    width: int = 50                    # Sprite width
    height: int = 80                   # Sprite height
    
    # --- SPECIAL ABILITIES (set True to enable) ---
    can_block: bool = False            # Can block attacks
    can_dodge: bool = False            # Can dodge attacks
    has_projectile: bool = False       # Can shoot projectiles
    projectile_damage: int = 0         # Projectile damage
    projectile_speed: float = 0.0      # Projectile speed
    
    # --- AI BEHAVIOR ---
    aggression: float = 0.5            # 0.0 = passive, 1.0 = aggressive
    patrol_range: int = 200            # How far they patrol
    
    # --- DROPS ---
    score_value: int = 100             # Points awarded when defeated
    health_drop_chance: float = 0.1    # Chance to drop health (0.0-1.0)

# =============================================================================
# ENEMY DEFINITIONS
# =============================================================================
# Add, modify, or remove enemies here. Each enemy needs a unique key.

ENEMY_CONFIGS: Dict[str, EnemyConfig] = {
    # -------------------------------------------------------------------------
    # BOSSES - One per level, much stronger than henchmen
    # -------------------------------------------------------------------------
    
    "joker": EnemyConfig(
        name="THE JOKER",
        is_boss=True,
        health=500,                    # High health for a boss
        damage=25,                     # Moderate damage
        speed=3.5,                     # Fairly quick
        attack_range=80,
        attack_cooldown=40,
        color_primary=Colors.JOKER_PRIMARY,
        color_secondary=Colors.JOKER_SECONDARY,
        width=60,
        height=90,
        can_dodge=True,                # Joker can dodge attacks
        has_projectile=True,           # Throws playing cards
        projectile_damage=15,
        projectile_speed=10.0,
        aggression=0.7,                # Quite aggressive
        score_value=5000,
        health_drop_chance=0.3,
    ),
    
    "bane": EnemyConfig(
        name="BANE",
        is_boss=True,
        health=800,                    # Extremely tanky
        damage=40,                     # Hits VERY hard
        speed=2.0,                     # Slow but powerful
        attack_range=100,              # Long reach
        attack_cooldown=60,            # Slow attacks
        color_primary=Colors.BANE_PRIMARY,
        color_secondary=Colors.BANE_SECONDARY,
        width=80,                      # Large sprite
        height=110,
        can_block=True,                # Can block attacks
        aggression=0.9,                # Very aggressive
        score_value=6000,
        health_drop_chance=0.4,
    ),
    
    "scarecrow": EnemyConfig(
        name="SCARECROW",
        is_boss=True,
        health=450,                    # Moderate health
        damage=22,
        speed=3.5,
        attack_range=85,               # Fear gas range
        attack_cooldown=35,
        color_primary=(80, 60, 40),    # Brown/tan
        color_secondary=(40, 30, 20),  # Dark brown
        width=60,
        height=95,
        has_projectile=True,           # Fear gas attacks
        projectile_damage=15,
        projectile_speed=8.0,
        can_dodge=True,                # Slippery
        aggression=0.65,
        score_value=4500,
        health_drop_chance=0.25,
    ),
    
    "twoface": EnemyConfig(
        name="TWO-FACE",
        is_boss=True,
        health=550,
        damage=30,
        speed=3.5,
        attack_range=75,
        attack_cooldown=45,
        color_primary=Colors.TWOFACE_PRIMARY,
        color_secondary=Colors.TWOFACE_SECONDARY,
        width=60,
        height=90,
        can_block=True,
        has_projectile=True,           # Dual pistols
        projectile_damage=18,
        projectile_speed=12.0,
        aggression=0.8,
        score_value=5500,
        health_drop_chance=0.35,
    ),
    
    "deathstroke": EnemyConfig(
        name="DEATHSTROKE",
        is_boss=True,
        health=750,                    # High health - master assassin
        damage=38,                     # High damage - deadly swordsman
        speed=5.5,                     # VERY fast (enhanced soldier)
        attack_range=95,               # Sword reach
        attack_cooldown=25,            # Fast attacks
        color_primary=(30, 40, 60),    # Dark blue armor
        color_secondary=(255, 140, 0), # Orange accents
        width=70,
        height=100,
        can_dodge=True,                # Can dodge
        can_block=True,                # Can block with sword
        has_projectile=True,           # Guns
        projectile_damage=20,
        projectile_speed=15.0,
        aggression=0.95,               # Extremely aggressive
        score_value=8000,
        health_drop_chance=0.5,
    ),
    
    # -------------------------------------------------------------------------
    # HENCHMEN - Spawned throughout levels, weaker than bosses
    # -------------------------------------------------------------------------
    
    "joker_thug": EnemyConfig(
        name="Joker Thug",
        is_boss=False,
        health=60,
        damage=10,
        speed=2.5,
        attack_range=50,
        attack_cooldown=45,
        color_primary=Colors.HENCHMAN_COLORS[0],
        color_secondary=(150, 80, 80),
        aggression=0.4,
        score_value=100,
        health_drop_chance=0.1,
    ),
    
    "bane_mercenary": EnemyConfig(
        name="Bane Mercenary",
        is_boss=False,
        health=100,                    # Tougher than average
        damage=15,
        speed=2.0,
        attack_range=60,
        attack_cooldown=50,
        color_primary=Colors.HENCHMAN_COLORS[1],
        color_secondary=(100, 100, 100),
        can_block=True,                # Some can block
        aggression=0.6,
        score_value=150,
        health_drop_chance=0.15,
    ),
    
    "scarecrow_thug": EnemyConfig(
        name="Fear Thug",
        is_boss=False,
        health=55,
        damage=10,
        speed=3.0,
        attack_range=50,
        attack_cooldown=40,
        color_primary=(80, 60, 40),
        color_secondary=(60, 45, 30),
        has_projectile=True,           # Fear toxin vials
        projectile_damage=8,
        projectile_speed=8.0,
        aggression=0.55,
        score_value=120,
        health_drop_chance=0.12,
    ),
    
    "twoface_goon": EnemyConfig(
        name="Two-Face Goon",
        is_boss=False,
        health=70,
        damage=12,
        speed=2.5,
        attack_range=55,
        attack_cooldown=42,
        color_primary=Colors.HENCHMAN_COLORS[3],
        color_secondary=(120, 120, 120),
        aggression=0.55,
        score_value=130,
        health_drop_chance=0.12,
    ),
    
    "deathstroke_soldier": EnemyConfig(
        name="Deathstroke Soldier",
        is_boss=False,
        health=90,
        damage=20,                     # Higher damage (military trained)
        speed=4.2,                     # Fast
        attack_range=65,
        attack_cooldown=32,
        color_primary=(40, 50, 60),    # Military grey-blue
        color_secondary=(80, 90, 100),
        can_dodge=True,                # Military training
        has_projectile=True,           # Armed with guns
        projectile_damage=12,
        projectile_speed=14.0,
        aggression=0.75,
        score_value=200,
        health_drop_chance=0.18,
    ),
}

# =============================================================================
# SECTION 5: LEVEL CONFIGURATION
# =============================================================================
# Define what enemies appear in each level

@dataclass
class LevelConfig:
    """
    Configuration for a single level.
    """
    level_number: int
    name: str
    boss_type: str                     # Key from ENEMY_CONFIGS
    henchman_types: List[str]          # List of henchman keys
    num_henchmen: int                  # How many henchmen to spawn
    background_color: Tuple[int, int, int]  # Level's sky color
    description: str = ""

LEVEL_CONFIGS: List[LevelConfig] = [
    LevelConfig(
        level_number=1,
        name="ACE CHEMICALS",
        boss_type="joker",
        henchman_types=["joker_thug"],
        num_henchmen=8,
        background_color=(20, 10, 30),  # Purple-tinted night
        description="The Joker has taken over Ace Chemicals!"
    ),
    LevelConfig(
        level_number=2,
        name="GOTHAM DOCKS",
        boss_type="bane",
        henchman_types=["bane_mercenary"],
        num_henchmen=6,                 # Fewer but tougher
        background_color=(10, 15, 25),  # Dark blue harbor
        description="Bane's mercenaries control the docks!"
    ),
    LevelConfig(
        level_number=3,
        name="ARKHAM ASYLUM",
        boss_type="scarecrow",
        henchman_types=["scarecrow_thug"],
        num_henchmen=10,
        background_color=(15, 15, 20),  # Dark creepy interior
        description="Scarecrow has released fear toxin in the asylum!"
    ),
    LevelConfig(
        level_number=4,
        name="OLD GOTHAM",
        boss_type="twoface",
        henchman_types=["twoface_goon", "scarecrow_thug"],  # Mixed enemies
        num_henchmen=8,
        background_color=(25, 20, 15),  # Brownish old city
        description="Two-Face controls Old Gotham's underworld!"
    ),
    LevelConfig(
        level_number=5,
        name="MILITARY BASE",
        boss_type="deathstroke",
        henchman_types=["deathstroke_soldier"],
        num_henchmen=12,
        background_color=(10, 15, 20),   # Dark military
        description="Face the world's deadliest assassin - Deathstroke!"
    ),
]

# =============================================================================
# SECTION 6: GRAPHICS SYSTEM
# =============================================================================
# This section handles drawing characters.
# TO USE CUSTOM IMAGES: Uncomment the image loading code and provide file paths.

class GraphicsManager:
    """
    Manages all game graphics.
    
    TO USE CUSTOM IMAGES:
    1. Create/download sprites for each character
    2. Update the image paths in the SPRITE_PATHS dictionary
    3. Set USE_CUSTOM_SPRITES = True
    
    Recommended sprite sizes:
    - Batman: 64x96 pixels
    - Bosses: 80x110 pixels  
    - Henchmen: 50x80 pixels
    """
    
    # Set to True to use image files instead of drawn shapes
    USE_CUSTOM_SPRITES: bool = True  # ENABLED - Using custom images!
    
    # Define paths to your sprite images here
    # =========================================================================
    # MODIFY THESE PATHS TO USE YOUR OWN IMAGES
    # =========================================================================
    SPRITE_PATHS: Dict[str, str] = {
        # Main Batman sprite (used for idle)
        "batman_main": "sprites/batman.jpg",
        
        # Background image
        "gotham_background": "sprites/gotham_background.jpg",
        
        # Player sprites - SEPARATE ANIMATIONS FOR EACH ACTION!
        "batman_idle": "sprites/batman.jpg",
        "batman_run": "sprites/batman_run.png",
        "batman_run_1": "sprites/batman_run.png",
        "batman_run_2": "sprites/batman_run.png",
        "batman_jump": "sprites/batman_jump.png",
        "batman_punch": "sprites/batman_punch.png",
        "batman_kick": "sprites/batman_kick.png",
        "batman_batarang": "sprites/batman_punch.png",  # Use punch pose for throwing
        
        # Boss sprites - NOW WITH CUSTOM IMAGES!
        "joker": "sprites/bosses/joker.jpg",
        "bane": "sprites/bosses/bane.jpg",
        "scarecrow": "sprites/bosses/scarecrow.jpg",
        "twoface": "sprites/bosses/twoface.jpg",
        "deathstroke": "sprites/bosses/deathstroke.png",
        
        # Henchman sprites - soldier image for all henchmen
        "soldier": "sprites/henchmen/soldier.jpg",
        "joker_thug": "sprites/henchmen/soldier.jpg",
        "bane_mercenary": "sprites/henchmen/soldier.jpg",
        "scarecrow_thug": "sprites/henchmen/soldier.jpg",
        "twoface_goon": "sprites/henchmen/soldier.jpg",
        "deathstroke_soldier": "sprites/henchmen/soldier.jpg",
        
        # Items (using fallback shapes if not found)
        "batarang": "sprites/items/batarang.png",
        "health_pickup": "sprites/items/health.png",
    }
    
    def __init__(self):
        """Initialize the graphics manager."""
        self.sprites: Dict[str, pygame.Surface] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.background_image: Optional[pygame.Surface] = None
        self.batman_image: Optional[pygame.Surface] = None
        self._load_fonts()
        # Note: _load_sprites() is called separately after display is set
        self._sprites_loaded = False
    
    def _load_fonts(self):
        """Load game fonts."""
        # Try to use a better font if available, fallback to default
        try:
            self.fonts["title"] = pygame.font.Font(None, 72)
            self.fonts["large"] = pygame.font.Font(None, 48)
            self.fonts["medium"] = pygame.font.Font(None, 36)
            self.fonts["small"] = pygame.font.Font(None, 24)
            self.fonts["tiny"] = pygame.font.Font(None, 18)
        except Exception:
            # Fallback to system font
            self.fonts["title"] = pygame.font.SysFont("Arial", 60)
            self.fonts["large"] = pygame.font.SysFont("Arial", 40)
            self.fonts["medium"] = pygame.font.SysFont("Arial", 30)
            self.fonts["small"] = pygame.font.SysFont("Arial", 20)
            self.fonts["tiny"] = pygame.font.SysFont("Arial", 14)
    
    def load_sprites(self):
        """
        Load sprite images from files.
        MUST be called after pygame.display.set_mode()!
        
        TO ADD NEW SPRITES:
        1. Add the path to SPRITE_PATHS dictionary above
        2. Place the image file in the specified location
        """
        if self._sprites_loaded:
            return
        
        print("\n--- Loading Custom Sprites ---")
        for name, path in self.SPRITE_PATHS.items():
            try:
                if os.path.exists(path):
                    image = pygame.image.load(path).convert_alpha()
                    self.sprites[name] = image
                    print(f"✓ Loaded sprite: {name}")
                    
                    # Store special references for easy access
                    if name == "batman_main":
                        self.batman_image = image
                    elif name == "gotham_background":
                        self.background_image = image
            except Exception as e:
                print(f"✗ Error loading sprite {name}: {e}")
        
        self._sprites_loaded = True
        
        # Summary
        print(f"\nLoaded {len(self.sprites)} sprites total")
        if self.batman_image:
            print("→ Batman custom sprite: ACTIVE")
        if self.background_image:
            print("→ Gotham background: ACTIVE")
        print("-------------------------------\n")
    
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """
        Get a loaded sprite by name.
        Returns None if sprite not found (will use fallback drawing).
        """
        return self.sprites.get(name)
    
    def draw_batman(self, surface: pygame.Surface, x: int, y: int, 
                    width: int, height: int, facing_right: bool,
                    state: str = "idle", frame: int = 0):
        """
        Draw Batman sprite or fallback shape.
        
        Args:
            surface: pygame surface to draw on
            x, y: position (top-left corner)
            width, height: size
            facing_right: direction Batman is facing
            state: animation state ("idle", "run", "jump", "punch", "kick", "batarang")
            frame: animation frame number
        """
        # Select the correct sprite based on state
        sprite = None
        sprite_key = None
        
        if state == "punch":
            sprite_key = "batman_punch"
        elif state == "kick":
            sprite_key = "batman_kick"
        elif state == "batarang":
            sprite_key = "batman_punch"  # Use punch pose for throwing
        elif state == "jump":
            sprite_key = "batman_jump"
        elif state == "run":
            sprite_key = "batman_run"
        else:  # idle
            sprite_key = "batman_idle"
        
        sprite = self.get_sprite(sprite_key)
        
        # Fallback to main batman if specific sprite not found
        if not sprite:
            sprite = self.batman_image
        
        if sprite:
            # Scale the image to fit the character size (slightly larger for detail)
            scaled = pygame.transform.scale(sprite, (width + 35, height + 25))
            
            # Flip if facing left
            if not facing_right:
                scaled = pygame.transform.flip(scaled, True, False)
            
            # Create surface with alpha for transparency
            scaled = scaled.convert_alpha()
            final_surface = pygame.Surface((width + 35, height + 25), pygame.SRCALPHA)
            final_surface.blit(scaled, (0, 0))
            
            # Remove white/light background pixels
            try:
                pixels = pygame.PixelArray(final_surface)
                # Remove white and near-white pixels
                for threshold in range(235, 256):
                    pixels.replace((threshold, threshold, threshold), (0, 0, 0, 0))
                del pixels
            except Exception:
                pass
            
            # Add slight animation effects
            offset_x = -17
            offset_y = -12
            
            if state == "run":
                # Bobbing animation while running
                offset_y += int(math.sin(frame * 0.8) * 3)
            elif state == "jump":
                # Slight scale effect for jump
                offset_y -= 5
            elif state in ["punch", "kick"]:
                # Forward lean for attacks
                offset_x += 5 if facing_right else -5
            
            surface.blit(final_surface, (x + offset_x, y + offset_y))
        else:
            # Fallback: Draw Batman using shapes
            self._draw_batman_fallback(surface, x, y, width, height, 
                                       facing_right, state)
    
    def _draw_batman_fallback(self, surface: pygame.Surface, x: int, y: int,
                              width: int, height: int, facing_right: bool,
                              state: str):
        """
        Draw Batman using primitive shapes (fallback when no sprites).
        This creates a stylized Batman silhouette.
        """
        # Cape (drawn first, behind body)
        cape_points = [
            (x + width // 2, y + height // 4),
            (x - 10 if facing_right else x + width + 10, y + height),
            (x + width // 2, y + height - 10),
            (x + width + 10 if facing_right else x - 10, y + height),
        ]
        pygame.draw.polygon(surface, Colors.BATMAN_SECONDARY, cape_points)
        
        # Body
        body_rect = pygame.Rect(x + width // 4, y + height // 3, 
                                width // 2, height // 2)
        pygame.draw.rect(surface, Colors.BATMAN_PRIMARY, body_rect)
        
        # Head (with ears)
        head_rect = pygame.Rect(x + width // 4, y, width // 2, height // 3)
        pygame.draw.rect(surface, Colors.BATMAN_PRIMARY, head_rect)
        
        # Bat ears
        ear_height = height // 6
        left_ear = [(x + width // 4, y), 
                    (x + width // 3, y - ear_height),
                    (x + width // 3 + 8, y)]
        right_ear = [(x + width * 2 // 3 - 8, y),
                     (x + width * 2 // 3, y - ear_height),
                     (x + width * 3 // 4, y)]
        pygame.draw.polygon(surface, Colors.BATMAN_PRIMARY, left_ear)
        pygame.draw.polygon(surface, Colors.BATMAN_PRIMARY, right_ear)
        
        # Belt
        belt_rect = pygame.Rect(x + width // 4, y + height // 2, 
                                width // 2, 8)
        pygame.draw.rect(surface, Colors.BATMAN_ACCENT, belt_rect)
        
        # Legs
        leg_width = width // 5
        left_leg = pygame.Rect(x + width // 3 - leg_width // 2, 
                               y + height * 2 // 3, leg_width, height // 3)
        right_leg = pygame.Rect(x + width * 2 // 3 - leg_width // 2,
                                y + height * 2 // 3, leg_width, height // 3)
        pygame.draw.rect(surface, Colors.BATMAN_PRIMARY, left_leg)
        pygame.draw.rect(surface, Colors.BATMAN_PRIMARY, right_leg)
        
        # Eyes (white slits)
        eye_y = y + height // 6
        if facing_right:
            pygame.draw.line(surface, (255, 255, 255), 
                           (x + width // 3, eye_y), 
                           (x + width // 2 - 5, eye_y - 3), 2)
            pygame.draw.line(surface, (255, 255, 255),
                           (x + width // 2 + 5, eye_y),
                           (x + width * 2 // 3, eye_y - 3), 2)
        else:
            pygame.draw.line(surface, (255, 255, 255),
                           (x + width // 3, eye_y - 3),
                           (x + width // 2 - 5, eye_y), 2)
            pygame.draw.line(surface, (255, 255, 255),
                           (x + width // 2 + 5, eye_y - 3),
                           (x + width * 2 // 3, eye_y), 2)
    
    def draw_enemy(self, surface: pygame.Surface, x: int, y: int,
                   config: EnemyConfig, facing_right: bool,
                   state: str = "idle"):
        """
        Draw an enemy sprite or fallback shape.
        
        Args:
            surface: pygame surface to draw on
            x, y: position
            config: enemy configuration
            facing_right: direction facing
            state: animation state
        """
        # Try to find a matching sprite
        # Check for boss sprites first, then henchman sprites
        sprite = None
        
        # Try exact name match (lowercase, no spaces)
        sprite_key = config.name.lower().replace(" ", "_").replace("'", "").replace("-", "")
        
        # Try various sprite keys
        possible_keys = [
            sprite_key,
            config.name.lower().replace(" ", ""),
            "soldier",  # Fallback for all henchmen
        ]
        
        for key in possible_keys:
            sprite = self.get_sprite(key)
            if sprite:
                break
        
        if sprite:
            # Scale sprite to character size
            scaled = pygame.transform.scale(sprite, (config.width + 20, config.height + 10))
            
            # Flip if facing left
            if not facing_right:
                scaled = pygame.transform.flip(scaled, True, False)
            
            # Create surface with alpha for transparency
            scaled = scaled.convert_alpha()
            final_surface = pygame.Surface((config.width + 20, config.height + 10), pygame.SRCALPHA)
            final_surface.blit(scaled, (0, 0))
            
            # Remove white/light gray background
            try:
                pixels = pygame.PixelArray(final_surface)
                # Remove white and near-white pixels
                for threshold in range(230, 256):
                    pixels.replace((threshold, threshold, threshold), (0, 0, 0, 0))
                # Also remove light grays
                for r in range(220, 256):
                    for g in range(220, 256):
                        for b in range(220, 256):
                            if r == g == b:  # Only pure grays
                                pixels.replace((r, g, b), (0, 0, 0, 0))
                del pixels
            except Exception:
                pass  # If pixel manipulation fails, just use the sprite as-is
            
            surface.blit(final_surface, (x - 10, y - 5))
        else:
            # Fallback drawing
            self._draw_enemy_fallback(surface, x, y, config, facing_right)
    
    def _draw_enemy_fallback(self, surface: pygame.Surface, x: int, y: int,
                             config: EnemyConfig, facing_right: bool):
        """Draw enemy using shapes (fallback)."""
        w, h = config.width, config.height
        
        # Body
        body_rect = pygame.Rect(x + w // 4, y + h // 4, w // 2, h // 2)
        pygame.draw.rect(surface, config.color_primary, body_rect)
        
        # Head
        head_size = min(w, h) // 3
        head_rect = pygame.Rect(x + w // 2 - head_size // 2, y, 
                                head_size, head_size)
        pygame.draw.ellipse(surface, config.color_secondary, head_rect)
        
        # Legs
        leg_width = w // 5
        left_leg = pygame.Rect(x + w // 3 - leg_width // 2,
                               y + h * 2 // 3, leg_width, h // 3)
        right_leg = pygame.Rect(x + w * 2 // 3 - leg_width // 2,
                                y + h * 2 // 3, leg_width, h // 3)
        pygame.draw.rect(surface, config.color_primary, left_leg)
        pygame.draw.rect(surface, config.color_primary, right_leg)
        
        # Boss indicator (glowing outline for bosses)
        if config.is_boss:
            outline_rect = pygame.Rect(x - 2, y - 2, w + 4, h + 4)
            pygame.draw.rect(surface, (255, 50, 50), outline_rect, 3)
    
    def draw_batarang(self, surface: pygame.Surface, x: int, y: int,
                      angle: float):
        """Draw a spinning batarang."""
        sprite = self.get_sprite("batarang")
        if sprite:
            rotated = pygame.transform.rotate(sprite, angle)
            rect = rotated.get_rect(center=(x, y))
            surface.blit(rotated, rect)
        else:
            # Fallback: draw bat-shaped projectile
            points = [
                (x, y - 5),       # Top
                (x - 15, y),      # Left wing
                (x - 5, y + 3),   # Left inner
                (x, y + 8),       # Bottom
                (x + 5, y + 3),   # Right inner
                (x + 15, y),      # Right wing
            ]
            # Rotate points
            cos_a = math.cos(math.radians(angle))
            sin_a = math.sin(math.radians(angle))
            rotated_points = []
            for px, py in points:
                dx, dy = px - x, py - y
                new_x = x + dx * cos_a - dy * sin_a
                new_y = y + dx * sin_a + dy * cos_a
                rotated_points.append((new_x, new_y))
            
            pygame.draw.polygon(surface, Colors.BATARANG_COLOR, rotated_points)

# Create global graphics manager
GRAPHICS = GraphicsManager()

# =============================================================================
# SECTION 7: GAME ENTITIES
# =============================================================================
# Classes for all game objects (player, enemies, projectiles)

class EntityState(Enum):
    """Possible states for game entities."""
    IDLE = "idle"
    RUNNING = "running"
    JUMPING = "jumping"
    FALLING = "falling"
    ATTACKING = "attacking"
    HIT = "hit"
    DEAD = "dead"
    BLOCKING = "blocking"

class AttackType(Enum):
    """Types of attacks."""
    NONE = "none"
    PUNCH = "punch"
    KICK = "kick"
    BATARANG = "batarang"
    ENEMY_MELEE = "enemy_melee"
    ENEMY_PROJECTILE = "enemy_projectile"

class Projectile:
    """Base class for projectiles (batarangs, enemy attacks)."""
    
    def __init__(self, x: float, y: float, velocity_x: float, velocity_y: float,
                 damage: int, owner_is_player: bool, max_distance: int = 500):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.damage = damage
        self.owner_is_player = owner_is_player
        self.max_distance = max_distance
        self.distance_traveled = 0
        self.active = True
        self.angle = 0  # For spinning animation
        self.width = 20
        self.height = 10
    
    def update(self):
        """Update projectile position."""
        if not self.active:
            return
        
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.distance_traveled += abs(self.velocity_x)
        self.angle += 15  # Spin animation
        
        # Deactivate if traveled too far
        if self.distance_traveled > self.max_distance:
            self.active = False
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                          self.width, self.height)
    
    def draw(self, surface: pygame.Surface, camera_x: int):
        """Draw the projectile."""
        if self.active:
            screen_x = self.x - camera_x
            GRAPHICS.draw_batarang(surface, int(screen_x), int(self.y), self.angle)

class Entity:
    """Base class for all game entities (player, enemies)."""
    
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.facing_right = True
        self.state = EntityState.IDLE
        self.health = 100
        self.max_health = 100
        self.animation_frame = 0
        self.animation_timer = 0
        self.invincibility_frames = 0
        self.attack_cooldown = 0
        self.current_attack = AttackType.NONE
        self.attack_frame = 0
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_attack_rect(self) -> Optional[pygame.Rect]:
        """Get attack hitbox (override in subclasses)."""
        return None
    
    def apply_gravity(self):
        """Apply gravity to the entity."""
        self.velocity_y += CONFIG.GRAVITY
        # Terminal velocity
        if self.velocity_y > 20:
            self.velocity_y = 20
    
    def is_on_ground(self) -> bool:
        """Check if entity is on the ground."""
        return self.y + self.height >= CONFIG.GROUND_LEVEL
    
    def take_damage(self, amount: int, knockback_direction: int = 0):
        """
        Apply damage to the entity.
        Override in subclasses for special behavior.
        """
        if self.invincibility_frames > 0:
            return
        
        self.health -= amount
        self.invincibility_frames = 30  # Brief invincibility
        self.velocity_x = knockback_direction * 5  # Knockback
        
        if self.health <= 0:
            self.health = 0
            self.state = EntityState.DEAD

class Player(Entity):
    """
    The player character (Batman).
    Uses PLAYER_STATS for all configuration.
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 50, 80)
        self.max_health = PLAYER_STATS.MAX_HEALTH
        self.health = self.max_health
        self.jumps_remaining = PLAYER_STATS.MAX_JUMPS
        self.combo_count = 0
        self.combo_timer = 0
        self.score = 0
        
        # Cooldown trackers
        self.punch_cooldown = 0
        self.kick_cooldown = 0
        self.batarang_cooldown = 0
        
        # Attack state
        self.attack_duration = 0
    
    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> Optional[Projectile]:
        """
        Handle player input.
        Returns a Projectile if batarang is thrown.
        """
        projectile = None
        
        # Don't accept input if attacking or dead
        if self.state == EntityState.DEAD:
            return None
        
        # Movement
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -PLAYER_STATS.MOVE_SPEED
            self.facing_right = False
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = PLAYER_STATS.MOVE_SPEED
            self.facing_right = True
            moving = True
        else:
            # Friction
            self.velocity_x *= 0.8
            if abs(self.velocity_x) < 0.5:
                self.velocity_x = 0
        
        # Update state based on movement
        if self.state not in [EntityState.ATTACKING, EntityState.JUMPING, EntityState.FALLING]:
            if moving:
                self.state = EntityState.RUNNING
            else:
                self.state = EntityState.IDLE
        
        # Decrement cooldowns
        if self.punch_cooldown > 0:
            self.punch_cooldown -= 1
        if self.kick_cooldown > 0:
            self.kick_cooldown -= 1
        if self.batarang_cooldown > 0:
            self.batarang_cooldown -= 1
        if self.attack_duration > 0:
            self.attack_duration -= 1
            if self.attack_duration == 0:
                self.current_attack = AttackType.NONE
        
        # Combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0
        
        return projectile
    
    def jump(self):
        """Make Batman jump."""
        if self.jumps_remaining > 0:
            if self.jumps_remaining == PLAYER_STATS.MAX_JUMPS:
                self.velocity_y = PLAYER_STATS.JUMP_POWER
            else:
                self.velocity_y = PLAYER_STATS.DOUBLE_JUMP_POWER
            self.jumps_remaining -= 1
            self.state = EntityState.JUMPING
    
    def punch(self) -> bool:
        """
        Perform a punch attack.
        Returns True if attack was executed.
        """
        if self.punch_cooldown <= 0 and self.attack_duration <= 0:
            self.punch_cooldown = PLAYER_STATS.PUNCH_COOLDOWN
            self.current_attack = AttackType.PUNCH
            self.attack_duration = 15
            self.state = EntityState.ATTACKING
            MUSIC.play_sfx('punch')  # Play punch sound!
            return True
        return False
    
    def kick(self) -> bool:
        """
        Perform a kick attack.
        Returns True if attack was executed.
        """
        if self.kick_cooldown <= 0 and self.attack_duration <= 0:
            self.kick_cooldown = PLAYER_STATS.KICK_COOLDOWN
            self.current_attack = AttackType.KICK
            self.attack_duration = 20
            self.state = EntityState.ATTACKING
            MUSIC.play_sfx('kick')  # Play kick sound!
            return True
        return False
    
    def throw_batarang(self) -> Optional[Projectile]:
        """
        Throw a batarang.
        Returns the Projectile object if thrown.
        """
        if self.batarang_cooldown <= 0:
            self.batarang_cooldown = PLAYER_STATS.BATARANG_COOLDOWN
            self.current_attack = AttackType.BATARANG
            self.attack_duration = 10
            MUSIC.play_sfx('batarang')  # Play whoosh sound!
            
            # Create batarang projectile
            direction = 1 if self.facing_right else -1
            batarang = Projectile(
                x=self.x + (self.width if self.facing_right else 0),
                y=self.y + self.height // 3,
                velocity_x=PLAYER_STATS.BATARANG_SPEED * direction,
                velocity_y=0,
                damage=PLAYER_STATS.BATARANG_DAMAGE,
                owner_is_player=True,
                max_distance=PLAYER_STATS.BATARANG_MAX_DISTANCE
            )
            return batarang
        return None
    
    def get_attack_rect(self) -> Optional[pygame.Rect]:
        """Get the hitbox for current attack."""
        if self.current_attack == AttackType.NONE or self.attack_duration <= 0:
            return None
        
        if self.current_attack == AttackType.PUNCH:
            attack_range = PLAYER_STATS.PUNCH_RANGE
        elif self.current_attack == AttackType.KICK:
            attack_range = PLAYER_STATS.KICK_RANGE
        else:
            return None
        
        if self.facing_right:
            return pygame.Rect(self.x + self.width, self.y + 20,
                              attack_range, self.height - 40)
        else:
            return pygame.Rect(self.x - attack_range, self.y + 20,
                              attack_range, self.height - 40)
    
    def get_attack_damage(self) -> int:
        """Get damage for current attack with combo bonus."""
        if self.current_attack == AttackType.PUNCH:
            base_damage = PLAYER_STATS.PUNCH_DAMAGE
        elif self.current_attack == AttackType.KICK:
            base_damage = PLAYER_STATS.KICK_DAMAGE
        else:
            return 0
        
        # Apply combo multiplier
        multiplier = 1.0 + (self.combo_count * PLAYER_STATS.COMBO_DAMAGE_BONUS)
        multiplier = min(multiplier, PLAYER_STATS.MAX_COMBO_MULTIPLIER)
        
        return int(base_damage * multiplier)
    
    def register_hit(self):
        """Register a successful hit (for combo system)."""
        self.combo_count += 1
        self.combo_timer = PLAYER_STATS.COMBO_WINDOW
        MUSIC.play_sfx('hit')  # Play hit sound!
    
    def take_damage(self, amount: int, knockback_direction: int = 0):
        """Take damage and reset combo."""
        if self.invincibility_frames > 0:
            return
        
        super().take_damage(amount, knockback_direction)
        self.combo_count = 0
        self.combo_timer = 0
        self.invincibility_frames = PLAYER_STATS.HIT_INVINCIBILITY
        MUSIC.play_sfx('player_hurt')  # Play hurt sound!
    
    def update(self):
        """Update player state."""
        # Apply gravity
        self.apply_gravity()
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Ground collision
        if self.y + self.height > CONFIG.GROUND_LEVEL:
            self.y = CONFIG.GROUND_LEVEL - self.height
            self.velocity_y = 0
            self.jumps_remaining = PLAYER_STATS.MAX_JUMPS
            if self.state in [EntityState.JUMPING, EntityState.FALLING]:
                self.state = EntityState.IDLE
        
        # Update jumping/falling state
        if self.velocity_y < 0:
            self.state = EntityState.JUMPING
        elif self.velocity_y > 2 and not self.is_on_ground():
            self.state = EntityState.FALLING
        
        # Keep in bounds
        if self.x < 0:
            self.x = 0
        if self.x > CONFIG.LEVEL_WIDTH - self.width:
            self.x = CONFIG.LEVEL_WIDTH - self.width
        
        # Invincibility countdown
        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1
        
        # Animation
        self.animation_timer += 1
        if self.animation_timer >= 8:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
    
    def draw(self, surface: pygame.Surface, camera_x: int):
        """Draw Batman."""
        screen_x = self.x - camera_x
        
        # Flash when invincible
        if self.invincibility_frames > 0 and self.invincibility_frames % 4 < 2:
            return  # Skip drawing (flash effect)
        
        # Determine animation state - now includes batarang!
        if self.current_attack == AttackType.PUNCH:
            state = "punch"
        elif self.current_attack == AttackType.KICK:
            state = "kick"
        elif self.current_attack == AttackType.BATARANG:
            state = "batarang"  # Uses punch sprite
        elif self.state == EntityState.JUMPING or self.state == EntityState.FALLING:
            state = "jump"
        elif self.state == EntityState.RUNNING:
            state = "run"
        else:
            state = "idle"
        
        GRAPHICS.draw_batman(surface, int(screen_x), int(self.y),
                            self.width, self.height, self.facing_right,
                            state, self.animation_frame)

class Enemy(Entity):
    """
    Enemy character class.
    Uses EnemyConfig for all configuration.
    """
    
    def __init__(self, x: float, y: float, config: EnemyConfig):
        super().__init__(x, y, config.width, config.height)
        self.config = config
        self.max_health = config.health
        self.health = self.max_health
        self.spawn_x = x  # Remember spawn position for patrol
        self.ai_timer = 0
        self.ai_state = "patrol"  # patrol, chase, attack, retreat
        self.blocking = False
        self.projectile_cooldown = 0
    
    def update(self, player: Player) -> Optional[Projectile]:
        """
        Update enemy AI and state.
        Returns a Projectile if enemy fires one.
        """
        if self.state == EntityState.DEAD:
            return None
        
        projectile = None
        
        # Decrement cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.projectile_cooldown > 0:
            self.projectile_cooldown -= 1
        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1
        
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Update facing direction
        self.facing_right = dx > 0
        
        # AI behavior based on aggression and distance
        self.ai_timer += 1
        
        # Random AI updates (less frequent = more performance)
        if self.ai_timer >= 30:
            self.ai_timer = 0
            
            # Decide AI state based on distance and aggression
            if distance < self.config.attack_range:
                self.ai_state = "attack"
            elif distance < 300 and random.random() < self.config.aggression:
                self.ai_state = "chase"
            elif distance > 400:
                self.ai_state = "patrol"
            else:
                # Random chance to attack or retreat based on aggression
                if random.random() < self.config.aggression:
                    self.ai_state = "chase"
                else:
                    self.ai_state = "retreat"
        
        # Execute AI state
        if self.ai_state == "patrol":
            # Patrol back and forth around spawn point
            target_x = self.spawn_x + math.sin(pygame.time.get_ticks() / 1000) * self.config.patrol_range
            if target_x > self.x:
                self.velocity_x = self.config.speed * 0.5
                self.facing_right = True
            else:
                self.velocity_x = -self.config.speed * 0.5
                self.facing_right = False
                
        elif self.ai_state == "chase":
            # Move toward player
            if dx > 10:
                self.velocity_x = self.config.speed
            elif dx < -10:
                self.velocity_x = -self.config.speed
            else:
                self.velocity_x = 0
                
        elif self.ai_state == "attack":
            self.velocity_x = 0  # Stop moving to attack
            
            # Melee attack
            if self.attack_cooldown <= 0 and distance < self.config.attack_range:
                self.current_attack = AttackType.ENEMY_MELEE
                self.attack_cooldown = self.config.attack_cooldown
                self.attack_frame = 15
            
            # Projectile attack (if capable)
            if (self.config.has_projectile and 
                self.projectile_cooldown <= 0 and 
                distance > 100 and distance < 400):
                direction = 1 if self.facing_right else -1
                projectile = Projectile(
                    x=self.x + (self.width if self.facing_right else 0),
                    y=self.y + self.height // 3,
                    velocity_x=self.config.projectile_speed * direction,
                    velocity_y=0,
                    damage=self.config.projectile_damage,
                    owner_is_player=False,
                    max_distance=600
                )
                self.projectile_cooldown = 90  # Slower than melee
                
        elif self.ai_state == "retreat":
            # Move away from player
            if dx > 0:
                self.velocity_x = -self.config.speed
            else:
                self.velocity_x = self.config.speed
        
        # Blocking behavior (for capable enemies)
        if self.config.can_block and player.attack_duration > 0:
            if random.random() < 0.3:  # 30% chance to block
                self.blocking = True
                self.state = EntityState.BLOCKING
        else:
            self.blocking = False
        
        # Dodge behavior (for capable enemies)
        if self.config.can_dodge and player.attack_duration > 5:
            if distance < 100 and random.random() < 0.2:
                # Dodge away
                dodge_dir = -1 if dx > 0 else 1
                self.velocity_x = dodge_dir * self.config.speed * 2
        
        # Apply gravity
        self.apply_gravity()
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Ground collision
        if self.y + self.height > CONFIG.GROUND_LEVEL:
            self.y = CONFIG.GROUND_LEVEL - self.height
            self.velocity_y = 0
        
        # Keep in level bounds
        if self.x < 0:
            self.x = 0
        if self.x > CONFIG.LEVEL_WIDTH - self.width:
            self.x = CONFIG.LEVEL_WIDTH - self.width
        
        # Update attack frame
        if self.attack_frame > 0:
            self.attack_frame -= 1
            if self.attack_frame == 0:
                self.current_attack = AttackType.NONE
        
        # Animation
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        
        return projectile
    
    def get_attack_rect(self) -> Optional[pygame.Rect]:
        """Get attack hitbox for enemy."""
        if self.current_attack != AttackType.ENEMY_MELEE or self.attack_frame < 5:
            return None
        
        if self.facing_right:
            return pygame.Rect(self.x + self.width, self.y + 20,
                              self.config.attack_range, self.height - 40)
        else:
            return pygame.Rect(self.x - self.config.attack_range, self.y + 20,
                              self.config.attack_range, self.height - 40)
    
    def take_damage(self, amount: int, knockback_direction: int = 0):
        """Take damage (reduced if blocking)."""
        if self.blocking and self.config.can_block:
            amount = amount // 3  # Blocking reduces damage by 2/3
        
        super().take_damage(amount, knockback_direction)
    
    def draw(self, surface: pygame.Surface, camera_x: int):
        """Draw the enemy."""
        screen_x = self.x - camera_x
        
        # Don't draw if off screen
        if screen_x < -self.width or screen_x > CONFIG.SCREEN_WIDTH + self.width:
            return
        
        # Flash when hit
        if self.invincibility_frames > 0 and self.invincibility_frames % 2 == 0:
            return
        
        # Determine state for drawing
        state = "idle"
        if self.current_attack != AttackType.NONE:
            state = "attack"
        elif self.blocking:
            state = "block"
        
        GRAPHICS.draw_enemy(surface, int(screen_x), int(self.y),
                           self.config, self.facing_right, state)
        
        # Draw health bar for bosses
        if self.config.is_boss:
            self._draw_boss_health_bar(surface, screen_x)
    
    def _draw_boss_health_bar(self, surface: pygame.Surface, screen_x: float):
        """Draw health bar above boss."""
        bar_width = self.width + 20
        bar_height = 8
        bar_x = screen_x - 10
        bar_y = self.y - 20
        
        # Background
        pygame.draw.rect(surface, Colors.HEALTH_BAR_BG,
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_width = (self.health / self.max_health) * bar_width
        pygame.draw.rect(surface, Colors.HEALTH_BAR,
                        (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255),
                        (bar_x, bar_y, bar_width, bar_height), 1)

class HealthPickup:
    """Health pickup item dropped by enemies."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.heal_amount = 20
        self.active = True
        self.lifetime = 600  # Frames before disappearing (10 seconds)
    
    def update(self):
        """Update pickup."""
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface: pygame.Surface, camera_x: int):
        """Draw the pickup."""
        if not self.active:
            return
        
        screen_x = self.x - camera_x
        
        # Pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() / 200)) * 0.3 + 0.7
        
        # Draw cross symbol
        color = (int(50 * pulse), int(200 * pulse), int(50 * pulse))
        center_x = screen_x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Vertical bar
        pygame.draw.rect(surface, color,
                        (center_x - 3, center_y - 10, 6, 20))
        # Horizontal bar
        pygame.draw.rect(surface, color,
                        (center_x - 10, center_y - 3, 20, 6))

# =============================================================================
# SECTION 8: LEVEL AND BACKGROUND
# =============================================================================

class Background:
    """
    Handles parallax scrolling background of Gotham City.
    
    TO CUSTOMIZE BACKGROUND:
    - Add your own background image to sprites/gotham_background.jpg
    - Or modify the building generation parameters below
    - Change colors in the Colors class
    """
    
    def __init__(self, level_config: LevelConfig):
        self.config = level_config
        self.buildings_far = self._generate_buildings(3, 80, 200)
        self.buildings_mid = self._generate_buildings(4, 100, 300)
        self.buildings_near = self._generate_buildings(5, 150, 400)
        
        # Load and prepare background image if available
        self.bg_image: Optional[pygame.Surface] = None
        self.bg_tiles: List[pygame.Surface] = []
        
        if GRAPHICS.background_image:
            # Scale background to screen height while maintaining aspect ratio
            orig_w, orig_h = GRAPHICS.background_image.get_size()
            scale_factor = CONFIG.SCREEN_HEIGHT / orig_h
            new_w = int(orig_w * scale_factor)
            new_h = CONFIG.SCREEN_HEIGHT
            
            self.bg_image = pygame.transform.scale(
                GRAPHICS.background_image, (new_w, new_h))
            
            # Create tiled versions for seamless scrolling
            # We need enough tiles to cover the level width
            num_tiles = (CONFIG.LEVEL_WIDTH // new_w) + 3
            for i in range(num_tiles):
                self.bg_tiles.append(self.bg_image)
            
            print(f"Background prepared: {new_w}x{new_h}, {num_tiles} tiles")
    
    def _generate_buildings(self, count_per_screen: int, 
                           min_height: int, max_height: int) -> List[dict]:
        """Generate random building positions for a layer."""
        buildings = []
        building_width = CONFIG.SCREEN_WIDTH // count_per_screen
        
        for i in range(count_per_screen * (CONFIG.LEVEL_WIDTH // CONFIG.SCREEN_WIDTH + 2)):
            buildings.append({
                'x': i * building_width + random.randint(-20, 20),
                'width': building_width - random.randint(5, 30),
                'height': random.randint(min_height, max_height),
                'windows': random.randint(2, 5),
            })
        
        return buildings
    
    def draw(self, surface: pygame.Surface, camera_x: int):
        """Draw the parallax background."""
        
        # If we have a custom background image, use it
        if self.bg_image and self.bg_tiles:
            self._draw_image_background(surface, camera_x)
        else:
            # Fallback to procedurally generated background
            self._draw_procedural_background(surface, camera_x)
        
        # Always draw ground on top
        self._draw_ground(surface)
    
    def _draw_image_background(self, surface: pygame.Surface, camera_x: int):
        """Draw the custom background image with parallax scrolling."""
        if not self.bg_image:
            return
        
        img_width = self.bg_image.get_width()
        
        # Parallax effect - background moves slower than foreground
        parallax_x = camera_x * 0.3  # Slow parallax for depth effect
        
        # Calculate which tiles are visible
        start_tile = int(parallax_x // img_width)
        
        # Draw visible tiles
        for i in range(start_tile - 1, start_tile + 3):
            if i >= 0 and i < len(self.bg_tiles):
                tile_x = i * img_width - parallax_x
                if tile_x < CONFIG.SCREEN_WIDTH and tile_x + img_width > 0:
                    surface.blit(self.bg_tiles[i], (int(tile_x), 0))
        
        # Add atmospheric overlay for depth
        overlay = pygame.Surface((CONFIG.SCREEN_WIDTH, CONFIG.SCREEN_HEIGHT))
        overlay.fill((0, 0, 20))  # Slight blue tint
        overlay.set_alpha(30)
        surface.blit(overlay, (0, 0))
    
    def _draw_procedural_background(self, surface: pygame.Surface, camera_x: int):
        """Draw procedurally generated Gotham background."""
        # Sky gradient
        for y in range(CONFIG.SCREEN_HEIGHT):
            progress = y / CONFIG.SCREEN_HEIGHT
            r = int(self.config.background_color[0] * (1 - progress * 0.5))
            g = int(self.config.background_color[1] * (1 - progress * 0.5))
            b = int(self.config.background_color[2] * (1 - progress * 0.3))
            pygame.draw.line(surface, (r, g, b), (0, y), (CONFIG.SCREEN_WIDTH, y))
        
        # Moon
        moon_x = CONFIG.SCREEN_WIDTH - 150 - camera_x * 0.02
        pygame.draw.circle(surface, (220, 220, 200), (int(moon_x), 80), 40)
        pygame.draw.circle(surface, self.config.background_color, 
                          (int(moon_x) + 10, 75), 35)  # Crescent effect
        
        # Far buildings (slowest parallax)
        self._draw_building_layer(surface, self.buildings_far, 
                                  Colors.CITY_DARK, camera_x * 0.2)
        
        # Mid buildings
        self._draw_building_layer(surface, self.buildings_mid,
                                  Colors.CITY_MID, camera_x * 0.5)
        
        # Near buildings
        self._draw_building_layer(surface, self.buildings_near,
                                  Colors.CITY_LIGHT, camera_x * 0.8)
    
    def _draw_ground(self, surface: pygame.Surface):
        """Draw the ground/street."""
        # Main ground
        pygame.draw.rect(surface, (35, 35, 45),
                        (0, CONFIG.GROUND_LEVEL, CONFIG.SCREEN_WIDTH,
                         CONFIG.SCREEN_HEIGHT - CONFIG.GROUND_LEVEL))
        
        # Street line
        pygame.draw.line(surface, (60, 60, 70),
                        (0, CONFIG.GROUND_LEVEL), 
                        (CONFIG.SCREEN_WIDTH, CONFIG.GROUND_LEVEL), 3)
        
        # Street markings
        for x in range(0, CONFIG.SCREEN_WIDTH, 100):
            pygame.draw.rect(surface, (80, 80, 60),
                           (x, CONFIG.GROUND_LEVEL + 20, 40, 4))
    
    def _draw_building_layer(self, surface: pygame.Surface, 
                             buildings: List[dict], color: Tuple[int, int, int],
                             parallax_x: float):
        """Draw a layer of buildings."""
        for building in buildings:
            x = building['x'] - parallax_x
            
            # Skip if off screen
            if x < -building['width'] or x > CONFIG.SCREEN_WIDTH:
                continue
            
            y = CONFIG.GROUND_LEVEL - building['height']
            
            # Building shape
            pygame.draw.rect(surface, color,
                           (x, y, building['width'], building['height']))
            
            # Windows (lit randomly)
            window_size = 6
            window_spacing = 15
            for wy in range(int(y + 10), CONFIG.GROUND_LEVEL - 10, window_spacing):
                for wx in range(int(x + 10), int(x + building['width'] - 10), window_spacing):
                    if random.random() < 0.3:
                        window_color = (255, 255, 150)  # Lit
                    else:
                        window_color = (30, 30, 40)  # Dark
                    pygame.draw.rect(surface, window_color,
                                   (wx, wy, window_size, window_size))

# =============================================================================
# SECTION 9: GAME UI
# =============================================================================

class GameUI:
    """Handles all UI rendering."""
    
    def __init__(self):
        self.fonts = GRAPHICS.fonts
    
    def draw_hud(self, surface: pygame.Surface, player: Player, 
                 level: LevelConfig, boss: Optional[Enemy] = None):
        """Draw the heads-up display."""
        # Player health bar
        self._draw_health_bar(surface, 20, 20, 200, 20, 
                             player.health, player.max_health,
                             "BATMAN")
        
        # Score
        score_text = self.fonts["medium"].render(
            f"SCORE: {player.score:,}", True, Colors.TEXT_PRIMARY)
        surface.blit(score_text, (20, 50))
        
        # Combo counter
        if player.combo_count > 1:
            combo_text = self.fonts["large"].render(
                f"x{player.combo_count} COMBO!", True, Colors.COMBO_TEXT)
            x = CONFIG.SCREEN_WIDTH // 2 - combo_text.get_width() // 2
            # Pulsing effect
            scale = 1.0 + abs(math.sin(pygame.time.get_ticks() / 100)) * 0.2
            scaled_text = pygame.transform.scale(
                combo_text,
                (int(combo_text.get_width() * scale),
                 int(combo_text.get_height() * scale))
            )
            surface.blit(scaled_text, (x, 80))
        
        # Level name
        level_text = self.fonts["small"].render(
            f"LEVEL {level.level_number}: {level.name}", 
            True, Colors.TEXT_SECONDARY)
        surface.blit(level_text, 
                    (CONFIG.SCREEN_WIDTH - level_text.get_width() - 20, 20))
        
        # Boss health bar (if boss is present and alive)
        if boss and boss.state != EntityState.DEAD:
            self._draw_boss_bar(surface, boss)
        
        # Controls hint
        controls = "MOVE: Arrow/WASD | JUMP: Space | PUNCH: Z/J | KICK: X/K | BATARANG: C/L"
        controls_text = self.fonts["tiny"].render(controls, True, Colors.TEXT_SECONDARY)
        surface.blit(controls_text, 
                    (CONFIG.SCREEN_WIDTH // 2 - controls_text.get_width() // 2,
                     CONFIG.SCREEN_HEIGHT - 25))
    
    def _draw_health_bar(self, surface: pygame.Surface, x: int, y: int,
                         width: int, height: int, current: int, maximum: int,
                         label: str = ""):
        """Draw a health bar with label."""
        # Background
        pygame.draw.rect(surface, Colors.HEALTH_BAR_BG,
                        (x, y, width, height))
        
        # Health fill
        fill_width = (current / maximum) * width
        pygame.draw.rect(surface, Colors.HEALTH_BAR,
                        (x, y, fill_width, height))
        
        # Border
        pygame.draw.rect(surface, Colors.TEXT_PRIMARY,
                        (x, y, width, height), 2)
        
        # Label
        if label:
            label_text = self.fonts["small"].render(label, True, Colors.TEXT_PRIMARY)
            surface.blit(label_text, (x + 5, y + 2))
    
    def _draw_boss_bar(self, surface: pygame.Surface, boss: Enemy):
        """Draw the boss health bar at bottom of screen."""
        bar_width = 400
        bar_height = 25
        x = CONFIG.SCREEN_WIDTH // 2 - bar_width // 2
        y = CONFIG.SCREEN_HEIGHT - 80
        
        # Boss name
        name_text = self.fonts["medium"].render(
            boss.config.name, True, (255, 50, 50))
        surface.blit(name_text, 
                    (CONFIG.SCREEN_WIDTH // 2 - name_text.get_width() // 2, y - 35))
        
        # Health bar
        self._draw_health_bar(surface, x, y, bar_width, bar_height,
                             boss.health, boss.max_health)
    
    def draw_title_screen(self, surface: pygame.Surface):
        """Draw the title screen."""
        # Background
        surface.fill(Colors.NIGHT_SKY)
        
        # Title
        title = self.fonts["title"].render("BATMAN", True, Colors.BATMAN_ACCENT)
        subtitle = self.fonts["large"].render("ARKHAM SHADOWS", True, Colors.TEXT_PRIMARY)
        
        title_x = CONFIG.SCREEN_WIDTH // 2 - title.get_width() // 2
        subtitle_x = CONFIG.SCREEN_WIDTH // 2 - subtitle.get_width() // 2
        
        surface.blit(title, (title_x, CONFIG.SCREEN_HEIGHT // 3))
        surface.blit(subtitle, (subtitle_x, CONFIG.SCREEN_HEIGHT // 3 + 70))
        
        # Start prompt
        prompt = self.fonts["medium"].render(
            "Press ENTER to Start", True, Colors.TEXT_SECONDARY)
        prompt_x = CONFIG.SCREEN_WIDTH // 2 - prompt.get_width() // 2
        
        # Blinking effect
        if pygame.time.get_ticks() % 1000 < 500:
            surface.blit(prompt, (prompt_x, CONFIG.SCREEN_HEIGHT * 2 // 3))
        
        # Credits
        credits = self.fonts["small"].render(
            "A tribute to the Arkham series", True, Colors.TEXT_SECONDARY)
        surface.blit(credits, 
                    (CONFIG.SCREEN_WIDTH // 2 - credits.get_width() // 2,
                     CONFIG.SCREEN_HEIGHT - 50))
    
    def draw_game_over(self, surface: pygame.Surface, score: int, won: bool):
        """Draw game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((CONFIG.SCREEN_WIDTH, CONFIG.SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        surface.blit(overlay, (0, 0))
        
        # Result text
        if won:
            result = self.fonts["title"].render("GOTHAM IS SAFE", True, Colors.BATMAN_ACCENT)
        else:
            result = self.fonts["title"].render("GAME OVER", True, (200, 50, 50))
        
        result_x = CONFIG.SCREEN_WIDTH // 2 - result.get_width() // 2
        surface.blit(result, (result_x, CONFIG.SCREEN_HEIGHT // 3))
        
        # Score
        score_text = self.fonts["large"].render(
            f"Final Score: {score:,}", True, Colors.TEXT_PRIMARY)
        score_x = CONFIG.SCREEN_WIDTH // 2 - score_text.get_width() // 2
        surface.blit(score_text, (score_x, CONFIG.SCREEN_HEIGHT // 2))
        
        # Restart prompt
        prompt = self.fonts["medium"].render(
            "Press R to Restart | ESC to Quit", True, Colors.TEXT_SECONDARY)
        prompt_x = CONFIG.SCREEN_WIDTH // 2 - prompt.get_width() // 2
        surface.blit(prompt, (prompt_x, CONFIG.SCREEN_HEIGHT * 2 // 3))
    
    def draw_level_intro(self, surface: pygame.Surface, level: LevelConfig):
        """Draw level introduction screen."""
        # Background
        surface.fill(level.background_color)
        
        # Level title
        title = self.fonts["title"].render(
            f"LEVEL {level.level_number}", True, Colors.TEXT_PRIMARY)
        name = self.fonts["large"].render(level.name, True, Colors.BATMAN_ACCENT)
        desc = self.fonts["medium"].render(level.description, True, Colors.TEXT_SECONDARY)
        
        title_x = CONFIG.SCREEN_WIDTH // 2 - title.get_width() // 2
        name_x = CONFIG.SCREEN_WIDTH // 2 - name.get_width() // 2
        desc_x = CONFIG.SCREEN_WIDTH // 2 - desc.get_width() // 2
        
        surface.blit(title, (title_x, CONFIG.SCREEN_HEIGHT // 3))
        surface.blit(name, (name_x, CONFIG.SCREEN_HEIGHT // 3 + 70))
        surface.blit(desc, (desc_x, CONFIG.SCREEN_HEIGHT // 2 + 30))
        
        # Boss name
        boss_config = ENEMY_CONFIGS.get(level.boss_type)
        if boss_config:
            boss_text = self.fonts["medium"].render(
                f"BOSS: {boss_config.name}", True, (255, 50, 50))
            boss_x = CONFIG.SCREEN_WIDTH // 2 - boss_text.get_width() // 2
            surface.blit(boss_text, (boss_x, CONFIG.SCREEN_HEIGHT * 2 // 3))
    
    def draw_pause_screen(self, surface: pygame.Surface):
        """Draw pause overlay."""
        overlay = pygame.Surface((CONFIG.SCREEN_WIDTH, CONFIG.SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        surface.blit(overlay, (0, 0))
        
        pause_text = self.fonts["title"].render("PAUSED", True, Colors.TEXT_PRIMARY)
        pause_x = CONFIG.SCREEN_WIDTH // 2 - pause_text.get_width() // 2
        surface.blit(pause_text, (pause_x, CONFIG.SCREEN_HEIGHT // 2 - 30))
        
        hint = self.fonts["small"].render(
            "Press P to Resume | ESC to Quit", True, Colors.TEXT_SECONDARY)
        hint_x = CONFIG.SCREEN_WIDTH // 2 - hint.get_width() // 2
        surface.blit(hint, (hint_x, CONFIG.SCREEN_HEIGHT // 2 + 40))

# =============================================================================
# SECTION 10: MAIN GAME CLASS
# =============================================================================

class Game:
    """
    Main game class that manages the entire game state.
    """
    
    def __init__(self):
        """Initialize the game."""
        # Setup display
        self.screen = pygame.display.set_mode(
            (CONFIG.SCREEN_WIDTH, CONFIG.SCREEN_HEIGHT))
        pygame.display.set_caption(CONFIG.TITLE)
        self.clock = pygame.time.Clock()
        
        # NOW load sprites (after display is set up)
        GRAPHICS.load_sprites()
        
        # Game state
        self.state = "title"  # title, playing, paused, level_intro, game_over
        self.running = True
        self.won = False
        
        # Level management
        self.current_level_index = 0
        self.level_intro_timer = 0
        
        # Initialize UI
        self.ui = GameUI()
        
        # Game objects (initialized when game starts)
        self.player: Optional[Player] = None
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []
        self.pickups: List[HealthPickup] = []
        self.boss: Optional[Enemy] = None
        self.background: Optional[Background] = None
        
        # Camera
        self.camera_x = 0
    
    def start_level(self, level_index: int):
        """
        Start a specific level.
        
        Args:
            level_index: Index into LEVEL_CONFIGS
        """
        if level_index >= len(LEVEL_CONFIGS):
            self.won = True
            self.state = "game_over"
            MUSIC.stop_ambient()
            return
        
        self.current_level_index = level_index
        level = LEVEL_CONFIGS[level_index]
        
        # Reset game objects
        self.player = Player(100, CONFIG.GROUND_LEVEL - 100)
        if self.state != "playing":
            self.player.score = 0  # Only reset score on new game
        self.enemies = []
        self.projectiles = []
        self.pickups = []
        self.camera_x = 0
        
        # Create background
        self.background = Background(level)
        
        # Spawn henchmen throughout the level
        henchman_spacing = (CONFIG.LEVEL_WIDTH - 500) // (level.num_henchmen + 1)
        for i in range(level.num_henchmen):
            # Pick random henchman type from level's available types
            henchman_type = random.choice(level.henchman_types)
            config = ENEMY_CONFIGS[henchman_type]
            
            x = 400 + i * henchman_spacing + random.randint(-50, 50)
            y = CONFIG.GROUND_LEVEL - config.height
            
            enemy = Enemy(x, y, config)
            self.enemies.append(enemy)
        
        # Spawn boss at end of level
        boss_config = ENEMY_CONFIGS[level.boss_type]
        boss_x = CONFIG.LEVEL_WIDTH - 300
        boss_y = CONFIG.GROUND_LEVEL - boss_config.height
        self.boss = Enemy(boss_x, boss_y, boss_config)
        self.enemies.append(self.boss)
        
        # Start dark ambient music!
        MUSIC.stop_ambient()
        MUSIC.play_ambient(boss_fight=False)
        
        # Show level intro
        self.state = "level_intro"
        self.level_intro_timer = 180  # 3 seconds
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Global keys
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "paused"
                    else:
                        self.running = False
                
                # Title screen
                elif self.state == "title":
                    if event.key == pygame.K_RETURN:
                        self.start_level(0)
                
                # Pause screen
                elif self.state == "paused":
                    if event.key == pygame.K_p:
                        self.state = "playing"
                
                # Game over
                elif self.state == "game_over":
                    if event.key == pygame.K_r:
                        self.start_level(0)
                
                # Playing
                elif self.state == "playing" and self.player:
                    if event.key == pygame.K_p:
                        self.state = "paused"
                    elif event.key == pygame.K_SPACE:
                        self.player.jump()
                    elif event.key in [pygame.K_z, pygame.K_j]:
                        self.player.punch()
                    elif event.key in [pygame.K_x, pygame.K_k]:
                        self.player.kick()
                    elif event.key in [pygame.K_c, pygame.K_l]:
                        batarang = self.player.throw_batarang()
                        if batarang:
                            self.projectiles.append(batarang)
    
    def update(self):
        """Update game state."""
        if self.state == "level_intro":
            self.level_intro_timer -= 1
            if self.level_intro_timer <= 0:
                self.state = "playing"
            return
        
        if self.state != "playing" or not self.player:
            return
        
        # Get pressed keys for continuous input
        keys = pygame.key.get_pressed()
        
        # Update player
        self.player.handle_input(keys)
        self.player.update()
        
        # Update camera to follow player
        target_camera = self.player.x - CONFIG.SCROLL_THRESHOLD
        target_camera = max(0, min(target_camera, 
                                   CONFIG.LEVEL_WIDTH - CONFIG.SCREEN_WIDTH))
        self.camera_x += (target_camera - self.camera_x) * 0.1
        
        # Update enemies
        for enemy in self.enemies[:]:
            if enemy.state == EntityState.DEAD:
                # Play death sound!
                MUSIC.play_sfx('enemy_death')
                
                # Check if should drop health
                if random.random() < enemy.config.health_drop_chance:
                    pickup = HealthPickup(enemy.x, enemy.y)
                    self.pickups.append(pickup)
                
                # Add score
                self.player.score += enemy.config.score_value
                self.enemies.remove(enemy)
                
                # Check if boss was defeated
                if enemy == self.boss:
                    # Proceed to next level
                    next_level = self.current_level_index + 1
                    if next_level >= len(LEVEL_CONFIGS):
                        self.won = True
                        self.state = "game_over"
                        MUSIC.stop_ambient()
                    else:
                        # Preserve score for next level
                        score = self.player.score
                        self.start_level(next_level)
                        if self.player:
                            self.player.score = score
                continue
            
            # Check if player is near boss - switch to intense music
            if enemy == self.boss and enemy.state != EntityState.DEAD:
                distance_to_boss = abs(self.player.x - enemy.x)
                if distance_to_boss < 400:
                    # Switch to boss music when approaching
                    if MUSIC.current_music != 'boss_drone':
                        MUSIC.stop_ambient()
                        MUSIC.play_ambient(boss_fight=True)
            
            # Update enemy and collect any projectiles
            enemy_projectile = enemy.update(self.player)
            if enemy_projectile:
                self.projectiles.append(enemy_projectile)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)
                continue
            
            # Check collisions
            proj_rect = projectile.get_rect()
            
            if projectile.owner_is_player:
                # Player projectile hitting enemies
                for enemy in self.enemies:
                    if enemy.state != EntityState.DEAD:
                        if proj_rect.colliderect(enemy.get_rect()):
                            direction = 1 if projectile.velocity_x > 0 else -1
                            enemy.take_damage(projectile.damage, direction)
                            self.player.register_hit()
                            projectile.active = False
                            break
            else:
                # Enemy projectile hitting player
                if proj_rect.colliderect(self.player.get_rect()):
                    direction = 1 if projectile.velocity_x > 0 else -1
                    self.player.take_damage(projectile.damage, direction)
                    projectile.active = False
        
        # Check player melee attacks hitting enemies
        player_attack_rect = self.player.get_attack_rect()
        if player_attack_rect and self.player.attack_duration == self.player.attack_duration:
            for enemy in self.enemies:
                if enemy.state != EntityState.DEAD:
                    if player_attack_rect.colliderect(enemy.get_rect()):
                        direction = 1 if self.player.facing_right else -1
                        damage = self.player.get_attack_damage()
                        enemy.take_damage(damage, direction)
                        self.player.register_hit()
        
        # Check enemy attacks hitting player
        for enemy in self.enemies:
            if enemy.state == EntityState.DEAD:
                continue
            enemy_attack_rect = enemy.get_attack_rect()
            if enemy_attack_rect:
                if enemy_attack_rect.colliderect(self.player.get_rect()):
                    direction = 1 if enemy.facing_right else -1
                    self.player.take_damage(enemy.config.damage, direction)
        
        # Update and check pickups
        for pickup in self.pickups[:]:
            pickup.update()
            if not pickup.active:
                self.pickups.remove(pickup)
                continue
            
            if pickup.get_rect().colliderect(self.player.get_rect()):
                self.player.health = min(self.player.max_health,
                                        self.player.health + pickup.heal_amount)
                self.pickups.remove(pickup)
        
        # Check player death
        if self.player.state == EntityState.DEAD:
            self.won = False
            self.state = "game_over"
    
    def draw(self):
        """Draw everything."""
        if self.state == "title":
            self.ui.draw_title_screen(self.screen)
        
        elif self.state == "level_intro":
            level = LEVEL_CONFIGS[self.current_level_index]
            self.ui.draw_level_intro(self.screen, level)
        
        elif self.state in ["playing", "paused"] and self.player:
            # Draw background
            if self.background:
                self.background.draw(self.screen, int(self.camera_x))
            
            # Draw pickups
            for pickup in self.pickups:
                pickup.draw(self.screen, int(self.camera_x))
            
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen, int(self.camera_x))
            
            # Draw player
            self.player.draw(self.screen, int(self.camera_x))
            
            # Draw projectiles
            for projectile in self.projectiles:
                projectile.draw(self.screen, int(self.camera_x))
            
            # Draw UI
            level = LEVEL_CONFIGS[self.current_level_index]
            living_boss = self.boss if self.boss and self.boss.state != EntityState.DEAD else None
            self.ui.draw_hud(self.screen, self.player, level, living_boss)
            
            # Draw pause overlay if paused
            if self.state == "paused":
                self.ui.draw_pause_screen(self.screen)
        
        elif self.state == "game_over":
            # Draw the last game frame behind the game over screen
            if self.background:
                self.background.draw(self.screen, int(self.camera_x))
            score = self.player.score if self.player else 0
            self.ui.draw_game_over(self.screen, score, self.won)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(CONFIG.FPS)
        
        pygame.quit()

# =============================================================================
# SECTION 11: MAIN ENTRY POINT
# =============================================================================

def main():
    """
    Main function to start the game.
    
    CUSTOMIZATION QUICK REFERENCE:
    -----------------------------
    1. To change Batman's stats:
       - Modify the PlayerStats class (line ~80)
       
    2. To add/modify enemies:
       - Add new entries to ENEMY_CONFIGS dictionary (line ~160)
       
    3. To change level progression:
       - Modify LEVEL_CONFIGS list (line ~280)
       
    4. To use custom sprites:
       - Set GraphicsManager.USE_CUSTOM_SPRITES = True
       - Add your sprite paths to SPRITE_PATHS dictionary
       
    5. To change colors:
       - Modify the Colors class (line ~60)
       
    6. To adjust game physics:
       - Modify GameConfig class (line ~50)
    """
    print("=" * 60)
    print("BATMAN: ARKHAM SHADOWS")
    print("=" * 60)
    print("\nStarting game...")
    print("\nCONTROLS:")
    print("  Arrow Keys / WASD  : Move")
    print("  SPACE              : Jump (double jump available)")
    print("  Z / J              : Punch")
    print("  X / K              : Kick")
    print("  C / L              : Throw Batarang")
    print("  P                  : Pause")
    print("  ESC                : Quit")
    print("\nDefeat all enemies and bosses to save Gotham!")
    print("=" * 60)
    
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
