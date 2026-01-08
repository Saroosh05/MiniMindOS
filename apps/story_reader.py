"""
MiniMind OS - Story Reader App
==============================
A kid-friendly story reader with:
- Pre-loaded stories
- Large, readable text
- Page navigation
- Text highlighting
- Simple interface

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, List, Dict
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles

# Try to import PIL for better image support
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class StoryReaderApp(tk.Frame):
    """
    Kid-friendly story reading application.
    Displays stories with large text and simple navigation.
    """
    
    # Pre-loaded stories
    STORIES = [
        {
            'id': 'three_bears',
            'title': '🐻 Goldilocks and the Three Bears',
            'icon': '🐻',
            'pages': [
                # Format: Can be string (old format) or dict with 'text' and 'image' (new format)
                {
                    'text': "Once upon a time, there were three bears who lived in a cozy house in the forest.\n\nThere was Papa Bear, Mama Bear, and little Baby Bear. 🐻",
                    'image': 'page1_three_bears.png'  # Optional: image filename
                },
                {
                    'text': "One morning, they made porridge for breakfast. But it was too hot to eat!\n\n'Let's go for a walk while it cools,' said Mama Bear. 🚶",
                    'image': 'page2_porridge.png'
                },
                {
                    'text': "While they were away, a little girl named Goldilocks came by. She knocked on the door, but no one answered.\n\nSo she walked right in! 🚪",
                    'image': 'page3_goldilocks.png'
                },
                {
                    'text': "Goldilocks saw the three bowls of porridge. She tried Papa Bear's - too hot! 🔥\n\nShe tried Mama Bear's - too cold! ❄️\n\nBaby Bear's was just right! 😋",
                    'image': 'page4_porridge_tasting.png'
                },
                {
                    'text': "Then Goldilocks found three chairs. Papa's was too hard. Mama's was too soft.\n\nBaby Bear's was just right - until it broke! 💥",
                    'image': 'page5_chairs.png'
                },
                {
                    'text': "Feeling sleepy, Goldilocks found three beds upstairs.\n\nPapa's was too hard. Mama's was too soft.\n\nBaby Bear's was just right! She fell fast asleep. 😴",
                    'image': 'page6_beds.png'
                },
                {
                    'text': "When the bears came home, they found their porridge eaten and chair broken!\n\nUpstairs, they found Goldilocks in Baby Bear's bed! 😱",
                    'image': 'page7_bears_find.png'
                },
                {
                    'text': "Goldilocks woke up and saw the three bears! She jumped up and ran out of the house as fast as she could.\n\nAnd she never came back again! 🏃‍♀️\n\n🌟 THE END 🌟",
                    'image': 'page8_goldilocks_runs.png'
                }
            ]
        },
        {
            'id': 'little_star',
            'title': '⭐ Twinkle Little Star',
            'icon': '⭐',
            'pages': [
                "⭐ Twinkle, twinkle, little star ⭐\n\nHigh above the world so far!\n\nIn the dark night sky you shine,\n\nLike a diamond, oh so fine!",
                "🌙 When the sun goes down to sleep,\n\nThrough the clouds you start to peek.\n\nGuiding travelers on their way,\n\nUntil the break of day! 🌅",
                "✨ Little star up in the sky,\n\nI often wonder as you fly,\n\nWhat you see from way up there,\n\nFloating in the midnight air! ✨",
                "💫 You watch over girls and boys,\n\nWith their dreams and favorite toys.\n\nTwinkling bright throughout the night,\n\nUntil the morning light! 🌈\n\n🌟 THE END 🌟"
            ]
        },
        {
            'id': 'bunny',
            'title': '🐰 The Little Bunny',
            'icon': '🐰',
            'pages': [
                "🐰 Once there was a little bunny\n\nWhose ears were long and nose was funny!\n\nHe hopped around from dawn to night,\n\nLooking for a carrot bright! 🥕",
                "🌳 In the garden he would play,\n\nEvery single sunny day.\n\nMunching lettuce, green and fresh,\n\nLife for bunny was the best! 🥬",
                "☁️ One day it started raining hard,\n\nBunny hopped across the yard.\n\nFound a hole beneath a tree,\n\nWarm and dry as it could be! 🌧️",
                "🌈 When the rainbow came around,\n\nBunny hopped out from the ground.\n\nDanced and played in puddles deep,\n\nThen went home to fall asleep! 😴\n\n🌟 THE END 🌟"
            ]
        },
        {
            'id': 'counting',
            'title': '🔢 Let\'s Count Together!',
            'icon': '🔢',
            'pages': [
                "1️⃣ ONE little apple on the tree 🍎\n\nSwinging in the breeze so free!\n\nLet's count up and have some fun,\n\nReady? Here we go - it's ONE!",
                "2️⃣ TWO little birds up in the sky 🐦🐦\n\nFlying, soaring way up high!\n\nCount them as they fly right through,\n\nOne and one makes exactly TWO!",
                "3️⃣ THREE little fish swim in the sea 🐟🐟🐟\n\nSplashing, playing, wild and free!\n\nBlue and yellow, can you see?\n\nCount along - one, two, THREE!",
                "4️⃣ FOUR little stars shine at night ⭐⭐⭐⭐\n\nTwinkling, sparkling, oh so bright!\n\nCount them as they light the floor,\n\nOne, two, three, and FOUR!",
                "5️⃣ FIVE little flowers in a row 🌸🌸🌸🌸🌸\n\nPink and pretty, watch them grow!\n\nCount them now, you're doing great,\n\nOne, two, three, four, FIVE - celebrate! 🎉\n\n🌟 THE END 🌟"
            ]
        }
    ]
    
    def __init__(self, parent, os_kernel, on_close: Callable = None):
        super().__init__(parent, bg=Styles.get_color('bg_main'))
        self.os_kernel = os_kernel
        self.on_close = on_close
        
        # Reading state
        self.current_story = None
        self.current_page = 0
        
        # Get images directory path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.images_dir = os.path.join(base_dir, 'data', 'stories', 'images')
        
        # Store loaded images to prevent garbage collection
        self.current_image_ref = None
        
        self._create_widgets()
        self._show_story_list()
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Header
        self._create_header()
        
        # Content area
        self.content = tk.Frame(self, bg=Styles.get_color('bg_main'))
        self.content.pack(fill='both', expand=True)
        
        # Bind keyboard shortcuts
        self.bind_all('<Right>', lambda e: self._next_page() if self.current_story else None)
        self.bind_all('<Left>', lambda e: self._prev_page() if self.current_story else None)
        self.bind_all('<space>', lambda e: self._next_page() if self.current_story else None)
        self.bind_all('<Return>', lambda e: self._next_page() if self.current_story else None)
    
    def _create_header(self):
        """Create header bar"""
        header = tk.Frame(self, bg=Styles.get_color('stories'), height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Back button
        self.back_btn = tk.Button(
            header,
            text="← Back",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('stories'),
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self._go_back
        )
        self.back_btn.pack(side='left', padx=15, pady=10)
        
        # Title
        self.title_label = tk.Label(
            header,
            text="📚 Story Time",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('stories'),
            fg='white'
        )
        self.title_label.pack(side='left', padx=20, pady=10)
    
    def _show_story_list(self):
        """Show the list of available stories"""
        # Clear content
        for widget in self.content.winfo_children():
            widget.destroy()
        
        self.title_label.configure(text="📚 Story Time")
        self.back_btn.configure(command=self._close_app)
        
        # Story selection frame
        list_frame = tk.Frame(self.content, bg=Styles.get_color('bg_main'))
        list_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        tk.Label(
            list_frame,
            text="Choose a Story! 📖",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('bg_main'),
            fg=Styles.get_color('text_dark')
        ).pack(pady=20)
        
        # Story buttons
        for story in self.STORIES:
            btn = tk.Button(
                list_frame,
                text=story['title'],
                font=Styles.get_font('large'),
                width=35,
                height=2,
                bg=Styles.get_color('stories'),
                fg='white',
                cursor='hand2',
                command=lambda s=story: self._open_story(s)
            )
            btn.pack(pady=10)
    
    def _open_story(self, story: Dict):
        """Open and display a story"""
        self.current_story = story
        self.current_page = 0
        
        # Log story open
        self.os_kernel.parental.logger.log(
            "STORY",
            f"Opened story: {story['title']}",
            "kid"
        )
        
        self._show_page()
    
    def _show_page(self):
        """Display the current page"""
        if not self.current_story:
            return
        
        # Clear content
        for widget in self.content.winfo_children():
            widget.destroy()
        
        story = self.current_story
        # Support both old format (string) and new format (dict with text and image)
        page_data = story['pages'][self.current_page]
        if isinstance(page_data, dict):
            page_text = page_data.get('text', '')
            page_image = page_data.get('image', None)
        else:
            page_text = page_data
            page_image = None
        
        total_pages = len(story['pages'])
        
        # Update title
        self.title_label.configure(text=story['title'])
        self.back_btn.configure(command=self._show_story_list)
        
        # Reading frame
        read_frame = tk.Frame(self.content, bg=Styles.get_color('bg_card'))
        read_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Page indicator
        page_indicator = tk.Label(
            read_frame,
            text=f"Page {self.current_page + 1} of {total_pages}",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_card'),
            fg=Styles.get_color('text_muted')
        )
        page_indicator.pack(pady=10)
        
        # Main content area (image and text)
        content_frame = tk.Frame(read_frame, bg=Styles.get_color('bg_card'))
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Try to load and display image
        image_path = None
        if page_image:
            image_path = self._get_image_path(story['id'], page_image)
        
        if image_path and os.path.exists(image_path):
            # Display image above text
            image_label = self._load_and_display_image(content_frame, image_path)
            if image_label:
                image_label.pack(pady=(0, 20))
        
        # Story text
        text_frame = tk.Frame(content_frame, bg=Styles.get_color('bg_card'))
        text_frame.pack(fill='both', expand=True)
        
        story_text = tk.Text(
            text_frame,
            font=('Comic Sans MS', 22),
            wrap='word',
            bg=Styles.get_color('bg_card'),
            fg=Styles.get_color('text_dark'),
            relief='flat',
            padx=20,
            pady=20,
            cursor='arrow',
            state='normal'
        )
        story_text.insert('1.0', page_text)
        story_text.configure(state='disabled')  # Read-only
        story_text.pack(fill='both', expand=True)
        
        # Set focus to enable keyboard navigation
        read_frame.focus_set()
        
        # Navigation buttons
        nav_frame = tk.Frame(read_frame, bg=Styles.get_color('bg_card'))
        nav_frame.pack(fill='x', pady=20)
        
        # Previous button
        if self.current_page > 0:
            prev_btn = tk.Button(
                nav_frame,
                text="⬅️ Previous",
                font=Styles.get_font('button'),
                bg=Styles.get_color('secondary'),
                fg='white',
                cursor='hand2',
                command=self._prev_page
            )
            prev_btn.pack(side='left', padx=30)
        
        # Next button
        if self.current_page < total_pages - 1:
            next_btn = tk.Button(
                nav_frame,
                text="Next ➡️",
                font=Styles.get_font('button'),
                bg=Styles.get_color('secondary'),
                fg='white',
                cursor='hand2',
                command=self._next_page
            )
            next_btn.pack(side='right', padx=30)
        else:
            # Finish button on last page
            finish_btn = tk.Button(
                nav_frame,
                text="🌟 The End! 🌟",
                font=Styles.get_font('button'),
                bg=Styles.get_color('success'),
                fg='white',
                cursor='hand2',
                command=self._finish_story
            )
            finish_btn.pack(side='right', padx=30)
    
    def _prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self._show_page()
    
    def _next_page(self):
        """Go to next page"""
        if self.current_story and self.current_page < len(self.current_story['pages']) - 1:
            self.current_page += 1
            self._show_page()
    
    def _finish_story(self):
        """Finish reading the story"""
        self.os_kernel.parental.logger.log(
            "STORY",
            f"Finished story: {self.current_story['title']}",
            "kid"
        )
        
        messagebox.showinfo(
            "Great Job! 🌟",
            f"You finished reading\n{self.current_story['title']}!\n\n⭐ Great job! ⭐"
        )
        
        self._show_story_list()
    
    def _go_back(self):
        """Handle back button"""
        if self.current_story:
            self._show_story_list()
            self.current_story = None
        else:
            self._close_app()
    
    def _get_image_path(self, story_id: str, image_filename: str):
        """Get the full path to a story image"""
        if not image_filename:
            return None
        return os.path.join(self.images_dir, story_id, image_filename)
    
    def _load_and_display_image(self, parent, image_path: str):
        """Load and display an image, returning the label widget"""
        try:
            if PIL_AVAILABLE:
                # Use PIL for better image support (JPEG, PNG, etc.)
                img = Image.open(image_path)
                # Resize to fit nicely (max width 500px, maintain aspect ratio)
                max_width = 500
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    # Use LANCZOS resampling (fallback to ANTIALIAS for older PIL)
                    try:
                        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    except AttributeError:
                        img = img.resize((max_width, new_height), Image.ANTIALIAS)
                
                self.current_image_ref = ImageTk.PhotoImage(img)
            else:
                # Fallback to tkinter PhotoImage (supports GIF and PPM)
                if image_path.lower().endswith(('.gif', '.ppm', '.pgm')):
                    self.current_image_ref = tk.PhotoImage(file=image_path)
                else:
                    # Can't load this format without PIL
                    return None
            
            image_label = tk.Label(
                parent,
                image=self.current_image_ref,
                bg=Styles.get_color('bg_card')
            )
            return image_label
            
        except Exception as e:
            # If image loading fails, just continue without image
            print(f"Could not load image {image_path}: {e}")
            return None
    
    def _close_app(self):
        """Close the story reader"""
        if self.on_close:
            self.on_close()

