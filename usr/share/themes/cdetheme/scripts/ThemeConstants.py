#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON 3 COMPATIBILITY
"""
Theme Constants

This module defines constants used across all theme implementations.
"""

# Theme names
THEME_BASE_NAME = 'cdetheme'
THEME_XFCE = f"{THEME_BASE_NAME}-xfce"
THEME_LXQT = f"{THEME_BASE_NAME}-lxqt"
THEME_GTK = f"{THEME_BASE_NAME}-gtk"

# Color definitions - DO NOT MODIFY THESE VALUES
COLOR_ACTIVE_TITLE_BG = "#4e5d89"
COLOR_ACTIVE_TITLE_TEXT = "#ffffff"
COLOR_INACTIVE_TITLE_BG = "#a0a0a0"
COLOR_INACTIVE_TITLE_TEXT = "#000000"
COLOR_BORDER = "#4e5d89"
COLOR_MENU_BG = "#dcdcdc"
COLOR_MENU_TEXT = "#000000"
COLOR_MENU_ACTIVE_BG = "#4e5d89"
COLOR_MENU_ACTIVE_TEXT = "#ffffff"
COLOR_TOOLTIP_BG = "#4e5d89"
COLOR_TOOLTIP_TEXT = "#ffffff"

# Font settings
FONT_DEFAULT = "Sans 10"
FONT_BOLD = "Sans Bold 10"
FONT_WINDOW_TITLE = FONT_BOLD

# Window manager button layout
BUTTON_LAYOUT = "menu:minimize,maximize,close"

# Icon and cursor themes
ICON_THEME = "NsCDE"
CURSOR_THEME = "cde"
