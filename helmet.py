# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'helmet.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1169, 745)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.DetectPicture = QtWidgets.QPushButton(self.centralwidget)
        self.DetectPicture.setGeometry(QtCore.QRect(30, 350, 91, 51))
        self.DetectPicture.setObjectName("DetectPicture")
        self.show_label = QtWidgets.QLabel(self.centralwidget)
        self.show_label.setGeometry(QtCore.QRect(190, 30, 951, 671))
        self.show_label.setText("")
        self.show_label.setScaledContents(True)
        pixmap = QPixmap('./000.jpg')
        self.show_label.setPixmap(pixmap)
        self.show_label.setObjectName("show_label")
        self.Read = QtWidgets.QPushButton(self.centralwidget)
        self.Read.setGeometry(QtCore.QRect(30, 90, 91, 51))
        self.Read.setObjectName("Read")
        self.StartDetect = QtWidgets.QPushButton(self.centralwidget)
        self.StartDetect.setGeometry(QtCore.QRect(30, 220, 91, 51))
        self.StartDetect.setObjectName("StartDetect")
        self.DetectVideo = QtWidgets.QPushButton(self.centralwidget)
        self.DetectVideo.setGeometry(QtCore.QRect(30, 480, 91, 51))
        self.DetectVideo.setObjectName("DetectVideo")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.DetectPicture.setText(_translate("MainWindow", "检测图片"))
        self.Read.setText(_translate("MainWindow", "读入图片或视频"))
        self.StartDetect.setText(_translate("MainWindow", "开始检测"))
        self.DetectVideo.setText(_translate("MainWindow", "检测视频"))

