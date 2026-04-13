2026-03-16

Changes:

- Old legacy (unused) files removed. 
- Calendar support: Clock and date panel buttons now launch a calendar app.
  Auto-detects the best available calendar via xdg-mime defaults, then falls
  back to known apps (Orage, GNOME Calendar, gsimplecal).
  Blocklist prevents non-calendar apps (LibreOffice, text editors, etc.) from
  being selected as the calendar handler.
  Optional: sudo apt install gsimplecal
- Backdrop tiling fix: Tile-based backdrops are now correctly tiled instead of
  scaled. Gradient backdrops are stretched. Uses XFCE image-style property.
- No pre-built `cdepanel` binary is included in this repository.
- Any `cdepanel` binary must be built by the user on that user's own system.
- startpanel: Falls back to Python source if binary fails (e.g. glibc mismatch
  on older distros like RHEL 9).
- startpanel: On x86_64, now also prefers Python source when files under
  scripts/ are newer than a locally built cdepanel binary. Set
  CDEPANEL_PREFER_SOURCE=1 to force source execution.
- Icon theme added (NsCDE)
- GTK theme fix: Color files (GTK2 gtkrc, GTK3/4 CSS) are now regenerated
  when changing palettes. Previously these calls were dead code.
- Installer rewritten (install.py v2.0) with correct paths and --uninstall.
- Workspace switch fix: Panel now keeps a stable application identity and is
  placed on all desktops in XFCE, preventing it from disappearing when a
  workspace button is clicked.
- First-run theming fix: Initial startup now applies the XFCE/GTK theme
  synchronously before the panel is interactive, so apps launched immediately
  from the panel inherit CDE styling.
- Calendar button fix: Clock/date buttons now upgrade legacy calendar targets
  like NOAPP, xfcalendar, and Orage to a working calendar desktop entry at
  runtime, preferring CDE/Motif Calendar (gsimplecal) when available.

Bug Fix Summary

**1. PyQt5 API Deprecations**
- Replaced deprecated widget classes, layout methods, event APIs, painter hints, and translate signatures across 15+ files

**2. Broken Syntax from Prior Automated Tools**
- Malformed `open()` calls, conflicting file modes, `'as'` instead of commas in lists, invalid `subprocess.Popen` args, `/n` instead of `\n`, broken multiline strings and regex patterns

**3. Pillow API Compatibility**
- `ImageQt` removal workaround with manual RGBA buffer conversion

**4. Platform & Import Fixes**
- `signal.SIGHUP` platform check for non-Unix, relative import corrections, missing imports

**5. Calendar Panel Buttons**
- Clock/date buttons now launch a calendar app with auto-detection (xdg-mime -> known apps -> gsimplecal fallback)
- Blocklist filters out non-calendar apps (LibreOffice, Thunderbird, text editors) that register for text/calendar MIME type

**6. Backdrop Tiling**
- Tile-based backdrops were being scaled instead of tiled; fixed by setting XFCE `image-style` property correctly via `xfconf-query`

**7. WSL2/VcXsrv Compatibility**
- Wayland environment variables (`WAYLAND_DISPLAY`, `XDG_SESSION_TYPE`) overridden to force X11 backend for XFCE components

**8. GTK Theme Generation**
- GTK2/3/4 color files were never regenerated on palette change (dead code after return statement). Fixed: ThemeXfce now generates cdecolors.rc (GTK2), cdecolors.css (GTK3 3.16/3.20, GTK4), updates pixmap images, and toggles cdetheme/cdetheme1 to force GTK reload.

**9. startpanel glibc Fallback**
- A `cdepanel` binary built on newer glibc (2.38) can fail on older distros (RHEL 9 has 2.34). startpanel now falls back to running Python source directly if a locally built binary fails.

