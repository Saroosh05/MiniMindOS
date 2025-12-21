"""
MiniMind OS - Scheduler
=======================
Implements CPU scheduling for processes.
Uses Round-Robin with Priority scheduling algorithm.

Scheduling Policy:
- Higher priority processes get more CPU time
- Interactive apps (drawing, games) get higher priority
- Background tasks get lower priority
- Time quantum: 100ms per slice

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import threading
import time
from collections import deque
from typing import List, Optional, Callable, Dict
from .process_manager import Process, ProcessState

class Scheduler:
    """
    Round-Robin scheduler with priority support.
    Manages CPU time allocation for all processes.
    """
    
    TIME_QUANTUM = 0.1  # 100ms time slice
    
    def __init__(self, process_manager, logger=None):
        self.process_manager = process_manager
        self.logger = logger
        
        # Ready queue for each priority level (1-5)
        self.ready_queues: Dict[int, deque] = {
            i: deque() for i in range(1, 6)
        }
        
        # Currently running process
        self.current_process: Optional[int] = None
        
        # Scheduler state
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # Statistics
        self.context_switches = 0
        self.total_time = 0.0
        
        self._log("Scheduler initialized (Round-Robin with Priority)")
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        self._log("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1.0)
        self._log("Scheduler stopped")
    
    def add_process(self, pid: int, priority: int = 3):
        """
        Add a process to the ready queue.
        
        Args:
            pid: Process ID
            priority: Priority level (1-5)
        """
        with self.lock:
            # Clamp priority to valid range
            priority = max(1, min(5, priority))
            self.ready_queues[priority].append(pid)
            self._log(f"Process {pid} added to ready queue (priority {priority})")
    
    def remove_process(self, pid: int):
        """Remove a process from all queues"""
        with self.lock:
            for queue in self.ready_queues.values():
                if pid in queue:
                    queue.remove(pid)
                    break
            if self.current_process == pid:
                self.current_process = None
    
    def _scheduler_loop(self):
        """Main scheduler loop - runs in background thread"""
        while self.running:
            self._schedule_next()
            time.sleep(self.TIME_QUANTUM)
            self.total_time += self.TIME_QUANTUM
    
    def _schedule_next(self):
        """Select and run the next process"""
        with self.lock:
            # Find highest priority process
            next_pid = self._get_next_process()
            
            if next_pid is None:
                return
            
            # Context switch if needed
            if self.current_process != next_pid:
                self._context_switch(next_pid)
            
            # Update CPU time for current process
            self.process_manager.update_cpu_time(next_pid, self.TIME_QUANTUM)
    
    def _get_next_process(self) -> Optional[int]:
        """Get the next process to run (highest priority first)"""
        # Check from highest to lowest priority
        for priority in range(5, 0, -1):
            queue = self.ready_queues[priority]
            if queue:
                # Round-robin within same priority
                pid = queue.popleft()
                
                # Verify process still exists
                process = self.process_manager.get_process(pid)
                if process and process.state != ProcessState.TERMINATED:
                    # Add back to end of queue
                    queue.append(pid)
                    return pid
        
        return None
    
    def _context_switch(self, new_pid: int):
        """Perform a context switch to a new process"""
        old_pid = self.current_process
        
        # Update old process state
        if old_pid is not None:
            self.process_manager.set_process_state(old_pid, ProcessState.READY)
        
        # Update new process state
        self.process_manager.set_process_state(new_pid, ProcessState.RUNNING)
        self.current_process = new_pid
        
        self.context_switches += 1
    
    def get_queue_status(self) -> Dict:
        """Get status of all ready queues"""
        status = {}
        with self.lock:
            for priority, queue in self.ready_queues.items():
                status[priority] = list(queue)
        return status
    
    def get_stats(self) -> Dict:
        """Get scheduler statistics"""
        return {
            'current_process': self.current_process,
            'context_switches': self.context_switches,
            'total_time': round(self.total_time, 2),
            'time_quantum': self.TIME_QUANTUM,
            'running': self.running
        }
    
    def _log(self, message: str):
        """Log a message if logger is available"""
        if self.logger:
            self.logger.log("SCHEDULER", message)

