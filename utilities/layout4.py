## tab4 layout
import os
import sqlite3

from PyQt6.QtWidgets import (
    QPushButton,
    QLabel,
    QCheckBox,
    QLineEdit,
    QTableWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTableWidgetItem,
    QButtonGroup,
    QRadioButton,
)

import style

import platform
opsystem = platform.system()
if opsystem == "Darwin":
    rdisk = '/Volumes/Data'
elif opsystem == "Linux":
    rdisk = '/mnt/r'
else:  # 'Windows'
    rdisk = 'R:'

db_path = rdisk + '/crd_G9000/AVXxx/3610-NUV1022/R&D/Calibration/Compounds.db'
con = sqlite3.connect(db_path)
cur = con.cursor()

def tab4_layout(self):
    mainLayout = QHBoxLayout()
    self.tab4.setLayout(mainLayout)

    self.tab4_leftLayout = QVBoxLayout()
    rightLayout = QVBoxLayout()
    gapLabel = QLabel("   ")
    mainLayout.addLayout(self.tab4_leftLayout, 28)
    mainLayout.addWidget(gapLabel, 2)
    mainLayout.addLayout(rightLayout, 70)

    self.table = QTableWidget()  # table for query results
    label = QLabel("Compound Database Query Results")
    rightLayout.addWidget(label)
    rightLayout.addWidget(self.table)

    self.table.setColumnCount(13)
    self.table.setHorizontalHeaderLabels(["CID", "Name", "CAS", "CF", "CFDate",
                                          "Barcode", "MW", "MeltingPoint", "BoilingPoint",
                                          "State", "Fitter", "Fomula", "Notes"])
    self.table.setColumnWidth(0, 70)
    self.table.setColumnWidth(1, 200)
    self.table.setColumnWidth(3, 70)
    self.table.setColumnWidth(4, 70)
    self.table.setColumnWidth(5, 70)
    self.table.setColumnWidth(6, 70)
    self.table.setColumnWidth(9, 50)
    self.table.setColumnWidth(10, 50)

    createTab4_Layout1(self)  # create layout: tab4 left


