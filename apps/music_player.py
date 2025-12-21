"""
MiniMind OS - Music Player App
==============================
A simple music player for kids with:
- Pre-loaded songs (simulated)
- Play/pause controls
- Visual animation
- Volume control

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, List, Dict
import threading
import time
import math

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles

class MusicPlayerApp(tk.Frame):
    """
    Kid-friendly music player application.
    Simulates playing music with visual feedback.
    """
    
    # Pre-loaded songs (simulated)
    SONGS = [
        {'id': 1, 'title': '🎵 Twinkle Twinkle Little Star', 'duration': 60, 'icon': '⭐'},
        {'id': 2, 'title': '🎶 Old MacDonald Had a Farm', 'duration': 90, 'icon': '🐄'},
        {'id': 3, 'title': '🎵 The Wheels on the Bus', 'duration': 75, 'icon': '🚌'},
        {'id': 4, 'title': '🎶 If You\'re Happy and You Know It', 'duration': 45, 'icon': '😊'},
        {'id': 5, 'title': '🎵 Baby Shark', 'duration': 120, 'icon': '🦈'},
        {'id': 6, 'title': '🎶 Itsy Bitsy Spider', 'duration': 50, 'icon': '🕷️'},
        {'id': 7, 'title': '🎵 Row Row Row Your Boat', 'duration': 40, 'icon': '🚣'},
        {'id': 8, 'title': '🎶 Head Shoulders Knees and Toes', 'duration': 55, 'icon': '🧍'},
    ]
    
    def __init__(self, parent, os_kernel, on_close: Callable = None):
        super().__init__(parent, bg=Styles.get_color('bg_main'))
        self.os_kernel = os_kernel
        self.on_close = on_close
        
        # Player state
        self.current_song = None
        self.is_playing = False
        self.current_time = 0
        self.volume = 70
        
        # Animation state
        self.animation_running = False
        self.animation_angle = 0
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Header
        self._create_header()
        
        # Main content
        content = tk.Frame(self, bg=Styles.get_color('bg_main'))
        content.pack(fill='both', expand=True)
        
        # Left: Song list
        self._create_song_list(content)
        
        # Right: Player controls
        self._create_player(content)
    
    def _create_header(self):
        """Create header bar"""
        header = tk.Frame(self, bg=Styles.get_color('music'), height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Back button
        close_btn = tk.Button(
            header,
            text="← Back",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('music'),
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self._close_app
        )
        close_btn.pack(side='left', padx=15, pady=10)
        
        # Title
        title = tk.Label(
            header,
            text="🎵 Music Player",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('music'),
            fg='white'
        )
        title.pack(side='left', padx=20, pady=10)
    
    def _create_song_list(self, parent):
        """Create the song list panel"""
        list_frame = tk.Frame(parent, bg=Styles.get_color('bg_card'), width=350)
        list_frame.pack(side='left', fill='y', padx=10, pady=10)
        list_frame.pack_propagate(False)
        
        # Title
        tk.Label(
            list_frame,
            text="🎶 Songs",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('bg_card')
        ).pack(pady=15)
        
        # Song buttons
        for song in self.SONGS:
            btn = tk.Button(
                list_frame,
                text=f"{song['icon']} {song['title'].split(' ', 1)[1]}",
                font=Styles.get_font('normal'),
                width=28,
                anchor='w',
                cursor='hand2',
                command=lambda s=song: self._select_song(s)
            )
            btn.pack(pady=5, padx=10)
    
    def _create_player(self, parent):
        """Create the player control panel"""
        player_frame = tk.Frame(parent, bg=Styles.get_color('bg_card'))
        player_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # Now playing section
        self.now_playing_frame = tk.Frame(player_frame, bg=Styles.get_color('bg_card'))
        self.now_playing_frame.pack(fill='x', pady=30)
        
        # Album art / animation canvas
        self.art_canvas = tk.Canvas(
            self.now_playing_frame,
            width=200,
            height=200,
            bg=Styles.get_color('music'),
            highlightthickness=0
        )
        self.art_canvas.pack(pady=20)
        
        # Draw initial music note
        self._draw_music_icon()
        
        # Song title
        self.song_title = tk.Label(
            self.now_playing_frame,
            text="Select a song to play! 🎵",
            font=Styles.get_font('large'),
            bg=Styles.get_color('bg_card'),
            fg=Styles.get_color('text_dark')
        )
        self.song_title.pack(pady=10)
        
        # Progress section
        progress_frame = tk.Frame(player_frame, bg=Styles.get_color('bg_card'))
        progress_frame.pack(fill='x', padx=40, pady=20)
        
        self.time_label = tk.Label(
            progress_frame,
            text="0:00",
            font=Styles.get_font('small'),
            bg=Styles.get_color('bg_card')
        )
        self.time_label.pack(side='left')
        
        self.progress = tk.Canvas(
            progress_frame,
            width=300,
            height=10,
            bg='lightgray',
            highlightthickness=0
        )
        self.progress.pack(side='left', padx=10)
        
        self.duration_label = tk.Label(
            progress_frame,
            text="0:00",
            font=Styles.get_font('small'),
            bg=Styles.get_color('bg_card')
        )
        self.duration_label.pack(side='left')
        
        # Control buttons
        controls_frame = tk.Frame(player_frame, bg=Styles.get_color('bg_card'))
        controls_frame.pack(pady=20)
        
        # Previous
        prev_btn = tk.Button(
            controls_frame,
            text="⏮️",
            font=('Segoe UI Emoji', 24),
            bg=Styles.get_color('bg_card'),
            relief='flat',
            cursor='hand2',
            command=self._prev_song
        )
        prev_btn.pack(side='left', padx=15)
        
        # Play/Pause
        self.play_btn = tk.Button(
            controls_frame,
            text="▶️",
            font=('Segoe UI Emoji', 36),
            bg=Styles.get_color('music'),
            fg='white',
            width=3,
            cursor='hand2',
            command=self._toggle_play
        )
        self.play_btn.pack(side='left', padx=15)
        
        # Next
        next_btn = tk.Button(
            controls_frame,
            text="⏭️",
            font=('Segoe UI Emoji', 24),
            bg=Styles.get_color('bg_card'),
            relief='flat',
            cursor='hand2',
            command=self._next_song
        )
        next_btn.pack(side='left', padx=15)
        
        # Volume control
        volume_frame = tk.Frame(player_frame, bg=Styles.get_color('bg_card'))
        volume_frame.pack(pady=20)
        
        tk.Label(
            volume_frame,
            text="🔊",
            font=('Segoe UI Emoji', 16),
            bg=Styles.get_color('bg_card')
        ).pack(side='left')
        
        self.volume_scale = tk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient='horizontal',
            length=200,
            bg=Styles.get_color('bg_card'),
            highlightthickness=0,
            command=self._set_volume
        )
        self.volume_scale.set(self.volume)
        self.volume_scale.pack(side='left', padx=10)
    
    def _draw_music_icon(self, angle: float = 0):
        """Draw the music icon/animation"""
        self.art_canvas.delete('all')
        
        cx, cy = 100, 100  # Center
        
        if self.is_playing:
            # Animated equalizer bars
            colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3']
            for i in range(5):
                x = 40 + i * 30
                height = 40 + 60 * abs(math.sin(angle + i * 0.5))
                self.art_canvas.create_rectangle(
                    x, 160 - height,
                    x + 20, 160,
                    fill=colors[i % len(colors)],
                    outline=''
                )
        else:
            # Static music note
            self.art_canvas.create_text(
                cx, cy,
                text="🎵",
                font=('Segoe UI Emoji', 72),
                fill='white'
            )
    
    def _select_song(self, song: Dict):
        """Select a song to play"""
        self.current_song = song
        self.current_time = 0
        self.song_title.configure(text=song['title'])
        self.duration_label.configure(text=self._format_time(song['duration']))
        
        self.os_kernel.parental.logger.log(
            "MUSIC",
            f"Selected: {song['title']}",
            "kid"
        )
        
        # Start playing
        self._play()
    
    def _toggle_play(self):
        """Toggle play/pause"""
        if not self.current_song:
            messagebox.showinfo("Music", "Please select a song first! 🎵")
            return
        
        if self.is_playing:
            self._pause()
        else:
            self._play()
    
    def _play(self):
        """Start playing"""
        if not self.current_song:
            return
        
        self.is_playing = True
        self.play_btn.configure(text="⏸️")
        
        # Start animation
        self.animation_running = True
        self._animate()
        
        # Start progress update
        self._update_progress()
        
        self.os_kernel.parental.logger.log(
            "MUSIC",
            f"Playing: {self.current_song['title']}",
            "kid"
        )
    
    def _pause(self):
        """Pause playback"""
        self.is_playing = False
        self.play_btn.configure(text="▶️")
        self.animation_running = False
        self._draw_music_icon(0)
        
        self.os_kernel.parental.logger.log(
            "MUSIC",
            "Paused",
            "kid"
        )
    
    def _prev_song(self):
        """Go to previous song"""
        if not self.current_song:
            return
        
        current_idx = next(
            (i for i, s in enumerate(self.SONGS) if s['id'] == self.current_song['id']),
            0
        )
        prev_idx = (current_idx - 1) % len(self.SONGS)
        self._select_song(self.SONGS[prev_idx])
    
    def _next_song(self):
        """Go to next song"""
        if not self.current_song:
            self._select_song(self.SONGS[0])
            return
        
        current_idx = next(
            (i for i, s in enumerate(self.SONGS) if s['id'] == self.current_song['id']),
            0
        )
        next_idx = (current_idx + 1) % len(self.SONGS)
        self._select_song(self.SONGS[next_idx])
    
    def _set_volume(self, value):
        """Set volume level"""
        self.volume = int(value)
        
        # Check parental volume limit
        max_vol = self.os_kernel.parental.policy.max_volume
        if self.volume > max_vol:
            self.volume = max_vol
            self.volume_scale.set(max_vol)
    
    def _animate(self):
        """Run animation loop"""
        if self.animation_running and self.winfo_exists():
            self.animation_angle += 0.2
            self._draw_music_icon(self.animation_angle)
            self.after(50, self._animate)
    
    def _update_progress(self):
        """Update progress bar"""
        if not self.is_playing or not self.current_song:
            return
        
        if not self.winfo_exists():
            return
        
        self.current_time += 1
        
        # Update time label
        self.time_label.configure(text=self._format_time(self.current_time))
        
        # Update progress bar
        progress_pct = self.current_time / self.current_song['duration']
        self.progress.delete('all')
        self.progress.create_rectangle(
            0, 0,
            300 * progress_pct, 10,
            fill=Styles.get_color('music'),
            outline=''
        )
        
        # Check if song ended
        if self.current_time >= self.current_song['duration']:
            self._next_song()
            return
        
        # Schedule next update
        self.after(1000, self._update_progress)
    
    def _format_time(self, seconds: int) -> str:
        """Format time as M:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"
    
    def _close_app(self):
        """Close the music player"""
        self.is_playing = False
        self.animation_running = False
        
        if self.on_close:
            self.on_close()

