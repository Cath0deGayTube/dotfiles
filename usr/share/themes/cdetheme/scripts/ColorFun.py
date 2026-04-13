#!/usr/bin/python3
# -*- coding: utf-8 -*-

from io import StringIO, BytesIO
from PIL import Image, ImageFilter,ImageEnhance
import os,sys
from PyQt5 import QtGui, QtCore, QtWidgets
import re
import Globals
import platform_utils
from JosQPainter import JosQPainter
import threading
import time
from glob import glob
import tempfile,shutil
from MiscFun import *
from xdg import IconTheme
from xdg import DesktopEntry

#create text icon the size of baseimage=QPixmap, save to destination file
def textIconSameSizeAsFile(baseimage,destinationfile,text):
    painter = JosQPainter(baseimage)
    painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
    painter.fillRect(0, 0, 1000, 1000, QtCore.Qt.transparent)
    #if Globals.smoothTransform:
        #painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
    painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
    font=painter.font()
    font.setPointSize (20)
     #//font.setWeight(QtGui.QFont::DemiBold);
    painter.setFont(font)
    painter.setPen(QtGui.QColor('#111111'))
    x=10
    y=22
    painter.drawText(x,y,text)
    painter.setPen(QtCore.Qt.white)
    painter.drawText(x-1,y-1,text)
    painter.end()
    #baseimage.save(destinationfile)#__debug

def convertPixmap(pixmap, brightness, contrast, saturation, sharpness):
    if pixmap.isNull():
        return pixmap
    tmpf=None
    try:
        #save QPixmap to temp file, process with PIL, load back
        tmpf=tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        tmpname=tmpf.name
        tmpf.close()
        saveok=pixmap.save(tmpname,'PNG')
        fsize=os.path.getsize(tmpname) if os.path.exists(tmpname) else -1
        im=Image.open(tmpname)
        if brightness!=1.0:
            im=ImageEnhance.Brightness(im).enhance(brightness)
        if contrast!=1.0:
            im=ImageEnhance.Contrast(im).enhance(contrast)
        if sharpness!=1.0:
            im=ImageEnhance.Sharpness(im).enhance(sharpness)
        im=im.filter(ImageFilter.UnsharpMask(radius=0,percent=100,threshold=0))
        if saturation!=1.0:
            im=ImageEnhance.Color(im).enhance(saturation)
        im.save(tmpname,'PNG')
        im.close()
        pixmap=QtGui.QPixmap(tmpname)
        os.unlink(tmpname)
        return pixmap
    except Exception as e:
        print('Error in convertPixmap: '+str(e))
        if tmpf and os.path.exists(tmpf.name):
            try: os.unlink(tmpf.name)
            except: pass
        return pixmap

#icon in pixbut is no global resource yet, but file. maybe later
#returns the width
#for drawer entries
def createTextIcon(text,pixelsize,destinationfile,opts=None):
    #font=QtGui.QFont('Lucida Bright') #werkt wel #font.setStyleName('Book') 
    font=QtGui.QFont(Globals.font) #werkt wel
    font.setStyleName(Globals.fontStyle) 
    font.setPixelSize (pixelsize)
    spacing=1
    font.setLetterSpacing(QtGui.QFont.PercentageSpacing,spacing*100)
    fm=QtGui.QFontMetrics(font)
    r=fm.boundingRect(text)
    #hmmm------------------v
    xpm=QtGui.QPixmap(int(r.width()*1.1),r.height())
    c = QtGui.QColor(0)
    c.setAlpha(0)
    xpm.fill(c)
    #for some reason the string is in the negative half plane so pull it down
    x=-r.x()*spacing*1.1#??
    y=-r.y()
    painter = JosQPainter(xpm)
    painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
    #20221109
    #painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
    #painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
    #toch beter met antialias
    if opts:
        if opts.fontantialias:
            font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        else:
            font.setStyleStrategy(QtGui.QFont.NoAntialias)
    painter.setFont(font)
    painter.setPen(QtGui.QColor('#000000'))
    painter.drawText(int(x),int(y),text)
    painter.setPen(QtCore.Qt.white)
    painter.drawText(int(x-1),int(y-1),text)
    painter.end()
    if opts:
        xpm=convertPixmap(xpm,1,1,opts.saturation,opts.sharp)
    xpm.save(destinationfile)

    return r.width()




