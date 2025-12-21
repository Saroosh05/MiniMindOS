"""
MiniMind OS - Virtual File System
=================================
Implements a sandboxed file system for safe kid usage.

File System Structure:
/
├── system/          (read-only, hidden from kids)
│   ├── config/      (OS configuration)
│   └── logs/        (activity logs)
├── kids/            (read-write for kids)
│   ├── drawings/    (saved artwork)
│   ├── stories/     (story files)
│   └── music/       (music files)
└── shared/          (read-only media content)
    ├── stories/     (pre-loaded stories)
    └── music/       (pre-loaded music)

Roll Numbers: 2023-CS-67, 2023-CS-63
"""

import os
import json
import time
import threading
from enum import Enum, Flag, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

class Permission(Flag):
    """File/Directory permissions"""
    NONE = 0
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()
    ALL = READ | WRITE | EXECUTE

class FileType(Enum):
    """Types of files in the system"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    JSON = "json"
    BINARY = "binary"

@dataclass
class File:
    """Represents a file in the virtual file system"""
    name: str
    path: str
    file_type: FileType = FileType.TEXT
    content: Any = ""
    size: int = 0
    owner: str = "kid"
    permissions: Permission = Permission.READ | Permission.WRITE
    created: float = field(default_factory=time.time)
    modified: float = field(default_factory=time.time)
    icon: str = "📄"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'name': self.name,
            'path': self.path,
            'type': self.file_type.value,
            'content': self.content,
            'size': self.size,
            'owner': self.owner,
            'permissions': self.permissions.value,
            'created': self.created,
            'modified': self.modified,
            'icon': self.icon
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'File':
        """Create File from dictionary"""
        return File(
            name=data['name'],
            path=data['path'],
            file_type=FileType(data.get('type', 'text')),
            content=data.get('content', ''),
            size=data.get('size', 0),
            owner=data.get('owner', 'kid'),
            permissions=Permission(data.get('permissions', 3)),
            created=data.get('created', time.time()),
            modified=data.get('modified', time.time()),
            icon=data.get('icon', '📄')
        )

@dataclass
class Directory:
    """Represents a directory in the virtual file system"""
    name: str
    path: str
    owner: str = "system"
    permissions: Permission = Permission.READ | Permission.WRITE
    files: Dict[str, File] = field(default_factory=dict)
    subdirs: Dict[str, 'Directory'] = field(default_factory=dict)
    icon: str = "📁"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'name': self.name,
            'path': self.path,
            'owner': self.owner,
            'permissions': self.permissions.value,
            'files': {k: v.to_dict() for k, v in self.files.items()},
            'subdirs': {k: v.to_dict() for k, v in self.subdirs.items()},
            'icon': self.icon
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Directory':
        """Create Directory from dictionary"""
        directory = Directory(
            name=data['name'],
            path=data['path'],
            owner=data.get('owner', 'system'),
            permissions=Permission(data.get('permissions', 3)),
            icon=data.get('icon', '📁')
        )
        
        # Restore files
        for name, file_data in data.get('files', {}).items():
            directory.files[name] = File.from_dict(file_data)
        
        # Restore subdirectories
        for name, subdir_data in data.get('subdirs', {}).items():
            directory.subdirs[name] = Directory.from_dict(subdir_data)
        
        return directory

class FileSystem:
    """
    Virtual File System for MiniMind OS.
    Provides sandboxed file operations with access control.
    """
    
    def __init__(self, data_path: str = "data", logger=None):
        self.data_path = Path(data_path)
        self.logger = logger
        self.lock = threading.Lock()
        
        # Root directory
        self.root = Directory(name="/", path="/", owner="system")
        
        # Current user (kid or parent)
        self.current_user = "kid"
        
        # Initialize file system structure
        self._initialize_filesystem()
        
        # Load saved data
        self._load_filesystem()
        
        self._log("File system initialized")
    
    def _initialize_filesystem(self):
        """Create the default directory structure"""
        # System directory (hidden, read-only for kids)
        system_dir = Directory(
            name="system",
            path="/system",
            owner="system",
            permissions=Permission.READ,
            icon="⚙️"
        )
        system_dir.subdirs["config"] = Directory(
            name="config",
            path="/system/config",
            owner="system",
            permissions=Permission.READ
        )
        system_dir.subdirs["logs"] = Directory(
            name="logs",
            path="/system/logs",
            owner="system",
            permissions=Permission.READ
        )
        
        # Kids directory (full access for kids)
        kids_dir = Directory(
            name="kids",
            path="/kids",
            owner="kid",
            permissions=Permission.ALL,
            icon="👶"
        )
        kids_dir.subdirs["drawings"] = Directory(
            name="drawings",
            path="/kids/drawings",
            owner="kid",
            permissions=Permission.ALL,
            icon="🎨"
        )
        kids_dir.subdirs["stories"] = Directory(
            name="stories",
            path="/kids/stories",
            owner="kid",
            permissions=Permission.ALL,
            icon="📚"
        )
        kids_dir.subdirs["music"] = Directory(
            name="music",
            path="/kids/music",
            owner="kid",
            permissions=Permission.ALL,
            icon="🎵"
        )
        
        # Shared directory (read-only media)
        shared_dir = Directory(
            name="shared",
            path="/shared",
            owner="system",
            permissions=Permission.READ,
            icon="📂"
        )
        shared_dir.subdirs["stories"] = Directory(
            name="stories",
            path="/shared/stories",
            owner="system",
            permissions=Permission.READ,
            icon="📖"
        )
        shared_dir.subdirs["music"] = Directory(
            name="music",
            path="/shared/music",
            owner="system",
            permissions=Permission.READ,
            icon="🎶"
        )
        
        # Add to root
        self.root.subdirs["system"] = system_dir
        self.root.subdirs["kids"] = kids_dir
        self.root.subdirs["shared"] = shared_dir
    
    def _check_permission(self, path: str, required: Permission) -> bool:
        """Check if current user has required permission for path"""
        # Parent has all permissions
        if self.current_user == "parent":
            return True
        
        # Kid cannot access system directory
        if path.startswith("/system") and self.current_user == "kid":
            return False
        
        # Get the item's permissions
        item = self._get_item(path)
        if item is None:
            return False
        
        return bool(item.permissions & required)
    
    def _get_item(self, path: str):
        """Get a file or directory by path"""
        if path == "/":
            return self.root
        
        parts = path.strip("/").split("/")
        current = self.root
        
        for part in parts[:-1]:
            if part in current.subdirs:
                current = current.subdirs[part]
            else:
                return None
        
        # Check for file or directory
        last = parts[-1]
        if last in current.subdirs:
            return current.subdirs[last]
        elif last in current.files:
            return current.files[last]
        
        return None
    
    def _get_parent_dir(self, path: str) -> Optional[Directory]:
        """Get the parent directory of a path"""
        if path == "/":
            return None
        
        parent_path = "/".join(path.rstrip("/").split("/")[:-1])
        if not parent_path:
            parent_path = "/"
        
        return self._get_item(parent_path)
    
    # Public API
    def set_user(self, user: str):
        """Set current user (kid or parent)"""
        self.current_user = user
        self._log(f"User changed to: {user}")
    
    def list_directory(self, path: str = "/") -> Dict:
        """
        List contents of a directory.
        
        Returns:
            Dictionary with 'dirs' and 'files' lists
        """
        if not self._check_permission(path, Permission.READ):
            self._log(f"Access denied: {path}")
            return {'dirs': [], 'files': [], 'error': 'Access denied'}
        
        directory = self._get_item(path)
        if not isinstance(directory, Directory):
            return {'dirs': [], 'files': [], 'error': 'Not a directory'}
        
        # Filter out system directories for kids
        dirs = []
        for name, subdir in directory.subdirs.items():
            if self.current_user == "kid" and name == "system":
                continue
            dirs.append({
                'name': name,
                'path': subdir.path,
                'icon': subdir.icon
            })
        
        files = []
        for name, file in directory.files.items():
            files.append({
                'name': name,
                'path': file.path,
                'type': file.file_type.value,
                'size': file.size,
                'icon': file.icon
            })
        
        return {'dirs': dirs, 'files': files}
    
    def create_file(self, path: str, content: Any = "", 
                    file_type: FileType = FileType.TEXT) -> bool:
        """Create a new file"""
        parent_path = "/".join(path.rstrip("/").split("/")[:-1])
        if not parent_path:
            parent_path = "/"
        
        if not self._check_permission(parent_path, Permission.WRITE):
            self._log(f"Cannot create file: Access denied to {parent_path}")
            return False
        
        with self.lock:
            parent = self._get_parent_dir(path)
            if parent is None:
                return False
            
            filename = path.split("/")[-1]
            
            # Determine icon based on type
            icons = {
                FileType.TEXT: "📄",
                FileType.IMAGE: "🖼️",
                FileType.AUDIO: "🎵",
                FileType.JSON: "📋"
            }
            
            file = File(
                name=filename,
                path=path,
                file_type=file_type,
                content=content,
                size=len(str(content)),
                owner=self.current_user,
                icon=icons.get(file_type, "📄")
            )
            
            parent.files[filename] = file
            self._log(f"File created: {path}")
            self._save_filesystem()
            return True
    
    def read_file(self, path: str) -> Optional[Any]:
        """Read file content"""
        if not self._check_permission(path, Permission.READ):
            self._log(f"Cannot read: Access denied to {path}")
            return None
        
        file = self._get_item(path)
        if not isinstance(file, File):
            return None
        
        return file.content
    
    def write_file(self, path: str, content: Any) -> bool:
        """Write content to existing file"""
        if not self._check_permission(path, Permission.WRITE):
            self._log(f"Cannot write: Access denied to {path}")
            return False
        
        with self.lock:
            file = self._get_item(path)
            if not isinstance(file, File):
                return False
            
            file.content = content
            file.size = len(str(content))
            file.modified = time.time()
            
            self._log(f"File updated: {path}")
            self._save_filesystem()
            return True
    
    def delete_file(self, path: str) -> bool:
        """Delete a file"""
        if not self._check_permission(path, Permission.WRITE):
            self._log(f"Cannot delete: Access denied to {path}")
            return False
        
        with self.lock:
            parent = self._get_parent_dir(path)
            if parent is None:
                return False
            
            filename = path.split("/")[-1]
            if filename in parent.files:
                del parent.files[filename]
                self._log(f"File deleted: {path}")
                self._save_filesystem()
                return True
            
            return False
    
    def create_directory(self, path: str) -> bool:
        """Create a new directory"""
        parent_path = "/".join(path.rstrip("/").split("/")[:-1])
        if not parent_path:
            parent_path = "/"
        
        if not self._check_permission(parent_path, Permission.WRITE):
            return False
        
        with self.lock:
            parent = self._get_parent_dir(path)
            if parent is None:
                return False
            
            dirname = path.split("/")[-1]
            new_dir = Directory(
                name=dirname,
                path=path,
                owner=self.current_user
            )
            
            parent.subdirs[dirname] = new_dir
            self._log(f"Directory created: {path}")
            self._save_filesystem()
            return True
    
    def file_exists(self, path: str) -> bool:
        """Check if a file exists"""
        return self._get_item(path) is not None
    
    def get_file_info(self, path: str) -> Optional[Dict]:
        """Get file metadata"""
        item = self._get_item(path)
        if item is None:
            return None
        
        if isinstance(item, File):
            return item.to_dict()
        elif isinstance(item, Directory):
            return item.to_dict()
        
        return None
    
    # Persistence
    def _save_filesystem(self):
        """Save filesystem state to disk"""
        try:
            fs_path = self.data_path / "filesystem.json"
            fs_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(fs_path, 'w') as f:
                json.dump(self.root.to_dict(), f, indent=2)
        except Exception as e:
            self._log(f"Failed to save filesystem: {e}")
    
    def _load_filesystem(self):
        """Load filesystem state from disk"""
        try:
            fs_path = self.data_path / "filesystem.json"
            if fs_path.exists():
                with open(fs_path, 'r') as f:
                    data = json.load(f)
                    self.root = Directory.from_dict(data)
                    self._log("Filesystem loaded from disk")
        except Exception as e:
            self._log(f"Failed to load filesystem: {e}")
    
    def _log(self, message: str):
        """Log a message if logger is available"""
        if self.logger:
            self.logger.log("FILESYSTEM", message)

