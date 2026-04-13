# CDE Theme on Termux + Termux:X11 — Feasibility Analysis

**Date:** March 2026  
**Scope:** Running CDE/Motif Theme 1.4 on ARM-based Android phones via Termux + Termux:X11  

---

## 1. Executive Summary

**Verdict: Feasible with in-tree support — a fork is NOT necessary.**

The CDE theme can run on Termux + Termux:X11 with targeted modifications. All critical
dependencies (Python 3, PyQt5, ImageMagick, XFCE4, Pillow, xhost) are available as
Termux packages. The main obstacles are **filesystem path differences** and
**hardcoded system paths** in the codebase. These can be addressed with a Termux
compatibility layer (detection + path remapping) without breaking existing Linux support.

However, there are significant caveats, known bugs, and UX limitations that users
must be aware of.

---

## 2. Termux + Termux:X11 Ecosystem Overview

### 2.1 What is Termux?
Termux is a terminal emulator and Linux environment for Android (no root required).
It provides its own package manager (`pkg`/`apt`) with ~2000+ packages compiled for
Android's Bionic libc. It runs natively on the device — not in a VM or emulator.

- **Latest version:** 0.119.x (F-Droid, 2025)
- **Requires:** Android 8+
- **Architecture:** aarch64 (ARM64) on most modern phones, armv7l on older devices

### 2.2 What is Termux:X11?
Termux:X11 is a fully-fledged X11 server built with Android NDK. It replaces VNC-based
approaches with a native X server that renders directly to an Android Activity.

- Installed via: `pkg install x11-repo && pkg install termux-x11-nightly`
- Recommended DE: XFCE4 (`pkg install xfce4`)
- Launch: `termux-x11 :1 -xstartup "dbus-launch --exit-with-session xfce4-session"`