def createTab4_Layout1(self):
    layout1 = QVBoxLayout()
    grid = QGridLayout()
    layout2 = QVBoxLayout()

    self.tab4_leftLayout.addLayout(layout1)
    self.tab4_leftLayout.addLayout(grid)
    self.tab4_leftLayout.addLayout(layout2)
    self.tab4_leftLayout.addStretch()

    label_title1 = QLabel("Select Query Conditions:")
    label_title1.setStyleSheet("font: bold")
    layout1.addWidget(label_title1)

    label1 = QLabel("Yes")
    label2 = QLabel("No")
    label3 = QLabel("All")
    label4 = QLabel("Counts")

    label_cal = QLabel("Calibrated?")
    self.tab4CalRadioButton1 = QRadioButton()
    self.tab4CalRadioButton2 = QRadioButton()
    self.tab4CalRadioButton3 = QRadioButton()
    self.tab4CalRadioButton2.setChecked(True)

    self.tab4_bg1 = QButtonGroup()
    self.tab4_bg1.addButton(self.tab4CalRadioButton1)
    self.tab4_bg1.addButton(self.tab4CalRadioButton2)
    self.tab4_bg1.addButton(self.tab4CalRadioButton3)
    
    button1 = QPushButton("Query")
    button1.clicked.connect(lambda: query_cal(self))
    self.calCountLabel = QLabel()

    label_exist = QLabel("Have it in the lab?")
    self.tab4ExistRadioButton1 = QRadioButton()
    self.tab4ExistRadioButton2 = QRadioButton()
    self.tab4ExistRadioButton3 = QRadioButton()
    self.tab4ExistRadioButton1.setChecked(True)

    self.tab4_bg2 = QButtonGroup()
    self.tab4_bg2.addButton(self.tab4ExistRadioButton1)
    self.tab4_bg2.addButton(self.tab4ExistRadioButton2)
    self.tab4_bg2.addButton(self.tab4ExistRadioButton3)

    button2 = QPushButton("Query")
    button2.clicked.connect(lambda: query_exist(self))
    self.existCountLabel = QLabel()

    label_state = QLabel("Is a liquid/solid?")
    self.tab4StateRadioButton1 = QRadioButton()
    self.tab4StateRadioButton2 = QRadioButton()
    self.tab4StateRadioButton3 = QRadioButton()
    self.tab4StateRadioButton1.setChecked(True)

    self.tab4_bg3 = QButtonGroup()
    self.tab4_bg3.addButton(self.tab4StateRadioButton1)
    self.tab4_bg3.addButton(self.tab4StateRadioButton2)
    self.tab4_bg3.addButton(self.tab4StateRadioButton3)

    button3 = QPushButton("Query")
    button3.clicked.connect(lambda: query_state(self))
    self.stateCountLabel = QLabel()

    label_fitter = QLabel("Exists in the fitter?")
    self.tab4FitterRadioButton1 = QRadioButton()
    self.tab4FitterRadioButton2 = QRadioButton()
    self.tab4FitterRadioButton3 = QRadioButton()
    self.tab4FitterRadioButton1.setChecked(True)

    self.tab4_bg4 = QButtonGroup()
    self.tab4_bg4.addButton(self.tab4FitterRadioButton1)
    self.tab4_bg4.addButton(self.tab4FitterRadioButton2)
    self.tab4_bg4.addButton(self.tab4FitterRadioButton3)

    button4 = QPushButton("Query")
    button4.clicked.connect(lambda: query_fitter(self))
    self.fitterCountLabel = QLabel()

    label_title2 = QLabel("Combined Queries:")
    label_title2.setStyleSheet("font: bold")
    button_combine = QPushButton("Query above conditions")
    button_combine.clicked.connect(lambda: query_combine(self))
    button_all = QPushButton("Show whole database")
    button_all.clicked.connect(lambda: query_all(self))
    button_todo = QPushButton("Show to-do list")
    button_todo.setStyleSheet("font: bold")
    button_todo.clicked.connect(lambda: query_todo(self))

    label_todo = QLabel("To-do list are compounds that are:\n"
                        "- not calibrated yet,\n- exists in the lab and fitter,\n"
                        "- a liquid or solid.")
    gap1 = QLabel("    ")

    self.combineCountLabel = QLabel()
    self.allCountLabel = QLabel()
    self.todoCountLabel = QLabel()
    
    grid.addWidget(label1, 0, 1)
    grid.addWidget(label2, 0, 2)
    grid.addWidget(label3, 0, 3)
    grid.addWidget(label4, 0, 5)

    grid.addWidget(label_cal, 1, 0)
    grid.addWidget(self.tab4CalRadioButton1, 1, 1)
    grid.addWidget(self.tab4CalRadioButton2, 1, 2)
    grid.addWidget(self.tab4CalRadioButton3, 1, 3)
    grid.addWidget(button1, 1, 4)
    grid.addWidget(self.calCountLabel, 1, 5)

    grid.addWidget(label_exist, 2, 0)
    grid.addWidget(self.tab4ExistRadioButton1, 2, 1)
    grid.addWidget(self.tab4ExistRadioButton2, 2, 2)
    grid.addWidget(self.tab4ExistRadioButton3, 2, 3)
    grid.addWidget(button2, 2, 4)
    grid.addWidget(self.existCountLabel, 2, 5)

    grid.addWidget(label_state, 3, 0)
    grid.addWidget(self.tab4StateRadioButton1, 3, 1)
    grid.addWidget(self.tab4StateRadioButton2, 3, 2)
    grid.addWidget(self.tab4StateRadioButton3, 3, 3)
    grid.addWidget(button3, 3, 4)
    grid.addWidget(self.stateCountLabel, 3, 5)

    grid.addWidget(label_fitter, 4, 0)
    grid.addWidget(self.tab4FitterRadioButton1, 4, 1)
    grid.addWidget(self.tab4FitterRadioButton2, 4, 2)
    grid.addWidget(self.tab4FitterRadioButton3, 4, 3)
    grid.addWidget(button4, 4, 4)
    grid.addWidget(self.fitterCountLabel, 4, 5)
    
    grid.addWidget(label_title2, 5, 0, 1, 4)
    grid.addWidget(button_combine, 6, 0, 1, 5)
    grid.addWidget(self.combineCountLabel, 6, 5)
    grid.addWidget(gap1, 7, 0)
    
    grid.addWidget(button_all, 8, 0, 1, 5)
    grid.addWidget(self.allCountLabel, 8, 5)
    grid.addWidget(button_todo, 9, 0, 1, 5)
    grid.addWidget(self.todoCountLabel, 9, 5)
    grid.addWidget(label_todo, 10, 0, 1, 5)

    gap2 = QLabel("    ")
    label_youselect = QLabel("You have selected: ")
    self.label_select = QLabel()
    button_select = QPushButton("Calibrated this compound")
    button_select.clicked.connect(lambda: query_select(self))
    self.tab4HintLabel = QLabel()
    self.tab4HintLabel.setStyleSheet(style.grey1())


    layout2.addWidget(gap2)
    layout2.addWidget(label_youselect)
    layout2.addWidget(self.label_select)
    layout2.addWidget(button_select)
    layout2.addWidget(self.tab4HintLabel)

    self.table.cellClicked.connect(lambda: getClickedCell(self, self.table.currentRow(), 0))


def displayQ(self, query, label):
    if query:
        list1 = cur.execute(query).fetchall()
        con.commit()
        try:
            n = len(list1)
            self.table.setRowCount(n)
            for i in range(n):
                for j in range(12):
                    self.table.setItem(i, j, QTableWidgetItem(str(list1[i][j + 1])))
            label.setText(str(n))
            self.tab4HintLabel.setText("Query success.")
        except:
            self.tab4HintLabel.setText("Query error.")
    else:
        self.tab4HintLabel.setText("You have to select Yes or No for this query.")

