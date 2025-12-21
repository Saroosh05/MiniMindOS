"""
MiniMind OS - Process Manager
=============================
Handles process lifecycle: creation, execution, suspension, and termination.
Each app runs as a "process" with its own ID, state, and resource allocation.

Process States:
- NEW: Just created
- READY: Waiting to run
- RUNNING: Currently executing
- WAITING: Blocked (e.g., waiting for I/O)
- TERMINATED: Finished execution

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable

class ProcessState(Enum):
    """Process states in the OS lifecycle"""
    NEW = "New"
    READY = "Ready"
    RUNNING = "Running"
    WAITING = "Waiting"
    TERMINATED = "Terminated"

@dataclass
class Process:
    """
    Represents a process in the OS.
    Each app (Drawing, Music, etc.) becomes a process when launched.
    """
    pid: int                          # Process ID (unique)
    name: str                         # Process name (e.g., "Drawing App")
    priority: int = 1                 # Priority (1=low, 5=high)
    state: ProcessState = ProcessState.NEW
    memory_used: int = 0              # Memory in KB
    cpu_time: float = 0.0             # Total CPU time used
    start_time: float = field(default_factory=time.time)
    parent_pid: Optional[int] = None  # Parent process ID
    icon: str = "🔷"                  # Icon for UI display
    
    def to_dict(self) -> dict:
        """Convert process to dictionary for display/logging"""
        return {
            'pid': self.pid,
            'name': self.name,
            'priority': self.priority,
            'state': self.state.value,
            'memory_used': self.memory_used,
            'cpu_time': round(self.cpu_time, 2),
            'icon': self.icon
        }

class ProcessManager:
    """
    Manages all processes in MiniMind OS.
    Provides methods to create, terminate, and monitor processes.
    """
    
    def __init__(self, memory_manager=None, logger=None):
        self.process_table: Dict[int, Process] = {}  # PID -> Process
        self.next_pid: int = 1                        # Next available PID
        self.memory_manager = memory_manager
        self.logger = logger
        self.lock = threading.Lock()
        self.observers: List[Callable] = []          # UI update callbacks
        
        # Create the init process (PID 0) - always running
        self._create_init_process()
    
    def _create_init_process(self):
        """Create the initial system process"""
        init_process = Process(
            pid=0,
            name="MiniMind Init",
            priority=5,
            state=ProcessState.RUNNING,
            memory_used=128,
            icon="⚙️"
        )
        self.process_table[0] = init_process
    
    def create_process(self, name: str, priority: int = 3, 
                       memory_required: int = 64, icon: str = "🔷",
                       parent_pid: int = 0) -> Optional[int]:
        """
        Create a new process.
        
        Args:
            name: Process name
            priority: 1-5 (higher = more important)
            memory_required: Memory in KB
            icon: Display icon
            parent_pid: Parent process ID
            
        Returns:
            Process ID if successful, None if failed
        """
        with self.lock:
            # Check if memory is available
            if self.memory_manager:
                if not self.memory_manager.allocate(self.next_pid, memory_required):
                    self._log(f"Failed to create process '{name}': Not enough memory")
                    return None
            
            # Create the process
            process = Process(
                pid=self.next_pid,
                name=name,
                priority=priority,
                state=ProcessState.NEW,
                memory_used=memory_required,
                parent_pid=parent_pid,
                icon=icon
            )
            
            # Add to process table
            self.process_table[self.next_pid] = process
            pid = self.next_pid
            self.next_pid += 1
            
            # Set to READY state
            process.state = ProcessState.READY
            
            self._log(f"Process created: {name} (PID={pid}, Memory={memory_required}KB)")
            self._notify_observers()
            
            return pid
    
    def terminate_process(self, pid: int) -> bool:
        """
        Terminate a process and free its resources.
        
        Args:
            pid: Process ID to terminate
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if pid not in self.process_table:
                self._log(f"Cannot terminate: Process {pid} not found")
                return False
            
            if pid == 0:
                self._log("Cannot terminate init process")
                return False
            
            process = self.process_table[pid]
            process.state = ProcessState.TERMINATED
            
            # Free memory
            if self.memory_manager:
                self.memory_manager.free(pid)
            
            # Remove from process table
            del self.process_table[pid]
            
            self._log(f"Process terminated: {process.name} (PID={pid})")
            self._notify_observers()
            
            return True
    
    def set_process_state(self, pid: int, state: ProcessState) -> bool:
        """Change the state of a process"""
        with self.lock:
            if pid not in self.process_table:
                return False
            
            old_state = self.process_table[pid].state
            self.process_table[pid].state = state
            
            self._log(f"Process {pid} state: {old_state.value} -> {state.value}")
            self._notify_observers()
            return True
    
    def get_process(self, pid: int) -> Optional[Process]:
        """Get a process by PID"""
        return self.process_table.get(pid)
    
    def get_all_processes(self) -> List[Process]:
        """Get all active processes"""
        return list(self.process_table.values())
    
    def get_running_processes(self) -> List[Process]:
        """Get only running/ready processes"""
        return [p for p in self.process_table.values() 
                if p.state in (ProcessState.RUNNING, ProcessState.READY)]
    
    def get_process_count(self) -> int:
        """Get total number of active processes"""
        return len(self.process_table)
    
    def update_cpu_time(self, pid: int, time_slice: float):
        """Update CPU time used by a process"""
        if pid in self.process_table:
            self.process_table[pid].cpu_time += time_slice
    
    def add_observer(self, callback: Callable):
        """Add a callback to be notified of process changes"""
        self.observers.append(callback)
    
    def _notify_observers(self):
        """Notify all observers of changes"""
        for callback in self.observers:
            try:
                callback()
            except Exception:
                pass
    
    def _log(self, message: str):
        """Log a message if logger is available"""
        if self.logger:
            self.logger.log("PROCESS", message)

