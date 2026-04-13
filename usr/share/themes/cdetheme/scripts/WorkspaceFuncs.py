#!/usr/bin/python3
# -*- coding: utf-8 -*-
#   cb .jos http://ewmh.readthedocs.io/en/latest/ewmh.html#examples
#import subprocess
import os,sys
import re
try:
    from ewmh import EWMH
    ewmh = EWMH()
except Exception as e:
    print(f"WARNING: Could not connect to X11 display: {e}")
    print("Make sure an X server is running and DISPLAY is set (e.g. export DISPLAY=:0)")
    ewmh = None
from Xlib.error import BadWindow
import Globals
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
from xdg import BaseDirectory, DesktopEntry
from MiscFun import *


def safe_get_wm_class(w):
    """Safely get WM_CLASS, returning None if window no longer exists."""
    try:
        return w.get_wm_class()
    except BadWindow:
        return None
    except Exception:
        return None

def wm_class_matches(wm_class, executable):
    if not wm_class or not executable:
        return False
    names = []
    for value in wm_class:
        if value:
            names.append(str(value))
    executable_names = {str(executable)}
    executable_base = os.path.splitext(str(executable))[0]
    executable_names.add(executable_base)
    for candidate in names:
        for executable_name in executable_names:
            if candidate == executable_name or re.search(re.escape(executable_name), candidate):
                return True
    return False

def set_window_all_desktops_and_sticky(w):
    ewmh.setWmDesktop(w, 0xFFFFFFFF)
    ewmh.setWmState(w,1,'_NET_WM_STATE_STICKY')
    ewmh.display.flush()

def which(cmd, mode=os.F_OK | os.X_OK, path=None):
        """Given a command, mode, and a PATH string, return the path which"
        conforms to the given mode on the PATH, or None if there is no such
        file.
        `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
        of os.environ.get("PATH"), or can be overridden with a custom search
        path.
        Note: This function was backported from the Python 3 source code.
        """
        # Check that a given file can be accessed with the correct mode.
        # Additionally check that `file` is not a directory, as on Windows
        # directories pass the os.access check.

        def _access_check(fn, mode):
            return (
                os.path.exists(fn) and os.access(fn, mode) and not os.path.isdir(fn)
            )

        # If we're given a path with a directory part, look it up directly'
        # rather than referring to PATH directories. This includes checking
        # relative to the current directory, e.g. ./script
        if os.path.dirname(cmd):
            if _access_check(cmd, mode):
                return cmd

            return None

        if path is None:
            path = os.environ.get("PATH", os.defpath)
        if not path:
            return None

        path = path.split(os.pathsep)

        if sys.platform == "win32":
            # The current directory takes precedence on Windows.
            if os.curdir not in path:
                path.insert(0, os.curdir)

            # PATHEXT is necessary to check on Windows.
            pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
            # See if the given file matches any of the expected path
            # extensions. This will allow us to short circuit when given
            # "python.exe". If it does match, only test that one, otherwise we
            # have to try others.
            if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
                files = [cmd]
            else:
                files = [cmd + ext for ext in pathext]
        else:
            # On other platforms you don't have things like PATHEXT to tell you'
            # what file suffixes are executable, so just pass on cmd as-is.
            files = [cmd]

        seen = set()
        for dir in path:
            normdir = os.path.normcase(dir)
            if normdir not in seen:
                seen.add(normdir)
                for thefile in files:
                    name = os.path.normpath(os.path.join(dir, thefile))
                    if _access_check(name, mode):
                        return name

        return None


APP_NAME='xterm'

def get_config_dir(app_name=APP_NAME):
    if "XDG_CONFIG_HOME" in os.environ:
        confighome = os.environ['XDG_CONFIG_HOME'] 
    elif "APPDATA" in os.environ: # On Windows
        confighome = os.environ['APPDATA'] 
    else:
        try:
            from xdg import BaseDirectory   
            confighome =  BaseDirectory.xdg_config_home
        except ImportError: # Most likely a Linux/Unix system anyway
            confighome =  os.path.normpath(os.path.join(get_home_dir(), ".config"))
    configdir = os.path.normpath(os.path.join(confighome, app_name))
    return configdir

