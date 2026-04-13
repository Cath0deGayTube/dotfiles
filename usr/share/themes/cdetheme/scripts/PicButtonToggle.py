import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PicButton import PicButton
from JosQPainter import JosQPainter
import Globals
#!/usr/bin/python3
# -*- coding: utf-8 -*-
#normalbutton with 2 images met ff standaardimag voor test
#zie ComboButton.py

#used for drawer buttons and, base for other buttons
class PicButtonToggle(PicButton):
   def __init__(self, filebgtag, filebgpressedtag, fileicon, htop, parent):
      super(PicButtonToggle, self).__init__(filebgtag, filebgpressedtag, fileicon, htop, parent)
      self.setAutoExclusive(False)
      self.setCheckable(True)
      self.drawerfile=''#hack
   def paintEvent(self, event):
       if self.isChecked(): pixbgcur=Globals.IMG[self.filebgpressedtag].img
       else: pixbgcur=Globals.IMG[self.filebgtag].img
       painter = JosQPainter(self)
       #painter.setRenderHint(QtGui.QPainter.Antialiasing)
       painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
       painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
       painter.drawPixmap(event.rect(), pixbgcur)
       #not actually used in the case of drawerbutton, arrow is in the backgroudn image:
       painter.drawPixmapCenter(event.rect(),1, self.imgicon)


class PicButtonWorkspace(PicButton):
   def __init__(self, filebgtag, filebgpressedtag, fileicon, htop, parent):
      super(PicButtonWorkspace, self).__init__(filebgtag, filebgpressedtag, fileicon, htop, parent)
      self.setAutoExclusive(False)
      self.setCheckable(True)
      self.clicked.connect(self.clickTwiceStayDown)
   #make button stay pressed when clicking 2 or more times in a row. Actual state
   #of workspacebuttons is set by updateWorkspaceButtons
   def clickTwiceStayDown(self):
          self.setChecked(True)
   def setWorkspaceNr(self,workspacenr):
       self.workspacenr=workspacenr
   def paintEvent(self, event):
       if self.isChecked(): pixbgcur=Globals.IMG[self.filebgpressedtag].img
       else: pixbgcur=Globals.IMG[self.filebgtag].img
       painter = JosQPainter(self)
       #painter.setRenderHint(QtGui.QPainter.Antialiasing)
       #deze moet uit staan anders wordt alles wazig zelfs indien geen font alasingng
       #of alleen aanzetten indien vergrotinsfactor non integer?
       #eigenaardig: de icons zijn bij schaal 1 niet wazig, de letters wel
       painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform);
       painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
       #is ook wazig een beetje bij schaal 1. maar icons niet (ondanks smooting)
       #wordt opgerekt misschien door verkeerde afmeting?
       painter.drawPixmap(event.rect(), pixbgcur)
       #pixbgcur.save('/tmp/test.png')
       #painter.drawPixmapCenter(event.rect(), self.imgicon)
       #painter.drawPixmapLeft(event.rect(), leftmarginfrac, heightfrac, yoffsetfrac, self.imgicon)
       #waarom deze?:
       #painter.drawPixmapLeft(event.rect(), .1, .45, .05, self.imgicon)
       #painter.drawPixmapCenter(event.rect(), Globals.paneliconsize/61.0, self.imgicon)

 



def main():
    print('MAIN ')
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout(window)
    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)

    #button = PicButtonToggle("launcherbg.xpm","launcherbgpressed.xpm","terminal.xpm")
    #button = PicButtonToggle("xpm/launcher.xpm","xpm/launcher-pressed.xpm","terminal.xpm",Globals.TESTOPTS,window)
    #button = PicButtonWorkspace("xpm/launcher.xpm","xpm/launcher-pressed.xpm","terminal.xpm",Globals.TESTOPTS,window)
    button = PicButtonWorkspace('xpm/pager-button-2.xpm','xpm/pager-button-down-2.xpm',"empty.xpm",Globals.TESTOPTS,window)
    layout.addWidget(button)

    #button.toggle()

    button.setChecked(True)
    button.setChecked(False)

    window.show()
    window.resize(200,200)
    sys.exit(app.exec_())

if __name__ == '__main__':
   main()




