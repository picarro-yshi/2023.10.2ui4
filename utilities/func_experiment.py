## run experiment
import os
import sys
import time
import numpy as np
from PyQt6.QtWidgets import QMessageBox

from utilities import func_analyzer, func_mfc

path_current = os.getcwd()  # when cited from gui1 this will be parent path
# path_parent= os.path.abspath(os.path.join(path_current, os.pardir))
# PARAMETER_PATH = os.path.join(path_parent, "par1")
PARAMETER_PATH = os.path.join(path_current, "par1")
print(PARAMETER_PATH)

from queue import Queue
from Listener_py3 import Listener
import StringPickler_py3 as StringPickler

BASELINE_Time = 20  # min, sample baseline time
PLOT_WINDOW_LENGTH = 1  # hour, time length for plot window
# window_points = int(PLOT_WINDOW_LENGTH * 3600 / 5)  # about 5/s generates a point
# baseline_points = int(BASELINE_Time * 60 / 5)
ANALYZER_SOURCE2 = "analyze_VOC_1"


def choose_droplet(self):
    self.dropletRadioButton.setStyleSheet("color: red")
    self.tankRadioButton.setStyleSheet("color: black")
    self.weightTitleLabel.setDisabled(False)  # weight
    self.sampleWeightLineEdit.setDisabled(False)
    self.tankTitleLabel.setDisabled(True)  # tank conc
    self.sampleTankConcLineEdit.setDisabled(True)
    self.aqCheckbox.setDisabled(False)  # aqueous droplet
    self.automationCheckbox.setDisabled(False)

    ## button tips
    self.expStartButton.setToolTip("Start experiment,\nsend Alicat data to analyzer.\n"
                                   "Record start time.")
    self.expAddButton.setToolTip("Steps:\n->Stop bubble line flow\n->Add sample \n"
                                 "->Click this button to\n record time and weight.")


def choose_tank(self):
    self.dropletRadioButton.setStyleSheet("color: black")
    self.tankRadioButton.setStyleSheet("color: red")
    self.weightTitleLabel.setDisabled(True)  # weight
    self.sampleWeightLineEdit.setDisabled(True)
    self.tankTitleLabel.setDisabled(False)  # tank conc.
    self.sampleTankConcLineEdit.setDisabled(False)
    self.aqCheckbox.setDisabled(True)  # aqueous droplet
    self.automationCheckbox.setDisabled(True)

    ## button tips
    self.expStartButton.setToolTip("Start experiment.\nRecord start time.")
    self.expAddButton.setToolTip("Steps:\nDisconnect Zero Air line\n->Connect sample line\n"
                                 "->Click this button to record\n"
                                 " time and tank concentration.")


def input_check(self):
    r_drive = self.sampleRDriveLineEdit.toPlainText()
    sample = self.sampleNameLineEdit.text()
    cid = self.sampleCIDLineEdit.text()

    start_day = time.strftime("%Y%m%d")  # today's date
    self.expStartLineEdit.setText(start_day)
    suffix = self.expSuffix.text()
    self.experiment_path = os.path.join(r_drive, sample, start_day + suffix)

    # check GUI input field
    tag = 0
    if r_drive == '':
        self.tab1ExperimentHint.setText(' ! Error: Please type in R drive location.\n')
    elif sample == '':
        self.tab1ExperimentHint.setText(' ! Error: Please type in sample name.\n')
    elif cid == '':
        self.tab1ExperimentHint.setText(' ! Error: Please type in CID number.\n')
    elif not os.path.exists(r_drive):
        self.tab1ExperimentHint.setText(' ! Error: R/Data drive not found.\n')
    elif not os.path.exists(os.path.join(r_drive, sample)):
        self.tab1ExperimentHint.setText(' ! Error: %s folder not found on R drive.\n' % sample)
    elif os.path.exists(self.experiment_path):
        self.tab1ExperimentHint.setText(' ! Error: folder %s already exists.\n'
                                        'Please delete or rename the folder.' % (start_day + suffix))
    else:
        # print("GUI input check passed")
        tag = 1

    if tag:
        # droplet
        if self.dropletRadioButton.isChecked():
            tag = 0
            if self.sampleMWLineEdit.text() == '':  # MW
                self.tab1ExperimentHint.setText(' ! Error: Please type in sample molecular weight.\n')
            elif not func_mfc.detect_mfc1(self):  # MFC1
                self.tab1ExperimentHint.setText(' ! Error: MFC1 not connected.\n')
            else:
                if self.mfc100RadioButton.isChecked():
                    if not func_mfc.detect_mfc2large(self):
                        self.tab1ExperimentHint.setText(' ! Error: MFC2(100 sccm) not connected.\n')
                    else:
                        tag = 1
                else:
                    if not func_mfc.detect_mfc2small(self):
                        self.tab1ExperimentHint.setText(' ! Error: MFC2(10 sccm) not connected.\n')
                    else:
                        print("MFC check passed")
                        tag = 1
        # tank
        else:
            if self.sampleTankConcLineEdit.text() == '':  # tank_conc
                self.tab1ExperimentHint.setText(' ! Error: Please type in tank concentration.\n')
                tag = 0
    return tag


