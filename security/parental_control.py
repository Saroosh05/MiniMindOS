"""
MiniMind OS - Parental Control System
=====================================
Provides comprehensive parental controls including:
- Password-protected parent mode
- App access control
- Daily time limits
- Bedtime scheduling
- Activity logging

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import json
import time
import hashlib
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from pathlib import Path

@dataclass
class Policy:
    """Parental control policy settings"""
    # App permissions
    allowed_apps: List[str] = field(default_factory=lambda: [
        "drawing", "stories", "music", "puzzle"
    ])
    
    # Time limits
    daily_limit_minutes: int = 120  # 2 hours default
    session_limit_minutes: int = 30  # Break every 30 min
    
    # Bedtime settings
    bedtime_enabled: bool = True
    bedtime_start: str = "20:00"  # 8 PM
    bedtime_end: str = "07:00"    # 7 AM
    
    # Content settings
    content_filter_enabled: bool = True
    max_volume: int = 80  # Max volume percentage
    
    def to_dict(self) -> dict:
        return {
            'allowed_apps': self.allowed_apps,
            'daily_limit_minutes': self.daily_limit_minutes,
            'session_limit_minutes': self.session_limit_minutes,
            'bedtime_enabled': self.bedtime_enabled,
            'bedtime_start': self.bedtime_start,
            'bedtime_end': self.bedtime_end,
            'content_filter_enabled': self.content_filter_enabled,
            'max_volume': self.max_volume
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Policy':
        return Policy(
            allowed_apps=data.get('allowed_apps', ["drawing", "stories", "music", "puzzle"]),
            daily_limit_minutes=data.get('daily_limit_minutes', 120),
            session_limit_minutes=data.get('session_limit_minutes', 30),
            bedtime_enabled=data.get('bedtime_enabled', True),
            bedtime_start=data.get('bedtime_start', "20:00"),
            bedtime_end=data.get('bedtime_end', "07:00"),
            content_filter_enabled=data.get('content_filter_enabled', True),
            max_volume=data.get('max_volume', 80)
        )

@dataclass
class ActivityLog:
    """Single activity log entry"""
    timestamp: float
    event_type: str
    details: str
    user: str = "kid"
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            'event_type': self.event_type,
            'details': self.details,
            'user': self.user
        }

class ActivityLogger:
    """Logs all kid activities for parent review"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.logs: List[ActivityLog] = []
        self.lock = threading.Lock()
        self.max_logs = 1000  # Keep last 1000 entries
        
        self._load_logs()
    
    def log(self, event_type: str, details: str, user: str = "kid"):
        """Add a new log entry"""
        with self.lock:
            entry = ActivityLog(
                timestamp=time.time(),
                event_type=event_type,
                details=details,
                user=user
            )
            self.logs.append(entry)
            
            # Trim old logs
            if len(self.logs) > self.max_logs:
                self.logs = self.logs[-self.max_logs:]
            
            self._save_logs()
    
    def get_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent log entries"""
        with self.lock:
            recent = self.logs[-limit:] if limit else self.logs
            return [log.to_dict() for log in reversed(recent)]
    
    def get_logs_by_type(self, event_type: str, limit: int = 50) -> List[Dict]:
        """Get logs filtered by event type"""
        with self.lock:
            filtered = [log for log in self.logs if log.event_type == event_type]
            recent = filtered[-limit:] if limit else filtered
            return [log.to_dict() for log in reversed(recent)]
    
    def get_today_logs(self) -> List[Dict]:
        """Get all logs from today"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0).timestamp()
        with self.lock:
            today = [log for log in self.logs if log.timestamp >= today_start]
            return [log.to_dict() for log in reversed(today)]
    
    def clear_logs(self):
        """Clear all logs (parent only)"""
        with self.lock:
            self.logs = []
            self._save_logs()
    
    def _save_logs(self):
        """Save logs to disk"""
        try:
            log_path = self.data_path / "activity_log.json"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_path, 'w') as f:
                json.dump([log.to_dict() for log in self.logs], f, indent=2)
        except Exception:
            pass
    
    def _load_logs(self):
        """Load logs from disk"""
        try:
            log_path = self.data_path / "activity_log.json"
            if log_path.exists():
                with open(log_path, 'r') as f:
                    data = json.load(f)
                    self.logs = [
                        ActivityLog(
                            timestamp=entry['timestamp'],
                            event_type=entry['event_type'],
                            details=entry['details'],
                            user=entry.get('user', 'kid')
                        )
                        for entry in data
                    ]
        except Exception:
            pass

