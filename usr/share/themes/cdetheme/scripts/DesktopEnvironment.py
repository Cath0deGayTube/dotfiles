#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Desktop Environment Detection and Integration

This module provides functionality to detect the current desktop environment
and load appropriate theming modules.
"""

import os
import subprocess
import logging
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DesktopEnvironment(Enum):
    """Supported desktop environments"""
    UNKNOWN = 0
    XFCE = 1
    LXQT = 2
    GNOME = 3


def detect_desktop_environment():
    """
    Detect the current desktop environment.
    
    Returns:
        DesktopEnvironment: The detected desktop environment
    """
    # Check environment variables first
    desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    session = os.environ.get('DESKTOP_SESSION', '').lower()
    
    # Check for XFCE
    if any(x in desktop for x in ['xfce', 'xfce4']) or 'xfce' in session:
        return DesktopEnvironment.XFCE
    
    # Check for LXQt
    if 'lxqt' in desktop or 'lxqt' in session:
        return DesktopEnvironment.LXQT
    
    # Check for GNOME (fallback for some DEs)
    if 'gnome' in desktop or 'gnome' in session:
        return DesktopEnvironment.GNOME
    
    # Fallback: Try to detect using process list
    try:
        processes = subprocess.check_output(['ps', '-e'], universal_newlines=True)
        
        if 'xfce4-session' in processes:
            return DesktopEnvironment.XFCE
        elif 'lxqt-session' in processes:
            return DesktopEnvironment.LXQT
        elif 'gnome-session' in processes:
            return DesktopEnvironment.GNOME
            
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.warning("Could not detect desktop environment from process list")
    
    return DesktopEnvironment.UNKNOWN


def get_environment_module(desktop_env):
    """
    Get the appropriate theming module for the detected desktop environment.
    
    Args:
        desktop_env: DesktopEnvironment enum or string name (e.g. 'xfce', 'lxqt')
        
    Returns:
        module: The appropriate theming module
    """
    # Normalize to string for comparison
    if isinstance(desktop_env, DesktopEnvironment):
        env_name = desktop_env.name.lower()
    else:
        env_name = str(desktop_env).lower()

    try:
        if env_name == 'xfce':
            from ThemeXfce import XfceTheme
            return XfceTheme()
        elif env_name == 'lxqt':
            from ThemeLxqt import LxqtTheme
            return LxqtTheme()
        else:
            # Fallback to XFCE theming for unsupported/unknown environments
            logger.info(f"Unknown environment '{env_name}', falling back to XFCE theming")
            from ThemeXfce import XfceTheme
            return XfceTheme()
            
    except ImportError as e:
        logger.error(f"Failed to load theming module: {e}")
        # Last resort fallback to XFCE theming
        from ThemeXfce import XfceTheme
        return XfceTheme()


def init_environment():
    """
    Initialize the appropriate theming for the current desktop environment.
    
    Returns:
        tuple: (detected_environment, theme_module)
    """
    # Detect desktop environment
    env = detect_desktop_environment()
    logger.info(f"Detected desktop environment: {env.name}")
    
    # Load appropriate theming module
    theme = get_environment_module(env)
    
    return env, theme


if __name__ == "__main__":
    # Test the detection
    env = detect_desktop_environment()
    print(f"Detected environment: {env.name}")
