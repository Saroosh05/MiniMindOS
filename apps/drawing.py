"""
MiniMind OS - Drawing App
=========================
A simple paint application for kids with:
- Canvas for drawing
- Color palette
- Brush sizes
- Clear and save functions
- Auto-save feature

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import json
import time
import threading
from typing import Callable, List, Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles

class DrawingApp(tk.Frame):
    """
    Kid-friendly drawing application.
    Features color picker, brush sizes, and auto-save.
    """
    
    # Color palette
    COLORS = [
        '#FF0000',  # Red
        '#FF9800',  # Orange
        '#FFEB3B',  # Yellow
        '#4CAF50',  # Green
        '#2196F3',  # Blue
        '#9C27B0',  # Purple
        '#E91E63',  # Pink
        '#795548',  # Brown
        '#000000',  # Black
        '#FFFFFF',  # White
    ]
    
    # Brush sizes
    BRUSH_SIZES = [4, 8, 12, 20, 30]
    
    def __init__(self, parent, os_kernel, on_close: Callable = None):
        super().__init__(parent, bg=Styles.get_color('bg_main'))
        self.os_kernel = os_kernel
        self.filesystem = os_kernel.filesystem
        self.on_close = on_close
        
        # Drawing state
        self.current_color = '#000000'
        self.brush_size = 8
        self.last_x = None
        self.last_y = None
        self.drawing_data: List[dict] = []  # Store drawing for save
        
        # Auto-save
        self.autosave_interval = 30  # seconds
        self.last_save_time = time.time()
        self.modified = False
        
        self._create_widgets()
        self._start_autosave()
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Header with title and close button
        self._create_header()
        
        # Main content area
        content = tk.Frame(self, bg=Styles.get_color('bg_main'))
        content.pack(fill='both', expand=True)
        
        # Tool panel (left side)
        self._create_tool_panel(content)
        
        # Canvas (center)
        self._create_canvas(content)
    
    def _create_header(self):
        """Create header bar"""
        header = tk.Frame(self, bg=Styles.get_color('drawing'), height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Close button
        close_btn = tk.Button(
            header,
            text="← Back",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('drawing'),
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self._close_app
        )
        close_btn.pack(side='left', padx=15, pady=10)
        
        # Title
        title = tk.Label(
            header,
            text="🎨 Drawing",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('drawing'),
            fg='white'
        )
        title.pack(side='left', padx=20, pady=10)
        
        # Save indicator
        self.save_indicator = tk.Label(
            header,
            text="",
            font=Styles.get_font('small'),
            bg=Styles.get_color('drawing'),
            fg='white'
        )
        self.save_indicator.pack(side='right', padx=20)
        
        # Save button
        save_btn = tk.Button(
            header,
            text="💾 Save",
            font=Styles.get_font('normal'),
            bg='white',
            fg=Styles.get_color('drawing'),
            cursor='hand2',
            command=self._save_drawing
        )
        save_btn.pack(side='right', padx=10, pady=10)
        
        # Load button
        load_btn = tk.Button(
            header,
            text="📂 Load",
            font=Styles.get_font('normal'),
            bg='white',
            fg=Styles.get_color('drawing'),
            cursor='hand2',
            command=self._load_drawing
        )
        load_btn.pack(side='right', padx=5, pady=10)
    
    def _create_tool_panel(self, parent):
        """Create the tool panel with colors and brushes"""
        panel = tk.Frame(parent, bg=Styles.get_color('bg_card'), width=120)
        panel.pack(side='left', fill='y', padx=10, pady=10)
        panel.pack_propagate(False)
        
        # Colors section
        color_label = tk.Label(
            panel,
            text="🎨 Colors",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_card')
        )
        color_label.pack(pady=(15, 10))
        
        # Color palette grid
        color_frame = tk.Frame(panel, bg=Styles.get_color('bg_card'))
        color_frame.pack()
        
        self.color_buttons = []
        for i, color in enumerate(self.COLORS):
            row = i // 2
            col = i % 2
            
            btn = tk.Button(
                color_frame,
                bg=color,
                width=3,
                height=1,
                relief='raised',
                cursor='hand2',
                command=lambda c=color: self._select_color(c)
            )
            btn.grid(row=row, column=col, padx=3, pady=3)
            self.color_buttons.append(btn)
        
        # Current color display
        self.current_color_display = tk.Canvas(
            panel,
            width=80,
            height=30,
            bg=self.current_color,
            highlightthickness=2,
            highlightbackground='gray'
        )
        self.current_color_display.pack(pady=15)
        
        # Brush size section
        brush_label = tk.Label(
            panel,
            text="✏️ Brush Size",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_card')
        )
        brush_label.pack(pady=(20, 10))
        
        # Brush size buttons
        for size in self.BRUSH_SIZES:
            btn = tk.Button(
                panel,
                text=f"●",
                font=('Arial', size // 2),
                width=4,
                cursor='hand2',
                command=lambda s=size: self._select_brush_size(s)
            )
            btn.pack(pady=3)
        
        # Eraser button
        eraser_btn = tk.Button(
            panel,
            text="🧹 Eraser",
            font=Styles.get_font('small'),
            cursor='hand2',
            command=lambda: self._select_color('#FFFFFF')
        )
        eraser_btn.pack(pady=15)
        
        # Clear button
        clear_btn = tk.Button(
            panel,
            text="🗑️ Clear",
            font=Styles.get_font('small'),
            bg=Styles.get_color('warning'),
            fg='white',
            cursor='hand2',
            command=self._clear_canvas
        )
        clear_btn.pack(pady=10)
    
    def _create_canvas(self, parent):
        """Create the drawing canvas"""
        canvas_frame = tk.Frame(parent, bg=Styles.get_color('bg_main'))
        canvas_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # Canvas with border
        self.canvas = tk.Canvas(
            canvas_frame,
            bg='white',
            cursor='pencil',
            highlightthickness=3,
            highlightbackground=Styles.get_color('border')
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self._start_draw)
        self.canvas.bind('<B1-Motion>', self._draw)
        self.canvas.bind('<ButtonRelease-1>', self._stop_draw)
    
    def _select_color(self, color: str):
        """Select a drawing color"""
        self.current_color = color
        self.current_color_display.configure(bg=color)
        
        # Log color selection
        self.os_kernel.parental.logger.log(
            "DRAWING",
            f"Selected color: {color}",
            "kid"
        )
    
    def _select_brush_size(self, size: int):
        """Select brush size"""
        self.brush_size = size
    
    def _start_draw(self, event):
        """Start drawing"""
        self.last_x = event.x
        self.last_y = event.y
    
    def _draw(self, event):
        """Draw on canvas"""
        if self.last_x is not None and self.last_y is not None:
            # Draw line
            self.canvas.create_line(
                self.last_x, self.last_y,
                event.x, event.y,
                fill=self.current_color,
                width=self.brush_size,
                capstyle=tk.ROUND,
                smooth=True
            )
            
            # Store for saving
            self.drawing_data.append({
                'type': 'line',
                'x1': self.last_x,
                'y1': self.last_y,
                'x2': event.x,
                'y2': event.y,
                'color': self.current_color,
                'width': self.brush_size
            })
            
            self.last_x = event.x
            self.last_y = event.y
            self.modified = True
    
    def _stop_draw(self, event):
        """Stop drawing"""
        self.last_x = None
        self.last_y = None
    
    def _clear_canvas(self):
        """Clear the canvas"""
        if messagebox.askyesno("Clear", "Clear the canvas? 🎨"):
            self.canvas.delete('all')
            self.drawing_data = []
            self.modified = True
            
            self.os_kernel.parental.logger.log(
                "DRAWING",
                "Canvas cleared",
                "kid"
            )
    
    def _save_drawing(self):
        """Save the drawing to filesystem"""
        if not self.drawing_data:
            messagebox.showinfo("Save", "Nothing to save yet! Draw something first 🎨")
            return
        
        # Generate filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"drawing_{timestamp}.json"
        filepath = f"/kids/drawings/{filename}"
        
        # Save to virtual filesystem
        content = json.dumps({
            'version': '1.0',
            'created': time.time(),
            'data': self.drawing_data
        })
        
        if self.filesystem.create_file(filepath, content, file_type=None):
            self.save_indicator.configure(text=f"✓ Saved: {filename}")
            self.modified = False
            self.last_save_time = time.time()
            
            self.os_kernel.parental.logger.log(
                "DRAWING",
                f"Drawing saved: {filename}",
                "kid"
            )
            
            # Clear indicator after 3 seconds
            self.after(3000, lambda: self.save_indicator.configure(text=""))
        else:
            messagebox.showerror("Error", "Could not save drawing")
    
    def _load_drawing(self):
        """Load a saved drawing"""
        # List available drawings
        contents = self.filesystem.list_directory("/kids/drawings")
        files = contents.get('files', [])
        
        if not files:
            messagebox.showinfo("Load", "No saved drawings found! 📂")
            return
        
        # Create selection dialog
        dialog = tk.Toplevel(self)
        dialog.title("📂 Load Drawing")
        dialog.geometry("300x300")
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="Select a drawing:",
            font=Styles.get_font('normal')
        ).pack(pady=10)
        
        listbox = tk.Listbox(dialog, font=Styles.get_font('normal'))
        listbox.pack(fill='both', expand=True, padx=20, pady=10)
        
        for f in files:
            listbox.insert('end', f['name'])
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                selected_file = files[selection[0]]
                self._do_load(selected_file['path'])
                dialog.destroy()
        
        tk.Button(
            dialog,
            text="Load",
            font=Styles.get_font('normal'),
            command=load_selected
        ).pack(pady=10)
    
    def _do_load(self, filepath: str):
        """Actually load the drawing file"""
        content = self.filesystem.read_file(filepath)
        if content:
            try:
                data = json.loads(content)
                self.canvas.delete('all')
                self.drawing_data = data.get('data', [])
                
                # Redraw
                for item in self.drawing_data:
                    if item['type'] == 'line':
                        self.canvas.create_line(
                            item['x1'], item['y1'],
                            item['x2'], item['y2'],
                            fill=item['color'],
                            width=item['width'],
                            capstyle=tk.ROUND,
                            smooth=True
                        )
                
                self.os_kernel.parental.logger.log(
                    "DRAWING",
                    f"Drawing loaded: {filepath}",
                    "kid"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Could not load drawing: {e}")
    
    def _start_autosave(self):
        """Start auto-save timer"""
        def autosave_loop():
            while True:
                time.sleep(self.autosave_interval)
                if self.modified and self.drawing_data:
                    # Schedule save on main thread
                    try:
                        self.after(0, self._autosave)
                    except:
                        break
        
        self.autosave_thread = threading.Thread(target=autosave_loop, daemon=True)
        self.autosave_thread.start()
    
    def _autosave(self):
        """Perform auto-save"""
        if self.modified and self.drawing_data:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"autosave_{timestamp}.json"
            filepath = f"/kids/drawings/{filename}"
            
            content = json.dumps({
                'version': '1.0',
                'created': time.time(),
                'autosave': True,
                'data': self.drawing_data
            })
            
            if self.filesystem.create_file(filepath, content):
                self.save_indicator.configure(text="💾 Auto-saved")
                self.modified = False
                self.after(2000, lambda: self.save_indicator.configure(text=""))
    
    def _close_app(self):
        """Close the drawing app"""
        if self.modified and self.drawing_data:
            if messagebox.askyesno("Save?", "Save your drawing before closing? 💾"):
                self._save_drawing()
        
        if self.on_close:
            self.on_close()