def datakey_check(self):
    cid = self.sampleCIDLineEdit.text()
    self.datakey = "broadband_gasConcs_%s" % cid
    lib_value = 'broadband_eCompoundOutputs_' + cid + '_calibration'
    self.datakeyLabel.setText(self.datakey)
    self.plotKeyLabel.setText("Data Key for Plot: broadband_gasConcs_%s" % cid)

    dm_queue = Queue(180)  ## data manager
    listener = Listener(dm_queue, self.host, self.port_out, StringPickler.ArbitraryObject, retry=True)

    tag = 0
    for j in range(20):
        dm = dm_queue.get(timeout=5)
        if dm['source'] == self.analyzer_source:
            if 'time' not in dm['data']:
                self.tab1ExperimentHint.setText(" ! Error: Missing datakey 'time'.\nPlease try again.")
            elif self.datakey not in dm['data']:
                self.tab1ExperimentHint.setText(" ! Error: Missing datakey '%s'.\nPlease try again." % self.datakey)
            elif lib_value not in dm['data']:
                self.tab1ExperimentHint.setText(" ! Error: Missing datakey '%s'.\nPlease try again." % lib_value)
            else:
                tag = 1
                # print(dm['data']['time'])
                # print(dm['data'][self.datakey])
                # print(dm['data'][lib_value])

            if tag:
                if self.dropletRadioButton.isChecked():  # check datakey: MFC1_flow, MFC2_flow
                    if 'MFC1_flow' not in dm['data']:
                        self.tab1ExperimentHint.setText(" ! Error: Missing datakey dm['MFC1_flow'].\nPlease try again.")
                        tag = 0
                    elif 'MFC2_flow' not in dm['data']:
                        self.tab1ExperimentHint.setText(" ! Error: Missing datakey dm['MFC2_flow'].\nPlease try again.")
                        tag = 0

        if tag:
            print("data key check passed")
            break
    return tag


