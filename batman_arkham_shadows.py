#!/usr/bin/env python3
"""
=============================================================================
BATMAN: ARKHAM SHADOWS - 2D Side-Scrolling Beat 'Em Up
=============================================================================

VERSION 2.0 - VILLAIN TERRITORIES UPDATE

Features:
- 7 Unique villain territories with custom backgrounds
- Sprite sheet auto-splitting for villain animations
- Unique fighting styles per villain
- State-driven animation system
- Dark Knight inspired music

VILLAIN PROGRESSION:
1. Two-Face (Coin-flip attacks)
2. Joker (Erratic, unpredictable)
3. Penguin (Umbrella ranged attacks)
4. Scarecrow (Fear toxin special)
5. Killer Croc (Heavy melee, grabs)
6. Bane (Multi-phase, Venom boost)
7. Deathstroke (Counter master, final boss)

CONTROLS:
    Arrow Keys / WASD  : Move Batman
    SPACE              : Jump
    Z / J              : Punch
    X / K              : Kick
    C / L              : Throw Batarang
    P                  : Pause Game
    R                  : Restart (when game over)
    ESC                : Quit

Author: Claude (Anthropic AI)
=============================================================================
"""

import pygame
import random
import math
import os
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Initialize Pygame
pygame.init()

# Initialize audio
AUDIO_AVAILABLE = False
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    AUDIO_AVAILABLE = True
except pygame.error:
    print("Note: Audio not available")

# =============================================================================
# GAME CONFIGURATION
# =============================================================================

@dataclass
class GameConfig:
    """Central game configuration."""
    SCREEN_WIDTH: int = 1280
    SCREEN_HEIGHT: int = 720
    FPS: int = 60
    TITLE: str = "BATMAN: ARKHAM SHADOWS"
    GRAVITY: float = 0.8
    GROUND_LEVEL: int = 580
    LEVEL_WIDTH: int = 6000

CONFIG = GameConfig()

# =============================================================================
# VILLAIN DEFINITIONS - The 7 territories of Gotham
# =============================================================================

class VillainType(Enum):
    """The 7 villains in order of progression."""
    TWOFACE = "twoface"
    JOKER = "joker"
    PENGUIN = "penguin"
    SCARECROW = "scarecrow"
    CROC = "croc"
    BANE = "bane"
    DEATHSTROKE = "deathstroke"

# Villain order for level progression
VILLAIN_ORDER = [
    VillainType.TWOFACE,
    VillainType.JOKER,
    VillainType.PENGUIN,
    VillainType.SCARECROW,
    VillainType.CROC,
    VillainType.BANE,
    VillainType.DEATHSTROKE,
]

@dataclass
class VillainConfig:
    """Configuration for each villain."""
    name: str
    display_name: str
    territory_name: str
    health: int
    damage: int
    speed: float
    attack_range: int
    attack_cooldown: int
    width: int
    height: int
    
    # Special abilities
    can_block: bool = False
    can_dodge: bool = False
    can_counter: bool = False
    has_projectile: bool = False
    projectile_damage: int = 0
    has_special: bool = False
    special_damage: int = 0
    
    # Multi-phase boss
    phases: int = 1
    
    # AI behavior
    aggression: float = 0.5
    
    # Rewards
    score_value: int = 5000
    num_henchmen: int = 8

# =============================================================================
# VILLAIN CONFIGURATIONS - Unique fighting styles
# =============================================================================

VILLAIN_CONFIGS: Dict[VillainType, VillainConfig] = {
    VillainType.TWOFACE: VillainConfig(
        name="twoface",
        display_name="TWO-FACE",
        territory_name="THE COURTS",
        health=500,
        damage=25,
        speed=3.5,
        attack_range=80,
        attack_cooldown=40,
        width=70,
        height=100,
        has_projectile=True,      # Dual pistols
        projectile_damage=18,
        can_block=True,
        aggression=0.6,
        score_value=5000,
        num_henchmen=8,
    ),
    
    VillainType.JOKER: VillainConfig(
        name="joker",
        display_name="THE JOKER",
        territory_name="ACE CHEMICALS",
        health=550,
        damage=22,
        speed=4.0,
        attack_range=75,
        attack_cooldown=35,
        width=65,
        height=100,
        can_dodge=True,           # Erratic movement
        has_projectile=True,      # Joker toxin
        projectile_damage=15,
        has_special=True,         # Fake attack
        aggression=0.7,
        score_value=6000,
        num_henchmen=10,
    ),
    
    VillainType.PENGUIN: VillainConfig(
        name="penguin",
        display_name="THE PENGUIN",
        territory_name="ICEBERG LOUNGE",
        health=450,
        damage=20,
        speed=2.5,
        attack_range=120,         # Umbrella reach
        attack_cooldown=45,
        width=70,
        height=85,
        has_projectile=True,      # Umbrella gun
        projectile_damage=20,
        aggression=0.5,
        score_value=5500,
        num_henchmen=10,
    ),
    
    VillainType.SCARECROW: VillainConfig(
        name="scarecrow",
        display_name="SCARECROW",
        territory_name="ARKHAM ASYLUM",
        health=480,
        damage=24,
        speed=3.8,
        attack_range=90,
        attack_cooldown=38,
        width=65,
        height=105,
        can_dodge=True,
        has_projectile=True,      # Fear toxin
        projectile_damage=12,
        has_special=True,         # Fear cloud
        special_damage=30,
        aggression=0.65,
        score_value=6000,
        num_henchmen=9,
    ),
    
    VillainType.CROC: VillainConfig(
        name="croc",
        display_name="KILLER CROC",
        territory_name="GOTHAM SEWERS",
        health=900,               # Very tanky
        damage=45,                # Heavy hitter
        speed=2.2,                # Slow
        attack_range=100,
        attack_cooldown=55,
        width=90,
        height=120,
        can_block=True,
        has_special=True,         # Grab attack
        special_damage=60,
        aggression=0.8,
        score_value=7000,
        num_henchmen=6,
    ),
    
    VillainType.BANE: VillainConfig(
        name="bane",
        display_name="BANE",
        territory_name="SANTA PRISCA",
        health=1000,
        damage=50,
        speed=2.5,
        attack_range=110,
        attack_cooldown=50,
        width=95,
        height=125,
        can_block=True,
        has_special=True,         # Venom boost
        special_damage=70,
        phases=2,                 # Venom phase
        aggression=0.85,
        score_value=8000,
        num_henchmen=7,
    ),
    
    VillainType.DEATHSTROKE: VillainConfig(
        name="deathstroke",
        display_name="DEATHSTROKE",
        territory_name="MILITIA HQ",
        health=850,
        damage=40,
        speed=5.5,                # Very fast
        attack_range=100,
        attack_cooldown=25,       # Fast attacks
        width=75,
        height=105,
        can_block=True,
        can_dodge=True,
        can_counter=True,         # Counter attacks!
        has_projectile=True,
        projectile_damage=25,
        phases=3,                 # Multiple phases
        aggression=0.95,
        score_value=10000,
        num_henchmen=12,
    ),
}

# =============================================================================
# PLAYER (BATMAN) CONFIGURATION
# =============================================================================

@dataclass
class PlayerStats:
    """Batman's combat statistics."""
    MAX_HEALTH: int = 150
    MAX_LIVES: int = 3              # 3 lives!
    MOVE_SPEED: float = 7.0
    JUMP_POWER: float = -19.0
    DOUBLE_JUMP_POWER: float = -16.0
    MAX_JUMPS: int = 2
    
    PUNCH_DAMAGE: int = 35
    KICK_DAMAGE: int = 45
    BATARANG_DAMAGE: int = 25
    
    PUNCH_RANGE: int = 75
    KICK_RANGE: int = 90
    BATARANG_SPEED: float = 18.0
    BATARANG_MAX_DISTANCE: int = 600
    
    PUNCH_COOLDOWN: int = 10
    KICK_COOLDOWN: int = 18
    BATARANG_COOLDOWN: int = 30
    
    HIT_INVINCIBILITY: int = 45
    COMBO_WINDOW: int = 100
    COMBO_DAMAGE_BONUS: float = 0.15
    MAX_COMBO_MULTIPLIER: float = 2.5
    
    RESPAWN_INVINCIBILITY: int = 120  # 2 seconds of invincibility after respawn

PLAYER_STATS = PlayerStats()

# =============================================================================
# ENTITY STATES
# =============================================================================

class EntityState(Enum):
    """States for all game entities."""
    IDLE = auto()
    RUNNING = auto()
    JUMPING = auto()
    FALLING = auto()
    PUNCHING = auto()
    KICKING = auto()
    THROWING = auto()
    BLOCKING = auto()
    HIT = auto()
    DEAD = auto()
    SPECIAL = auto()

class AttackType(Enum):
    """Types of attacks."""
    NONE = auto()
    PUNCH = auto()
    KICK = auto()
    BATARANG = auto()
    PROJECTILE = auto()
    SPECIAL = auto()

# =============================================================================
# SPRITE SHEET SPLITTER - Automatically splits villain sprite sheets
# =============================================================================

