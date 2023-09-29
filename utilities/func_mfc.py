## other tab1 functions
import socket
from queue import Queue
import time
import os

from Listener_py3 import Listener
import StringPickler_py3 as StringPickler
from alicat import FlowController
import CmdFIFO_py3 as CmdFIFO

datakey1 = 'MFC1_flow'
datakey2 = 'MFC2_flow'


def set_mfc_1slpm(self, x=None):
    try:
        if x is None:
            F1 = float(self.tab1MFC1LineEdit.text())  # dilution line
        else:
            F1 = x
            
        if F1 > 1 or F1 < 0:
            self.mfcHintLabel.setText('! Error: Input a value between 0-1.')
        else:
            port_mfc = self.mfcPortCombobox.currentText()
            adr1 = self.MFC1AddressLineEdit.text()
            flow_controller1 = FlowController(port=port_mfc, address=adr1)
            flow_controller1.set_flow_rate(flow=F1)
            self.mfcHintLabel.setText('• Dilution line set to ' + str(F1))
    except:
        self.mfcHintLabel.setText('! Error: unable to set MFC1 flow.')


def set_mfc_100sccm(self, x=None):
    try:
        if x is None:
            F2 = float(self.tab1MFC100Combobox.currentText())  # bubbler line large
        else:
            F2 = x
        
        if F2 > 100 or F2 < 0:
            self.mfcHintLabel.setText('! Error: Input a value between 0-100.')
        else:
            port_mfc = self.mfcPortCombobox.currentText()
            adr1 = self.MFC1AddressLineEdit.text()
            adr2 = self.MFC2largeAddressLineEdit.text()
            F1 = 1 - F2 / 1000  # dilution
            flow_controller1 = FlowController(port=port_mfc, address=adr1)
            flow_controller2 = FlowController(port=port_mfc, address=adr2)
            flow_controller1.set_flow_rate(flow=F1)
            flow_controller2.set_flow_rate(flow=F2)
            self.tab1MFC1LineEdit.setText(str(F1))
            self.mfcHintLabel.setText('• Bubble line set to ' + str(F2))
    except:
        self.mfcHintLabel.setText('! Error: Unable to set MFC2 flow.')


def set_mfc_10sccm(self, x=None):
    try:
        if x is None:
            F2 = float(self.tab1MFC10Combobox.currentText())  # bubbler line small
        else:
            F2 = x
        
        if F2 > 10 or F2 < 0:
            self.mfcHintLabel.setText('! Error: Input a value between 0-10.')
        else:
            port_mfc = self.mfcPortCombobox.currentText()
            adr1 = self.MFC1AddressLineEdit.text()
            adr2 = self.MFC2smallAddressLineEdit.text()
            F1 = 1 - F2 / 1000  # dilution
            flow_controller1 = FlowController(port=port_mfc, address=adr1)
            flow_controller2 = FlowController(port=port_mfc, address=adr2)
            flow_controller1.set_flow_rate(flow=F1)
            flow_controller2.set_flow_rate(flow=F2)
            self.tab1MFC1LineEdit.setText(str(F1))
            self.mfcHintLabel.setText('• Bubble line set to ' + str(F2))
    except:
        self.mfcHintLabel.setText('! Error: Unable to set MFC2 flow.')


def choose_100sccm(self):
    self.mfc100RadioButton.setStyleSheet("color: black")
    self.tab1MFC100Combobox.setStyleSheet("color: black")
    self.tab1MFC100Button.setStyleSheet("color: black")

    self.mfc10RadioButton.setStyleSheet("color: grey")
    self.tab1MFC10Combobox.setStyleSheet("color: grey")
    self.tab1MFC10Button.setStyleSheet("color: grey")


def choose_10sccm(self):
    self.mfc100RadioButton.setStyleSheet("color: grey")
    self.tab1MFC100Combobox.setStyleSheet("color: grey")
    self.tab1MFC100Button.setStyleSheet("color: grey")

    self.mfc10RadioButton.setStyleSheet("color: black")
    self.tab1MFC10Combobox.setStyleSheet("color: black")
    self.tab1MFC10Button.setStyleSheet("color: black")


def stop_flow(self):
    try:
        port_mfc = self.mfcPortCombobox.currentText()
        adr1 = self.MFC1AddressLineEdit.text()
        adr2large = self.MFC2largeAddressLineEdit.text()
        adr2small = self.MFC2smallAddressLineEdit.text()

        flow_controller1 = FlowController(port=port_mfc, address=adr1)
        flow_controller2large = FlowController(port=port_mfc, address=adr2large)
        flow_controller2small = FlowController(port=port_mfc, address=adr2small)
        flow_controller1.set_flow_rate(flow=1)
        flow_controller2large.set_flow_rate(flow=0)
        flow_controller2small.set_flow_rate(flow=0)

        # self.tab1MFC100Combobox.setCurrentText("0")
        # self.tab1MFC10Combobox.setCurrentText("0")
        self.mfcHintLabel.setText('• MFC2 Bubble line stopped.')
    except:
        self.mfcHintLabel.setText('! Error: Unable to stop the flow.')


