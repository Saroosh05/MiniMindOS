"""
MiniMind OS - Main Launcher
===========================
A child-friendly operating system prototype for educational purposes.

Features:
- Safe, sandboxed environment for kids (ages 2-8)
- Parental controls with password protection
- Time limits and bedtime scheduling
- Educational apps: Drawing, Stories, Music, Puzzles
- Core OS modules: Process Management, Memory, File System, Security

Roll Numbers: 2023-CS-67, 2023-CS-63

Usage:
    python main.py

Requirements:
    - Python 3.8+
    - Tkinter (usually comes with Python)
"""

import tkinter as tk
from tkinter import messagebox
import threading
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import OS core modules
from os_core.process_manager import ProcessManager
from os_core.memory_manager import MemoryManager
from os_core.scheduler import Scheduler
from os_core.hardware import Hardware

# Import file system
from filesystem.fs import FileSystem

# Import security
from security.parental_control import ParentalControl

# Import UI
from ui.styles import Styles
from ui.home_screen import HomeScreen
from ui.parent_panel import ParentPanel
from ui.process_viewer import ProcessViewer, MemoryViewer

# Import apps
from apps.drawing import DrawingApp
from apps.story_reader import StoryReaderApp
from apps.music_player import MusicPlayerApp
from apps.puzzle import PuzzleApp