def get_home_dir():
    if sys.platform == "cygwin":
        home_dir = os.getenv('HOME')
    else:
        home_dir = os.getenv('USERPROFILE') or os.getenv('HOME')
    if home_dir is not None:
        return os.path.normpath(home_dir)
    else:
        raise KeyError("Neither USERPROFILE or HOME environment variables set.")

#command is launched somewhere earlier
#looks for NEWEST occurence of command in ps uxa
#then puts pid on blinkerList
#and removes 'dummypid' from blnkerlist
def findPidAddToBlinkerList(command):
    #if command=='google-chrome-stable':command='chrome'#hmm doesnt seem tow ork try some other time
    cmd="""
    ps --sort=start_time uxa|grep {command}
    """.format(**locals())
    #output=subprocess.check_output(cmd, shell=True, universal_newlines=True)
    output=execWSysLibsStdO(cmd)
    lines=output.splitlines()
    if len(lines)==2:
        print('findPidAddToBlinkerList no worke leave for now')
        #google-chrome-stable couples to some other process or somehting or it is just
        #a script that launches another executable. So leave for now. Maybe add a list of
        #other options here to try and find the correct one eg for google-chrome-stable look for 'chrome'
    else:
        #output contains newest occurrences of command in ps on the bottom. But last 2 occurrences are
        #the ps command itself and the grep ! So third from last is the command we are looking for.
        line=lines[-3]
        words=line.split()
        pidIHope=int(words[1])#should be int  for updateBlinkerList
        Globals.blinkerList.append(pidIHope)
    #to make the blinker go right away, a dummypid can be added on it. Remove if present
    if 'dummypid' in Globals.blinkerList: Globals.blinkerList.remove('dummypid')


def execFromDesktopentrypath (desktopentrypath):
    if not desktopentrypath or not os.path.isfile(desktopentrypath):
        return ''
    d=DesktopEntry.DesktopEntry(desktopentrypath)
    getexec=d.getExec()#all kind of junk..?: 'set BLABLA command {:f} %Bla'
    if not getexec:
        return ''
    getexec=os.path.basename(getexec)
    getexec1=re.sub('%.*','',getexec) #remove the %Fs and what not: 
    parts=getexec1.split()
    if not parts:
        return ''
    command=parts[-1]#hopefully the actual execultutble 'command' , the last word
                                #note: but if gtk-launch is on system, use 'gtk-launch x.desktop'
    return command

#in picbuttoncommand for start and exit buttons i still use Run(command) 
#should be reconfigured to do only Run(desktopentry) or something (mabye)
#not used anymore directly to exec program
def Run(command,desktopentrypath=None):
    print('Run')
    if desktopentrypath: 
        #cmd='xdg-open '+desktopentrypath#aha this only works 'with shell' and then the blinkerlist doesnt owrk
        #xdg-open doesnt work consistently on all systems. Sometimes it just opens the .desktop file
        #in a text editor. So use gtk-launch for now. But this doesnt accept the full path
        desktopentrybase=os.path.basename(desktopentrypath)
        cmd='gtk-launch '+desktopentrybase 
    else:
        #if it is a plain command only, ie Run(command), just exec
        cmd=command

    if cmd:
        p=None
        try:
            print('TRYING TO RUN "'+str(cmd)+'"')
            p = execWSysLibNonBlock(cmd)
        except OSError as e:
            print("Execution failed:", e, file=sys.stderr)

        if p:
            #try and find the pid of the process launched by xdg-open and put it on the blinkerlist
            #but give it a second to appear (add dummypid right away, see below)
            Globals.timer3=QtCore.QTimer()
            Globals.timer3.timeout.connect(partial(findPidAddToBlinkerList,command))
            Globals.timer3.setSingleShot(True)
            Globals.timer3.start(200)
            #see CdePanel.py: def updateBlinkerList():
            #hmmm if one of these timers is run, local var inside func, it doesnt work:    
            #var gets cleaned up before timer is finished
            #put a dummy pid in the blinkerlist right away, to make the blinker blink directly after
            #the button is pressed. The dummypid is replaced by the real one by findPidAddToBlinkerList 
            # updateBlinkerList then watches the windowlist, and removes the found pid if the window
            # appears. Then the blinker stops blinking.
            #If all doesnt work.. just kill the blinker after 5 seconds
            Globals.blinkerList.append('dummypid')
            Globals.timer2=QtCore.QTimer()
            Globals.timer2.timeout.connect(purgeBlinkerList)
            Globals.timer2.setSingleShot(True)
            Globals.timer2.start(5000)

