#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
XFCE Theme Module

This module provides XFCE-specific theming functionality.
"""

import os
import shutil
import subprocess
from BaseTheme import BaseTheme
import XfceDecor
import ThemeBackdrops
import ThemeGtk
import Globals
from MiscFun import *

class XfceTheme(BaseTheme):
    """XFCE-specific theming implementation"""
    
    def __init__(self, opts=None):
        """Initialize the XFCE theme"""
        super().__init__(opts)
        self.environment = 'xfce'
        self.cur_theme = 'cdetheme'
        self.screen_height = '1024'  # Default, will be updated
    
    def init_theme(self):
        """Initialize the XFCE theme"""
        self.logger.info("Initializing XFCE theme")
        
        # Create necessary directories
        user_home = os.path.expanduser("~")
        home_dot_themes = os.path.normpath(os.path.join(user_home, '.themes'))
        
        if not os.path.exists(home_dot_themes):
            self.logger.info(f"Creating directory: {home_dot_themes}")
            try:
                os.makedirs(home_dot_themes)
            except OSError as e:
                self.logger.error(f"Failed to create {home_dot_themes}: {e}")
                return False
        
        # Copy theme files if they don't exist'
        if os.path.exists(home_dot_themes):
            if not os.path.exists(Globals.themedir):
                self.logger.info(f"Copying theme files to {Globals.themedir}")
                try:
                    shutil.copytree(Globals.cdethemedirsrc, Globals.themedir, symlinks=True)
                except Exception as e:
                    self.logger.error(f"Failed to copy theme files: {e}")
                    return False
            
            # Create a symlink for the theme
            theme_link = os.path.normpath(os.path.join(home_dot_themes, 'cdetheme1'))
            if os.path.lexists(theme_link):
                os.remove(theme_link)
            os.symlink(Globals.themedir, theme_link)
        
        self.initialized = True
        return True
    
    def update_theme(self):
        """Update the XFCE theme with current settings"""
        if not self.initialized and not self.init_theme():
            return False
        
        self.logger.info("Updating XFCE theme")
        
        # Update backdrops if enabled
        if self.opts.themeBackdrops == 'xfce':
            self.logger.info("Updating XFCE backdrops")
            ThemeBackdrops.prepareBackDrops(self.opts)
            
            # Apply backdrop to current workspace
            current_workspace = 1  # Default to workspace 1 if we can't determine the current one'
            try:
                # Try to get current workspace number
                from WorkspaceFuncs import getCurrentWorkspace
                current_workspace = getCurrentWorkspace()
            except:
                pass
                
            try:
                # Set backdrop for the current workspace with correct image style
                backdropsrc=self.opts.workspacebackdrops[current_workspace]
                style=ThemeBackdrops.imageStyleForBackdrop(backdropsrc)
                ThemeBackdrops.setXfBackdrop(current_workspace,style)
                self.logger.info(f"Applied backdrop to workspace {current_workspace} (style={style})")
            except Exception as e:
                self.logger.error(f"Failed to apply backdrop to workspace {current_workspace}: {e}")
        
        # Update window decorations if enabled
        if self.opts.themeWindecs == 'xfce':
            self.logger.info("Updating XFCE window decorations")
            self._update_window_decorations()
        
        # Apply GTK theme if enabled
        if self.opts.themeGtk:
            self.logger.info("Updating GTK theme")
            self._update_gtk_theme()
        
        return True
    
    def apply_colors(self):
        """Apply color scheme to XFCE"""
        self.logger.info("Applying XFCE color scheme")
        # This is handled by the GTK theme in XFCE
        return True
    
    def apply_window_decorations(self):
        """Apply window decorations in XFCE"""
        self.logger.info("Applying XFCE window decorations")
        return self._update_window_decorations()
    
    def apply_icons(self):
        """Apply icon theme in XFCE"""
        self.logger.info("Applying XFCE icon theme")
        # Try NsCDE first (bundled CDE-style icon theme), then fall back to CDE-Reborn if user installed it
        icon_dirs = [
            os.path.normpath(os.path.join(os.path.expanduser("~"), '.local/share/icons')),
            os.path.normpath(os.path.join(os.path.expanduser("~"), '.icons')),
            '/usr/share/icons'
        ]
        theme_name = None
        for candidate in ['NsCDE', 'CDE-Reborn']:
            for d in icon_dirs:
                if os.path.isdir(os.path.join(d, candidate)):
                    theme_name = candidate
                    break
            if theme_name:
                break
        if not theme_name:
            self.logger.warning("No CDE-style icon theme found. Install NsCDE or CDE-Reborn.")
            return False
        self.logger.info(f"Using icon theme: {theme_name}")
        cmd = [
            'xfconf-query', '-c', 'xsettings', '-p', '/Net/IconThemeName',
            '-s', theme_name
        ]
        success, _ = self.run_command(cmd)
        return success
    
    def apply_cursor_theme(self):
        """Apply cursor theme in XFCE"""
        self.logger.info("Applying XFCE cursor theme")
        # Set the cursor theme using xfconf-query
        cmd = [
            'xfconf-query', '-c', 'xsettings',
            '-p', '/Gtk/CursorThemeName',
            '-s', 'cde'
        ]
        success, _ = self.run_command(cmd)
        return success
    
    def apply_font_settings(self):
        """Apply font settings in XFCE"""
        self.logger.info("Applying XFCE font settings")
        # Set the default font
        cmd = [
            'xfconf-query', '-c', 'xsettings',
            '-p', '/Gtk/FontName',
            '-s', 'Sans 10'
        ]
        success, _ = self.run_command(cmd)
        return success
    
    def _update_window_decorations(self):
        """Update XFWM4 window decorations"""
        try:
            # Generate the themerc file
            filename = os.path.normpath(os.path.join(Globals.themedir, 'xfwm4/themerc'))
            XfceDecor.genXfwmThemerc(filename, self.opts)
            
            # Generate the decorations
            dirname = os.path.normpath(os.path.join(Globals.themedir, 'xfwm4'))
            XfceDecor.genXfceDecor(dirname, self.opts)
            XfceDecor.init(self.opts)
            
            # xfwm4 automatically picks up decoration changes via xfconf-query
            # DO NOT use 'xfwm4 --replace' as it kills window management state
            # and causes frameless windows (like the CDE panel) to vanish
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update window decorations: {e}")
            return False
    
    def _update_gtk_theme(self):
        """Update GTK theme settings: regenerate color files, update images, toggle theme to force reload"""
        try:
            # Generate GTK2 color definitions (cdecolors.rc)
            gtk2colorsfile = os.path.normpath(os.path.join(Globals.themedir, 'gtk-2.0', 'cdecolors.rc'))
            if os.path.isdir(os.path.dirname(gtk2colorsfile)):
                ThemeGtk.gengtk2colors(gtk2colorsfile, self.opts)
            
            # Generate GTK3 color definitions (cdecolors.css) for both 3.16 and 3.20
            for gtkver in ['gtk-3.16', 'gtk-3.20']:
                gtk3colorsfile = os.path.normpath(os.path.join(Globals.themedir, gtkver, 'cdecolors.css'))
                if os.path.isdir(os.path.dirname(gtk3colorsfile)):
                    ThemeGtk.gengtk3colors(gtk3colorsfile, self.opts)
            
            # Generate GTK4 color definitions (cdecolors.css)
            gtk4colorsfile = os.path.normpath(os.path.join(Globals.themedir, 'gtk-4.0', 'cdecolors.css'))
            if os.path.isdir(os.path.dirname(gtk4colorsfile)):
                ThemeGtk.gengtk4css(gtk4colorsfile, self.opts)
            
            # Update GTK2 pixmap-engine images with current palette colors
            ThemeGtk.updateThemeImages(self.opts)
            
            # Write user-level GTK3/GTK4 CSS overrides for libadwaita and GNOME apps.
            # These apps ignore ~/.themes/ and only read ~/.config/gtk-{3.0,4.0}/gtk.css
            self._write_user_gtk_overrides()
            
            # Toggle theme name between cdetheme and cdetheme1 to force GTK to reload
            if self.cur_theme == 'cdetheme':
                self.cur_theme = 'cdetheme1'
            else:
                self.cur_theme = 'cdetheme'
            
            # Set the GTK theme (toggled name forces reload)
            cmd = [
                'xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName',
                '-s', self.cur_theme
            ]
            success, _ = self.run_command(cmd)
            
            # Also toggle xfwm4 theme if window decorations are enabled
            # (cdetheme and cdetheme1 are symlinks to the same dir)
            if self.opts.themeWindecs == 'xfce':
                cmd = [
                    'xfconf-query', '-c', 'xfwm4', '-p', '/general/theme',
                    '-s', self.cur_theme
                ]
                self.run_command(cmd)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update GTK theme: {e}")
            return False
    
    def _write_user_gtk_overrides(self):
        """Write user-level GTK3/GTK4 CSS so libadwaita and GNOME apps pick up CDE colors.
        
        libadwaita apps (GNOME Software, Settings, etc.) ignore /Net/ThemeName and
        ~/.themes/ entirely.  The only way to inject colors is via the user CSS at
        ~/.config/gtk-4.0/gtk.css.  Same for GNOME GTK3 apps via ~/.config/gtk-3.0/gtk.css.
        """
        user_home = os.path.expanduser("~")
        colors = Globals.colorshash
        
        # Build color definitions from current palette
        color_defs = ''
        for a in range(1, 9):
            s = str(a)
            color_defs += '@define-color bg_color_' + s + ' ' + colors['bg_color_' + s] + ';\n'
            color_defs += '@define-color fg_color_' + s + ' ' + colors['fg_color_' + s] + ';\n'
            color_defs += '@define-color ts_color_' + s + ' ' + colors['ts_color_' + s] + ';\n'
            color_defs += '@define-color bs_color_' + s + ' ' + colors['bs_color_' + s] + ';\n'
            color_defs += '@define-color sel_color_' + s + ' ' + colors['sel_color_' + s] + ';\n'
        
        # Map CDE palette colors to the named colors that libadwaita/GTK actually use.
        # Color slot 5 = general bg, slot 4 = text fields, slot 6 = menus, slot 1 = accent/highlight
        libadwaita_overrides = """
