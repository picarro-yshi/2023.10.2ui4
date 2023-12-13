## Power Switch functions
import os
import socket
import json
import urllib.request

from PyQt6.QtWidgets import QPushButton


# Python Program to Get IP Address of this computer
def ip_thisPC(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # [Comment]: 8.8.8.8 is the primary DNS server for Google DNS. It is assumed that this DNS server will always be up.
    s.connect(("8.8.8.8", 80))

    ip = s.getsockname()[0]
    # ip = s.getsockname()
    s.close()
    # print(ip)
    self.computerIPAddressLineEdit.setText(ip)
    return ip


def set_button(button, state):
    button.setEnabled(True)
    if state:  # on
        button.setText("ON")
        button.setStyleSheet("background-color: #A9E226")  # Green
    else:
        button.setText("OFF")
        button.setStyleSheet("background-color: #FE461E")  # Red


def power_connect(self):
    # url = "http://10.100.2.71/api/control?target=outlet2&action=off"
    ip_switch = self.powerSwitchIPAddressLineEdit.text()
    url = "http://%s/api/control?target=outlet2&action=" % ip_switch

    try:
        response = urllib.request.urlopen(url, timeout=5).read().decode('utf-8')
        print(response)
        a = json.loads(response)
        self.powerHintLabel.setText("\u2713")

        heater1 = a['outlet'][0]
        heater2 = a['outlet'][1]
        set_button(self.heater1Button, heater1)
        set_button(self.heater2Button, heater2)
        self.heater1Checkbox.setDisabled(False)
        self.heater2Checkbox.setDisabled(False)

        fn = os.path.join("par1", "IP_computer.txt")
        with open(fn, "w") as f:
            f.write("%s" % self.computerIPAddressLineEdit.text())

        fn = os.path.join("par1", "IP_powerswitch.txt")
        with open(fn, "w") as f:
            f.write("%s" % ip_switch)

    except:
        print('power switch connection error')
        self.powerHintLabel.setText("\u2717")

        self.heater1Button.setEnabled(False)
        self.heater1Button.setStyleSheet("")
        self.heater2Button.setEnabled(False)
        self.heater2Button.setStyleSheet("")

        self.heater1Checkbox.setChecked(False)
        self.heater1Checkbox.setDisabled(True)
        self.heater2Checkbox.setChecked(False)
        self.heater2Checkbox.setDisabled(True)


# API of power switch
def button_click(self, id, button):
    ip_switch = self.powerSwitchIPAddressLineEdit.text()
    state = button.text()

    try:
        if state == 'ON':
            url = "http://%s/api/control?target=outlet%s&action=%s" % (ip_switch, str(id),"off")
            response = urllib.request.urlopen(url, timeout=5).read().decode('utf-8')
            set_button(button, False)
        else:
            url = "http://%s/api/control?target=outlet%s&action=%s" % (ip_switch, str(id), "on")
            response = urllib.request.urlopen(url, timeout=5).read().decode('utf-8')
            set_button(button, True)
    except:
        print("error set power switch")


# def button(self, id, state):
#     ip_switch = self.powerSwitchIPAddressLineEdit.text()
#     url = "http://%s/api/control?target=outlet%s&action=%s" % (ip_switch, str(id), state)
#     response = urllib.request.urlopen(url, timeout=5).read().decode('utf-8')
#     set_button(button, False)



if __name__ == "__main__":
    print()