def create_experiment(self):
    # open the N2 gas
    set_MFC2_flow(self)

    # input error check, fill in start day, check MFC connection
    tag = input_check(self)

    # check analyzer port
    if tag:
        tag = func_analyzer.detect_analyzer_portin(self)

    if tag:
        data_speed = func_analyzer.detect_analyzer_portout(self)
        if data_speed:
            # ideal value:
            print("analyzer port check passed, fitter data speed (s/pt): %s" % data_speed)
            # if data_speed < 5:  # set uplimit of points, faster speed may have too many points
            #     data_speed = 5
            # elif data_speed > 8:  # bottom line, slow speed wait too long
            #     data_speed = 8

            self.window_points = int(PLOT_WINDOW_LENGTH * 3600 / data_speed)
            self.baseline_points = int(BASELINE_Time * 60 / data_speed)
            print(self.window_points, self.baseline_points)

            # practical value: very slow, 3~4 points/min
            self.window_points = int(PLOT_WINDOW_LENGTH * 60 * 4)
            self.baseline_points = int(BASELINE_Time * 4)
            print(self.window_points, self.baseline_points)
        else:
            tag = 0

    # send MFC data to analyzer if not yet
    if tag:
        if self.dropletRadioButton.isChecked():
            if self.sendMFCButton.isEnabled():
                func_mfc.send_MFC_data(self)

    # check if datakey exist
    if tag:
        tag = datakey_check(self)
        
    # tab2 plot
    if tag:
        # self.startPlotButton.setEnabled(True)
        # self.stopPlotButton.setEnabled(False)
        if self.plotCheckbox.isChecked():
            start_plot(self)

    # everything is ready, we can run experiment now
    if tag:
        print("all checks passed!")
        # set_MFC2_flow(self)

        try:
            # data manager
            self.dm_queue = Queue(180)  ## data manager
            listener = Listener(self.dm_queue, self.host, self.port_out, StringPickler.ArbitraryObject, retry=True)
            self.timer_data.start()
            print('data manager timer started')

            # start plot fresh
            self.graphWidget.clear()
            self.x = []
            self.y = []
            self.xtick = []
            self.baseline = []

            try:
                self.sample_sigma = int(self.sampleSigmaCombobox.currentText())
            except:
                self.sampleSigmaCombobox.setCurrentText("4")
                self.sample_sigma = 4

            # clear entry fields
            self.expStartCombobox1.setCurrentText('00')
            self.expStartCombobox2.setCurrentText('00')
            self.expAddLineEdit.setText('')
            self.expAddCombobox1.setCurrentText('00')
            self.expAddCombobox2.setCurrentText('00')
            self.expEndLineEdit.setText('')
            self.expEndCombobox1.setCurrentText('00')
            self.expEndCombobox2.setCurrentText('00')

            self.tab1ExperimentHint.setText(" ")
            self.weightLabel.setText('0.00000')  # weight in 'Scale'
            self.sampleWeightLineEdit.setText('')  # weight in 'Calibration'

            # create folder
            os.mkdir(self.experiment_path)
            fnrp = os.path.join(self.experiment_path, 'par')
            os.mkdir(fnrp)

            save_parameter_local(self)
            save_parameter_R(self)
            print('parameters saved')

            # enable, disable
            self.tab1CreateExpButton.setEnabled(False)
            self.expStartButton.setEnabled(True)
            if self.dropletRadioButton.isChecked():
                self.tankRadioButton.setEnabled(False)
            else:
                self.dropletRadioButton.setEnabled(False)

            start_day = self.expStartLineEdit.text()
            suffix = self.expSuffix.text()
            self.tab1ExperimentHint.setText(
                "• Experiment %s created!\nYou may press the start button now." % (start_day + suffix))
        except:
            self.tab1ExperimentHint.setText(' ! Error creating experiment.\n')


## save parameters locally for the GUI
def save_parameter_local(self):
    try:
        p = os.path.join(PARAMETER_PATH, 'r_drive.txt')
        with open(p, 'w') as f:
            f.write(self.sampleRDriveLineEdit.toPlainText())

        p = os.path.join(PARAMETER_PATH, 'sample.txt')
        with open(p, 'w') as f:
            f.write(self.sampleNameLineEdit.text())

        p = os.path.join(PARAMETER_PATH, 'cid.txt')
        with open(p, 'w') as f:
            f.write(self.sampleCIDLineEdit.text())

        if self.dropletRadioButton.isChecked():
            p = os.path.join(PARAMETER_PATH, 'molecular_weight.txt')
            with open(p, 'w') as f:
                f.write(self.sampleMWLineEdit.text())

        if self.tankRadioButton.isChecked():
            p = os.path.join(PARAMETER_PATH, 'tankconc.txt')
            with open(p, 'w') as f:
                f.write(self.sampleTankConcLineEdit.text())
    except:
        print("Error saving parameters locally.")


