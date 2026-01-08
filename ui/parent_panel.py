"""
MiniMind OS - Parent Panel
==========================
Password-protected panel for parental controls.
Allows parents to manage apps, time limits, and view logs.

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Callable
from datetime import datetime
from .styles import Styles

class PasswordDialog(tk.Toplevel):
    """Dialog for entering parent password"""
    
    def __init__(self, parent, parental_control):
        super().__init__(parent)
        self.parental = parental_control
        self.result = False
        
        self.title("🔒 Parent Login")
        self.geometry("350x200")
        self.configure(bg=Styles.get_color('bg_main'))
        self.resizable(False, False)
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 350) // 2
        y = (self.winfo_screenheight() - 200) // 2
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets"""
        # Title
        title = tk.Label(
            self,
            text="👨‍👩‍👧 Parent Login",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('bg_main'),
            fg=Styles.get_color('text_dark')
        )
        title.pack(pady=20)
        
        # Password entry
        if self.parental.is_password_set():
            label_text = "Enter Password:"
        else:
            label_text = "Create Password:"
        
        label = tk.Label(
            self,
            text=label_text,
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_main')
        )
        label.pack()
        
        self.password_entry = tk.Entry(
            self,
            font=Styles.get_font('normal'),
            show="●",
            width=20
        )
        self.password_entry.pack(pady=10)
        self.password_entry.focus_set()
        self.password_entry.bind('<Return>', lambda e: self._submit())
        
        # Buttons
        btn_frame = tk.Frame(self, bg=Styles.get_color('bg_main'))
        btn_frame.pack(pady=15)
        
        submit_btn = tk.Button(
            btn_frame,
            text="Enter",
            font=Styles.get_font('button'),
            bg=Styles.get_color('success'),
            fg='white',
            width=10,
            command=self._submit
        )
        submit_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=Styles.get_font('button'),
            bg=Styles.get_color('error'),
            fg='white',
            width=10,
            command=self.destroy
        )
        cancel_btn.pack(side='left', padx=10)
    
    def _submit(self):
        """Handle password submission"""
        password = self.password_entry.get()
        
        if not password:
            messagebox.showwarning("Warning", "Please enter a password")
            return
        
        if not self.parental.is_password_set():
            # Set new password
            self.parental.set_password(password)
            messagebox.showinfo("Success", "Password set successfully!")
            self.parental.is_parent_mode = True
            # Automatically unlock system when parent sets password
            if self.parental.is_locked:
                self.parental.is_locked = False
                self.parental.lock_reason = ""
                self.parental.logger.log("UNLOCK", "System unlocked by parent login", "parent")
            self.result = True
            self.destroy()
        else:
            # Verify password
            if self.parental.enter_parent_mode(password):
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("Error", "Incorrect password!")
                self.password_entry.delete(0, 'end')

