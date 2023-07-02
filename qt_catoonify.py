from PySide2 import QtGui, QtWidgets
from PySide2.QtWidgets import QWidget, QApplication, QMessageBox, QFileDialog, QMainWindow, QDialog, QLabel, \
    QSpacerItem, \
    QSizePolicy
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon
import os, shutil, time
from threading import Thread
from PySide2.QtCore import Qt
from process_image import *
import winsound

CWD = os.getcwd()


class Window(QDialog):

    def __init__(self):
        super().__init__()
        qfile_stats = QFile('./Display/Display.ui')
        qfile_stats.open(QFile.ReadOnly)
        qfile_stats.close()
        self.ui = QUiLoader().load(qfile_stats)
        self.ui.MakeSingleButton.clicked.connect(self.save_single)
        self.ui.MakeMultipleButton.clicked.connect(self.produce_multiple)
        self.ui.InputFileButton.clicked.connect(self.choose_input_address)
        self.ui.OutputFileButton.clicked.connect(self.choose_output_address)

        self.ui.InputPreview = DropArea(self)
        str = "若只需生成单张图片,拖拽.jpg格式原图至此处"
        self.ui.InputPreview.setText(str)
        self.ui.InputPreview.setAlignment(Qt.AlignmentFlag(0x84))
        self.ui.horizontalLayout.addWidget(self.ui.InputPreview)
        InputPreview = QSpacerItem(40, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.ui.horizontalLayout.addItem(InputPreview)

        self.ui.OutputPreview = DropArea(self)
        str = "效果图预览"
        self.ui.OutputPreview.setText(str)
        self.ui.OutputPreview.setAlignment(Qt.AlignmentFlag(0x84))
        self.ui.OutputPreview.setAcceptDrops(False)
        self.ui.horizontalLayout.addWidget(self.ui.OutputPreview)
        OutputPreview = QSpacerItem(40, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.ui.horizontalLayout.addItem(OutputPreview)

    def save_single(self):
        """保存生成的单张图片"""
        Directory = QFileDialog.getExistingDirectory(self.ui, "保存图片")
        if not os.path.exists(Directory):
            QMessageBox.about(self.ui, '提示', '保存图片的文件夹不存在，请检查路径名')
            return
        files = list()
        for file in os.listdir(os.path.join(CWD, 'CurOutput') + "\\"):
            files.append(file)
        shutil.copy(os.path.join(os.path.join(CWD, 'CurOutput'), files[0]), os.path.join(Directory, files[0]))

    def produce_multiple(self):
        """运行程序，批量生成图片"""
        input_dir = self.ui.InputAddress.text()
        output_dir = self.ui.OutputAddress.text()
        if not os.path.exists(input_dir):
            QMessageBox.about(self.ui, '提示', '批量生成的输入文件夹不存在，请检查路径名')
            return
        if not os.path.exists(output_dir):
            QMessageBox.about(self.ui, '提示', '批量生成的输出文件夹不存在，请检查路径名')
            return
        thread2 = Thread(target=generate_image_lock, args=(self, input_dir, output_dir))
        thread2.start()

    def choose_input_address(self):
        """用于批量处理的原始图片的地址"""
        Directory = QFileDialog.getExistingDirectory(self.ui, "")
        self.ui.InputAddress.setText(Directory)

    def choose_output_address(self):
        """用于批量处理的生成图片的地址"""
        Directory = QFileDialog.getExistingDirectory(self.ui, "")
        self.ui.OutputAddress.setText(Directory)

    def make_output_preview(self):
        self.ui.OutputPreview.setText("请稍等,效果预览图加载中...")
        shutil.rmtree(os.path.join(CWD, 'CurOutput'))
        os.mkdir(os.path.join(CWD, 'CurOutput'))
        thread1 = Thread(target=self.draw,
                         args=((os.path.join(CWD, 'CurInput'), os.path.join(CWD, 'CurOutput') + "\\")))
        thread1.start()

    def draw(self, input_dir, output_dir):
        mass_cartoonify(input_dir, output_dir)
        files = list()
        for file in os.listdir(os.path.join(CWD, 'CurOutput') + "\\"):
            files.append(file)
        self.ui.OutputPreview.setPixmap(os.path.join(CWD, 'CurOutput') + "\\" + files[0])


def generate_image_lock(win, input_dir, output_dir):
    win.ui.MakeMultipleButton.setEnabled(False)
    win.ui.MakeMultipleButton.setText('正在批量处理,请稍后..')
    mass_cartoonify(input_dir, output_dir)
    win.ui.MakeMultipleButton.setEnabled(True)
    win.ui.MakeMultipleButton.setText('批量处理')
    winsound.MessageBeep()


class DropArea(QLabel):

    def __init__(self, parent: Window):
        super().__init__(parent)
        self.parent = parent
        self.setAcceptDrops(True)
        self.setFixedSize(500, 500)
        self.setAlignment(Qt.AlignmentFlag(0x84))
        self.setScaledContents(True)
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setStyleSheet('border-width: 1px;border-style: solid;border-color: #54687A;')

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = list()
        urls = [u for u in event.mimeData().urls()]
        for url in urls:
            files.append(url.toLocalFile())
        self.setPixmap(files[0])
        shutil.rmtree(os.path.join(CWD, 'CurInput'))
        os.mkdir(os.path.join(CWD, 'CurInput'))
        shutil.copy(files[0], os.path.join(CWD, 'CurInput'))
        self.parent.make_output_preview()


if __name__ == '__main__':
    app = QApplication([])
    Mywindow = Window()
    Mywindow.ui.show()
    app.exec_()
