#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Openbox Window Manager Theme

This module provides theming support for the Openbox window manager used by LXQt.
"""

import os
import logging
import shutil
import subprocess
import json
import hashlib
import time
from pathlib import Path
from functools import lru_cache
from typing import Dict, Any, Optional, Set
from ThemeConstants import THEME_LXQT, COLOR_ACTIVE_TITLE_BG, COLOR_ACTIVE_TITLE_TEXT
from ThemeConstants import COLOR_INACTIVE_TITLE_BG, COLOR_INACTIVE_TITLE_TEXT
from ThemeConstants import COLOR_BORDER, COLOR_MENU_BG, COLOR_MENU_TEXT
from ThemeConstants import COLOR_MENU_ACTIVE_BG, COLOR_MENU_ACTIVE_TEXT
from ThemeConstants import COLOR_TOOLTIP_BG, COLOR_TOOLTIP_TEXT
from ThemeConstants import FONT_DEFAULT, FONT_BOLD, FONT_WINDOW_TITLE
from ThemeConstants import BUTTON_LAYOUT, ICON_THEME, CURSOR_THEME

# Cache for storing theme data
_theme_cache: Dict[str, Any] = {}

# Cache for storing file hashes
_file_hashes: Dict[str, str] = {}

def _get_file_hash(file_path: str) -> str:
    """Get MD5 hash of a file's contents with caching."""
    if file_path in _file_hashes:
        return _file_hashes[file_path]
        
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        _file_hashes[file_path] = hasher.hexdigest()
    except (IOError, OSError):
        _file_hashes[file_path] = ""
    
    return _file_hashes[file_path]

def _get_dir_hash(directory: str) -> str:
    """Generate a hash for a directory's contents."""
    hasher = hashlib.md5()
    try:
        for root, _, files in os.walk(directory):
            for file in sorted(files):
                file_path = os.path.normpath(os.path.join(root, file))
                hasher.update(_get_file_hash(file_path).encode('utf-8'))
    except (IOError, OSError):
        pass
    
    return hasher.hexdigest()

logger = logging.getLogger('OpenboxTheme')

