import qdarkstyle
from PySide2.QtWidgets import QApplication
from MainWindow import MainWindow
import os

CWD = os.getcwd()


def main():
    app = QApplication()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    mainWindow = MainWindow()
    mainWindow.show()
    mainWindow.setFixedSize(mainWindow.size())
    app.exec_()


if __name__ == '__main__':
    main()
