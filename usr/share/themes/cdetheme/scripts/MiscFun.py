#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import signal
#signal.signal(signal.SIGINT, signal.SIG_DFL)
import os.path
import subprocess
import sys
import os


#calling xfconf-query (or other external commands) from inside pyinstaller environemnt
#can cause problems: remove LD_LIBRARY_PATH from env if present (this is inside pyinstaller env)
#then external command will use system libraries instead of ones in pyinstaller environment
#20221203 because pyinstaller sets this variable
pip_env = os.environ.copy()
if 'LD_LIBRARY_PATH' in pip_env:
    pip_env.pop('LD_LIBRARY_PATH')

#NON BLOCKING
#(stdout,stderr)=execWSysLibsNonBlckStdOE(cmd)
#return stdout and stderr

def execWSysLibsNonBlckStdOE(cmd):
    out = subprocess.Popen(cmd, shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=pip_env, universal_newlines=True)
    (stdout, stderr) = out.communicate()
    return (stdout,stderr)

#NON BLOCKING
    #popen returns a Popen object.
#p=execWSysLibNonBlock(cmd)
#(stdout,stderr)=p.communicate()
#return subprocess obj

def execWSysLibNonBlock(cmd):
    try: 
        p=subprocess.Popen(cmd, shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=pip_env, universal_newlines=True)
    except OSError as e: 
        #this doesnt seem to work
        print(cmd)
        print('!!!!!!!!!!!!!!!!!!!subprocess ERROR!!!!!!!!!!!!!!!!!!!!!!!')
        print(e.output)
        p=''
    return p

#BLOCKING
#check_output returns the output of the command execution.
#return stdout

def execWSysLibsStdO(cmd):
    print(cmd)
    output=subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, env=pip_env, universal_newlines=True)
    print(output)
    return output


def cmd_exists(cmd, path=None):
    """ test if path contains an executable file with name"
    """
    if path is None:
        path = os.environ["PATH"].split(os.pathsep)

    for prefix in path:
        filename = os.path.normpath(os.path.join(prefix, cmd))
        executable = os.access(filename, os.X_OK)
        is_not_directory = os.path.isfile(filename)
        if executable and is_not_directory:
            return True
    return False


def checkFile(filename):
    if os.path.isfile(filename):
        return filename
    else:
        print('FILE NOT FOUND: '+filename)
        sys.exit()

def checkDir(filename):
    if os.path.isdir(filename):
        return filename
    else:
        print('DIRECTORY NOT FOUND: '+filename)
        sys.exit()

