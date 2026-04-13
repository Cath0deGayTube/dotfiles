#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
LXQt Theme Module

This module provides LXQt-specific theming functionality.
"""

import os
import subprocess
import logging
import shutil
import json
import hashlib
from pathlib import Path
from functools import lru_cache
from typing import Dict, Any, Optional

# Cache for storing theme settings to avoid redundant file operations
_theme_cache: Dict[str, Any] = {}

# Cache for storing file modification times
_file_mtimes: Dict[str, float] = {}

def _get_file_hash(file_path: str) -> str:
    """Get MD5 hash of a file's contents."""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError):
        return ""
from BaseTheme import BaseTheme
from ThemeConstants import (
    THEME_LXQT, ICON_THEME, CURSOR_THEME, FONT_DEFAULT, FONT_BOLD,
    COLOR_ACTIVE_TITLE_BG, COLOR_INACTIVE_TITLE_BG, COLOR_MENU_BG,
    COLOR_MENU_ACTIVE_BG, COLOR_MENU_TEXT, COLOR_MENU_ACTIVE_TEXT,
    BUTTON_LAYOUT
)
from LxqtUtils import LxqtUtils
from OpenboxTheme import OpenboxTheme

class LxqtTheme(BaseTheme):
    """LXQt-specific theming implementation"""
    
    def __init__(self, opts=None):
        """Initialize the LXQt theme"
        
        Args:
            opts: Options object containing theme settings
        """
        super().__init__(opts)
        self.environment = 'lxqt'
        self.cur_theme = THEME_LXQT
        self.logger = logging.getLogger('LxqtTheme')
        self.utils = LxqtUtils()
        self.openbox_theme = OpenboxTheme(opts)
        self.dirs = self._get_theme_directories()
        self.initialized = False
    
    @lru_cache(maxsize=1)
    def _get_theme_directories(self) -> Dict[str, str]:
        """Get the standard LXQt theme directories with caching and fallbacks."
        
        Returns:
            dict: Dictionary of theme directory paths with fallback to system temp if needed
        """
        cache_key = 'theme_directories'
        if cache_key in _theme_cache:
            return _theme_cache[cache_key]
            
        try:
            home = str(Path.home())
            temp_dir = os.path.normpath(os.path.join(tempfile.gettempdir()), 'cdetheme')
            
            # Define primary and fallback directories
            dirs = {
                'themes': os.path.normpath(os.path.join(home, '.themes')),
                'icons': os.path.normpath(os.path.join(home, '.icons')),
                'local_share': os.path.normpath(os.path.join(home, '.local', 'share')),
                'lxqt': os.path.normpath(os.path.join(home, '.config', 'lxqt')),
                'openbox': os.path.normpath(os.path.join(home, '.config', 'openbox')),
                'backgrounds': os.path.normpath(os.path.join(home, '.local', 'share', 'backgrounds')),
                'cache': os.path.normpath(os.path.join(home, '.cache', 'cdetheme'))
            }
            
            # Create directories if they don't exist'
            for name, path in dirs.items():
                try:
                    os.makedirs(path, exist_ok=True)
                    # Verify write access
                    test_file = os.path.normpath(os.path.join(path, '.write_test'))
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write('test')
                    os.unlink(test_file)
                except (OSError, IOError) as e:
                    self.logger.warning(f"Cannot write to {path}: {e}")
                    # Fallback to temp directory if we can't write to the primary location'
                    fallback_dir = os.path.normpath(os.path.join(temp_dir, name))
                    try:
                        os.makedirs(fallback_dir, exist_ok=True)
                        dirs[name] = fallback_dir
                        self.logger.info(f"Using fallback directory: {fallback_dir}")
                    except (OSError, IOError) as e:
                        self.logger.error(f"Failed to create fallback directory {fallback_dir}: {e}")
                        # If we can't create the fallback, use a temporary file'
                        dirs[name] = tempfile.mkdtemp(prefix=f'cdetheme_{name}_')
                        self.logger.warning(f"Using temporary directory: {dirs[name]}")
            
            # Cache the result
            _theme_cache[cache_key] = dirs
            return dirs
            
        except Exception as e:
            self.logger.critical(f"Critical error getting theme directories: {e}")
            # Return minimal working directories in temp if all else fails
            temp_base = tempfile.mkdtemp(prefix='cdetheme_')
            return {
                'themes': temp_base, 'icons': temp_base, 'local_share': temp_base, 'lxqt': temp_base,
                'openbox': temp_base,
                'backgrounds': temp_base,
                'cache': temp_base
            }
    
    def _cache_theme_settings(self, settings: Dict[str, Any]) -> None:
        """Cache theme settings to disk."
        
        Args:
            settings: Dictionary of settings to cache
        """
        try:
            cache_dir = self.dirs.get('cache')
            if cache_dir:
                os.makedirs(cache_dir, exist_ok=True)
                cache_file = os.path.normpath(os.path.join(cache_dir, 'theme_settings.json'))
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2)
        except (IOError, OSError) as e:
            self.logger.warning(f"Failed to cache theme settings: {e}")
    
    def _get_cached_settings(self) -> Dict[str, Any]:
        """Get cached theme settings from disk."
        
        Returns:
            Dictionary of cached settings or empty dict if not found
        """
        try:
            cache_file = os.path.normpath(os.path.join(self.dirs.get('cache', ''), 'theme_settings.json'))
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (IOError, OSError, json.JSONDecodeError) as e:
            self.logger.warning(f"Failed to load cached settings: {e}")
        return {}
    
    def _has_theme_changed(self) -> bool:
        """Check if theme files have changed since last cache."
        
        Returns:
            bool: True if theme files have changed, False otherwise
        """
        theme_dir = os.path.normpath(os.path.join(self.dirs['themes'], self.cur_theme))
        if not os.path.exists(theme_dir):
            return True
            
        # Check if theme directory has changed
        current_hash = _get_file_hash(os.path.normpath(os.path.join(theme_dir, 'index.theme')))
        cached_settings = self._get_cached_settings()
        cached_hash = cached_settings.get('theme_hash')
        
        return current_hash != cached_hash
    
    def init_theme(self):
        """Initialize the LXQt theme with caching."
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self.logger.info("Initializing LXQt theme")
            
            # Check cache first
            if not self._has_theme_changed() and self.initialized:
                self.logger.debug("Using cached theme settings")
                return True
            
            # Create necessary directories
            for dir_path in self.dirs.values():
                os.makedirs(dir_path, exist_ok=True)
            
            # Initialize Openbox theme
            if not self.openbox_theme.install_theme():
                self.logger.error("Failed to initialize Openbox theme")
                return False
            
            # Cache the current theme state
            theme_dir = os.path.normpath(os.path.join(self.dirs['themes'], self.cur_theme))
            theme_hash = _get_file_hash(os.path.normpath(os.path.join(theme_dir, 'index.theme')))
            self._cache_theme_settings({
                'theme_hash': theme_hash,
                'initialized': True,
                'theme_name': self.cur_theme
            })
            
            self.initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LXQt theme: {e}")
            return False
    
    def _should_update_component(self, component_name: str, force: bool = False) -> bool:
        """Check if a component needs to be updated."
        
        Args:
            component_name: Name of the component to check
            force: If True, always return True
            
        Returns:
            bool: True if the component should be updated, False otherwise
        """
        if force:
            return True
            
        cache_key = f"{component_name}_last_updated"
        cached_settings = self._get_cached_settings()
        
        # Check if this component was already updated in this session
        if hasattr(self, f'_{cache_key}') and getattr(self, f'_{cache_key}'):
            return False
            
        # Check if the component needs updating based on cache
        if not self._has_theme_changed() and cache_key in cached_settings:
            self.logger.debug(f"Using cached {component_name} settings")
            return False
            
        return True
    
    def _mark_component_updated(self, component_name: str) -> None:
        """Mark a component, updated in the cache."
        
        Args:
            component_name: Name of the component to mark, updated
        """
        cache_key = f"{component_name}_last_updated"
        setattr(self, f'_{cache_key}', True)
        
        # Update disk cache
        cached_settings = self._get_cached_settings()
        cached_settings[cache_key] = str(datetime.now().timestamp())
        self._cache_theme_settings(cached_settings)
    
    def update_theme(self, force: bool = False):
        """Update the LXQt theme with current settings."
        
        Args:
            force: If True, force update all components
            
        Returns:
            bool: True if theme was updated successfully, False otherwise
        """
        if not self.initialized and not self.init_theme():
            return False
        
        self.logger.info("Updating LXQt theme")
        
        try:
            # Apply all theme components with caching
            components = [
                (self.apply_colors, 'colors'),
                (self.apply_window_decorations, 'window_decorations'),
                (self.apply_icons, 'icons'),
                (self.apply_cursor_theme, 'cursor_theme'),
                (self.apply_font_settings, 'font_settings')
            ]
            
            results = []
            for component, name in components:
                if self._should_update_component(name, force):
                    result = component()
                    if result:
                        self._mark_component_updated(name)
                    results.append(result)
                else:
                    results.append(True)  # Consider cached components, successful
            
            return all(results)
            
        except Exception as e:
            self.logger.error(f"Failed to update LXQt theme: {e}")
            return False
    
    def _apply_with_fallback(self, func, *args, max_retries=2, **kwargs):
        """Helper method to apply a function with retries and fallbacks."
        
        Args:
            func: Function to call
            *args: Positional arguments to pass to the function
            max_retries: Maximum number of retry attempts
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Tuple of (success, result) where success is a boolean
        """
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                result = func(*args, **kwargs)
                return True, result
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 0.5  # Exponential backoff
                    self.logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed, retrying in {wait_time}s: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"All attempts failed: {e}")
        
        return False, last_error
    
    def _apply_color_scheme(self):
        """Internal method to apply color scheme with fallback to alternative methods."""
        # Try primary method first
        success, _ = self._apply_with_fallback(
            self.utils.run_lxqt_config_command,
            'lxqt-qt5', 'color_scheme', 'CDE.colors'
        )
        
        if not success:
            self.logger.warning("Falling back to manual color scheme application")
            # Try alternative method using gsettings
            try:
                subprocess.run(
                    ['gsettings', 'set', 'org.gnome.desktop.interface', 'gtk-theme', 'CDE'],
                    check=True, capture_output=True, text=True
                , universal_newlines=True)
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Fallback color scheme application failed: {e}")
                return False
        return True
    
    def apply_colors(self):
        """Apply color scheme to LXQt with comprehensive error handling and fallbacks."
        
        Returns:
            bool: True if colors were applied successfully or partially, False only if all methods fail
        """
        self.logger.info("Applying LXQt color scheme")
        
        # Track overall success
        overall_success = True
        
        # Apply color scheme
        if not self._apply_color_scheme():
            overall_success = False
            self.logger.warning("Color scheme application partially failed")
        
        # Apply window colors with fallback
        window_colors = [
            ('window_color', COLOR_ACTIVE_TITLE_BG), ('inactive_window_color', COLOR_INACTIVE_TITLE_BG)
        ]
        
        for color_type, color_value in window_colors:
            success, _ = self._apply_with_fallback(
                self.utils.run_lxqt_config_command,
                'lxqt-qt5', color_type, color_value
            )
            if not success:
                overall_success = False
                self.logger.warning(f"Failed to apply {color_type}")
        
        # If all else fails, try to set a basic color scheme
        if not overall_success:
            self.logger.warning("Attempting minimal color setup")
            try:
                # Try to set at least the basic theme
                subprocess.run(
                    ['lxqt-config-appearance', '--select-theme', 'breeze'],
                    check=False, capture_output=True, text=True
                , universal_newlines=True)
            except Exception as e:
                self.logger.error(f"Minimal color setup failed: {e}")
        
        return overall_success  # Return True if any method succeeded
    
    def apply_window_decorations(self):
        """Apply window decorations in LXQt with comprehensive error handling and fallbacks."
        
        Returns:
            bool: True if window decorations were applied successfully or partially, False only if all methods fail
        """
        self.logger.info("Applying LXQt window decorations")
        
        # Track overall success
        overall_success = True
        
        # Try to apply Openbox theme with retries
        try:
            theme_success = False
            for attempt in range(3):  # Try up to 3 times
                try:
                    if self.openbox_theme.apply_theme(force=attempt > 0):
                        theme_success = True
                        break
                    time.sleep(0.5 * (attempt + 1))
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} to apply Openbox theme failed: {e}")
            
            if not theme_success:
                overall_success = False
                self.logger.error("All attempts to apply Openbox theme failed")
                
                # Fallback to default theme
                try:
                    subprocess.run(
                        ['openbox', '--reconfigure'], check=True, capture_output=True, text=True
                    , universal_newlines=True)
                    self.logger.info("Successfully reconfigured Openbox with default settings")
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to reconfigure Openbox: {e}")
        
        except Exception as e:
            overall_success = False
            self.logger.error(f"Unexpected error applying window decorations: {e}")
        
        # Set window button layout with fallback
        try:
            success, _ = self._apply_with_fallback(
                self.utils.run_lxqt_config_command, 'lxqt-qt5', 'button_layout', BUTTON_LAYOUT
            )
            if not success:
                overall_success = False
                self.logger.warning("Failed to set window button layout")
        except Exception as e:
            overall_success = False
            self.logger.error(f"Error setting window button layout: {e}")
        
        # Update Openbox configuration with fallback
        try:
            success, _ = self._apply_with_fallback(
                self.utils.update_openbox_theme, self.cur_theme
            )
            if not success:
                overall_success = False
                self.logger.warning("Failed to update Openbox theme")
        except Exception as e:
            overall_success = False
            self.logger.error(f"Error updating Openbox theme: {e}")
        
        # Final fallback: try to restart Openbox if things look really bad
        if not overall_success:
            self.logger.warning("Attempting to restart Openbox, last resort")
            try:
                subprocess.Popen(['openbox', '--reconfigure'], universal_newlines=True)
                time.sleep(1)  # Give it a moment to restart
            except Exception as e:
                self.logger.error(f"Failed to restart Openbox: {e}")
        
        return overall_success  # Return True if any part succeeded
    
    def apply_icons(self):
        """Apply icon theme in LXQt."
        
        Returns:
            bool: True if icon theme was applied successfully, False otherwise
        """
        self.logger.info("Applying LXQt icon theme")
        
        try:
            # Set icon theme
            self.utils.run_lxqt_config_command(
                'lxqt-qt5',
                'icon_theme',
                ICON_THEME
            )
            
            # Update PCManFM-Qt icon theme
            self.utils.update_pcmanfm_qt_theme(ICON_THEME)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply icon theme: {e}")
            return False
    
    def apply_cursor_theme(self):
        """Apply cursor theme in LXQt."
        
        Returns:
            bool: True if cursor theme was applied successfully, False otherwise
        """
        self.logger.info("Applying LXQt cursor theme")
        
        try:
            # Set cursor theme
            self.utils.run_lxqt_config_command(
                'lxqt-qt5', 'cursor_theme', CURSOR_THEME
            )
            
            # Update PCManFM-Qt cursor theme
            self.utils.update_pcmanfm_qt_theme(CURSOR_THEME)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply cursor theme: {e}")
            return False
    
    def apply_font_settings(self):
        """Apply font settings in LXQt."
        
        Returns:
            bool: True if font settings were applied successfully, False otherwise
        """
        self.logger.info("Applying LXQt font settings")
        
        try:
            # Set default font
            self.utils.run_lxqt_config_command(
                'lxqt-qt5',
                'font',
                FONT_DEFAULT
            )
            
            # Set fixed width font
            self.utils.run_lxqt_config_command(
                'lxqt-qt5',
                'fixed',
                FONT_DEFAULT
            )
            
            # Set window title font
            self.utils.run_lxqt_config_command(
                'lxqt-qt5',
                'window_title_font',
                FONT_BOLD
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply font settings: {e}")
            return False
