"""
MiniMind OS - Puzzle Game App
=============================
A simple puzzle game for kids with:
- Shape matching
- Color sorting
- Memory game
- Educational content

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import tkinter as tk
from tkinter import messagebox
import random
from typing import Callable, List, Dict, Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles

class PuzzleApp(tk.Frame):
    """
    Kid-friendly puzzle game application.
    Multiple puzzle types for learning and fun.
    """
    
    def __init__(self, parent, os_kernel, on_close: Callable = None):
        super().__init__(parent, bg=Styles.get_color('bg_main'))
        self.os_kernel = os_kernel
        self.on_close = on_close
        
        # Game state
        self.current_game = None
        self.score = 0
        
        self._create_widgets()
        self._show_menu()
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Header
        self._create_header()
        
        # Content area
        self.content = tk.Frame(self, bg=Styles.get_color('bg_main'))
        self.content.pack(fill='both', expand=True)
    
    def _create_header(self):
        """Create header bar"""
        header = tk.Frame(self, bg=Styles.get_color('puzzle'), height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Back button
        self.back_btn = tk.Button(
            header,
            text="← Back",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('puzzle'),
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self._go_back
        )
        self.back_btn.pack(side='left', padx=15, pady=10)
        
        # Title
        self.title_label = tk.Label(
            header,
            text="🧩 Puzzle Games",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('puzzle'),
            fg='white'
        )
        self.title_label.pack(side='left', padx=20, pady=10)
        
        # Score
        self.score_label = tk.Label(
            header,
            text="⭐ Score: 0",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('puzzle'),
            fg='white'
        )
        self.score_label.pack(side='right', padx=20, pady=10)
    
    def _show_menu(self):
        """Show the game selection menu"""
        self._clear_content()
        self.title_label.configure(text="🧩 Puzzle Games")
        self.back_btn.configure(command=self._close_app)
        self.current_game = None
        
        # Menu frame
        menu = tk.Frame(self.content, bg=Styles.get_color('bg_main'))
        menu.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(
            menu,
            text="Choose a Game! 🎮",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('bg_main')
        ).pack(pady=30)
        
        games = [
            ("🎨 Color Match", self._start_color_match),
            ("🔷 Shape Puzzle", self._start_shape_puzzle),
            ("🧠 Memory Game", self._start_memory_game),
            ("🔢 Number Sort", self._start_number_sort),
        ]
        
        for title, command in games:
            btn = tk.Button(
                menu,
                text=title,
                font=Styles.get_font('large'),
                width=20,
                height=2,
                bg=Styles.get_color('puzzle'),
                fg='white',
                cursor='hand2',
                command=command
            )
            btn.pack(pady=10)
    
    def _clear_content(self):
        """Clear the content area"""
        for widget in self.content.winfo_children():
            widget.destroy()
    
    # ==================== Color Match Game ====================
    def _start_color_match(self):
        """Start the color matching game"""
        self._clear_content()
        self.current_game = "color_match"
        self.title_label.configure(text="🎨 Color Match")
        self.back_btn.configure(command=self._show_menu)
        
        self.os_kernel.parental.logger.log("PUZZLE", "Started Color Match", "kid")
        
        # Game frame
        game_frame = tk.Frame(self.content, bg=Styles.get_color('bg_card'))
        game_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(
            game_frame,
            text="Click the matching color! 🎨",
            font=Styles.get_font('large'),
            bg=Styles.get_color('bg_card')
        ).pack(pady=20)
        
        # Target color
        colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF']
        self.target_color = random.choice(colors)
        
        target_frame = tk.Frame(game_frame, bg=Styles.get_color('bg_card'))
        target_frame.pack(pady=20)
        
        tk.Label(
            target_frame,
            text="Find this color:",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_card')
        ).pack(side='left', padx=10)
        
        target_box = tk.Canvas(
            target_frame,
            width=80,
            height=80,
            bg=self.target_color,
            highlightthickness=3,
            highlightbackground='black'
        )
        target_box.pack(side='left')
        
        # Options
        options_frame = tk.Frame(game_frame, bg=Styles.get_color('bg_card'))
        options_frame.pack(pady=30)
        
        random.shuffle(colors)
        for i, color in enumerate(colors):
            btn = tk.Canvas(
                options_frame,
                width=80,
                height=80,
                bg=color,
                highlightthickness=2,
                highlightbackground='gray',
                cursor='hand2'
            )
            btn.grid(row=i // 3, column=i % 3, padx=10, pady=10)
            btn.bind('<Button-1>', lambda e, c=color: self._check_color(c))
    
    def _check_color(self, color: str):
        """Check if selected color matches"""
        if color == self.target_color:
            self.score += 10
            self.score_label.configure(text=f"⭐ Score: {self.score}")
            messagebox.showinfo("Correct! 🎉", "Great job! That's the right color!")
            self._start_color_match()  # Next round
        else:
            messagebox.showinfo("Try Again! 🤔", "That's not quite right. Try again!")
    
    # ==================== Shape Puzzle Game ====================
    def _start_shape_puzzle(self):
        """Start the shape puzzle game"""
        self._clear_content()
        self.current_game = "shape_puzzle"
        self.title_label.configure(text="🔷 Shape Puzzle")
        self.back_btn.configure(command=self._show_menu)
        
        self.os_kernel.parental.logger.log("PUZZLE", "Started Shape Puzzle", "kid")
        
        game_frame = tk.Frame(self.content, bg=Styles.get_color('bg_card'))
        game_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(
            game_frame,
            text="Drag shapes to their matching slots! 🔷",
            font=Styles.get_font('large'),
            bg=Styles.get_color('bg_card')
        ).pack(pady=20)
        
        # Canvas for shapes
        self.shape_canvas = tk.Canvas(
            game_frame,
            width=600,
            height=400,
            bg='white',
            highlightthickness=2,
            highlightbackground='gray'
        )
        self.shape_canvas.pack(pady=20)
        
        # Draw target slots (outlined)
        self.slots = [
            (100, 150, 'circle'),
            (300, 150, 'square'),
            (500, 150, 'triangle')
        ]
        
        for x, y, shape in self.slots:
            if shape == 'circle':
                self.shape_canvas.create_oval(x-40, y-40, x+40, y+40, outline='gray', width=3, dash=(5,3))
            elif shape == 'square':
                self.shape_canvas.create_rectangle(x-40, y-40, x+40, y+40, outline='gray', width=3, dash=(5,3))
            elif shape == 'triangle':
                self.shape_canvas.create_polygon(x, y-45, x-45, y+35, x+45, y+35, outline='gray', width=3, dash=(5,3), fill='')
        
        # Draw draggable shapes at bottom
        shapes_data = [
            (150, 320, 'square', '#FF6B6B'),
            (300, 320, 'triangle', '#4ECDC4'),
            (450, 320, 'circle', '#FFE66D')
        ]
        
        self.shape_items = {}
        for x, y, shape, color in shapes_data:
            if shape == 'circle':
                item = self.shape_canvas.create_oval(x-35, y-35, x+35, y+35, fill=color, outline='black', width=2)
            elif shape == 'square':
                item = self.shape_canvas.create_rectangle(x-35, y-35, x+35, y+35, fill=color, outline='black', width=2)
            elif shape == 'triangle':
                item = self.shape_canvas.create_polygon(x, y-40, x-40, y+30, x+40, y+30, fill=color, outline='black', width=2)
            
            self.shape_items[item] = shape
            self.shape_canvas.tag_bind(item, '<Button-1>', lambda e, i=item: self._start_drag(e, i))
            self.shape_canvas.tag_bind(item, '<B1-Motion>', lambda e, i=item: self._drag(e, i))
            self.shape_canvas.tag_bind(item, '<ButtonRelease-1>', lambda e, i=item: self._end_drag(e, i))
        
        self.dragging = None
        self.drag_offset = (0, 0)
        self.matched = set()
    
    def _start_drag(self, event, item):
        """Start dragging a shape"""
        self.dragging = item
        coords = self.shape_canvas.coords(item)
        if len(coords) >= 4:
            center_x = (coords[0] + coords[2]) / 2 if len(coords) == 4 else coords[0]
            center_y = (coords[1] + coords[3]) / 2 if len(coords) == 4 else coords[1]
        else:
            center_x = sum(coords[::2]) / len(coords[::2])
            center_y = sum(coords[1::2]) / len(coords[1::2])
        self.drag_offset = (event.x - center_x, event.y - center_y)
    
    def _drag(self, event, item):
        """Drag a shape"""
        if self.dragging != item:
            return
        
        coords = self.shape_canvas.coords(item)
        if len(coords) == 4:  # Rectangle or oval
            width = (coords[2] - coords[0]) / 2
            height = (coords[3] - coords[1]) / 2
            new_x = event.x - self.drag_offset[0]
            new_y = event.y - self.drag_offset[1]
            self.shape_canvas.coords(item, new_x-width, new_y-height, new_x+width, new_y+height)
        else:  # Polygon (triangle)
            dx = event.x - self.drag_offset[0] - sum(coords[::2]) / 3
            dy = event.y - self.drag_offset[1] - sum(coords[1::2]) / 3
            new_coords = []
            for i in range(0, len(coords), 2):
                new_coords.extend([coords[i] + dx, coords[i+1] + dy])
            self.shape_canvas.coords(item, *new_coords)
    
    def _end_drag(self, event, item):
        """End dragging - check if matched"""
        if self.dragging != item:
            return
        
        shape_type = self.shape_items.get(item)
        
        # Check if dropped on matching slot
        for slot_x, slot_y, slot_shape in self.slots:
            if abs(event.x - slot_x) < 50 and abs(event.y - slot_y) < 50:
                if shape_type == slot_shape and item not in self.matched:
                    self.matched.add(item)
                    self.score += 15
                    self.score_label.configure(text=f"⭐ Score: {self.score}")
                    
                    # Snap to slot
                    if shape_type == 'circle':
                        self.shape_canvas.coords(item, slot_x-35, slot_y-35, slot_x+35, slot_y+35)
                    elif shape_type == 'square':
                        self.shape_canvas.coords(item, slot_x-35, slot_y-35, slot_x+35, slot_y+35)
                    elif shape_type == 'triangle':
                        self.shape_canvas.coords(item, slot_x, slot_y-40, slot_x-40, slot_y+30, slot_x+40, slot_y+30)
                    
                    if len(self.matched) == 3:
                        messagebox.showinfo("🎉 Complete!", "You matched all shapes!")
                        self._show_menu()
                    break
        
        self.dragging = None
    
    # ==================== Memory Game ====================
    def _start_memory_game(self):
        """Start the memory matching game"""
        self._clear_content()
        self.current_game = "memory"
        self.title_label.configure(text="🧠 Memory Game")
        self.back_btn.configure(command=self._show_menu)
        
        self.os_kernel.parental.logger.log("PUZZLE", "Started Memory Game", "kid")
        
        game_frame = tk.Frame(self.content, bg=Styles.get_color('bg_card'))
        game_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(
            game_frame,
            text="Find the matching pairs! 🧠",
            font=Styles.get_font('large'),
            bg=Styles.get_color('bg_card')
        ).pack(pady=20)
        
        # Grid of cards
        grid_frame = tk.Frame(game_frame, bg=Styles.get_color('bg_card'))
        grid_frame.pack(pady=20)
        
        # Create pairs
        symbols = ['🐱', '🐶', '🐰', '🐻', '🦁', '🐸', '🐵', '🐷']
        cards = symbols + symbols  # Pairs
        random.shuffle(cards)
        
        self.memory_cards = []
        self.memory_buttons = []
        self.revealed = []
        self.matched_pairs = set()
        
        for i, symbol in enumerate(cards):
            row = i // 4
            col = i % 4
            
            btn = tk.Button(
                grid_frame,
                text="❓",
                font=('Segoe UI Emoji', 36),
                width=3,
                height=1,
                bg=Styles.get_color('secondary'),
                cursor='hand2',
                command=lambda idx=i: self._reveal_card(idx)
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
            
            self.memory_cards.append(symbol)
            self.memory_buttons.append(btn)
    
    def _reveal_card(self, idx: int):
        """Reveal a card"""
        if idx in self.matched_pairs or idx in self.revealed:
            return
        
        if len(self.revealed) >= 2:
            return
        
        # Show card
        self.memory_buttons[idx].configure(text=self.memory_cards[idx])
        self.revealed.append(idx)
        
        # Check for match
        if len(self.revealed) == 2:
            self.after(800, self._check_match)
    
    def _check_match(self):
        """Check if revealed cards match"""
        if len(self.revealed) != 2:
            return
        
        idx1, idx2 = self.revealed
        
        if self.memory_cards[idx1] == self.memory_cards[idx2]:
            # Match!
            self.matched_pairs.add(idx1)
            self.matched_pairs.add(idx2)
            self.score += 20
            self.score_label.configure(text=f"⭐ Score: {self.score}")
            
            self.memory_buttons[idx1].configure(bg=Styles.get_color('success'))
            self.memory_buttons[idx2].configure(bg=Styles.get_color('success'))
            
            if len(self.matched_pairs) == 16:
                messagebox.showinfo("🎉 Complete!", "You found all the pairs!")
                self._show_menu()
        else:
            # No match - hide cards
            self.memory_buttons[idx1].configure(text="❓")
            self.memory_buttons[idx2].configure(text="❓")
        
        self.revealed = []
    
    # ==================== Number Sort Game ====================
    def _start_number_sort(self):
        """Start the number sorting game"""
        self._clear_content()
        self.current_game = "number_sort"
        self.title_label.configure(text="🔢 Number Sort")
        self.back_btn.configure(command=self._show_menu)
        
        self.os_kernel.parental.logger.log("PUZZLE", "Started Number Sort", "kid")
        
        game_frame = tk.Frame(self.content, bg=Styles.get_color('bg_card'))
        game_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(
            game_frame,
            text="Click numbers in order: 1, 2, 3... 🔢",
            font=Styles.get_font('large'),
            bg=Styles.get_color('bg_card')
        ).pack(pady=20)
        
        # Grid of numbers
        grid_frame = tk.Frame(game_frame, bg=Styles.get_color('bg_card'))
        grid_frame.pack(pady=30)
        
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        self.number_buttons = {}
        self.next_number = 1
        
        for i, num in enumerate(numbers):
            row = i // 3
            col = i % 3
            
            btn = tk.Button(
                grid_frame,
                text=str(num),
                font=('Comic Sans MS', 36, 'bold'),
                width=3,
                height=1,
                bg=Styles.get_color('accent'),
                cursor='hand2',
                command=lambda n=num: self._click_number(n)
            )
            btn.grid(row=row, column=col, padx=10, pady=10)
            self.number_buttons[num] = btn
    
    def _click_number(self, num: int):
        """Handle number click"""
        if num == self.next_number:
            self.number_buttons[num].configure(
                bg=Styles.get_color('success'),
                state='disabled'
            )
            self.score += 5
            self.score_label.configure(text=f"⭐ Score: {self.score}")
            self.next_number += 1
            
            if self.next_number > 9:
                messagebox.showinfo("🎉 Complete!", "You sorted all the numbers!")
                self._show_menu()
        else:
            self.number_buttons[num].configure(bg=Styles.get_color('error'))
            self.after(300, lambda: self.number_buttons[num].configure(bg=Styles.get_color('accent')))
    
    def _go_back(self):
        """Handle back button"""
        if self.current_game:
            self._show_menu()
        else:
            self._close_app()
    
    def _close_app(self):
        """Close the puzzle app"""
        if self.on_close:
            self.on_close()