class OpenboxTheme:
    """Openbox Window Manager theme handler"""
    
    def __init__(self, opts=None):
        """Initialize the Openbox theme handler."
        
        Args:
            opts: Options object containing theme settings
        """
        self.opts = opts
        self.theme_name = THEME_LXQT
        self.dirs = self._get_theme_directories()
        
    @lru_cache(maxsize=1)
    def _get_theme_directories(self) -> Dict[str, str]:
        """Get the standard Openbox theme directories with caching."
        
        Returns:
            dict: Dictionary of theme directory paths
        """
        cache_key = f"openbox_dirs_{self.theme_name}"
        if cache_key in _theme_cache:
            return _theme_cache[cache_key]
            
        home = str(Path.home())
        dirs = {
            'themes': os.path.normpath(os.path.join(home, '.themes')),
            'openbox': os.path.normpath(os.path.join(home, '.themes', self.theme_name, 'openbox-3')),
            'config': os.path.normpath(os.path.join(home, '.config', 'openbox')),
            'local_share': os.path.normpath(os.path.join(home, '.local', 'share')),
            'cache': os.path.normpath(os.path.join(home, '.cache', 'cdetheme'))
        }
        
        # Cache the result
        _theme_cache[cache_key] = dirs
        return dirs
    
    def _get_theme_cache_file(self) -> str:
        """Get the path to the theme cache file."
        
        Returns:
            str: Path to the cache file
        """
        cache_dir = self.dirs.get('cache')
        if not cache_dir:
            return ""
            
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.normpath(os.path.join(cache_dir, 'openbox_theme_cache.json'))
    
    def _load_theme_cache(self) -> Dict[str, Any]:
        """Load the theme cache from disk."
        
        Returns:
            dict: Cached theme data
        """
        cache_file = self._get_theme_cache_file()
        if not cache_file or not os.path.exists(cache_file):
            return {}
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load theme cache: {e}")
            return {}
    
    def _save_theme_cache(self, cache_data: Dict[str, Any]) -> None:
        """Save the theme cache to disk."
        
        Args:
            cache_data: Data to cache
        """
        cache_file = self._get_theme_cache_file()
        if not cache_file:
            return
            
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except IOError as e:
            logger.warning(f"Failed to save theme cache: {e}")
    
    def _needs_theme_update(self) -> bool:
        """Check if the theme needs to be updated."
        
        Returns:
            bool: True if update is needed, False otherwise
        """
        theme_dir = os.path.normpath(os.path.join(self.dirs['themes'], self.theme_name))
        if not os.path.exists(theme_dir):
            return True
            
        cache = self._load_theme_cache()
        if not cache:
            return True
            
        # Check if theme files have changed
        current_hash = _get_dir_hash(theme_dir)
        return current_hash != cache.get('theme_hash')
    
    def install_theme(self, force: bool = False) -> bool:
        """Install the Openbox window manager theme with caching."
        
        Args:
            force: If True, force reinstallation even if not needed
            
        Returns:
            bool: True if installation was successful or not needed, False otherwise
        """
        try:
            # Check cache first
            if not force and not self._needs_theme_update():
                logger.debug("Using cached Openbox theme")
                return True
                
            # Create theme directory structure
            theme_dir = os.path.normpath(os.path.join(self.dirs['themes'], self.theme_name))
            openbox_dir = os.path.normpath(os.path.join(theme_dir, 'openbox-3'))
            
            # Create directories if they don't exist'
            os.makedirs(openbox_dir, exist_ok=True)
            
            # Create theme files
            self._create_theme_metadata(theme_dir)
            self._create_openbox_theme(openbox_dir)
            
            # Copy theme assets
            self._copy_theme_assets(openbox_dir)
            
            # Update cache
            theme_hash = _get_dir_hash(theme_dir)
            self._save_theme_cache({
                'theme_hash': theme_hash,
                'last_updated': time.time(),
                'version': '1.0'
            })
            
            logger.info(f"Installed Openbox theme to {theme_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install Openbox theme: {e}")
            return False
    
    def _create_theme_metadata(self, theme_dir):
        """Create the theme metadata file with comprehensive error handling."
        
        Args:
            theme_dir: Path to the theme directory
            
        Returns:
            bool: True if metadata was created successfully, False otherwise
        """
        try:
            metadata = f"""[Desktop Entry]"
Name={self.theme_name}
Comment=CDE-style theme for Openbox
Type=X-Theme
"""
            theme_file = os.path.normpath(os.path.join(theme_dir, 'index.theme'))
            
            # Create parent directories if they don't exist'
            os.makedirs(os.path.dirname(theme_file), exist_ok=True)
            
            # Write with atomic write pattern
            temp_file = f"{theme_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(metadata)
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic rename
            if os.path.exists(theme_file):
                os.replace(temp_file, theme_file)
            else:
                os.rename(temp_file, theme_file)
                
            # Set appropriate permissions
            os.chmod(theme_file, 0o644)
            return True
            
        except (IOError, OSError) as e:
            logger.error(f"Failed to create theme metadata: {e}")
            # Try fallback to user's home directory if we can't write to theme dir
            try:
                fallback_dir = os.path.normpath(os.path.join(str(Path.home()), '.local', 'share', 'themes', self.theme_name))
                os.makedirs(fallback_dir, exist_ok=True)
                return self._create_theme_metadata(fallback_dir)
            except Exception as fallback_e:
                logger.error(f"Fallback theme metadata creation failed: {fallback_e}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error creating theme metadata: {e}")
            return False
    
    def _create_openbox_theme(self, openbox_dir):
        """Create the Openbox theme files with comprehensive error handling."
        
        Args:
            openbox_dir: Path to the Openbox theme directory
            
        Returns:
            bool: True if theme files were created successfully, False otherwise
        """
        try:
            # Create theme directory if it doesn't exist'
            os.makedirs(openbox_dir, exist_ok=True)
            
            # Create themerc file with atomic write
            themerc_content = f"""# CDE Theme for Openbox"

# Window Title
window.title.bg: flat
window.title.bg.color: {COLOR_ACTIVE_TITLE_BG}
window.title.text.color: {COLOR_ACTIVE_TITLE_TEXT}
window.title.font: {FONT_WINDOW_TITLE}

# Inactive Window Title
window.inactive.title.bg: flat
window.inactive.title.bg.color: {COLOR_INACTIVE_TITLE_BG}
window.inactive.title.text.color: {COLOR_INACTIVE_TITLE_TEXT}
window.inactive.title.font: {FONT_WINDOW_TITLE}

# Window Border
window.border.color: {COLOR_BORDER}
window.border.width: 1

# Menu
menu.items.bg: flat
menu.items.bg.color: {COLOR_MENU_BG}
menu.items.text.color: {COLOR_MENU_TEXT}
menu.items.font: {FONT_DEFAULT}

menu.items.active.bg: flat
menu.items.active.bg.color: {COLOR_MENU_ACTIVE_BG}
menu.items.active.text.color: {COLOR_MENU_ACTIVE_TEXT}
menu.items.active.font: {FONT_DEFAULT}

# Tooltip
tooltip.bg: flat
tooltip.bg.color: {COLOR_TOOLTIP_BG}
tooltip.text.color: {COLOR_TOOLTIP_TEXT}
tooltip.font: {FONT_DEFAULT}
"""
            themerc_path = os.path.normpath(os.path.join(openbox_dir, 'themerc'))
            temp_path = f"{themerc_path}.tmp"
            
            try:
                # Write to temporary file first
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(themerc_content)
                    f.flush()
                    os.fsync(f.fileno())
                
                # Atomic replace
                if os.path.exists(themerc_path):
                    os.replace(temp_path, themerc_path)
                else:
                    os.rename(temp_path, themerc_path)
                
                # Set appropriate permissions
                os.chmod(themerc_path, 0o644)
                
            except (IOError, OSError) as e:
                # If we can't write to the target, try a fallback location'
                logger.warning(f"Failed to write themerc to {themerc_path}: {e}")
                fallback_dir = os.path.normpath(os.path.join(str(Path.home()), '.config', 'openbox', 'themes', self.theme_name))
                os.makedirs(fallback_dir, exist_ok=True)
                return self._create_openbox_theme(fallback_dir)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Openbox theme: {e}")
            return False
    
    def _copy_theme_assets(self, openbox_dir):
        """Copy theme assets to the Openbox theme directory with error handling."
        
        Args:
            openbox_dir: Path to the Openbox theme directory
            
        Returns:
            bool: True if assets were copied successfully, False otherwise
        """
        try:
            # Create necessary subdirectories with error checking
            required_dirs = [
                os.path.normpath(os.path.join(openbox_dir, 'close')),
                os.path.normpath(os.path.join(openbox_dir, 'max')),
                os.path.normpath(os.path.join(openbox_dir, 'iconify'))
            ]
            
            for dir_path in required_dirs:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    # Verify directory is writable
                    test_file = os.path.normpath(os.path.join(dir_path, '.write_test'))
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write('test')
                    os.unlink(test_file)
                except (OSError, IOError) as e:
                    logger.error(f"Cannot write to {dir_path}: {e}")
                    # Try fallback location if primary location fails
                    fallback_dir = os.path.normpath(os.path.join(str(Path.home()), '.local', 'share', 'themes', 
                                             self.theme_name, 'openbox-3', os.path.basename(dir_path)))
                    os.makedirs(fallback_dir, exist_ok=True)
                    logger.info(f"Using fallback directory: {fallback_dir}")
            
            # Create button images with error handling
            try:
                return self._create_button_images(openbox_dir)
            except Exception as e:
                logger.error(f"Failed to create button images: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error copying theme assets: {e}")
            return False
    
    def _create_button_images(self, openbox_dir):
        """Create button images for the Openbox theme."
        
        Args:
            openbox_dir: Path to the Openbox theme directory
            
        Returns:
            bool: True if button images were created successfully, False otherwise
        """
        try:
            # Create close button image
            close_btn = """/* XPM */
static char * close_btn_xpm[] = {
"16 16 2 1",
"  c #4e5d89",
". c #ff0000",
"                ",
"                ",
"  ..        ..  ",
"   ..      ..   ",
"    ..    ..    ",
"     ..  ..     ",
"      ....      ",
"       ..       ",
"      ....      ",
"     ..  ..     ",
"    ..    ..    ",
"   ..      ..   ",
"  ..        ..  ",
"                ",
"                "};
"""
            with open(os.path.normpath(os.path.join(openbox_dir, 'close.xpm')), 'w') as f:
                f.write(close_btn)
            return True
        except Exception as e:
            logger.error(f"Failed to create button images: {e}")
            return False
    
    def _load_theme_cache(self):
        """Load the theme cache."
        
        Returns:
            dict: Theme cache
        """
        cache_file = os.path.normpath(os.path.join(self.cache_dir, 'theme_cache.json'))
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    
    def _save_theme_cache(self, cache):
        """Save the theme cache."
        
        Args:
            cache: Theme cache
        """
        cache_file = os.path.normpath(os.path.join(self.cache_dir, 'theme_cache.json'))
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f)
    
    def _run_cached_command(self, cmd: list, cache_key: str, force: bool = False) -> bool:
        """Run a command with caching of the result."
        
        Args:
            cmd: Command to run
            cache_key: Unique key for caching
            force: If True, force execution even if cached
            
        Returns:
            bool: True if command was successful or already run, False otherwise
        """
        cache = self._load_theme_cache()
        command_cache = cache.setdefault('commands', {})
        
        # Check cache
        if not force and cache_key in command_cache:
            logger.debug(f"Using cached command result for {cache_key}")
            return True
            
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, universal_newlines=True)
            # Update cache
            command_cache[cache_key] = {
                'command': ' '.join(cmd),
                'timestamp': time.time(),
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            self._save_theme_cache(cache)
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            return False
    
    def apply_theme(self, force: bool = False) -> bool:
        """Apply the Openbox window manager theme with caching."
        
        Args:
            force: If True, force reapplication even if not needed
            
        Returns:
            bool: True if theme was applied successfully or already applied, False otherwise
        """
        if not self.install_theme(force):
            return False
        
        try:
            # Set the theme using lxqt-config-qt5 with caching
            success = self._run_cached_command(
                ['lxqt-config-qt5', '--config-module', 'lxqt-qt5', '--set', 'theme', self.theme_name],
                'set_theme',
                force
            )
            
            # Set the window button layout with caching
            success &= self._run_cached_command(
                ['gsettings', 'set', 'org.cinnamon.desktop.wm.preferences', 'button-layout', ThemeConstants.BUTTON_LAYOUT],
                'set_button_layout',
                force
            )
            
            # Set icon theme with caching
            success &= self._run_cached_command(
                ['lxqt-config-qt5', '--config-module', 'lxqt-qt5', '--set', 'icon_theme', ThemeConstants.ICON_THEME],
                'set_icon_theme',
                force
            )
            
            # Set cursor theme with caching
            success &= self._run_cached_command(
                ['lxqt-config-qt5', '--config-module', 'lxqt-qt5', '--set', 'cursor_theme', ThemeConstants.CURSOR_THEME],
                'set_cursor_theme',
                force
            )
            
            if success:
                logger.info("Applied Openbox window manager theme")
            else:
                logger.warning("Some theme components failed to apply")
                
            return success
            
        except Exception as e:
            logger.error(f"Error applying Openbox theme: {e}")
            return False