## save parameters on R drive
def save_parameter_R(self):
    try:
        fnrp = os.path.join(self.experiment_path, 'par')
        p = os.path.join(fnrp, 'sample.txt')
        with open(p, 'w') as f:
            f.write(self.sampleNameLineEdit.text())

        p = os.path.join(fnrp, 'cid.txt')
        with open(p, 'w') as f:
            f.write(self.sampleCIDLineEdit.text())

        if self.dropletRadioButton.isChecked():
            p = os.path.join(fnrp, 'molecular_weight.txt')
            with open(p, 'w') as f:
                f.write(self.sampleMWLineEdit.text())

        if self.tankRadioButton.isChecked():
            p = os.path.join(fnrp, 'tankconc.txt')
            with open(p, 'w') as f:
                f.write(self.sampleTankConcLineEdit.text())
    except:
        self.tab1ExperimentHint.setText(" ! Failed to save parameters on R drive.\n")


def save_parameter_R_time(self):
    # start
    fnrt = os.path.join(self.experiment_path, 'par', 't1.txt')
    # if os.path.isfile(fnrt):
    #     os.remove(fnrt)
    # with open(fnrt, 'a') as f:
    #     f.write(self.expStartLineEdit.text() + '\n')
    #     f.write(self.expStartCombobox1.currentText() + '\n')
    #     f.write(self.expStartCombobox2.currentText() + '\n')

    with open(fnrt, 'w') as f:
        f.write("%s\n%s\n%s" % (
            self.expStartLineEdit.text(),
            self.expStartCombobox1.currentText(),
            self.expStartCombobox2.currentText()
        ))

    # add
    fnrt = os.path.join(self.experiment_path, 'par', 't2.txt')
    # if os.path.isfile(fnrt):
    #     os.remove(fnrt)
    # with open(fnrt, 'a') as f:
    #     f.write(self.expAddLineEdit.text() + '\n')
    #     f.write(self.expAddCombobox1.currentText() + '\n')
    #     f.write(self.expAddCombobox2.currentText() + '\n')
    with open(fnrt, 'w') as f:
        f.write("%s\n%s\n%s" % (
            self.expAddLineEdit.text(),
            self.expAddCombobox1.currentText(),
            self.expAddCombobox2.currentText()
        ))

    # end
    fnrt = os.path.join(self.experiment_path, 'par', 't3.txt')
    # if os.path.isfile(fnrt):
    #     os.remove(fnrt)
    # with open(fnrt, 'a') as f:
    #     f.write(self.expEndLineEdit.text() + '\n')
    #     f.write(self.expEndCombobox1.currentText() + '\n')
    #     f.write(self.expEndCombobox2.currentText() + '\n')
    with open(fnrt, 'w') as f:
        f.write("%s\n%s\n%s" % (
            self.expEndLineEdit.text(),
            self.expEndCombobox1.currentText(),
            self.expEndCombobox2.currentText()
        ))


# def plot_spectrum(self):
#     self.graphWidget.clear()
#     self.x = []
#     self.y = []
#     self.xtick = []
#     self.baseline = []
# 
#     self.timer_plot.start()  # start plot fresh
#     print('viewer started')


