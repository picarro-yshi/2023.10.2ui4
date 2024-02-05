## tab1 layout
import platform
opsystem = platform.system()

from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QPushButton,
    QLabel,
    QCheckBox,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QGridLayout,
    QButtonGroup,
    QRadioButton,
    QToolButton,
    QTextEdit,
    QComboBox,
)

import pyqtgraph as pg

import style
from utilities import (
    func_mfc,
    func_scale,
    func_experiment,
    func_calibration, func_move,
)

MINUTE = [str(i).zfill(2) for i in range(60)]
HOUR = [str(i).zfill(2) for i in range(24)]
COMBOKEYS = ["partial_fit", "absorbance", "model", "residuals"]

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

    createTab1LogoLayout(self)
    createTab1ScaleLayout(self)
    createTab1SampleLayout(self)
    createTab1ExperimentLayout(self)

    self.calibrationLayoutTop = QVBoxLayout()
    self.calibrationLayoutBtm = QVBoxLayout()
    self.tab1CalibrationLayout.addLayout(self.calibrationLayoutTop)
    self.tab1CalibrationLayout.addLayout(self.calibrationLayoutBtm)
    createCalibrationLayoutTop(self)
    createCalibrationLayoutBtm(self)

    # self.bg1 = QButtonGroup()
    # self.bg1.addButton(self.dropletRadioButton)
    # self.bg1.addButton(self.tankRadioButton)


