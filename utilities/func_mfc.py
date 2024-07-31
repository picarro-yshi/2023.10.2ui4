## MFC functions

import time
import os

from alicat import FlowController
import CmdFIFO_py3 as CmdFIFO
RPC_PORT_DRIVER = 50010

datakey1 = "MFC1_flow"
datakey2 = "MFC2_flow"


def set_mfc_1slpm(self, x=None):
    try:
        if x is None:
            F1 = float(self.tab1MFC1LineEdit.text())  # dilution line
        else:
            F1 = x

        if F1 > 1 or F1 < 0:
            self.mfcHintLabel.setText("! MFC1 value error.")
        else:
            port_mfc = self.mfcPortCombobox.currentText()
            adr1 = self.MFC1AddressLineEdit.text()
            flow_controller1 = FlowController(port=port_mfc, address=adr1)
            flow_controller1.set_flow_rate(flow=F1)
            self.mfcHintLabel.setText("• MFC1 set to %.2f" % F1)
    except:
        self.mfcHintLabel.setText("! Error set MFC1.")


def set_mfc_100sccm(self, x=None):
    try:
        if x is None:
            F2 = float(self.tab1MFC100Combobox.currentText())  # bubbler line large
        else:
            F2 = x

        if F2 > 100 or F2 < 0:
            self.mfcHintLabel.setText("! MFC2 value error.")
        else:
            port_mfc = self.mfcPortCombobox.currentText()
            adr1 = self.MFC1AddressLineEdit.text()
            adr2 = self.MFC2LargeAddressLineEdit.text()
            F1 = 1 - F2 / 1000  # dilution
            flow_controller1 = FlowController(port=port_mfc, address=adr1)
            flow_controller2 = FlowController(port=port_mfc, address=adr2)
            flow_controller1.set_flow_rate(flow=F1)
            flow_controller2.set_flow_rate(flow=F2)
            self.tab1MFC1LineEdit.setText(str(F1))
            self.mfcHintLabel.setText("• MFC2 set to %.2f" % F2)
    except:
        self.mfcHintLabel.setText("! Error set MFC2.")


def set_mfc_10sccm(self, x=None):
    try:
        if x is None:
            F2 = float(self.tab1MFC10Combobox.currentText())  # bubbler line small
        else:
            F2 = x

        if F2 > 10 or F2 < 0:
            self.mfcHintLabel.setText("! MFC2 value error.")
        else:
            port_mfc = self.mfcPortCombobox.currentText()
            adr1 = self.MFC1AddressLineEdit.text()
            adr2 = self.MFC2SmallAddressLineEdit.text()
            F1 = 1 - F2 / 1000  # dilution line
            flow_controller1 = FlowController(port=port_mfc, address=adr1)
            flow_controller2 = FlowController(port=port_mfc, address=adr2)
            flow_controller1.set_flow_rate(flow=F1)
            flow_controller2.set_flow_rate(flow=F2)
            self.tab1MFC1LineEdit.setText(str(F1))
            self.mfcHintLabel.setText("• MFC2 set to %.2f" % F2)
    except:
        self.mfcHintLabel.setText("! Error set MFC2.")


def choose_100sccm(self):
    self.mfc100RadioButton.setStyleSheet("color: black")
    self.tab1MFC100Combobox.setStyleSheet("color: black")
    self.tab1MFC100Button.setStyleSheet("color: black")

    self.mfc10RadioButton.setStyleSheet("color: grey")
    self.tab1MFC10Combobox.setStyleSheet("color: grey")
    self.tab1MFC10Button.setStyleSheet("color: grey")

    # switch valve
    self.host = self.analyzerIPLineEdit.text()
    Driver = CmdFIFO.CmdFIFOServerProxy("http://%s:%d" % (self.host, RPC_PORT_DRIVER), "Automation",
                                        IsDontCareConnection=False)
    Driver.setValveMask(0)
    valveState = Driver.getValveMask()
    print('Valve State =', int(valveState))


def choose_10sccm(self):
    self.mfc100RadioButton.setStyleSheet("color: grey")
    self.tab1MFC100Combobox.setStyleSheet("color: grey")
    self.tab1MFC100Button.setStyleSheet("color: grey")

    self.mfc10RadioButton.setStyleSheet("color: black")
    self.tab1MFC10Combobox.setStyleSheet("color: black")
    self.tab1MFC10Button.setStyleSheet("color: black")

    # switch valve
    Driver = CmdFIFO.CmdFIFOServerProxy("http://%s:%d" % (self.host, RPC_PORT_DRIVER), "Automation",
                                        IsDontCareConnection=False)
    Driver.setValveMask(1)
    valveState = Driver.getValveMask()
    print('Valve State =', int(valveState))


def stop_mfc2_flow(self):  # stop MFC2, set MFC1 to maximum
    try:
        port_mfc = self.mfcPortCombobox.currentText()
        adr1 = self.MFC1AddressLineEdit.text()
        adr2large = self.MFC2LargeAddressLineEdit.text()
        adr2small = self.MFC2SmallAddressLineEdit.text()

        flow_controller1 = FlowController(port=port_mfc, address=adr1)
        flow_controller2large = FlowController(port=port_mfc, address=adr2large)
        flow_controller2small = FlowController(port=port_mfc, address=adr2small)
        flow_controller1.set_flow_rate(flow=1)
        flow_controller2large.set_flow_rate(flow=0)
        flow_controller2small.set_flow_rate(flow=0)

        self.mfcHintLabel.setText("• MFC2 flow stopped.")
    except:
        self.mfcHintLabel.setText("! Error stop MFC2 flow.")