#for workspacebuttons, draw the text white with black shadow
def drawTextOnPixmap(text,pixelsize,leftmarginfrac,yoffsetfrac,pixmap,opts=None):
    #font=QtGui.QFont('Lucida Bright') #werkt wel
    #font=QtGui.QFont('DejaVu Serif') #werkt wel
    font=QtGui.QFont(Globals.font) #werkt wel
    #font.setStyleName('Book') #doet niks. andere keer uitzoeken
    font.setStyleName(Globals.fontStyle) #doet niks. andere keer uitzoeken
    font.setPixelSize (pixelsize)
    spacing=1
    font.setLetterSpacing(QtGui.QFont.PercentageSpacing,spacing*100)
    #font=QtGui.QFont('Helvetica')
    fm=QtGui.QFontMetrics(font)
    r=fm.boundingRect(text)
    #xpm=QtGui.QPixmap(r.width(),r.height())
    #c = QtGui.QColor(0)
    #c.setAlpha(0)
    #xpm.fill(c)
    #for some reason the string is in the negative half plane so pull it down
    wp=pixmap.size().width()
    hp=pixmap.size().height()
    wt=r.width()
    ht=r.height()
    xt=-r.x()
    yt=-r.y()

    x=xt+leftmarginfrac*wp
    y=yt+(hp-ht)/2+yoffsetfrac*hp

    #dyn=(h-hpn)/2.0+h*yoffsetfrac
    painter = JosQPainter(pixmap)
    painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
    #if Globals.smoothTransform:
    #20221109
    painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
    painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
    #BIG NOTE:
        #these antialias etc functions also take into account the font settings
        #in qt5c / fonts.conf of qt. So even if I set 'preferantialias' here
        #then if in fonts.conf is set 'noantialias' , there is NO ANTIALIAS.
        #!!!^#&^@#@#@ WAS ZUM FUCK. 3 HOUERZE LETEEERE
    if opts:
        if opts.fontantialias:
            font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        else:
            font.setStyleStrategy(QtGui.QFont.NoAntialias)
    painter.setFont(font)
    painter.setPen(QtGui.QColor('#111111'))
    painter.drawText(int(x),int(y),text)
    painter.setPen(QtCore.Qt.white)
    painter.drawText(int(x-1),int(y-1),text)
    painter.end()



#take python 
def replaceColors(colors,xpm1):
    rows=len(colors)
    xpm=list(xpm1) #make a copy of the list and make replacements in that, return that
    for row in range(rows):
        colorname=colors[row][0]
        colorval=colors[row][1]
        for j in range(len(xpm)):
            if re.search(colorname,xpm[j]):
                xpm[j]=re.sub('#(?:[0-9a-fA-F]{3}){1,2}',colorval,xpm[j]) #take xpm[j] and replace colorname with colorval and return string
    return xpm


