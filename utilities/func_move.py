# use move script on your own computer through ssh
# last updated: 2024.2.2
import os
import paramiko
username = "picarro"
password = "310595054"

def extract_time(dstfolder):
    try:
        f = open(os.path.join(dstfolder, 'par', 't1.txt'), 'r')
        temp = f.read().splitlines()
        ta1 = temp[0]  # 20230725
        ta2 = temp[1]  # 17
        ta3 = temp[2]  # 14

        f = open(os.path.join(dstfolder, 'par', 't3.txt'), 'r')
        temp = f.read().splitlines()
        tc1 = temp[0]
        tc2 = temp[1]
        tc3 = temp[2]

        start = '%s-%s-%s_%s:%s' % (ta1[:4], ta1[4:6], ta1[6:8], ta2, ta3)
        end = '%s-%s-%s_%s:%s' % (tc1[:4], tc1[4:6], tc1[6:8], tc2, tc3)
        print(start, end)
    except:
        # print("error extract start/end time.")
        start = None
        end = None
    return start, end

def move(self):
    tag = 1
    # open ssh
    analyzer_ip = self.analyzerIPLineEdit.text()  # '10.100.3.72'
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=analyzer_ip, username=username, password=password)
    except:
        self.tab1CalHintLabel.setText("ssh to analyzer failed. Check analyzer IP.")
        tag = 0

    # get time
    if tag:
        # destination folder path as it is on the Analyzer Linux computer
        # x = "/mnt/r/crd_G9000/AVXxx/3610-NUV1022/R&D/Calibration/12100 - 3-Ethyltoluene/20240102t"
        # y = "2024-01-02_17:34"  # start time
        # z = "2024-01-03_09:41"  # end time
        path = self.experiment_path.split("/")
        x = os.path.join("/mnt/r/crd_G9000/AVXxx/3610-NUV1022/R&D/Calibration", path[-2], path[-1])
        # print(x)
        y, z = extract_time(self.experiment_path)
        if y is None or z is None:
            self.tab1CalHintLabel.setText("! Error move&unzip, cannot extract start/end time.")
            tag = 0

    if tag:
        if self.rdfCheckbox.isChecked():
            rdf = 1  # 1: grab RDF data
        else:
            rdf = 0

        if self.privateCheckbox.isChecked():
            private = 1  # 1: grab Private data
        else:
            private = 0

        if self.comboCheckbox.isChecked():
            combo = 1  # 1: grab Combo Log
        else:
            combo = 0

        if self.broadbandCheckbox.isChecked():
            broadband = 1  # 1: only pick broadband combo data
        else:
            broadband = 0

        # Quoting special characters in shell command
        forbidden_characters = [r'"', r"'"]
        special_characters = [' ', '~', '`', '#', '&', '*', '(', ')', '|', ';', '<', '>']  #, "\\"

        tag = 1
        for i in forbidden_characters:
            if i in x:
                print("%s character is found in the destination folder path and cannot be handled in shell command. "
                      "Please replace or remove it then try again." % i)
                self.tab1CalHintLabel.setText("! Error move&&unzip due to %s character in file path." % i)
                tag = 0
                break

        if tag:
            for i in special_characters:
                if i in x:
                    x = x.replace(i, "'%s'" % i)
            if "\\" in x:
                x = x.replace("\\", "'\\'")
            # print(x)

            try:
                cmd = "cd /home/picarro/Documents/move && python3 moveAnz.py %s %s %s %s %s %s %s" \
                      % (x, y, z, rdf, private, combo, broadband)

                stdin, stdout, stderr = ssh.exec_command(cmd)

                k = stdout.readlines()
                for line in k:
                    print(line[:-1])  # end with '\n'

                ssh.close()
                self.tab1CalHintLabel.setText("• Move and unzip data finished.")
            except:
                self.tab1CalHintLabel.setText("! Failed to move and unzip data.")