def data_manager(self):
    try:
        # dm_queue = Queue(180)  ## data manager
        # listener = Listener(dm_queue, self.host, self.port_out, StringPickler.ArbitraryObject, retry=True)
        dm = self.dm_queue.get(timeout=5)

        if dm['source'] == self.analyzer_source:
            if len(self.y) == self.window_points:  ## x-axis number
                self.x.pop(0)
                self.y.pop(0)

            t = dm['time']
            self.x.append(t)
            self.y.append(dm['data'][self.datakey])

            if len(self.y) > self.baseline_points:
                self.baseline = self.y[-self.baseline_points:]
            else:
                self.baseline = self.y
            # print(self.baseline)

            clock = time.strftime('%H:%M', time.localtime(self.x[-1]))
            # print('clock', clock)
            # print(self.xtick)
            if self.xtick:
                clock0 = time.strftime(
                    "%H:%M", time.localtime(self.x[-2])
                )  # previous time string
                if (
                        (clock0[-2:] == "59" and clock[-2:] == "00")
                        or (clock0[-2:] == "29" and clock[-2:] == "30")
                        # or (clock0[-2:] == "14" and clock[-2:] == "15")
                        # or (clock0[-2:] == "44" and clock[-2:] == "45")
                ):
                    self.xtick.append((t, clock))
            else:  # no tick label yet, add current as the first one
                self.xtick.append((t, clock))
            # print(self.xtick)

            if self.xtick[0][0] < self.x[0]:
                self.xtick.pop(0)
            # print('len xtick', len(self.xtick))
    except:
        pass


def start_plot(self):
    self.startPlotButton.setEnabled(False)
    self.stopPlotButton.setEnabled(True)
    self.timer_plot.start()
    print('viewer started')


def stop_plot(self):
    self.startPlotButton.setEnabled(True)
    self.stopPlotButton.setEnabled(False)
    self.timer_plot.stop()


def plot_spectrum(self):
    # dm_queue = Queue(180)  ## data manager
    # listener = Listener(dm_queue, self.host, self.port_out, StringPickler.ArbitraryObject, retry=True)
    # dm = dm_queue.get(timeout=5)
    # if dm['source'] == analyzer_source:
    #     window_points = int(PLOT_WINDOW_LENGTH * 3600 / 5)  # about 5/s generates a point
    #     if len(self.y) == window_points:  ## x-axis number
    #         self.x.pop(0)
    #         self.y.pop(0)
    #
    #     t = dm['time']
    #     self.x.append(t)
    #     self.y.append(dm['data'][self.datakey])
    #
    #     baseline_pt = int(BASELINE_Time * 60 / 5)
    #     if len(self.baseline) == baseline_pt:  ## baseline points
    #         self.baseline.pop(0)
    #     self.baseline.append(dm['data'][self.datakey])

    # clock = time.strftime('%H:%M', time.localtime(t))  # current time
    # clock = time.strftime('%H:%M', self.x[-1])  # current time
    # if self.xtick:
    #     clock0 = time.strftime(
    #         "%H:%M", time.localtime(self.x[-2])
    #     )  # previous time string
    #     if (
    #         (clock0[-2:] == "59" and clock[-2:] == "00")
    #         or (clock0[-2:] == "14" and clock[-2:] == "15")
    #         or (clock0[-2:] == "44" and clock[-2:] == "45")
    #         or (clock0[-2:] == "29" and clock[-2:] == "30")
    #     ):
    #         self.xtick.append((t, clock))
    # else:  # no tick label yet, add current as the first one
    #     self.xtick.append((t, clock))
    #
    # if self.xtick[0][0] < self.x[0]:
    #     self.xtick.pop(0)

    try:
        self.graphWidget.plot(self.x, self.y, pen="k")
        ax = self.graphWidget.getAxis("bottom")
        ax.setTicks([self.xtick])
    except:
        print("error plot")


def set_MFC2_flow(self, percentage=1.0):
    if self.mfc100RadioButton.isChecked():
        flow = float(self.tab1MFC100Combobox.currentText()) * percentage
        func_mfc.set_mfc_100sccm(self, flow)
    else:
        flow = float(self.tab1MFC10Combobox.currentText()) * percentage
        func_mfc.set_mfc_10sccm(self, flow)

