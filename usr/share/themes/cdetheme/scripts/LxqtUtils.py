#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
LXQt Utilities

This module provides utility functions for LXQt desktop environment theming.
"""

import os
import subprocess
import logging
import shutil
import configparser
from pathlib import Path

logger = logging.getLogger('LxqtUtils')

def run_lxqt_config_command(module, key, value):
    """Run an LXQt configuration command to set a value."
    
    Args:
        module: The configuration module (e.g., 'lxqt-qt5')
        key: The key to set (e.g., 'icon_theme')
        value: The value to set
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        subprocess.run(
            ['lxqt-config-qt5', '--config-module', module, '--set', key, value],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        , universal_newlines=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"LXQt config command failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Error running LXQt config command: {e}")
        return False

def get_lxqt_version():
    """Get the installed LXQt version."
    
    Returns:
        tuple: (major, minor) version numbers or (0, 0) if not found
    """
    try:
        result = subprocess.run(
            ['lxqt-about', '--version'],
            capture_output=True,
            text=True
        , universal_newlines=True)
        if result.returncode == 0:
            # Example output: "lxqt-about 0.17.0"
            version_str = result.stdout.strip().split()[-1]
            return tuple(map(int, version_str.split('.')[:2]))
    except (subprocess.SubprocessError, ValueError, IndexError) as e:
        logger.warning(f"Could not determine LXQt version: {e}")
    
    return (0, 0)

def get_theme_directories():
    """Get the standard LXQt theme directories."
    
    Returns:
        dict: Dictionary of theme directory paths
    """
    home = str(Path.home())
    
    return {
        'themes': os.path.normpath(os.path.join(home, '.themes')),
        'icons': os.path.normpath(os.path.join(home, '.icons')),
        'local_share': os.path.normpath(os.path.join(home, '.local', 'share')),
        'lxqt': os.path.normpath(os.path.join(home, '.config', 'lxqt')),
        'openbox': os.path.normpath(os.path.join(home, '.config', 'openbox')),
        'backgrounds': os.path.normpath(os.path.join(home, '.local', 'share', 'backgrounds'))
    }

def is_lxqt_running():
    """Check if LXQt desktop is currently running."
    
    Returns:
        bool: True if LXQt is running, False otherwise
    """
    try:
        result = subprocess.run(
            ['pgrep', '-x', 'lxqt-session'],
            capture_output=True,
            text=True
        , universal_newlines=True)
        return result.returncode == 0
    except subprocess.SubprocessError:
        return False

def reload_lxqt():
    """Reload LXQt to apply theme changes."""
    try:
        # Try to restart the panel
        subprocess.run(['killall', 'lxqt-panel'], check=False, universal_newlines=True)
        subprocess.Popen(['lxqt-panel'], universal_newlines=True)
        
        # Restart Openbox
        subprocess.run(['openbox', '--reconfigure'], check=True, universal_newlines=True)
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reload LXQt: {e}")
        return False

def set_lxqt_theme(theme_name):
    """Set the LXQt desktop theme."
    
    Args:
        theme_name: Name of the theme to apply
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Set GTK theme
        run_lxqt_config_command(
            'lxqt-qt5',
            'theme',
            theme_name
        )
        
        # Set icon theme
        run_lxqt_config_command(
            'lxqt-qt5',
            'icon_theme',
            'cde'
        )
        
        # Set cursor theme
        run_lxqt_config_command(
            'lxqt-qt5',
            'cursor_theme',
            'cde'
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to set LXQt theme: {e}")
        return False

def get_current_lxqt_theme():
    """Get the current LXQt theme name."
    
    Returns:
        str: The current theme name or empty string if not found
    """
    try:
        result = subprocess.run(
            ['lxqt-config-qt5', '--config-module', 'lxqt-qt5', '--get', 'theme'],
            capture_output=True,
            text=True,
            check=True
        , universal_newlines=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get current LXQt theme: {e}")
        return ""

def update_openbox_theme(theme_name):
    """Update the Openbox theme for LXQt."
    
    Args:
        theme_name: Name of the Openbox theme to apply
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create Openbox config directory if it doesn't exist'
        openbox_dir = os.path.normpath(os.path.join(str(Path.home())), '.config', 'openbox')
        os.makedirs(openbox_dir, exist_ok=True)
        
        # Path to Openbox autostart file
        autostart_file = os.path.normpath(os.path.join(openbox_dir, 'autostart'))
        
        # Add or update theme setting in autostart
        theme_line = f'openbox --reconfigure &'
        
        # Read existing autostart file if it exists
        lines = []
        if os.path.exists(autostart_file):
            with open(autostart_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # Remove any existing theme lines
        lines = [line for line in lines if 'openbox --reconfigure' not in line]
        
        # Add the theme line
        lines.append(theme_line + '\n')
        
        # Write the updated autostart file
        with open(autostart_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Set the Openbox theme
        run_lxqt_config_command(
            'lxqt-qt5',
            'theme',
            theme_name
        )
        
        # Reconfigure Openbox
        subprocess.run(['openbox', '--reconfigure'], check=True, universal_newlines=True)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to update Openbox theme: {e}")
        return False

def update_pcmanfm_qt_theme(theme_name):
    """Update the PCManFM-Qt file manager theme."
    
    Args:
        theme_name: Name of the theme to apply
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Path to PCManFM-Qt settings file
        pcmanfm_qt_dir = os.path.normpath(os.path.join(str(Path.home()), '.config', 'pcmanfm-qt'))
        os.makedirs(pcmanfm_qt_dir, exist_ok=True)
        
        settings_file = os.path.normpath(os.path.join(pcmanfm_qt_dir, 'settings'))
        
        # Create or update settings file
        config = configparser.ConfigParser()
        
        if os.path.exists(settings_file):
            config.read(settings_file)
        
        # Update or add settings
        if 'System' not in config:
            config['System'] = {}
        
        config['System']['Theme'] = theme_name
        config['System']['IconTheme'] = 'NsCDE'
        
        # Write the updated settings
        with open(settings_file, 'w', encoding='utf-8') as f:
            config.write(f)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to update PCManFM-Qt theme: {e}")
        return False
