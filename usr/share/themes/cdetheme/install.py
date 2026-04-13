#!/usr/bin/env python3
# CDE Panel Installation Script
#
# Installs the CDE/Motif theme panel to the user's home directory.
# Matches the runtime expectations of cdepanel.py:
#   - Theme directory:  ~/.themes/cdetheme  (with cdetheme1 symlink for GTK reload)
#   - Config directory: ~/.config/CdePanel
#   - Desktop entries:  ~/.local/share/applications/cdemotif-*.desktop
#   - Panel icons:      ~/.local/share/icons/hicolor/48x48/apps/
#   - NsCDE icon theme: ~/.local/share/icons/NsCDE/
#
# Usage:
#   python3 install.py              # install (prompts before overwriting)
#   python3 install.py --force      # install, overwrite existing files
#   python3 install.py --uninstall  # remove all installed files

import os
import sys
import shutil
import subprocess
import argparse
import platform

VERSION = "2.0.0"
ARCH = platform.machine()
IS_ARM = ARCH in ('aarch64', 'armv7l', 'armv6l', 'arm')
IS_TERMUX = os.path.isdir('/data/data/com.termux')


class Installer:
    def __init__(self, force=False):
        self.force = force
        self.src_dir = os.path.dirname(os.path.abspath(__file__))
        self.home = os.path.expanduser("~")

        # Paths that match cdepanel.py runtime expectations
        self.themedir = os.path.normpath(os.path.join(self.home, '.themes', 'cdetheme'))
        self.themelink = os.path.normpath(os.path.join(self.home, '.themes', 'cdetheme1'))
        self.configdir = os.path.normpath(os.path.join(self.home, '.config', 'CdePanel'))
        self.applicationsdir = os.path.normpath(os.path.join(self.home, '.local', 'share', 'applications'))
        self.hicolor_icons = os.path.normpath(os.path.join(self.home, '.local', 'share', 'icons', 'hicolor', '48x48', 'apps'))
        self.nscde_icons = os.path.normpath(os.path.join(self.home, '.local', 'share', 'icons', 'NsCDE'))

    def verify_source(self):
        """Verify required source files/directories exist"""
        required_dirs = [
            'scripts/CdePanel',
            'gtk-2.0',
            'gtk-3.16',
            'gtk-3.20',
            'gtk-4.0',
            'backdrops',
            'palettes',
            'img2',
            'xfwm4',
        ]
        required_files = [
            'startpanel',
            'index.theme',
            'scripts/cdepanel.py',
        ]
        missing = []
        for d in required_dirs:
            if not os.path.isdir(os.path.join(self.src_dir, d)):
                missing.append(f"Directory: {d}")
        for f in required_files:
            if not os.path.isfile(os.path.join(self.src_dir, f)):
                missing.append(f"File: {f}")
        if missing:
            print("Error: Missing required source files:")
            for m in missing:
                print(f"  - {m}")
            sys.exit(1)

    def _copy_tree(self, src, dst, label):
        """Copy a directory tree, respecting --force flag"""
        if not os.path.isdir(src):
            print(f"  Warning: source not found: {src}")
            return False
        if os.path.exists(dst) and not self.force:
            print(f"  Skipping {label} - already exists (use --force to overwrite)")
            return True
        if os.path.exists(dst):
            shutil.rmtree(dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copytree(src, dst, symlinks=True)
        print(f"  Installed {label} -> {dst}")
        return True

    def _copy_dir_contents(self, src, dst, label):
        """Copy contents of src into dst (merging with existing)"""
        if not os.path.isdir(src):
            print(f"  Warning: source not found: {src}")
            return False
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
            elif os.path.isdir(s):
                if os.path.exists(d) and self.force:
                    shutil.rmtree(d)
                if not os.path.exists(d):
                    shutil.copytree(s, d, symlinks=True)
        print(f"  Installed {label} -> {dst}")
        return True

    def install_theme_dir(self):
        """Install the full theme to ~/.themes/cdetheme"""
        # The panel expects the entire project tree at ~/.themes/cdetheme.
        # On first run, ThemeXfce.init_theme() copies cdethemedirsrc there.
        # We replicate that here so the panel is ready immediately.
        if os.path.exists(self.themedir) and not self.force:
            print(f"  Skipping theme dir - already exists (use --force to overwrite)")
        else:
            if os.path.exists(self.themedir):
                shutil.rmtree(self.themedir)
            os.makedirs(os.path.dirname(self.themedir), exist_ok=True)
            shutil.copytree(self.src_dir, self.themedir, symlinks=True,
                           ignore=shutil.ignore_patterns(
                               '.git', '.idea', '.venv', '__pycache__',
                               'legacy_files', 'legacy_readmes',
                               '*.pyc', 'install.py'
                           ))
            print(f"  Installed theme dir -> {self.themedir}")

    def install_theme_symlink(self):
        """Create cdetheme1 symlink for GTK theme toggle trick"""
        if os.path.lexists(self.themelink):
            os.remove(self.themelink)
        os.symlink(self.themedir, self.themelink)
        print(f"  Created symlink {self.themelink} -> {self.themedir}")

    def install_config(self):
        """Install config dir to ~/.config/CdePanel"""
        src = os.path.normpath(os.path.join(self.src_dir, 'scripts', 'CdePanel'))
        self._copy_tree(src, self.configdir, 'config')

    def install_desktop_files(self):
        """Install .desktop files to ~/.local/share/applications"""
        src = os.path.normpath(os.path.join(self.src_dir, 'scripts', 'CdePanel', 'applications'))
        self._copy_dir_contents(src, self.applicationsdir, 'desktop entries')

    def install_panel_icons(self):
        """Install panel icons to hicolor fallback theme"""
        src = os.path.normpath(os.path.join(self.src_dir, 'scripts', 'CdePanel', 'xpm'))
        self._copy_dir_contents(src, self.hicolor_icons, 'panel icons')

    def install_nscde_icons(self):
        """Install NsCDE icon theme to ~/.local/share/icons/NsCDE"""
        src = os.path.normpath(os.path.join(self.src_dir, 'icon_themes', 'NsCDE'))
        if not os.path.isdir(src):
            print("  Skipping NsCDE icon theme - not found in source")
            return
        self._copy_tree(src, self.nscde_icons, 'NsCDE icon theme')
        # Update icon cache if available
        gtk_update = shutil.which('gtk-update-icon-cache')
        if gtk_update:
            subprocess.run([gtk_update, '-f', '-t', self.nscde_icons],
                          capture_output=True, check=False)
            print("  Updated NsCDE icon cache")

    def install_startpanel(self):
        """Ensure startpanel is executable"""
        startpanel = os.path.join(self.themedir, 'startpanel')
        if os.path.isfile(startpanel):
            os.chmod(startpanel, 0o755)
            print(f"  startpanel is executable at {startpanel}")

    def verify(self):
        """Verify installation"""
        print("\nVerifying installation...")
        checks = [
            (self.themedir, 'Theme directory'),
            (os.path.join(self.themedir, 'gtk-2.0'), 'GTK2 theme'),
            (os.path.join(self.themedir, 'gtk-3.20'), 'GTK3 theme'),
            (os.path.join(self.themedir, 'gtk-4.0'), 'GTK4 theme'),
            (os.path.join(self.themedir, 'xfwm4'), 'XFWM4 decorations'),
            (os.path.join(self.themedir, 'backdrops'), 'Backdrops'),
            (os.path.join(self.themedir, 'palettes'), 'Palettes'),
            (os.path.join(self.themedir, 'img2'), 'GTK2 images'),
            (os.path.join(self.themedir, 'scripts', 'cdepanel.py'), 'Panel script'),
            (os.path.join(self.themedir, 'startpanel'), 'Start script'),
            (self.themelink, 'cdetheme1 symlink'),
            (self.configdir, 'Config directory'),
            (self.applicationsdir, 'Desktop entries dir'),
            (self.hicolor_icons, 'Panel icons dir'),
        ]
        ok = True
        for path, label in checks:
            if os.path.exists(path) or os.path.islink(path):
                print(f"  OK  {label}")
            else:
                print(f"  MISSING  {label} ({path})")
                ok = False
        # NsCDE is optional but report its status
        if os.path.isdir(self.nscde_icons):
            print(f"  OK  NsCDE icon theme")
        else:
            print(f"  --  NsCDE icon theme (not installed)")
        return ok

    def run(self):
        """Run the full installation"""
        print(f"CDE Panel Installer v{VERSION}")
        print("=" * 50)
        print(f"Source:  {self.src_dir}")
        print(f"Target:  {self.themedir}")
        print(f"Config:  {self.configdir}")
        print(f"Arch:    {ARCH} ({'ARM' if IS_ARM else 'x86_64'})")
        print(f"Termux:  {'Yes' if IS_TERMUX else 'No'}")
        print(f"Python:  {platform.python_version()}")
        print()

        if not self.force:
            response = input("Install CDE Panel? [Y/n] ").strip().lower()
            if response not in ('', 'y', 'yes'):
                print("Installation cancelled.")
                sys.exit(0)

        self.verify_source()

        print("\nInstalling...")
        self.install_theme_dir()
        self.install_theme_symlink()
        self.install_config()
        self.install_desktop_files()
        self.install_panel_icons()
        self.install_nscde_icons()
        self.install_startpanel()

        ok = self.verify()

        if ok:
            print("\nInstallation completed successfully!")
        else:
            print("\nInstallation completed with warnings.")

        print(f"\nTo start the panel:")
        print(f"  {os.path.join(self.themedir, 'startpanel')}")
        print(f"\nTo start on login, add that command to your desktop environment's autostart.")


def uninstall():
    """Remove all installed CDE Panel files"""
    home = os.path.expanduser("~")
    src_dir = os.path.dirname(os.path.abspath(__file__))
    targets = [
        ('~/.themes/cdetheme1', os.path.join(home, '.themes', 'cdetheme1'), 'symlink'),
        ('~/.themes/cdetheme',  os.path.join(home, '.themes', 'cdetheme'),  'dir'),
        ('~/.config/CdePanel',  os.path.join(home, '.config', 'CdePanel'),  'dir'),
        ('~/.local/share/icons/NsCDE', os.path.join(home, '.local', 'share', 'icons', 'NsCDE'), 'dir'),
        ('~/.config/gtk-4.0/gtk.css', os.path.join(home, '.config', 'gtk-4.0', 'gtk.css'), 'file'),
        ('~/.config/gtk-3.0/gtk.css', os.path.join(home, '.config', 'gtk-3.0', 'gtk.css'), 'file'),
    ]
    # Also remove cdemotif-*.desktop files
    appdir = os.path.join(home, '.local', 'share', 'applications')
    desktop_files = []
    if os.path.isdir(appdir):
        desktop_files = [os.path.join(appdir, f) for f in os.listdir(appdir)
                        if f.startswith('cdemotif-') and f.endswith('.desktop')]

    icon_src_dir = os.path.join(src_dir, 'scripts', 'CdePanel', 'xpm')
    icon_dst_dir = os.path.join(home, '.local', 'share', 'icons', 'hicolor', '48x48', 'apps')
    panel_icon_files = []
    if os.path.isdir(icon_src_dir) and os.path.isdir(icon_dst_dir):
        panel_icon_files = [
            os.path.join(icon_dst_dir, f)
            for f in os.listdir(icon_src_dir)
            if os.path.isfile(os.path.join(icon_src_dir, f))
            and os.path.isfile(os.path.join(icon_dst_dir, f))
        ]

    print("CDE Panel Uninstaller")
    print("=" * 50)
    print("The following will be removed:")
    for label, path, kind in targets:
        exists = os.path.lexists(path)
        print(f"  {'[exists]' if exists else '[not found]':14s} {label}")
    for f in desktop_files:
        print(f"  {'[exists]':14s} {os.path.basename(f)}")
    if not desktop_files:
        print(f"  {'[not found]':14s} cdemotif-*.desktop")
    for f in panel_icon_files:
        print(f"  {'[exists]':14s} {os.path.basename(f)}")
    if not panel_icon_files:
        print(f"  {'[not found]':14s} CDE panel icons in hicolor/48x48/apps")

    response = input("\nProceed with uninstall? [y/N] ").strip().lower()
    if response not in ('y', 'yes'):
        print("Uninstall cancelled.")
        sys.exit(0)

    for label, path, kind in targets:
        if kind == 'symlink' and os.path.islink(path):
            os.remove(path)
            print(f"  Removed symlink {label}")
        elif kind == 'dir' and os.path.isdir(path):
            shutil.rmtree(path)
            print(f"  Removed {label}")
        elif kind == 'file' and os.path.isfile(path):
            os.remove(path)
            print(f"  Removed {label}")
        elif os.path.lexists(path):
            os.remove(path)
            print(f"  Removed {label}")

    for f in desktop_files:
        os.remove(f)
        print(f"  Removed {os.path.basename(f)}")
    for f in panel_icon_files:
        os.remove(f)
        print(f"  Removed {os.path.basename(f)}")

    print("\nUninstall completed.")
    print("Note: pip-installed Python packages (PyQt5, Pillow, etc.) were not removed.")


def main():
    parser = argparse.ArgumentParser(
        description='CDE Panel Installer / Uninstaller',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 install.py              # Install for current user
  python3 install.py --force      # Overwrite existing installation
  python3 install.py --uninstall  # Remove all installed files
""")
    parser.add_argument('--force', action='store_true',
                       help='Overwrite existing files without prompting')
    parser.add_argument('--uninstall', action='store_true',
                       help='Remove all installed CDE Panel files')
    parser.add_argument('--version', action='version',
                       version=f'CDE Panel Installer v{VERSION}')
    args = parser.parse_args()

    if args.uninstall:
        uninstall()
    else:
        try:
            installer = Installer(force=args.force)
            installer.run()
        except KeyboardInterrupt:
            print("\nInstallation cancelled.")
            sys.exit(1)
        except Exception as e:
            print(f"\nError: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
