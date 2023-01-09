"""
ver 1.1.0 - 20230109
============================================================
                       업데이트 내역
------------------------------------------------------------
ver. 1.1.0 배포 20230109
ver. 1.0.0 Initial Commit 20230109
============================================================
"""

import sys
from webbrowser import open as opn
from os import path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, \
                            QPushButton, QTextBrowser, \
                            QHBoxLayout, QVBoxLayout, \
                            QDesktopWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from pathlib import Path
from utils import *

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
        return path.join(base_path, relative_path)
    except Exception:
        base_path = path.abspath(".")
        return path.join(base_path, relative_path)

class TaskArea(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        ## setting widgets ##
        # hbox_1: buttons
        findBtn = QPushButton(text='find...')
        jsonBtn = QPushButton(text='convert to json')
        listBtn = QPushButton(text='listing')
        helpBtn = QPushButton(text='help')

        # hbox_2: fileNameBox
        fileNameBox = QTextBrowser()

        ## setting style ##
        font_init = findBtn.font()
        font_init.setPointSize(15)
        font_init.setFamilies(['Times New Roman', 'Malgun Gothic'])

        findBtn.setFont(font_init)
        jsonBtn.setFont(font_init)
        listBtn.setFont(font_init)
        helpBtn.setFont(font_init)
        fileNameBox.setFont(font_init)

        ## setting boxes ##
        hbox_1 = QHBoxLayout()
        hbox_1.addWidget(findBtn)
        hbox_1.addWidget(jsonBtn)
        hbox_1.addWidget(listBtn)
        hbox_1.addWidget(helpBtn)

        hbox_2 = QHBoxLayout()
        hbox_2.addWidget(fileNameBox)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_1)
        vbox.addLayout(hbox_2)

        ## get initial UI ##
        self.setLayout(vbox)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        task_area = TaskArea()
        self.setCentralWidget(task_area)
        self.statusBar().showMessage('준비됨')

        """
        0   <PyQt5.QtWidgets.QVBoxLayout object at 0x000002023BCE04C0> vbox
        1   <PyQt5.QtWidgets.QPushButton object at 0x000002023BCE0160> findBtn
        2   <PyQt5.QtWidgets.QPushButton object at 0x000002023BCE01F0> jsonBtn
        3   <PyQt5.QtWidgets.QPushButton object at 0x000002023BCE0280> listBtn
        4   <PyQt5.QtWidgets.QTextBrowser object at 0x000002023BCE0310> fileNameBox
        """
        self.findBtn = self.centralWidget().children()[1]
        self.jsonBtn = self.centralWidget().children()[2]
        self.listBtn = self.centralWidget().children()[3]
        self.helpBtn = self.centralWidget().children()[4]
        self.fileNameBox = self.centralWidget().children()[5]

        ## actions ##
        self.findBtn.clicked.connect(self.fileOpen)
        self.jsonBtn.clicked.connect(self.getJSON)
        self.listBtn.clicked.connect(self.getList)
        self.helpBtn.clicked.connect(lambda: opn('https://github.com/SeHaan/program_TGtoLIST'))

        ## window ##
        self.setWindowTitle("TextGrid to List for ASK-REAL (ver. 1.1.0)")
        self.setWindowIcon(QIcon(resource_path("img\\icon.png")))
        self.resize(1000, 300)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    ## actions ##
    def fileOpen(self):
        self.fileNameBox.clear()
        self.statusBar().showMessage('파일 불러오기...')
        self.files = QFileDialog.getOpenFileNames(self, 'Find file(s)', './') # tuple([file_list], str)
        for file in self.files[0]:
            self.fileNameBox.append(file)

    def getJSON(self):
        try:
            file_len = len(self.files[0])
        except AttributeError:
            self.NoFileWarning()
            return
        else:
            if file_len == 0:
                self.NoFileWarning()
                return
            else:
                task = TextGridJSON()
                self.fileNameBox.append('\n' + '='*30 + str(file_len) + ' JSON file(s)' + '='*30 + '\n')
                for file in self.files[0]: 
                    if str(Path(file).suffix) != '.TextGrid':
                        self.NotTextGridWaring()
                        return
                    else:
                        new_file = file[:-len(Path(file).name)] + str(Path(file).stem)
                        task.tg_to_json(file, new_file)
                        self.fileNameBox.append(new_file + '.json')
                self.CompleteJSON()
                return

    def getList(self):
        try:
            file_len = len(self.files[0])
        except AttributeError:
            self.NoFileWarning()
            return
        else:
            if file_len == 0:
                self.NoFileWarning()
                return
            else:
                task = TextGridJSON()
                self.fileNameBox.append('\n' + '='*30 + str(file_len) + ' List file(s)' + '='*30 + '\n')
                for file in self.files[0]:
                    new_file = file[:-len(Path(file).name)] + str(Path(file).stem)
                    if str(Path(file).suffix) == '.TextGrid' or str(Path(file).suffix) == '.json':
                        if not Path(new_file + '.json').exists():
                            self.NoFileWarning()
                            return
                        else:
                            task.json_to_list(new_file, new_file)                            
                            self.fileNameBox.append(new_file + '.txt')
                    else:
                        self.NoFileWarning()
                        return
                self.CompleteList()
                return

    ## warnings ##
    def NoFileWarning(self):
        self.statusBar().showMessage('오류: 파일 없음')
        msgBox = QMessageBox.critical(self, 'Warning', '오류: 파일이 없습니다')

    def NotTextGridWaring(self):
        self.statusBar().showMessage('오류: 텍스트그리드가 아닌 파일 포함')
        msgBox = QMessageBox.critical(self, 'Warning', '오류: 텍스트그리드가 아닌 파일이 포함되어 있습니다')

    def CompleteJSON(self):
        self.statusBar().showMessage('완료')
        msgBox = QMessageBox.information(self, 'Completed', '완료: 전체 {0}개의 파일을 JSON 포맷으로 변환함'.format(str(len(self.files[0]))))
    
    def CompleteList(self):
        self.statusBar().showMessage('완료')
        msgBox = QMessageBox.information(self, 'Completed', '완료: 전체 {0}개의 파일을 리스트로 변환함'.format(str(len(self.files[0]))))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainApp()
    sys.exit(app.exec_())
