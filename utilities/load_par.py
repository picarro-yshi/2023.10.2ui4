# load parameters used last time to GUI

import os
import serial.tools.list_ports as ls
import platform

opsystem = platform.system()  # 'Linux', 'Windows', 'Darwin'


def load_tab1(self):
    # Sample
    try:
        with open(os.path.join("par1", "r_drive.txt"), "r") as f:
            temp = f.read()
        self.sampleRDriveLineEdit.setPlainText(temp)
    except:
        if opsystem == "Windows":
            self.sampleRDriveLineEdit.setPlainText(
                "R:\crd_G9000\AVXxx\3610-NUV1022\R&D\Calibration"
            )  ## Windows
        elif opsystem == "Darwin":
            self.sampleRDriveLineEdit.setPlainText(
                "/Volumes/Data/crd_G9000/AVXxx/3610-NUV1022/R&D/Calibration/"
            )  ## Mac
        else:
            self.sampleRDriveLineEdit.setPlainText(
                "/mnt/r/crd_G9000/AVXxx/3610-NUV1022/R&D/Calibration/"
            )  ## Linux
        print("failed to load R drive location.")

    try:
        with open(os.path.join("par1", "sample.txt"), "r") as f:
            temp = f.read()
        if temp:
            self.sampleNameLineEdit.setText(temp)
    except:
        print("failed to load sample name.")

    try:
        with open(os.path.join("par1", "cid.txt"), "r") as f:
            temp = f.read()
        self.sampleCIDLineEdit.setText(temp)
    except:
        print("failed to load compound CID number.")

    try:
        with open(os.path.join("par1", "molecular_weight.txt"), "r") as f:
            temp = f.read()
        self.sampleMWLineEdit.setText(temp)
    except:
        print("Failed to load molecular weight value.")

    try:
        with open(os.path.join("par1", "tankconc.txt"), "r") as f:
            temp = f.read()
        self.sampleTankConcLineEdit.setText(temp)
    except:
        print("No tank concentration value available.")


def get_port(self):
    portusb = [p.device for p in ls.comports()]
    self.portListLabel.setText(str(portusb))

    self.mfcPortCombobox.clear()
    self.mfcPortCombobox.addItems(portusb)


def load_tab3(self):
    # hardware
    try:
        with open(os.path.join("par1", "analyzer_ip.txt"), "r") as f:
            temp = f.read()
        self.analyzerIPLineEdit.setText(temp)
    except:
        print("No analyzer IP Address.")

    with open(os.path.join("par1", "mfc_port.txt"), "r") as f:
        temp = f.read()
    self.mfcPortCombobox.setCurrentText(temp)
    if temp != self.mfcPortCombobox.currentText():
        print("MFC port name not in record.")

    try:
        with open(os.path.join("par1", "mfc1_address.txt"), "r") as f:
            temp = f.read()
        self.MFC1AddressLineEdit.setText(temp)
    except:
        print("No MFC1 address.")

    try:
        with open(os.path.join("par1", "mfc2large_address.txt"), "r") as f:
            temp = f.read()
        self.MFC2largeAddressLineEdit.setText(temp)
    except:
        print("No MFC2 large address.")

    try:
        with open(os.path.join("par1", "mfc2small_address.txt"), "r") as f:
            temp = f.read()
        self.MFC2smallAddressLineEdit.setText(temp)
    except:
        print("No MFC2 small address.")

    try:
        with open(os.path.join("par1", "scale.txt"), "r") as f:
            temp = f.read().splitlines()
        self.scaleIPAddressLineEdit.setText(temp[0])
        self.scalePortLineEdit.setText(temp[1])
    except:
        print("No scale ip or port.")

    try:
        with open(os.path.join("par1", "IP_computer.txt"), "r") as f:
            temp = f.read()
        self.computerIPAddressLineEdit.setText(temp)
    except:
        print("No IP address for this computer.")

    try:
        with open(os.path.join("par1", "IP_powerswitch.txt"), "r") as f:
            temp = f.read()
        self.powerSwitchIPAddressLineEdit.setText(temp)
    except:
        print("No IP address for power switch.")
