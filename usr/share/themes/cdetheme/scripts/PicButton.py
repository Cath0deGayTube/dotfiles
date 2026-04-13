#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import io
from PyQt5 import QtCore, QtGui, QtWidgets
from JosQPainter import JosQPainter
import Globals
from Opts import Opts
from WorkspaceFuncs import purgeBlinkerList

#tags are global resource images from Globals.IMG[tag]
class PicButton(QtWidgets.QAbstractButton):
    def __init__(self, filebgtag, filebgpressedtag, fileicon, opts, parent=None):
        super(PicButton, self).__init__(parent)
        self.filebgtag=filebgtag
        self.filebgpressedtag=filebgpressedtag
        self.isDrawer=False
        self.isLauncher=False
        self.isWorkspaceButton=False
        #global options vor hbox like colors and such
        self.opts=opts
        #remember list of all instances to easy access attr or fun from all instances in one go
        #specifically: used to set transparent/opaque and color all imgbg simultaneously
        self.setFocusPolicy(0);
        #these contain screen grabbed pixmaps form the original cde frontpanel. 
        #store here the unscaled size
        #imgbg is not used only to get the w/h
        #self.imgbg=Globals.IMG[self.filebgtag].img
        #self.w0=self.imgbg.width()
        #self.h0=self.imgbg.height()
        self.w0=Globals.IMG[self.filebgtag].img.width()
        self.h0=Globals.IMG[self.filebgtag].img.height()
        #self.imgbg=None
        self.imgicon = QtGui.QPixmap(fileicon)
        #to make the updated background visible if state changes:
        self.pressed.connect(self.update)
        self.released.connect(self.update)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)   
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #set background color green for pixelgap debugging
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor('green'))
        self.setPalette(palette)
        #if true display display faded icon with double left/right arrows on top
        #used in CdePanel.py moveComboButton
        self.displayArrows=False
        self.arrowspng=QtGui.QPixmap(Globals.configdir+'/arrows.png')
        self.displayAlwaysUp=False
    def paintEvent(self, event):
        if self.isDown() or self.isChecked(): 
            pixbgcur=Globals.IMG[self.filebgpressedtag].img
        else: pixbgcur=Globals.IMG[self.filebgtag].img
        painter = JosQPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing)
        #draw the icon
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.drawPixmap(event.rect(), pixbgcur)
        if not self.imgicon.isNull():
            painter.drawPixmapCenter(event.rect(), Globals.paneliconsize/61.0, self.imgicon)
        if self.displayArrows:
            painter.setOpacity(1)
            painter.drawPixmapCenter(event.rect(), 1, self.arrowspng)
    #some mystery redrawing for some reason need
    def enterEvent(self, event):
        self.update()
    def leaveEvent(self, event):
        self.update()
    #raise panel and drawers when pressed anywhere
    def mousePressEvent(self,event):  
        try: Globals.cdepanel.activateAllWindows()
        except Exception: pass
        super(PicButton, self).mousePressEvent(event)




class PicButtonBlink(PicButton):
    def __init__(self, blinkerList, filebgtag, filebgpressedtag, htop, parent):
        fileicon=''
        super(PicButtonBlink, self).__init__(filebgtag, filebgpressedtag, fileicon, htop, parent)
        self.blinkerList=blinkerList
        self.blinkOn=False

        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.updateBlinker)
        self.timer.start(200)
        self.clicked.connect(purgeBlinkerList)
    #def purgeBlinkerList(self):
        #purgeBlinkerList()
    def updateBlinker(self):
        if len(self.blinkerList)>0:
            if self.blinkOn==True:self.blinkOn=False
            else: self.blinkOn=True
        else:
            self.blinkOn=False
        self.update()
    def paintEvent(self, event):
        if self.isDown() or self.blinkOn: 
            pixbgcur=Globals.IMG[self.filebgpressedtag].img
        else: pixbgcur=Globals.IMG[self.filebgtag].img
        painter = JosQPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing)
        #draw the icon
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.drawPixmap(event.rect(), pixbgcur)
        #painter.drawPixmapCenter(event.rect(), self.imgicon)
    #some mystery redrawing for some reason need

def main():


    defaultopts=Opts()
    defaultopts.currentpalettefile='Broica.dp'
    defaultopts.defaultworkspacecolor=2
    defaultopts.initialheight=85 
    defaultopts.contrast=0
    defaultopts.saturation=100
    defaultopts.sharp=0.1
    defaultopts.ncolors=8
    defaultopts.nworkspaces=6
    defaultopts.workspacecolors=[0, 8, 5, 6, 7, 2, 2, 2, 2, 2, 2]
    defaultopts.workspacelabels=['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven']

    print('MAIN ')
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    #hbox is parented here to 'window'
    #                      V
    #layout = QtGui.QHBoxLayout(window) 
    #layout.setSpacing(0)
    #layout.setMargin(0)

    #unparented button
    button = PicButton("launcher.xpm","launcher-pressed.xpm","terminal.xpm",defaultopts)

    # this func parents button to parent of hbox (='window')
    #layout.addWidget(button) 
    #parent the button otherwise explicit by adding 'window', but then the hbox doesnt work-------------V
    #button = PicButton("xpm/launcher.xpm","xpm/launcher-pressed.xpm","terminal.xpm",Globals.TESTOPTS,window)

    #blinker=0
    #but=PicButtonBlink(blinker,



    window.show()
    window.resize(200,200)
    sys.exit(app.exec_())

if __name__ == '__main__':
   main()