class ParentalControl:
    """
    Main parental control system for MiniMind OS.
    Manages authentication, policies, and time tracking.
    """
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.logger = ActivityLogger(data_path)
        
        # Authentication
        self.parent_password_hash: Optional[str] = None
        self.is_parent_mode: bool = False
        
        # Policy
        self.policy = Policy()
        
        # Time tracking
        self.session_start: float = time.time()
        self.today_usage_minutes: float = 0.0
        self.last_break_time: float = time.time()
        
        # Status
        self.is_locked: bool = False
        self.lock_reason: str = ""
        
        # Callbacks
        self.on_lock_callbacks: List[Callable] = []
        self.on_unlock_callbacks: List[Callable] = []
        self.on_time_warning_callbacks: List[Callable] = []
        
        # Load saved data
        self._load_settings()
        
        # Start time tracking thread
        self.tracking = True
        self.track_thread = threading.Thread(target=self._time_tracking_loop, daemon=True)
        self.track_thread.start()
    
    # Authentication
    def set_password(self, password: str):
        """Set the parental password"""
        self.parent_password_hash = hashlib.sha256(password.encode()).hexdigest()
        self._save_settings()
        self.logger.log("SECURITY", "Parent password set", "parent")
    
    def check_password(self, password: str) -> bool:
        """Verify the parental password"""
        if self.parent_password_hash is None:
            return True  # No password set yet
        
        return hashlib.sha256(password.encode()).hexdigest() == self.parent_password_hash
    
    def enter_parent_mode(self, password: str) -> bool:
        """Attempt to enter parent mode"""
        if self.check_password(password):
            self.is_parent_mode = True
            self.logger.log("SECURITY", "Parent mode activated", "parent")
            return True
        
        self.logger.log("SECURITY", "Failed parent login attempt", "kid")
        return False
    
    def exit_parent_mode(self):
        """Exit parent mode back to kid mode"""
        self.is_parent_mode = False
        self.logger.log("SECURITY", "Parent mode deactivated", "parent")
    
    def is_password_set(self) -> bool:
        """Check if a parent password has been set"""
        return self.parent_password_hash is not None
    
    # Policy Management
    def update_policy(self, **kwargs):
        """Update policy settings"""
        for key, value in kwargs.items():
            if hasattr(self.policy, key):
                setattr(self.policy, key, value)
        
        self._save_settings()
        self.logger.log("POLICY", f"Policy updated: {kwargs}", "parent")
    
    def is_app_allowed(self, app_name: str) -> bool:
        """Check if an app is allowed by policy"""
        if self.is_parent_mode:
            return True
        return app_name.lower() in [a.lower() for a in self.policy.allowed_apps]
    
    def toggle_app(self, app_name: str, enabled: bool):
        """Enable or disable an app"""
        app_lower = app_name.lower()
        
        if enabled:
            if app_lower not in self.policy.allowed_apps:
                self.policy.allowed_apps.append(app_lower)
        else:
            if app_lower in self.policy.allowed_apps:
                self.policy.allowed_apps.remove(app_lower)
        
        self._save_settings()
        status = "enabled" if enabled else "disabled"
        self.logger.log("POLICY", f"App {app_name} {status}", "parent")
    
    # Time Management
    def is_bedtime(self) -> bool:
        """Check if it's currently bedtime"""
        if not self.policy.bedtime_enabled or self.is_parent_mode:
            return False
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        
        # Parse bedtime
        start_parts = self.policy.bedtime_start.split(":")
        end_parts = self.policy.bedtime_end.split(":")
        
        start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
        end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])
        
        # Handle overnight bedtime
        if start_minutes > end_minutes:
            # Bedtime spans midnight
            return current_time >= start_minutes or current_time < end_minutes
        else:
            return start_minutes <= current_time < end_minutes
    
    def is_time_limit_reached(self) -> bool:
        """Check if daily time limit is reached"""
        if self.is_parent_mode:
            return False
        return self.today_usage_minutes >= self.policy.daily_limit_minutes
    
    def get_remaining_time(self) -> int:
        """Get remaining time in minutes"""
        remaining = self.policy.daily_limit_minutes - self.today_usage_minutes
        return max(0, int(remaining))
    
    def needs_break(self) -> bool:
        """Check if kid needs a break"""
        if self.is_parent_mode:
            return False
        
        session_minutes = (time.time() - self.last_break_time) / 60
        return session_minutes >= self.policy.session_limit_minutes
    
    def take_break(self):
        """Record that a break was taken"""
        self.last_break_time = time.time()
        self.logger.log("BREAK", "Break taken", "kid")
    
    def reset_daily_time(self):
        """Reset daily usage (for new day)"""
        self.today_usage_minutes = 0.0
        self.session_start = time.time()
        self._save_settings()
    
    # Lock System
    def check_and_lock(self) -> bool:
        """Check conditions and lock if needed"""
        if self.is_parent_mode:
            return False
        
        if self.is_bedtime():
            self._lock("It's bedtime! 🌙")
            return True
        
        if self.is_time_limit_reached():
            self._lock("Daily time limit reached! 🕐")
            return True
        
        return False
    
    def _lock(self, reason: str):
        """Lock the system"""
        if not self.is_locked:
            self.is_locked = True
            self.lock_reason = reason
            self.logger.log("LOCK", reason, "system")
            
            for callback in self.on_lock_callbacks:
                try:
                    callback(reason)
                except Exception:
                    pass
    
    def unlock(self, password: str) -> bool:
        """Unlock the system (requires parent password)"""
        if self.check_password(password):
            self.is_locked = False
            self.lock_reason = ""
            self.logger.log("UNLOCK", "System unlocked by parent", "parent")
            
            for callback in self.on_unlock_callbacks:
                try:
                    callback()
                except Exception:
                    pass
            return True
        return False
    
    def force_lock(self, reason: str = "Locked by parent"):
        """Force lock the system (parent action)"""
        self._lock(reason)
    
    # Callbacks
    def on_lock(self, callback: Callable):
        """Register callback for lock events"""
        self.on_lock_callbacks.append(callback)
    
    def on_unlock(self, callback: Callable):
        """Register callback for unlock events"""
        self.on_unlock_callbacks.append(callback)
    
    def on_time_warning(self, callback: Callable):
        """Register callback for time warnings"""
        self.on_time_warning_callbacks.append(callback)
    
    # Time tracking
    def _time_tracking_loop(self):
        """Background thread for time tracking"""
        last_check = time.time()
        
        while self.tracking:
            time.sleep(60)  # Check every minute
            
            if not self.is_parent_mode and not self.is_locked:
                # Add one minute of usage
                self.today_usage_minutes += 1
                
                # Check conditions
                self.check_and_lock()
                
                # Warn when time is running low
                remaining = self.get_remaining_time()
                if remaining in [15, 10, 5, 1]:
                    for callback in self.on_time_warning_callbacks:
                        try:
                            callback(remaining)
                        except Exception:
                            pass
                
                # Save periodically
                if int(self.today_usage_minutes) % 5 == 0:
                    self._save_settings()
    
    # Persistence
    def _save_settings(self):
        """Save settings to disk"""
        try:
            settings_path = self.data_path / "parental_settings.json"
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'password_hash': self.parent_password_hash,
                'policy': self.policy.to_dict(),
                'today_usage_minutes': self.today_usage_minutes,
                'last_save_date': datetime.now().strftime("%Y-%m-%d")
            }
            
            with open(settings_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def _load_settings(self):
        """Load settings from disk"""
        try:
            settings_path = self.data_path / "parental_settings.json"
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    data = json.load(f)
                
                self.parent_password_hash = data.get('password_hash')
                
                if 'policy' in data:
                    self.policy = Policy.from_dict(data['policy'])
                
                # Reset usage if new day
                last_date = data.get('last_save_date', '')
                today = datetime.now().strftime("%Y-%m-%d")
                
                if last_date == today:
                    self.today_usage_minutes = data.get('today_usage_minutes', 0)
                else:
                    self.today_usage_minutes = 0
        except Exception:
            pass
    
    def get_status(self) -> Dict:
        """Get current parental control status"""
        return {
            'is_parent_mode': self.is_parent_mode,
            'is_locked': self.is_locked,
            'lock_reason': self.lock_reason,
            'is_bedtime': self.is_bedtime(),
            'today_usage_minutes': int(self.today_usage_minutes),
            'remaining_minutes': self.get_remaining_time(),
            'daily_limit': self.policy.daily_limit_minutes,
            'password_set': self.is_password_set()
        }
    
    def shutdown(self):
        """Shutdown parental control system"""
        self.tracking = False
        self._save_settings()