class SpriteSheetSplitter:
    """
    Splits a 2x2 or 2x3 sprite sheet into individual animation frames.
    
    Expected layout for villain sprites:
    ┌─────────┬─────────┐
    │  KICK   │  PUNCH  │
    ├─────────┼─────────┤
    │  JUMP   │   RUN   │
    └─────────┴─────────┘
    
    Or for 2x3:
    ┌─────────┬─────────┬─────────┐
    │  KICK   │  PUNCH  │ SPECIAL │
    ├─────────┼─────────┼─────────┤
    │  JUMP   │   RUN   │  IDLE   │
    └─────────┴─────────┴─────────┘
    """
    
    @staticmethod
    def detect_grid(image: pygame.Surface) -> Tuple[int, int]:
        """Detect if image is 2x2, 2x3, or other grid layout."""
        width, height = image.get_size()
        aspect = width / height
        
        if aspect > 1.4:  # Wide image - likely 2x3 or 3x2
            if width > height:
                return (3, 2)  # 3 columns, 2 rows
            else:
                return (2, 3)
        else:  # Square-ish - likely 2x2
            return (2, 2)
    
    @staticmethod
    def split_sprite_sheet(image: pygame.Surface, 
                           cols: int = None, 
                           rows: int = None) -> Dict[str, pygame.Surface]:
        """
        Split a sprite sheet into named animation frames.
        
        Returns dict with keys: 'kick', 'punch', 'jump', 'run', 'idle', 'special'
        """
        if cols is None or rows is None:
            cols, rows = SpriteSheetSplitter.detect_grid(image)
        
        width, height = image.get_size()
        frame_w = width // cols
        frame_h = height // rows
        
        frames = {}
        
        # Define frame positions based on grid size
        if cols == 2 and rows == 2:
            # 2x2 layout
            frame_map = {
                'kick': (0, 0),
                'punch': (1, 0),
                'jump': (0, 1),
                'run': (1, 1),
            }
        elif cols == 3 and rows == 2:
            # 3x2 layout  
            frame_map = {
                'kick': (0, 0),
                'punch': (1, 0),
                'special': (2, 0),
                'jump': (0, 1),
                'run': (1, 1),
                'idle': (2, 1),
            }
        elif cols == 2 and rows == 3:
            # 2x3 layout
            frame_map = {
                'kick': (0, 0),
                'punch': (1, 0),
                'jump': (0, 1),
                'run': (1, 1),
                'idle': (0, 2),
                'special': (1, 2),
            }
        else:
            # Default - just number them
            frame_map = {}
            idx = 0
            names = ['kick', 'punch', 'jump', 'run', 'idle', 'special']
            for row in range(rows):
                for col in range(cols):
                    if idx < len(names):
                        frame_map[names[idx]] = (col, row)
                        idx += 1
        
        # Extract frames
        for name, (col, row) in frame_map.items():
            x = col * frame_w
            y = row * frame_h
            
            # Create surface for this frame
            frame_surface = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
            frame_surface.blit(image, (0, 0), (x, y, frame_w, frame_h))
            
            frames[name] = frame_surface
        
        # Ensure we have all needed frames (use fallbacks)
        needed = ['kick', 'punch', 'jump', 'run', 'idle']
        for key in needed:
            if key not in frames:
                # Use any available frame as fallback
                fallback = list(frames.values())[0] if frames else None
                if fallback:
                    frames[key] = fallback
        
        return frames

# =============================================================================
# GRAPHICS MANAGER
# =============================================================================

class GraphicsManager:
    """
    Manages all game graphics with automatic sprite sheet splitting.
    
    Asset naming convention:
    - Backgrounds: sprites/backgrounds/{villain_name}.jpg
    - Villains: sprites/villains/{villain_name}.png (sprite sheet)
    - Batman: sprites/batman/{action}.png
    """
    
    SPRITES_PATH = "sprites"
    
    def __init__(self):
        self.loaded = False
        self.batman_sprites: Dict[str, pygame.Surface] = {}
        self.villain_animations: Dict[str, Dict[str, pygame.Surface]] = {}
        self.backgrounds: Dict[str, pygame.Surface] = {}
        self.henchman_sprite: Optional[pygame.Surface] = None
        self.fonts: Dict[str, pygame.font.Font] = {}
        self._sprite_cache: Dict[tuple, pygame.Surface] = {}  # Cache for processed sprites
        
        self._load_fonts()
    
    def _load_fonts(self):
        """Load game fonts."""
        try:
            self.fonts["title"] = pygame.font.Font(None, 80)
            self.fonts["large"] = pygame.font.Font(None, 56)
            self.fonts["medium"] = pygame.font.Font(None, 40)
            self.fonts["small"] = pygame.font.Font(None, 28)
            self.fonts["tiny"] = pygame.font.Font(None, 20)
        except Exception:
            for name, size in [("title", 70), ("large", 48), ("medium", 34), ("small", 24), ("tiny", 18)]:
                self.fonts[name] = pygame.font.SysFont("Arial", size)
    
    def clear_cache(self):
        """Clear sprite cache to free memory."""
        self._sprite_cache.clear()
    
    def load_all(self):
        """Load all sprites after display is initialized."""
        if self.loaded:
            return
        
        print("\n=== Loading Game Assets ===")
        
        # Load Batman sprites
        self._load_batman_sprites()
        
        # Load villain sprite sheets and split them
        self._load_villain_sprites()
        
        # Load backgrounds (named after villains)
        self._load_backgrounds()
        
        # Load henchman
        self._load_henchman()
        
        self.loaded = True
        print("=== Asset Loading Complete ===\n")
    
    def _load_batman_sprites(self):
        """Load Batman's animation sprites."""
        batman_path = os.path.join(self.SPRITES_PATH, "batman")
        
        sprite_files = {
            'idle': ['idle.jpg', 'idle.png'],
            'run': ['run.png', 'run.jpg'],
            'jump': ['jump.png', 'jump.jpg'],
            'punch': ['punch.png', 'punch.jpg'],
            'kick': ['kick.png', 'kick.jpg'],
        }
        
        for action, filenames in sprite_files.items():
            for filename in filenames:
                path = os.path.join(batman_path, filename)
                if os.path.exists(path):
                    try:
                        self.batman_sprites[action] = pygame.image.load(path).convert_alpha()
                        print(f"  ✓ Batman {action}")
                        break
                    except Exception as e:
                        print(f"  ✗ Error loading Batman {action}: {e}")
        
        # Use idle as fallback for missing sprites
        if 'idle' in self.batman_sprites:
            for action in sprite_files.keys():
                if action not in self.batman_sprites:
                    self.batman_sprites[action] = self.batman_sprites['idle']
    
    def _load_villain_sprites(self):
        """Load and split villain sprite sheets."""
        villain_path = os.path.join(self.SPRITES_PATH, "villains")
        
        for villain_type in VillainType:
            name = villain_type.value
            
            # Try different extensions
            for ext in ['.png', '.jpg', '.jpeg']:
                path = os.path.join(villain_path, f"{name}{ext}")
                if os.path.exists(path):
                    try:
                        sheet = pygame.image.load(path).convert_alpha()
                        # Split into animation frames
                        self.villain_animations[name] = SpriteSheetSplitter.split_sprite_sheet(sheet)
                        print(f"  ✓ Villain {name} (split into {len(self.villain_animations[name])} frames)")
                        break
                    except Exception as e:
                        print(f"  ✗ Error loading villain {name}: {e}")
    
    def _load_backgrounds(self):
        """Load backgrounds (named after villains)."""
        bg_path = os.path.join(self.SPRITES_PATH, "backgrounds")
        
        for villain_type in VillainType:
            name = villain_type.value
            
            for ext in ['.jpg', '.png', '.jpeg', '.avif']:
                path = os.path.join(bg_path, f"{name}{ext}")
                if os.path.exists(path):
                    try:
                        bg = pygame.image.load(path).convert()
                        # Scale to screen height
                        scale_factor = CONFIG.SCREEN_HEIGHT / bg.get_height()
                        new_w = int(bg.get_width() * scale_factor)
                        self.backgrounds[name] = pygame.transform.scale(bg, (new_w, CONFIG.SCREEN_HEIGHT))
                        print(f"  ✓ Background {name}")
                        break
                    except Exception as e:
                        print(f"  ✗ Error loading background {name}: {e}")
    
    def _load_henchman(self):
        """Load henchman sprite."""
        path = os.path.join(self.SPRITES_PATH, "henchmen", "soldier.jpg")
        if os.path.exists(path):
            try:
                self.henchman_sprite = pygame.image.load(path).convert_alpha()
                print(f"  ✓ Henchman sprite")
            except Exception as e:
                print(f"  ✗ Error loading henchman: {e}")
    
    def get_batman_sprite(self, action: str) -> Optional[pygame.Surface]:
        """Get Batman sprite for an action."""
        return self.batman_sprites.get(action, self.batman_sprites.get('idle'))
    
    def get_villain_sprite(self, villain_name: str, action: str) -> Optional[pygame.Surface]:
        """Get villain sprite for specific action."""
        if villain_name in self.villain_animations:
            frames = self.villain_animations[villain_name]
            return frames.get(action, frames.get('idle', list(frames.values())[0] if frames else None))
        return None
    
    def get_background(self, villain_name: str) -> Optional[pygame.Surface]:
        """Get background for a villain's territory."""
        return self.backgrounds.get(villain_name)
    
    def draw_sprite(self, surface: pygame.Surface, sprite: pygame.Surface,
                    x: int, y: int, width: int, height: int, 
                    facing_right: bool = True, remove_bg: bool = True):
        """Draw a sprite with scaling and cached background removal."""
        if sprite is None:
            return
        
        # Create cache key
        cache_key = (id(sprite), width, height, facing_right)
        
        # Check cache first
        if cache_key in self._sprite_cache:
            surface.blit(self._sprite_cache[cache_key], (x, y))
            return
        
        # Scale
        scaled = pygame.transform.scale(sprite, (width, height))
        
        # Flip if facing left
        if not facing_right:
            scaled = pygame.transform.flip(scaled, True, False)
        
        # Advanced background removal for more natural look
        if remove_bg:
            scaled = self._remove_background_fast(scaled)
        
        # Cache the result
        self._sprite_cache[cache_key] = scaled
        
        surface.blit(scaled, (x, y))
    
    def _remove_background_fast(self, sprite: pygame.Surface) -> pygame.Surface:
        """
        Fast background removal - removes white and light backgrounds.
        Optimized for performance.
        """
        result = sprite.convert_alpha()
        
        try:
            # Sample corners to find background color
            w, h = result.get_size()
            
            # Get corner colors
            corners = []
            for pos in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]:
                try:
                    c = result.get_at(pos)
                    corners.append((c[0], c[1], c[2]))
                except:
                    pass
            
            pixels = pygame.PixelArray(result)
            
            # Remove pure white and near-white
            for t in range(240, 256):
                pixels.replace((t, t, t), (0, 0, 0, 0))
            
            # Remove light grays
            for t in range(220, 240):
                pixels.replace((t, t, t), (0, 0, 0, 0))
            
            # Remove detected corner colors (likely background)
            for bg in corners:
                if bg[0] > 200 and bg[1] > 200 and bg[2] > 200:
                    # It's a light color, remove it with some tolerance
                    for offset in range(0, 20, 4):
                        r = max(0, bg[0] - offset)
                        g = max(0, bg[1] - offset)
                        b = max(0, bg[2] - offset)
                        pixels.replace((r, g, b), (0, 0, 0, 0))
            
            del pixels
            
        except Exception:
            pass
        
        return result

