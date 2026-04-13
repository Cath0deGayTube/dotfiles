#
# ~/.bashrc

# Source environment variables
source "~/.config/sh/env.sh"
# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Source aliases
source "~/.config/sh/aliases.sh"
# Fetch
hyfetch --ascii-file "~/.config/fastfetch/nyarch.txt"
