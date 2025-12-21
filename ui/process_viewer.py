"""
MiniMind OS - Process Viewer
============================
Visual display of running processes for education.
Shows process states, memory usage, and allows termination.

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List
from .styles import Styles

class ProcessViewer(tk.Toplevel):
    """
    Process viewer window showing all running processes.
    Educational tool to demonstrate OS process management.
    """
    
    def __init__(self, parent, os_kernel, is_parent_mode: bool = False):
        super().__init__(parent)
        self.os_kernel = os_kernel
        self.process_manager = os_kernel.process_manager
        self.memory_manager = os_kernel.memory_manager
        self.is_parent_mode = is_parent_mode
        
        self.title("📊 Process Viewer")
        self.geometry("700x500")
        self.configure(bg=Styles.get_color('bg_main'))
        
        self._create_widgets()
        self._update_display()
        
        # Auto-refresh
        self._schedule_refresh()
    
    def _create_widgets(self):
        """Create all widgets"""
        # Header
        header = tk.Frame(self, bg=Styles.get_color('secondary'), height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="📊 Running Processes",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('secondary'),
            fg='white'
        )
        title.pack(pady=15)
        
        # Process list
        list_frame = tk.Frame(self, bg=Styles.get_color('bg_main'))
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Treeview for processes
        columns = ('PID', 'Name', 'State', 'Priority', 'Memory', 'CPU Time')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.tree.heading('PID', text='PID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('State', text='State')
        self.tree.heading('Priority', text='Priority')
        self.tree.heading('Memory', text='Memory (KB)')
        self.tree.heading('CPU Time', text='CPU Time (s)')
        
        self.tree.column('PID', width=50, anchor='center')
        self.tree.column('Name', width=200, anchor='w')
        self.tree.column('State', width=100, anchor='center')
        self.tree.column('Priority', width=70, anchor='center')
        self.tree.column('Memory', width=100, anchor='center')
        self.tree.column('CPU Time', width=100, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Memory bar
        mem_frame = tk.Frame(self, bg=Styles.get_color('bg_main'))
        mem_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            mem_frame,
            text="Memory Usage:",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_main')
        ).pack(side='left')
        
        self.mem_progress = ttk.Progressbar(
            mem_frame,
            length=400,
            mode='determinate'
        )
        self.mem_progress.pack(side='left', padx=10)
        
        self.mem_label = tk.Label(
            mem_frame,
            text="0%",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_main')
        )
        self.mem_label.pack(side='left')
        
        # Buttons
        btn_frame = tk.Frame(self, bg=Styles.get_color('bg_main'))
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        refresh_btn = tk.Button(
            btn_frame,
            text="🔄 Refresh",
            font=Styles.get_font('normal'),
            command=self._update_display
        )
        refresh_btn.pack(side='left', padx=5)
        
        if self.is_parent_mode:
            kill_btn = tk.Button(
                btn_frame,
                text="⛔ End Process",
                font=Styles.get_font('normal'),
                bg=Styles.get_color('error'),
                fg='white',
                command=self._kill_selected
            )
            kill_btn.pack(side='left', padx=5)
        
        close_btn = tk.Button(
            btn_frame,
            text="Close",
            font=Styles.get_font('normal'),
            command=self.destroy
        )
        close_btn.pack(side='right', padx=5)
    
    def _update_display(self):
        """Update the process list display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add processes
        processes = self.process_manager.get_all_processes()
        for proc in processes:
            data = proc.to_dict()
            self.tree.insert('', 'end', values=(
                data['pid'],
                f"{data['icon']} {data['name']}",
                data['state'],
                data['priority'],
                data['memory_used'],
                data['cpu_time']
            ))
        
        # Update memory bar
        stats = self.memory_manager.get_stats()
        self.mem_progress['value'] = stats['percent']
        self.mem_label.configure(
            text=f"{stats['percent']:.1f}% ({stats['used']}/{stats['total']} KB)"
        )
    
    def _kill_selected(self):
        """Kill the selected process"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a process")
            return
        
        item = self.tree.item(selected[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        if pid == 0:
            messagebox.showerror("Error", "Cannot terminate system process")
            return
        
        if messagebox.askyesno("Confirm", f"Terminate '{name}'?"):
            self.process_manager.terminate_process(pid)
            self._update_display()
    
    def _schedule_refresh(self):
        """Schedule periodic refresh"""
        if self.winfo_exists():
            self._update_display()
            self.after(2000, self._schedule_refresh)  # Refresh every 2 seconds

class MemoryViewer(tk.Toplevel):
    """
    Memory map viewer showing allocation details.
    Educational tool to demonstrate memory management.
    """
    
    def __init__(self, parent, os_kernel):
        super().__init__(parent)
        self.memory_manager = os_kernel.memory_manager
        
        self.title("💾 Memory Map")
        self.geometry("600x400")
        self.configure(bg=Styles.get_color('bg_main'))
        
        self._create_widgets()
        self._update_display()
    
    def _create_widgets(self):
        """Create memory visualization"""
        # Header
        header = tk.Frame(self, bg=Styles.get_color('info'), height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="💾 Memory Map",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('info'),
            fg='white'
        )
        title.pack(pady=10)
        
        # Memory visualization canvas
        self.canvas = tk.Canvas(
            self,
            width=560,
            height=200,
            bg='white',
            highlightthickness=1,
            highlightbackground=Styles.get_color('border')
        )
        self.canvas.pack(pady=20)
        
        # Legend
        legend_frame = tk.Frame(self, bg=Styles.get_color('bg_main'))
        legend_frame.pack(pady=10)
        
        self._add_legend_item(legend_frame, "System", "#E74C3C")
        self._add_legend_item(legend_frame, "Apps", "#3498DB")
        self._add_legend_item(legend_frame, "Free", "#2ECC71")
        
        # Stats
        self.stats_label = tk.Label(
            self,
            text="",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_main')
        )
        self.stats_label.pack(pady=10)
        
        # Close button
        close_btn = tk.Button(
            self,
            text="Close",
            font=Styles.get_font('normal'),
            command=self.destroy
        )
        close_btn.pack(pady=10)
    
    def _add_legend_item(self, parent, text: str, color: str):
        """Add a legend item"""
        frame = tk.Frame(parent, bg=Styles.get_color('bg_main'))
        frame.pack(side='left', padx=15)
        
        box = tk.Canvas(frame, width=20, height=20, bg=color, highlightthickness=0)
        box.pack(side='left')
        
        label = tk.Label(
            frame,
            text=text,
            font=Styles.get_font('small'),
            bg=Styles.get_color('bg_main')
        )
        label.pack(side='left', padx=5)
    
    def _update_display(self):
        """Update memory visualization"""
        self.canvas.delete('all')
        
        stats = self.memory_manager.get_stats()
        memory_map = self.memory_manager.get_memory_map()
        
        # Draw memory blocks
        canvas_width = 540
        canvas_height = 180
        x_offset = 10
        y_offset = 10
        
        total_memory = stats['total']
        
        for block in memory_map:
            # Calculate block position
            start_x = x_offset + (block['start'] / total_memory) * canvas_width
            end_x = x_offset + (block['end'] / total_memory) * canvas_width
            
            # Color based on type
            if block['pid'] == 0:
                color = "#E74C3C"  # System - Red
            else:
                color = "#3498DB"  # Apps - Blue
            
            # Draw block
            self.canvas.create_rectangle(
                start_x, y_offset,
                end_x, y_offset + canvas_height,
                fill=color,
                outline='white'
            )
            
            # Label if block is big enough
            if end_x - start_x > 40:
                self.canvas.create_text(
                    (start_x + end_x) / 2,
                    y_offset + canvas_height / 2,
                    text=f"PID {block['pid']}\n{block['size']}KB",
                    fill='white',
                    font=Styles.get_font('small')
                )
        
        # Draw free space
        if stats['free'] > 0:
            free_start = x_offset + (stats['used'] / total_memory) * canvas_width
            self.canvas.create_rectangle(
                free_start, y_offset,
                x_offset + canvas_width, y_offset + canvas_height,
                fill="#2ECC71",
                outline='white'
            )
            self.canvas.create_text(
                (free_start + x_offset + canvas_width) / 2,
                y_offset + canvas_height / 2,
                text=f"Free\n{stats['free']}KB",
                fill='white',
                font=Styles.get_font('small')
            )
        
        # Update stats label
        self.stats_label.configure(
            text=f"Total: {stats['total']}KB | Used: {stats['used']}KB | "
                 f"Free: {stats['free']}KB ({100-stats['percent']:.1f}% free)"
        )

