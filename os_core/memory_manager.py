"""
MiniMind OS - Memory Manager
============================
Simulates RAM allocation and management.
Uses a simple block allocation scheme for educational purposes.

Memory Layout:
- System Reserved: 256 KB (for OS core)
- User Space: 768 KB (for apps)
- Total: 1024 KB (1 MB simulated RAM)

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import threading
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class MemoryBlock:
    """Represents a block of allocated memory"""
    pid: int           # Process ID that owns this block
    start: int         # Start address
    size: int          # Size in KB
    name: str = ""     # Optional name for display

class MemoryManager:
    """
    Manages simulated RAM for MiniMind OS.
    Uses First-Fit allocation algorithm.
    """
    
    # Memory constants (in KB)
    TOTAL_MEMORY = 1024      # 1 MB total
    SYSTEM_RESERVED = 256    # Reserved for OS
    USER_MEMORY = 768        # Available for apps
    
    def __init__(self, logger=None):
        self.logger = logger
        self.lock = threading.Lock()
        
        # Memory allocation table: PID -> MemoryBlock
        self.allocation_table: Dict[int, MemoryBlock] = {}
        
        # Track free memory
        self.used_memory = self.SYSTEM_RESERVED  # System uses some memory
        
        # Reserve system memory (PID 0)
        self.allocation_table[0] = MemoryBlock(
            pid=0,
            start=0,
            size=self.SYSTEM_RESERVED,
            name="System Reserved"
        )
        
        self._log(f"Memory initialized: {self.TOTAL_MEMORY}KB total, "
                  f"{self.USER_MEMORY}KB available for apps")
    
    def allocate(self, pid: int, size: int, name: str = "") -> bool:
        """
        Allocate memory for a process.
        
        Args:
            pid: Process ID
            size: Memory size in KB
            name: Optional name for the allocation
            
        Returns:
            True if allocation successful, False otherwise
        """
        with self.lock:
            # Check if enough memory is available
            if self.get_free_memory() < size:
                self._log(f"Allocation failed for PID {pid}: "
                         f"Need {size}KB, only {self.get_free_memory()}KB free")
                return False
            
            # Find starting address (simple: use end of last allocation)
            start_address = self.used_memory
            
            # Create allocation
            self.allocation_table[pid] = MemoryBlock(
                pid=pid,
                start=start_address,
                size=size,
                name=name
            )
            
            self.used_memory += size
            self._log(f"Allocated {size}KB for PID {pid} at address {start_address}")
            
            return True
    
    def free(self, pid: int) -> bool:
        """
        Free memory allocated to a process.
        
        Args:
            pid: Process ID
            
        Returns:
            True if freed successfully, False if not found
        """
        with self.lock:
            if pid not in self.allocation_table:
                return False
            
            if pid == 0:
                self._log("Cannot free system memory")
                return False
            
            block = self.allocation_table[pid]
            freed_size = block.size
            
            del self.allocation_table[pid]
            self.used_memory -= freed_size
            
            self._log(f"Freed {freed_size}KB from PID {pid}")
            return True
    
    def get_free_memory(self) -> int:
        """Get available free memory in KB"""
        return self.TOTAL_MEMORY - self.used_memory
    
    def get_used_memory(self) -> int:
        """Get used memory in KB"""
        return self.used_memory
    
    def get_usage_percent(self) -> float:
        """Get memory usage as percentage"""
        return (self.used_memory / self.TOTAL_MEMORY) * 100
    
    def get_process_memory(self, pid: int) -> int:
        """Get memory used by a specific process"""
        if pid in self.allocation_table:
            return self.allocation_table[pid].size
        return 0
    
    def get_memory_map(self) -> List[Dict]:
        """
        Get a visual map of memory allocation.
        Returns list of blocks for display.
        """
        memory_map = []
        for pid, block in sorted(self.allocation_table.items(), 
                                  key=lambda x: x[1].start):
            memory_map.append({
                'pid': pid,
                'name': block.name,
                'start': block.start,
                'size': block.size,
                'end': block.start + block.size
            })
        return memory_map
    
    def get_stats(self) -> Dict:
        """Get memory statistics for display"""
        return {
            'total': self.TOTAL_MEMORY,
            'used': self.used_memory,
            'free': self.get_free_memory(),
            'percent': self.get_usage_percent(),
            'system_reserved': self.SYSTEM_RESERVED,
            'process_count': len(self.allocation_table)
        }
    
    def _log(self, message: str):
        """Log a message if logger is available"""
        if self.logger:
            self.logger.log("MEMORY", message)