### 2.3 Two Approaches: Native vs proot-distro
| Aspect | Native Termux | proot-distro (Debian/Ubuntu) |
|--------|--------------|------------------------------|
| Performance | Best (no overhead) | ~5-10% overhead from proot |
| Package availability | Termux repos only | Full distro repos |
| Filesystem | Non-standard (`$PREFIX`) | Standard Linux layout |
| GTK3 theming | **BUGGY** (known issue #27569) | Works correctly |
| PyQt5 | Available (`pkg install pyqt5`) | Available (`apt install python3-pyqt5`) |
| Complexity | Lower | Higher (container setup) |

**Recommendation:** Support BOTH approaches. Native Termux for simplicity,
proot-distro for full compatibility (especially GTK3 theming).

---

## 3. Dependency Availability on Termux

### 3.1 All Critical Dependencies: AVAILABLE

| Dependency | Termux Package | Status |
|-----------|---------------|--------|
| Python 3 | `python` | ✅ Available (3.12+) |
| PyQt5 | `pyqt5` (from x11-repo) | ✅ Available (5.15.x) |
| Pillow/PIL | `pip install pillow` | ✅ Available (requires build deps) |
| ImageMagick (`convert`) | `imagemagick` | ✅ Available |
| XFCE4 | `xfce4` (from x11-repo) | ✅ Available |
| xhost | `xorg-xhost` (from x11-repo) | ✅ Available |
| xfconf-query | Part of `xfce4` package | ✅ Available |
| dbus | `dbus` | ✅ Available |
| pyxdg | `pip install pyxdg` | ✅ Available (pure Python) |
| configparser | stdlib | ✅ Built-in |
| gtk-launch | Part of `glib` package | ⚠️ Needs verification |

### 3.2 Pillow Installation on Termux
**Do NOT use `pip install pillow`** — there are no pip wheels for Android ARM,
and building from source fails. Termux provides a prebuilt binary package:
```bash
pkg install python-pillow
```
This is the only reliable way to install Pillow on Termux.

---

## 4. Critical Compatibility Issues

### 4.1 FILESYSTEM PATHS (HIGH IMPACT)

This is the **#1 blocker**. Termux uses a non-standard filesystem layout:

| Standard Linux | Termux Native |
|---------------|--------------|
| `/usr/share` | `$PREFIX/share` (`/data/data/com.termux/files/usr/share`) |
| `/usr/lib` | `$PREFIX/lib` |
| `/usr/bin` | `$PREFIX/bin` |
| `/etc` | `$PREFIX/etc` |
| `~` (home) | `/data/data/com.termux/files/home` |
| `~/.themes` | `/data/data/com.termux/files/home/.themes` |
| `~/.config` | `/data/data/com.termux/files/home/.config` |
| `/usr/share/icons` | `$PREFIX/share/icons` |
| `/usr/share/applications` | `$PREFIX/share/applications` |
| `/usr/share/pixmaps` | `$PREFIX/share/pixmaps` |
| `/tmp` | `$PREFIX/tmp` |

**Good news:** `os.path.expanduser("~")` correctly returns `/data/data/com.termux/files/home`
in Termux. So all `~/.themes`, `~/.config/CdePanel`, etc. paths resolve correctly.

**Bad news:** The codebase has **many hardcoded `/usr/share/...` paths** that will fail:

- `ColorFun.py` lines 412, 461, 475, 481, 557-561: Hardcoded `/usr/share/icons/...`,
  `/usr/share/pixmaps`
- `GenDefaultDrawersAndLayout.py` lines 144-145: Hardcoded `/usr/share/applications`,
  `/usr/share` for pixmaps
- Icon search paths throughout `ColorFun.py` use `find /usr/share/icons/...`

**Fix approach:** Detect Termux and prepend `$PREFIX` to system paths. A helper function:
```python
def get_system_share_dir():
    prefix = os.environ.get('PREFIX', '/usr')
    return os.path.join(prefix, 'share')
```

### 4.2 GTK3 THEMING BUG (MEDIUM IMPACT)

There is a **confirmed, open bug** (termux-packages#27569) where GTK3 applications in
native Termux XFCE do not respect theme changes made via `xfce4-appearance-settings`.
GTK2 apps and xfwm4 DO work. This means:

- The CDE GTK2 theme (`gtk-2.0/`) will apply to GTK2 apps ✅
- The CDE GTK3 themes (`gtk-3.16/`, `gtk-3.20/`) may NOT apply to GTK3 apps ❌
- The CDE xfwm4 window decorations will work ✅

**Workaround:** This bug does not exist in proot-distro environments (Debian/Ubuntu).
Users who need full GTK3 theming should use proot-distro.

### 4.3 DISPLAY ENVIRONMENT (MEDIUM IMPACT)

The `DISPLAY` environment variable must be set for PyQt5/X11 to work:
```bash
export DISPLAY=:1
```

Termux:X11 handles this, but `startpanel` should verify it's set.

Known Termux:X11 display quirks:
- **Black screen:** Some devices need `-legacy-drawing` flag
- **Swapped colors (R/B channels):** Some devices need `-force-bgra` flag
- **DPI/scaling:** Phone screens have very high DPI; the CDE panel may appear
  tiny or huge. Users need to adjust with `-dpi` flag or XFCE settings.

### 4.4 ANDROID PHANTOM PROCESS KILLER (MEDIUM IMPACT)

Android 12+ has a "Phantom Process Killer" that kills background processes exceeding
a 32-process limit (across ALL apps). This can randomly kill Termux sessions including
the XFCE desktop and CDE panel.

**Workaround by Android version:**
- **Android 14+:** Enable Developer Options → "Disable child process restrictions"
- **Android 12-13:** Requires ADB command from a PC:
  `adb shell settings put global settings_enable_monitor_phantom_procs false`
  OR root access.

This is NOT a CDE-specific issue but users must be aware of it.

### 4.5 SIGNAL HANDLING (LOW IMPACT)

`cdepanel.py` registers `signal.SIGHUP` handler. SIGHUP is available on Android/Bionic,
so this should work. However, Android's process lifecycle is different — apps can be
killed without signals. The `atexit` handler in `ShutdownHandler` is a good fallback.

### 4.6 LD_LIBRARY_PATH (LOW IMPACT)

The `MiscFun.py` module explicitly removes `LD_LIBRARY_PATH` when executing external
commands (to avoid PyInstaller conflicts). On Termux:
- When running from Python source (not PyInstaller), `LD_LIBRARY_PATH` is typically
  not set by Termux itself, so this is a non-issue.
- Termux uses `DT_RUNPATH` in binaries instead of `LD_LIBRARY_PATH`.

### 4.7 xhost BEHAVIOR (LOW IMPACT)

`startpanel` calls `xhost +si:localuser:$USER`. On Termux, the username is typically
the app's UID (e.g., `u0_a123`). `xorg-xhost` is available in Termux and should work,
but the exact behavior with Termux:X11's X server may differ from traditional X servers.
Termux:X11 generally doesn't require xhost configuration since it runs locally.

---

## 5. Code Changes Required for Termux Support

### 5.1 Changes That Can Be Done IN-TREE (no fork needed)

These are backward-compatible changes that improve Termux support without breaking
existing Linux functionality:

1. **Platform detection utility** (`scripts/platform_utils.py` or in `Globals.py`):
   ```python
   import os, platform
   
   def is_termux():
       return os.path.isdir('/data/data/com.termux')
   
   def get_prefix():
       return os.environ.get('PREFIX', '/usr')
   
   def get_system_share():
       return os.path.join(get_prefix(), 'share')
   
   def get_icon_dirs():
       share = get_system_share()
       dirs = [
           os.path.join(share, 'icons'),
           os.path.join(share, 'pixmaps'),
           os.path.expanduser('~/.local/share/icons'),
       ]
       if not is_termux():
           dirs.extend(['/usr/share/icons', '/usr/share/pixmaps',
                        '/usr/local/share/icons'])
       return dirs
   ```

2. **Update hardcoded paths in `ColorFun.py`**:
   - Replace `/usr/share/icons/...` with dynamic path resolution
   - Replace `/usr/share/pixmaps` with `get_system_share() + '/pixmaps'`

3. **Update `GenDefaultDrawersAndLayout.py`**:
   - Replace hardcoded `applications_dirs` and `image_dir_base`

4. **Update `startpanel`**:
   - Add Termux detection and `DISPLAY` verification
   - Optionally set `DISPLAY=:1` if not already set in Termux

5. **Update `install.py`**:
   - Add Termux-specific installation paths

6. **Update `cdepanel.py`**:
   - The `Globals.cdethemedirsrc` resolution when not running from PyInstaller
     should handle the Termux directory structure

### 5.2 Changes Requiring User Action (NOT code changes)

1. Install Termux packages: `pkg install x11-repo pyqt5 imagemagick xfce4 xorg-xhost`
2. Install Python packages: `pip install pillow pyxdg`
3. Disable Phantom Process Killer (Android 12+)
4. Configure Termux:X11 display flags if needed (`-legacy-drawing`, `-force-bgra`)

---

## 6. Fork vs In-Tree: Decision Matrix

| Factor | In-Tree | Fork |
|--------|---------|------|
| Code complexity | Low — mostly path abstraction | Same changes needed |
| Maintenance burden | Single codebase | Two codebases to maintain |
| Breaking existing Linux | No (if done correctly) | N/A |
| Termux-specific UX | Can be handled with detection | Full control |
| GTK3 theming workarounds | Limited (upstream Termux bug) | Same limitation |
| Community benefit | All users benefit | Fragmented |

**Verdict: IN-TREE SUPPORT IS RECOMMENDED.**

The required changes are:
- ~20 lines of platform detection utility code
- ~30-50 lines of path substitution across 2-3 files
- ~10 lines in startpanel for Termux detection

This is well within the scope of the existing codebase and does not justify a fork.

---

## 7. Known Bugs & Quirks Summary

| Issue | Severity | Workaround |
|-------|----------|------------|
| GTK3 themes don't apply in native Termux XFCE | Medium | Use proot-distro, or accept GTK2-only theming |
| Black screen on some devices | Medium | Use `-legacy-drawing` flag |
| Color channel swap (R↔B) | Low | Use `-force-bgra` flag |
| Phantom Process Killer (Android 12+) | High | Disable in Developer Options (14+) or via ADB (12-13) |
| High DPI phone screens | Medium | Adjust `-dpi` flag or XFCE scaling settings |
| `gtk-launch` may not be available | Low | Falls back gracefully in cdepanel.py |
| Pillow requires manual build on Termux | Low | Documented build command |
| Termux:X11 app must be installed separately (APK) | Low | Documented in setup |
| No Wayland support (X11 only) | Info | Termux:X11 is X11-only; CDE theme is X11-only — perfect match |

---

## 8. Recommended Implementation Plan

### Phase 1: Path Abstraction (Required)
- Create `platform_utils.py` with Termux detection and path helpers
- Update `ColorFun.py` hardcoded icon/pixmap paths
- Update `GenDefaultDrawersAndLayout.py` hardcoded application paths
- Update `startpanel` with Termux-aware DISPLAY handling

### Phase 2: Installation Support (Required)
- Update `install.py` with Termux-specific paths
- Create Termux setup script or document manual setup steps

### Phase 3: Documentation (Required)
- Termux + Termux:X11 setup guide
- Known limitations and workarounds
- Dependency installation commands

### Phase 4: UX Polish (Optional)
- DPI auto-detection for phone screens
- Panel size/position adjustment for small screens
- Touch-friendly interaction mode

---

## 9. Sources

- Termux:X11 GitHub: https://github.com/termux/termux-x11
- Termux packages wiki (filesystem layout): https://github.com/termux/termux-packages/wiki/Termux-file-system-layout
- Termux XFCE setup (phoenixbyrd): https://github.com/phoenixbyrd/Termux_XFCE
- GTK3 theming bug: https://github.com/termux/termux-packages/issues/27569
- Phantom Process Killer: https://github.com/termux/termux-app/issues/2366
- PyQt5 on Termux: https://github.com/termux/termux-app/issues/2990
- Pillow on Termux: https://pillow.readthedocs.io/en/stable/installation/building-from-source.html
- Termux:X11 troubleshooting: https://deepwiki.com/termux/termux-x11/6.3-troubleshooting