#copy icon to cache dir and (attempt to) cde-ify it. return full path of cached 1996-style icon
# genicon96
#filename has full path...............newfilename in cache
def copyToCacheAndGenCdeIcon(filename,newfilename=None):
        print('processing icon '+filename)

        basename=os.path.basename(filename)
        if newfilename:
            basename=newfilename
        basenamenoext, file_extension = os.path.splitext(basename)
        fullname=os.path.normpath(os.path.join(Globals.cache,basenamenoext))+'.png'
        #20221114 reworked 1996-style icon generator
        #tried to do everyting in a single convert command using -write mpr:cachfile but that
        #didn't work entirely. so still use a few separate convert commands '


        #                       suffix prefix
        tmpdir=tempfile.mkdtemp('','cdemotif')
        #shutil.rmtree(tmpdir)

        iconsmall=os.path.normpath(os.path.join(tmpdir,'iconsmall.png'))
        alpha=os.path.normpath(os.path.join(tmpdir,'alpha.png'))
        edgebw=os.path.normpath(os.path.join(tmpdir,'edgebw.png'))

        #/b/iconcdescript
        #alternatieven
        #convert {iconsmall} {edgebw} -composite -ordered-dither o4x4,3 {fullname}
        #convert {iconsmall} {edgebw} -composite -ordered-dither h4x4a,4 {fullname}
        #convert {iconsmall} {edgebw} -composite -dither None -remap /tmp/colortable.gif {fullname}
        #convert {iconsmall} {edgebw} -composite -posterize 4 {fullname}
        #convert {iconsmall} {edgebw} -composite -posterize 5 -ordered-dither o4x4,4 {fullname}
        #convert {iconsmall} {edgebw} -composite -posterize 5 -ordered-dither o8x8,3 {fullname}
        #convert {iconsmall} {edgebw} -composite -posterize 5 -ordered-dither h4x4a,3 {fullname}
        #convert {iconsmall} -posterize 5 -ordered-dither o8x8,3  {iconsmall}
        #convert {iconsmall} -posterize 8 -dither FloydSteinberg -colors 8  {iconsmall}
        #convert {iconsmall} -posterize 8 -ordered-dither o8x8,3  {iconsmall}
        #OMG SVGS 20221109
        #imagemagic convert doesnt work with pyinstaller due to mixed libraries on
        #different sys.  so first convert to png using qt...  
        #but pixmap doesnt work because not allowed to use outside gui thread (so not in
        #backgroudn icon cache thread)
        #tmppixmap=QtGui.QPixmap(filename)
        #tmppixmap=tmppixmap.scaled(48,48)
        #tmppixmap.save(iconsmall)
        #tmppixmap.save(Globals.tmpdir+'/'+basenamenoext+'.png')
        #this does work for svg conv so first conv to png, and do the rest with convert
        #20221127 CAN GO NOW: hierx
        img = QtGui.QImage()
        img.load(filename)
        img.save(iconsmall)
        img.save(tmpdir+'/'+basenamenoext+'.png')
        black='black'
        white='white'
        #external command 'convert' i could not get to work in pyinstaller package so
        #have to use libraries not from 'imei' directory but from native system. in som
        #systems it is /usr/lib, in others /lib, so just use root /

        #20221129 hierx put cmdWithPrependedLD in separate file/also find etc
        convert="convert "

        #in im6/7 range of 'threshold' is reversed so patch...
        threshold=80
        if Globals.convertversion>6:
            threshold=20

        infile=iconsmall
        outfile=fullname
        black='black'
        white='white'
        sharpen="""  -sharpen 0x1.5""".format(**locals())
        iconsize=44
        infileresized=tmpdir+'/100.infileresized.tmp.png'
        alpha=tmpdir+'/200.alpharesized.tmp.png'
        dither=tmpdir+'/250.dither.tmp.png'
        posterize=tmpdir+'/260.posterize.tmp.png'
        tone=tmpdir+'/270.tone.tmp.png'
        edge=tmpdir+'/300.edge.tmp.png'
        edget=tmpdir+'/300.edget.tmp.png'
        edgetn=tmpdir+'/300.edgetn.tmp.png'
        edgebw=tmpdir+'/400.edgebw.tmp.png'
        edgebwgray=tmpdir+'/420.edgebwgray.tmp.png'
        mask=tmpdir+'/450.mask.tmp.png'
        transparent=tmpdir+'/460.transparent.tmp.png'
        beveledic=tmpdir+'/470.beveledic.tmp.png'
        if Globals.convertversion>0:
            cmd="""
            #resize to fit front panel at default size (then there is no scaling, so crisp)
            {convert} {infile} -resize {iconsize} {sharpen} {infileresized}

            #put on 48^2 canvas transparent
            {convert}  -size 48x48 xc:transparent {infileresized} -gravity Center -composite {infileresized}

            #extract alpha 
            #in im6/7 range of 'threshold' is reversed so patch...
            {convert} {infileresized} -channel alpha -threshold {threshold}% +channel -alpha extract {alpha}

            #for 'cde-izing' create posterized and dithered version
            {convert} {infileresized} -posterize 8 {posterize}
            {convert} {posterize} -dither FloydSteinberg -colors 8  {dither}

            #make a bit lighter to match original cde icons on front panel
            {convert} {dither} -auto-level -gamma 1.1 -brightness-contrast 0x0 {tone}

            #grow the edge of the alpha channel, basis for a sunken bevel, a white and black one
            {convert} {alpha} -morphology edgeout diamond:1:1 -threshold 90% {edge}
            {convert} {edge} -transparent {black} {edget}
            {convert} {edget} -channel RGB -negate {edgetn}

            #dark bevel at left top, light bevel bottom right
            {convert} {edgetn} -channel RGB -sparse-color voronoi "%[fx:(w-h)/2],%[fx:(h-w)/2] {black} %[fx:(w+h)/2],%[fx:(h+w)/2] {white}" -colorspace RGB {edgebw}

            #dim down the white and black->grey
            {convert} {edgebw} -fill '#ffffff' -opaque white -fill '#444444' -opaque black {edgebwgray}

            #put bevel around scaled icon
            {convert} {tone} -alpha set -background none -channel A -evaluate multiply 0.65 +channel {edgebwgray} -composite {beveledic}

            #transparent version of posterized icon, to put over dithered one (dither is too apparent)
            {convert} {posterize} -channel a -evaluate multiply 0.7 +channel {posterize}

            # put posterize over heavy dither to loose
            {convert} {beveledic} -gravity Center  {posterize} -composite {outfile}

            """.format(**locals())
        else:
            #if convert not on system just copy
            cmd="""
            cp {infile} {outfile}
            """.format(**locals())
        (stdout,stderr)=execWSysLibsNonBlckStdOE(cmd)
        print(stdout)
        print(stderr)
        shutil.rmtree(tmpdir)
        return fullname