def RunDesktopEntry(desktopentrypath):
    #extract command from desktopentry. Also needed for blinkerlist
    #but run using gtk-launch
    if not desktopentrypath or not os.path.isfile(desktopentrypath):
        print('RunDesktopEntry: no desktop entry path, ignoring click')
        return
    command=execFromDesktopentrypath(desktopentrypath)
    print('RunDesktopEntry '+command)
    name=DesktopEntry.DesktopEntry(desktopentrypath).getName()
    #when desktopentry name is this open the settings dialog from main window
    #if it exists. Kind of send message if it exist
    if name=='CDE/Motif Settings':
        try: 
            Globals.cdepanel
        except: 
            print("Tried to open SETTINGS but cdepanel no exist")
            return
        else: 
            Globals.cdepanel.openConfigDialog()
            return
    
    # Special handling for Orage calendar - fall back to system default calendar if not available
    if 'orage' in desktopentrypath.lower() and not which('orage'):
        print("Orage not found, trying to use system default calendar application")
        cmd = 'xdg-open "calendar:"'
    # Use gtk-launch if available
    elif which('gtk-launch'):
        desktopentrybase=os.path.basename(desktopentrypath)
        cmd='gtk-launch '+desktopentrybase 
    else:
        #if gtk-launch is not on system, use command that was attempted to extract from desktopentry file
        cmd=command
    
    p=None
    try:
        print('TRYING TO RUN "'+str(cmd)+'"')
        p = execWSysLibNonBlock(cmd)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        # If the command failed and we're trying to run Orage, try the system default calendar'
        if 'orage' in cmd.lower():
            try:
                print("Falling back to system default calendar application")
                p = execWSysLibNonBlock('xdg-open "calendar:"')
            except OSError as e2:
                print("Also failed to open system calendar:", e2, file=sys.stderr)
    if p:
        #try and find the pid of the process launched and put it on the blinkerlist
        #but give it a second to appear (add dummypid right away, see below)
        Globals.timer3=QtCore.QTimer()
        Globals.timer3.timeout.connect(partial(findPidAddToBlinkerList,command))
        Globals.timer3.setSingleShot(True)
        Globals.timer3.start(200)

        #testing
        if command=='orage':
            callMoveWinToMousePointerUntilExists('orage')

        #see CdePanel.py: def updateBlinkerList():
        #hmmm if one of these timers is run, local var inside func, it doesnt work:    
        #var gets cleaned up before timer is finished
        #put a dummy pid in the blinkerlist right away, to make the blinker blink directly after
        #the button is pressed. The dummypid is replaced by the real one by findPidAddToBlinkerList 
        # updateBlinkerList then watches the windowlist, and removes the found pid if the window
        # appears. Then the blinker stops blinking.
        #If all doesnt work.. just kill the blinker after 5 seconds
        Globals.blinkerList.append('dummypid')
        Globals.timer2=QtCore.QTimer()
        Globals.timer2.timeout.connect(purgeBlinkerList)
        Globals.timer2.setSingleShot(True)
        Globals.timer2.start(5000)

