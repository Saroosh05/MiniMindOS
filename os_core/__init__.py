# MiniMind OS - Core Module
# This module contains the core OS components:
# - Process Manager: Handles process creation, termination, and state management
# - Memory Manager: Simulates memory allocation and tracking
# - Scheduler: Implements Round-Robin scheduling with priority support
# - Hardware: Simulates hardware interactions (CPU, RAM, Clock)

from .process_manager import ProcessManager
from .memory_manager import MemoryManager
from .scheduler import Scheduler
from .hardware import Hardware

__all__ = ['ProcessManager', 'MemoryManager', 'Scheduler', 'Hardware']

