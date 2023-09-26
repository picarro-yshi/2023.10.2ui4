## analyzer
import socket
from queue import Queue
import CmdFIFO_py3 as CmdFIFO
from Listener_py3 import Listener
import StringPickler_py3 as StringPickler


def detect_analyzer_portin(self):
    try:
        self.host = self.analyzerIPLineEdit.text()
        socket.create_connection((self.host, self.port_in), 5)  # '10.100.3.123'   ## 50070
        ipadd = 'http://' + self.host
        MeasSystem = CmdFIFO.CmdFIFOServerProxy(f"{ipadd}:{self.port_in}", "test_connection",
                                                IsDontCareConnection=False)
        print(MeasSystem.GetStates())
        self.analyzerPortInHintLabel.setText('\u2713')
        return 1
    except:
        self.analyzerPortInHintLabel.setText('\u2717')
        return 0


def detect_analyzer_portout(self):
    try:
        self.host = self.analyzerIPLineEdit.text()
        socket.create_connection((self.host, self.port_out), 5)
        dm_queue = Queue(180)  ## data manager
        listener = Listener(dm_queue, self.host, self.port_out, StringPickler.ArbitraryObject, retry=True)

        for i in range(10):
            dm = dm_queue.get(timeout=5)
            print(i, dm['source'])
            if dm['source'] == self.analyzer_source:
                self.analyzerPortOutHintLabel.setText('\u2713')
                return 1
            if i == 5:
                self.analyzerPortOutHintLabel.setText('\u2717')
                self.tab1ExperimentHint.setText("Analyzer source '%s' not exist.\n"
                                                "A problem may occur with the fitter." % self.analyzer_source)
                return 0
    except:
        self.tab1ExperimentHint.setText("Analyzer output port not ready.\n")
        self.analyzerPortOutHintLabel.setText('\u2717')
        return 0


def detect_analyzer_portin_local():
    try:
        host = "10.100.3.72"
        port = 50070  # in
        socket.create_connection((host, port), 5)
        ipadd = 'http://' + host
        MeasSystem = CmdFIFO.CmdFIFOServerProxy(f"{ipadd}:{port}", "test_connection",
                                                IsDontCareConnection=False)
        print(MeasSystem.GetStates())
        return 1
    except:
        return 0


def detect_analyzer_portout_local():
    try:
        host = "10.100.3.72"
        port = 40060  # out
        socket.create_connection((host, port), 5)
        dm_queue = Queue(180)  ## data manager
        listener = Listener(dm_queue, host, port, StringPickler.ArbitraryObject, retry=True)

        for i in range(10):
            dm = dm_queue.get(timeout=5)
            print(i, dm['source'])
            if dm['source'] == "analyze_VOC_broadband":
                return 1
            if i == 5:
                return 0
    except:
        return 0



if __name__ == "__main__":
    # print(detect_analyzer_portin_local())
    print(detect_analyzer_portout_local())