**10. requirements.txt**
- Fixed colors.py version (was >=1.2.0 which doesn't exist, now >=0.2.0)

**11. Binary Build / Test Workflow**
- No pre-built binary is shipped with this project.
- If you want a `cdepanel` binary, you must build it yourself on the system where you intend to use it.
- Current Linux/Kubuntu x86_64 binary builds should use `cdepanel.spec`
- Recommended commands:
  `python3 -m pip install -r requirements.txt pyinstaller`
  `python3 -m PyInstaller cdepanel.spec`
  `cp dist/cdepanel ./cdepanel && chmod +x ./cdepanel`
- To test the compiled binary specifically, run `./cdepanel`
- `./startpanel` may run Python source instead if the source tree is newer than
  the binary


Icon Themes
-----------
This project bundles the NsCDE icon theme, a CDE-style freedesktop icon theme
from the NsCDE project (Not so Common Desktop Environment).

  Source:  https://github.com/NsCDE/NsCDE
  License: GPL-3.0
  Author:  NsCDE contributors

The NsCDE icon theme is installed automatically on first run.
Additional icon theme options (CDE-Reborn, SGI-Enhanced) are documented in:
  icon_themes/README.md


Installation
------------
Quick install:
  python3 install.py

Force overwrite existing:
  python3 install.py --force

Uninstall:
  python3 install.py --uninstall

The installer copies the theme to ~/.themes/cdetheme, creates the cdetheme1
symlink (needed for GTK theme reloading), installs config to ~/.config/CdePanel,
desktop entries to ~/.local/share/applications, and the NsCDE icon theme to
~/.local/share/icons/NsCDE.

Alternatively, manually place the folder in ~/.themes/ and run ./startpanel.
The panel will set up config files on first run.

Linux / Kubuntu x86_64 local binary rebuild:
  No pre-built binary is included. Build your own locally on the machine that
  will run it.
  sudo apt update
  sudo apt install python3 python3-pip python3-pyqt5 imagemagick x11-xserver-utils
  python3 -m pip install -r requirements.txt
  python3 -m pip install pyinstaller
  python3 -m PyInstaller cdepanel.spec
  cp dist/cdepanel ./cdepanel
  chmod +x ./cdepanel

To test the rebuilt binary itself, run:
  ./cdepanel

Note:
  ./startpanel may choose the Python source instead of the binary when files in
  scripts/ are newer than ./cdepanel.


Disabling the default XFCE panel:
  The CDE panel does not replace the default XFCE panel (xfce4-panel).
  If both panels appear at the bottom of the screen, disable the XFCE panel:
    xfce4-panel --quit
  To permanently prevent xfce4-panel from starting, create an empty panel config:
    mkdir -p ~/.config/xfce4/xfconf/xfce-perchannel-xml
    cat > ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml << 'EOF'
    <?xml version="1.0" encoding="UTF-8"?>
    <channel name="xfce4-panel" version="1.0">
      <property name="configver" type="int" value="2"/>
      <property name="panels" type="array"/>
    </channel>
    EOF



ARM Support (aarch64 / armv7l)
------------------------------
The startpanel script now detects the system architecture automatically.
- On x86_64: if you built `./cdepanel` locally, it can be used. If it fails
  (e.g. glibc mismatch), startpanel falls back to running the Python source
  directly.
- On ARM (aarch64, armv7l, etc.): the Python source (scripts/cdepanel.py) is
  executed directly with python3.

ARM additional requirements:
- Python 3 must be installed (python3)
- All Python dependencies from requirements.txt must be installed:
    pip3 install -r requirements.txt
- PyQt5 must be available for your ARM platform. On Debian/Ubuntu ARM:
    sudo apt install python3-pyqt5
- ImageMagick must be installed:
    sudo apt install imagemagick

Do not build a PyInstaller binary on ARM. It is pointless because it will not
run there. On ARM, use the Python source directly with the required
dependencies installed. The startpanel script already does this.


Termux + Termux:X11 on Android (ARM phones/tablets)
The CDE theme can run on Android devices via Termux with Termux:X11.
See TERMUX_FEASIBILITY_ANALYSIS.md for the full technical analysis.

Quick setup:
1. Install Termux from F-Droid (NOT Google Play)
2. Install Termux:X11 APK from https://github.com/termux/termux-x11/releases
3. In Termux, run:
    pkg update && pkg upgrade
    pkg install x11-repo
    pkg install xfce4 pyqt5 imagemagick xorg-xhost python python-pillow
    pip install pyxdg

    CRITICAL - PyQt5: ALWAYS use "pkg install pyqt5" (NOT "pip install PyQt5").
    There are no pip wheels for ARM/aarch64 on PyPI. If pip install is attempted,
    it will fail. If pip PyQt5 was previously installed and then uninstalled via
    pip, it can corrupt/remove files shared with the Termux pkg version. If this
    happens, run "pkg reinstall pyqt5" to restore the package.
    Confirmed working: PyQt5 5.15.11 via pkg on Python 3.13.12 (aarch64).

    NOTE: Pillow must be installed via pkg (not pip). There are no pip wheels
    for Android ARM, and building from source fails. The Termux package
    python-pillow provides a prebuilt binary.
4. Copy the cdetheme folder to your Termux home directory
5. Start Termux:X11 and XFCE:
    termux-x11 :1 -xstartup "dbus-launch --exit-with-session xfce4-session"
6. In a Termux terminal inside XFCE, cd to the cdetheme folder and run:
    ./startpanel

Known Termux limitations:
- Android 12+: You MUST disable the Phantom Process Killer or Termux will
  randomly crash. On Android 14+: Developer Options > Disable child process
  restrictions. On Android 12-13: requires ADB command from a PC.
- Black screen: If you see only a black screen with cursor, restart Termux:X11
  with: termux-x11 :1 -legacy-drawing -xstartup "xfce4-session"
- Wrong colors: If colors appear swapped, add -force-bgra flag.
- GTK3 theming: There is a known Termux bug where GTK3 apps may not respect
  theme changes. GTK2 apps and window decorations (xfwm4) work correctly.
  For full GTK3 support, use proot-distro with Debian instead of native Termux.
- DPI/scaling: Phone screens have very high DPI. Adjust via XFCE Settings >
  Appearance, or use the -dpi flag with termux-x11.





2025-09-06

NOTICE: I claim no ownership, authorship or make any other claim on this package. The original developer Jos van Riswick (http://www.josvanriswick.com/) retains all rights and credit for the project. It is based on the "CDE / Motif theme for Xfce / Gtk etc" package from "https://www.gnome-look.org/p/1231025/". The code was updated to support python 3.x and newer GTK by IDE AI assistants. I know NOTHING about programming python, GTK, XFCE, etc. I cannot provide any support or answer any questions about this version of the theme. If you have errors, problems or questions, do your own research. I can't help you!

This version was tested only one time on Red Hat Enterprise Linux 9.6 (Plow) with X11, Gnome and XFCE. I have done no other testing. As far as I know, it will not work with Wayland. 


Instructions
Place the cdetheme folder in your .themes folder, or run: python3 install.py
Then run ./startpanel from the theme directory.

Requirements:
- X11 (Wayland is not supported)
- XFCE desktop environment
- ImageMagick (sudo apt install imagemagick / sudo dnf install ImageMagick)
- Python 3 with PyQt5, Pillow, pyxdg, python-xlib, PyYAML, colors.py
  (pip install -r requirements.txt)

RHEL 9 / CentOS 9 note:
  sudo dnf install epel-release
  sudo dnf config-manager --set-enabled crb
  sudo dnf groupinstall "Xfce" "base-x"
  sudo dnf install python3 python3-pip python3-qt5 ImageMagick
  pip3 install -r requirements.txt



aec-junk@mail.com