# Create global instance
GRAPHICS = GraphicsManager()

# =============================================================================
# DARK KNIGHT MUSIC SYSTEM - Hans Zimmer Inspired
# =============================================================================

class DarkKnightMusic:
    """
    Generates dark atmospheric music inspired by Hans Zimmer's Dark Knight score.
    Features the iconic low drones, rising tension, and powerful brass-like tones.
    """
    
    def __init__(self):
        self.enabled = AUDIO_AVAILABLE
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_music = None
        self.music_volume = 0.5
        self.sfx_volume = 0.6
        self.music_channel: Optional[pygame.mixer.Channel] = None
        self.bass_channel: Optional[pygame.mixer.Channel] = None
        
        if self.enabled:
            try:
                pygame.mixer.set_num_channels(16)
                self.music_channel = pygame.mixer.Channel(0)
                self.bass_channel = pygame.mixer.Channel(1)
                self._generate_sounds()
            except:
                self.enabled = False
    
    def _generate_wave(self, frequency: float, duration: float, 
                       volume: float = 0.3, wave_type: str = "dark",
                       fade_in: float = 0.1, fade_out: float = 0.2) -> Optional[pygame.mixer.Sound]:
        """Generate different types of atmospheric waves."""
        if not self.enabled:
            return None
        
        try:
            import array
            sample_rate = 44100
            n_samples = int(sample_rate * duration)
            buf = array.array('h')
            max_amp = int(32767 * volume)
            
            for i in range(n_samples):
                t = i / sample_rate
                progress = i / n_samples
                
                if wave_type == "dark":
                    # Dark Knight iconic drone - layered low frequencies
                    wave = math.sin(2 * math.pi * frequency * t)  # Base
                    wave += 0.6 * math.sin(2 * math.pi * (frequency * 0.5) * t)  # Sub octave
                    wave += 0.4 * math.sin(2 * math.pi * (frequency * 1.5) * t)  # Fifth
                    wave += 0.3 * math.sin(2 * math.pi * (frequency * 2) * t)  # Octave up
                    wave += 0.15 * math.sin(2 * math.pi * (frequency * 0.25) * t)  # Deep sub
                    # Add subtle pulsing
                    pulse = 1 + 0.15 * math.sin(2 * math.pi * 0.25 * t)
                    wave *= pulse
                    wave /= 2.5
                    
                elif wave_type == "tension":
                    # Rising tension - dissonant intervals
                    wave = math.sin(2 * math.pi * frequency * t)
                    wave += 0.5 * math.sin(2 * math.pi * (frequency * 1.06) * t)  # Minor 2nd
                    wave += 0.4 * math.sin(2 * math.pi * (frequency * 1.5) * t)
                    # Slow LFO modulation
                    mod = 1 + 0.2 * math.sin(2 * math.pi * 0.1 * t)
                    wave *= mod
                    wave /= 2.0
                    
                elif wave_type == "boss":
                    # Aggressive boss music - powerful and driving
                    wave = math.sin(2 * math.pi * frequency * t)
                    wave += 0.7 * math.sin(2 * math.pi * (frequency * 0.5) * t)  # Power
                    wave += 0.5 * math.sin(2 * math.pi * (frequency * 2) * t)
                    wave += 0.3 * math.sin(2 * math.pi * (frequency * 3) * t)  # Brightness
                    # Rhythmic pulse (like heartbeat)
                    beat = abs(math.sin(2 * math.pi * 1.2 * t)) ** 0.5
                    wave *= (0.7 + 0.3 * beat)
                    wave /= 2.5
                    
                elif wave_type == "hit":
                    # Impact sound
                    decay = math.exp(-t * 15)
                    wave = math.sin(2 * math.pi * frequency * t) * decay
                    wave += 0.5 * math.sin(2 * math.pi * (frequency * 0.5) * t) * decay
                    
                elif wave_type == "whoosh":
                    # Batarang whoosh - frequency sweep
                    sweep_freq = frequency * (1 + t * 2)
                    wave = math.sin(2 * math.pi * sweep_freq * t)
                    decay = math.exp(-t * 5)
                    wave *= decay
                    
                else:  # Simple sine
                    wave = math.sin(2 * math.pi * frequency * t)
                
                # Apply envelope
                envelope = 1.0
                if progress < fade_in:
                    envelope = progress / fade_in
                elif progress > (1 - fade_out):
                    envelope = (1 - progress) / fade_out
                
                sample = int(wave * envelope * max_amp)
                sample = max(-32767, min(32767, sample))
                buf.append(sample)
                buf.append(sample)
            
            return pygame.mixer.Sound(buffer=buf)
        except Exception as e:
            print(f"Audio gen error: {e}")
            return None
    
    def _generate_sounds(self):
        """Generate all Dark Knight inspired sounds."""
        print("Generating Dark Knight audio...")
        
        # Main ambient drone (A1 = 55Hz) - the iconic low rumble
        self.sounds['ambient'] = self._generate_wave(
            frequency=55, duration=10.0, volume=0.35,
            wave_type="dark", fade_in=1.0, fade_out=2.0
        )
        
        # Boss fight music - more intense
        self.sounds['boss'] = self._generate_wave(
            frequency=45, duration=8.0, volume=0.4,
            wave_type="boss", fade_in=0.5, fade_out=1.5
        )
        
        # Tension layer
        self.sounds['tension'] = self._generate_wave(
            frequency=110, duration=6.0, volume=0.2,
            wave_type="tension", fade_in=0.5, fade_out=1.0
        )
        
        # Combat sounds
        self.sounds['hit'] = self._generate_wave(
            frequency=80, duration=0.15, volume=0.5,
            wave_type="hit", fade_in=0.01, fade_out=0.1
        )
        
        self.sounds['punch'] = self._generate_wave(
            frequency=100, duration=0.12, volume=0.45,
            wave_type="hit", fade_in=0.01, fade_out=0.08
        )
        
        self.sounds['kick'] = self._generate_wave(
            frequency=65, duration=0.18, volume=0.5,
            wave_type="hit", fade_in=0.01, fade_out=0.12
        )
        
        self.sounds['batarang'] = self._generate_wave(
            frequency=300, duration=0.25, volume=0.35,
            wave_type="whoosh", fade_in=0.02, fade_out=0.2
        )
        
        self.sounds['death'] = self._generate_wave(
            frequency=40, duration=0.6, volume=0.4,
            wave_type="dark", fade_in=0.01, fade_out=0.5
        )
        
        self.sounds['hurt'] = self._generate_wave(
            frequency=120, duration=0.2, volume=0.35,
            wave_type="hit", fade_in=0.01, fade_out=0.15
        )
        
        print("Dark Knight audio ready!")
    
    def play_ambient(self, boss: bool = False):
        """Start playing ambient music loop."""
        if not self.enabled:
            return
        
        self.stop_ambient()
        
        key = 'boss' if boss else 'ambient'
        if key in self.sounds and self.sounds[key]:
            self.sounds[key].set_volume(self.music_volume)
            if self.music_channel:
                self.music_channel.play(self.sounds[key], loops=-1)
            else:
                self.sounds[key].play(loops=-1)
            self.current_music = key
            
            # Layer tension track for boss
            if boss and 'tension' in self.sounds and self.sounds['tension']:
                self.sounds['tension'].set_volume(self.music_volume * 0.5)
                if self.bass_channel:
                    self.bass_channel.play(self.sounds['tension'], loops=-1)
    
    def stop_ambient(self):
        """Stop all ambient music."""
        if not self.enabled:
            return
        
        if self.music_channel:
            self.music_channel.stop()
        if self.bass_channel:
            self.bass_channel.stop()
        
        if self.current_music and self.current_music in self.sounds:
            try:
                self.sounds[self.current_music].stop()
            except:
                pass
        
        if 'tension' in self.sounds:
            try:
                self.sounds['tension'].stop()
            except:
                pass
        
        self.current_music = None
    
    def play_sfx(self, name: str):
        """Play a sound effect."""
        if not self.enabled:
            return
        
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].set_volume(self.sfx_volume)
            self.sounds[name].play()
    
    def set_volume(self, music: float = None, sfx: float = None):
        """Set volume levels."""
        if music is not None:
            self.music_volume = max(0.0, min(1.0, music))
        if sfx is not None:
            self.sfx_volume = max(0.0, min(1.0, sfx))

MUSIC = DarkKnightMusic()

# =============================================================================
# PROJECTILE CLASS
# =============================================================================

