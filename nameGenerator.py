import sys
import os
import zlib
import random
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QComboBox,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QWidget,
)

# set lv1: 0=cn,1=en,2=jp  lv2: cn=([0.female_name][1.male_name][2.family_name][3.neutral_name][4.ancient_name])    en_or_jp=(0=female,1=male,2=family)
namesForGenerate=[[[],[],[],[],[]],[[],[],[]],[[],[],[]]]=[[[],[],[],[],[]],[[],[],[]],[[],[],[]]]
cur_file_dir=os.path.dirname(os.path.realpath(__file__))+os.path.sep
curDataFileName=cur_file_dir+"all_names_data.dat"
curConfigFileName=cur_file_dir+"nameGenerator.cfg"
app=QApplication(sys.argv)

class MainWindow(QWidget):
    cbx_lang=QComboBox()
    rbx_middle=QRadioButton("Middle")
    rbx_male=QRadioButton("Male")
    rbx_female=QRadioButton("Female")
    btn_generate=QPushButton("Loading names data...")
    tbx_result=QTextEdit("")
    btn_exit=QPushButton("Exit")

    def __init__(self, ax=100,ay=100,aw=300,ah=300) -> None:
        super().__init__()
        self.setWindowTitle("Loading data...")
        self.setGeometry(ax,ay,aw,ah)
        self.setWindowIcon(QIcon(cur_file_dir+"8fdfsf.ico"))
        self.cbx_lang.addItem("Chinese")
        self.cbx_lang.addItem("American")
        self.cbx_lang.addItem("Japanese")
        self.cbx_count=QComboBox()
        for n in range(1,11):
            self.cbx_count.addItem(str(n*10),n*10)
        self.btn_generate.setDisabled(True)
        self.btn_generate.clicked.connect(self.clickToGenerateNames)
        self.btn_exit.clicked.connect(self.exitProgram)
        self.tbx_result.setReadOnly(True)
        self.tbx_result.setFontFamily("Tahoma")
        self.tbx_result.setGeometry(0,0,90,90)
        self.tbx_result.setFontPointSize(16)
        self.rbx_middle.setChecked(True)
        self.cbx_lang.setCurrentIndex(0)
        self.cbx_count.setCurrentIndex(0)

        layoutH=QHBoxLayout()
        layoutH.addWidget(self.rbx_middle)
        layoutH.addWidget(self.rbx_male)
        layoutH.addWidget(self.rbx_female)

        layout=QFormLayout()
        layout.addRow("Current Language:",self.cbx_lang)
        layout.addRow("Name count:",self.cbx_count)
        layout.addRow(layoutH)
        layout.addRow(self.btn_generate)
        layout.addRow(self.tbx_result)
        layout.addRow(self.btn_exit)
        self.setLayout(layout)
        self.getConfig()
        random.seed(version=3.2)
    
    def getConfig(self):
        if(os.path.exists(curConfigFileName)):
            with open(curConfigFileName,"r",encoding="utf-8") as f:
                settings=f.read().split('|')
                if(settings.__len__()==7):
                    self.cbx_lang.setCurrentIndex(int(settings[0]))
                    self.cbx_count.setCurrentIndex(int(settings[1]))
                    if(int(settings[2])==0):
                        self.rbx_female.setChecked(True)
                    elif(int(settings[2])==1):
                        self.rbx_male.setChecked(True)
                    else:
                        self.rbx_middle.setChecked(True)
                    self.setGeometry(int(settings[3]),int(settings[4]),int(settings[5]),int(settings[6]))

    # gender female=0,male=1,nogender=2, lan 0=cn,1=en,2=jp
    def clickToGenerateNames(self):
        totalNameGenerated=10

        def getNamesForEnJp():
            result_names=[[],[]]
            result_names[1]=random.choices(namesForGenerate[self.cbx_lang.currentIndex()][2],k=totalNameGenerated)
            if(self.rbx_middle.isChecked()):
                result_names[0]=random.choices(namesForGenerate[self.cbx_lang.currentIndex()][0],k=totalNameGenerated//2)
                result_names[0].extend(random.choices(namesForGenerate[self.cbx_lang.currentIndex()][1],k=totalNameGenerated//2))
            else:
                gd=1
                if(self.rbx_female.isChecked()):
                    gd=0
                result_names[0]=random.choices(namesForGenerate[self.cbx_lang.currentIndex()][gd],k=totalNameGenerated)
            return result_names

        def cn():
            r=""
            if(self.rbx_female.isChecked()):
                r=str(random.choices(namesForGenerate[0][0],k=totalNameGenerated))[1:-1]
            elif(self.rbx_male.isChecked()):
                r=str(random.choices(namesForGenerate[0][1],k=totalNameGenerated))[1:-1]
            else:
                d=random.choices(namesForGenerate[0][3],k=totalNameGenerated//2)
                d.extend(random.choices(namesForGenerate[0][4],k=totalNameGenerated//2))
                r=str(d)[1:-1]
            return r.replace("'","").replace(", ","\t")

        def en():
            names=getNamesForEnJp()
            result=""
            for n in range(totalNameGenerated):
                result+=names[0][n]+" "+ names[1][n]+"\n"
            return result[:-1]

        def jp():
            names=getNamesForEnJp()
            result=""
            for n in range(totalNameGenerated):
                result+=names[1][n]+ names[0][n]+"\t"
            return result[:-1]

        result=""
        totalNameGenerated=self.cbx_count.currentData()
        if(self.cbx_lang.currentIndex()==0):
            result=cn()
        elif(self.cbx_lang.currentIndex()==1):
            result=en()
        else:
            result=jp()
        self.tbx_result.setText(result)


    def exitProgram(self):
        n=2
        if(self.rbx_female.isChecked()):
            n=0
        elif(self.rbx_male.isChecked()):
            n=1
        with open(curConfigFileName,"w",encoding="utf-8") as f:
            f.write(str(self.cbx_lang.currentIndex())+"|"+str(self.cbx_count.currentIndex())+"|"+str(n)+"|"+str(self.frameGeometry().left())+"|"+str(self.frameGeometry().top())+"|"+str(self.frameGeometry().width())+"|"+str(self.frameGeometry().height()))
        sys.exit(0)


ww=MainWindow()

class dataLoadingQThread(QObject):
    finished=pyqtSignal()
    progress=pyqtSignal(int)

    def run(self):
        with open(curDataFileName,"rb") as f:
            global namesForGenerate
            b=f.read()
            self.progress.emit(10)
            b=zlib.decompress(b)
            self.progress.emit(50)
            s=b.decode()
            self.progress.emit(70)
            namesForGenerate=eval(s)
            self.progress.emit(99)
        self.finished.emit()

def showProgress(n):
    ww.setWindowTitle(f"Loading data...{n}%")
    ww.btn_generate.setText(f"Loading names data...{n}%")

def finishedProgress():
    ww.setWindowTitle("Random Names Generator v1.0")
    ww.btn_generate.setDisabled(False)
    ww.btn_generate.setText("Generate Random Names")


ww.show()

loading_data_thread=QThread()
loading_data_worker=dataLoadingQThread()
loading_data_worker.moveToThread(loading_data_thread)
loading_data_thread.started.connect(loading_data_worker.run)
loading_data_worker.finished.connect(loading_data_thread.quit)
loading_data_worker.finished.connect(loading_data_worker.deleteLater)
loading_data_thread.finished.connect(loading_data_thread.deleteLater)
loading_data_worker.progress.connect(showProgress)
loading_data_thread.start()
loading_data_thread.finished.connect(finishedProgress)

sys.exit(app.exec_())