# start experiment, record time, no error check
def start_exp(self):
    try:
        # t1 = self.expStartLineEdit.text()
        t2 = time.strftime("%H")
        t3 = time.strftime("%M")
        self.expStartCombobox1.setCurrentText(t2)
        self.expStartCombobox2.setCurrentText(t3)

        self.expStartButton.setEnabled(False)
        self.expAddButton.setEnabled(True)
        self.expEndButton.setEnabled(True)

        # 30 min later: 20 min baseline+10 min, see spike when turn on bubble line
        self.epoch2 = int(time.time()) + BASELINE_Time * 60 + 660
        ep = time.strftime('%Y%m%d %H:%M:%S', time.localtime(self.epoch2))
        note1 = "• Experiment started at %s:%s!\nPlease wait at least 30min, until %s:%s to " % (t2, t3, ep[9:11], ep[12:14])
        if self.dropletRadioButton.isChecked():
            note2 = "add sample."
        else:
            note2 = "switch tank."
        self.tab1ExperimentHint.setText(note1 + note2)

    except:
        self.tab1ExperimentHint.setText(' ! Error start experiment.\n')


# add sample, get baseline 1
def add_sample(self):
    try:
        if int(time.time()) < self.epoch2:
            ep = time.strftime('%Y%m%d %H:%M:%S', time.localtime(self.epoch2))
            note = 'Please wait at least 30 min,\nuntil %s:%s to add sample.\n' % (ep[9:11], ep[12:14])
            reply = QMessageBox.question(self, 'Warning', note, QMessageBox.StandardButton.Ok)

        if self.dropletRadioButton.isChecked():
            print("check weight")
            weight = self.sampleWeightLineEdit.text()
            if not weight:
                note = 'Please type in sample weight!\n'
                reply = QMessageBox.question(self, 'Warning', note, QMessageBox.StandardButton.Ok)

        ## get baseline 1:
        print('len baseline', len(self.baseline))
        if len(self.baseline) > 20:
            baseline_before = self.baseline[:-10]
        else:  # cheater to waive the 30-min baseline requirement
            baseline_before = self.baseline
            print('baseline_before = baseline')

        self.zero1 = np.mean(baseline_before)
        self.sigma1 = np.std(baseline_before)

        print('zero1, sample added:')
        print(time.ctime(time.time()))
        print(self.zero1)
        print(self.sigma1)

        # track baseline
        self.timer_baseline.start()

        t1 = time.strftime("%Y%m%d")
        t2 = time.strftime("%H")
        t3 = time.strftime("%M")
        self.expAddLineEdit.setText(t1)  # '20211124'
        self.expAddCombobox1.setCurrentText(t2)  # '08'
        self.expAddCombobox2.setCurrentText(t3)  # '00'

        self.expAddButton.setEnabled(False)
        if self.dropletRadioButton.isChecked():
            self.note1 = "• Sample added at %s:%s! Please run until baseline is stable.\n" \
                         "Baseline before: %.4E" % (t2, t3, self.zero1)

            # automation
            if self.automationCheckbox.isChecked():
                # use 20% of the set flow for start
                set_MFC2_flow(self, 0.2)
                # if self.mfc100RadioButton.isChecked():
                #     flow = float(self.tab1MFC100Combobox.currentText())/5
                #     func_mfc.set_mfc_100sccm(self, flow)
                # else:
                #     flow = float(self.tab1MFC10Combobox.currentText())/5
                #     func_mfc.set_mfc_10sccm(self, flow)

                self.auto_tag1 = 1  # full flow
                self.auto_tag2 = 0  # maximum flow
                self.auto_tag3 = 0  # stop flow
                # self.auto_tag4 = 0  # stop flow
                self.timer_auto.start()
                print("auto step1: set to 20% flow rate.")
            else:
                set_MFC2_flow(self)
                # if self.mfc100RadioButton.isChecked():
                #     flow = float(self.tab1MFC100Combobox.currentText())
                #     func_mfc.set_mfc_100sccm(self, flow)
                # else:
                #     flow = float(self.tab1MFC10Combobox.currentText())
                #     func_mfc.set_mfc_10sccm(self, flow)

            self.automationCheckbox.setDisabled(True)

        else:
            self.note1 = "• Sample tank connected at %s:%s! Please run until baseline is stable.\n" \
                         "Baseline std before: %.4f" % (t2, t3, self.sigma1)
        self.tab1ExperimentHint.setText(self.note1)
        save_parameter_R_time(self)

    except:
        self.tab1ExperimentHint.setText(' ! Error record add sample time.\n')


