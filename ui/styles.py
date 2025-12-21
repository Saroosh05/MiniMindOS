"""
MiniMind OS - UI Styles
=======================
Centralized styling for kid-friendly UI.
Uses bright, playful colors and large fonts.

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

class Styles:
    """
    Centralized styling constants for MiniMind OS.
    Kid-friendly colors, fonts, and dimensions.
    """
    
    # Color Palette - Bright & Playful
    COLORS = {
        # Primary colors
        'primary': '#FF6B6B',        # Coral Red
        'secondary': '#4ECDC4',      # Turquoise
        'accent': '#FFE66D',         # Sunny Yellow
        
        # Background colors
        'bg_main': '#F7F9FC',        # Light gray-blue
        'bg_card': '#FFFFFF',        # White
        'bg_dark': '#2C3E50',        # Dark blue-gray
        
        # App colors
        'drawing': '#FF6B6B',        # Red
        'stories': '#9B59B6',        # Purple
        'music': '#3498DB',          # Blue
        'puzzle': '#2ECC71',         # Green
        'settings': '#95A5A6',       # Gray
        
        # Status colors
        'success': '#2ECC71',        # Green
        'warning': '#F39C12',        # Orange
        'error': '#E74C3C',          # Red
        'info': '#3498DB',           # Blue
        
        # Text colors
        'text_dark': '#2C3E50',
        'text_light': '#FFFFFF',
        'text_muted': '#7F8C8D',
        
        # UI elements
        'border': '#E0E0E0',
        'shadow': '#00000020',
        'overlay': '#00000080',
    }
    
    # Fonts
    FONTS = {
        'family': 'Comic Sans MS',   # Kid-friendly font
        'family_alt': 'Arial Rounded MT Bold',
        
        # Sizes
        'size_title': 36,
        'size_heading': 24,
        'size_large': 20,
        'size_normal': 16,
        'size_small': 12,
        
        # Font tuples for Tkinter
        'title': ('Comic Sans MS', 36, 'bold'),
        'heading': ('Comic Sans MS', 24, 'bold'),
        'large': ('Comic Sans MS', 20),
        'normal': ('Comic Sans MS', 16),
        'small': ('Comic Sans MS', 12),
        'button': ('Comic Sans MS', 18, 'bold'),
        'icon': ('Segoe UI Emoji', 48),
    }
    
    # Dimensions
    DIMENSIONS = {
        # Window
        'window_width': 1024,
        'window_height': 768,
        
        # App icons
        'icon_size': 120,
        'icon_radius': 20,
        
        # Buttons
        'button_width': 150,
        'button_height': 50,
        'button_radius': 15,
        
        # Padding
        'padding_large': 30,
        'padding_normal': 15,
        'padding_small': 8,
        
        # Taskbar
        'taskbar_height': 60,
    }
    
    # App Icons (Emoji)
    APP_ICONS = {
        'drawing': '🎨',
        'stories': '📚',
        'music': '🎵',
        'puzzle': '🧩',
        'settings': '⚙️',
        'parent': '👨‍👩‍👧',
        'home': '🏠',
        'close': '✖️',
        'back': '◀️',
        'save': '💾',
        'play': '▶️',
        'pause': '⏸️',
        'next': '⏭️',
        'prev': '⏮️',
        'lock': '🔒',
        'unlock': '🔓',
        'time': '⏰',
        'star': '⭐',
    }
    
    # Animation settings
    ANIMATION = {
        'hover_duration': 100,       # ms
        'click_duration': 50,        # ms
        'transition_duration': 200,  # ms
    }
    
    @classmethod
    def get_color(cls, name: str) -> str:
        """Get a color by name with fallback"""
        return cls.COLORS.get(name, '#000000')
    
    @classmethod
    def get_font(cls, name: str) -> tuple:
        """Get a font tuple by name"""
        return cls.FONTS.get(name, cls.FONTS['normal'])
    
    @classmethod
    def get_app_color(cls, app_name: str) -> str:
        """Get the color for an app"""
        return cls.COLORS.get(app_name.lower(), cls.COLORS['primary'])
    
    @classmethod
    def get_app_icon(cls, app_name: str) -> str:
        """Get the icon for an app"""
        return cls.APP_ICONS.get(app_name.lower(), '📱')

