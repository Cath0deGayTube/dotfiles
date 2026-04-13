#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import signal
#signal.signal(signal.SIGINT, signal.SIG_DFL)
import re
import os
import sys
import shutil
from PyQt5 import QtCore, QtGui, QtWidgets
import MotifColors
import Globals
from MotifColors import colorize_bg
from MiscFun import *

import time

#XFCE image-style values for xfconf-query
XFCE_STYLE_NONE=0
XFCE_STYLE_CENTERED=1
XFCE_STYLE_TILED=2
XFCE_STYLE_STRETCHED=3
XFCE_STYLE_SCALED=4
XFCE_STYLE_ZOOMED=5

screenHeight=600
def prepareBackDrops(opts):
    global screenHeight
    screenHeight=QtWidgets.QApplication.primaryScreen().geometry().height()
    for i in range(1,opts.nworkspaces+1):
        wscol=opts.workspacecolors[i]
        backdropsrc=opts.workspacebackdrops[i]
        if backdropsrc=="Gradient":scaletoheight=True
        else:scaletoheight=False
        prepareBackdrop(opts,i,backdropsrc,wscol,scaletoheight)
#all backdrops are called backdrop.pm, converted to backdrop.png
#def prepareBackdrop(self,i,backdropsrc,wscol,scaletoheight):
def prepareBackdrop(opts,i,backdropsrc,wscol,scaletoheight):
    print(Globals.backdropdir)
    global screenHeight
    scaleopts=''
    if scaletoheight:scaleopts='-geometry x{screenHeight}'.format(**globals())
    #colorize backdrop to given motif colorset. produces xpm
    palettefile=os.path.normpath(os.path.join(Globals.palettedir,opts.currentpalettefile))
    backdropin=os.path.normpath(os.path.join(Globals.backdropdir,"""{backdropsrc}.pm""".format(**locals())))
    backdropoutxpm=os.path.normpath(os.path.join(Globals.backdropdir,"""BACKDROP{i}.xpm""".format(**locals())))
    #todo checkfile shouldnt exit the program
    colorize_bg(checkFile(backdropin),backdropoutxpm,checkFile(palettefile),opts.ncolors,wscol)
    #convert original colored cde pm file to fit screen if required
    backdropoutpng=os.path.normpath(os.path.join(Globals.backdropdir,"""BACKDROP{i}.png""".format(**locals())))
    if Globals.convertversion>0:
        cmd="convert {scaleopts} {backdropoutxpm} {backdropoutpng}".format(**locals())
        execWSysLibsStdO(cmd)

#IN LAPTOP XUBUNTU IT IS THIS
#/backdrop/screen0/monitor0/workspace0/last-image
#/backdrop/screen0/monitor0/workspace1/last-image
#BUT IN VIRTUALBOX INSTALL OF XUBUNTU IT WAS
#/backdrop/screen0/monitorVGA-1/workspace0/last-image
#/backdrop/screen0/monitorVGA-1/workspace1/last-image
#THERE WERE ALSO OTHER MONITOR AND SCREEN ENTRIES IN SETTINGS EDITOR
#DONT KNOW WHAT THOSE ARE FOR ONLY THE ONES WITH 'WORKSPACEN' SEEM TO
#AFFECT THE ACTUAL BACKGROUND. DUNNO.
#20221030
#didnt work in virtualbox, so modified to set the backrop file in all
#'monitor' entries for xfce4-desktop property. 
def xfconfWorkspacePaths():
    """Get all workspace paths from xfconf-query with error handling and fallbacks."""
    wspaths = []
    try:
        # First try to get workspace paths from xfconf-query
        cmd = "xfconf-query -c xfce4-desktop --list 2>/dev/null | grep workspace | grep last-image || true"
        cmdout = execWSysLibsStdO(cmd).splitlines()
        
        if not cmdout:
            # If no workspaces found, try to create default workspace
            try:
                cmd = """
                xfconf-query -c xfce4-desktop -p /backdrop/single-workspace-mode -t bool -s false --create 2>/dev/null || true
                xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/last-image -t string -s "" --create 2>/dev/null || true
                """
                execWSysLibNonBlock(cmd)
                # Try getting workspaces again
                cmd = "xfconf-query -c xfce4-desktop --list 2>/dev/null | grep workspace | grep last-image || true"
                cmdout = execWSysLibsStdO(cmd).splitlines()
            except Exception as e:
                print(f"Warning: Could not initialize XFCE workspaces: {e}")
                return ["/backdrop/screen0/monitor0/workspace"]  # Default fallback
        
        # Extract workspace paths
        for line in cmdout:
            match = re.search(r'(^.*workspace\d+)', line)
            if match:
                wspaths.append(match.group(1).strip())
        
        # If still no workspaces found, use default
        if not wspaths:
            wspaths = ["/backdrop/screen0/monitor0/workspace"]
            
    except Exception as e:
        print(f"Error getting XFCE workspace paths: {e}")
        wspaths = ["/backdrop/screen0/monitor0/workspace"]  # Fallback value
        
    return wspaths

