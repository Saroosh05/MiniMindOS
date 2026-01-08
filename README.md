# MiniMind OS

**A Child-Friendly Operating System Prototype**

---

## Description

MiniMind OS is a child-friendly operating system prototype designed for kids aged 2-8 years. It provides a safe, educational computing environment with parental controls, time limits, and age-appropriate applications.

This project demonstrates core Operating System concepts including:
- **Process Management** - Process creation, termination, and state management
- **Memory Management** - Memory allocation and tracking
- **CPU Scheduling** - Round-robin with priority scheduling
- **File System** - Virtual sandboxed file system with permissions
- **Security** - Parental controls, access control, activity logging
- **Hardware Simulation** - CPU, RAM, Clock, and I/O simulation

---

## Features

### Kid Mode
- 🎨 **Drawing App** - Paint and create artwork with auto-save
- 📚 **Story Reader** - Read kid-friendly stories with large text
- 🎵 **Music Player** - Listen to children's songs with visual feedback
- 🧩 **Puzzle Games** - Educational games (Color Match, Shape Puzzle, Memory, Number Sort)

### Parental Controls
- 🔒 Password-protected parent mode
- ⏰ Daily time limits
- 🌙 Bedtime scheduling
- 📱 App enable/disable controls
- 📋 Activity logging

### OS Features
- Process viewer showing running applications
- Memory usage visualization
- Real-time system status
- Auto-save and crash recovery
- Sandboxed file system

---

## Requirements

- **Python 3.8+**
- **Tkinter** (usually included with Python)

No additional packages required!

---

## How to Run

1. Open a terminal/command prompt
2. Navigate to the MiniMindOS folder
3. Run the main file:

```bash
python main.py
```

Or on some systems:
```bash
python3 main.py
```

---

## Project Structure

```
MiniMindOS/
├── main.py              # Main launcher & OS kernel
├── README.md            # This file
│
├── os_core/             # Core OS components
│   ├── __init__.py
│   ├── process_manager.py   # Process lifecycle management
│   ├── memory_manager.py    # Memory allocation
│   ├── scheduler.py         # CPU scheduling
│   └── hardware.py          # Hardware simulation
│
├── filesystem/          # Virtual file system
│   ├── __init__.py
│   └── fs.py               # File operations & permissions
│
├── security/            # Security & parental controls
│   ├── __init__.py
│   └── parental_control.py  # Password, time limits, logging
│
├── apps/                # Kid-friendly applications
│   ├── __init__.py
│   ├── drawing.py          # Drawing/painting app
│   ├── story_reader.py     # Story reading app
│   ├── music_player.py     # Music player app
│   └── puzzle.py           # Puzzle games
│
├── ui/                  # User interface components
│   ├── __init__.py
│   ├── styles.py           # Colors, fonts, dimensions
│   ├── home_screen.py      # Main home screen
│   ├── parent_panel.py     # Parental control panel
│   └── process_viewer.py   # Process & memory viewers
│
├── config/              # Configuration files
│   └── policies.json       # Default policies
│
└── data/                # Persistent data storage
    ├── stories/            # Story files
    ├── music/              # Music files (simulated)
    └── kids_files/         # Kid's saved work
```

---

## OS Modules Mapping

| OS Concept | Implementation |
|------------|----------------|
| Process Management | `os_core/process_manager.py` - Each app runs as a process |
| Memory Management | `os_core/memory_manager.py` - Simulated RAM allocation |
| CPU Scheduling | `os_core/scheduler.py` - Round-robin with priority |
| File System | `filesystem/fs.py` - Virtual FS with permissions |
| I/O Handling | `os_core/hardware.py` - Mouse, audio simulation |
| Security | `security/parental_control.py` - Access control, sandbox |

---

## Parent Guide

### First Time Setup
1. Click the parent icon (👨‍👩‍👧) in the top-left corner
2. Create a password when prompted
3. Configure time limits and allowed apps

### Features
- **App Control**: Enable/disable apps for kids
- **Time Limits**: Set daily usage limits (15-240 minutes)
- **Bedtime**: Automatically lock at specified times
- **Activity Log**: View all kid activities
- **Lock/Unlock**: Manually lock or unlock the system

### Default Settings
- Daily limit: 2 hours
- Bedtime: 8:00 PM - 7:00 AM
- All apps enabled
- Max volume: 80%

---

## Technical Details

### Process States
- NEW → READY → RUNNING → WAITING → TERMINATED

### Memory Layout
- Total: 1024 KB (simulated)
- System Reserved: 256 KB
- User Space: 768 KB

### Scheduling Algorithm
- Round-Robin with Priority
- Time Quantum: 100ms
- Priority Range: 1-5 (higher = more important)

### File System
- `/system/` - System files (read-only for kids)
- `/kids/` - Kid's files (read-write)
- `/shared/` - Shared media (read-only)

---