def copyToCache(filename,newfilename=None):
        basename=os.path.basename(filename)
        if newfilename:
            basename=newfilename
        basenamenoext, file_extension = os.path.splitext(basename)
        fullname=os.path.normpath(os.path.join(Globals.cache,basenamenoext))+'.png'
        cmd=("""cp {filename} {fullname} """.format(**locals()))
        (stdout,stderr)=execWSysLibsNonBlckStdOE(cmd)
        return fullname



#xpm / png dond treally need separate cmd call todo. later.. later..
def findIconFromName1(name, default_icon=None):
    """
    Find an icon by name with multiple fallback mechanisms.
    
    Args:
        name: Name of the icon to find
        default_icon: Default icon path to return if not found (defaults to Globals.defaultxpm)
        
    Returns:
        Path to the icon file or default icon if not found
    """
    if default_icon is None:
        default_icon = getattr(Globals, 'defaultxpm', None) or platform_utils.get_default_icon_fallback()
    
    # If no name provided, return default icon
    if not name:
        print(f"No icon name provided, using default icon: {default_icon}")
        return default_icon
        
    print(f'\nLooking for icon: {name}...')
    
    def log_warning(message):
        print(f"WARNING: {message}")
        
    def log_debug(message):
        if getattr(Globals, 'debug_icons', False):
            print(f"DEBUG: {message}")

    def is_raster_icon(path):
        """Check if path exists and is a raster image QPixmap can load (not SVG)"""
        if not path or not os.path.isfile(path):
            return False
        if path.lower().endswith('.svg') or path.lower().endswith('.svgz'):
            return False
        return True

    def make_loadable_icon(path):
        if not path or not os.path.isfile(path):
            return None
        if is_raster_icon(path):
            return path
        if path.lower().endswith('.svg') or path.lower().endswith('.svgz'):
            try:
                cached_name = os.path.splitext(os.path.basename(path))[0] + '.png'
                converted = copyToCacheAndGenCdeIcon(path, cached_name)
                if converted and os.path.isfile(converted):
                    log_debug(f"Converted SVG icon to cached PNG: {converted}")
                    return converted
            except Exception as e:
                log_warning(f"SVG icon conversion failed for {path}: {e}")
        return None

    # Check if it's already a valid file path'
    if is_raster_icon(name):
        log_debug(f"Found icon at path: {name}")
        return name
        
    # Try xdg icon theme lookup
    try:
        from xdg import IconTheme
        icon_path = IconTheme.getIconPath(name, 48)
        loadable_icon = make_loadable_icon(icon_path)
        if loadable_icon:
            log_debug(f"Found icon in XDG theme: {loadable_icon}")
            return loadable_icon
        if icon_path and not is_raster_icon(icon_path):
            for size in [32, 64, 24, 96, 128, 256]:
                icon_path = IconTheme.getIconPath(name, size)
                loadable_icon = make_loadable_icon(icon_path)
                if loadable_icon:
                    log_debug(f"Found icon in XDG theme at size {size}: {loadable_icon}")
                    return loadable_icon
    except Exception as e:
        log_warning(f"XDG icon lookup failed for {name}: {e}")
    
    # Try common system icon locations
    _share = platform_utils.get_system_share()
    _pixmaps = platform_utils.get_pixmaps_dir()
    _local_share = os.path.expanduser('~/.local/share')
    _xpmdir = getattr(Globals, 'xpmdir', '')
    common_icon_paths = [
        os.path.join(_xpmdir, name),
        os.path.join(_xpmdir, f"{name}.png"),
        os.path.join(_xpmdir, f"{name}.xpm"),
        os.path.join(_local_share, 'icons', 'hicolor', '48x48', 'apps', name),
        os.path.join(_local_share, 'icons', 'hicolor', '48x48', 'apps', f"{name}.png"),
        os.path.join(_local_share, 'icons', 'hicolor', '48x48', 'apps', f"{name}.xpm"),
        os.path.join(_local_share, 'pixmaps', name),
        os.path.join(_local_share, 'pixmaps', f"{name}.png"),
        os.path.join(_local_share, 'pixmaps', f"{name}.xpm"),
        f"{_share}/icons/hicolor/48x48/apps/{name}.png",
        f"{_share}/icons/hicolor/48x48/apps/{name}",
        f"{_share}/icons/gnome/48x48/apps/{name}.png",
        f"{_share}/icons/gnome/48x48/apps/{name}",
        f"{_pixmaps}/{name}.png",
        f"{_pixmaps}/{name}.xpm",
        f"{_pixmaps}/{name}"
    ]
    
    for path in common_icon_paths:
        if is_raster_icon(path):
            log_debug(f"Found icon in common location: {path}")
            return path
    
    # Try with different extensions
    for ext in ['', '.png', '.xpm', '.xbm']:
        test_path = f"{_share}/icons/hicolor/48x48/apps/{name}{ext}"
        if is_raster_icon(test_path):
            log_debug(f"Found icon with extension {ext}: {test_path}")
            return test_path
    
    additional_paths = []
    if _xpmdir:
        additional_paths.append(_xpmdir)
    additional_paths.extend([
        os.path.join(_local_share, 'icons'),
        os.path.join(_local_share, 'pixmaps'),
    ])
    additional_paths.extend(platform_utils.get_icon_search_paths())

    seen_paths = set()
    wanted_names = {
        name.lower(),
        f"{name.lower()}.png",
        f"{name.lower()}.xpm",
        f"{name.lower()}.xbm",
        f"{name.lower()}.svg",
        f"{name.lower()}.svgz",
    }
    for base_path in additional_paths:
        if not base_path or base_path in seen_paths:
            continue
        seen_paths.add(base_path)
        if not os.path.isdir(base_path):
            continue
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.lower() in wanted_names:
                    found_path = os.path.normpath(os.path.join(root, file))
                    loadable_icon = make_loadable_icon(found_path)
                    if loadable_icon:
                        log_debug(f"Found icon in recursive search: {loadable_icon}")
                        return loadable_icon

    log_warning(f"Icon not found: {name}, using default icon: {default_icon}")
    return default_icon

    # This function is now handled by the new implementation above
    # Keeping this comment to maintain context
    #remove ugly ones
    sysicondirs = [x for x in sysicondirs if not re.search(r'HighContrast', x)]
    #search these first
    icondirsfirst=[Globals.xpmdir] + platform_utils.get_icon_dirs() 
    #on mx the icon firefox is nowhere in /usr/share/icons except in the eye wateringly ugly HighContrast. So include /usr/share/pixmaps in path
    #icondirsfirst=[] 
    #hmmon debian stable HighContrast is about the only one available. Do this better hwo???????????????
    #doe die als laatste nog een keer
    icondirs=icondirsfirst+sysicondirs
    pixmapdir=platform_utils.get_pixmaps_dir()

    extensions=['png', 'xpm', 'svg'] 

    #20221106 now icons are sometimes listed, Icon=org.xfce.terminal 
    #without extension, but with dots! so only remove image extensions
    basenameext=os.path.basename(name)
    basename=re.sub(".png|.xpm|.svg|.jpg|.PNG|.XPM|.SVG|.JPG", "", basenameext)

    #check if basename.png is in cache (if not all icons will be put there, png later)
    cachedicon=os.path.normpath(os.path.join(Globals.cache,basename+'.png'))
    if os.path.isfile(cachedicon):
        print('Icon found in cache '+cachedicon)
        return cachedicon

    #ICON WITH A FULL PATH GIVEN  (because somtimes the icon is not in /usr/share/icons)
    if not os.path.basename(name)==name: #has full path-check
        if os.path.isfile(name): 
            print('Icon with full path found, copying to cache'+name)
            cachediconwithpath=copyToCacheAndGenCdeIcon(name)
            return cachediconwithpath
        else: 
            #misschien gewoon doorgaan
            err(name)
            return Globals.defaultxpm

    print('SEARCHING FOR ICON '+name)

    #ICON NAME WITHOUT PATH GIVEN
    #in case given without extension: search for basename*, with ext: basenameext* also ok
    #but in the first case, basenameext=basename so search for basenameext* in both cases


    #look in my own xpm dir, these are not modified dither etc
    b = Globals.xpmdir
    cmd = f'find "{b}" -name "{basenameext}*" -print'
    (stdout, stderr) = execWSysLibsNonBlckStdOE(cmd)
    if stdout:
        l = stdout.splitlines()
        #c = Globals.cache
        print(f'found icon {l[0]}')
        #cachediconwithpath = copyToCacheAndGenCdeIcon(l[0], f'{basename}.png')
        cachediconwithpath = copyToCache(l[0], f'{basename}.png')
        return cachediconwithpath

    #more extensive search and copy to cache if found #always QUOTE globs in 'find' statements WHY #in som icon dirs it is not
    #48x48 so grep only 48 #20221108 moet zijn eerst basename, dan evt die naar cache copieren anders basename * voor alternatief
    #maar dan basenamen aar cache clop
    print('MORE EXTENSIVE SEARCH...')
    print('looking for icon in system icon dirs...')
    for b in icondirs:
        #uitgaan van een grotere levert een beter resultaat voor kleine icon na omlaag schalen
        #cmd=("""find {b} -name "{basenameext}*" -print|grep -E '64|72|96|128|256|scalable'""".format(**locals()))
        cmd=("""find {b} -name "{basenameext}*" -print|grep -E '96|128|256|scalable'""".format(**locals()))
        (stdout,stderr)=execWSysLibsNonBlckStdOE(cmd)
        if stdout:
            l=stdout.splitlines()
            #c=Globals.cache
            if os.path.isfile(l[0]):
                print('found icon  '+l[0])
                cachediconwithpath=copyToCacheAndGenCdeIcon(l[0],basename+'.png')
                return cachediconwithpath
        #put in on efunc, larger ones first
    print('Trying smaller one...')
    for b in icondirs:
        cmd=("""find {b} -name "{basenameext}*" -print|grep -E '48|64'""".format(**locals()))
        (stdout,stderr)=execWSysLibsNonBlckStdOE(cmd)
        if stdout:
            l=stdout.splitlines()
            #c=Globals.cache
            if os.path.isfile(l[0]):
                print('found icon  '+l[0])
                cachediconwithpath=copyToCacheAndGenCdeIcon(l[0],basename+'.png')
                return cachediconwithpath
    print('nope...')
    # Search in additional system locations, a last resort
    additional_paths = platform_utils.get_icon_search_paths()
    
    for base_path in additional_paths:
        if not os.path.isdir(base_path):
            continue
            
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.lower() == name.lower() or file.lower() == f"{name.lower()}.png" or file.lower() == f"{name.lower()}.xpm":
                    found_path = os.path.normpath(os.path.join(root, file))
                    log_debug(f"Found icon in additional location: {found_path}")
                    return found_path
    print('looking in pixmap dir')
    cmd=("""find {pixmapdir} -name "{basenameext}*" -print""".format(**locals()))
    (stdout,stderr)=execWSysLibsNonBlckStdOE(cmd)
    if stdout:
        l=stdout.splitlines()
        #c=Globals.cache
        if os.path.isfile(l[0]):
            print('found icon  '+l[0])
            cachediconwithpath=copyToCacheAndGenCdeIcon(l[0],basename+'.png')
            return cachediconwithpath

    #search everything. maybe step through result with 'identify' later
    print('NOTHING... search the entire system now using locate...')
    if which('locate'):
        for e in extensions: #here we need grep of extensions, because non img results are also in the 'locate' 
            cmd=("""locate {basenameext}|grep icon|grep -i {e}""".format(**locals()))
            (stdout,stderr)=execWSysLibsNonBlckStdOE(cmd)
            if stdout:
                l=stdout.splitlines()
                #c=Globals.cache
                ####this search original eg 'xterm' couldnt be found, so maybe chooses 'xterm-color.png'
                ####so for quick, make copy of that with name xterm in cache
                ####or make cache 'xterm_alt.png' and then check next time also for filname'_alt' or something
                ####.... later later leave for now 
                ####BUT then create 'xterm' to cache directory, not 'xterm-color', otherwise it will next
                ####time also not find it...
                if os.path.isfile(l[0]):
                    print("""ICON {name} NOT FOUND SO USING ALTERNATIVE {l[0]} INSTEAD. PLS CHECK """.format(**locals()))
                    cachediconwithpath=copyToCacheAndGenCdeIcon(l[0],basename+'.png')
                    return cachediconwithpath

    highcontrastdir=os.path.join(platform_utils.get_system_share(), 'icons', 'HighContrast')
    print('looking in the eye wateringly ugly HighContrast directory, a last resort.')
    cmd=("""find {highcontrastdir} -name "{basenameext}*" -print""".format(**locals()))
    (stdout,stderr)=execWSysLibsNonBlckStdOE(cmd)
    if stdout:
        l=stdout.splitlines()
        #c=Globals.cache
        if os.path.isfile(l[0]):
            print('found icon  '+l[0])
            cachediconwithpath=copyToCacheAndGenCdeIcon(l[0],basename+'.png')
            return cachediconwithpath

    #finally, give up
    err(name)
    cachediconwithpath=copyToCacheAndGenCdeIcon(Globals.defaultxpm,basename+'.png')
    return cachediconwithpath