class Projectile:
    """Projectile for batarangs and enemy attacks."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float,
                 damage: int, from_player: bool, max_dist: int = 500):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.from_player = from_player
        self.max_dist = max_dist
        self.traveled = 0
        self.active = True
        self.angle = 0
        self.width = 20
        self.height = 10
    
    def update(self):
        """Update projectile."""
        if not self.active:
            return
        self.x += self.vx
        self.y += self.vy
        self.traveled += abs(self.vx)
        self.angle += 12
        if self.traveled > self.max_dist:
            self.active = False
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rect."""
        return pygame.Rect(self.x - 10, self.y - 5, self.width, self.height)
    
    def draw(self, surface: pygame.Surface, camera_x: int):
        """Draw projectile."""
        if not self.active:
            return
        sx = self.x - camera_x
        # Draw batarang shape
        points = [(sx, self.y - 5), (sx - 12, self.y), (sx - 4, self.y + 3),
                  (sx, self.y + 7), (sx + 4, self.y + 3), (sx + 12, self.y)]
        cos_a = math.cos(math.radians(self.angle))
        sin_a = math.sin(math.radians(self.angle))
        rotated = []
        for px, py in points:
            dx, dy = px - sx, py - self.y
            rotated.append((sx + dx * cos_a - dy * sin_a, self.y + dx * sin_a + dy * cos_a))
        pygame.draw.polygon(surface, (40, 40, 40), rotated)

# =============================================================================
# BASE ENTITY CLASS
# =============================================================================

class Entity:
    """Base class for all game entities."""
    
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = 0.0
        self.vy = 0.0
        self.facing_right = True
        self.state = EntityState.IDLE
        self.health = 100
        self.max_health = 100
        self.invincibility = 0
        self.attack_cooldown = 0
        self.current_attack = AttackType.NONE
        self.attack_frame = 0
        self.anim_frame = 0
        self.anim_timer = 0
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_on_ground(self) -> bool:
        return self.y + self.height >= CONFIG.GROUND_LEVEL
    
    def apply_gravity(self):
        self.vy += CONFIG.GRAVITY
        if self.vy > 20:
            self.vy = 20
    
    def take_damage(self, amount: int, knockback_dir: int = 0):
        if self.invincibility > 0:
            return
        self.health -= amount
        self.invincibility = 30
        self.vx = knockback_dir * 5
        if self.health <= 0:
            self.health = 0
            self.state = EntityState.DEAD

# =============================================================================
# PLAYER (BATMAN) CLASS
# =============================================================================