def createTab1LogoLayout(self):
    logo = QLabel()
    pixmap = QPixmap("icons/picarro.png")
    logo.setPixmap(
        pixmap.scaled(
            250,
            250,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
    )
    logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

    version = QLabel("Yilin Shi | Version 4.2 | Fall 2023 | Santa Clara, CA    ")
    if opsystem == "Darwin":
        vfont = 10
    elif opsystem == "Windows":
        vfont = 8
    else:
        vfont = 10
    version.setFont(QFont("Arial", vfont))
    version.setAlignment(Qt.AlignmentFlag.AlignRight)

    self.plotCheckbox = QCheckBox("Plot data key:")
    self.plotCheckbox.setToolTip("Check if you want plot on tab 2 to start.")
    self.datakeyLabel = QLabel("broadband_gasConcs_[CID]")
    self.tab1Layout1Hint = QLabel()
    layout0 = QHBoxLayout()

    self.tab1LogoLayout.addWidget(logo)
    self.tab1LogoLayout.addWidget(version)
    self.tab1LogoLayout.addWidget(self.plotCheckbox)
    self.tab1LogoLayout.addWidget(self.datakeyLabel)
    self.tab1LogoLayout.addLayout(layout0)
    self.tab1LogoLayout.addWidget(self.tab1Layout1Hint)

    layout2 = QVBoxLayout()
    layout3 = QVBoxLayout()
    layout4 = QVBoxLayout()

    layout0.addLayout(layout2)
    layout0.addStretch()
    layout0.addLayout(layout3)
    layout0.addStretch()
    layout0.addLayout(layout4)

    self.sendMFCButton = QToolButton()
    self.sendMFCButton.setIcon(QIcon("icons/arrow.png"))
    self.sendMFCButton.setIconSize(QSize(40, 40))
    self.sendMFCButton.setToolTip(
        "Send MFC data to the analyzer\nso it will show up in the\n"
        "'Data Key' of the analyzer GUI\nSelect MFC2 before click it."
    )
    self.sendMFCButton.clicked.connect(lambda: func_mfc.send_MFC_data(self))
    label2 = QLabel("Send MFC")

    layout2.addWidget(self.sendMFCButton)
    layout2.addWidget(label2)

    self.stopSendMFCButton = QToolButton()
    self.stopSendMFCButton.setIcon(QIcon("icons/stop2.jpg"))
    self.stopSendMFCButton.setIconSize(QSize(40, 40))
    self.stopSendMFCButton.setToolTip("Stop sending MFC data to the analyzer")
    self.stopSendMFCButton.clicked.connect(
        lambda: func_mfc.stop_send_MFC_data(self)
    )
    self.stopSendMFCButton.setEnabled(False)
    label3 = QLabel("Stop Send MFC")

    layout3.addWidget(self.stopSendMFCButton)
    layout3.addWidget(label3)

    button2 = QToolButton()
    button2.setIcon(QIcon("icons/stop.png"))
    button2.setIconSize(QSize(40, 40))
    button2.setToolTip("Close VOC Calibration GUI Window")
    button2.clicked.connect(self.exitFunc)
    label4 = QLabel("  Close")

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
    self.weightLabel.setFont(QFont("Times", 24))
    self.weightLabel.setStyleSheet("background-color: white")
    self.weightLabel.setTextInteractionFlags(
        Qt.TextInteractionFlag.TextSelectableByMouse
    )
    label1 = QLabel("g  ")

    layout11.addWidget(self.weightLabel, 90)
    layout11.addWidget(label1, 10)

    label2 = QLabel("Time (sec):")
    self.scaleTimeLineEdit = QLineEdit("180")
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
    self.scaleStartButton.setToolTip(
        "Continuously measure and plot weight for a time"
    )
    self.scaleStartButton.clicked.connect(lambda: func_scale.scale_reading(self))
    label5 = QLabel("   Start")

    layout5.addWidget(self.scaleStartButton)
    layout5.addWidget(label5)

    button2 = QToolButton()
    button2.setIcon(QIcon("icons/weigh5.png"))
    button2.setIconSize(QSize(40, 40))
    button2.setToolTip("Get current weight measurement")
    button2.clicked.connect(lambda: func_scale.scale_weigh(self))
    label6 = QLabel("  Weigh")

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
    self.sampleSigmaCombobox.setToolTip(
        "When baseline after the peak is n*σ \n"
        "higher than the baseline before the peak,\n"
        "end the experiment."
    )

    self.sampleTankConcLineEdit = QLineEdit()
    self.sampleTankConcLineEdit.setToolTip(
        "Gas tank concentration, ppm\nfound on tank label."
    )
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
    self.MFCLayout = QVBoxLayout()  # MFC
    self.timeLayout = QHBoxLayout()  # time
    self.tab1ExperimentHint = QLabel("  ")
    self.tab1ExperimentHint.setStyleSheet(style.grey1())

    self.tab1ExperimentLayout.addLayout(layout1, 10)
    # self.tab1ExperimentLayout.addStretch()
    self.tab1ExperimentLayout.addLayout(self.MFCLayout, 20)
    # self.tab1ExperimentLayout.addStretch()
    self.tab1ExperimentLayout.addLayout(self.timeLayout, 40)
    # self.tab1ExperimentLayout.addStretch()
    self.tab1ExperimentLayout.addWidget(self.tab1ExperimentHint, 10)

    # droplet or tank
    self.dropletRadioButton = QRadioButton("Droplet Test", self)
    self.tankRadioButton = QRadioButton("Gas Tank Test", self)
    self.dropletRadioButton.setChecked(
        True
    )  # follow immediately after all radiobutton, otherwise python crash
    self.dropletRadioButton.setStyleSheet("color: red")
    self.tankRadioButton.setStyleSheet("color: black")

    self.tab1_bg1 = QButtonGroup()
    self.tab1_bg1.addButton(self.dropletRadioButton)
    self.tab1_bg1.addButton(self.tankRadioButton)

    self.aqCheckbox = QCheckBox("(aq)")
    self.aqCheckbox.setToolTip("Check if this is an aqueous droplet")

    # create experiment
    self.tab1CreateExpButton = QPushButton("Create Exp.", self)
    self.tab1CreateExpButton.clicked.connect(
        lambda: func_experiment.create_experiment(self)
    )
    self.tab1CreateExpButton.setStyleSheet("font: bold")
    self.tab1CreateExpButton.setToolTip(
        "Create a folder named with today's date\n"
        "+suffix (if needed) on the R drive,\n"
        "for a new experiment and store parameters."
    )

    layout1.addWidget(self.dropletRadioButton)
    layout1.addWidget(self.aqCheckbox)
    layout1.addWidget(self.tankRadioButton)
    layout1.addWidget(self.tab1CreateExpButton)

    createTab1MFCLayout(self)
    createTab1TimeLayout(self)


def createTab1MFCLayout(self):
    grid = QGridLayout()
    layout = QHBoxLayout()
    self.MFCLayout.addLayout(grid)
    self.MFCLayout.addLayout(layout)

    # grid
    label1 = QLabel("Pressure (psi)")
    self.tab1PressureLabel = QLabel(" ")
    self.tab1PressureLabel.setStyleSheet(style.grey1())
    self.tab1PressureLabel.setFixedWidth(70)

    label2 = QLabel("Temperature (°C)")
    self.tab1TempLabel = QLabel()
    self.tab1TempLabel.setStyleSheet(style.grey1())

    label3 = QLabel("MFC1 (1 SLPM)")
    self.tab1MFC1Label = QLabel("     ")
    self.tab1MFC1Label.setStyleSheet(style.grey1())
    self.tab1MFC1Label.setFixedWidth(70)
    self.tab1MFC1LineEdit = QLineEdit("0.95")
    self.tab1MFC1LineEdit.setToolTip("Dilution line, SLPM\nInput value between 0 ~ 1")
    self.tab1MFC1Button = QPushButton("  Set  ")
    self.tab1MFC1Button.clicked.connect(lambda: func_mfc.set_mfc_1slpm(self))

    self.mfc100RadioButton = QRadioButton("MFC2 (100 SCCM)", self)
    self.mfc100RadioButton.setToolTip(
        "Valve mask 0\n! Please set up manually on analyzer"
    )
    self.mfc10RadioButton = QRadioButton("MFC2 (10 SCCM)", self)
    self.mfc10RadioButton.setToolTip(
        "Valve mask 1\n! Please set up manually on analyzer"
    )
    self.mfc100RadioButton.setChecked(True)

    self.tab1_bg2 = QButtonGroup()
    self.tab1_bg2.addButton(self.mfc100RadioButton)
    self.tab1_bg2.addButton(self.mfc10RadioButton)

    self.mfc100RadioButton.toggled.connect(lambda: func_mfc.choose_100sccm(self))
    self.mfc10RadioButton.toggled.connect(lambda: func_mfc.choose_10sccm(self))

    self.tab1MFC100Label = QLabel(" ")
    self.tab1MFC100Label.setStyleSheet(style.grey1())
    self.tab1MFC100Label.setFixedWidth(70)

    self.tab1MFC100Combobox = QComboBox()
    self.tab1MFC100Combobox.addItems(
        ["50", "5", "10", "20", "40", "60", "80", "100"]
    )
    self.tab1MFC100Combobox.setEditable(True)
    self.tab1MFC100Combobox.setToolTip("Bubble line, 100 SCCM\nInput value between 0 ~ 100")

    self.tab1MFC100Button = QPushButton("  Set  ", self)
    self.tab1MFC100Button.setStyleSheet("font: bold")
    self.tab1MFC100Button.clicked.connect(lambda: func_mfc.set_mfc_100sccm(self))

    self.tab1MFC10Label = QLabel(" ")
    self.tab1MFC10Label.setStyleSheet(style.grey1())
    self.tab1MFC10Label.setFixedWidth(70)

    self.tab1MFC10Combobox = QComboBox()
    self.tab1MFC10Combobox.addItems(["1", "0.1", "0.2", "0.5", "2", "5", "10"])
    self.tab1MFC10Combobox.setEditable(True)
    self.tab1MFC10Combobox.setToolTip("Bubble line 10 SCCM\nInput value between 0 ~ 10")

    self.tab1MFC10Button = QPushButton("  Set  ", self)
    self.tab1MFC10Button.setStyleSheet("font: bold")
    self.tab1MFC10Button.clicked.connect(lambda: func_mfc.set_mfc_10sccm(self))

    func_mfc.choose_100sccm(self)

    grid.addWidget(label1, 0, 0)
    grid.addWidget(self.tab1PressureLabel, 0, 1)
    grid.addWidget(label2, 0, 3)
    grid.addWidget(self.tab1TempLabel, 0, 4)

    grid.addWidget(label3, 1, 0)
    grid.addWidget(self.tab1MFC1Label, 1, 1)
    grid.addWidget(self.tab1MFC1LineEdit, 1, 3)
    grid.addWidget(self.tab1MFC1Button, 1, 4)

    grid.addWidget(self.mfc100RadioButton, 2, 0)
    grid.addWidget(self.tab1MFC100Label, 2, 1)
    grid.addWidget(self.tab1MFC100Combobox, 2, 3)
    grid.addWidget(self.tab1MFC100Button, 2, 4)

    grid.addWidget(self.mfc10RadioButton, 3, 0)
    grid.addWidget(self.tab1MFC10Label, 3, 1)
    grid.addWidget(self.tab1MFC10Combobox, 3, 3)
    grid.addWidget(self.tab1MFC10Button, 3, 4)

    # layout
    self.automationCheckbox = QCheckBox("Automate Exp.")
    self.automationCheckbox.setToolTip(
        "Set the flows automatically.\n"
        "take effect only before\nclick the 'Add Sample' Button."
    )
    self.automationCheckbox.setChecked(True)

    self.heater1Checkbox = QCheckBox("Heater1")
    self.heater1Checkbox.setDisabled(True)
    self.heater1Checkbox.setToolTip(
        "Use heater 1, 2:\nturn on heater after concentration is below 1e-6 and \nturn off heater when experiment ends."
        "\nTemperature needs to be set manually.\nEnable them using Tab3 'Detect' button."
    )

    self.heater2Checkbox = QCheckBox("Heater2")
    self.heater2Checkbox.setDisabled(True)

    self.mfcHintLabel = QLabel()

    layout.addWidget(self.automationCheckbox)
    layout.addWidget(self.heater1Checkbox)
    layout.addWidget(self.heater2Checkbox)
    layout.addWidget(self.mfcHintLabel)


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
    label1 = QLabel("Start Exp.")
    label1.setAlignment(Qt.AlignmentFlag.AlignTop)

    self.expStartLineEdit = QLineEdit("")  # 20220222' start
    self.expStartLineEdit.setToolTip(
        "Experiment start date.\n(Used as folder name)\nFormat: yyyymmdd."
    )
    self.expStartCombobox1 = QComboBox()  # '08'
    self.expStartCombobox1.addItems(HOUR)
    self.expStartCombobox2 = QComboBox()  # '11'
    self.expStartCombobox2.addItems(MINUTE)

    layout1.addWidget(self.expStartButton)
    layout1.addWidget(label1)
    layout1.addWidget(self.expStartLineEdit)
    layout1.addWidget(self.expStartCombobox1)
    layout1.addWidget(self.expStartCombobox2)
    # layout1.addStretch()

    # box 2
    self.mfcStopButton = QToolButton()
    self.mfcStopButton.setIcon(QIcon("icons/zero.png"))
    self.mfcStopButton.setIconSize(QSize(40, 40))
    self.mfcStopButton.setToolTip("Stop MFC2 (bubble line) flow,\nset MFC1 (dilution line) to 1 SLPM.")
    self.mfcStopButton.clicked.connect(lambda: func_mfc.stop_mfc2_flow(self))
    label2 = QLabel("Stop MFC2 Flow")
    label2.setAlignment(Qt.AlignmentFlag.AlignTop)

    self.expSuffix = QLineEdit("")  # '' suffix
    self.expSuffix.setToolTip(
        "(Optional) Add a suffix to\nthe start date as the folder name."
    )
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
    self.expAddButton.clicked.connect(lambda: func_experiment.add_sample(self))
    self.expAddButton.setEnabled(False)
    label3 = QLabel("Add Sample")
    label3.setAlignment(Qt.AlignmentFlag.AlignTop)

    self.expAddLineEdit = QLineEdit("")  # 20220222' add
    self.expAddLineEdit.setToolTip("Date when sample is added.\nFormat: yyyymmdd")
    self.expAddCombobox1 = QComboBox()  # '09'
    self.expAddCombobox1.addItems(HOUR)
    self.expAddCombobox2 = QComboBox()  # '11'
    self.expAddCombobox2.addItems(MINUTE)

    layout3.addWidget(self.expAddButton)
    layout3.addWidget(label3)
    layout3.addWidget(self.expAddLineEdit)
    layout3.addWidget(self.expAddCombobox1)
    layout3.addWidget(self.expAddCombobox2)
    # layout3.addStretch()

    # box4
    self.expEndButton = QToolButton()
    self.expEndButton.setIcon(QIcon("icons/stop1.png"))
    self.expEndButton.setIconSize(QSize(40, 40))
    self.expEndButton.setToolTip(
        "End this experiment.\n"
        "Record current time or\n your input time as the end time.\n\n"
        "All parameters will be saved again.\n"
        "(make changes as needed\nbefore click this button)."
    )
    self.expEndButton.clicked.connect(lambda: func_experiment.end_exp(self))
    self.expEndButton.setEnabled(False)
    label4 = QLabel("End Exp.")
    label4.setAlignment(Qt.AlignmentFlag.AlignTop)

    self.expEndLineEdit = QLineEdit("")  # 20220222' end
    self.expEndLineEdit.setToolTip("Date when experiment ends.\nFormat: yyyymmdd")
    self.expEndCombobox1 = QComboBox()  # '23'
    self.expEndCombobox1.addItems(HOUR)
    self.expEndCombobox2 = QComboBox()  # '59'
    self.expEndCombobox2.addItems(MINUTE)

    layout4.addWidget(self.expEndButton)
    layout4.addWidget(label4)
    layout4.addWidget(self.expEndLineEdit)
    layout4.addWidget(self.expEndCombobox1)
    layout4.addWidget(self.expEndCombobox2)
    # layout4.addStretch()


# step 1: calibration factor
def createCalibrationLayoutTop(self):
    layout1 = QHBoxLayout()
    layout2 = QHBoxLayout()
    layout3 = QHBoxLayout()
    layout4 = QHBoxLayout()
    layout_calbutton = QHBoxLayout()
    # self.tab1CalHintLabel = QLabel(" ")
    # self.tab1CalHintLabel.setStyleSheet(style.grey1())
    # self.tab1CalHintLabel.setTextInteractionFlags(
    #     Qt.TextInteractionFlag.TextSelectableByMouse
    # )

    self.calibrationLayoutTop.addLayout(layout1)
    self.calibrationLayoutTop.addLayout(layout2)
    self.calibrationLayoutTop.addLayout(layout3)
    self.calibrationLayoutTop.addLayout(layout4)
    self.calibrationLayoutTop.addLayout(layout_calbutton)

    # title
    label1 = QLabel(" Step 1: Calibration Factor")
    label1.setStyleSheet(style.body1())
    self.saveFigCheckbox = QCheckBox("Save Figure")
    self.saveFigCheckbox.setChecked(True)
    layout1.addWidget(label1)
    layout1.addStretch()
    layout1.addWidget(self.saveFigCheckbox)

    # move and unzip ssh
    self.rdfCheckbox = QCheckBox("RDF")
    self.privateCheckbox = QCheckBox("Private")
    self.comboCheckbox = QCheckBox("Combo")
    self.broadbandCheckbox = QCheckBox("broadband")
    self.broadbandCheckbox.setToolTip("Combo Log broadband h5 files")

    self.rdfCheckbox.setChecked(True)
    self.privateCheckbox.setChecked(True)
    self.comboCheckbox.setChecked(True)
    self.broadbandCheckbox.setChecked(False)

    layout2.addWidget(self.rdfCheckbox)
    layout2.addWidget(self.privateCheckbox)
    layout2.addWidget(self.comboCheckbox)
    layout2.addWidget(self.broadbandCheckbox)

    label_move = QLabel("From analyzer to R drive: ")
    self.button_move = QPushButton("Move && Unzip Data", self)
    self.button_move.setStyleSheet("font: bold")
    self.button_move.setToolTip("For current compound, between Start and End time")
    self.button_move.clicked.connect(lambda: func_move.move(self))
    self.button_move.setEnabled(False)
    layout3.addWidget(label_move)
    layout3.addWidget(self.button_move)

    # label2 = QLabel("Combo Spectrum Keys:")
    # self.combo_spectrum_key = QComboBox()
    # self.combo_spectrum_key.addItems(COMBOKEYS)
    # layout2.addWidget(label2)
    # layout2.addWidget(self.combo_spectrum_key)

    label3 = QLabel("Combo Log Row #:")
    self.oneComboNumLineEdit = QLineEdit()
    self.oneComboNumLineEdit.setFixedWidth(50)
    self.oneComboNumLineEdit.setToolTip(
        "Optional, default to 500.\ninteger between 0 and Maximal."
    )
    label4 = QLabel("Maximal: ")
    self.maxRowLabel = QLabel("            ")

    layout4.addWidget(label3)
    layout4.addWidget(self.oneComboNumLineEdit)
    layout4.addStretch()
    layout4.addWidget(label4)
    layout4.addWidget(self.maxRowLabel)

    # 4 round buttons
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
    self.tab1LoadExpButton.setToolTip(
        "Fill in the start date (+suffix) to \nload parameters for this experiment."
    )
    self.tab1LoadExpButton.clicked.connect(
        lambda: func_calibration.load_experiment(self)
    )
    label11 = QLabel("Load Exp.")

    layout11.addWidget(self.tab1LoadExpButton)
    layout11.addWidget(label11)

    self.tab1CalculateButton = QToolButton()
    self.tab1CalculateButton.setIcon(QIcon("icons/start1.png"))
    self.tab1CalculateButton.setIconSize(QSize(40, 40))
    self.tab1CalculateButton.setToolTip("Calculate the Calibration factor.")
    self.tab1CalculateButton.clicked.connect(
        lambda: func_calibration.calculate(self)
    )
    self.tab1CalculateButton.setEnabled(False)
    label12 = QLabel("Calculate")

    layout12.addWidget(self.tab1CalculateButton)
    layout12.addWidget(label12)

    self.PlotOneComboButton = QToolButton()
    self.PlotOneComboButton.setIcon(QIcon("icons/plot1.png"))
    self.PlotOneComboButton.setIconSize(QSize(40, 40))
    self.PlotOneComboButton.setToolTip("Plot Combo spectrum\nfor a particular row.")
    self.PlotOneComboButton.clicked.connect(
        lambda: func_calibration.plot_one_combo(self)
    )
    self.PlotOneComboButton.setEnabled(False)
    label13 = QLabel("Plot Combo")

    layout13.addWidget(self.PlotOneComboButton)
    layout13.addWidget(label13)

    self.tab1ClosePlotButton = QToolButton()
    self.tab1ClosePlotButton.setIcon(QIcon("icons/stop.png"))
    self.tab1ClosePlotButton.setIconSize(QSize(40, 40))
    self.tab1ClosePlotButton.setToolTip("Close all calibration factor plots.")
    self.tab1ClosePlotButton.clicked.connect(
        lambda: func_calibration.close_plot(self)
    )
    self.tab1ClosePlotButton.setEnabled(False)
    label14 = QLabel("Close Plots")

    layout14.addWidget(self.tab1ClosePlotButton)
    layout14.addWidget(label14)


# step 2: calibration
def createCalibrationLayoutBtm(self):
    layout = QHBoxLayout()
    grid = QGridLayout()
    # self.tab1ComboHintLabel = QLabel("  ")
    self.tab1CalHintLabel = QLabel("  ")
    self.tab1CalHintLabel.setStyleSheet(style.grey1())
    self.tab1CalHintLabel.setTextInteractionFlags(
        Qt.TextInteractionFlag.TextSelectableByMouse
    )

    self.calibrationLayoutBtm.addLayout(layout)
    self.calibrationLayoutBtm.addLayout(grid)
    self.calibrationLayoutBtm.addWidget(self.tab1CalHintLabel)

    layout1 = QVBoxLayout()
    layout2 = QVBoxLayout()
    layout.addLayout(layout1)
    layout.addStretch()
    layout.addLayout(layout2)

    label_step2_1 = QLabel(" Step 2: Combo Log Study")
    label_step2_1.setStyleSheet(style.body1())
    label_step2_2 = QLabel("Plot data at two time points:")
    self.rowNumRadioButton = QRadioButton("Use Row Numbers: ", self)

    layout1.addWidget(label_step2_1)
    layout1.addWidget(label_step2_2)
    layout1.addWidget(self.rowNumRadioButton)

    self.plotComboButton = QPushButton("  Plot  ", self)
    self.plotComboButton.clicked.connect(lambda: func_calibration.combo_study(self))
    self.plotComboButton.setStyleSheet("font: bold")
    self.stopPlotComboButton = QPushButton("Stop Plot", self)
    self.stopPlotComboButton.clicked.connect(
        lambda: func_calibration.stop_combo_plot(self)
    )
    self.stopPlotComboButton.setEnabled(False)
    self.stopPlotComboButton.setToolTip(
        "To stop combo plot, change the value of 'par1/combo_stop.txt' to 1."
    )

    layout2.addWidget(self.plotComboButton)
    layout2.addWidget(self.stopPlotComboButton)

    gap = QLabel()
    label_step2_row1 = QLabel("Row 1")
    self.row1LineEdit = QLineEdit()
    self.row1LineEdit.setToolTip("Leave blank to use\nthe default value: 50")

    label_step2_row2 = QLabel("vs Row 2")
    self.row2LineEdit = QLineEdit()
    self.row2LineEdit.setToolTip("Leave blank to use\nthe default value: 100")

    self.peakRadioButton = QRadioButton("Use Peak Height (droplet only): ", self)
    label_step2_peak1 = QLabel("Peak")
    label_step2_peak2 = QLabel("vs Percentage %:")
    label_step2_peak2.setAlignment(Qt.AlignmentFlag.AlignRight)
    self.peakPecentageLineEdit = QLineEdit("10")

    self.peakRadioButton.setChecked(True)
    self.tab1_bg3 = QButtonGroup()
    self.tab1_bg3.addButton(self.rowNumRadioButton)
    self.tab1_bg3.addButton(self.peakRadioButton)

    label_step2_range1 = QLabel(
        "Row Range for Plots:"
    )
    label_step2_range2 = QLabel("From:")
    label_step2_range3 = QLabel("To:")
    label_step2_range3.setAlignment(Qt.AlignmentFlag.AlignRight)
    self.comboRange1LineEdit = QLineEdit()
    self.comboRange1LineEdit.setToolTip("Leave blank to use\nthe default value: minimal")
    self.comboRange2LineEdit = QLineEdit()
    self.comboRange2LineEdit.setToolTip("Leave blank to use\nthe default value: maximal")

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

    func_experiment.choose_droplet(self)
    self.dropletRadioButton.toggled.connect(
        lambda: func_experiment.choose_droplet(self)
    )
    self.tankRadioButton.toggled.connect(lambda: func_experiment.choose_tank(self))


if __name__ == "__main__":
    print()