def send_MFC_data(self):
    try:
        port_mfc = self.mfcPortCombobox.currentText()
        mfc_address1 = self.MFC1AddressLineEdit.text()
        self.flow_controller1 = FlowController(port=port_mfc, address=mfc_address1)

        mfc_address2 = self.MFC2LargeAddressLineEdit.text()
        self.flow_controller2_large = FlowController(port=port_mfc, address=mfc_address2)
        mfc_address2 = self.MFC2SmallAddressLineEdit.text()
        self.flow_controller2_small = FlowController(port=port_mfc, address=mfc_address2)

        if self.mfc100RadioButton.isChecked():
            self.use_large = 1
        else:
            self.use_large = 0

        self.timer_mfc.start()
        self.sendMFCButton.setEnabled(False)
        self.stopSendMFCButton.setEnabled(True)
    except:
        self.tab1ExperimentHint.setText(
            " ! Error sending MFC data to analyzer.\nPlease try again."
        )


def sendMFC(self):  # send data to analyzer
    try:
        fc1 = self.flow_controller1.get()
        fc2_large = self.flow_controller2_large.get()
        fc2_small = self.flow_controller2_small.get()

        # print(fc1.get()['pressure'])
        # print(fc1.get()['temperature'])

        # port_in = 50070  ## backdoor, send data to fitter on analyzer
        # port_out = 40060  ## listener, get data from analyzer
        # MeasSystem = CmdFIFO.CmdFIFOServerProxy("http://localhost:%s" % port_in, "test_connection",
        #                                         IsDontCareConnection=False)
        MeasSystem = CmdFIFO.CmdFIFOServerProxy(
            "http://%s:%d" % (self.host, self.port_in),
            "test_connection",
            IsDontCareConnection=False,
        )  # time out has no effect
        # print(MeasSystem.GetStates())

        a = fc1["mass_flow"]
        if self.use_large:
            fc2 = fc2_large
        else:
            fc2 = fc2_small

        b = fc2["mass_flow"]
        c = fc2["pressure"]
        d = fc2["temperature"]

        MeasSystem.Backdoor.SetData(datakey1, a)
        MeasSystem.Backdoor.SetData(datakey2, b)
        MeasSystem.Backdoor.SetData("MFC2_P_amb", c)
        MeasSystem.Backdoor.SetData("MFC2_T_amb", d)
        self.tab1Layout1Hint.setText("• MFC data sent to analyzer.")
    except:
        self.tab1Layout1Hint.setText(" ! Error sending MFC data sent to analyzer.")
        print("MFC data to analyzer error detected: ", time.ctime())

    # refresh
    try:
        self.tab1MFC1Label.setText(str(a))
        self.tab1MFC100Label.setText(str(fc2_large["mass_flow"]))
        self.tab1MFC10Label.setText(str(fc2_small["mass_flow"]))
        self.tab1PressureLabel.setText(str(c))
        self.tab1TempLabel.setText(str(d))
    except:
        print("MFC refresh error: ", time.ctime())


def stop_send_MFC_data(self):
    self.timer_mfc.stop()
    self.sendMFCButton.setEnabled(True)
    self.stopSendMFCButton.setEnabled(False)


def detect_mfc(self, adr):
    try:
        port_mfc = self.mfcPortCombobox.currentText()
        fc = FlowController(port=port_mfc, address=adr)
        print(fc.get())

        fn = os.path.join("par1", "mfc_port.txt")
        with open(fn, "w") as f:
            f.write(port_mfc)
        return 1
    except:
        return 0


def detect_mfc1(self):
    adr = self.MFC1AddressLineEdit.text()
    tag = detect_mfc(self, adr)
    if tag:
        self.alicatMFC1HintLabel.setText("\u2713")

        fn = os.path.join("par1", "mfc1_address.txt")
        with open(fn, "w") as f:
            f.write("%s" % adr)
    else:
        self.alicatMFC1HintLabel.setText("\u2717")
    return tag


def detect_mfc2large(self):
    adr = self.MFC2LargeAddressLineEdit.text()
    tag = detect_mfc(self, adr)
    if tag:
        self.alicatMFC2LargeHintLabel.setText("\u2713")

        fn = os.path.join("par1", "mfc2large_address.txt")
        with open(fn, "w") as f:
            f.write("%s" % adr)
    else:
        self.alicatMFC2LargeHintLabel.setText("\u2717")
    return tag


def detect_mfc2small(self):
    adr = self.MFC2SmallAddressLineEdit.text()
    tag = detect_mfc(self, adr)
    if tag:
        self.alicatMFC2SmallHintLabel.setText("\u2713")

        fn = os.path.join("par1", "mfc2small_address.txt")
        with open(fn, "w") as f:
            f.write("%s" % adr)
    else:
        self.alicatMFC2SmallHintLabel.setText("\u2717")
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
