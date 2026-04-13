#!/bin/bash

# Check if the OS is Arch-based
if ! grep -q -e "Arch" -e "Manjaro" -e "EndeavourOS" /etc/os-release; then
  echo "You aren't using arch btw :("
  exit 1 # KILL
fi

# Is Arch-based
echo "You use arch btw :3"
echo "Proceeding..."
echo ""

# Check if user actually has permissions to do this stuff
if ! sudo -v; then
  echo "You need sudo privileges to run this script."
  exit 1
fi

echo "WARNING: This WILL overwrite a bunch of configuration files without asking. I am NOT RESPONSIBLE if you mess up your system."
echo "You will be prompted to confirm in 5 seconds, PLEASE READ ABOVE!!!"
sleep 5

read -p "Type 'YES' all in CAPS to proceed" response

# Continue if YES
if [[ ! "$response" == "YES" ]]; then
  echo "Aborted"
  exit 1
fi

echo "Ok, we've warned you..."
CLONEDIR="$(pwd)"

# Install yay if needed
if ! command -v yay &>/dev/null; then
  git clone aur.archlinux.org/yay-bin "$CLONEDIR/yay-bin"
  cd "$CLONEDIR/yay-bin" || {
    echo "Something failed while changing into yay-bin directory"
    exit 1
  }
  makepkg -si
  cd "$CLONEDIR"
fi

# Check if CDE is already installed, if not, install dependencies, clone, and install
if [ ! -d /usr/dt ]; then

  # CDE Dependencies
  yay -S autoconf automake libtool make rpcsvc-proto rpcbind opensp xorg xorg-server-devel gcc dnsutils git libxinerama libxss ncurses openmotif xbitmaps bison flex tcl ksh ncompress --needed || {
    echo "Dependencies installation failed! Exiting..."
    exit 1
  }

  # Stuff that's needed to be done according to cde wiki
  sudo ln -s /usr/bin/cpp /lib/cpp
  sudo systemctl enable --now rpcbind

  # Clone and compile CDE
  git clone https://git.code.sf.net/p/cdesktopenv/code "$CLONEDIR/cdesktopenv-code"
  cd "$CLONEDIR/cdesktopenv-code" || {
    echo "Something failed at entering cdesktopenv-code :("
    exit 1
  }
  ./autogen.sh
  ./configure
  make
  #check if make succeeded
  if [ $? -ne 0 ]; then
    echo "Something failed at make for CDE :("
    echo "exiting..."
    exit 1
  fi

  sudo make install
  sudo cp -f cde/contrib/desktopentrycde.desktop /usr/share/xsessions/cde.desktop
  cd "$CLONEDIR"
fi

# Install programs
yay -S hyfetch fastfetch neovide neovim picom rofi ripgrep waterfox-bin lxterminal pcmanfm xorg-twm nitrogen xbindkeys dzen2 i3bar || {
  echo "Dependencies installation failed! Exiting..."
  exit 1
}

# Install TWM xsession and launch script
sudo cp -r "$CLONEDIR/etc/xinitrc.d" "/etc/xinitrc.d"
sudo cp -r "$CLONEDIR/usr/share/xsessions/twm.desktop" "/usr/share/xsessions/twm.desktop"

# Copy .bash_profile and .bashrc
cp -f "$CLONEDIR/home/user/.bash_profile" "$HOME/.bash_profile"
cp -f "$CLONEDIR/home/user/.bashrc" "$HOME/.bashrc"

# Copy CDE Config
cp -rf "$CLONEDIR/home/user/.dt" "$HOME/.dt"

# Copy twm config
cp -f "$CLONEDIR/home/user/.twmrc" "$HOME/.twmrc"

# Copy twm icons
cp -rf "$CLONEDIR/usr/include/X11/bitmaps" "/usr/include/X11/"

# Copy keybinds
cp -f "$CLONEDIR/home/user/.xbindkeysrc" "$HOME/.xbindkeysrc"

# Copy other configs
cp -rf "$CLONEDIR/home/user/.config" "$HOME/.config"