def send_MFC_data(self):
    try:
        port_mfc = self.mfcPortCombobox.currentText()
        mfc_address1 = self.MFC1AddressLineEdit.text()
        if self.mfc100RadioButton.isChecked():
            mfc_address2 = self.MFC2largeAddressLineEdit.text()
            self.mfc2_refresh_label = self.tab1MFC100Label
            self.tab1MFC10Label.setText()
        else:
            mfc_address2 = self.MFC2smallAddressLineEdit.text()
            self.mfc2_refresh_label = self.tab1MFC10Label
            self.tab1MFC100Label.setText()

        self.flow_controller1 = FlowController(port=port_mfc, address=mfc_address1)
        self.flow_controller2 = FlowController(port=port_mfc, address=mfc_address2)
    
        host = self.analyzerIPLineEdit.text()
        self.analyzer_ip = 'http://' + host
    
        self.timer_mfc.start()
        self.sendMFCButton.setEnabled(False)
        self.stopSendMFCButton.setEnabled(True)
    except:
        self.tab1ExperimentHint.setText(" ! Error sending MFC data to analyzer.\n")


def sendMFC(self):
    try:
        fc1 = self.flow_controller1.get()
        fc2 = self.flow_controller2.get()

        # print(fc1.get()['pressure'])
        # print(fc1.get()['temperature'])

        # port_in = 50070  ## backdoor, send data to fitter on analyzer
        # port_out = 40060  ## listener, get data from analyzer
        # MeasSystem = CmdFIFO.CmdFIFOServerProxy("http://localhost:%s" % port_in, "test_connection",
        #                                         IsDontCareConnection=False)
        MeasSystem = CmdFIFO.CmdFIFOServerProxy(f"{self.analyzer_ip}:{self.port_in}", "test_connection",
                                                IsDontCareConnection=False)  # time out has no effect
        # print(MeasSystem.GetStates())

        # sent measurement data on Alicat to Picarro fitting software
        a = fc1['mass_flow']
        b = fc2['mass_flow']
        c = fc2['pressure']
        d = fc2['temperature']

        MeasSystem.Backdoor.SetData(datakey1, a)
        MeasSystem.Backdoor.SetData(datakey2, b)
        MeasSystem.Backdoor.SetData('MFC2_P_amb', c)
        MeasSystem.Backdoor.SetData('MFC2_T_amb', d)
        self.tab1Layout1Hint.setText("• MFC data sent to analyzer.")
    except:
        self.tab1Layout1Hint.setText(" ! Error sending MFC data sent to analyzer.")
        print('MFC data to analyzer error detected: ', time.ctime())

    # refresh
    try:
        self.tab1MFC1Label.setText(str(a))
        self.mfc2_refresh_label.setText(str(b))
        self.tab1PressureLabel.setText(str(c))
        self.tab1TempLabel.setText(str(d))
    except:
        print('MFC refresh error: ', time.ctime())


def stop_send_MFC_data(self):
    self.timer_mfc.stop()
    self.sendMFCButton.setEnabled(True)
    self.stopSendMFCButton.setEnabled(False)


def detect_mfc(self, adr):
    try:
        port_mfc = self.mfcPortCombobox.currentText()
        fc = FlowController(port=port_mfc, address=adr)
        print(fc.get())

        fn = os.path.join('par1', 'mfc_port.txt')
        with open(fn, 'w') as f:
            f.write(port_mfc)
        return 1
    except:
        return 0


def detect_mfc1(self):
    adr = self.MFC1AddressLineEdit.text()
    tag = detect_mfc(self, adr)
    if tag:
        self.alicatMFC1HintLabel.setText('\u2713')

        fn = os.path.join('par1', 'mfc1_address.txt')
        with open(fn, 'w') as f:
            f.write("%s" % adr)
    else:
        self.alicatMFC1HintLabel.setText('\u2717')
    return tag


def detect_mfc2large(self):
    adr = self.MFC2largeAddressLineEdit.text()
    tag = detect_mfc(self, adr)
    if tag:
        self.alicatMFC2LargeHintLabel.setText('\u2713')

        fn = os.path.join('par1', 'mfc2large_address.txt')
        with open(fn, 'w') as f:
            f.write("%s" % adr)
    else:
        self.alicatMFC2LargeHintLabel.setText('\u2717')
    return tag


def detect_mfc2small(self):
    adr = self.MFC2smallAddressLineEdit.text()
    tag = detect_mfc(self, adr)
    if tag:
        self.alicatMFC2SmallHintLabel.setText('\u2713')

        fn = os.path.join('par1', 'mfc2small_address.txt')
        with open(fn, 'w') as f:
            f.write("%s" % adr)
    else:
        self.alicatMFC2SmallHintLabel.setText('\u2717')
    return tag


def detect_mfc_local():
    try:
        port_mfc = "COM6"
        adr1 = "A"
        fc1 = FlowController(port=port_mfc, address=adr1)
        print(fc1.get())
        return 1
    except:
        return 0


if __name__ == "__main__":
    print(detect_mfc_local())
