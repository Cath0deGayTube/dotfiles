#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Platform detection and path utilities for CDE Theme
# Provides Termux/Android and standard Linux compatibility
#

import os
import platform

def is_termux():
    """Detect if running inside Termux on Android."""
    return os.path.isdir('/data/data/com.termux')

def get_prefix():
    """Get the system prefix directory.
    On Termux: /data/data/com.termux/files/usr
    On standard Linux: /usr
    """
    return os.environ.get('PREFIX', '/usr')

def get_system_share():
    """Get the system share directory.
    On Termux: $PREFIX/share
    On standard Linux: /usr/share
    """
    return os.path.join(get_prefix(), 'share')

def get_icon_dirs():
    """Get list of system icon directories, platform-aware."""
    share = get_system_share()
    dirs = [
        os.path.join(share, 'icons', 'hicolor'),
        os.path.join(share, 'icons', 'NsCDE'),
        os.path.join(share, 'icons', 'elementary-xfce'),
        os.path.join(share, 'icons', 'gnome'),
        os.path.join(share, 'pixmaps'),
        os.path.expanduser('~/.local/share/icons'),
    ]
    if not is_termux():
        dirs.extend([
            '/usr/local/share/icons',
        ])
    return dirs

def get_icon_search_paths():
    """Get list of all icon search base directories."""
    share = get_system_share()
    paths = [
        os.path.join(share, 'icons'),
        os.path.expanduser('~/.local/share/icons'),
        os.path.join(share, 'pixmaps'),
    ]
    if not is_termux():
        paths.append('/usr/local/share/icons')
    return paths

def get_pixmaps_dir():
    """Get the system pixmaps directory."""
    return os.path.join(get_system_share(), 'pixmaps')

def get_applications_dirs():
    """Get list of .desktop application directories, platform-aware.
    Includes snap and flatpak directories when they exist."""
    share = get_system_share()
    dirs = [
        os.path.join(share, 'applications'),
        os.path.expanduser('~/.local/share/applications'),
        os.path.expanduser('~/.gnome/apps'),
        os.path.expanduser('~/.kde/share/apps'),
    ]
    if not is_termux():
        dirs.append('/usr/share/applications/kde4')
        # Snap .desktop files
        snap_dir = '/var/lib/snapd/desktop/applications'
        if os.path.isdir(snap_dir):
            dirs.append(snap_dir)
        # Flatpak .desktop files (system and user)
        flatpak_system = '/var/lib/flatpak/exports/share/applications'
        if os.path.isdir(flatpak_system):
            dirs.append(flatpak_system)
        flatpak_user = os.path.expanduser('~/.local/share/flatpak/exports/share/applications')
        if os.path.isdir(flatpak_user):
            dirs.append(flatpak_user)
    else:
        dirs.append(os.path.join(share, 'applications', 'kde4'))
    return tuple(dirs)

def get_default_icon_fallback():
    """Get a platform-aware default fallback icon path."""
    share = get_system_share()
    return os.path.join(share, 'icons', 'hicolor', '48x48', 'apps', 'utilities-terminal.png')

def get_arch():
    """Get the system architecture."""
    return platform.machine()

def is_arm():
    """Detect if running on ARM architecture."""
    arch = get_arch()
    return arch in ('aarch64', 'armv7l', 'armv6l', 'arm')
