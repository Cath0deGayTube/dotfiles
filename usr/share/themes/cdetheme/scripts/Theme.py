#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import shutil
from os.path import expanduser

from PyQt5 import QtCore, QtGui, QtWidgets

import Globals
from MiscFun import *
from MotifColors import colorize_bg
from DesktopEnvironment import detect_desktop_environment, get_environment_module

class Theme():
    def __init__(self, opts):
        """Initialize the theme system."
        
        Args:
            opts: Options object containing theme settings
        """
        self.opts = opts
        
        # Detect the current desktop environment
        self.environment = detect_desktop_environment().name.lower()
        print(f"Detected desktop environment: {self.environment}")
        
        # Load the appropriate theme module
        self.theme = get_environment_module(self.environment)
        self.theme.opts = self.opts
        
        # For backward compatibility
        self.curXfTheme = 'cdetheme'
        self.screenHeight = '1024'  # Default, will be updated
    def initTheme(self):
        """Initialize the theme system."""
        print("Initializing theme system...")
        
        # Initialize the theme for the detected environment
        if not hasattr(self, 'theme') or not self.theme:
            print("No theme module loaded, falling back to default")
            from ThemeXfce import XfceTheme
            self.theme = XfceTheme(self.opts)
        
        # Initialize the theme
        success = self.theme.init_theme()
        if not success:
            print("Failed to initialize theme", file=sys.stderr)
            return False
            
        print(f"Theme initialized for {self.environment}")
        return True

    
    def updateThemeNow(self):
        """Update the theme immediately."""
        print("Updating theme now...")
        return self._update_theme_components()
        
    def updateTheme(self, delay=300):
        """Update the theme after a short delay."
        
        Args:
            delay: Delay in milliseconds before applying the update
        """
        print(f"Scheduling theme update in {delay}ms...")
        
        # If we have a pending update, stop it
        if hasattr(self, 'updatextimer') and self.updatextimer.isActive():
            self.updatextimer.stop()
            
        # Schedule the update
        self.updatextimer = QtCore.QTimer()
        self.updatextimer.setSingleShot(True)
        self.updatextimer.timeout.connect(self._update_theme_components)
        self.updatextimer.start(delay)
        
    def _update_theme_components(self):
        """Update all theme components."""
        print("Updating theme components...")
        
        if not hasattr(self, 'theme') or not self.theme:
            print("No theme module loaded, initializing...")
            if not self.initTheme():
                print("Failed to initialize theme", file=sys.stderr)
                return
        
        try:
            # Update the theme using the appropriate module
            success = self.theme.update_theme()
            
            # Apply all theme components
            if success:
                self.theme.apply_colors()
                self.theme.apply_window_decorations()
                self.theme.apply_icons()
                self.theme.apply_cursor_theme()
                self.theme.apply_font_settings()
                
                print("Theme update completed successfully")
                return True
            else:
                print("Theme update failed", file=sys.stderr)
                return False
                
        except Exception as e:
            print(f"Error updating theme: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return False



