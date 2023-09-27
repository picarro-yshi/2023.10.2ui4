## other tab1 functions
import socket
import os

BUFFER_SIZE = 1024

def detect_scale(self):
    try:
        self.scale_ip = self.scaleIPAddressLineEdit.text()  # '10.100.3.148'  TCP_IP
        self.scale_port = int(self.scalePortLineEdit.text())  # 8001  TCP_PORT
        s = socket.create_connection((self.scale_ip, self.scale_port), 5)  # only try 5s time out
        s.settimeout(2)

        try:
            print(s.recv(BUFFER_SIZE))
            print('Mettler Toledo scale is ready.')
        except:
            s.send(b'@\r\n')  # Wake up scale
            k = s.recv(BUFFER_SIZE)  # = clear buffer
            print('Wake up the Mettler Toledo scale')

        self.scaleHintLabel.setText('\u2713')

        fn = os.path.join('par1', 'scale.txt')
        with open(fn, 'w') as f:
            f.write("%s\n%s" % (self.scale_ip, self.scale_port))

        return 1
    except:
        self.ScaleRealTimeLabel.setText("Not connected")
        self.scaleHintLabel.setText('\u2717')
        return 0


def get_measurement(self):
    s = socket.create_connection((self.scale_ip, self.scale_port), 5)
    w1 = s.recv(BUFFER_SIZE)
    w2 = w1.decode("utf-8")
    weight = round(float(w2[3:15]), 5)
    return weight


def scale_reading(self):
    self.graphWidget1.clear()
    self.weightLabel.setText('0.00000')
    self.ScaleRealTimeLabel.setText(' ')

    if detect_scale(self):
        try:
            self.weightime = int(self.scaleTimeLineEdit.text())
        except:
            self.weightime = 180
            self.scaleTimeLineEdit.setText('180')

        self.scale_x = []
        self.scale_y = []
        self.scale_i = 1

        try:
            self.timer_scale.start()
        except:
            self.ScaleRealTimeLabel.setText("! Error")
    

def scale_plot(self):
    if self.scale_i == self.weightime:
        self.timer_scale.stop()
    else:
        self.scale_x.append(self.scale_i)
        self.scale_i += 1

        weight = get_measurement(self)
        self.scale_y.append(weight)
        self.ScaleRealTimeLabel.setText(str(weight))
        
        self.graphWidget1.plot(self.scale_x, self.scale_y, pen="k")

        
def scale_weigh(self):
    self.weightLabel.setText(' ')
    try:  # when animation is running, get from label
        w1 = self.ScaleRealTimeLabel.text()  ##string
        w2 = round(float(w1), 5)
        self.weightLabel.setText(str(w2))
        self.sampleWeightLineEdit.setText(str(w2))
    except:  # when no animation is not run
        print('measuring ...')
        self.weightLabel.setText(' ')
        if detect_scale(self):
            weight = get_measurement(self)
            self.weightLabel.setText(str(weight))
            self.sampleWeightLineEdit.setText(str(weight))




if __name__ == "__main__":
    print()