class MiniMindOS:
    """
    Main OS Kernel for MiniMind OS.
    Integrates all OS components and manages the GUI.
    """
    
    VERSION = "1.0.0"
    TITLE = "MiniMind OS"
    
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title(f"🌟 {self.TITLE} v{self.VERSION}")
        self.root.geometry(f"{Styles.DIMENSIONS['window_width']}x{Styles.DIMENSIONS['window_height']}")
        self.root.minsize(800, 600)
        self.root.configure(bg=Styles.get_color('bg_main'))
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap(default='')  # Windows
        except:
            pass
        
        # Data path for persistence
        self.data_path = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize OS components
        self._init_os_components()
        
        # Current active view
        self.current_view = None
        self.current_app_pid = None
        
        # Start with home screen
        self._show_home()
        
        # Start background services
        self._start_services()
        
        # Bind window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Log startup
        self.parental.logger.log("SYSTEM", "MiniMind OS started", "system")
    
    def _init_os_components(self):
        """Initialize all OS core components"""
        # Activity logger (used by all components)
        self.logger = None  # Will use parental control's logger
        
        # Memory Manager
        self.memory_manager = MemoryManager()
        
        # Process Manager
        self.process_manager = ProcessManager(
            memory_manager=self.memory_manager
        )
        
        # Scheduler
        self.scheduler = Scheduler(
            process_manager=self.process_manager
        )
        
        # Hardware simulation
        self.hardware = Hardware(memory_manager=self.memory_manager)
        
        # File System
        self.filesystem = FileSystem(data_path=self.data_path)
        
        # Parental Control
        self.parental = ParentalControl(data_path=self.data_path)
        
        # Connect logger to all components
        self.memory_manager.logger = self.parental.logger
        self.process_manager.logger = self.parental.logger
        self.scheduler.logger = self.parental.logger
        self.filesystem.logger = self.parental.logger
        
        # Register parental control callbacks
        self.parental.on_lock(self._on_system_lock)
        self.parental.on_time_warning(self._on_time_warning)
    
    def _start_services(self):
        """Start background services"""
        # Start scheduler
        self.scheduler.start()
        
        # Start status update loop
        self._update_status()
    
    def _update_status(self):
        """Periodically update status displays"""
        if hasattr(self, 'home_screen') and self.home_screen:
            try:
                self.home_screen.update_status()
                self.home_screen.update_app_states()
            except:
                pass
        
        # Check for lock conditions
        self.parental.check_and_lock()
        
        # Schedule next update
        self.root.after(1000, self._update_status)
    
    def _show_home(self):
        """Show the home screen"""
        self._clear_view()
        
        self.home_screen = HomeScreen(
            self.root,
            self,
            on_app_launch=self._launch_app
        )
        self.home_screen.pack(fill='both', expand=True)
        self.current_view = self.home_screen
    
    def _clear_view(self):
        """Clear current view"""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
        self.home_screen = None
    
    def _launch_app(self, app_id: str):
        """Launch an application"""
        # Allow parent panel to launch even when locked (parents need access)
        if self.parental.is_locked and app_id != 'parent_panel':
            messagebox.showinfo(
                "System Locked 🔒",
                self.parental.lock_reason
            )
            return
        
        # Check if app is allowed
        if not self.parental.is_app_allowed(app_id) and app_id != 'parent_panel':
            messagebox.showinfo(
                "App Locked 🔒",
                "This app is locked. Ask a parent to unlock it."
            )
            return
        
        self._clear_view()
        
        # App configurations
        app_config = {
            'drawing': {
                'class': DrawingApp,
                'name': 'Drawing App',
                'memory': 128,
                'priority': 4,
                'icon': '🎨'
            },
            'stories': {
                'class': StoryReaderApp,
                'name': 'Story Reader',
                'memory': 64,
                'priority': 3,
                'icon': '📚'
            },
            'music': {
                'class': MusicPlayerApp,
                'name': 'Music Player',
                'memory': 96,
                'priority': 3,
                'icon': '🎵'
            },
            'puzzle': {
                'class': PuzzleApp,
                'name': 'Puzzle Games',
                'memory': 80,
                'priority': 4,
                'icon': '🧩'
            },
            'parent_panel': {
                'class': ParentPanel,
                'name': 'Parent Panel',
                'memory': 64,
                'priority': 5,
                'icon': '👨‍👩‍👧'
            }
        }
        
        if app_id not in app_config:
            messagebox.showerror("Error", f"Unknown app: {app_id}")
            self._show_home()
            return
        
        config = app_config[app_id]
        
        # Create process for the app
        pid = self.process_manager.create_process(
            name=config['name'],
            priority=config['priority'],
            memory_required=config['memory'],
            icon=config['icon']
        )
        
        if pid is None:
            messagebox.showerror(
                "Error",
                "Not enough memory to start app!\nClose some apps and try again."
            )
            self._show_home()
            return
        
        self.current_app_pid = pid
        
        # Add to scheduler
        self.scheduler.add_process(pid, config['priority'])
        
        # Create and show app
        if app_id == 'parent_panel':
            app = config['class'](
                self.root,
                self,
                on_exit=lambda: self._close_app(pid)
            )
        else:
            app = config['class'](
                self.root,
                self,
                on_close=lambda: self._close_app(pid)
            )
        
        app.pack(fill='both', expand=True)
        self.current_view = app
    
    def _close_app(self, pid: int = None):
        """Close current app and return to home"""
        if pid:
            self.process_manager.terminate_process(pid)
            self.scheduler.remove_process(pid)
        
        self.current_app_pid = None
        self._show_home()
    
    def _on_system_lock(self, reason: str):
        """Handle system lock event"""
        # Close current app
        if self.current_app_pid:
            self._close_app(self.current_app_pid)
        
        # Show lock message
        messagebox.showinfo("System Locked 🔒", reason)
    
    def _on_time_warning(self, minutes_remaining: int):
        """Handle time warning"""
        messagebox.showwarning(
            "Time Warning ⏰",
            f"Only {minutes_remaining} minutes remaining!"
        )
    
    def show_process_viewer(self):
        """Show the process viewer window"""
        ProcessViewer(self.root, self, self.parental.is_parent_mode)
    
    def show_memory_viewer(self):
        """Show the memory viewer window"""
        MemoryViewer(self.root, self)
    
    def _on_close(self):
        """Handle window close"""
        # Save all data
        self.parental._save_settings()
        self.filesystem._save_filesystem()
        
        # Stop services
        self.scheduler.stop()
        self.hardware.shutdown()
        self.parental.shutdown()
        
        # Log shutdown
        self.parental.logger.log("SYSTEM", "MiniMind OS shutdown", "system")
        
        # Close window
        self.root.destroy()
    
    def run(self):
        """Start the OS main loop"""
        try:
            print(f"""
================================================================
                                                              
       Welcome to MiniMind OS v{self.VERSION}                    
                                                              
  A child-friendly operating system prototype                 
                                                              
  Roll Numbers: 2023-CS-67, 2023-CS-63                       
                                                              
  Features:                                                   
  - Process Management                                        
  - Memory Management                                         
  - Virtual File System                                       
  - Parental Controls                                         
  - Educational Apps                                          
                                                              
================================================================
            """)
        except:
            print("MiniMind OS Starting...")
        
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        os_instance = MiniMindOS()
        os_instance.run()
    except Exception as e:
        print(f"Error starting MiniMind OS: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()