class Player(Entity):
    """Batman - the player character."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 60, 95)
        self.max_health = PLAYER_STATS.MAX_HEALTH
        self.health = self.max_health
        self.lives = PLAYER_STATS.MAX_LIVES  # 3 lives!
        self.jumps_left = PLAYER_STATS.MAX_JUMPS
        self.combo = 0
        self.combo_timer = 0
        self.score = 0
        self.punch_cd = 0
        self.kick_cd = 0
        self.batarang_cd = 0
        self.attack_duration = 0
        
        # Checkpoint system - save position for respawn
        self.checkpoint_x = x
        self.checkpoint_y = y
        self.last_safe_x = x  # Updates as player progresses
        self.last_safe_y = y
    
    def update_checkpoint(self):
        """Update the last safe position (called periodically)."""
        if self.is_on_ground() and self.state != EntityState.DEAD:
            self.last_safe_x = self.x
            self.last_safe_y = self.y
    
    def respawn(self) -> bool:
        """
        Respawn Batman at last safe position.
        Returns True if respawn successful, False if no lives left.
        """
        if self.lives <= 0:
            return False
        
        self.lives -= 1
        self.health = self.max_health
        self.x = self.last_safe_x
        self.y = self.last_safe_y
        self.vx = 0
        self.vy = 0
        self.state = EntityState.IDLE
        self.invincibility = PLAYER_STATS.RESPAWN_INVINCIBILITY
        self.combo = 0
        self.combo_timer = 0
        self.current_attack = AttackType.NONE
        self.attack_duration = 0
        return True
    
    def handle_input(self, keys) -> Optional[Projectile]:
        """Handle player input."""
        if self.state == EntityState.DEAD:
            return None
        
        # Movement
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_STATS.MOVE_SPEED
            self.facing_right = False
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_STATS.MOVE_SPEED
            self.facing_right = True
            moving = True
        else:
            self.vx *= 0.8
            if abs(self.vx) < 0.5:
                self.vx = 0
        
        # Update state
        if self.state not in [EntityState.PUNCHING, EntityState.KICKING, 
                              EntityState.THROWING, EntityState.JUMPING, EntityState.FALLING]:
            self.state = EntityState.RUNNING if moving else EntityState.IDLE
        
        # Cooldowns
        if self.punch_cd > 0: self.punch_cd -= 1
        if self.kick_cd > 0: self.kick_cd -= 1
        if self.batarang_cd > 0: self.batarang_cd -= 1
        if self.attack_duration > 0:
            self.attack_duration -= 1
            if self.attack_duration == 0:
                self.current_attack = AttackType.NONE
        
        # Combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0
        
        return None
    
    def jump(self):
        """Make Batman jump."""
        if self.jumps_left > 0:
            power = PLAYER_STATS.JUMP_POWER if self.jumps_left == PLAYER_STATS.MAX_JUMPS else PLAYER_STATS.DOUBLE_JUMP_POWER
            self.vy = power
            self.jumps_left -= 1
            self.state = EntityState.JUMPING
    
    def punch(self) -> bool:
        """Perform punch."""
        if self.punch_cd <= 0 and self.attack_duration <= 0:
            self.punch_cd = PLAYER_STATS.PUNCH_COOLDOWN
            self.current_attack = AttackType.PUNCH
            self.attack_duration = 12
            self.state = EntityState.PUNCHING
            MUSIC.play_sfx('punch')
            return True
        return False
    
    def kick(self) -> bool:
        """Perform kick."""
        if self.kick_cd <= 0 and self.attack_duration <= 0:
            self.kick_cd = PLAYER_STATS.KICK_COOLDOWN
            self.current_attack = AttackType.KICK
            self.attack_duration = 16
            self.state = EntityState.KICKING
            MUSIC.play_sfx('kick')
            return True
        return False
    
    def throw_batarang(self) -> Optional[Projectile]:
        """Throw batarang."""
        if self.batarang_cd <= 0:
            self.batarang_cd = PLAYER_STATS.BATARANG_COOLDOWN
            self.current_attack = AttackType.BATARANG
            self.attack_duration = 8
            self.state = EntityState.THROWING
            MUSIC.play_sfx('batarang')
            
            direction = 1 if self.facing_right else -1
            return Projectile(
                self.x + (self.width if self.facing_right else 0),
                self.y + self.height // 3,
                PLAYER_STATS.BATARANG_SPEED * direction, 0,
                PLAYER_STATS.BATARANG_DAMAGE, True,
                PLAYER_STATS.BATARANG_MAX_DISTANCE
            )
        return None
    
    def get_attack_rect(self) -> Optional[pygame.Rect]:
        """Get attack hitbox."""
        if self.current_attack == AttackType.NONE or self.attack_duration <= 0:
            return None
        
        if self.current_attack == AttackType.PUNCH:
            r = PLAYER_STATS.PUNCH_RANGE
        elif self.current_attack == AttackType.KICK:
            r = PLAYER_STATS.KICK_RANGE
        else:
            return None
        
        if self.facing_right:
            return pygame.Rect(self.x + self.width, self.y + 15, r, self.height - 30)
        return pygame.Rect(self.x - r, self.y + 15, r, self.height - 30)
    
    def get_damage(self) -> int:
        """Get attack damage with combo bonus."""
        base = PLAYER_STATS.PUNCH_DAMAGE if self.current_attack == AttackType.PUNCH else PLAYER_STATS.KICK_DAMAGE
        mult = min(1.0 + self.combo * PLAYER_STATS.COMBO_DAMAGE_BONUS, PLAYER_STATS.MAX_COMBO_MULTIPLIER)
        return int(base * mult)
    
    def register_hit(self):
        """Register successful hit."""
        self.combo += 1
        self.combo_timer = PLAYER_STATS.COMBO_WINDOW
        MUSIC.play_sfx('hit')
    
    def take_damage(self, amount: int, knockback_dir: int = 0):
        """Take damage."""
        if self.invincibility > 0:
            return
        super().take_damage(amount, knockback_dir)
        self.combo = 0
        self.combo_timer = 0
        self.invincibility = PLAYER_STATS.HIT_INVINCIBILITY
        MUSIC.play_sfx('hurt')
    
    def update(self):
        """Update Batman."""
        self.apply_gravity()
        self.x += self.vx
        self.y += self.vy
        
        # Ground collision
        if self.y + self.height > CONFIG.GROUND_LEVEL:
            self.y = CONFIG.GROUND_LEVEL - self.height
            self.vy = 0
            self.jumps_left = PLAYER_STATS.MAX_JUMPS
            if self.state in [EntityState.JUMPING, EntityState.FALLING]:
                self.state = EntityState.IDLE
        
        # Air state
        if self.vy < 0:
            self.state = EntityState.JUMPING
        elif self.vy > 2 and not self.is_on_ground():
            self.state = EntityState.FALLING
        
        # Bounds
        self.x = max(0, min(self.x, CONFIG.LEVEL_WIDTH - self.width))
        
        # Invincibility
        if self.invincibility > 0:
            self.invincibility -= 1
        
        # Update checkpoint every 60 frames (1 second)
        if self.anim_timer == 0:
            self.update_checkpoint()
        
        # Animation
        self.anim_timer += 1
        if self.anim_timer >= 8:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
    
    def draw(self, surface: pygame.Surface, camera_x: int):
        """Draw Batman."""
        sx = self.x - camera_x
        
        # Flash when invincible (different pattern for respawn vs hit)
        if self.invincibility > 0:
            if self.invincibility > PLAYER_STATS.HIT_INVINCIBILITY:
                # Respawn effect - golden glow + rapid flash
                if self.invincibility % 6 < 3:
                    # Draw golden glow behind Batman
                    glow_surf = pygame.Surface((self.width + 40, self.height + 30), pygame.SRCALPHA)
                    pygame.draw.ellipse(glow_surf, (255, 215, 0, 100), 
                                       (0, 0, self.width + 40, self.height + 30))
                    surface.blit(glow_surf, (sx - 20, self.y - 15))
                else:
                    return  # Skip drawing for flash
            else:
                # Normal hit invincibility - simple flash
                if self.invincibility % 4 < 2:
                    return
        
        # Determine sprite
        if self.current_attack == AttackType.PUNCH:
            action = 'punch'
        elif self.current_attack == AttackType.KICK:
            action = 'kick'
        elif self.current_attack == AttackType.BATARANG:
            action = 'punch'
        elif self.state in [EntityState.JUMPING, EntityState.FALLING]:
            action = 'jump'
        elif self.state == EntityState.RUNNING:
            action = 'run'
        else:
            action = 'idle'
        
        sprite = GRAPHICS.get_batman_sprite(action)
        if sprite:
            GRAPHICS.draw_sprite(surface, sprite, int(sx) - 15, int(self.y) - 10,
                                self.width + 30, self.height + 15, self.facing_right)
        else:
            # Fallback rectangle
            pygame.draw.rect(surface, (30, 30, 30), (sx, self.y, self.width, self.height))

# =============================================================================
# VILLAIN CLASS - State-driven animation
# =============================================================================

class Villain(Entity):
    """
    Villain boss with state-driven animations.
    Automatically uses split sprite sheets for different actions.
    """
    
    def __init__(self, x: float, y: float, villain_type: VillainType):
        config = VILLAIN_CONFIGS[villain_type]
        super().__init__(x, y, config.width, config.height)
        
        self.villain_type = villain_type
        self.config = config
        self.max_health = config.health
        self.health = self.max_health
        self.spawn_x = x
        
        # AI
        self.ai_state = "patrol"
        self.ai_timer = 0
        self.special_cooldown = 0
        self.projectile_cooldown = 0
        
        # Phase (for multi-phase bosses)
        self.phase = 1
        self.phase_triggered = False
        
        # Unique behaviors
        self.coin_flip_timer = 0  # Two-Face
        self.erratic_timer = 0    # Joker
        self.venom_active = False # Bane
        self.counter_window = 0   # Deathstroke
    
    def update(self, player: Player) -> Optional[Projectile]:
        """Update villain AI and state."""
        if self.state == EntityState.DEAD:
            return None
        
        projectile = None
        
        # Cooldowns
        if self.attack_cooldown > 0: self.attack_cooldown -= 1
        if self.invincibility > 0: self.invincibility -= 1
        if self.special_cooldown > 0: self.special_cooldown -= 1
        if self.projectile_cooldown > 0: self.projectile_cooldown -= 1
        if self.attack_frame > 0:
            self.attack_frame -= 1
            if self.attack_frame == 0:
                self.current_attack = AttackType.NONE
        
        # Distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        # Face player
        self.facing_right = dx > 0
        
        # Check for phase transition
        self._check_phase_transition()
        
        # Execute villain-specific AI
        projectile = self._execute_ai(player, dx, dist)
        
        # Physics
        self.apply_gravity()
        self.x += self.vx
        self.y += self.vy
        
        # Ground
        if self.y + self.height > CONFIG.GROUND_LEVEL:
            self.y = CONFIG.GROUND_LEVEL - self.height
            self.vy = 0
        
        # Bounds
        self.x = max(0, min(self.x, CONFIG.LEVEL_WIDTH - self.width))
        
        # Animation
        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
        
        return projectile
    
    def _check_phase_transition(self):
        """Check if boss should enter new phase."""
        if self.config.phases <= 1:
            return
        
        health_percent = self.health / self.max_health
        
        if self.villain_type == VillainType.BANE:
            if health_percent < 0.5 and self.phase == 1:
                self.phase = 2
                self.venom_active = True
                # Venom boost!
                self.config.damage = int(self.config.damage * 1.5)
                self.config.speed *= 1.3
        
        elif self.villain_type == VillainType.DEATHSTROKE:
            if health_percent < 0.66 and self.phase == 1:
                self.phase = 2
            elif health_percent < 0.33 and self.phase == 2:
                self.phase = 3
                self.config.can_counter = True
    
    def _execute_ai(self, player: Player, dx: float, dist: float) -> Optional[Projectile]:
        """Execute villain-specific AI behavior."""
        projectile = None
        
        # AI state update
        self.ai_timer += 1
        if self.ai_timer >= 30:
            self.ai_timer = 0
            self._update_ai_state(dist)
        
        # Execute based on villain type
        if self.villain_type == VillainType.TWOFACE:
            projectile = self._ai_twoface(player, dx, dist)
        elif self.villain_type == VillainType.JOKER:
            projectile = self._ai_joker(player, dx, dist)
        elif self.villain_type == VillainType.PENGUIN:
            projectile = self._ai_penguin(player, dx, dist)
        elif self.villain_type == VillainType.SCARECROW:
            projectile = self._ai_scarecrow(player, dx, dist)
        elif self.villain_type == VillainType.CROC:
            projectile = self._ai_croc(player, dx, dist)
        elif self.villain_type == VillainType.BANE:
            projectile = self._ai_bane(player, dx, dist)
        elif self.villain_type == VillainType.DEATHSTROKE:
            projectile = self._ai_deathstroke(player, dx, dist)
        
        return projectile
    
    def _update_ai_state(self, dist: float):
        """Update AI state based on distance."""
        if dist < self.config.attack_range:
            self.ai_state = "attack"
        elif dist < 350 and random.random() < self.config.aggression:
            self.ai_state = "chase"
        elif dist > 450:
            self.ai_state = "patrol"
        else:
            self.ai_state = "chase" if random.random() < self.config.aggression else "retreat"
    
    def _ai_twoface(self, player: Player, dx: float, dist: float) -> Optional[Projectile]:
        """Two-Face AI - Coin flip determines behavior."""
        self.coin_flip_timer += 1
        
        # Coin flip every ~3 seconds
        if self.coin_flip_timer >= 180:
            self.coin_flip_timer = 0
            # Flip coin - affects aggression
            if random.random() > 0.5:
                self.config.aggression = 0.9  # Good side - aggressive
            else:
                self.config.aggression = 0.3  # Bad side - cautious
        
        return self._basic_ai(player, dx, dist)
    
    def _ai_joker(self, player: Player, dx: float, dist: float) -> Optional[Projectile]:
        """Joker AI - Erratic, unpredictable movement."""
        self.erratic_timer += 1
        
        # Random direction changes
        if self.erratic_timer >= 60:
            self.erratic_timer = 0
            if random.random() < 0.4:
                # Fake out - suddenly change direction
                self.vx = -self.vx if abs(self.vx) > 0.1 else (random.choice([-1, 1]) * self.config.speed)
        
        # Sometimes dodge randomly
        if self.config.can_dodge and random.random() < 0.02:
            self.vx = random.choice([-1, 1]) * self.config.speed * 2
        
        return self._basic_ai(player, dx, dist)
    
    def _ai_penguin(self, player: Player, dx: float, dist: float) -> Optional[Projectile]:
        """Penguin AI - Prefers ranged combat."""
        # Stay at range
        if dist < 150:
            self.ai_state = "retreat"
        elif dist > 300 and dist < 500:
            self.ai_state = "attack"  # Optimal range
        
        # More frequent projectiles
        if self.projectile_cooldown <= 0 and dist > 100 and dist < 500:
            self.projectile_cooldown = 50
            direction = 1 if self.facing_right else -1
            return Projectile(
                self.x + (self.width if self.facing_right else 0),
                self.y + self.height // 3,
                self.config.projectile_damage * direction * 0.7, 0,
                self.config.projectile_damage, False, 600
            )
        
        return self._basic_ai(player, dx, dist, prefer_melee=False)
    
    def _ai_scarecrow(self, player: Player, dx: float, dist: float) -> Optional[Projectile]:
        """Scarecrow AI - Fear toxin attacks."""
        # Fear gas projectile
        if self.projectile_cooldown <= 0 and dist < 400:
            self.projectile_cooldown = 70
            direction = 1 if self.facing_right else -1
            return Projectile(
                self.x + (self.width if self.facing_right else 0),
                self.y + self.height // 2,
                8 * direction, 0,
                self.config.projectile_damage, False, 400
            )
        
        return self._basic_ai(player, dx, dist)
    
    def _ai_croc(self, player: Player, dx: float, dist: float) -> Optional[Projectile]:
        """Killer Croc AI - Heavy melee, grab attacks."""
        # Very aggressive when close
        if dist < 150:
            self.ai_state = "attack"
            self.config.aggression = 0.95
        
        # Special grab attack
        if self.special_cooldown <= 0 and dist < 80:
            self.special_cooldown = 120
            self.current_attack = AttackType.SPECIAL
            self.attack_frame = 25
            # Deal extra damage if hits
        
        return self._basic_ai(player, dx, dist)
    
    def _ai_bane(self, player: Player, dx: float, dist: float) -> Optional[Projectile]:
        """Bane AI - Multi-phase with Venom boost."""
        # More aggressive in Venom phase
        if self.venom_active:
            self.config.aggression = 0.95
            # Jump attack
            if dist > 150 and dist < 400 and self.is_on_ground() and random.random() < 0.03:
                self.vy = -20
                self.vx = (1 if dx > 0 else -1) * self.config.speed * 2
        
        return self._basic_ai(player, dx, dist)
    
    def _ai_deathstroke(self, player: Player, dx: float, dist: float) -> Optional[Projectile]:
        """Deathstroke AI - Counter master, very aggressive."""
        # Counter window - if player is attacking, chance to counter
        if self.config.can_counter and player.attack_duration > 5:
            if dist < 120 and random.random() < 0.3:
                # Counter attack!
                self.current_attack = AttackType.SPECIAL
                self.attack_frame = 15
        
        # Very mobile
        if dist < 100 and random.random() < 0.05:
            # Dodge roll
            self.vx = (-1 if dx > 0 else 1) * self.config.speed * 2.5
        
        # Frequent attacks
        return self._basic_ai(player, dx, dist)
    
    def _basic_ai(self, player: Player, dx: float, dist: float, 
                  prefer_melee: bool = True) -> Optional[Projectile]:
        """Basic AI behavior shared by all villains."""
        projectile = None
        
        if self.ai_state == "patrol":
            target = self.spawn_x + math.sin(pygame.time.get_ticks() / 1000) * 150
            self.vx = self.config.speed * 0.5 * (1 if target > self.x else -1)
            self.state = EntityState.RUNNING
            
        elif self.ai_state == "chase":
            self.vx = self.config.speed * (1 if dx > 0 else -1)
            self.state = EntityState.RUNNING
            
        elif self.ai_state == "attack":
            self.vx = 0
            
            # Melee attack
            if prefer_melee and self.attack_cooldown <= 0 and dist < self.config.attack_range:
                self.current_attack = AttackType.PUNCH if random.random() > 0.5 else AttackType.KICK
                self.attack_cooldown = self.config.attack_cooldown
                self.attack_frame = 15
                self.state = EntityState.PUNCHING if self.current_attack == AttackType.PUNCH else EntityState.KICKING
            
            # Projectile attack
            elif self.config.has_projectile and self.projectile_cooldown <= 0 and dist > 80:
                self.projectile_cooldown = 80
                direction = 1 if self.facing_right else -1
                projectile = Projectile(
                    self.x + (self.width if self.facing_right else 0),
                    self.y + self.height // 3,
                    12 * direction, 0,
                    self.config.projectile_damage, False, 500
                )
                self.state = EntityState.THROWING
                
        elif self.ai_state == "retreat":
            self.vx = self.config.speed * (-1 if dx > 0 else 1)
            self.state = EntityState.RUNNING
        
        # Blocking
        if self.config.can_block and player.attack_duration > 0 and dist < 150:
            if random.random() < 0.25:
                self.state = EntityState.BLOCKING
        
        return projectile
    
    def get_attack_rect(self) -> Optional[pygame.Rect]:
        """Get attack hitbox."""
        if self.current_attack == AttackType.NONE or self.attack_frame < 5:
            return None
        
        if self.facing_right:
            return pygame.Rect(self.x + self.width, self.y + 20,
                              self.config.attack_range, self.height - 40)
        return pygame.Rect(self.x - self.config.attack_range, self.y + 20,
                          self.config.attack_range, self.height - 40)
    
    def take_damage(self, amount: int, knockback_dir: int = 0):
        """Take damage with blocking reduction."""
        if self.state == EntityState.BLOCKING and self.config.can_block:
            amount = amount // 3
        super().take_damage(amount, knockback_dir)
    
    def draw(self, surface: pygame.Surface, camera_x: int):
        """Draw villain with state-driven animation."""
        sx = self.x - camera_x
        
        # Skip if off screen
        if sx < -self.width or sx > CONFIG.SCREEN_WIDTH + self.width:
            return
        
        # Flash when hit
        if self.invincibility > 0 and self.invincibility % 3 == 0:
            return
        
        # Determine animation based on state
        if self.current_attack in [AttackType.PUNCH, AttackType.SPECIAL]:
            action = 'punch'
        elif self.current_attack == AttackType.KICK:
            action = 'kick'
        elif self.state == EntityState.JUMPING:
            action = 'jump'
        elif self.state == EntityState.RUNNING:
            action = 'run'
        else:
            action = 'idle'
        
        # Get sprite from split sprite sheet
        sprite = GRAPHICS.get_villain_sprite(self.config.name, action)
        
        if sprite:
            GRAPHICS.draw_sprite(surface, sprite, int(sx) - 10, int(self.y) - 5,
                                self.width + 20, self.height + 10, self.facing_right)
        else:
            # Fallback colored rectangle
            color = (128, 0, 128) if self.villain_type == VillainType.JOKER else (100, 50, 50)
            pygame.draw.rect(surface, color, (sx, self.y, self.width, self.height))
        
        # Boss health bar
        self._draw_health_bar(surface, sx)
        
        # Phase indicator for multi-phase bosses
        if self.config.phases > 1:
            phase_text = GRAPHICS.fonts["tiny"].render(f"Phase {self.phase}", True, (255, 200, 0))
            surface.blit(phase_text, (sx + self.width // 2 - 20, self.y - 35))
    
    def _draw_health_bar(self, surface: pygame.Surface, sx: float):
        """Draw boss health bar."""
        bar_w = self.width + 30
        bar_h = 8
        bar_x = sx - 15
        bar_y = self.y - 20
        
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
        health_w = (self.health / self.max_health) * bar_w
        color = (220, 20, 60) if not self.venom_active else (0, 255, 0)
        pygame.draw.rect(surface, color, (bar_x, bar_y, health_w, bar_h))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 1)

# =============================================================================
# HENCHMAN CLASS
# =============================================================================

class Henchman(Entity):
    """Basic henchman enemy."""
    
    def __init__(self, x: float, y: float, villain_type: VillainType):
        super().__init__(x, y, 45, 75)
        self.villain_type = villain_type
        self.max_health = 60 + villain_type.value.__hash__() % 40
        self.health = self.max_health
        self.damage = 12
        self.speed = 2.5
        self.attack_range = 55
        self.spawn_x = x
        self.ai_timer = 0
        self.score_value = 150
    
    def update(self, player: Player) -> Optional[Projectile]:
        """Update henchman."""
        if self.state == EntityState.DEAD:
            return None
        
        if self.attack_cooldown > 0: self.attack_cooldown -= 1
        if self.invincibility > 0: self.invincibility -= 1
        if self.attack_frame > 0:
            self.attack_frame -= 1
            if self.attack_frame == 0:
                self.current_attack = AttackType.NONE
        
        dx = player.x - self.x
        dist = abs(dx)
        self.facing_right = dx > 0
        
        self.ai_timer += 1
        if self.ai_timer >= 45:
            self.ai_timer = 0
        
        # Simple AI
        if dist < self.attack_range and self.attack_cooldown <= 0:
            self.current_attack = AttackType.PUNCH
            self.attack_cooldown = 50
            self.attack_frame = 12
            self.vx = 0
        elif dist < 300:
            self.vx = self.speed * (1 if dx > 0 else -1)
        else:
            self.vx = math.sin(pygame.time.get_ticks() / 1000 + self.spawn_x) * self.speed * 0.5
        
        self.apply_gravity()
        self.x += self.vx
        self.y += self.vy
        
        if self.y + self.height > CONFIG.GROUND_LEVEL:
            self.y = CONFIG.GROUND_LEVEL - self.height
            self.vy = 0
        
        self.x = max(0, min(self.x, CONFIG.LEVEL_WIDTH - self.width))
        
        return None
    
    def get_attack_rect(self) -> Optional[pygame.Rect]:
        """Get attack hitbox."""
        if self.current_attack == AttackType.NONE or self.attack_frame < 4:
            return None
        if self.facing_right:
            return pygame.Rect(self.x + self.width, self.y + 15, self.attack_range, self.height - 30)
        return pygame.Rect(self.x - self.attack_range, self.y + 15, self.attack_range, self.height - 30)
    
    def draw(self, surface: pygame.Surface, camera_x: int):
        """Draw henchman."""
        sx = self.x - camera_x
        if sx < -self.width or sx > CONFIG.SCREEN_WIDTH + self.width:
            return
        
        if self.invincibility > 0 and self.invincibility % 2 == 0:
            return
        
        if GRAPHICS.henchman_sprite:
            GRAPHICS.draw_sprite(surface, GRAPHICS.henchman_sprite, 
                                int(sx) - 5, int(self.y) - 3,
                                self.width + 10, self.height + 6, self.facing_right)
        else:
            pygame.draw.rect(surface, (80, 80, 80), (sx, self.y, self.width, self.height))

# =============================================================================
# HEALTH PICKUP
# =============================================================================

class HealthPickup:
    """Health pickup item."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.heal = 25
        self.active = True
        self.lifetime = 600
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface: pygame.Surface, camera_x: int):
        if not self.active:
            return
        sx = self.x - camera_x
        pulse = abs(math.sin(pygame.time.get_ticks() / 200)) * 0.3 + 0.7
        color = (int(50 * pulse), int(220 * pulse), int(50 * pulse))
        cx, cy = sx + self.width // 2, self.y + self.height // 2
        pygame.draw.rect(surface, color, (cx - 3, cy - 10, 6, 20))
        pygame.draw.rect(surface, color, (cx - 10, cy - 3, 20, 6))