def which(program):
    path_ext = [""];
    ext_list = None

    if sys.platform == "win32":
        ext_list = [ext.lower() for ext in os.environ["PATHEXT"].split(";")]

    def is_exe(fpath):
        exe = os.path.isfile(fpath) and os.access(fpath, os.X_OK)
        # search for executable under windows
        if not exe:
            if ext_list:
                for ext in ext_list:
                    exe_path = "{}{}".format(fpath,ext)
                    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                        path_ext[0] = ext
                        return True
                return False
        return exe

    fpath, fname = os.path.split(program)

    if fpath:
        if is_exe(program):
            return "{}{}".format(program, path_ext[0])
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.normpath(os.path.join(path, program))
            if is_exe(exe_file):
                return "{}{}".format(exe_file, path_ext[0])
    return None


    #def function_that_downloads(my_args):
    #import threading
    #def my_inline_function(some_args):
        # do some stuff
        #download_thread = threading.Thread(target=function_that_downloads, name="Downloader", args=some_args)
        #download_thread.start()

# cde-ize and cache drawer icons in advance
# called in separate thread from main program
def cacheIcons():

    #wait a bit
    print('CACHING ICONS...')
    print('CACHING ICONS...')
    print('CACHING ICONS...')
    print('CACHING ICONS...')
    print('CACHING ICONS...')
    print('CACHING ICONS...')
    print('CACHING ICONS...')

    drawerdir=Globals.drawerdir
    print(drawerdir)
    cmd="""
    grep desktop {drawerdir}/*
    """.format(**locals())
    (stdout,stderr)=execWSysLibsNonBlckStdOE(cmd)

    for desktopfile in stdout.splitlines():
        desktopfile=re.sub('^.*:',"",desktopfile)
        d=DesktopEntry.DesktopEntry(desktopfile)
        iconnamenoext=d.getIcon()
        print('\n\nFind icon for combobutton '+iconnamenoext)
        icon=findIconFromName1(iconnamenoext)

    return None



