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
from typing import Callable, Dict
import threading
import time
import math
import sys
import os
import array

# Try to import pygame for audio playback
try:
    import pygame
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    # Fallback: use winsound on Windows
    try:
        import winsound
        WINSOUND_AVAILABLE = True
    except ImportError:
        WINSOUND_AVAILABLE = False

# Try to import mutagen for MP3 metadata (optional)
try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles

class MusicPlayerApp(tk.Frame):
    """
    Kid-friendly music player application.
    Simulates playing music with visual feedback.
    """
    
    # Pre-loaded songs
    SONGS = [
        {'id': 1, 'title': '🎵 Twinkle Twinkle Little Star', 'duration': 60, 'icon': '⭐', 'filename': 'twinkle_twinkle.mp3'},
        {'id': 2, 'title': '🎶 Old MacDonald Had a Farm', 'duration': 90, 'icon': '🐄', 'filename': 'old_macdonald.mp3'},
        {'id': 3, 'title': '🎵 The Wheels on the Bus', 'duration': 75, 'icon': '🚌', 'filename': 'wheels_on_bus.mp3'},
        {'id': 4, 'title': '🎶 If You\'re Happy and You Know It', 'duration': 45, 'icon': '😊', 'filename': 'happy_clap.mp3'},
        {'id': 5, 'title': '🎵 Baby Shark', 'duration': 120, 'icon': '🦈', 'filename': 'baby_shark.mp3'},
        {'id': 6, 'title': '🎶 Itsy Bitsy Spider', 'duration': 50, 'icon': '🕷️', 'filename': 'itsy_bitsy.mp3'},
        {'id': 7, 'title': '🎵 Row Row Row Your Boat', 'duration': 40, 'icon': '🚣', 'filename': 'row_boat.mp3'},
        {'id': 8, 'title': '🎶 Head Shoulders Knees and Toes', 'duration': 55, 'icon': '🧍', 'filename': 'head_shoulders.mp3'},
    ]
    
    def __init__(self, parent, os_kernel, on_close: Callable = None):
        super().__init__(parent, bg=Styles.get_color('bg_main'))
        self.os_kernel = os_kernel
        self.on_close = on_close
        
        # Player state
        self.current_song = None
        self.is_playing = False
        self.current_time = 0.0  # Use float for more precise time tracking
        self.volume = 70
        self.actual_duration = None  # Actual duration of the audio file in seconds
        self.playback_start_time = None  # When playback started (for tracking position)
        
        # Animation state
        self.animation_running = False
        self.animation_angle = 0
        
        # Audio playback
        self.audio_thread = None
        self.stop_audio = False
        self.using_audio_file = False  # Track if we're using actual audio file
        
        # Get music directory path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.music_dir = os.path.join(base_dir, 'data', 'music')
        
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
        # Stop current playback
        if self.is_playing:
            self._pause()
        
        self.current_song = song
        self.current_time = 0.0
        self.using_audio_file = False
        self.actual_duration = None
        self.playback_start_time = None
        
        # Try to get actual audio file duration
        audio_file_path = self._get_audio_file_path()
        if audio_file_path and os.path.exists(audio_file_path):
            self.actual_duration = self._get_audio_duration(audio_file_path)
            if self.actual_duration:
                self.duration_label.configure(text=self._format_time(int(self.actual_duration)))
            else:
                # Fallback to hardcoded duration if we can't determine actual duration
                self.actual_duration = song['duration']
                self.duration_label.configure(text=self._format_time(song['duration']))
        else:
            # No audio file, use hardcoded duration
            self.actual_duration = song['duration']
            self.duration_label.configure(text=self._format_time(song['duration']))
        
        self.song_title.configure(text=song['title'])
        
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
        self.stop_audio = False
        
        # Resume if paused (using audio file)
        if AUDIO_AVAILABLE and self.using_audio_file and self.playback_start_time is not None:
            try:
                # Adjust playback_start_time so elapsed time continues from current_time
                # We want: elapsed = time.time() - playback_start_time = current_time
                # So: playback_start_time = time.time() - current_time
                self.playback_start_time = time.time() - self.current_time
                pygame.mixer.music.unpause()
            except Exception:
                # If resume fails, restart audio
                self.playback_start_time = time.time()
                self.current_time = 0.0
                self._start_audio()
        else:
            # Start audio playback
            if self.current_time > 0:
                # Resuming from a paused state - adjust start time to account for already played time
                self.playback_start_time = time.time() - self.current_time
            else:
                # Starting fresh
                self.playback_start_time = time.time()
                self.current_time = 0.0
            self._start_audio()
        
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
        self.stop_audio = True
        self._draw_music_icon(0)
        
        # Update current time based on elapsed playback time
        if self.playback_start_time is not None:
            elapsed = time.time() - self.playback_start_time
            self.current_time = elapsed
        
        # Stop audio
        if AUDIO_AVAILABLE:
            try:
                if self.using_audio_file:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.stop()
            except Exception:
                pass
        
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
        # Stop current audio playback
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        
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
        
        # Update audio volume
        if AUDIO_AVAILABLE:
            try:
                # pygame volume is 0.0 to 1.0
                pygame.mixer.music.set_volume(self.volume / 100.0)
            except Exception:
                pass
    
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
        
        # Update current time based on actual playback
        if self.playback_start_time is not None:
            elapsed = time.time() - self.playback_start_time
            self.current_time = elapsed
        else:
            # Fallback: increment by 1 second
            self.current_time += 1.0
        
        # Use actual duration if available, otherwise fall back to hardcoded
        duration = self.actual_duration if self.actual_duration else self.current_song['duration']
        
        # Update time label
        self.time_label.configure(text=self._format_time(int(self.current_time)))
        
        # Update progress bar
        if duration > 0:
            progress_pct = min(self.current_time / duration, 1.0)  # Cap at 100%
            self.progress.delete('all')
            self.progress.create_rectangle(
                0, 0,
                300 * progress_pct, 10,
                fill=Styles.get_color('music'),
                outline=''
            )
        
        # Check if song ended
        # For audio files, check if pygame mixer is still busy
        song_ended = False
        if self.using_audio_file and AUDIO_AVAILABLE:
            try:
                # Check if audio has finished playing
                if not pygame.mixer.music.get_busy() and self.current_time > 1.0:
                    song_ended = True
            except Exception:
                # If we can't check, use time-based check
                if self.current_time >= duration:
                    song_ended = True
        else:
            # For generated audio, use time-based check
            if self.current_time >= duration:
                song_ended = True
        
        if song_ended:
            self._next_song()
            return
        
        # Schedule next update (more frequent for smoother progress)
        self.after(100, self._update_progress)
    
    def _format_time(self, seconds: int) -> str:
        """Format time as M:SS or H:MM:SS if over an hour"""
        if seconds < 3600:
            mins = seconds // 60
            secs = seconds % 60
            return f"{mins}:{secs:02d}"
        else:
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{mins:02d}:{secs:02d}"
    
    def _get_audio_duration(self, file_path: str) -> float:
        """Get the duration of an audio file in seconds"""
        if not file_path or not os.path.exists(file_path):
            return None
        
        # Try mutagen for MP3 files
        if MUTAGEN_AVAILABLE and file_path.lower().endswith('.mp3'):
            try:
                audio_file = MP3(file_path)
                duration = audio_file.info.length
                return duration
            except (ID3NoHeaderError, Exception):
                pass
        
        # Try pygame.Sound for WAV/OGG files
        if AUDIO_AVAILABLE:
            try:
                sound = pygame.mixer.Sound(file_path)
                duration = sound.get_length()
                return duration
            except Exception:
                pass
        
        # If we can't determine duration, return None
        return None
    
    def _start_audio(self):
        """Start audio playback"""
        if AUDIO_AVAILABLE:
            # First try to load actual audio file
            audio_file_path = self._get_audio_file_path()
            if audio_file_path and os.path.exists(audio_file_path):
                self._play_audio_file(audio_file_path)
            else:
                # Fallback to generated tones
                self._play_pygame_audio()
        elif WINSOUND_AVAILABLE:
            # Use winsound as fallback (Windows only)
            self._play_winsound_audio()
        else:
            # No audio available - just visual feedback
            pass
    
    def _get_audio_file_path(self):
        """Get the path to the audio file for the current song"""
        if not self.current_song:
            return None
        
        filename = self.current_song.get('filename', '')
        if not filename:
            return None
        
        # Try the exact filename first
        file_path = os.path.join(self.music_dir, filename)
        if os.path.exists(file_path):
            return file_path
        
        # Try different formats with base name
        base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
        formats = ['.mp3', '.wav', '.ogg', '.m4a']
        
        for fmt in formats:
            file_path = os.path.join(self.music_dir, base_name + fmt)
            if os.path.exists(file_path):
                return file_path
        
        return None
    
    def _play_audio_file(self, file_path):
        """Play an actual audio file using pygame"""
        try:
            self.using_audio_file = True
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.volume / 100.0)
            pygame.mixer.music.play(0)  # Play once (0 = no loops), let it play fully
            
            # Monitor playback in a thread to detect when it ends
            def monitor_playback():
                while self.is_playing and not self.stop_audio:
                    try:
                        if not pygame.mixer.music.get_busy():
                            # Song has finished playing
                            if self.is_playing:
                                # Small delay to ensure UI updates before moving to next song
                                time.sleep(0.5)
                                # The progress update will detect this and move to next song
                                break
                    except Exception:
                        break
                    time.sleep(0.1)
            
            self.audio_thread = threading.Thread(target=monitor_playback, daemon=True)
            self.audio_thread.start()
            
        except Exception as e:
            # If file playback fails, fall back to generated tones
            self.using_audio_file = False
            self._play_pygame_audio()
    
    def _get_song_melody(self, song_id: int):
        """Get the melody notes for a specific song"""
        # Musical note frequencies (in Hz)
        # C4=261.63, D4=293.66, E4=329.63, F4=349.23, G4=392.00, A4=440.00, B4=493.88
        # C5=523.25, D5=587.33, E5=659.25, F5=698.46, G5=783.99, A5=880.00
        
        melodies = {
            1: [  # Twinkle Twinkle Little Star
                (523.25, 0.5), (523.25, 0.5), (659.25, 0.5), (659.25, 0.5),  # C C E E
                (698.46, 0.5), (698.46, 0.5), (659.25, 1.0),  # F F E (long)
                (587.33, 0.5), (587.33, 0.5), (523.25, 0.5), (523.25, 0.5),  # D D C C
                (587.33, 0.5), (587.33, 0.5), (523.25, 1.0),  # D D C (long)
            ],
            2: [  # Old MacDonald Had a Farm
                (523.25, 0.4), (523.25, 0.4), (523.25, 0.4), (392.00, 0.4),  # C C C G
                (440.00, 0.4), (440.00, 0.4), (392.00, 0.8),  # A A G (long)
                (349.23, 0.4), (349.23, 0.4), (392.00, 0.4), (440.00, 0.4),  # F F G A
                (523.25, 0.4), (440.00, 0.4), (392.00, 0.8),  # C A G (long)
            ],
            3: [  # The Wheels on the Bus
                (523.25, 0.5), (587.33, 0.5), (659.25, 0.5), (523.25, 0.5),  # C D E C
                (523.25, 0.5), (587.33, 0.5), (659.25, 0.5), (523.25, 0.5),  # C D E C
                (659.25, 0.5), (698.46, 0.5), (783.99, 1.0),  # E F G (long)
                (659.25, 0.5), (698.46, 0.5), (783.99, 1.0),  # E F G (long)
            ],
            4: [  # If You're Happy and You Know It
                (523.25, 0.3), (523.25, 0.3), (659.25, 0.3), (659.25, 0.3),  # C C E E
                (698.46, 0.3), (698.46, 0.3), (659.25, 0.6),  # F F E (long)
                (587.33, 0.3), (587.33, 0.3), (523.25, 0.3), (523.25, 0.3),  # D D C C
                (587.33, 0.3), (587.33, 0.3), (523.25, 0.6),  # D D C (long)
            ],
            5: [  # Baby Shark
                (392.00, 0.2), (392.00, 0.2), (392.00, 0.2), (392.00, 0.2),  # G G G G
                (440.00, 0.2), (440.00, 0.2), (440.00, 0.2), (440.00, 0.2),  # A A A A
                (523.25, 0.4), (523.25, 0.4), (523.25, 0.4), (523.25, 0.4),  # C C C C
                (440.00, 0.2), (440.00, 0.2), (392.00, 0.4),  # A A G
            ],
            6: [  # Itsy Bitsy Spider
                (523.25, 0.4), (587.33, 0.4), (659.25, 0.4), (523.25, 0.4),  # C D E C
                (659.25, 0.4), (698.46, 0.4), (659.25, 0.4), (587.33, 0.4),  # E F E D
                (523.25, 0.4), (587.33, 0.4), (659.25, 0.4), (523.25, 0.4),  # C D E C
                (587.33, 0.8), (523.25, 0.8),  # D (long) C (long)
            ],
            7: [  # Row Row Row Your Boat
                (523.25, 0.5), (523.25, 0.5), (523.25, 0.5), (659.25, 0.5),  # C C C E
                (698.46, 0.5), (698.46, 0.5), (659.25, 0.5), (523.25, 0.5),  # F F E C
                (587.33, 0.5), (587.33, 0.5), (523.25, 0.5), (392.00, 0.5),  # D D C G
                (523.25, 1.0),  # C (long)
            ],
            8: [  # Head Shoulders Knees and Toes
                (523.25, 0.3), (523.25, 0.3), (659.25, 0.3), (659.25, 0.3),  # C C E E
                (698.46, 0.3), (698.46, 0.3), (659.25, 0.3), (659.25, 0.3),  # F F E E
                (523.25, 0.3), (523.25, 0.3), (587.33, 0.3), (587.33, 0.3),  # C C D D
                (523.25, 0.6), (392.00, 0.6),  # C (long) G (long)
            ],
        }
        
        return melodies.get(song_id, melodies[1])  # Default to Twinkle Twinkle
    
    def _play_pygame_audio(self):
        """Play audio using pygame"""
        try:
            # Generate a simple musical tone using array generation
            sample_rate = 22050
            duration_sec = self.current_song['duration']
            
            # Generate a pleasant tone sequence
            def generate_tone(freq, duration_sec, sample_rate=22050):
                num_samples = int(sample_rate * duration_sec)
                samples = array.array('h')  # signed short integers
                
                for i in range(num_samples):
                    t = float(i) / sample_rate
                    # Generate sine wave with harmonics
                    sample = math.sin(2 * math.pi * freq * t)
                    sample += 0.3 * math.sin(2 * math.pi * freq * 2 * t)
                    sample += 0.1 * math.sin(2 * math.pi * freq * 3 * t)
                    # Normalize and convert to 16-bit integer
                    sample = int(sample * 16383)  # Max value for 16-bit signed
                    samples.append(sample)
                
                return samples
            
            # Get the melody for this specific song
            melody_notes = self._get_song_melody(self.current_song['id'])
            
            # Calculate total melody duration
            total_melody_duration = sum(duration for _, duration in melody_notes)
            
            # Scale note durations to fit the song duration (loop if needed)
            scale_factor = duration_sec / total_melody_duration if total_melody_duration > 0 else 1.0
            if scale_factor < 1.0:
                # Song is shorter than melody, scale down
                melody_notes = [(freq, dur * scale_factor) for freq, dur in melody_notes]
            else:
                # Song is longer, we'll loop the melody
                loops_needed = int(scale_factor) + 1
                original_notes = melody_notes[:]
                for _ in range(loops_needed):
                    if sum(dur for _, dur in melody_notes) >= duration_sec:
                        break
                    melody_notes.extend(original_notes)
                
                # Trim to exact duration
                current_duration = 0
                final_notes = []
                for freq, dur in melody_notes:
                    if current_duration + dur > duration_sec:
                        dur = duration_sec - current_duration
                        if dur > 0:
                            final_notes.append((freq, dur))
                        break
                    final_notes.append((freq, dur))
                    current_duration += dur
                melody_notes = final_notes
            
            # Generate audio for all notes in the melody
            all_samples = array.array('h')
            for freq, note_duration in melody_notes:
                tone_samples = generate_tone(freq, note_duration, sample_rate)
                all_samples.extend(tone_samples)
            
            # Convert array to format pygame can use
            # pygame.sndarray.make_sound can work with array.array directly
            # but we need to convert to a format it understands
            try:
                # Try using numpy if available for better stereo support
                import numpy as np
                audio_array = np.frombuffer(all_samples, dtype=np.int16)
                # Convert to stereo
                stereo = np.zeros((len(audio_array), 2), dtype=np.int16)
                stereo[:, 0] = audio_array
                stereo[:, 1] = audio_array
                sound = pygame.sndarray.make_sound(stereo)
            except (ImportError, ValueError, AttributeError):
                # Fallback: create mono sound from array
                # Convert array.array to list of tuples for stereo simulation
                mono_list = list(all_samples)
                # Create simple stereo by duplicating channels
                stereo_data = [(s, s) for s in mono_list]
                sound = pygame.sndarray.make_sound(stereo_data)
            
            sound.set_volume(self.volume / 100.0)
            
            # Play in a loop
            def play_loop():
                while self.is_playing and not self.stop_audio:
                    sound.play()
                    time.sleep(duration_sec)
                    if not self.is_playing:
                        break
            
            self.audio_thread = threading.Thread(target=play_loop, daemon=True)
            self.audio_thread.start()
            
        except Exception:
            # Fallback to simple beep pattern
            self._play_winsound_audio()
    
    def _play_winsound_audio(self):
        """Play audio using winsound (Windows fallback)"""
        if not WINSOUND_AVAILABLE:
            return
        
        # Get melody for this song
        melody_notes = self._get_song_melody(self.current_song['id'])
        
        def play_beep_pattern():
            beep_duration_ms = 200  # base duration in milliseconds
            while self.is_playing and not self.stop_audio:
                try:
                    # Play the melody pattern
                    for freq, duration in melody_notes:
                        if not self.is_playing or self.stop_audio:
                            break
                        # Convert duration to milliseconds
                        duration_ms = int(duration * 1000)
                        # Limit beep duration (winsound has limits)
                        duration_ms = min(duration_ms, 1000)
                        if duration_ms > 50:  # Only beep if duration is reasonable
                            winsound.Beep(int(freq), duration_ms)
                            time.sleep(0.05)  # Small pause between notes
                    
                    # Small pause before looping
                    if self.is_playing and not self.stop_audio:
                        time.sleep(0.2)
                except Exception:
                    break
        
        self.audio_thread = threading.Thread(target=play_beep_pattern, daemon=True)
        self.audio_thread.start()
    
    def _close_app(self):
        """Close the music player"""
        self.is_playing = False
        self.animation_running = False
        self.stop_audio = True
        
        # Stop audio
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        
        if self.on_close:
            self.on_close()

