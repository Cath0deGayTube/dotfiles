#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Base Theme Class

This module provides a base class for all desktop environment themes.
"""

import os
import logging
import subprocess
from abc import ABC, abstractmethod

class BaseTheme(ABC):
    """Base class for all desktop environment themes"""
    
    def __init__(self, opts=None):
        """
        Initialize the theme.
        
        Args:
            opts: Options object containing theme settings
        """
        self.opts = opts
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialized = False
    
    @abstractmethod
    def init_theme(self):
        """Initialize the theme"""
        pass
    
    @abstractmethod
    def update_theme(self):
        """Update the theme with current settings"""
        pass
    
    @abstractmethod
    def apply_colors(self):
        """Apply color scheme to the desktop environment"""
        pass
    
    @abstractmethod
    def apply_window_decorations(self):
        """Apply window decorations and borders"""
        pass
    
    @abstractmethod
    def apply_icons(self):
        """Apply icon theme"""
        pass
    
    @abstractmethod
    def apply_cursor_theme(self):
        """Apply cursor theme"""
        pass
    
    @abstractmethod
    def apply_font_settings(self):
        """Apply font settings"""
        pass
    
    def ensure_directory(self, path):
        """
        Ensure a directory exists, create it if it doesn't.'
        
        Args:
            path: Path to the directory
            
        Returns:
            bool: True if directory exists or was created, False otherwise
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except OSError as e:
            self.logger.error(f"Failed to create directory {path}: {e}")
            return False
    
    def run_command(self, cmd, cwd=None):
        """
        Run a shell command.
        
        Args:
            cmd: Command to run (string or list of strings)
            cwd: Working directory for the command
            
        Returns:
            tuple: (success, output)
        """
        try:
            result = subprocess.run(
                cmd, cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            , universal_newlines=True)
            
            if result.returncode != 0:
                self.logger.error(
                    f"Command failed with code {result.returncode}: {cmd}\n"
                    f"STDOUT: {result.stdout}\n"
                    f"STDERR: {result.stderr}"
                )
                return False, result.stderr
                
            return True, result.stdout
            
        except Exception as e:
            self.logger.error(f"Error running command {cmd}: {e}")
            return False, str(e)
    
    def is_installed(self, program):
        """
        Check if a program is installed and in PATH.
        
        Args:
            program: Name of the program to check
            
        Returns:
            bool: True if the program is installed, False otherwise
        """
        try:
            subprocess.run(
                ['which', program],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            , universal_newlines=True)
            return True
        except subprocess.CalledProcessError:
            return False
        except Exception as e:
            self.logger.warning(f"Error checking for program {program}: {e}")
            return False