def update_endtime(self):
    fnrt = os.path.join(self.experiment_path, 'par', 't3.txt')
    t1 = time.strftime("%Y%m%d")
    t2 = time.strftime("%H")
    t3 = time.strftime("%M")
    self.expEndLineEdit.setText(t1)  # autofill, as a message, baseline is low enough and experiment can stop
    self.expEndCombobox1.setCurrentText(t2)
    self.expEndCombobox2.setCurrentText(t3)

    with open(fnrt, 'w') as f:
        f.write("%s\n%s\n%s" % (t1, t2, t3))


def track_baseline1(self):
    try:
        zero2 = np.mean(self.baseline)
        sigma2 = float(np.std(self.baseline))

        print('zero2, sigma2: ', zero2, sigma2)
        print(time.ctime(time.time()))

        if self.dropletRadioButton.isChecked():
            if self.expEndLineEdit.text() == "":
                self.tab1ExperimentHint.setText(self.note1 + ', now: %.4E' % zero2)

            if zero2 < self.zero1 + self.sigma1 * self.sample_sigma:  # record value on GUI
                update_endtime(self)
                print('dropped below')
                self.tab1ExperimentHint.setText('• Concentration has dropped below baseline+%s sigma. You may end now\n'
                                         'Baseline before: %.4E, now: %.4f' % (self.sample_sigma, self.zero1, zero2))

                # stop plot to save memory
                self.timer_plot.stop()

        else:
            if self.expEndLineEdit.text() == "":
                self.tab1ExperimentHint.setText(self.note1 + ', now: %.4E' % sigma2)

            if sigma2 < self.sigma1 * 1.1:  # 1.05
                update_endtime(self)




        # if self.expEndLineEdit.text() == "":
        #     if self.dropletRadioButton.isChecked():
        #         self.tab1ExperimentHint.setText(self.note1 + ', now: %.4E' % zero2)
        #     else:
        #         self.tab1ExperimentHint.setText(self.note1 + ', now: %.4E' % sigma2)


        # if zero2 < self.zero1 + self.sigma1 * self.sample_sigma:  # record value when sees baseline+n*sigma


            # fnrt = os.path.join(self.experiment_path, 'par', 't3.txt')
            # t1 = time.strftime("%Y%m%d")
            # t2 = time.strftime("%H")
            # t3 = time.strftime("%M")
            # self.expEndLineEdit.setText(t1)  # autofill, as a message, baseline is low enough and experiment can stop
            # self.expEndCombobox1.setCurrentText(t2)
            # self.expEndCombobox2.setCurrentText(t3)
            #
            # with open(fnrt, 'w') as f:
            #     f.write("%s\n%s\n%s" % (t1, t2, t3))

            self.tab1ExperimentHint.setText('• Baseline is stable for the past 30-min. You may end now\n'
                                            'Baseline std before: %.4E, now: %.4E' % (
                                                self.sigma1, sigma2))
    except:
        self.tab1ExperimentHint.setText(' ! Error: Failed to track baseline.\n')