def imageStyleForBackdrop(backdropsrc):
    """Return the XFCE image-style value for the given backdrop type."""
    if backdropsrc=="Gradient":
        return XFCE_STYLE_STRETCHED
    else:
        return XFCE_STYLE_TILED

def initXfceBackdops(opts):
    """Initialize XFCE backdrops with error handling and fallbacks."""
    print("Initializing XFCE backdrops...")
    
    try:
        # Set single-workspace-mode to false if not already set
        cmd = """
        if ! xfconf-query -c xfce4-desktop -p /backdrop/single-workspace-mode 2>/dev/null; then
            xfconf-query -c xfce4-desktop -p /backdrop/single-workspace-mode -t bool -s false --create
        fi
        xfconf-query -c xfce4-desktop -p /backdrop/single-workspace-mode -s false 2>/dev/null || true
        """
        execWSysLibNonBlock(cmd)
        
        # Set xfce backdrops to BACKDROPN.png
        for i in range(1, opts.nworkspaces + 1):
            try:
                backdropsrc=opts.workspacebackdrops[i]
                style=imageStyleForBackdrop(backdropsrc)
                setXfBackdrop(i,style)
            except Exception as e:
                print(f"Warning: Could not set backdrop for workspace {i}: {e}")
                continue
                
    except Exception as e:
        print(f"Error initializing XFCE backdrops: {e}")
        print("Continuing without backdrop initialization...")

def setXfBackdrop(workspacenr,image_style=XFCE_STYLE_TILED):
    """Set backdrop for a specific workspace with error handling.
    image_style: XFCE image-style value (2=tiled, 3=stretched, etc.)"""
    try:
        print(f"Setting backdrop for workspace {workspacenr} (image-style={image_style})")
        
        # Get workspace paths with fallback
        workspacepaths = xfconfWorkspacePaths()
        if not workspacepaths:
            print("No workspace paths found, using default")
            workspacepaths = ["/backdrop/screen0/monitor0/workspace"]
            
        bgfile = os.path.normpath(os.path.join(Globals.backdropdir, f"BACKDROP{workspacenr}.png"))
        
        # Ensure the backdrop file exists
        if not os.path.exists(bgfile):
            print(f"Backdrop file not found: {bgfile}")
            return
            
        # Adjust workspace number (0-based for XFCE)
        workspace_idx = workspacenr - 1
        
        # Set backdrop for all monitor/workspace entries
        for workspace_path in workspacepaths:
            try:
                # Remove any existing workspace number
                base_path = re.sub(r'workspace\d+$', '', workspace_path)
                # Add the target workspace number
                ws_path = f"{base_path}workspace{workspace_idx}"
                
                # Set the backdrop image
                cmd = f"""
                xfconf-query -c xfce4-desktop -p {ws_path}/last-image -t string -s "{bgfile}" --create 2>/dev/null || \
                xfconf-query -c xfce4-desktop -p {ws_path}/last-image -s "{bgfile}" 2>/dev/null || true
                """
                execWSysLibNonBlock(cmd)
                
                # Set the image style (tiled vs stretched etc.)
                cmd = f"""
                xfconf-query -c xfce4-desktop -p {ws_path}/image-style -t int -s {image_style} --create 2>/dev/null || \
                xfconf-query -c xfce4-desktop -p {ws_path}/image-style -s {image_style} 2>/dev/null || true
                """
                execWSysLibNonBlock(cmd)
                
            except Exception as e:
                print(f"Warning: Could not set backdrop for {workspace_path}: {e}")
                continue
                
    except Exception as e:
        print(f"Error in setXfBackdrop: {e}")











