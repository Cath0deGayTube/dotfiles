# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_Help.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(510, 489)
        self.helpText = QtWidgets.QPlainTextEdit(Dialog)
        self.helpText.setGeometry(QtCore.QRect(20, 20, 461, 391))
        self.helpText.setObjectName(_fromUtf8("helpText"))
        self.openSettings = QtWidgets.QPushButton(Dialog)
        self.openSettings.setGeometry(QtCore.QRect(20, 430, 151, 41))
        self.openSettings.setObjectName(_fromUtf8("openSettings"))
        self.closeHelp = QtWidgets.QPushButton(Dialog)
        self.closeHelp.setGeometry(QtCore.QRect(350, 430, 131, 41))
        self.closeHelp.setObjectName(_fromUtf8("closeHelp"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.openSettings.setText(_translate("Dialog", "Open Settings", None))
        self.closeHelp.setText(_translate("Dialog", "Close", None))