#hiery
def callMoveWinToMousePointerUntilExists(command):
    print('callMoveWinToMousePointerUntilExists')
    #try a number of times because process doesnt appear in windwolist until  after some time
    if not moveWinToMousePointer(command):
        try:
            moveWinTimer.start(50)
        except: 
            moveWinTimer=QtCore.QTimer.singleShot(50,partial(callMoveWinToMousePointerUntilExists,command))


def moveWinToMousePointer(command):
    print("moveWinToMousePointer "+command)
    p=QtGui.QCursor.pos();
    screen = QtWidgets.QApplication.primaryScreen().geometry()
    screenheight=screen.height()
    panelheight=int(int(Globals.scalefactor)*85)
    if moveWinTo(command,p.x(),screenheight-panelheight):
        return True
    else:
        return False

def purgeBlinkerList():
    print('PURGE BLINKERLIST')
    #if pid in Globals.blinkerList: Globals.blinkerList.remove(pid)
    Globals.blinkerList[:]=[]

############################################################################################
#return false if win doesnt exist yet
def moveWinTo(executable,xnew,ynew):
    print('moveWinTo')
    print(executable,xnew,ynew)
    allwins = ewmh.getClientList() or []
    executablewins=[]
    for w in allwins:
        #this sometimes is 'None'
        wm_class = safe_get_wm_class(w)
        if wm_class:
            #if wm_class[0]==executable:
            if re.search(executable,wm_class[0]):
                executablewins.append(w)
    if len(executablewins)==0:
        return False
    else:
        for w in executablewins:
            windowheight=w.get_geometry().height
            windowwidth=w.get_geometry().width
            xnew1=xnew+windowwidth
            ynew1=ynew-windowheight
            #what is gravity supposed to do? gravity then title bar height is 
            #somehow involved 8=ok
            #x has no effect todo hierx
            ewmh.setMoveResizeWindow(w, gravity=8, x=xnew, y=ynew1)
        return True

#Keep panel on all desktops
def setWindowSticky(executable):
    print('setWindowSticky for '+executable)
    allwins = ewmh.getClientList() or []
    executablewins=[]
    for w in allwins:
        #this sometimes is 'None'
        wm_class = safe_get_wm_class(w)
        if wm_class_matches(wm_class, executable):
            executablewins.append(w)
    for w in executablewins:
        set_window_all_desktops_and_sticky(w)

#return Flase if window doesnt exist yet
#if does exist: set all sticky and return true
def setWindowSticky1(executable):
    print('setWindowSticky for '+executable)
    allwins = ewmh.getClientList() or []
    executablewins=[]
    for w in allwins:
        #this sometimes is 'None'
        wm_class = safe_get_wm_class(w)
        if wm_class_matches(wm_class, executable):
            executablewins.append(w)
    if len(executablewins)==0:
        return False
    else:
        for w in executablewins:
            set_window_all_desktops_and_sticky(w)
        return True

def setWindowAbove(executable):
    allwins = ewmh.getClientList() or []
    executablewins=[]
    for w in allwins:
        #this sometimes is 'None'
        wm_class = safe_get_wm_class(w)
        if wm_class_matches(wm_class, executable):
            executablewins.append(w)
    for w in executablewins:
        set_window_all_desktops_and_sticky(w)
        ewmh.setWmState(w,0,'_NET_WM_STATE_BELOW')
        ewmh.setWmState(w,1,'_NET_WM_STATE_ABOVE')
        ewmh.display.flush()


def setWindowBelow(executable):
    allwins = ewmh.getClientList() or []
    executablewins=[]
    for w in allwins:
        #this sometimes is 'None'
        wm_class = safe_get_wm_class(w)
        if wm_class_matches(wm_class, executable):
            executablewins.append(w)
    for w in executablewins:
        set_window_all_desktops_and_sticky(w)
        ewmh.setWmState(w,0,'_NET_WM_STATE_ABOVE')
        ewmh.setWmState(w,1,'_NET_WM_STATE_BELOW')
        ewmh.display.flush()

