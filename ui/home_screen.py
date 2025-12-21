"""
MiniMind OS - Home Screen
=========================
Main home screen with app launcher for kids.
Features large, colorful icons and simple navigation.

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Callable, Optional
from .styles import Styles

class HomeScreen(tk.Frame):
    """
    Main home screen for MiniMind OS.
    Displays app icons in a kid-friendly grid layout.
    """
    
    def __init__(self, parent, os_kernel, on_app_launch: Callable = None):
        super().__init__(parent, bg=Styles.get_color('bg_main'))
        self.os_kernel = os_kernel
        self.on_app_launch = on_app_launch
        
        # App definitions
        self.apps = [
            {'name': 'Drawing', 'id': 'drawing', 'icon': '🎨', 'color': '#FF6B6B'},
            {'name': 'Stories', 'id': 'stories', 'icon': '📚', 'color': '#9B59B6'},
            {'name': 'Music', 'id': 'music', 'icon': '🎵', 'color': '#3498DB'},
            {'name': 'Puzzle', 'id': 'puzzle', 'icon': '🧩', 'color': '#2ECC71'},
        ]
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Header
        self._create_header()
        
        # App Grid
        self._create_app_grid()
        
        # Status Bar
        self._create_status_bar()
    
    def _create_header(self):
        """Create the header with title and time"""
        header = tk.Frame(self, bg=Styles.get_color('primary'), height=80)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        # Title
        title = tk.Label(
            header,
            text="🌟 MiniMind OS 🌟",
            font=Styles.get_font('title'),
            bg=Styles.get_color('primary'),
            fg=Styles.get_color('text_light')
        )
        title.pack(pady=15)
        
        # Time display
        self.time_label = tk.Label(
            header,
            text="",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('primary'),
            fg=Styles.get_color('text_light')
        )
        self.time_label.place(relx=0.95, rely=0.5, anchor='e')
        
        # Parent mode button (small, in corner)
        parent_btn = tk.Button(
            header,
            text="👨‍👩‍👧",
            font=('Segoe UI Emoji', 20),
            bg=Styles.get_color('primary'),
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self._open_parent_mode
        )
        parent_btn.place(relx=0.02, rely=0.5, anchor='w')
    
    def _create_app_grid(self):
        """Create the grid of app icons"""
        # Container for centering
        container = tk.Frame(self, bg=Styles.get_color('bg_main'))
        container.pack(expand=True, fill='both', pady=50)
        
        # Inner frame for app icons
        grid_frame = tk.Frame(container, bg=Styles.get_color('bg_main'))
        grid_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Create app buttons
        self.app_buttons: Dict[str, tk.Frame] = {}
        
        for i, app in enumerate(self.apps):
            row = i // 2
            col = i % 2
            
            btn = self._create_app_button(grid_frame, app)
            btn.grid(row=row, column=col, padx=40, pady=40)
            self.app_buttons[app['id']] = btn
    
    def _create_app_button(self, parent, app: Dict) -> tk.Frame:
        """Create a single app button with icon and label"""
        # Container frame
        frame = tk.Frame(
            parent,
            bg=app['color'],
            cursor='hand2',
            width=160,
            height=180
        )
        frame.pack_propagate(False)
        
        # Icon
        icon_label = tk.Label(
            frame,
            text=app['icon'],
            font=('Segoe UI Emoji', 64),
            bg=app['color'],
            fg='white'
        )
        icon_label.pack(expand=True, pady=(20, 5))
        
        # Name label
        name_label = tk.Label(
            frame,
            text=app['name'],
            font=Styles.get_font('button'),
            bg=app['color'],
            fg='white'
        )
        name_label.pack(pady=(0, 15))
        
        # Bind click events
        for widget in [frame, icon_label, name_label]:
            widget.bind('<Button-1>', lambda e, a=app: self._launch_app(a))
            widget.bind('<Enter>', lambda e, f=frame, c=app['color']: self._on_hover(f, c, True))
            widget.bind('<Leave>', lambda e, f=frame, c=app['color']: self._on_hover(f, c, False))
        
        return frame
    
    def _on_hover(self, frame: tk.Frame, color: str, entering: bool):
        """Handle hover effects"""
        if entering:
            # Lighten color on hover
            frame.configure(bg=self._lighten_color(color))
            for child in frame.winfo_children():
                child.configure(bg=self._lighten_color(color))
        else:
            frame.configure(bg=color)
            for child in frame.winfo_children():
                child.configure(bg=color)
    
    def _lighten_color(self, hex_color: str) -> str:
        """Lighten a hex color"""
        # Remove # and convert to RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        
        # Lighten
        factor = 1.15
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _create_status_bar(self):
        """Create the bottom status bar"""
        status = tk.Frame(self, bg=Styles.get_color('bg_dark'), height=50)
        status.pack(fill='x', side='bottom')
        status.pack_propagate(False)
        
        # Memory usage
        self.memory_label = tk.Label(
            status,
            text="Memory: --",
            font=Styles.get_font('small'),
            bg=Styles.get_color('bg_dark'),
            fg=Styles.get_color('text_light')
        )
        self.memory_label.pack(side='left', padx=20, pady=10)
        
        # Process count
        self.process_label = tk.Label(
            status,
            text="Processes: --",
            font=Styles.get_font('small'),
            bg=Styles.get_color('bg_dark'),
            fg=Styles.get_color('text_light')
        )
        self.process_label.pack(side='left', padx=20, pady=10)
        
        # Time remaining
        self.remaining_label = tk.Label(
            status,
            text="⏰ Time: --",
            font=Styles.get_font('small'),
            bg=Styles.get_color('bg_dark'),
            fg=Styles.get_color('accent')
        )
        self.remaining_label.pack(side='right', padx=20, pady=10)
    
    def _launch_app(self, app: Dict):
        """Launch an app"""
        # Check if app is allowed
        if not self.os_kernel.parental.is_app_allowed(app['id']):
            messagebox.showinfo(
                "App Locked 🔒",
                f"Sorry! {app['name']} is locked.\nAsk a parent to unlock it."
            )
            return
        
        # Check if system is locked
        if self.os_kernel.parental.is_locked:
            messagebox.showinfo(
                "System Locked 🔒",
                self.os_kernel.parental.lock_reason
            )
            return
        
        # Log the app launch
        self.os_kernel.parental.logger.log(
            "APP_LAUNCH",
            f"Launched {app['name']}",
            "kid"
        )
        
        # Callback to launch the app
        if self.on_app_launch:
            self.on_app_launch(app['id'])
    
    def _open_parent_mode(self):
        """Open the parent mode dialog"""
        from .parent_panel import PasswordDialog
        
        dialog = PasswordDialog(self, self.os_kernel.parental)
        self.wait_window(dialog)
        
        if self.os_kernel.parental.is_parent_mode:
            # Open parent panel
            if self.on_app_launch:
                self.on_app_launch('parent_panel')
    
    def update_status(self):
        """Update the status bar with current info"""
        # Update time
        if hasattr(self.os_kernel, 'hardware'):
            time_str = self.os_kernel.hardware.get_system_time()
            self.time_label.configure(text=time_str)
        
        # Update memory
        if hasattr(self.os_kernel, 'memory_manager'):
            stats = self.os_kernel.memory_manager.get_stats()
            self.memory_label.configure(
                text=f"Memory: {stats['used']}/{stats['total']} KB ({stats['percent']:.0f}%)"
            )
        
        # Update process count
        if hasattr(self.os_kernel, 'process_manager'):
            count = self.os_kernel.process_manager.get_process_count()
            self.process_label.configure(text=f"Processes: {count}")
        
        # Update remaining time
        if hasattr(self.os_kernel, 'parental'):
            remaining = self.os_kernel.parental.get_remaining_time()
            self.remaining_label.configure(text=f"⏰ Time: {remaining} min left")
    
    def update_app_states(self):
        """Update app button states based on permissions"""
        for app in self.apps:
            btn = self.app_buttons.get(app['id'])
            if btn:
                is_allowed = self.os_kernel.parental.is_app_allowed(app['id'])
                
                if is_allowed:
                    # Normal state
                    btn.configure(bg=app['color'])
                    for child in btn.winfo_children():
                        child.configure(bg=app['color'])
                else:
                    # Disabled/locked state
                    btn.configure(bg='#CCCCCC')
                    for child in btn.winfo_children():
                        child.configure(bg='#CCCCCC')