def track_loss(self):
    try:
        if self.auto_tag1:
            # dm_queue = Queue(180)  ## data manager
            # listener = Listener(dm_queue, self.host, self.port_out, StringPickler.ArbitraryObject, retry=True)
            loss = 0

            for i in range(20):
                dm = self.dm_queue.get(timeout=5)
                if dm['source'] == ANALYZER_SOURCE2:
                    loss = int(dm['data']['max_loss'])
                    print("loss", loss)
                    break
        
        # avoid the spike, set to full flow rate after steps * 5min
            if loss == 0:
                self.tab1ExperimentHint.setText(" ! Error: no loss value.\n")
            elif loss < 750:
                set_MFC2_flow(self)
                # if self.dropletRadioButton.isChecked():
                #     flow = float(self.tab1MFC100Combobox.currentText())
                #     func_mfc.set_mfc_100sccm(self, flow)
                # else:
                #     flow = float(self.tab1MFC10Combobox.currentText())
                #     func_mfc.set_mfc_10sccm(self, flow)

                self.auto_tag1 = 0
                self.auto_tag2 = 1
                print("auto step2: set to full flow rate.  ", time.ctime(time.time()))

            elif loss > 1500:
                self.tab1ExperimentHint.setText(" ! Concentration too high, failed to automate the experiment.\n"
                                                " Please leave it run, or reduce flow and try again.")
                self.timer_auto.stop()

        # if self.auto_tag2:
        #     # set to full flow rate
        #     if self.mfc100RadioButton.isChecked():
        #         func_mfc.set_mfc_100sccm(self)
        #     else:
        #         func_mfc.set_mfc_10sccm(self)
        #     self.auto_tag2 = 0
        #     self.auto_tag3 = 1
        # print("auto step3: set to full flow rate.  ", time.ctime(time.time()))

        # set to maximum flow after baseline drop to e-07 '3.016901661630596e-07'
        if self.auto_tag2:
            # concentration = self.y[-1]
            print(self.y[-1])
            print(self.y[-1]+1)
            if self.y[-1] < 5e-7 and self.y[-2] < 5e-7:
                if self.dropletRadioButton.isChecked():
                    func_mfc.set_mfc_100sccm(self, 100)
                else:
                    func_mfc.set_mfc_10sccm(self, 10)
                self.auto_tag2 = 0
                self.auto_tag3 = 1
                print("auto step3: set to maximum flow rate for quick clean.  ", time.ctime(time.time()))

        # shut down gas flow after experiment ends
        if self.auto_tag3:
            if not self.expEndLineEdit.text() == "":
                end_exp(self)
                # time.sleep(60)
                # func_mfc.set_mfc_1slpm(self, 0)
                # func_mfc.stop_flow(self)
                # self.timer_auto.stop()
    except:
        print('Failed to automate the experiment')


def end_exp(self):
    # easy things first
    if self.dropletRadioButton.isChecked():
        fnrp = os.path.join(self.experiment_path, 'par')
        p = os.path.join(fnrp, 'weight.txt')
        with open(p, 'w') as f:
            f.write(self.sampleWeightLineEdit.text())

    # fill in end time
    note = ''
    if not self.expEndLineEdit.text():
        note = 'Your baseline may still be higher than before experiment start.'

    t1 = time.strftime("%Y%m%d")
    t2 = time.strftime("%H")
    t3 = time.strftime("%M")
    self.expEndLineEdit.setText(t1)  ## '20211124'
    self.expEndCombobox1.setCurrentText(t2)
    self.expEndCombobox2.setCurrentText(t3)
    self.tab1ExperimentHint.setText('• Experiment ended at %s:%s.\n%s' % (t2, t3, note))

    # stop the plot
    if self.stopPlotButton.isEnabled():
        stop_plot(self)
    self.startPlotButton.setEnabled(False)

    self.timer_baseline.stop()  # track baseline
    self.timer_data.stop()  # data manager

    try:
        self.timer_auto.stop()
    except:
        pass

    if self.automationCheckbox.isChecked():
        func_mfc.stop_flow(self)
        func_mfc.set_mfc_1slpm(self, 0)
    # enough time to get the most recent time from line_edit
    save_parameter_R(self)
    save_parameter_R_time(self)

    # Enable, disable
    self.expEndButton.setEnabled(False)
    self.tab1CreateExpButton.setEnabled(True)
    if self.dropletRadioButton.isChecked():
        self.tankRadioButton.setEnabled(True)
        self.automationCheckbox.setDisabled(False)
    else:
        self.dropletRadioButton.setEnabled(True)



if __name__ == "__main__":
    # needs to comment out the import at top due to different parent directory
    import func_analyzer

    tag = func_analyzer.detect_analyzer_portin_local()
    print(tag)
    print()