/* CDE/Motif color overrides — generated by cdepanel, edits will be overwritten */
{color_defs}
@define-color window_bg_color {bg5};
@define-color window_fg_color {fg5};
@define-color view_bg_color {bg4};
@define-color view_fg_color {fg4};
@define-color headerbar_bg_color {bg6};
@define-color headerbar_fg_color {fg6};
@define-color headerbar_backdrop_color {sel6};
@define-color card_bg_color {bg5};
@define-color card_fg_color {fg5};
@define-color dialog_bg_color {bg6};
@define-color dialog_fg_color {fg6};
@define-color popover_bg_color {bg6};
@define-color popover_fg_color {fg6};
@define-color sidebar_bg_color {sel5};
@define-color sidebar_fg_color {fg5};
@define-color sidebar_backdrop_color {sel5};
@define-color accent_bg_color {bg1};
@define-color accent_fg_color {fg1};
@define-color accent_color {bg1};
@define-color destructive_bg_color {bg8};
@define-color destructive_fg_color {fg8};
@define-color success_color {bg4};
@define-color warning_color {bg1};
@define-color error_color {bg8};
""".format(
            color_defs=color_defs,
            bg5=colors['bg_color_5'], fg5=colors['fg_color_5'],
            bg4=colors['bg_color_4'], fg4=colors['fg_color_4'],
            bg6=colors['bg_color_6'], fg6=colors['fg_color_6'],
            sel5=colors['sel_color_5'], sel6=colors['sel_color_6'],
            bg1=colors['bg_color_1'], fg1=colors['fg_color_1'],
            bg8=colors['bg_color_8'], fg8=colors['fg_color_8'],
        )
        
        # Write GTK4 user override (affects libadwaita apps)
        gtk4_config = os.path.normpath(os.path.join(user_home, '.config', 'gtk-4.0'))
        os.makedirs(gtk4_config, exist_ok=True)
        gtk4_css = os.path.join(gtk4_config, 'gtk.css')
        try:
            with open(gtk4_css, 'w', encoding='utf-8') as f:
                f.write(libadwaita_overrides)
            self.logger.info(f"Wrote user GTK4 CSS: {gtk4_css}")
        except OSError as e:
            self.logger.error(f"Failed to write {gtk4_css}: {e}")
        
        # Write GTK3 user override (affects GNOME GTK3 apps that ignore xsettings)
        gtk3_config = os.path.normpath(os.path.join(user_home, '.config', 'gtk-3.0'))
        os.makedirs(gtk3_config, exist_ok=True)
        gtk3_css = os.path.join(gtk3_config, 'gtk.css')
        try:
            with open(gtk3_css, 'w', encoding='utf-8') as f:
                f.write(libadwaita_overrides)
            self.logger.info(f"Wrote user GTK3 CSS: {gtk3_css}")
        except OSError as e:
            self.logger.error(f"Failed to write {gtk3_css}: {e}")
