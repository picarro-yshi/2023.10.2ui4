## VOC Automation: Calibration, experiment and calculation
## Yilin Shi | Picarro | last update: 2023.12.18

# ----- constants -------
PORT_IN = 50070  ## backdoor, send data to fitter on analyzer
PORT_OUT = 40060  ## listener, get data from analyzer
ANALYZER_SRC = "analyze_VOC_bb_FOUP_FOUP" #"analyze_VOC_broadband_custom" #"analyze_VOC_broadband"  ## listener data key
MFC_REFRESH_TIME = 2000  # ms
PLOT_REFRESH_TIME = 2000  # ms
DATA_RECEIVE_TIME = 10000  # ms

# ------------
import sys
import platform

opsystem = platform.system()  # 'Linux', 'Windows', 'Darwin'
print(opsystem)

import serial.tools.list_ports as ls
print([p.device for p in ls.comports()])

from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QToolButton,
    QLabel,
    QComboBox,
    QMessageBox,
    QLineEdit,
    QRadioButton,
    QPushButton,
)

import pyqtgraph as pg

import style
from utilities import (
    func_analyzer,
    func_mfc,
    # func_calibration,
    func_experiment,
    func_scale,
    func_power,
    load_par,
    layout1,
    layout4,
)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VOC Calibration")

        self.setGeometry(350, 50, 1200, 800)
        if opsystem == "Darwin":
            self.setMinimumSize(1200, 880)
        elif opsystem == "Windows":
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
        self.timer_baseline.timeout.connect(
            lambda: func_experiment.track_baseline1(self)
        )

        self.timer_data = QTimer()
        self.timer_data.setInterval(DATA_RECEIVE_TIME)  # data manager
        self.timer_data.timeout.connect(lambda: func_experiment.data_manager(self))

        self.timer_auto = QTimer()
        self.timer_auto.setInterval(300000)  # ms, check loss every 5 mins
        self.timer_auto.timeout.connect(lambda: func_experiment.auto_flow(self))

    def set_window_layout(self):
        self.mainlayout()
        self.tab3_layout()  # hardware needed
        load_par.load_tab3(self)

        layout1.tab1_layout(self)
        self.tab2_layout()

        # load parameters
        load_par.load_tab1(self)
        load_par.get_port(self)
        layout4.tab4_layout(self)  # sql table
        self.tab5_layout()


    def mainlayout(self):
        mainLayout = QVBoxLayout()
        tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        tabs.addTab(self.tab1, "     ⬥ Experiment Settings     ")
        tabs.addTab(self.tab2, "  ⬥ Spectrum Viewer Real Time  ")
        tabs.addTab(self.tab3, "     ⬥ Hardware Detection      ")
        tabs.addTab(self.tab4, "     ⬥ Compound Inventory      ")
        # tabs.addTab(self.tab5, "     ⬥ Heater Power Switch     ")

        mainLayout.addWidget(tabs)
        self.setLayout(mainLayout)
        self.show()


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
        label1 = QLabel("  Start")

        self.stopPlotButton = QToolButton()
        self.stopPlotButton.setIcon(QIcon("icons/stop1.png"))
        self.stopPlotButton.setIconSize(QSize(40, 40))
        self.stopPlotButton.setToolTip("Close")
        self.stopPlotButton.clicked.connect(lambda: func_experiment.stop_plot(self))
        self.stopPlotButton.setEnabled(False)
        label2 = QLabel("  Stop")

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
        pixmap1 = QPixmap("icons/droplet_setup.png")
        image1.setPixmap(
            pixmap1.scaled(
                550,
                300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )
        image1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image2 = QLabel()
        pixmap2 = QPixmap("icons/gas_setup.png")
        image2.setPixmap(
            pixmap2.scaled(
                320,
                200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )
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
        grid4 = QGridLayout()  # power switch for heater

        self.tab3_layout_left.addStretch()
        self.tab3_layout_left.addLayout(layout1)
        self.tab3_layout_left.addLayout(grid1)
        self.tab3_layout_left.addLayout(grid2)
        self.tab3_layout_left.addLayout(grid3)
        self.tab3_layout_left.addLayout(grid4)
        self.tab3_layout_left.addStretch()

        # system
        label0 = QLabel("Your system:")
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()

        self.portListLabel = QLabel()
        self.portListLabel.setStyleSheet("background-color: white")
        self.portListLabel.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        layout1.addWidget(label0)
        layout1.addLayout(layout2)
        layout1.addLayout(layout3)
        layout1.addWidget(self.portListLabel)

        rb1 = QRadioButton("Windows", self)
        rb2 = QRadioButton("Mac", self)
        rb3 = QRadioButton("Linux", self)

        if opsystem == "Darwin":
            rb1.setEnabled(False)
            rb2.setChecked(True)
            rb3.setEnabled(False)
        elif opsystem == "Linux":
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
        button_analyzer1.clicked.connect(
            lambda: func_analyzer.detect_analyzer_portin(self)
        )
        self.analyzerPortInHintLabel = QLabel()

        label_analyzer4 = QLabel("Port Out: ")
        label_analyzer_portout = QLabel(
            "40060 (Receiving data from analyzer/ listener)"
        )

        button_analyzer2 = QPushButton("Detect")
        button_analyzer2.clicked.connect(
            lambda: func_analyzer.detect_analyzer_portout(self)
        )
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
        mfc1Button.clicked.connect(lambda: func_mfc.detect_mfc1(self))
        label_mfc4 = QLabel("dilution line, 1 SLPM")
        self.alicatMFC1HintLabel = QLabel()

        label_mfc5 = QLabel("MFC2 (large) Address: ")
        self.MFC2largeAddressLineEdit = QLineEdit()
        mfc2largeButton = QPushButton("Detect")
        mfc2largeButton.clicked.connect(lambda: func_mfc.detect_mfc2large(self))
        label_mfc6 = QLabel("Bubble line, 100 sccm")
        self.alicatMFC2LargeHintLabel = QLabel()

        label_mfc7 = QLabel("MFC2 (small) Address: ")
        self.MFC2smallAddressLineEdit = QLineEdit()
        mfc2smallButton = QPushButton("Detect")
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

        # Heater power switch
        label_power1 = QLabel("Heat Tape Power Switch")
        label_power1.setStyleSheet(style.headline2())

        label_power2 = QLabel("IP Address of this Computer: ")
        self.computerIPAddressLineEdit = QLineEdit()
        button_computerIP = QPushButton("Get")
        button_computerIP.clicked.connect(lambda: func_power.ip_thisPC(self))

        label_power3 = QLabel("IP Address of Power Switch: ")
        self.powerSwitchIPAddressLineEdit = QLineEdit()
        button_powerIP = QPushButton("Detect")
        button_powerIP.clicked.connect(lambda: func_power.power_connect(self))
        self.powerHintLabel = QLabel()

        label_heater1 = QLabel("Heater 1:")
        label_heater1.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.heater1Button = QPushButton("ON/OFF")
        self.heater1Button.clicked.connect(lambda: func_power.button_click(self, 1, self.heater1Button))
        self.heater1Button.setEnabled(False)

        label_heater2 = QLabel("Heater 2:")
        label_heater2.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.heater2Button = QPushButton("ON/OFF")
        self.heater2Button.clicked.connect(lambda: func_power.button_click(self, 2, self.heater2Button))
        self.heater2Button.setEnabled(False)

        grid4.addWidget(label_power1, 0, 0, 1, 4)
        grid4.addWidget(label_power2, 1, 0, 1, 2)
        grid4.addWidget(self.computerIPAddressLineEdit, 1, 2, 1, 2)
        grid4.addWidget(button_computerIP, 1, 4)

        grid4.addWidget(label_power3, 2, 0, 1, 2)
        grid4.addWidget(self.powerSwitchIPAddressLineEdit, 2, 2, 1, 2)
        grid4.addWidget(button_powerIP, 2, 4)
        grid4.addWidget(self.powerHintLabel, 2, 5)

        grid4.addWidget(label_heater1, 3, 0)
        grid4.addWidget(self.heater1Button, 3, 1)
        grid4.addWidget(label_heater2, 3, 3)
        grid4.addWidget(self.heater2Button, 3, 4)



    def tab5_layout(self):
        mainLayout = QVBoxLayout()
        self.tab5.setLayout(mainLayout)

        # web = QWebEngineView()
        # mainLayout.addWidget(web)
        # web.load(QUrl("http://10.100.2.71/api/control?target=outlet2&action=off"))
        # web.show()


    # //////////////////// functions
    # in utility folder


    def exitFunc(self, event):
        reply = QMessageBox.question(
            self,
            "Message",
            "Are you sure to quit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.close()


def main():
    app = QApplication(sys.argv)
    window = Window()
    app.setWindowIcon(QIcon("icons/logo.png"))
    window.show()
    app.exec()


if __name__ == "__main__":
    main()

# @author: Yilin Shi | 2023.9.15
# shiyilin890@gmail.com
# Bog the Fat Crocodile vvvvvvv
#                       ^^^^^^^