def getLastWorkspace():
    return ewmh.getNumberOfDesktops()


#VERSION BASED ON WMCTRL WORKS FASTER AND LESS POLOINKY
#still use that so we dont need wmctrl installed
#Switch to new desktop
#def setCurrentWorkspace1(workspace):
    #workspace-=1
    #cmd='wmctrl -s '+str(workspace)
    #output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
def setCurrentWorkspace(workspace):
    try:
        ewmh.setCurrentDesktop(workspace-1)
        ewmh.display.flush()
    except Exception as e:
        print('Error switching workspace: '+str(e))

#Get currently displayed workspace
#NOT SURE WHICH ONE WORKS BEST HERE, BUT HAS TO BE CALLED EVERY 300 MS
#SO MAYBE BETTER NOT USE EXTERNAL COMMAND
#def getCurrentWorkspace():
    #cmd='wmctrl -d'
    #output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    #lines=output.splitlines() #array with elements=lines
    #for c in lines:
        #if re.search('//*',c):
            #x=c.split(' ') 
    #currentdestkop=int(x[0])+1
    #return currentdestkop
def getCurrentWorkspace():
    #on MWM this returns error..
    try:
        W=ewmh.getCurrentDesktop()
    except:
        return 1
    return W+1

#best not rely on wmctrl
def setNumberOfWorkspaces(n):
    ewmh.setNumberOfDesktops(n)
    ewmh.display.flush()
#def setNumberOfWorkspaces(n):
    #cmd='wmctrl -n '+str(n)
    #output = subprocess.check_output(cmd, shell=True, universal_newlines=True)

def switchToNextWorkspace():
    N=getLastWorkspace()
    C=getCurrentWorkspace()
    C+=1
    if C>N:C=1
    setCurrentWorkspace(C)

def switchToPrevWorkspace():
    N=getLastWorkspace()
    C=getCurrentWorkspace()
    C-=1
    if C<1:C=N
    setCurrentWorkspace(C)








##################################################################
#FOR GETTING CORRECT ENTRY IN WINDOWLIST ---------------V
#pycdewins = filter(lambda w: w.get_wm_class()[1] == 'HBox.py', wins)
def printWindowList():
    wins = ewmh.getClientList() or []
    for w in wins:
        #<class 'Xlib.display.Window'>(0x04600002)
        #[0] is kleine letters/[1] is hoofdletters (exec/name?)
        #!?!?!bij [1]: is executalbe (script) 'cdepanel' dan staat er in [1]: 'Cdepanel' Waar komt de HL vandaan????
        #wacht bij [0] staat erbij CdePanel ook gewoon hoofdletters, die dus gebruiken
        #ook bij stwindowsticky
        wm_class = safe_get_wm_class(w)
        if wm_class:
            print('>>>'+wm_class[0])
            print(ewmh.getWmPid(w))
#printWindowList()
#setWindowSticky('HBox.py')


#def main():
    #app = QApplication(sys.argv)
    #d=Dum()
    #sys.exit(app.exec_())
#if __name__ == '__main__':
   #main()






##################################################################
##################################################################
##################################################################
##################################################################

#def getDesktopList():
    #cmd='wmctrl -d'
    #output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    #lines=output.splitlines() #array with elements=lines
    #desktops=[]
    #for c in lines:
        #x=c.split(' ')[0]
        #desktops.append(x)
    #return desktops 

#def getLastWorkspace():
    #cmd='wmctrl -d'
    #output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    #lines=output.splitlines() #array with elements=lines
    #return len(lines)

#def setPanelSticky():
    #wins = ewmh.getClientList()
    #pycdewins = filter(lambda w: w.get_wm_class()[1] == 'HBox.py', wins)
    #for pycdewin in pycdewins:
        #pycdewin=pycdewins[0]
        #ewmh.setWmState(pycdewin,1,'_NET_WM_STATE_STICKY')
        #ewmh.display.flush()