if __name__ == '__main__':

    #8 or reduced 4 color palette
    #colors=readMotifColors('4','Broica.dp')
    #colors=readMotifColors('8','Broica.dp')


    #xpm=extractXpm('xpm/launcher.xpm')
    #xpm1=replaceColors(colors,xpm)

    #app = QtCore.QApplication(sys.argv)
    #window = QtGui.QMainWindow()

    #pic = QtGui.QLabel(window)

    #########################
    #pixmap=QtGui.QPixmap(xpm) #the original one
    #pixmap=QtGui.QPixmap(xpm1) #the replaced one
    #########################

    #pic.setPixmap(pixmap)
    #pic.resize(200,100)

    #for testing
    Globals.cache='/x/pycde/scaletest/cdepanel/cache'
    Globals.defaultxpm='/x/pycde/scaletest/cdepanel/xpm/empty.xpm'
    Globals.xpmdir='/x/pycde/scaletest/cdepanel/xpm'

    ##################################################
    #print(findIconFromName1('mozilla.xpm'))
    #print(findIconFromName1('xterm'))
    #print(findIconFromName1('firefox.png'))
    #print(findIconFromName1('org.xfce.terminal'))
    #print(findIconFromName1(''))
    #print(findIconFromName1(None))
    #print(findIconFromName1('/x/pycde/scaletest/cdepanel/xpm/terminal.xpm'))
    #print(findIconFromName1('/x/ycde/scaletest/cdepanel/xpm/txxxxeminal.xpm'))

    ##################################################
    #app = QtCore.QApplication(sys.argv)
    #p=QtGui.QPixmap('xpm/pager-button-1.xpm')
    #textIconSameSizeAsFile(p,'/tmp/testicon.png','My Text')
    #print('done')
    #sys.exit(app.exec_())
    ##################################################






    app = QtWidgets.QApplication(sys.argv)

    ###########################3
    #print(createTextIcon('/tmp/testicon.png','M111yTExxxxxxxxxxxxxxxXT 123'))
    print('done')

    ###########################3
    #pixmap=QtGui.QPixmap('/tmp/testpagerbutton2.png')
    #drawTextOnPixmap('Hello',14,.1,0.05,pixmap)
    #pixmap.save('/tmp/1.png')
    
    sys.exit()

    sys.exit(app.exec_())


    #window.show()
    #sys.exit(app.exec_())
