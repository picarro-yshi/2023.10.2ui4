## VOC Automation: Calibration, experiment and calculation
## Yilin Shi | Picarro | last update: 2023.10.1

# ----- constants -------
PORT_IN = 50070  ## backdoor, send data to fitter on analyzer
PORT_OUT = 40060  ## listener, get data from analyzer
ANALYZER_SRC = 'analyze_VOC_broadband'  ## listener data key
MFC_REFRESH_TIME = 2000  # ms
PLOT_REFRESH_TIME = 2000  # ms
DATA_RECEIVE_TIME = 1000  # ms

# ------------

import sys, os
import time

import platform
opsystem = platform.system()  # 'Linux', 'Windows', 'Darwin'
print(opsystem)

# import serial.tools.list_ports as ls
# print([p.device for p in ls.comports()])

from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QGridLayout,
    QToolButton,
    QLabel,
    QComboBox,
    QMessageBox,
    QLineEdit,
    QTextEdit,
    QRadioButton,
    QCheckBox,
    QPushButton,
    QButtonGroup,

)
from pyqtgraph import PlotWidget
import pyqtgraph as pg

import style
from utilities import (
    func_analyzer,
    func_mfc, 
    func_calibration, 
    func_experiment, 
    func_scale,
    load_par,
)


MINUTE = [str(i).zfill(2) for i in range(60)]
HOUR = [str(i).zfill(2) for i in range(24)]
COMBOKEYS = ['partial_fit', 'absorbance', 'model', 'residuals']

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VOC Calibration")

        self.setGeometry(350, 50, 1200, 800)
        if opsystem == 'Darwin':
            self.setMinimumSize(1200, 880)
        elif opsystem == 'Windows':
            self.setFixedSize(1100, 800)
        else:
            self.setMinimumSize(1200, 800)

        self.constants()
        self.timers()
        self.set_window_layout()

            
    def constants(self):
        self.port_in = PORT_IN
        self.port_out = PORT_OUT
        self.analyzer_source = ANALYZER_SRC
        # self.refresh_mfc = MFC_REFRESH_TIME
        # self.refresh_plot = PLOT_REFRESH_TIME
        
    def timers(self):
        self.timer_scale = QTimer()
        self.timer_scale.setInterval(PLOT_REFRESH_TIME)
        self.timer_scale.timeout.connect(lambda: func_scale.scale_plot(self))
        
        self.timer_plot = QTimer()
        self.timer_plot.setInterval(PLOT_REFRESH_TIME)
        self.timer_plot.timeout.connect(lambda: func_experiment.plot_spectrum(self))
        
        self.timer_mfc = QTimer()
        self.timer_mfc.setInterval(MFC_REFRESH_TIME)
        self.timer_mfc.timeout.connect(lambda: func_mfc.sendMFC(self))
        
        self.timer_baseline = QTimer()
        self.timer_baseline.setInterval(600000)  # ms, check baseline every 10 mins
        self.timer_baseline.timeout.connect(lambda: func_experiment.track_baseline1(self))
        
        self.timer_data = QTimer()
        self.timer_data.setInterval(DATA_RECEIVE_TIME)  # data manager
        self.timer_data.timeout.connect(lambda: func_experiment.data_manager(self))
        
        self.timer_auto = QTimer()
        self.timer_auto.setInterval(600000)  # ms, check loss every 10 mins
        self.timer_auto.timeout.connect(lambda: func_experiment.track_loss(self))


    def set_window_layout(self):
        self.mainlayout()
        self.tab1_layout()
        self.tab2_layout()
        self.tab3_layout()

        # load parameters
        load_par.load_tab1(self)
        load_par.get_port(self)
        load_par.load_tab3(self)

    def mainlayout(self):
        mainLayout = QVBoxLayout()
        tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        tabs.addTab(self.tab1, "     ⬥ Experiment Settings     ")
        tabs.addTab(self.tab2, "  ⬥ Spectrum Viewer Real Time  ")
        tabs.addTab(self.tab3, "     ⬥ Hardware Detection      ")
        # self.tab1.setStyleSheet('QTabBar::tab: selected { font-size: 18px; font-family: Courier; }')
        mainLayout.addWidget(tabs)
        self.setLayout(mainLayout)
        self.show()

    def tab1_layout(self):
        mainLayout = QVBoxLayout()
        self.tab1.setLayout(mainLayout)

        topLayout = QHBoxLayout()
        bottomLayout = QHBoxLayout()
        mainLayout.addLayout(topLayout, 30)
        mainLayout.addLayout(bottomLayout, 70)

        self.tab1LogoLayout = QVBoxLayout()  # top left
        self.tab1ScaleLayout = QHBoxLayout()  # scale
        self.tab1SampleLayout = QHBoxLayout()  # Sample
        self.tab1ExperimentLayout = QVBoxLayout()  # Experiment
        self.tab1CalibrationLayout = QVBoxLayout()  # Calibration

        # layout1: top
        self.graphWidget1 = pg.PlotWidget()  # scale
        self.graphWidget1.setBackground("w")
        layout1 = QVBoxLayout()  ## figure here
        layout1.addWidget(self.graphWidget1)
        layout1.setContentsMargins(20, 25, 20, 10)  ##left, top, right, bottom

        box1 = QGroupBox("Weight Viewer Real Time")
        box1.setStyleSheet(style.box1())
        box1.setLayout(layout1)

        topLayout.addLayout(self.tab1LogoLayout, 20)
        topLayout.addWidget(box1, 80)

        # layout2: scale
        box2 = QGroupBox("Scale (Mettler Toledo)")
        box2.setLayout(self.tab1ScaleLayout)
        box2.setStyleSheet(style.box1())
        self.tab1ScaleLayout.setContentsMargins(10, 30, 10, 10)

        # layout3: sample
        box3 = QGroupBox("Sample")
        box3.setLayout(self.tab1SampleLayout)
        box3.setStyleSheet(style.box1())
        self.tab1SampleLayout.setContentsMargins(10, 20, 10, 10)

        # layout4: MFC
        box4 = QGroupBox("Experiment - Mass Flow Control (Alicat)")
        box4.setLayout(self.tab1ExperimentLayout)
        box4.setStyleSheet(style.box1())
        self.tab1ExperimentLayout.setContentsMargins(10, 30, 10, 10)

        # layout5: Calibration
        box5 = QGroupBox("Calibration Data Analysis")
        box5.setLayout(self.tab1CalibrationLayout)
        box5.setStyleSheet(style.box1())
        self.tab1CalibrationLayout.setContentsMargins(10, 30, 10, 10)

        layout2 = QVBoxLayout()
        layout2.addWidget(box2, 25)
        layout2.addWidget(box3, 75)

        bottomLayout.addLayout(layout2, 30)
        bottomLayout.addWidget(box4, 40)
        bottomLayout.addWidget(box5, 30)

        self.createTab1LogoLayout()
        self.createTab1ScaleLayout()
        self.createTab1SampleLayout()
        self.createTab1ExperimentLayout()
        self.createTab1CalibrationLayout()


    def createTab1LogoLayout(self):
        logo = QLabel()
        pixmap = QPixmap('icons/picarro.png')
        logo.setPixmap(
            pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version = QLabel('Yilin Shi | Version 4.0 | Fall 2023 | Santa Clara, CA    ')
        if opsystem == 'Darwin':
            vfont = 10
        elif opsystem == 'Windows':
            vfont = 8
        else:
            vfont = 10
        version.setFont(QFont('Arial', vfont))
        version.setAlignment(Qt.AlignmentFlag.AlignRight)

        # label0 = QLabel('Select data key for plot:')
        # self.datakeyCombobox = QComboBox(self)
        # label0 = QLabel("Data key for plot:")
        # layout_key = QHBoxLayout()

        self.plotCheckbox = QCheckBox("Plot data key:")
        self.plotCheckbox.setChecked(True)
        self.plotCheckbox.setToolTip('Check if you want tab2 plot to start.')
        self.datakeyLabel = QLabel("broadband_gasConcs_[CID]")
        self.tab1Layout1Hint = QLabel()
        layout0 = QHBoxLayout()

        # button_key = QPushButton()
        # layout_key.addWidget(self.datakeyLabel)
        # layout_key.addWidget(button_key)

        self.tab1LogoLayout.addWidget(logo)
        self.tab1LogoLayout.addWidget(version)
        self.tab1LogoLayout.addWidget(self.plotCheckbox)
        self.tab1LogoLayout.addWidget(self.datakeyLabel)
        self.tab1LogoLayout.addLayout(layout0)
        self.tab1LogoLayout.addWidget(self.tab1Layout1Hint)

        # layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()
        layout4 = QVBoxLayout()

        # layout0.addLayout(layout1)
        # layout0.addStretch()
        layout0.addLayout(layout2)
        layout0.addStretch()
        layout0.addLayout(layout3)
        layout0.addStretch()
        layout0.addLayout(layout4)

        # button1 = QToolButton()
        # button1.setIcon(QIcon("icons/list2.png"))
        # button1.setIconSize(QSize(40, 40))
        # button1.setToolTip("Get data key of current sample for plot.")
        # # button1.clicked.connect(self.get_key)
        # button1.clicked.connect(lambda: func_experiment.update_key(self))
        # label1 = QLabel('Update Key')
        # 
        # layout1.addWidget(button1)
        # layout1.addWidget(label1)

        self.sendMFCButton = QToolButton()
        self.sendMFCButton.setIcon(QIcon("icons/arrow.png"))
        self.sendMFCButton.setIconSize(QSize(40, 40))
        self.sendMFCButton.setToolTip("Send MFC data to the analyzer\nso it will show up in the\n"
                                      "'Data Key' of the analyzer GUI\nSelect MFC2 before click it.")
        # self.sendMFCButton.clicked.connect(self.send_MFC_data)
        self.sendMFCButton.clicked.connect(lambda: func_mfc.send_MFC_data(self))
        label2 = QLabel('Send MFC')

        layout2.addWidget(self.sendMFCButton)
        layout2.addWidget(label2)

        self.stopSendMFCButton = QToolButton()
        self.stopSendMFCButton.setIcon(QIcon("icons/stop2.jpg"))
        self.stopSendMFCButton.setIconSize(QSize(40, 40))
        self.stopSendMFCButton.setToolTip("Stop sending MFC data to the analyzer")
        # self.stopSendMFCButton.clicked.connect(self.stop_send_MFC_data)
        self.stopSendMFCButton.clicked.connect(lambda: func_mfc.stop_send_MFC_data(self))
        self.stopSendMFCButton.setEnabled(False)
        label3 = QLabel('Stop Send MFC')

        layout3.addWidget(self.stopSendMFCButton)
        layout3.addWidget(label3)

        button2 = QToolButton()
        button2.setIcon(QIcon("icons/stop.png"))
        button2.setIconSize(QSize(40, 40))
        button2.setToolTip("Close VOC Calibration GUI Window")
        button2.clicked.connect(self.exitFunc)
        label4 = QLabel('  Close')

        layout4.addWidget(button2)
        layout4.addWidget(label4)

    def createTab1ScaleLayout(self):
        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        gap = QLabel("  ")
        self.tab1ScaleLayout.addLayout(layout1, 48)
        self.tab1ScaleLayout.addWidget(gap, 2)
        self.tab1ScaleLayout.addLayout(layout2, 50)

        layout11 = QHBoxLayout()
        layout12 = QHBoxLayout()
        layout1.addLayout(layout11)
        layout1.addLayout(layout12)

        # left part
        self.weightLabel = QLabel("0.00000")
        self.weightLabel.setFont(QFont('Times', 24))
        self.weightLabel.setStyleSheet("background-color: white")
        self.weightLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label1 = QLabel("g  ")

        layout11.addWidget(self.weightLabel, 90)
        layout11.addWidget(label1, 10)

        label2 = QLabel("Time (sec):")
        self.scaleTimeLineEdit = QLineEdit('180')
        self.scaleTimeLineEdit.setToolTip("Weigh sample for a time (in seconds).")
        self.scaleTimeLineEdit.setStyleSheet(style.grey1())

        layout12.addWidget(label2)
        layout12.addWidget(self.scaleTimeLineEdit)

        # right part
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()
        layout2.addLayout(layout3)
        layout2.addLayout(layout4)

        layout5 = QVBoxLayout()
        layout6 = QVBoxLayout()
        layout3.addLayout(layout5)
        layout3.addLayout(layout6)

        self.scaleStartButton = QToolButton()
        self.scaleStartButton.setIcon(QIcon("icons/start1.png"))
        self.scaleStartButton.setIconSize(QSize(40, 40))
        self.scaleStartButton.setToolTip("Continuously measure and plot weight for a time")
        self.scaleStartButton.clicked.connect(lambda: func_scale.scale_reading(self))
        label5 = QLabel('   Start')

        layout5.addWidget(self.scaleStartButton)
        layout5.addWidget(label5)

        button2 = QToolButton()
        button2.setIcon(QIcon("icons/weigh5.png"))
        button2.setIconSize(QSize(40, 40))
        button2.setToolTip("Get current weight measurement")
        button2.clicked.connect(lambda: func_scale.scale_weigh(self))
        label6 = QLabel('  Weigh')

        layout6.addWidget(button2)
        layout6.addWidget(label6)

        label3 = QLabel("Reading: ")
        self.ScaleRealTimeLabel = QLabel("                 ")
        self.ScaleRealTimeLabel.setStyleSheet(style.grey1())
        # self.ScaleRealTimeLabel.setWordWrap(True)
        layout4.addWidget(label3)
        layout4.addWidget(self.ScaleRealTimeLabel)


    def createTab1SampleLayout(self):
        grid = QGridLayout()  # 4 columns grid
        self.tab1SampleLayout.addLayout(grid)

        label1 = QLabel("R drive\nlocation")
        label2 = QLabel("Sample")
        label3 = QLabel("CID")
        self.weightTitleLabel = QLabel("Weight (g)")
        label5 = QLabel("Molecular Weight")
        label6 = QLabel("Baseline+n*σ (1 - 5)")
        self.tankTitleLabel = QLabel("Tank conc (ppm)")
        self.tankTitleLabel.setDisabled(True)

        self.sampleRDriveLineEdit = QTextEdit()
        self.sampleRDriveLineEdit.setFixedHeight(60)  ## box won't expand!

        self.sampleNameLineEdit = QLineEdit()  # '176 - Acetic Acid'
        self.sampleCIDLineEdit = QLineEdit()  # '176'
        self.sampleWeightLineEdit = QLineEdit()  # weight '0.0090'
        self.sampleMWLineEdit = QLineEdit()  # MW '60.052'

        self.sampleSigmaCombobox = QComboBox()  # zero 2 < zero1 + pct*sigma
        self.sampleSigmaCombobox.addItems(["4", "1", "2", "3", "5", "6", "8", "10"])
        self.sampleSigmaCombobox.setToolTip('When baseline after the peak is n*σ \n'
                            'higher than the baseline before the peak,\n'
                            'end the experiment.')

        self.sampleTankConcLineEdit = QLineEdit()
        self.sampleTankConcLineEdit.setToolTip('Gas tank concentration, ppm\nfound on tank label.')
        self.sampleTankConcLineEdit.setDisabled(True)

        grid.addWidget(label1, 0, 0, 1, 1)  # R drive
        grid.addWidget(self.sampleRDriveLineEdit, 0, 1, 1, 3)
        grid.addWidget(label2, 1, 0, 1, 1)
        grid.addWidget(self.sampleNameLineEdit, 1, 1, 1, 3)  # '176 - Acetic Acid'
        grid.addWidget(label3, 3, 0, 1, 2)
        grid.addWidget(self.sampleCIDLineEdit, 3, 2, 1, 2)  # '176'

        grid.addWidget(self.weightTitleLabel, 4, 0, 1, 2)  # weight
        grid.addWidget(self.sampleWeightLineEdit, 4, 2, 1, 2)  # weight
        grid.addWidget(label5, 5, 0, 1, 2)  # MW
        grid.addWidget(self.sampleMWLineEdit, 5, 2, 1, 2)  # MW
        grid.addWidget(label6, 6, 0, 1, 2)  # sigma
        grid.addWidget(self.sampleSigmaCombobox, 6, 2, 1, 2)  # sigma
        grid.addWidget(self.tankTitleLabel, 7, 0, 1, 2)  # tank conc
        grid.addWidget(self.sampleTankConcLineEdit, 7, 2, 1, 2)  # tank conc


    def createTab1ExperimentLayout(self):
        layout1 = QHBoxLayout()  # droplet or gas
        self.MFCLayout = QHBoxLayout()  # MFC
        self.timeLayout = QHBoxLayout()  # time
        self.tab1ExperimentHint = QLabel(' \n ')
        self.tab1ExperimentHint.setStyleSheet(style.grey1())

        self.tab1ExperimentLayout.addLayout(layout1)
        self.tab1ExperimentLayout.addStretch()
        self.tab1ExperimentLayout.addLayout(self.MFCLayout)
        self.tab1ExperimentLayout.addStretch()
        self.tab1ExperimentLayout.addLayout(self.timeLayout)
        self.tab1ExperimentLayout.addStretch()
        self.tab1ExperimentLayout.addWidget(self.tab1ExperimentHint)

        # droplet or tank
        self.dropletRadioButton = QRadioButton("Droplet Test", self)
        self.tankRadioButton = QRadioButton("Gas Tank Test", self)
        self.dropletRadioButton.setChecked(True)  ## follow immediate after all radiobutton, otherwise python clapse
        self.dropletRadioButton.setStyleSheet('color: red')
        self.tankRadioButton.setStyleSheet('color: black')

        self.dropletRadioButton.toggled.connect(lambda: func_experiment.choose_droplet(self))
        self.tankRadioButton.toggled.connect(lambda: func_experiment.choose_tank(self))

        self.bg1 = QButtonGroup()
        self.bg1.addButton(self.dropletRadioButton)
        self.bg1.addButton(self.tankRadioButton)

        self.aqCheckbox = QCheckBox("(aq)")
        self.aqCheckbox.setToolTip('Check if this is an aqueous droplet')

        # create experiment
        self.tab1CreateExpButton = QPushButton("Create Exp.", self)
        # self.tab1CreateExpButton.clicked.connect(self.create_experiment)
        self.tab1CreateExpButton.clicked.connect(lambda: func_experiment.create_experiment(self))
        self.tab1CreateExpButton.setStyleSheet("font: bold")
        self.tab1CreateExpButton.setToolTip("Create a folder named with today's date\n"
                            "+suffix (if needed) on the R drive,\n"
                            "for a new experiment and store parameters.")

        layout1.addWidget(self.dropletRadioButton)
        layout1.addWidget(self.aqCheckbox)
        layout1.addWidget(self.tankRadioButton)
        layout1.addWidget(self.tab1CreateExpButton)

        # self.tab1AbandonExpButton = QPushButton("Abandon Current Exp.", self)
        # self.tab1AbandonExpButton.clicked.connect(self.tab1_terminate_exp)
        # self.tab1AbandonExpButton.setStyleSheet("font: bold")
        # self.tab1AbandonExpButton.setToolTip("Abandon current experiment without saving data.\n")
        # self.tab1AbandonExpButton.setEnabled(False)
        #
        # layout2.addWidget(self.tab1CreateExpButton)
        # layout2.addWidget(self.tab1AbandonExpButton)

        self.createTab1MFCLayout()
        self.createTab1TimeLayout()

    def createTab1MFCLayout(self):
        grid = QGridLayout()
        self.MFCLayout.addLayout(grid)

        label1 = QLabel("Pressure (psi)")
        self.tab1PressureLabel = QLabel(" ")
        self.tab1PressureLabel.setStyleSheet(style.grey1())
        self.tab1PressureLabel.setFixedWidth(70)
        # gap = QLabel()

        label2 = QLabel("Temperature (°C)")
        self.tab1TempLabel = QLabel()
        self.tab1TempLabel.setStyleSheet(style.grey1())

        label3 = QLabel("MFC1 (1 SLPM)")
        self.tab1MFC1Label = QLabel("     ")
        self.tab1MFC1Label.setStyleSheet(style.grey1())
        self.tab1MFC1Label.setFixedWidth(70)
        self.tab1MFC1LineEdit = QLineEdit('0.95')
        self.tab1MFC1Label.setToolTip('Dilution line\n1 SLPM Alicat')
        self.tab1MFC1Button = QPushButton("  Set  ")
        # self.tab1MFC1Button.clicked.connect(self.set_mfc_1slpm)
        self.tab1MFC1Button.clicked.connect(lambda: func_mfc.set_mfc_1slpm(self))

        self.mfc100RadioButton = QRadioButton("MFC2 (100 SCCM)", self)
        self.mfc100RadioButton.setToolTip("valve mask 0\n! Please set up manually on analyzer")
        self.mfc10RadioButton = QRadioButton("MFC2 (10 SCCM)", self)
        self.mfc10RadioButton.setToolTip("valve mask 1\n! Please set up manually on analyzer")
        self.mfc100RadioButton.setChecked(True)

        self.mfc100RadioButton.toggled.connect(lambda: func_mfc.choose_100sccm(self))
        self.mfc10RadioButton.toggled.connect(lambda: func_mfc.choose_10sccm(self))

        self.bg2 = QButtonGroup()
        self.bg2.addButton(self.mfc100RadioButton)
        self.bg2.addButton(self.mfc10RadioButton)

        self.tab1MFC100Label = QLabel(" ")
        self.tab1MFC100Label.setStyleSheet(style.grey1())
        self.tab1MFC100Label.setFixedWidth(70)

        self.tab1MFC100Combobox = QComboBox()
        self.tab1MFC100Combobox.addItems(["50", "5", "10", "20", "40", "60", "80", "100"])
        self.tab1MFC100Combobox.setEditable(True)
        self.tab1MFC100Combobox.setToolTip('Bubble line\n100 SCCM Alicat')

        self.tab1MFC100Button = QPushButton("  Set  ", self)
        self.tab1MFC100Button.setStyleSheet("font: bold")
        # self.tab1MFC100Button.clicked.connect(self.set_mfc_100sccm)
        self.tab1MFC100Button.clicked.connect(lambda: func_mfc.set_mfc_100sccm(self))

        # label5 = QLabel("MFC2 (10 SCCM)")
        self.tab1MFC10Label = QLabel(" ")
        self.tab1MFC10Label.setStyleSheet(style.grey1())
        self.tab1MFC10Label.setFixedWidth(70)

        self.tab1MFC10Combobox = QComboBox()
        self.tab1MFC10Combobox.addItems(["1", "0.1", "0.2", "0.5", "2", "5", "10"])
        self.tab1MFC10Combobox.setEditable(True)
        self.tab1MFC10Combobox.setToolTip('Bubble line\n10 SCCM Alicat')

        self.tab1MFC10Button = QPushButton("  Set  ", self)
        self.tab1MFC10Button.setStyleSheet("font: bold")
        # self.tab1MFC10Button.clicked.connect(self.set_mfc_10sccm)
        self.tab1MFC10Button.clicked.connect(lambda: func_mfc.set_mfc_10sccm(self))

        func_mfc.choose_100sccm(self)

        self.automationCheckbox = QCheckBox("Automate the experiment.")
        self.automationCheckbox.setToolTip('Check if you want to set the flows automatically.')
        self.mfcHintLabel = QLabel()
        # self.mfcHintLabel.setStyleSheet(style.grey1())

        grid.addWidget(label1, 0, 0)
        grid.addWidget(self.tab1PressureLabel, 0, 1)
        # grid.addWidget(gap, 0, 2)
        grid.addWidget(label2, 0, 3)
        grid.addWidget(self.tab1TempLabel, 0, 4)

        grid.addWidget(label3, 1, 0)
        grid.addWidget(self.tab1MFC1Label, 1, 1)
        grid.addWidget(self.tab1MFC1LineEdit, 1, 3)
        grid.addWidget(self.tab1MFC1Button, 1, 4)

        # grid.addWidget(label4, 3, 0)
        grid.addWidget(self.mfc100RadioButton, 2, 0)
        grid.addWidget(self.tab1MFC100Label, 2, 1)
        grid.addWidget(self.tab1MFC100Combobox, 2, 3)
        grid.addWidget(self.tab1MFC100Button, 2, 4)

        # grid.addWidget(label5, 4, 0)
        grid.addWidget(self.mfc10RadioButton, 3, 0)
        grid.addWidget(self.tab1MFC10Label, 3, 1)
        grid.addWidget(self.tab1MFC10Combobox, 3, 3)
        grid.addWidget(self.tab1MFC10Button, 3, 4)

        grid.addWidget(self.automationCheckbox, 4, 0, 1, 2)
        grid.addWidget(self.mfcHintLabel, 4, 3, 1, 2)


    # 4 round buttons
    def createTab1TimeLayout(self):
        box1 = QGroupBox()
        box2 = QGroupBox()
        box3 = QGroupBox()
        box4 = QGroupBox()

        self.timeLayout.addWidget(box1)
        self.timeLayout.addWidget(box2)
        self.timeLayout.addWidget(box3)
        self.timeLayout.addWidget(box4)

        box1.setStyleSheet(style.box2())
        box2.setStyleSheet(style.box3())
        box3.setStyleSheet(style.box2())
        box4.setStyleSheet(style.box2())

        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()
        layout4 = QVBoxLayout()

        layout1.setContentsMargins(1, 1, 1, 1)
        layout2.setContentsMargins(1, 1, 1, 1)
        layout3.setContentsMargins(1, 1, 1, 1)
        layout4.setContentsMargins(1, 1, 1, 1)

        box1.setLayout(layout1)
        box2.setLayout(layout2)
        box3.setLayout(layout3)
        box4.setLayout(layout4)

        # box1
        self.expStartButton = QToolButton()
        self.expStartButton.setIcon(QIcon("icons/start1.png"))
        self.expStartButton.setIconSize(QSize(40, 40))
        self.expStartButton.clicked.connect(lambda: func_experiment.start_exp(self))
        self.expStartButton.setEnabled(False)
        label1 = QLabel('Start Exp.')
        label1.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.expStartLineEdit = QLineEdit('')  # 20220222' start
        self.expStartLineEdit.setToolTip('Experiment start date.\n(Used as folder name)\nFormat: yyyymmdd.')
        self.expStartCombobox1 = QComboBox()  # '08'
        self.expStartCombobox1.addItems(HOUR)
        self.expStartCombobox2 = QComboBox()  # '11'
        self.expStartCombobox2.addItems(MINUTE)

        layout1.addWidget(self.expStartButton)
        layout1.addWidget(label1)
        layout1.addWidget(self.expStartLineEdit)
        layout1.addWidget(self.expStartCombobox1)
        layout1.addWidget(self.expStartCombobox2)
        layout1.addStretch()

        # box 2
        self.mfcStopButton = QToolButton()
        self.mfcStopButton.setIcon(QIcon("icons/zero.png"))
        self.mfcStopButton.setIconSize(QSize(40, 40))
        self.mfcStopButton.setToolTip("Stop Alicat flow.")
        self.mfcStopButton.clicked.connect(lambda: func_mfc.stop_flow(self))
        label2 = QLabel('Stop Flow')
        label2.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.expSuffix = QLineEdit('')  # '' suffix
        self.expSuffix.setToolTip('(Optional) Add a suffix to\nthe start date as the folder name.')
        label20 = QLabel("  (suffix)")

        layout2.addWidget(self.mfcStopButton)
        layout2.addWidget(label2)
        layout2.addWidget(self.expSuffix)
        layout2.addWidget(label20)
        layout2.addStretch()

        # box3
        self.expAddButton = QToolButton()
        self.expAddButton.setIcon(QIcon("icons/droplet2.png"))
        self.expAddButton.setIconSize(QSize(40, 40))
        # self.expAddButton.clicked.connect(self.add_sample)
        self.expAddButton.clicked.connect(lambda: func_experiment.add_sample(self))
        self.expAddButton.setEnabled(False)
        label3 = QLabel('Add Sample')
        label3.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.expAddLineEdit = QLineEdit('')  # 20220222' add
        self.expAddLineEdit.setToolTip('Date when sample is added.\nFormat: yyyymmdd')
        self.expAddCombobox1 = QComboBox()  # '09'
        self.expAddCombobox1.addItems(HOUR)
        self.expAddCombobox2 = QComboBox()  # '11'
        self.expAddCombobox2.addItems(MINUTE)

        layout3.addWidget(self.expAddButton)
        layout3.addWidget(label3)
        layout3.addWidget(self.expAddLineEdit)
        layout3.addWidget(self.expAddCombobox1)
        layout3.addWidget(self.expAddCombobox2)
        layout3.addStretch()

        # box4
        self.expEndButton = QToolButton()
        self.expEndButton.setIcon(QIcon("icons/stop1.png"))
        self.expEndButton.setIconSize(QSize(40, 40))
        self.expEndButton.setToolTip("End this experiment.\n"
                                     "Record current time or\n your input time as the end time.\n\n"
                                     "All parameters will be saved again.\n"
                                     "(make changes as needed before click this button).")
        self.expEndButton.clicked.connect(lambda: func_experiment.end_exp(self))
        self.expEndButton.setEnabled(False)
        label4 = QLabel('End Exp.')
        label4.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.expEndLineEdit = QLineEdit('')  # 20220222' end
        self.expEndLineEdit.setToolTip('Date when experiment ends.\nFormat: yyyymmdd')
        self.expEndCombobox1 = QComboBox()  # '23'
        self.expEndCombobox1.addItems(HOUR)
        self.expEndCombobox2 = QComboBox()  # '59'
        self.expEndCombobox2.addItems(MINUTE)

        layout4.addWidget(self.expEndButton)
        layout4.addWidget(label4)
        layout4.addWidget(self.expEndLineEdit)
        layout4.addWidget(self.expEndCombobox1)
        layout4.addWidget(self.expEndCombobox2)
        layout4.addStretch()


    def createTab1CalibrationLayout(self):
        layoutTop = QVBoxLayout()
        layoutBtm = QVBoxLayout()
        self.tab1CalibrationLayout.addLayout(layoutTop)
        self.tab1CalibrationLayout.addLayout(layoutBtm)

        # step 1: calibration factor
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout_calbutton = QHBoxLayout()
        self.tab1CalHintLabel = QLabel(" ")
        self.tab1CalHintLabel.setStyleSheet(style.grey1())
        self.tab1CalHintLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        layoutTop.addLayout(layout1)
        layoutTop.addLayout(layout2)
        layoutTop.addLayout(layout3)
        layoutTop.addLayout(layout_calbutton)
        layoutTop.addWidget(self.tab1CalHintLabel)

        label1 = QLabel(" Step 1: Calibration Factor")
        label1.setStyleSheet(style.body1())
        self.saveFigCheckbox = QCheckBox("Save Figure")
        self.saveFigCheckbox.setChecked(True)
        layout1.addWidget(label1)
        layout1.addStretch()
        layout1.addWidget(self.saveFigCheckbox)

        label2 = QLabel("Combo Spectrum Keys:")
        self.combo_spectrum_key = QComboBox()
        self.combo_spectrum_key.addItems(COMBOKEYS)
        layout2.addWidget(label2)
        layout2.addWidget(self.combo_spectrum_key)

        label3 = QLabel("Combo Log Row #:")
        self.oneComboNumLineEdit = QLineEdit()
        self.oneComboNumLineEdit.setFixedWidth(50)
        self.oneComboNumLineEdit.setToolTip("Optional, default to 500.\ninteger between 0 and Maximal.")
        label4 = QLabel("Maximal: ")
        self.maxRowLabel = QLabel("     ")

        layout3.addWidget(label3)
        layout3.addWidget(self.oneComboNumLineEdit)
        layout3.addStretch()
        layout3.addWidget(label4)
        layout3.addWidget(self.maxRowLabel)

        layout11 = QVBoxLayout()
        layout12 = QVBoxLayout()
        layout13 = QVBoxLayout()
        layout14 = QVBoxLayout()
        layout_calbutton.addLayout(layout11)
        layout_calbutton.addLayout(layout12)
        layout_calbutton.addLayout(layout13)
        layout_calbutton.addLayout(layout14)

        self.tab1LoadExpButton = QToolButton()
        self.tab1LoadExpButton.setIcon(QIcon("icons/list2.png"))
        self.tab1LoadExpButton.setIconSize(QSize(40, 40))
        self.tab1LoadExpButton.setToolTip("Fill in the start date (+suffix) to \nload parameters for this experiment.")
        self.tab1LoadExpButton.clicked.connect(lambda: func_calibration.load_experiment(self))
        label11 = QLabel('Load Exp.')

        layout11.addWidget(self.tab1LoadExpButton)
        layout11.addWidget(label11)

        self.tab1CalculateButton = QToolButton()
        self.tab1CalculateButton.setIcon(QIcon("icons/start1.png"))
        self.tab1CalculateButton.setIconSize(QSize(40, 40))
        self.tab1CalculateButton.setToolTip("Calculate the Calibration factor.")
        self.tab1CalculateButton.clicked.connect(lambda: func_calibration.calculate(self))
        self.tab1CalculateButton.setEnabled(False)
        label12 = QLabel('Calculate')

        layout12.addWidget(self.tab1CalculateButton)
        layout12.addWidget(label12)

        self.PlotOneComboButton = QToolButton()
        self.PlotOneComboButton.setIcon(QIcon("icons/plot1.png"))
        self.PlotOneComboButton.setIconSize(QSize(40, 40))
        self.PlotOneComboButton.setToolTip("Plot Combo spectrum\nfor a particular row.")
        self.PlotOneComboButton.clicked.connect(lambda: func_calibration.plot_one_combo(self))
        self.PlotOneComboButton.setEnabled(False)
        label13 = QLabel('Plot Combo')

        layout13.addWidget(self.PlotOneComboButton)
        layout13.addWidget(label13)

        self.tab1ClosePlotButton = QToolButton()
        self.tab1ClosePlotButton.setIcon(QIcon("icons/stop.png"))
        self.tab1ClosePlotButton.setIconSize(QSize(40, 40))
        self.tab1ClosePlotButton.setToolTip("Close all calibration factor plots.")
        self.tab1ClosePlotButton.clicked.connect(lambda: func_calibration.close_plot(self))
        self.tab1ClosePlotButton.setEnabled(False)
        label14 = QLabel('Close Plots')

        layout14.addWidget(self.tab1ClosePlotButton)
        layout14.addWidget(label14)

        # self.oneComboButton = QPushButton("  Plot  ", self)
        # self.oneComboButton.clicked.connect(self.plot_one_combo)
        # self.oneComboButton.setEnabled(False)
        # self.oneComboButton.setStyleSheet("font: bold")

        # step 2
        layout4 = QHBoxLayout()
        grid = QGridLayout()
        self.tab1ComboHintLabel = QLabel("  ")
        self.tab1ComboHintLabel.setStyleSheet(style.grey1())
        self.tab1ComboHintLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        layoutBtm.addLayout(layout4)
        layoutBtm.addLayout(grid)
        layoutBtm.addWidget(self.tab1ComboHintLabel)

        layout5 = QVBoxLayout()
        layout6 = QVBoxLayout()
        layout4.addLayout(layout5)
        layout4.addStretch()
        layout4.addLayout(layout6)

        label_step2_1 = QLabel(" Step 2: Combo Log Study")
        label_step2_1.setStyleSheet(style.body1())
        label_step2_2 = QLabel("Plot data at two time points:")
        self.rowNumRadioButton = QRadioButton("Use Row Numbers: ", self)

        layout5.addWidget(label_step2_1)
        layout5.addWidget(label_step2_2)
        layout5.addWidget(self.rowNumRadioButton)

        self.plotComboButton = QPushButton("  Plot  ", self)
        self.plotComboButton.clicked.connect(lambda: func_calibration.combo_study(self))
        self.plotComboButton.setStyleSheet("font: bold")
        self.stopPlotComboButton = QPushButton("Stop Plot", self)
        self.stopPlotComboButton.clicked.connect(lambda: func_calibration.stop_combo_plot(self))
        self.stopPlotComboButton.setEnabled(False)
        self.stopPlotComboButton.setToolTip("To stop combo plot, change the value of 'par1/combo_stop.txt' to 1.")

        layout6.addWidget(self.plotComboButton)
        layout6.addWidget(self.stopPlotComboButton)

        gap = QLabel()
        # self.rowNumRadioButton = QRadioButton("Use Row Numbers: ", self)
        label_step2_row1 = QLabel("Row 1")
        self.row1LineEdit = QLineEdit()
        label_step2_row2 = QLabel("vs Row 2")
        self.row2LineEdit = QLineEdit()

        self.peakRadioButton = QRadioButton("Use Peak Height: ", self)
        label_step2_peak1 = QLabel("Peak")
        label_step2_peak2 = QLabel("vs Percentage %:")
        label_step2_peak2.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.peakPecentageLineEdit = QLineEdit("10")

        self.peakRadioButton.setChecked(True)
        # self.rowNumRadioButton.toggled.connect(self.choose_row)
        # self.peakRadioButton.toggled.connect(self.choose_peak)
        self.bg3 = QButtonGroup()
        self.bg3.addButton(self.rowNumRadioButton)
        self.bg3.addButton(self.peakRadioButton)

        label_step2_range1 = QLabel("Row Range for Plots: (leave blank to use defaults)")
        label_step2_range2 = QLabel("From:")
        label_step2_range3 = QLabel("To:")
        label_step2_range3.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.comboRange1LineEdit = QLineEdit()
        self.comboRange1LineEdit.setToolTip("Default to minimal")
        self.comboRange2LineEdit = QLineEdit()
        self.comboRange2LineEdit.setToolTip("Default to maximal")

        # grid.addWidget(self.rowNumRadioButton, 0, 0, 1, 3)

        grid.addWidget(gap, 1, 0)
        grid.addWidget(label_step2_row1, 1, 1)
        grid.addWidget(self.row1LineEdit, 1, 2)
        grid.addWidget(label_step2_row2, 1, 3)
        grid.addWidget(self.row2LineEdit, 1, 4)

        grid.addWidget(self.peakRadioButton, 2, 0, 1, 5)
        grid.addWidget(label_step2_peak1, 3, 1)
        grid.addWidget(label_step2_peak2, 3, 2, 1, 2)
        grid.addWidget(self.peakPecentageLineEdit, 3, 4)

        grid.addWidget(label_step2_range1, 4, 0, 1, 5)
        grid.addWidget(label_step2_range2, 5, 1)
        grid.addWidget(self.comboRange1LineEdit, 5, 2)
        grid.addWidget(label_step2_range3, 5, 3)
        grid.addWidget(self.comboRange2LineEdit, 5, 4)


    def tab2_layout(self):  # real time spectrum viewer
        mainLayout = QVBoxLayout()
        self.tab2.setLayout(mainLayout)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground("w")
        layout0 = QHBoxLayout()
        mainLayout.addWidget(self.graphWidget)
        mainLayout.addLayout(layout0)
        
        self.plotKeyLabel = QLabel("Data Key for Plot:")
        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        gap = QLabel()

        layout0.addWidget(self.plotKeyLabel)
        layout0.addStretch()
        layout0.addLayout(layout1)
        layout0.addWidget(gap)
        layout0.addLayout(layout2)
        layout0.addStretch()

        self.startPlotButton = QToolButton()
        self.startPlotButton.setIcon(QIcon("icons/start1.png"))
        self.startPlotButton.setIconSize(QSize(40, 40))
        self.startPlotButton.setToolTip("Close")
        self.startPlotButton.clicked.connect(lambda: func_experiment.start_plot(self))
        self.startPlotButton.setEnabled(False)
        label1 = QLabel('  Start')

        self.stopPlotButton = QToolButton()
        self.stopPlotButton.setIcon(QIcon("icons/stop1.png"))
        self.stopPlotButton.setIconSize(QSize(40, 40))
        self.stopPlotButton.setToolTip("Close")
        self.stopPlotButton.clicked.connect(lambda: func_experiment.stop_plot(self))
        self.stopPlotButton.setEnabled(False)
        label2 = QLabel('  Stop')

        layout1.addWidget(self.startPlotButton)
        layout1.addWidget(label1)
        layout2.addWidget(self.stopPlotButton)
        layout2.addWidget(label2)
        

    # hardware
    def tab3_layout(self):
        mainLayout = QHBoxLayout()
        self.tab3.setLayout(mainLayout)
        gap = QLabel()

        self.tab3_layout_left = QVBoxLayout()  # hardware
        layout_right = QVBoxLayout()  # images
        mainLayout.addLayout(self.tab3_layout_left, 40)
        mainLayout.addWidget(gap, 10)
        mainLayout.addLayout(layout_right, 50)

        image1 = QLabel()
        pixmap1 = QPixmap('icons/droplet_setup.png')
        image1.setPixmap(
            pixmap1.scaled(550, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation))
        image1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image2 = QLabel()
        pixmap2 = QPixmap('icons/gas_setup.png')
        image2.setPixmap(
            pixmap2.scaled(320, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation))
        image2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_exp = QLabel("Calibration Experiment Set Up")
        label_exp.setStyleSheet(style.headline1())
        label_exp.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_droplet = QLabel("Droplet")
        label_droplet.setStyleSheet(style.headline2())
        label_droplet.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_gas = QLabel("Gas Tank")
        label_gas.setStyleSheet(style.headline2())
        label_gas.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_right.addStretch()
        layout_right.addWidget(label_exp)
        layout_right.addStretch()
        layout_right.addWidget(image1)
        layout_right.addWidget(label_droplet)
        layout_right.addStretch()
        layout_right.addWidget(image2)
        layout_right.addWidget(label_gas)
        layout_right.addStretch()


        self.createTab3HardwareLayout()


    def createTab3HardwareLayout(self):
        layout1 = QVBoxLayout()  # system
        grid1 = QGridLayout()  # analyzer
        grid2 = QGridLayout()  # MFC
        grid3 = QGridLayout()  # scale

        self.tab3_layout_left.addStretch()
        self.tab3_layout_left.addLayout(layout1)
        self.tab3_layout_left.addLayout(grid1)
        self.tab3_layout_left.addLayout(grid2)
        self.tab3_layout_left.addLayout(grid3)
        self.tab3_layout_left.addStretch()

        # system
        label0 = QLabel("Your system:")
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        
        # portlist = [p.device for p in ls.comports()]
        self.portListLabel = QLabel()
        # self.portListLabel.setText(str(portlist))
        self.portListLabel.setStyleSheet("background-color: white")
        self.portListLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        layout1.addWidget(label0)
        layout1.addLayout(layout2)
        layout1.addLayout(layout3)
        layout1.addWidget(self.portListLabel)

        rb1 = QRadioButton("Windows", self)
        rb2 = QRadioButton("Mac", self)
        rb3 = QRadioButton("Linux", self)

        if opsystem == 'Darwin':
            rb1.setEnabled(False)
            rb2.setChecked(True)
            rb3.setEnabled(False)
        elif opsystem == 'Linux':
            rb1.setEnabled(False)
            rb2.setEnabled(False)
            rb3.setChecked(True)
        else:
            rb1.setChecked(True)
            rb2.setEnabled(False)
            rb3.setEnabled(False)

        layout2.addWidget(rb1)
        layout2.addWidget(rb2)
        layout2.addWidget(rb3)

        button1 = QPushButton("Get Serial Port Names", self)
        button1.clicked.connect(lambda: load_par.get_port(self))
        button1.setStyleSheet("font: bold")
        button1.setToolTip("Available serial ports on this computer")
        layout3.addWidget(button1)
        layout3.addStretch()

        # Analyzer
        label_analyzer1 = QLabel("Analyzer")
        label_analyzer1.setStyleSheet(style.headline2())
        label_analyzer2 = QLabel("IP Address:")
        self.analyzerIPLineEdit = QLineEdit()

        label_analyzer3 = QLabel("Port In: ")
        label_analyzer_portin = QLabel("50070  (send data to analyzer/ backdoor)")
        button_analyzer1 = QPushButton("Detect")
        button_analyzer1.clicked.connect(lambda: func_analyzer.detect_analyzer_portin(self))
        self.analyzerPortInHintLabel = QLabel()

        label_analyzer4 = QLabel("Port Out: ")
        label_analyzer_portout = QLabel("40060 (Receiving data from analyzer/ listener)")

        button_analyzer2 = QPushButton("Detect")
        # button_analyzer2.clicked.connect(self.detect_analyzer_portout)
        button_analyzer2.clicked.connect(lambda: func_analyzer.detect_analyzer_portout(self))
        self.analyzerPortOutHintLabel = QLabel()

        grid1.addWidget(label_analyzer1, 0, 0, 1, 3)
        grid1.addWidget(label_analyzer2, 1, 0)
        grid1.addWidget(self.analyzerIPLineEdit, 1, 1)
        grid1.addWidget(label_analyzer3, 2, 0)
        grid1.addWidget(label_analyzer_portin, 2, 1)
        grid1.addWidget(button_analyzer1, 2, 2)
        grid1.addWidget(self.analyzerPortInHintLabel, 2, 3)

        grid1.addWidget(label_analyzer4, 3, 0)
        grid1.addWidget(label_analyzer_portout, 3, 1)
        grid1.addWidget(button_analyzer2, 3, 2)
        grid1.addWidget(self.analyzerPortOutHintLabel, 3, 3)

        # Alicat MFC
        label_mfc1 = QLabel("Mass Flower Controller (Alicat)")
        label_mfc1.setStyleSheet(style.headline2())
        label_mfc2 = QLabel("Serial Port: ")
        self.mfcPortCombobox = QComboBox()

        label_mfc3 = QLabel("MFC1 Address: ")
        self.MFC1AddressLineEdit = QLineEdit()
        mfc1Button = QPushButton("Detect")
        # mfc1Button.clicked.connect(self.detect_mfc1)
        mfc1Button.clicked.connect(lambda: func_mfc.detect_mfc1(self))
        label_mfc4 = QLabel("dilution line, 1 SLPM")
        self.alicatMFC1HintLabel = QLabel()

        label_mfc5 = QLabel("MFC2 (large) Address: ")
        self.MFC2largeAddressLineEdit = QLineEdit()
        mfc2largeButton = QPushButton("Detect")
        # mfc2largeButton.clicked.connect(self.detect_mfc2large)
        mfc2largeButton.clicked.connect(lambda: func_mfc.detect_mfc2large(self))
        label_mfc6 = QLabel("Bubble line, 100 sccm")
        self.alicatMFC2LargeHintLabel = QLabel()

        label_mfc7 = QLabel("MFC2 (small) Address: ")
        self.MFC2smallAddressLineEdit = QLineEdit()
        mfc2smallButton = QPushButton("Detect")
        # mfc2smallButton.clicked.connect(self.detect_mfc2small)
        mfc2smallButton.clicked.connect(lambda: func_mfc.detect_mfc2small(self))
        label_mfc8 = QLabel("Bubble line, 10 sccm")
        self.alicatMFC2SmallHintLabel = QLabel()

        grid2.addWidget(label_mfc1, 0, 0, 1, 4)
        grid2.addWidget(label_mfc2, 1, 0)
        grid2.addWidget(self.mfcPortCombobox, 1, 1, 1, 2)

        grid2.addWidget(label_mfc3, 2, 0)
        grid2.addWidget(self.MFC1AddressLineEdit, 2, 1)
        grid2.addWidget(mfc1Button, 2, 2)
        grid2.addWidget(label_mfc4, 2, 3)
        grid2.addWidget(self.alicatMFC1HintLabel, 2, 4)

        grid2.addWidget(label_mfc5, 3, 0)
        grid2.addWidget(self.MFC2largeAddressLineEdit, 3, 1)
        grid2.addWidget(mfc2largeButton, 3, 2)
        grid2.addWidget(label_mfc6, 3, 3)
        grid2.addWidget(self.alicatMFC2LargeHintLabel, 3, 4)

        grid2.addWidget(label_mfc7, 4, 0)
        grid2.addWidget(self.MFC2smallAddressLineEdit, 4, 1)
        grid2.addWidget(mfc2smallButton, 4, 2)
        grid2.addWidget(label_mfc8, 4, 3)
        grid2.addWidget(self.alicatMFC2SmallHintLabel, 4, 4)

        # Scale
        label_scale1 = QLabel("Mettler Toledo Scale")
        label_scale1.setStyleSheet(style.headline2())
        label_scale2 = QLabel("IP Address: ")
        self.scaleIPAddressLineEdit = QLineEdit()
        button_scale = QPushButton("Detect")
        # button_scale.clicked.connect(self.detect_scale)
        button_scale.clicked.connect(lambda: func_scale.detect_scale(self))
        self.scaleHintLabel = QLabel()
        
        label_scale3 = QLabel("Port: ")
        self.scalePortLineEdit = QLineEdit()

        grid3.addWidget(label_scale1, 0, 0, 1, 3)
        grid3.addWidget(label_scale2, 1, 0)
        grid3.addWidget(self.scaleIPAddressLineEdit, 1, 1)
        grid3.addWidget(button_scale, 1, 3)
        grid3.addWidget(self.scaleHintLabel, 1, 4)
        
        grid3.addWidget(label_scale3, 2, 0)
        grid3.addWidget(self.scalePortLineEdit, 2, 1)



# //////////////////// functions

    # def get_key(self):
    #     pass

    # def send_MFC_data(self): # mfc
    #     pass


    # def scale_reading(self):  # scale
    #     pass


    # def scale_weigh(self):  # scale
    #     pass

    # def choose_droplet(self):  # exp
    #     pass
    #
    # def choose_tank(self):  # exp
    #     pass


    # def create_experiment(self):  # exp
        # if self.sendMFCButton.isEnabled():
        #     print('enabled')
        # if self.expAddButton.isEnabled():
        #     print('yes')
        # else:
        #     print('no')


    # def tab1_terminate_exp(self):
    #     pass


    # def set_mfc_1slpm(self):  #mfc
    #     pass
    # 
    # def set_mfc_100sccm(self):  # mfc
    #     pass
    # 
    # def set_mfc_10sccm(self):  # mfc
    #     pass

    # def choose_100sccm(self):  # mfc
    #     pass
    #
    # def choose_10sccm(self):  # mfc
    #     pass

    # def start_exp(self):  # exp
    #     pass

    # def stop_flow(self):  # mfc
    #     pass

    # def add_sample(self):
    #     pass

    # def end_exp(self):
    #     pass

    # def load_experiment(self):  cal
    #     pass

    # def calculate(self): cal
    #     pass

    # def close_plot(self): #cal
    #     pass

    # def plot_one_combo(self): #cal
    #     pass

    # def combo_study(self):  # cal
    #     pass

    # def choose_row(self):
    #     pass
    # 
    # def choose_peak(self):
    #     pass



    # def detect_analyzer_portin(self):  # analyzer
    #     pass
    # 
    # def detect_analyzer_portout(self):  # analyzer
    #     pass

    # def detect_mfc1(self):  # mfc
    #     pass

    # def detect_mfc2large(self):  # mfc
    #     pass

    # def detect_mfc2small(self):  # mfc
    #     pass

    # def detect_scale(self):  # scale
    #     pass


    def exitFunc(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)

        if reply == QMessageBox.StandardButton.Yes:
            self.close()


def main():
    app = QApplication(sys.argv)
    window = Window()
    app.setWindowIcon(QIcon('icons/logo.png'))
    window.show()
    app.exec()


if __name__ == '__main__':
    main()

# @author: Yilin Shi | 2023.9.15
# shiyilin890@gmail.com
# Bog the Fat Crocodile vvvvvvv
#                       ^^^^^^^