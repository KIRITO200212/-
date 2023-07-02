# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.horizontalLayout = QHBoxLayout(MainWindow)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame = QFrame(MainWindow)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButton_catoonify = QPushButton(self.frame)
        self.pushButton_catoonify.setObjectName(u"pushButton_catoonify")
        font = QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_catoonify.setFont(font)
        self.pushButton_catoonify.setCheckable(True)
        self.pushButton_catoonify.setChecked(False)

        self.verticalLayout.addWidget(self.pushButton_catoonify)

        self.pushButton_sketch = QPushButton(self.frame)
        self.pushButton_sketch.setObjectName(u"pushButton_sketch")
        self.pushButton_sketch.setFont(font)
        self.pushButton_sketch.setCheckable(True)

        self.verticalLayout.addWidget(self.pushButton_sketch)

        self.pushButton_DL = QPushButton(self.frame)
        self.pushButton_DL.setObjectName(u"pushButton_DL")
        self.pushButton_DL.setFont(font)
        self.pushButton_DL.setCheckable(True)

        self.verticalLayout.addWidget(self.pushButton_DL)

        self.pushButton_ML = QPushButton(self.frame)
        self.pushButton_ML.setObjectName(u"pushButton_ML")
        self.pushButton_ML.setFont(font)
        self.pushButton_ML.setCheckable(True)

        self.verticalLayout.addWidget(self.pushButton_ML)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.frame)

        self.stackedWidget_main = QStackedWidget(MainWindow)
        self.stackedWidget_main.setObjectName(u"stackedWidget_main")

        self.horizontalLayout.addWidget(self.stackedWidget_main)

        self.horizontalLayout.setStretch(1, 1)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u56fe\u50cf\u5904\u7406\u5de5\u5177", None))
        self.pushButton_catoonify.setText(QCoreApplication.translate("MainWindow", u"\u5361\u901a\u5316", None))
        self.pushButton_sketch.setText(QCoreApplication.translate("MainWindow", u"\u7d20\u63cf\u5316", None))
        self.pushButton_DL.setText(QCoreApplication.translate("MainWindow", u"\u6362\u8138\uff08DL\uff09", None))
        self.pushButton_ML.setText(QCoreApplication.translate("MainWindow", u"\u6362\u8138\uff08ML\uff09", None))
    # retranslateUi