# single query
# calibrate
def query_cal(self):
    query = ""
    if self.tab4CalRadioButton1.isChecked():
        query = 'SELECT * FROM chemicals WHERE CF >0 ORDER BY CID ASC'
    elif self.tab4CalRadioButton2.isChecked():
        query = 'SELECT * FROM chemicals WHERE CF =0 ORDER BY CID ASC'
    displayQ(self, query, self.calCountLabel)

# in the lab
def query_exist(self):
    query = ""
    if self.tab4ExistRadioButton1.isChecked():
        query = 'SELECT * FROM chemicals WHERE Barcode !=0 AND Barcode != -1 ORDER BY CID ASC'
    elif self.tab4ExistRadioButton2.isChecked():
        query = 'SELECT * FROM chemicals WHERE Barcode =0 AND Barcode != -1 ORDER BY CID ASC'
    displayQ(self, query, self.existCountLabel)

# is a liquid/soilid
def query_state(self):
    query = ""
    if self.tab4StateRadioButton1.isChecked():
        query = 'SELECT * FROM chemicals WHERE Barcode != -1 ORDER BY CID ASC'
    elif self.tab4StateRadioButton2.isChecked():
        query = 'SELECT * FROM chemicals WHERE Barcode = -1 ORDER BY CID ASC'
    displayQ(self, query, self.stateCountLabel)

# in the fitter
def query_fitter(self):
    query = ""
    if self.tab4FitterRadioButton1.isChecked():
        query = 'SELECT * FROM chemicals WHERE Fitter=1 ORDER BY CID ASC'
    elif self.tab4FitterRadioButton2.isChecked():
        query = 'SELECT * FROM chemicals WHERE Fitter=0 ORDER BY CID ASC'
    displayQ(self, query, self.fitterCountLabel)


# combined query
# combine
def query_combine(self):
    if self.tab4CalRadioButton1.isChecked():
        query = "CF >0"
    elif self.tab4CalRadioButton2.isChecked():
        query = "CF =0"
    else:
        query = ""

    if self.tab4ExistRadioButton1.isChecked():
        x = "Barcode !=0 AND Barcode != -1"
    elif self.tab4ExistRadioButton2.isChecked():
        x = "Barcode =0 AND Barcode != -1"
    else:
        x = ""

    def add_q(x, query):
        if x:
            if query:
                query = query + " AND " + x
            else:
                query = x
        return query

    query = add_q(x, query)

    if self.tab4StateRadioButton1.isChecked():
        x = "Barcode != -1"
    elif self.tab4StateRadioButton2.isChecked():
        x = "Barcode = -1"
    else:
        x = ""
    query = add_q(x, query)

    if self.tab4FitterRadioButton1.isChecked():
        x = "Fitter=1"
    elif self.tab4FitterRadioButton2.isChecked():
        x = "Fitter=0"
    else:
        x = ""
    query = add_q(x, query)

    if query:
        query = "SELECT * FROM chemicals WHERE " + query + " ORDER BY CID ASC"
    else:
        query = "SELECT * FROM chemicals ORDER BY CID ASC"

    print(query)
    displayQ(self, query, self.combineCountLabel)


# whole database
def query_all(self):
    query = "SELECT * FROM chemicals"
    displayQ(self, query, self.allCountLabel)

# to-do list
def query_todo(self):
    query = "SELECT * FROM chemicals WHERE CF = 0 AND Barcode !=0 AND Barcode != -1 AND Fitter = 1 ORDER BY CID ASC"
    displayQ(self, query, self.todoCountLabel)

def getClickedCell(self, row, column):
    self.q_cid = self.table.item(row, 0).text()
    self.q_name = self.table.item(row, 1).text()
    self.q_cas = self.table.item(row, 2).text()
    self.q_barcode = self.table.item(row, 5).text()
    self.q_mw = self.table.item(row, 6).text()

    x = " ❚ "
    self.label_select.setText(self.q_cid + x + self.q_name + x + self.q_cas + x + self.q_barcode)


def query_select(self):
    r_drive = self.sampleRDriveLineEdit.toPlainText()
    if not os.path.exists(r_drive):
        self.tab4HintLabel.setText(" ! Error: R/Data drive not found.")
    else:
        try:
            folder = self.q_cid + " - " + self.q_name
            folder_path = os.path.join(r_drive, folder)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
                print('folder created.')
    
            self.sampleNameLineEdit.setText(folder)
            self.sampleCIDLineEdit.setText(self.q_cid)
            self.sampleWeightLineEdit.setText("")
            self.sampleMWLineEdit.setText(self.q_mw)
            self.tab4HintLabel.setText("• Information has been passed to Tab1.")
        except:
            self.tab4HintLabel.setText("! Cannot fill information automatically on Tab1.")


if __name__ == "__main__":
    print()
