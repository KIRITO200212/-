from PySide2.QtGui import QImage, QPixmap, QPainter, QFont, QPen, QColor, QFontDatabase

from ui_MainWidnow import Ui_MainWindow
from PySide2.QtWidgets import QWidget, QSizePolicy, QLabel, QApplication, QStyle
from PySide2.QtCore import Qt

from qt_catoonify import Window as CatoonifyWindow
from qt_pencil_sketch import Window as SketchWindow
from qt_swap_face_DL import Window as DLWindow
from qt_swap_face_ML import Window as MLWindow

import os

CWD = os.getcwd()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        icon = QPixmap("./Display/favicon.ico")
        self.setWindowIcon(icon)
        self.setWindowTitle("数字图像处理")

        self.setWindowFlags(Qt.WindowCloseButtonHint)
        background_pixmap = QPixmap("./hello.jpg")  # 设置主界面图片

        self.helloWindow = QLabel("数字图像处理")

        # YanShiYouRanXiaoKai-2.ttf
        font_id = QFontDatabase.addApplicationFont("./YanShiYouRanXiaoKai-2.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        def paintEvent(event):
            painter = QPainter(self.helloWindow)
            painter.setRenderHint(QPainter.Antialiasing)  # 设置抗锯齿渲染
            painter.setFont(QFont(font_family, 64, QFont.Bold))  # 设置字体和大小
            painter.setPen(QPen(QColor("#19232D")))  # 设置画笔颜色
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            scaled_pixmap = background_pixmap.scaled(self.helloWindow.size(), Qt.KeepAspectRatioByExpanding,
                                                     Qt.SmoothTransformation)
            painter.drawPixmap(self.helloWindow.rect(), scaled_pixmap)
            rect = self.helloWindow.rect()
            flags = Qt.AlignCenter
            painter.drawText(rect, flags, "数字图像处理")  # 在指定区域居中绘制文本

        self.helloWindow.paintEvent = paintEvent

        self.catoonifyWindow = CatoonifyWindow()
        self.sketchWindow = SketchWindow()
        self.dlWindow = DLWindow()
        self.mlWindow = MLWindow()

        self.ui.stackedWidget_main.addWidget(self.helloWindow)
        self.helloWindow.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.stackedWidget_main.addWidget(self.catoonifyWindow.ui)
        self.catoonifyWindow.ui.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.stackedWidget_main.addWidget(self.sketchWindow.ui)
        self.sketchWindow.ui.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.stackedWidget_main.addWidget(self.dlWindow.ui)
        self.dlWindow.ui.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ui.stackedWidget_main.addWidget(self.mlWindow.ui)
        self.mlWindow.ui.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        def setCurrentWidget(btn, w):
            self.ui.pushButton_catoonify.setChecked(False)
            self.ui.pushButton_sketch.setChecked(False)
            self.ui.pushButton_DL.setChecked(False)
            self.ui.pushButton_ML.setChecked(False)
            self.ui.stackedWidget_main.setCurrentWidget(w.ui)
            btn.setChecked(True)
            w.ui.show()

        # Connections
        self.ui.pushButton_catoonify.clicked.connect(
            lambda: setCurrentWidget(self.ui.pushButton_catoonify, self.catoonifyWindow))
        self.ui.pushButton_sketch.clicked.connect(
            lambda: setCurrentWidget(self.ui.pushButton_sketch, self.sketchWindow))
        self.ui.pushButton_DL.clicked.connect(
            lambda: setCurrentWidget(self.ui.pushButton_DL, self.dlWindow))
        self.ui.pushButton_ML.clicked.connect(
            lambda: setCurrentWidget(self.ui.pushButton_ML, self.mlWindow))
