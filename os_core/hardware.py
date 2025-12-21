"""
MiniMind OS - Hardware Simulation
=================================
Simulates hardware components for educational demonstration.

Simulated Hardware:
- CPU: Clock speed, utilization
- RAM: Total/used memory (connected to Memory Manager)
- Clock: System time, uptime
- Display: Screen resolution, color depth
- Input: Mouse/keyboard events
- Audio: Sound output simulation

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import time
import threading
from dataclasses import dataclass
from typing import Dict, List, Callable, Optional
from datetime import datetime

@dataclass
class CPUInfo:
    """CPU hardware information"""
    name: str = "MiniMind CPU"
    cores: int = 2
    clock_speed: str = "1.0 GHz"
    utilization: float = 0.0

@dataclass
class DisplayInfo:
    """Display hardware information"""
    width: int = 1024
    height: int = 768
    color_depth: int = 32
    refresh_rate: int = 60

class Hardware:
    """
    Simulates hardware components for MiniMind OS.
    Provides system information and hardware abstraction.
    """
    
    def __init__(self, memory_manager=None):
        self.memory_manager = memory_manager
        self.start_time = time.time()
        
        # Hardware components
        self.cpu = CPUInfo()
        self.display = DisplayInfo()
        
        # Input event queue
        self.input_queue: List[Dict] = []
        self.input_lock = threading.Lock()
        
        # Audio state
        self.audio_playing = False
        self.audio_volume = 50  # 0-100
        
        # Event listeners - must be initialized before clock thread
        self.listeners: Dict[str, List[Callable]] = {
            'input': [],
            'clock': [],
            'audio': []
        }
        
        # System clock
        self.clock_running = True
        self.clock_thread = threading.Thread(target=self._clock_loop, daemon=True)
        self.clock_thread.start()
    
    def get_uptime(self) -> float:
        """Get system uptime in seconds"""
        return time.time() - self.start_time
    
    def get_uptime_string(self) -> str:
        """Get formatted uptime string"""
        uptime = int(self.get_uptime())
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_system_time(self) -> str:
        """Get current system time"""
        return datetime.now().strftime("%I:%M:%S %p")
    
    def get_system_date(self) -> str:
        """Get current system date"""
        return datetime.now().strftime("%B %d, %Y")
    
    def get_cpu_info(self) -> Dict:
        """Get CPU information"""
        return {
            'name': self.cpu.name,
            'cores': self.cpu.cores,
            'clock_speed': self.cpu.clock_speed,
            'utilization': self.cpu.utilization
        }
    
    def get_memory_info(self) -> Dict:
        """Get memory information from Memory Manager"""
        if self.memory_manager:
            return self.memory_manager.get_stats()
        return {
            'total': 1024,
            'used': 256,
            'free': 768,
            'percent': 25.0
        }
    
    def get_display_info(self) -> Dict:
        """Get display information"""
        return {
            'resolution': f"{self.display.width}x{self.display.height}",
            'color_depth': f"{self.display.color_depth}-bit",
            'refresh_rate': f"{self.display.refresh_rate} Hz"
        }
    
    def set_cpu_utilization(self, utilization: float):
        """Update CPU utilization (0-100)"""
        self.cpu.utilization = max(0, min(100, utilization))
    
    # Input handling
    def queue_input_event(self, event_type: str, data: Dict):
        """Queue an input event (mouse, keyboard)"""
        with self.input_lock:
            event = {
                'type': event_type,
                'data': data,
                'timestamp': time.time()
            }
            self.input_queue.append(event)
            self._notify('input', event)
    
    def get_input_events(self) -> List[Dict]:
        """Get and clear pending input events"""
        with self.input_lock:
            events = self.input_queue.copy()
            self.input_queue.clear()
            return events
    
    # Audio handling
    def play_sound(self, sound_name: str):
        """Simulate playing a sound"""
        self.audio_playing = True
        self._notify('audio', {'action': 'play', 'sound': sound_name})
    
    def stop_sound(self):
        """Stop audio playback"""
        self.audio_playing = False
        self._notify('audio', {'action': 'stop'})
    
    def set_volume(self, volume: int):
        """Set audio volume (0-100)"""
        self.audio_volume = max(0, min(100, volume))
        self._notify('audio', {'action': 'volume', 'level': self.audio_volume})
    
    def get_audio_status(self) -> Dict:
        """Get audio system status"""
        return {
            'playing': self.audio_playing,
            'volume': self.audio_volume
        }
    
    # System info
    def get_system_info(self) -> Dict:
        """Get complete system information"""
        return {
            'os_name': 'MiniMind OS',
            'version': '1.0.0',
            'uptime': self.get_uptime_string(),
            'time': self.get_system_time(),
            'date': self.get_system_date(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'display': self.get_display_info(),
            'audio': self.get_audio_status()
        }
    
    # Event system
    def add_listener(self, event_type: str, callback: Callable):
        """Add an event listener"""
        if event_type in self.listeners:
            self.listeners[event_type].append(callback)
    
    def _notify(self, event_type: str, data: Dict):
        """Notify listeners of an event"""
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                try:
                    callback(data)
                except Exception:
                    pass
    
    def _clock_loop(self):
        """Background thread for system clock updates"""
        while self.clock_running:
            self._notify('clock', {
                'time': self.get_system_time(),
                'uptime': self.get_uptime_string()
            })
            time.sleep(1)
    
    def shutdown(self):
        """Shutdown hardware simulation"""
        self.clock_running = False
        self.stop_sound()