# =============================================================================
# LEVEL / TERRITORY
# =============================================================================

class Territory:
    """A villain's territory with its own background."""
    
    def __init__(self, villain_type: VillainType):
        self.villain_type = villain_type
        self.config = VILLAIN_CONFIGS[villain_type]
        self.background = GRAPHICS.get_background(self.config.name)
    
    def draw_background(self, surface: pygame.Surface, camera_x: int):
        """Draw territory background with parallax."""
        if self.background:
            bg_w = self.background.get_width()
            parallax = camera_x * 0.3
            
            start_tile = int(parallax // bg_w)
            for i in range(start_tile - 1, start_tile + 3):
                tile_x = i * bg_w - parallax
                if tile_x < CONFIG.SCREEN_WIDTH and tile_x + bg_w > 0:
                    surface.blit(self.background, (int(tile_x), 0))
            
            # Atmospheric overlay
            overlay = pygame.Surface((CONFIG.SCREEN_WIDTH, CONFIG.SCREEN_HEIGHT))
            overlay.fill((0, 0, 15))
            overlay.set_alpha(25)
            surface.blit(overlay, (0, 0))
        else:
            # Fallback gradient
            for y in range(CONFIG.SCREEN_HEIGHT):
                p = y / CONFIG.SCREEN_HEIGHT
                c = (int(20 * (1 - p)), int(15 * (1 - p)), int(35 * (1 - p)))
                pygame.draw.line(surface, c, (0, y), (CONFIG.SCREEN_WIDTH, y))
        
        # Ground
        pygame.draw.rect(surface, (30, 30, 40),
                        (0, CONFIG.GROUND_LEVEL, CONFIG.SCREEN_WIDTH,
                         CONFIG.SCREEN_HEIGHT - CONFIG.GROUND_LEVEL))
        pygame.draw.line(surface, (50, 50, 60),
                        (0, CONFIG.GROUND_LEVEL), (CONFIG.SCREEN_WIDTH, CONFIG.GROUND_LEVEL), 3)

# =============================================================================
# GAME UI
# =============================================================================

class GameUI:
    """Game UI rendering."""
    
    def __init__(self):
        self.fonts = GRAPHICS.fonts
    
    def draw_hud(self, surface: pygame.Surface, player: Player, 
                 territory: Territory, villain: Optional[Villain]):
        """Draw HUD."""
        # Player health
        self._draw_bar(surface, 20, 20, 220, 22, player.health, player.max_health, 
                      (220, 20, 60), "BATMAN")
        
        # Lives display
        lives_txt = self.fonts["medium"].render(f"LIVES: ", True, (255, 255, 255))
        surface.blit(lives_txt, (20, 48))
        # Draw bat symbols for lives
        for i in range(player.lives):
            bat_x = 110 + i * 30
            # Draw simple bat shape
            pygame.draw.polygon(surface, (255, 215, 0), [
                (bat_x, 58), (bat_x - 10, 52), (bat_x - 5, 58),
                (bat_x - 12, 65), (bat_x, 60), (bat_x + 12, 65),
                (bat_x + 5, 58), (bat_x + 10, 52)
            ])
        
        # Score
        score_txt = self.fonts["medium"].render(f"SCORE: {player.score:,}", True, (255, 255, 255))
        surface.blit(score_txt, (20, 78))
        
        # Combo
        if player.combo > 1:
            combo_txt = self.fonts["large"].render(f"x{player.combo} COMBO!", True, (255, 215, 0))
            x = CONFIG.SCREEN_WIDTH // 2 - combo_txt.get_width() // 2
            scale = 1.0 + abs(math.sin(pygame.time.get_ticks() / 100)) * 0.15
            scaled = pygame.transform.scale(combo_txt, 
                (int(combo_txt.get_width() * scale), int(combo_txt.get_height() * scale)))
            surface.blit(scaled, (x, 100))
        
        # Territory name
        terr_txt = self.fonts["small"].render(territory.config.territory_name, True, (200, 200, 200))
        surface.blit(terr_txt, (CONFIG.SCREEN_WIDTH - terr_txt.get_width() - 20, 20))
        
        # Boss health bar
        if villain and villain.state != EntityState.DEAD:
            self._draw_boss_bar(surface, villain)
        
        # Controls
        ctrl = "MOVE: Arrow/WASD | JUMP: Space | PUNCH: Z | KICK: X | BATARANG: C"
        ctrl_txt = self.fonts["tiny"].render(ctrl, True, (150, 150, 150))
        surface.blit(ctrl_txt, (CONFIG.SCREEN_WIDTH // 2 - ctrl_txt.get_width() // 2,
                               CONFIG.SCREEN_HEIGHT - 22))
    
    def _draw_bar(self, surface, x, y, w, h, current, maximum, color, label=""):
        """Draw a health bar."""
        pygame.draw.rect(surface, (40, 40, 40), (x, y, w, h))
        fill_w = (current / maximum) * w
        pygame.draw.rect(surface, color, (x, y, fill_w, h))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, w, h), 2)
        if label:
            txt = self.fonts["small"].render(label, True, (255, 255, 255))
            surface.blit(txt, (x + 5, y + 2))
    
    def _draw_boss_bar(self, surface: pygame.Surface, villain: Villain):
        """Draw boss health bar at bottom."""
        bar_w = 450
        bar_h = 28
        x = CONFIG.SCREEN_WIDTH // 2 - bar_w // 2
        y = CONFIG.SCREEN_HEIGHT - 75
        
        # Boss name
        name_txt = self.fonts["medium"].render(villain.config.display_name, True, (255, 50, 50))
        surface.blit(name_txt, (CONFIG.SCREEN_WIDTH // 2 - name_txt.get_width() // 2, y - 40))
        
        # Health bar
        color = (220, 20, 60) if not villain.venom_active else (0, 255, 0)
        self._draw_bar(surface, x, y, bar_w, bar_h, villain.health, villain.max_health, color)
    
    def draw_title(self, surface: pygame.Surface):
        """Draw title screen."""
        surface.fill((10, 10, 20))
        
        title = self.fonts["title"].render("BATMAN", True, (255, 215, 0))
        subtitle = self.fonts["large"].render("ARKHAM SHADOWS", True, (255, 255, 255))
        
        surface.blit(title, (CONFIG.SCREEN_WIDTH // 2 - title.get_width() // 2, 
                            CONFIG.SCREEN_HEIGHT // 3))
        surface.blit(subtitle, (CONFIG.SCREEN_WIDTH // 2 - subtitle.get_width() // 2,
                               CONFIG.SCREEN_HEIGHT // 3 + 80))
        
        if pygame.time.get_ticks() % 1000 < 500:
            prompt = self.fonts["medium"].render("Press ENTER to Start", True, (200, 200, 200))
            surface.blit(prompt, (CONFIG.SCREEN_WIDTH // 2 - prompt.get_width() // 2,
                                 CONFIG.SCREEN_HEIGHT * 2 // 3))
        
        # Villain list
        y = CONFIG.SCREEN_HEIGHT // 2 + 50
        for i, vt in enumerate(VILLAIN_ORDER):
            cfg = VILLAIN_CONFIGS[vt]
            txt = self.fonts["small"].render(f"{i+1}. {cfg.display_name}", True, (150, 150, 150))
            surface.blit(txt, (CONFIG.SCREEN_WIDTH // 2 - txt.get_width() // 2, y + i * 25))
    
    def draw_level_intro(self, surface: pygame.Surface, territory: Territory):
        """Draw level intro."""
        surface.fill((10, 10, 20))
        
        cfg = territory.config
        level_txt = self.fonts["large"].render(f"TERRITORY {VILLAIN_ORDER.index(territory.villain_type) + 1}", 
                                               True, (255, 255, 255))
        name_txt = self.fonts["title"].render(cfg.territory_name, True, (255, 215, 0))
        boss_txt = self.fonts["medium"].render(f"BOSS: {cfg.display_name}", True, (255, 50, 50))
        
        surface.blit(level_txt, (CONFIG.SCREEN_WIDTH // 2 - level_txt.get_width() // 2,
                                CONFIG.SCREEN_HEIGHT // 3))
        surface.blit(name_txt, (CONFIG.SCREEN_WIDTH // 2 - name_txt.get_width() // 2,
                               CONFIG.SCREEN_HEIGHT // 3 + 60))
        surface.blit(boss_txt, (CONFIG.SCREEN_WIDTH // 2 - boss_txt.get_width() // 2,
                               CONFIG.SCREEN_HEIGHT // 2 + 40))
    
    def draw_game_over(self, surface: pygame.Surface, score: int, won: bool):
        """Draw game over screen."""
        overlay = pygame.Surface((CONFIG.SCREEN_WIDTH, CONFIG.SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        surface.blit(overlay, (0, 0))
        
        if won:
            result = self.fonts["title"].render("GOTHAM IS SAVED!", True, (255, 215, 0))
        else:
            result = self.fonts["title"].render("GAME OVER", True, (200, 50, 50))
        
        surface.blit(result, (CONFIG.SCREEN_WIDTH // 2 - result.get_width() // 2,
                             CONFIG.SCREEN_HEIGHT // 3))
        
        score_txt = self.fonts["large"].render(f"Final Score: {score:,}", True, (255, 255, 255))
        surface.blit(score_txt, (CONFIG.SCREEN_WIDTH // 2 - score_txt.get_width() // 2,
                                CONFIG.SCREEN_HEIGHT // 2))
        
        prompt = self.fonts["medium"].render("Press R to Restart | ESC to Quit", True, (200, 200, 200))
        surface.blit(prompt, (CONFIG.SCREEN_WIDTH // 2 - prompt.get_width() // 2,
                             CONFIG.SCREEN_HEIGHT * 2 // 3))
    
    def draw_pause(self, surface: pygame.Surface):
        """Draw pause screen."""
        overlay = pygame.Surface((CONFIG.SCREEN_WIDTH, CONFIG.SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        surface.blit(overlay, (0, 0))
        
        txt = self.fonts["title"].render("PAUSED", True, (255, 255, 255))
        surface.blit(txt, (CONFIG.SCREEN_WIDTH // 2 - txt.get_width() // 2,
                          CONFIG.SCREEN_HEIGHT // 2 - 30))
        
        hint = self.fonts["small"].render("Press P to Resume | ESC to Quit", True, (200, 200, 200))
        surface.blit(hint, (CONFIG.SCREEN_WIDTH // 2 - hint.get_width() // 2,
                           CONFIG.SCREEN_HEIGHT // 2 + 40))

# =============================================================================
# MAIN GAME CLASS
# =============================================================================

class Game:
    """Main game controller."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((CONFIG.SCREEN_WIDTH, CONFIG.SCREEN_HEIGHT))
        pygame.display.set_caption(CONFIG.TITLE)
        self.clock = pygame.time.Clock()
        
        # Load all graphics
        GRAPHICS.load_all()
        
        self.state = "title"
        self.running = True
        self.won = False
        
        self.current_level = 0
        self.intro_timer = 0
        
        self.ui = GameUI()
        
        self.player: Optional[Player] = None
        self.villain: Optional[Villain] = None
        self.henchmen: List[Henchman] = []
        self.projectiles: List[Projectile] = []
        self.pickups: List[HealthPickup] = []
        self.territory: Optional[Territory] = None
        
        self.camera_x = 0
    
    def start_level(self, level_idx: int):
        """Start a territory/level."""
        if level_idx >= len(VILLAIN_ORDER):
            self.won = True
            self.state = "game_over"
            MUSIC.stop_ambient()
            return
        
        # Clear sprite cache for memory
        GRAPHICS.clear_cache()
        
        self.current_level = level_idx
        villain_type = VILLAIN_ORDER[level_idx]
        config = VILLAIN_CONFIGS[villain_type]
        
        # Create territory
        self.territory = Territory(villain_type)
        
        # Create player (preserve score and lives)
        old_score = self.player.score if self.player else 0
        old_lives = self.player.lives if self.player else PLAYER_STATS.MAX_LIVES
        self.player = Player(100, CONFIG.GROUND_LEVEL - 120)
        self.player.score = old_score
        self.player.lives = old_lives  # Keep remaining lives!
        
        # Create villain
        self.villain = Villain(CONFIG.LEVEL_WIDTH - 350, CONFIG.GROUND_LEVEL - config.height - 10, villain_type)
        
        # Create henchmen
        self.henchmen = []
        spacing = (CONFIG.LEVEL_WIDTH - 600) // (config.num_henchmen + 1)
        for i in range(config.num_henchmen):
            x = 350 + i * spacing + random.randint(-40, 40)
            h = Henchman(x, CONFIG.GROUND_LEVEL - 85, villain_type)
            self.henchmen.append(h)
        
        self.projectiles = []
        self.pickups = []
        self.camera_x = 0
        
        # Start music
        MUSIC.stop_ambient()
        MUSIC.play_ambient(boss=False)
        
        # Level intro
        self.state = "level_intro"
        self.intro_timer = 180
    
    def handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "paused"
                    else:
                        self.running = False
                
                elif self.state == "title":
                    if event.key == pygame.K_RETURN:
                        self.start_level(0)
                
                elif self.state == "paused":
                    if event.key == pygame.K_p:
                        self.state = "playing"
                
                elif self.state == "game_over":
                    if event.key == pygame.K_r:
                        self.start_level(0)
                
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
                        proj = self.player.throw_batarang()
                        if proj:
                            self.projectiles.append(proj)
    
    def update(self):
        """Update game state."""
        if self.state == "level_intro":
            self.intro_timer -= 1
            if self.intro_timer <= 0:
                self.state = "playing"
            return
        
        if self.state != "playing" or not self.player:
            return
        
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update()
        
        # Camera
        target = self.player.x - 400
        target = max(0, min(target, CONFIG.LEVEL_WIDTH - CONFIG.SCREEN_WIDTH))
        self.camera_x += (target - self.camera_x) * 0.1
        
        # Update villain
        if self.villain and self.villain.state != EntityState.DEAD:
            proj = self.villain.update(self.player)
            if proj:
                self.projectiles.append(proj)
            
            # Boss music when close
            if abs(self.player.x - self.villain.x) < 450:
                if MUSIC.current_music != 'boss':
                    MUSIC.stop_ambient()
                    MUSIC.play_ambient(boss=True)
        
        # Update henchmen
        for h in self.henchmen[:]:
            if h.state == EntityState.DEAD:
                if random.random() < 0.15:
                    self.pickups.append(HealthPickup(h.x, h.y))
                self.player.score += h.score_value
                self.henchmen.remove(h)
                MUSIC.play_sfx('death')
                continue
            h.update(self.player)
        
        # Check villain death
        if self.villain and self.villain.state == EntityState.DEAD:
            self.player.score += self.villain.config.score_value
            MUSIC.play_sfx('death')
            # Next level
            next_lvl = self.current_level + 1
            if next_lvl >= len(VILLAIN_ORDER):
                self.won = True
                self.state = "game_over"
                MUSIC.stop_ambient()
            else:
                score = self.player.score
                self.start_level(next_lvl)
                if self.player:
                    self.player.score = score
        
        # Update projectiles
        for p in self.projectiles[:]:
            p.update()
            if not p.active:
                self.projectiles.remove(p)
                continue
            
            prect = p.get_rect()
            
            if p.from_player:
                # Hit villain
                if self.villain and self.villain.state != EntityState.DEAD:
                    if prect.colliderect(self.villain.get_rect()):
                        d = 1 if p.vx > 0 else -1
                        self.villain.take_damage(p.damage, d)
                        self.player.register_hit()
                        p.active = False
                        continue
                
                # Hit henchmen
                for h in self.henchmen:
                    if h.state != EntityState.DEAD and prect.colliderect(h.get_rect()):
                        d = 1 if p.vx > 0 else -1
                        h.take_damage(p.damage, d)
                        self.player.register_hit()
                        p.active = False
                        break
            else:
                # Enemy projectile hits player
                if prect.colliderect(self.player.get_rect()):
                    d = 1 if p.vx > 0 else -1
                    self.player.take_damage(p.damage, d)
                    p.active = False
        
        # Player melee attacks
        atk_rect = self.player.get_attack_rect()
        if atk_rect:
            # Hit villain
            if self.villain and self.villain.state != EntityState.DEAD:
                if atk_rect.colliderect(self.villain.get_rect()):
                    d = 1 if self.player.facing_right else -1
                    self.villain.take_damage(self.player.get_damage(), d)
                    self.player.register_hit()
            
            # Hit henchmen
            for h in self.henchmen:
                if h.state != EntityState.DEAD and atk_rect.colliderect(h.get_rect()):
                    d = 1 if self.player.facing_right else -1
                    h.take_damage(self.player.get_damage(), d)
                    self.player.register_hit()
        
        # Enemy attacks hit player
        if self.villain and self.villain.state != EntityState.DEAD:
            vatk = self.villain.get_attack_rect()
            if vatk and vatk.colliderect(self.player.get_rect()):
                d = 1 if self.villain.facing_right else -1
                dmg = self.villain.config.damage
                if self.villain.current_attack == AttackType.SPECIAL:
                    dmg = self.villain.config.special_damage
                self.player.take_damage(dmg, d)
        
        for h in self.henchmen:
            if h.state != EntityState.DEAD:
                hatk = h.get_attack_rect()
                if hatk and hatk.colliderect(self.player.get_rect()):
                    d = 1 if h.facing_right else -1
                    self.player.take_damage(h.damage, d)
        
        # Pickups
        for pk in self.pickups[:]:
            pk.update()
            if not pk.active:
                self.pickups.remove(pk)
                continue
            if pk.get_rect().colliderect(self.player.get_rect()):
                self.player.health = min(self.player.max_health, self.player.health + pk.heal)
                self.pickups.remove(pk)
        
        # Player death - check for respawn
        if self.player.state == EntityState.DEAD:
            # Try to respawn
            if self.player.respawn():
                # Successfully respawned - continue playing
                # Play respawn sound/effect
                MUSIC.play_sfx('hurt')
            else:
                # No lives left - game over
                self.won = False
                self.state = "game_over"
                MUSIC.stop_ambient()
    
    def draw(self):
        """Draw everything."""
        if self.state == "title":
            self.ui.draw_title(self.screen)
        
        elif self.state == "level_intro" and self.territory:
            self.ui.draw_level_intro(self.screen, self.territory)
        
        elif self.state in ["playing", "paused"] and self.territory and self.player:
            # Background
            self.territory.draw_background(self.screen, int(self.camera_x))
            
            # Pickups
            for pk in self.pickups:
                pk.draw(self.screen, int(self.camera_x))
            
            # Henchmen
            for h in self.henchmen:
                h.draw(self.screen, int(self.camera_x))
            
            # Villain
            if self.villain:
                self.villain.draw(self.screen, int(self.camera_x))
            
            # Player
            self.player.draw(self.screen, int(self.camera_x))
            
            # Projectiles
            for p in self.projectiles:
                p.draw(self.screen, int(self.camera_x))
            
            # HUD
            self.ui.draw_hud(self.screen, self.player, self.territory, self.villain)
            
            if self.state == "paused":
                self.ui.draw_pause(self.screen)
        
        elif self.state == "game_over":
            if self.territory:
                self.territory.draw_background(self.screen, int(self.camera_x))
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
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("BATMAN: ARKHAM SHADOWS v2.0")
    print("=" * 60)
    print("\n7 VILLAIN TERRITORIES TO CONQUER:")
    for i, vt in enumerate(VILLAIN_ORDER):
        cfg = VILLAIN_CONFIGS[vt]
        print(f"  {i+1}. {cfg.territory_name} - {cfg.display_name}")
    print("\nCONTROLS:")
    print("  Arrow/WASD: Move | Space: Jump")
    print("  Z: Punch | X: Kick | C: Batarang")
    print("  P: Pause | ESC: Quit")
    print("=" * 60)
    
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
