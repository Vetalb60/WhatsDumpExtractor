# -*- coding:utf-8 -*-

'''

=========whatsdumpextractor.py=========

Version 1.0.1

Copyright © 2021 by Alex Green.All rights reserved.

WDE is Open Source Software released under the GNU General Public License.

'''

import sys
import os
import time

from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from whatsdump import Whatsdump
from WhatsAppGDExtract import googleDriveExtractor
from decrypt12 import decryptDataBase
from whatsapp_xtract import whatsapp_xtract
from variables import Variables
from src.mainwindow import Ui_MainWindow
from src.newdump_dialog import Ui_NewDump_Dialog
from src.info_dialog import Ui_Info_Dialog
from functools import partial
from whatsdump import DumpException
from whatsdump import Communicate
from src.code_dialog import Ui_Code_Dialog


class WDE(QtWidgets.QMainWindow,
          Ui_MainWindow,
          QtCore.QThread,
          Variables,):
    def __init__(self,parent = None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.__newDump     = NewDumpDialog()
        self.web           = QWebEngineView()
        self.__variables   = Variables()
        self.communicate   = Communicate()
        self.__codeDialog  = CodeDialog()
        self.signals       = Signals()

        self.setupUi(self)
        self.setCentralWidget(self.web)
        self.setWindowTitle("WDE")
        self.resize(800, 600)
        self.show()

        self.actionConvert_to_html.triggered.connect(self.whatsapp_xtract)
        self.actionShow_logs.triggered.connect(self.show_logs)
        self.actionDecrypt.triggered.connect(self.decryptDataBase)
        self.actionNew_Dump.triggered.connect(self.newDump_open)
        self.actionAVD_State.triggered.connect(self.whatsdump_check)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionExit.triggered.connect(self.close)
        self.actionExit.triggered.connect(self.deleteLater)
        self.actionInstall_SDK.triggered.connect(partial(self.functions_in_thread,self.install_sdk))
        self.actionHelp.triggered.connect(partial(self.loadWebView,self.__variables.getHelpDocument()))
        self.actionAbout.triggered.connect(partial(self.setInfoText,__ABOUT_DESCRIPTION__))
        self.__newDump.button_ok.clicked.connect(partial(self.functions_in_thread,self.whatsdump_run))
        self.__newDump.button_cancel.clicked.connect(self.__newDump.close)
        self.__newDump.button_ok.clicked.connect(self.__newDump.close)
        self.communicate.setStatusBar.connect(partial(self.setStatus,self.__variables.getStatusBar))
        self.communicate.setCode.connect(self.openCodeDialog)
        self.__codeDialog.enter_button.clicked.connect(partial(self.__variables.setVerifyCode,self.__codeDialog.lineEdit.text))
        self.signals.loadHtml.connect(self.loadWebView)
        self.signals.enableMenuBar.connect(self.enableMenuBar)
        self.signals.end_animate.connect(partial(self.__variables.setLoading,False))
        self.signals.showInfoDialog.connect(self.setInfoText)

    def decryptDataBase(self):
        try:
            self.__variables.setMsgstorePath(QtWidgets.QFileDialog.getOpenFileName(self,
                                                                                 'Open file',
                                                                                 '/home',
                                                                                 'Crypt files (*.crypt12)')[0])
            self.__variables.setKeyPath(QtWidgets.QFileDialog.getOpenFileName     (self,
                                                                                 'Open file',
                                                                                 '/home',
                                                                                 'Key (*)')[0])
            self.__variables.setDstPath(QtWidgets.QFileDialog.getSaveFileName     (self,
                                                                                 'Save as',
                                                                                 '/home',
                                                                                 'Database (*.db)')[0])
            self.setInfoText(decryptDataBase(self.__variables.getKeyPath(),
                                                           self.__variables.getMsgstorePath(),
                                                           self.__variables.getDstPath()))
        except BaseException as e:
            self.setInfoText(e)
        except:
            self.setInfoText('Cannot decrypt file!')

    def whatsapp_xtract(self):
        try:
            self.__variables.setdbPath(QtWidgets.QFileDialog.getOpenFileName(self,
                                                                       'Open file',
                                                                       '/home',
                                                                       'Database (*.db)')[0])
            whatsapp_xtract([self.__variables.getdbPath()])
        except FileNotFoundError:
            self.setInfoText("Warning:File not found.")

    def functions_in_thread(self,target):
        self.thread = SlotsThread(target, self.signals, self.__variables)
        self.thread.start()
        self.thread.finished.connect(self.thread.quit)

    # Shows the loading animation.Not used yet
    def animate_in_thread(self):
        self.animation_thread = AnimateThread(self.animate, self.signals, self.__variables)
        self.animation_thread.start()
        self.animation_thread.finished.connect(self.animation_thread.quit)

    def whatsdump_run(self):

        self.__variables.setPhone(self.__newDump.lineEdit_phone.text())
        self.__variables.setGmail(self.__newDump.lineEdit_gmail.text())
        self.__variables.setPassword(self.__newDump.lineEdit_pass.text())

        self.__newDump.clearLineEdit()

        self.statusbar.showMessage("Download database from Google Drive...")

        googleDriveExtractor(self.__variables.getGmail(),
                             self.__variables.getPassword(),
                             self.__variables.getAndroidId())

        Whatsdump(argv = ['--wa-phone','+' + self.__variables.getPhone(),'--wa-verify', self.__variables.getVerifyType()],
                  variables = self.__variables,communicate = self.communicate)

        self.__variables.setDstPath(os.path.join(os.path.abspath("output"), self.__variables.getPhone()))
        self.__variables.setKeyPath(''.join((self.__variables.getDstPath(),'\\key')))
        self.__variables.setMsgstorePath(''.join((self.__variables.getDstPath(),'\\files\\Databases\\msgstore.db.crypt12')))
        self.__variables.setdbPath(''.join((self.__variables.getDstPath(),'\\', self.__variables.getPhone(),'.db')))

        decryptDataBase(self.__variables.getKeyPath(),
                        self.__variables.getMsgstorePath(),
                        self.__variables.getdbPath())

        whatsapp_xtract([self.__variables.getdbPath()])

        self.__variables.setHtmlPath(''.join((self.__variables.getdbPath(),'.html')))

        os.replace(self.__variables.getHtmlPath(),''.join((os.path.abspath(''),'\\',self.__variables.getPhone(),'.db.html')))
        self.__variables.setHtmlPath(''.join((os.path.abspath('') ,'\\',self.__variables.getPhone(),'.db.html')))

        self.signals.loadHtml.emit(self.__variables.getHtmlPath().replace('\\', '/'))

    def whatsdump_check(self):
        try:
            Whatsdump(argv = ['--check-sdk'],
                      variables = self.__variables,
                      communicate = self.communicate)
        except BaseException as e:
            self.setInfoText(e)
        except DumpException as e:
            self.setInfoText(e)

    def setStatus(self,status):
        self.statusbar.showMessage(status())

    def open_file(self):
        try:
            self.__variables.setHtmlPath(QtWidgets.QFileDialog.getOpenFileName(self,
                                                                             'Open file',
                                                                             '/home',
                                                                             'HTML Files (*.html)')[0])
            self.signals.loadHtml.emit(self.__variables.getHtmlPath())
        except BaseException as e:
            self.setInfoText(e)
        except:
            self.setInfoText("Error!Cannot open file!")

    def newDump_open(self):
        self.__newDump.open()

    def openCodeDialog(self):
        self.__codeDialog.show()

    def show_logs(self):
        if self.__variables.getPhone() :
            try:
                self.__variables.setDstPath(os.path.join(os.path.abspath("output"), self.__variables.getPhone()))
                self.signals.loadHtml.emit(''.join((self.__variables.getDstPath(),'\\log.txt')).replace('\\', '/'))
            except BaseException as e:
                self.setInfoText(e)
        else:
            self.setInfoText('Cannot find logs!')


    def install_sdk(self):
        Whatsdump(argv = ['--install-sdk'],variables=self.__variables,communicate=self.communicate)

    def loadWebView(self,path):
        self.web.load(QtCore.QUrl(path))

    def setInfoText(self,text):
        self.__info_dialog = InfoDialog()
        self.__info_dialog.label.setText(str(text))
        self.__info_dialog.show()
        self.__info_dialog.adjustSize()

    def enableMenuBar(self, flag):
        self.menuFile.setEnabled(flag)
        self.menuRun.setEnabled(flag)
        self.menuTools.setEnabled(flag)
        self.menuHelp.setEnabled(flag)

    def deleteThread(self):
        self.thread.deleteLater()

    def closeEvent(self,event):
        self.deleteLater()
        event.accept()

    def animate(self):
        while self.__variables.getLoading() == True:
            self.statusbar.showMessage('\rloading |')
            time.sleep(0.1)
            self.statusbar.showMessage('\rloading /')
            time.sleep(0.1)
            self.statusbar.showMessage('\rloading -')
            time.sleep(0.1)
            self.statusbar.showMessage('\rloading \\')
            time.sleep(0.1)

        self.statusbar.showMessage('\rDone!')
        self.__variables.setLoading(True)


class SlotsThread(QtCore.QThread):
    def __init__(self, target,signals,variables):
        QtCore.QThread.__init__(self)
        self.__variables = variables
        self.__info_dialog = InfoDialog()
        self.__target = target
        self.signals = signals

    def run(self):
        try:
            self.signals.enableMenuBar.emit(False)
            self.__target()
            self.signals.end_animate.emit()
            self.signals.enableMenuBar.emit(True)
        except BaseException as e:
            self.signals.showInfoDialog.emit(str(e))
            self.signals.enableMenuBar.emit(True)
            self.signals.end_animate.emit()

            self.exit()


class AnimateThread(QtCore.QThread):
    def __init__(self, target,signals,variables):
        QtCore.QThread.__init__(self)
        self.__variables = variables
        self.__info_dialog = InfoDialog()
        self.__target = target
        self.signals = signals

    def run(self):
        try:
            self.__target()
        except BaseException:
            self.signals.end_animate.emit()


class InfoDialog(QtWidgets.QDialog,
                 Ui_Info_Dialog,
                 Variables):
    def __init__(self,parent = None):
        QtWidgets.QDialog.__init__(self,parent)
        self.__variables = Variables()
        self.event = QtGui.QCloseEvent()
        self.setWindowFlag(QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setupUi(self)
        self.__variables.setIconPath('qicon.jpg')
        self.setWindowIcon(QtGui.QIcon(self.__variables.getIconPath()))
        self.label.setWordWrap(True)
        self.setBaseSize(180,70)

        self.cancelButton.clicked.connect(self.close)
        self.cancelButton.clicked.connect(partial(self.closeEvent,self.event))

    def closeEvent(self,event):
        self.deleteLater()
        event.accept()


class CodeDialog(QtWidgets.QDialog,
                 Ui_Code_Dialog,
                 Variables):

    def __init__(self,parent = None):

        QtWidgets.QDialog.__init__(self,parent)
        self.__info_dialog = InfoDialog()

        self.setupUi(self)
        self.setFixedSize(360,115)
        self.lineEdit.setMaxLength(20)
        self.setWindowTitle("Report")
        self.enter_button.clicked.connect(self.checklength)

    def checklength(self):
        if len(self.lineEdit.text()) == 6:
            self.close()
        else:
            self.__info_dialog.setInfoText("Code length must be 6!")

    def clearLineEdit(self):
        self.lineEdit.clear()


class NewDumpDialog(QtWidgets.QDialog,
                    Ui_NewDump_Dialog,
                    Variables):
    def __init__(self,parent = None):
        QtWidgets.QDialog.__init__(self,parent)
        self.variables = Variables()
        self.setupUi(self)
        self.setWindowTitle("Whatsapp New Dump")
        self.setFixedSize(450,180)
        self.lineEdit_phone.setMaxLength(20)
        self.lineEdit_gmail.setMaxLength(40)
        self.lineEdit_pass.setMaxLength(110)
        self.button_cancel.clicked.connect(self.close)
        self.button_ok.clicked.connect(self.close)

    def clearLineEdit(self):
        self.lineEdit_gmail.clear()
        self.lineEdit_pass.clear()
        self.lineEdit_phone.clear()


class Signals(QtCore.QObject,
                  Variables):
    loadHtml = QtCore.pyqtSignal(str)
    enableMenuBar = QtCore.pyqtSignal(bool)
    showInfoDialog = QtCore.pyqtSignal(str)
    start_animate = QtCore.pyqtSignal()
    end_animate = QtCore.pyqtSignal()


def main(argv = None):
    app = QtWidgets.QApplication([])
    WDE()
    sys.exit(app.exec())

__ABOUT_DESCRIPTION__ =\
"""
Version 1.0.1

Copyright © 2021 by Alex Green.
All rights reserved.

WDE is Open Source Software released under the GNU General Public License.
"""