class ParentPanel(tk.Frame):
    """
    Parent control panel for managing MiniMind OS.
    Provides access to app controls, time limits, and activity logs.
    """
    
    def __init__(self, parent, os_kernel, on_exit: Callable = None):
        super().__init__(parent, bg=Styles.get_color('bg_main'))
        self.os_kernel = os_kernel
        self.parental = os_kernel.parental
        self.on_exit = on_exit
        
        self._create_widgets()
        self._update_display()
    
    def _create_widgets(self):
        """Create all panel widgets"""
        # Header
        self._create_header()
        
        # Main content with tabs
        self._create_tabs()
    
    def _create_header(self):
        """Create the header"""
        header = tk.Frame(self, bg=Styles.get_color('bg_dark'), height=70)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        # Back button
        back_btn = tk.Button(
            header,
            text="← Back",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_dark'),
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self._exit_parent_mode
        )
        back_btn.pack(side='left', padx=20, pady=15)
        
        # Title
        title = tk.Label(
            header,
            text="👨‍👩‍👧 Parent Control Panel",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('bg_dark'),
            fg='white'
        )
        title.pack(side='left', padx=20, pady=15)
    
    def _create_tabs(self):
        """Create tabbed interface"""
        # Custom notebook style
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=Styles.get_font('normal'))
        
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both', padx=20, pady=20)
        
        # App Control Tab
        app_frame = self._create_app_control_tab()
        notebook.add(app_frame, text="  📱 Apps  ")
        
        # Time Limits Tab
        time_frame = self._create_time_limits_tab()
        notebook.add(time_frame, text="  ⏰ Time Limits  ")
        
        # Activity Log Tab
        log_frame = self._create_activity_log_tab()
        notebook.add(log_frame, text="  📋 Activity Log  ")
        
        # System Info Tab
        system_frame = self._create_system_info_tab()
        notebook.add(system_frame, text="  ⚙️ System  ")
    
    def _create_app_control_tab(self) -> tk.Frame:
        """Create app control section"""
        frame = tk.Frame(self, bg=Styles.get_color('bg_card'))
        
        title = tk.Label(
            frame,
            text="Enable/Disable Apps",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('bg_card')
        )
        title.pack(pady=20)
        
        # App toggles
        apps = [
            ('Drawing', 'drawing', '🎨'),
            ('Stories', 'stories', '📚'),
            ('Music', 'music', '🎵'),
            ('Puzzle', 'puzzle', '🧩'),
        ]
        
        self.app_vars = {}
        
        for name, app_id, icon in apps:
            row = tk.Frame(frame, bg=Styles.get_color('bg_card'))
            row.pack(fill='x', padx=50, pady=10)
            
            label = tk.Label(
                row,
                text=f"{icon} {name}",
                font=Styles.get_font('large'),
                bg=Styles.get_color('bg_card'),
                width=15,
                anchor='w'
            )
            label.pack(side='left')
            
            var = tk.BooleanVar(value=self.parental.is_app_allowed(app_id))
            self.app_vars[app_id] = var
            
            toggle = tk.Checkbutton(
                row,
                variable=var,
                onvalue=True,
                offvalue=False,
                bg=Styles.get_color('bg_card'),
                command=lambda aid=app_id: self._toggle_app(aid)
            )
            toggle.pack(side='right')
        
        return frame
    
    def _create_time_limits_tab(self) -> tk.Frame:
        """Create time limits section"""
        frame = tk.Frame(self, bg=Styles.get_color('bg_card'))
        
        title = tk.Label(
            frame,
            text="Time Settings",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('bg_card')
        )
        title.pack(pady=20)
        
        # Daily limit
        daily_frame = tk.Frame(frame, bg=Styles.get_color('bg_card'))
        daily_frame.pack(fill='x', padx=50, pady=10)
        
        tk.Label(
            daily_frame,
            text="Daily Limit (minutes):",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_card')
        ).pack(side='left')
        
        self.daily_var = tk.IntVar(value=self.parental.policy.daily_limit_minutes)
        daily_scale = tk.Scale(
            daily_frame,
            from_=15,
            to=240,
            orient='horizontal',
            variable=self.daily_var,
            length=200,
            bg=Styles.get_color('bg_card'),
            command=lambda v: self._update_daily_limit()
        )
        daily_scale.pack(side='right')
        
        # Bedtime settings
        bed_frame = tk.Frame(frame, bg=Styles.get_color('bg_card'))
        bed_frame.pack(fill='x', padx=50, pady=20)
        
        self.bedtime_var = tk.BooleanVar(value=self.parental.policy.bedtime_enabled)
        tk.Checkbutton(
            bed_frame,
            text="Enable Bedtime Lock",
            variable=self.bedtime_var,
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_card'),
            command=self._toggle_bedtime
        ).pack(anchor='w')
        
        # Bedtime hours
        hours_frame = tk.Frame(frame, bg=Styles.get_color('bg_card'))
        hours_frame.pack(fill='x', padx=50, pady=10)
        
        tk.Label(
            hours_frame,
            text="Bedtime Start:",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_card')
        ).pack(side='left')
        
        self.bedtime_start = tk.Entry(hours_frame, width=8, font=Styles.get_font('normal'))
        self.bedtime_start.insert(0, self.parental.policy.bedtime_start)
        self.bedtime_start.pack(side='left', padx=10)
        
        tk.Label(
            hours_frame,
            text="End:",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_card')
        ).pack(side='left', padx=10)
        
        self.bedtime_end = tk.Entry(hours_frame, width=8, font=Styles.get_font('normal'))
        self.bedtime_end.insert(0, self.parental.policy.bedtime_end)
        self.bedtime_end.pack(side='left', padx=10)
        
        # Save button
        save_btn = tk.Button(
            frame,
            text="💾 Save Settings",
            font=Styles.get_font('button'),
            bg=Styles.get_color('success'),
            fg='white',
            command=self._save_time_settings
        )
        save_btn.pack(pady=20)
        
        # Current status
        self.status_label = tk.Label(
            frame,
            text="",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_card'),
            fg=Styles.get_color('info')
        )
        self.status_label.pack(pady=10)
        
        return frame
    
    def _create_activity_log_tab(self) -> tk.Frame:
        """Create activity log section with improved UI"""
        frame = tk.Frame(self, bg=Styles.get_color('bg_card'))
        
        # Header
        header = tk.Frame(frame, bg=Styles.get_color('bg_card'))
        header.pack(fill='x', padx=20, pady=15)
        
        title = tk.Label(
            header,
            text="📋 Activity Log",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('bg_card')
        )
        title.pack(side='left')
        
        # Filter frame
        filter_frame = tk.Frame(frame, bg=Styles.get_color('bg_card'))
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        # Filter by event type
        tk.Label(
            filter_frame,
            text="Filter:",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_card')
        ).pack(side='left', padx=5)
        
        self.log_filter_var = tk.StringVar(value="ALL")
        filter_options = [
            ("All Events", "ALL"),
            ("🔒 Security", "SECURITY"),
            ("📱 Apps", "APP"),
            ("🎵 Music", "MUSIC"),
            ("📚 Stories", "STORY"),
            ("🎨 Drawing", "DRAWING"),
            ("🧩 Puzzle", "PUZZLE"),
            ("⏰ Time", "LOCK"),
            ("💾 System", "SYSTEM"),
            ("⚙️ Process", "PROCESS"),
            ("🧠 Memory", "MEMORY"),
            ("📅 Scheduler", "SCHEDULER")
        ]
        
        for text, value in filter_options:
            rb = tk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.log_filter_var,
                value=value,
                font=Styles.get_font('small'),
                bg=Styles.get_color('bg_card'),
                selectcolor=Styles.get_color('bg_card'),
                command=self._refresh_logs
            )
            rb.pack(side='left', padx=5)
        
        # View options
        view_frame = tk.Frame(frame, bg=Styles.get_color('bg_card'))
        view_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(
            view_frame,
            text="View:",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('bg_card')
        ).pack(side='left', padx=5)
        
        self.log_view_var = tk.StringVar(value="RECENT")
        view_options = [
            ("Recent (100)", "RECENT"),
            ("Today", "TODAY"),
            ("All", "ALL")
        ]
        
        for text, value in view_options:
            rb = tk.Radiobutton(
                view_frame,
                text=text,
                variable=self.log_view_var,
                value=value,
                font=Styles.get_font('small'),
                bg=Styles.get_color('bg_card'),
                selectcolor=Styles.get_color('bg_card'),
                command=self._refresh_logs
            )
            rb.pack(side='left', padx=5)
        
        # Log display with Treeview for better organization
        log_container = tk.Frame(frame, bg=Styles.get_color('bg_card'))
        log_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create Treeview with columns
        columns = ('Time', 'Type', 'Event', 'User')
        self.log_tree = ttk.Treeview(
            log_container,
            columns=columns,
            show='headings',
            height=18
        )
        
        # Configure columns
        self.log_tree.heading('Time', text='⏰ Time')
        self.log_tree.heading('Type', text='📋 Type')
        self.log_tree.heading('Event', text='📝 Event Details')
        self.log_tree.heading('User', text='👤 User')
        
        self.log_tree.column('Time', width=150, anchor='w')
        self.log_tree.column('Type', width=120, anchor='center')
        self.log_tree.column('Event', width=400, anchor='w')
        self.log_tree.column('User', width=80, anchor='center')
        
        # Configure alternating row colors
        style = ttk.Style()
        style.configure("Treeview", 
                       background=Styles.get_color('bg_card'),
                       foreground=Styles.get_color('text_dark'),
                       fieldbackground=Styles.get_color('bg_card'),
                       rowheight=25)
        style.configure("Treeview.Heading",
                       background=Styles.get_color('bg_dark'),
                       foreground='white',
                       font=Styles.get_font('normal'))
        
        # Tag for alternating rows
        self.log_tree.tag_configure('evenrow', background='#F5F5F5')
        self.log_tree.tag_configure('oddrow', background='#FFFFFF')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_container, orient='vertical', command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        
        self.log_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Action buttons
        btn_frame = tk.Frame(frame, bg=Styles.get_color('bg_card'))
        btn_frame.pack(pady=15)
        
        refresh_btn = tk.Button(
            btn_frame,
            text="🔄 Refresh",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('info'),
            fg='white',
            relief='flat',
            padx=15,
            pady=5,
            command=self._refresh_logs
        )
        refresh_btn.pack(side='left', padx=10)
        
        clear_btn = tk.Button(
            btn_frame,
            text="🗑️ Clear Logs",
            font=Styles.get_font('normal'),
            bg=Styles.get_color('warning'),
            fg='white',
            relief='flat',
            padx=15,
            pady=5,
            command=self._clear_logs
        )
        clear_btn.pack(side='left', padx=10)
        
        # Stats label
        self.log_stats_label = tk.Label(
            btn_frame,
            text="",
            font=Styles.get_font('small'),
            bg=Styles.get_color('bg_card'),
            fg=Styles.get_color('text_muted')
        )
        self.log_stats_label.pack(side='left', padx=20)
        
        # Load initial logs
        self._refresh_logs()
        
        return frame
    
    def _create_system_info_tab(self) -> tk.Frame:
        """Create system information section"""
        frame = tk.Frame(self, bg=Styles.get_color('bg_card'))
        
        title = tk.Label(
            frame,
            text="System Information",
            font=Styles.get_font('heading'),
            bg=Styles.get_color('bg_card')
        )
        title.pack(pady=20)
        
        # System info display
        info_frame = tk.Frame(frame, bg=Styles.get_color('bg_card'))
        info_frame.pack(fill='x', padx=50, pady=10)
        
        info = self.os_kernel.hardware.get_system_info()
        
        info_items = [
            ("OS Name", info['os_name']),
            ("Version", info['version']),
            ("Uptime", info['uptime']),
            ("CPU", info['cpu']['name']),
            ("Memory", f"{info['memory']['used']}/{info['memory']['total']} KB"),
            ("Display", info['display']['resolution']),
        ]
        
        for label_text, value in info_items:
            row = tk.Frame(info_frame, bg=Styles.get_color('bg_card'))
            row.pack(fill='x', pady=5)
            
            tk.Label(
                row,
                text=f"{label_text}:",
                font=Styles.get_font('normal'),
                bg=Styles.get_color('bg_card'),
                width=15,
                anchor='w'
            ).pack(side='left')
            
            tk.Label(
                row,
                text=value,
                font=Styles.get_font('normal'),
                bg=Styles.get_color('bg_card'),
                fg=Styles.get_color('info')
            ).pack(side='left')
        
        # Quick actions
        actions_frame = tk.Frame(frame, bg=Styles.get_color('bg_card'))
        actions_frame.pack(pady=30)
        
        lock_btn = tk.Button(
            actions_frame,
            text="🔒 Lock Now",
            font=Styles.get_font('button'),
            bg=Styles.get_color('error'),
            fg='white',
            command=self._force_lock
        )
        lock_btn.pack(side='left', padx=10)
        
        unlock_btn = tk.Button(
            actions_frame,
            text="🔓 Unlock",
            font=Styles.get_font('button'),
            bg=Styles.get_color('success'),
            fg='white',
            command=self._unlock_system
        )
        unlock_btn.pack(side='left', padx=10)
        
        return frame
    
    def _toggle_app(self, app_id: str):
        """Toggle an app on/off"""
        enabled = self.app_vars[app_id].get()
        self.parental.toggle_app(app_id, enabled)
    
    def _update_daily_limit(self):
        """Update daily limit (called by scale)"""
        pass  # Will be saved when Save button is clicked
    
    def _toggle_bedtime(self):
        """Toggle bedtime feature"""
        self.parental.update_policy(bedtime_enabled=self.bedtime_var.get())
    
    def _save_time_settings(self):
        """Save time-related settings"""
        self.parental.update_policy(
            daily_limit_minutes=self.daily_var.get(),
            bedtime_start=self.bedtime_start.get(),
            bedtime_end=self.bedtime_end.get()
        )
        self.status_label.configure(text="✓ Settings saved!")
        self.after(2000, lambda: self.status_label.configure(text=""))
    
    def _refresh_logs(self):
        """Refresh the activity log display with filtering"""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        # Get logs based on view option
        view_option = self.log_view_var.get()
        if view_option == "TODAY":
            logs = self.parental.logger.get_today_logs()
        elif view_option == "ALL":
            logs = self.parental.logger.get_logs(limit=None)
        else:  # RECENT
            logs = self.parental.logger.get_logs(limit=100)
        
        # Filter by event type
        filter_type = self.log_filter_var.get()
        if filter_type != "ALL":
            logs = [log for log in logs if log['event_type'] == filter_type]
        
        # Event type icons and colors
        event_icons = {
            'SECURITY': '🔒',
            'APP': '📱',
            'MUSIC': '🎵',
            'STORY': '📚',
            'DRAWING': '🎨',
            'PUZZLE': '🧩',
            'LOCK': '⏰',
            'SYSTEM': '💾',
            'PROCESS': '⚙️',
            'MEMORY': '🧠',
            'SCHEDULER': '📅'
        }
        
        # Format and insert logs
        for idx, log in enumerate(logs):
            event_type = log['event_type']
            icon = event_icons.get(event_type, '📋')
            
            # Format time (show only time if today, full date otherwise)
            log_time = datetime.fromtimestamp(log['timestamp'])
            now = datetime.now()
            
            if log_time.date() == now.date():
                time_str = log_time.strftime("%H:%M:%S")
            else:
                time_str = log_time.strftime("%m/%d %H:%M")
            
            # Format user
            user_icon = "👨‍👩‍👧" if log['user'] == 'parent' else "👶" if log['user'] == 'kid' else "🤖"
            user_display = f"{user_icon} {log['user'].title()}"
            
            # Alternate row colors
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            
            # Insert into treeview
            self.log_tree.insert(
                '',
                'end',
                values=(
                    time_str,
                    f"{icon} {event_type}",
                    log['details'],
                    user_display
                ),
                tags=(tag,)
            )
        
        # Update stats
        total_count = len(logs)
        self.log_stats_label.configure(
            text=f"Showing {total_count} log entries"
        )
    
    def _clear_logs(self):
        """Clear all activity logs"""
        if messagebox.askyesno("Confirm", "Clear all activity logs?"):
            self.parental.logger.clear_logs()
            self._refresh_logs()
    
    def _force_lock(self):
        """Force lock the system"""
        self.parental.force_lock("Locked by parent")
        messagebox.showinfo("Locked", "System has been locked")
    
    def _unlock_system(self):
        """Unlock the system"""
        if self.parental.is_locked:
            self.parental.is_locked = False
            self.parental.lock_reason = ""
            messagebox.showinfo("Unlocked", "System has been unlocked")
    
    def _update_display(self):
        """Update display with current status"""
        status = self.parental.get_status()
        today_usage = status['today_usage_minutes']
        remaining = status['remaining_minutes']
        
        status_text = f"Today's usage: {today_usage} min | Remaining: {remaining} min"
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=status_text)
    
    def _exit_parent_mode(self):
        """Exit parent mode and return to home"""
        self.parental.exit_parent_mode()
        if self.on_exit:
            self.on_exit()

