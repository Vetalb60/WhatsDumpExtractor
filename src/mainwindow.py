# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuRun = QtWidgets.QMenu(self.menubar)
        self.menuRun.setObjectName("menuRun")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionDecrypt = QtWidgets.QAction(MainWindow)
        self.actionDecrypt.setObjectName("actionDecrypt")
        self.actionExtract_demo = QtWidgets.QAction(MainWindow)
        self.actionExtract_demo.setObjectName("actionExtract_demo")
        self.actionNew_Dump = QtWidgets.QAction(MainWindow)
        self.actionNew_Dump.setObjectName("actionNew_Dump")
        self.actionShow_logs = QtWidgets.QAction(MainWindow)
        self.actionShow_logs.setObjectName("actionShow_logs")
        self.actionAVD_State = QtWidgets.QAction(MainWindow)
        self.actionAVD_State.setObjectName("actionAVD_State")
        self.actionInstall_SDK = QtWidgets.QAction(MainWindow)
        self.actionInstall_SDK.setObjectName("actionInstall_SDK")
        self.actionHelp = QtWidgets.QAction(MainWindow)
        self.actionHelp.setObjectName("actionHelp")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionConvert_to_html = QtWidgets.QAction(MainWindow)
        self.actionConvert_to_html.setObjectName("actionConvert_to_html")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionDecrypt)
        self.menuFile.addAction(self.actionConvert_to_html)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuRun.addAction(self.actionNew_Dump)
        self.menuRun.addAction(self.actionShow_logs)
        self.menuTools.addAction(self.actionAVD_State)
        self.menuTools.addAction(self.actionInstall_SDK)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuRun.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuRun.setTitle(_translate("MainWindow", "Run"))
        self.menuTools.setTitle(_translate("MainWindow", "SDK"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionDecrypt.setText(_translate("MainWindow", "Decrypt"))
        self.actionExtract_demo.setText(_translate("MainWindow", "Extract(demo)"))
        self.actionNew_Dump.setText(_translate("MainWindow", "New Dump"))
        self.actionShow_logs.setText(_translate("MainWindow", "Show logs"))
        self.actionAVD_State.setText(_translate("MainWindow", "AVD State"))
        self.actionInstall_SDK.setText(_translate("MainWindow", "Install SDK"))
        self.actionHelp.setText(_translate("MainWindow", "Help"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionConvert_to_html.setText(_translate("MainWindow", "Convert to html"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
