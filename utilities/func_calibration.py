## calibration functions
import sys
import os
import datetime
import matplotlib.pyplot as plt

jupyterpath = '../2023.10.1jupyter4/'
sys.path.append(jupyterpath)  ## jupyternotebook re-write
import combo_other, combo, droplet_aq, droplet, tank

from utilities import func_experiment

def load_experiment(self):
    # sanity check    
    r_drive = self.sampleRDriveLineEdit.toPlainText()
    self.sample = self.sampleNameLineEdit.text()
    start_day = self.expStartLineEdit.text()  # '20211124'
    suffix = self.expSuffix.text()
    self.experiment_path = os.path.join(r_drive, self.sample, start_day + suffix)

    fnrp = os.path.join(self.experiment_path, 'par')
    print(fnrp)

    tag = 0
    if not start_day:
        self.tab1CalHintLabel.setText('! Error: Please fill in the date(and/or suffix) of the experiment.')
    elif not os.path.isdir(r_drive):
        self.tab1CalHintLabel.setText('! Error: R drive not found.')
    elif not os.path.isdir(fnrp):
        self.tab1CalHintLabel.setText('! Error: parameters not found.')
    else:
        tag = 1

    if tag:
        try:
            f = open(os.path.join(fnrp, 't1.txt'), 'r')
            temp = f.read().splitlines()
            print(temp)
            self.expStartCombobox1.setCurrentText(temp[1])
            self.expStartCombobox2.setCurrentText(temp[2])

            f = open(os.path.join(fnrp, 't2.txt'), 'r')
            temp = f.read().splitlines()
            self.expAddLineEdit.setText(temp[0])
            self.expAddCombobox1.setCurrentText(temp[1])
            self.expAddCombobox2.setCurrentText(temp[2])

            f = open(os.path.join(fnrp, 't3.txt'), 'r')
            temp = f.read().splitlines()
            self.expEndLineEdit.setText(temp[0])
            self.expEndCombobox1.setCurrentText(temp[1])
            self.expEndCombobox2.setCurrentText(temp[2])

            f = open(os.path.join(fnrp, 'cid.txt'), 'r')
            temp = f.read()
            self.sampleCIDLineEdit.setText(temp)

            try:
                f = open(os.path.join(fnrp, 'row.txt'), 'r')
                temp = f.read()
                self.oneComboNumLineEdit.setText(temp)
            except:
                self.oneComboNumLineEdit.setText("")

            try:
                f = open(os.path.join(fnrp, 'n_sigma.txt'), 'r')
                temp = f.read()
                self.sampleSigmaCombobox.setCurrentText(temp)
            except:
                self.sampleSigmaCombobox.setCurrentText("4")

            if self.dropletRadioButton.isChecked():
                print('load droplet')
                f = open(os.path.join(fnrp, 'weight.txt'), 'r')
                temp = f.read()
                self.sampleWeightLineEdit.setText(temp)

                f = open(os.path.join(fnrp, 'molecular_weight.txt'), 'r')
                temp = f.read()
                self.sampleMWLineEdit.setText(temp)
            else:
                print('load gastank')
                f = open(os.path.join(fnrp, 'tankconc.txt'), 'r')
                temp = f.read()
                self.sampleTankConcLineEdit.setText(temp)

            self.tab1CalculateButton.setEnabled(True)
            self.PlotOneComboButton.setEnabled(True)
            self.tab1CalHintLabel.setText('⦿ Parameters  loaded.')
        except:
            self.tab1CalHintLabel.setText(' ! Error loading parameters for experiment %s.' % (start_day + suffix))


def calculation_check(self):
    self.tab1CalHintLabel.setText(" ")
    # fnzip1 = os.path.join(fnr, 'RDFs')  #RDF is not needed
    fnzip2 = os.path.join(self.experiment_path, 'PrivateData')
    fnzip3 = os.path.join(self.experiment_path, 'ComboResults')

    tag = 0  # sanity check
    if not os.path.isdir(self.experiment_path):
        self.tab1CalHintLabel.setText(' ! Error: experiment folder on R drive not found.')
    elif not os.path.isdir(fnzip2):
        self.tab1CalHintLabel.setText(' ! Error: PrivateData not found.')
    elif not os.path.isdir(fnzip3):
        self.tab1CalHintLabel.setText(' ! Error: ComboResults not found.')
    else:
        tag = 1

    t1, t2, t3 = 0, 0, 0
    if tag:
        ta1 = self.expStartLineEdit.text()
        ta2 = self.expStartCombobox1.currentText()
        ta3 = self.expStartCombobox2.currentText()
        tb1 = self.expAddLineEdit.text()
        tb2 = self.expAddCombobox1.currentText()
        tb3 = self.expAddCombobox2.currentText()
        tc1 = self.expEndLineEdit.text()
        tc2 = self.expEndCombobox1.currentText()
        tc3 = self.expEndCombobox2.currentText()

        try:
            epo1 = datetime.datetime(int(ta1[:4]), int(ta1[4:6]), int(ta1[6:8]), int(ta2[:2]),
                                     int(ta3[:2])).timestamp()  # start
            epo2 = datetime.datetime(int(tb1[:4]), int(tb1[4:6]), int(tb1[6:8]), int(tb2[:2]),
                                     int(tb3[:2])).timestamp()  # add sample
            epo3 = datetime.datetime(int(tc1[:4]), int(tc1[4:6]), int(tc1[6:8]), int(tc2[:2]),
                                     int(tc3[:2])).timestamp()  # end
            print(epo1, epo3)

            if (epo1 >= epo2) or (epo2 >= epo3):
                tag = 0
                self.tab1CalHintLabel.setText("! Error, start time is after end time.")
            else:
                t1 = "%s%s%s" % (ta1, ta2, ta3)
                t2 = "%s%s%s" % (tb1, tb2, tb3)
                t3 = "%s%s%s" % (tc1, tc2, tc3)
        except:
            self.tab1CalHintLabel.setText("! Error: invalid time.")
            tag = 0
    return tag, t1, t2, t3


