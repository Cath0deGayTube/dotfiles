# CDE Panel Installation Guide

This guide explains how to install the CDE Panel either system-wide (for all users) or locally (for the current user only).

## Prerequisites

- Python 3.6 or higher
- GTK 2.0, 3.16, 3.20, and 4.x development libraries
- PyGObject
- ImageMagick (for icon generation)
- XFCE desktop environment (recommended)

## Installation Methods

### 1. User Installation (Recommended for Testing)

This will install the CDE Panel for the current user only, without requiring root privileges.

```bash
# Clone the repository (if not already done)
git clone https://github.com/yourusername/cdetheme.git
cd cdetheme

# Run the installer
python3 install.py

# Start the panel
./startpanel
```

### 2. System-wide Installation (Requires Root)

This will install the CDE Panel for all users on the system.

```bash
# Clone the repository (if not already done)
git clone https://github.com/yourusername/cdetheme.git
cd cdetheme

# Run the installer with system flag
sudo python3 install.py --system

# Start the panel (as any user)
cdepanel
```

### Installation Options

- `--system`: Install system-wide (requires root)
- `--force`: Overwrite existing files during installation

Example with options:
```bash
sudo python3 install.py --system --force
```

## Post-Installation

### Autostart (Recommended)

To start the panel automatically when you log in:

1. Open "Session and Startup" in your desktop environment settings
2. Add a new startup program:
   - Name: CDE Panel
   - Command: `cdepanel` (system-wide) or `/path/to/cdetheme/startpanel` (user)
   - Description: CDE/Motif Style Panel

### Uninstallation

#### User Installation
```bash
rm -rf ~/.config/CdePanel
rm -rf ~/.local/share/themes/CDE
rm -f ~/.local/share/applications/cde-*.desktop
```

#### System-wide Installation
```bash
sudo rm -rf /etc/xdg/CdePanel
sudo rm -rf /usr/share/themes/CDE
sudo rm -f /usr/share/applications/cde-*.desktop
sudo rm -f /usr/local/bin/cdepanel
```

## Troubleshooting

### Missing Dependencies
If you see errors about missing dependencies, install them using your distribution's package manager:

- **Debian/Ubuntu**:
  ```bash
  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 imagemagick
  ```

- **Fedora**:
  ```bash
  sudo dnf install python3-gobject gtk3 ImageMagick
  ```

### Panel Not Starting
If the panel doesn't start, check the logs:
```bash
cdepanel --debug 2>&1 | tee ~/cdepanel.log
```

### Theme Not Applying
If the theme isn't being applied correctly:
1. Ensure you've logged out and back in after installation
2. Check that the theme is selected in your desktop environment's appearance settings
3. Verify that the theme files are in the correct location:
   - User: `~/.local/share/themes/CDE`
   - System: `/usr/share/themes/CDE`

## Support

For additional help, please open an issue on the [GitHub repository](https://github.com/yourusername/cdetheme/issues).

## License

[Your License Here]