def calculate(self):
    tag, t1, t2, t3 = calculation_check(self)

    if tag:
        try:
            print('start calculating')
            # sample = self.sampleNameLineEdit.text()
            cid = int(self.sampleCIDLineEdit.text())
            if self.saveFigCheckbox.isChecked():
                savefigure = True
            else:
                savefigure = False

            try:
                row = int(self.oneComboNumLineEdit.text())
            except:
                row = 500

            if self.dropletRadioButton.isChecked():
                print('droplet test')
                weight = float(self.sampleWeightLineEdit.text())
                MW = float(self.sampleMWLineEdit.text())
                sigma = int(self.sampleSigmaCombobox.currentText())

                if self.aqCheckbox.isChecked():  # aqueous solution
                    print('aqueous droplet')
                    self.F1, self.F2, self.F3, self.F4, max_row = \
                        droplet_aq.aqueous_droplet(self.experiment_path, self.sample, cid, weight, MW, t1, t2, t3,
                                                   pct=sigma, row=row, savefig=savefigure)

                else:  # pure analyte
                    self.F1, self.F2, self.F3, self.F4, max_row = \
                        droplet.calibration_droplet(self.experiment_path, self.sample, cid, weight, MW, t1, t2, t3,
                                                   pct=sigma, row=row, savefig=savefigure)
                    # plt.waitforbuttonpress()  # any key to close all figure
                    # plt.close('all')


                
                p = os.path.join(self.experiment_path, 'par', 'n_sigma.txt')
                with open(p, 'w') as f:
                    f.write(str(sigma))

            else:
                print('gas tank')
                tank_conc = float(self.sampleTankConcLineEdit.text())
                self.F1, self.F2, self.F3, self.F4, max_row = \
                         tank.calibration_gastank(self.experiment_path, self.sample, cid, tank_conc, t1, t2, t3,
                                                  row=500, savefig=savefigure)

            ## write on R drive
            fn = os.path.join(self.experiment_path, 'par', 'max_row.txt')
            with open(fn, 'w') as f:
                f.write(str(max_row))

            self.maxRowLabel.setText(str(max_row))
                
            p = os.path.join(self.experiment_path, 'par', 'row.txt')
            with open(p, 'w') as f:
                f.write(self.oneComboNumLineEdit.text())

            ## write locally for the gui
            func_experiment.save_parameter_local(self)

            f = open(os.path.join(self.experiment_path, 'par', 'calibration_factor.txt'), "r")
            cal = round(float(f.read()), 4)
            self.tab1CalHintLabel.setText('⦿ Calibration factor is %s' % cal)
            self.tab1ClosePlotButton.setEnabled(True)
        except:
            self.tab1CalHintLabel.setText('! Error calculation. Please run script to diagnose.')


def close_plot(self):
    try:
        plt.close(self.F1)
        plt.close(self.F2)
        plt.close(self.F3)
        plt.close(self.F4)
        self.tab1ClosePlotButton.setEnabled(False)
    except:
        pass


def plot_one_combo(self):
    try:
        row = int(self.oneComboNumLineEdit.text())
    except:
        row = None

    combokey = self.combo_spectrum_key.currentText()
    note = combo_other.plot_combo(self.experiment_path, self.sample, combokey, row)
    if note:
        self.tab1ComboHintLabel.setText('! Error: ' + note)


def combo_study(self):
    p = os.path.join('par1', 'combo_stop.txt')
    with open(p, 'w') as f:
        f.write("0")
    # self.stopPlotComboButton.setEnabled(True)

    row1, row2, range1, range2 = 0, 0, 0, 0
    peak_pct = 10

    if self.rowNumRadioButton.isChecked():
        try:
            row1 = int(self.row1LineEdit.text())
            row2 = int(self.row2LineEdit.text())
        except:
            pass

    if self.peakRadioButton.isChecked():
        try:
            peak_pct = int(self.peakPecentageLineEdit.text())
        except:
            pass

    try:
        range1 = int(self.comboRange1LineEdit.text())
        range2 = int(self.comboRange2LineEdit.text())
    except:
        pass

    cid = int(self.sampleCIDLineEdit.text())
    start_day = self.expStartLineEdit.text()  # '20211124'
    if self.saveFigCheckbox.isChecked():
        savefigure = True
    else:
        savefigure = False
        
    note = combo.combo_study(self.experiment_path, self.sample, cid, start_day,
                             row1, row2, range1, range2, peak_pct, savefig=savefigure)

    if note:
        self.tab1ComboHintLabel.setText('! Error: ' + note)
    # self.stopPlotComboButton.setEnabled(False)


def stop_combo_plot(self):
    p = os.path.join('par1', 'combo_stop.txt')
    with open(p, 'w') as f:
        f.write("1")

    # self.stopPlotComboButton.setEnabled(False)


if __name__ == "__main__":
    print()
