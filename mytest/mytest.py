from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QAxContainer import *
from PyQt4.QtCore import QVariant
import re
import sys
import datetime, time
import pandas_datareader.data as web
from pandas import Series, DataFrame
import matplotlib.pyplot as plt

class Ui_Form(QAxWidget):
    def __init__(self):
        super().__init__()
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')
        self.connect(self, SIGNAL("OnEventConnect(int)"), self.OnEventConnect)
        self.connect(self, SIGNAL("OnReceiveMsg(QString, QString, QString, QString)"), self.OnReceiveMsg)
        self.connect(self, SIGNAL("OnReceiveTrData(QString, QString, QString, QString, QString, int, QString, QString, QString)"), self.OnReceiveTrData)
        self.connect(self, SIGNAL("OnReceiveChejanData(QString, int, QString)"),self.OnReceiveChejanData)

class MainWindow(QAxWidget):
    def __init__(self):
        super().__init__()
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')
        self.connect(self, SIGNAL("OnEventConnect(int)"), self.OnEventConnect)
        self.connect(self, SIGNAL("OnReceiveMsg(QString, QString, QString, QString)"), self.OnReceiveMsg)
        self.connect(self, SIGNAL(
            "OnReceiveTrData(QString, QString, QString, QString, QString, int, QString, QString, QString)"),
                     self.OnReceiveTrData)
        self.connect(self, SIGNAL("OnReceiveChejanData(QString, int, QString)"), self.OnReceiveChejanData)

    def btn_login(self):
        ret = self.dynamicCall("CommConnect()")

    def btn_getAccInfo(self):
        ACCOUNT_CNT = self.dynamicCall('GetLoginInfo("ACCOUNT_CNT")')
        ACC_NO = self.dynamicCall('GetLoginInfo("ACCNO")')
        ACC_NO = ACC_NO.rstrip(';')
        ret = self.dynamicCall('SetInputValue(QString, QString)', "계좌번호", ACC_NO)
        ret = self.dynamicCall('SetInputValue(QString, QString)', "비밀번호", "")
        ret = self.dynamicCall('SetInputValue(QString, QString)', "상장폐지조회구분", "0")
        ret = self.dynamicCall('SetInputValue(QString, QString)', "비밀번호입력매체구분", "")
        self.lineEdit6.setText(ACC_NO)

    def btn_Quit(self):
        self.dynamicCall("CommTerminate()")
        sys.exit()

    def OnEventConnect(self, nErrCode):
        if nErrCode == 0:
            self.textEdit1.append("서버에 연결 되었습니다...")
            self.GetInfoBtn.setEnabled(True)
            self.SendOrder.setEnabled(False)
            self.LoginBtn.setEnabled(False)
            self.LoginBtn.setText(self.dynamicCall('GetLoginInfo("USER_ID")'))
            self.AccInfoBtn.setEnabled(True)
            self.textEdit1.setEnabled(True)
            self.textEdit2.setEnabled(True)
            self.comboBox.setEnabled(True)
            self.lineEdit1.setEnabled(True)
            self.lineEdit3.setEnabled(True)
            self.lineEdit4.setEnabled(True)
            self.lineEdit5.setEnabled(True)
            self.FindTRBtn.setEnabled(True)
        else:
            self.textEdit.append("서버 연결에 실패 했습니다...")
            print("서버 연결에 실패 했습니다...")

    def btn_getTRInfo(self):
        Code = self.lineEdit1.text().strip()
        ret = self.dynamicCall('SetInputValue(QString, QString)', "종목코드", Code)
        ret = self.dynamicCall('CommRqData(QString, QString, int, QString)', "주식기본정보", "OPT10001", 0, "0101")
        self.SendOrder.setEnabled(True)

    def btn_SendOrder(self):
        #HogaGb = "00"
        Type = int(self.comboBox.currentText()[0:1].strip())
        Code = self.lineEdit1.text().strip()
        Qty = int(self.lineEdit3.text().strip())
        Price = int(self.lineEdit4.text().strip())
        OrgNo = self.lineEdit5.text().strip()
        ACCNO = self.lineEdit6.text().strip()
        Order = self.dynamicCall('SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)', ["주식주문", "0107", ACCNO, Type, Code, Qty, Price,"00", OrgNo])
        self.SendOrder.setEnabled(False)

    def OnReceiveMsg(self, sScrNo, sRQName, sTrCode, sMsg):
        if sScrNo == "0003":
            print(sMsg)
            self.textEdit1.append(sMsg)

        else:
            print(sMsg)
            self.textEdit1.append(sMsg)

    def btn_FindTRBtn(self):
        self.GetHighTR() #거래량급증요청
        self.GetLowPer() #저PER요청
        self.FindCondBtn.setEnabled(True)
        #self.GetDailyPrice("015760") # 해당 코드 일별주가

    def btn_FindCondBtn(self):
        self.CompDataSet()  # 거래량급증 & 저PER 코드

    def GetLowPer(self):
        self.dynamicCall('SetInputValue(QString,QString)', "PER구분", "1")
        self.dynamicCall('CommRqData(QString,QString,int,QString)', "저PER", "opt10026", 2, "0171")

    def GetHighTR(self):
        self.dynamicCall('SetInputValue(QString,QString)', "시장구분", "001")
        self.dynamicCall('SetInputValue(QString,QString)', "정렬구분", "2")
        self.dynamicCall('SetInputValue(QString,QString)', "시간구분", "2")
        self.dynamicCall('SetInputValue(QString,QString)', "거래량구분", "50")
        self.dynamicCall('SetInputValue(QString,QString)', "시간", "30")
        self.dynamicCall('SetInputValue(QString,QString)', "종목조건", "1")
        self.dynamicCall('SetInputValue(QString,QString)', "가격구분", "0")
        self.dynamicCall('CommRqData(QString,QString,int,QString)', "거래량급증", "OPT10023", 0, "0168")

    def CompDataSet(self):
        pf = open("per.txt",'r')
        hf = open("QInc.txt",'r')
        sf = open("same.txt",'w')
        pfdata = pf.readlines()
        hfdata = hf.readlines()
        self.textEdit2.append("==모든 조건 만족 종목==")
        for pfline in pfdata:
            for hfline in hfdata:
                if pfline[0:6] == hfline[0:6]:
                    self.textEdit2.append(pfline)
                    sf.write(pfline)
        pf.close()
        hf.close()
        sf.close()

    def GetDailyPrice(self,Code):
        start = datetime.datetime(2015, 2, 19)
        end = datetime.datetime(2016, 2, 19)
        end = end.today()
        Code = Code + ".KS"
        gs = web.DataReader(Code, "yahoo", start, end)
        gs = gs[gs['Volume']!=0]
        self.DrawGraph(gs)

    def DrawGraph(self,dataframe):
        dataframe = dataframe[dataframe['Volume'] != 0]
        dataframe['MA5'] = dataframe['Adj Close'].rolling(window=5).mean()
        dataframe['MA20'] = dataframe['Adj Close'].rolling(window=20).mean()
        dataframe['MA60'] = dataframe['Adj Close'].rolling(window=60).mean()
        dataframe['MA120'] = dataframe['Adj Close'].rolling(window=120).mean()
        print(dataframe)
        fig = plt.figure()
        plt.plot(dataframe.index, dataframe['Adj Close'], label="Adj Close")
        plt.plot(dataframe.index, dataframe['MA5'], label="MA5")
        plt.plot(dataframe.index, dataframe['MA20'], label="MA20")
        plt.plot(dataframe.index, dataframe['MA60'], label="MA60")
        plt.plot(dataframe.index, dataframe['MA120'], label="MA120")
        plt.legend(loc='best')
        plt.grid()
        plt.show()

    def GetChjanData(self, nFid):
        chjang = self.dynamicCall('GetChejanData(QString)', nFid)
        return chjang

    def OnReceiveChejanData(self, sGubun, nItemCnt, sFidList):
        self.lineEdit5.setText(self.GetChjanData(9203))
        self.textEdit1.append("주문번호: " + self.GetChjanData(9203))
        self.textEdit1.append("종 목 명: " + self.GetChjanData(302))
        self.textEdit1.append("주문수량: " + self.GetChjanData(900))
        self.textEdit1.append("주문가격: " + self.GetChjanData(901))

    def OnReceiveTrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPreNext, nDataLength, sErrorCode, sMessage,
                        sSPlmMsg):
        if sRQName == "주식기본정보":
            cnt = self.dynamicCall('GetRepeatCnt(QString, QString)', sTrCode, sRQName)
            종목명 = self.dynamicCall('CommGetData(QString, QString, QString, int, QString)', sTrCode, "", sRQName, 0,
                                   "종목명")
            현재가 = self.dynamicCall('CommGetData(QString, QString, QString, int, QString)', sTrCode, "", sRQName, 0,
                                   "현재가")
            self.textEdit1.append("종목명: " + 종목명.strip())
            self.textEdit1.append("현재가: " + 현재가.strip())

        elif sRQName == "저PER":
            i=0
            f = open("per.txt",'w')
            perlist = self.dynamicCall('GetCommDataEx(QString,QString)',sTrCode,sRQName)
            self.textEdit2.append("==Low PER 3==")
            while i < 100:
                if i < 3:
                    self.textEdit2.append("종목코드: " + perlist[i][0])
                    self.textEdit2.append("종목명: " + perlist[i][1])
                    self.textEdit2.append("PER: " + perlist[i][2])
                    self.textEdit2.append("")
                f.write(perlist[i][0]+"\t")
                f.write(perlist[i][1]+"\n")
                i += 1
            f.close()

        elif sRQName == '거래량급증':
            i = 0
            qi = open("QInc.txt", 'w')
            qilist = self.dynamicCall('GetCommDataEx(QString,QString)', sTrCode, sRQName)
            self.textEdit2.append("==거래량급증 Top 3==")
            while i < 100:
                if i < 3:
                    self.textEdit2.append("종목코드: " + qilist[i][0])
                    self.textEdit2.append("종목명: " + qilist[i][1])
                    self.textEdit2.append("급증률: " + qilist[i][9])
                    self.textEdit2.append("")
                qi.write(qilist[i][0] + "\n")
                i += 1
            qi.close()

        else:
            pass

    def UIsetup(self, Form):
        Form.setWindowTitle("완성시키자! From 16.05.24 ~ ")
        Form.setObjectName("Form")
        Form.resize(585, 505)
        self.groupBox1 = QtGui.QGroupBox(Form)
        self.groupBox1.setTitle(" 간편 매매 ")
        self.groupBox1.setGeometry(QtCore.QRect(10,10,220,225))
        self.groupBox1.setObjectName("groupBox1")
        self.formLayoutWidget = QtGui.QWidget(self.groupBox1)
        self.formLayoutWidget.setGeometry(QtCore.QRect(9, 20, 191, 161))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName("formLayout")
        self.textEdit1 = QtGui.QTextEdit(Form)
        self.textEdit1.setEnabled(False)
        self.textEdit1.setGeometry(QtCore.QRect(240, 17, 335, 218))
        self.textEdit1.setObjectName("textEdit1")
        self.groupBox2 = QtGui.QGroupBox(Form)
        self.groupBox2.setTitle(" 인공지능 트레이딩 ")
        self.groupBox2.setGeometry(QtCore.QRect(10, 240, 220, 225))
        self.groupBox2.setObjectName("groupBox2")
        self.textEdit2 = QtGui.QTextEdit(Form)
        self.textEdit2.setEnabled(False)
        self.textEdit2.setGeometry(QtCore.QRect(240, 247, 335, 218))
        self.textEdit2.setObjectName("textEdit2")

        self.lineEdit1 = QtGui.QLineEdit(self.formLayoutWidget)
        self.lineEdit1.setEnabled(False)
        self.lineEdit1.setObjectName("lineEdit1")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineEdit1)
        self.label1 = QtGui.QLabel(self.formLayoutWidget)
        self.label1.setText("종목코드")
        self.label1.setObjectName("label1")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label1)

        self.label2 = QtGui.QLabel(self.formLayoutWidget)
        self.label2.setText("매매구분")
        self.label2.setObjectName("label2")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label2)

        self.label3 = QtGui.QLabel(self.formLayoutWidget)
        self.label3.setText("주문수량")
        self.label3.setObjectName("label3")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label3)
        self.lineEdit3 = QtGui.QLineEdit(self.formLayoutWidget)
        self.lineEdit3.setEnabled(False)
        self.lineEdit3.setObjectName("lineEdit3")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.lineEdit3)

        self.label4 = QtGui.QLabel(self.formLayoutWidget)
        self.label4.setText("주문가격")
        self.label4.setObjectName("label4")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label4)
        self.lineEdit4 = QtGui.QLineEdit(self.formLayoutWidget)
        self.lineEdit4.setEnabled(False)
        self.lineEdit4.setObjectName("lineEdit4")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.lineEdit4)

        self.label5 = QtGui.QLabel(self.formLayoutWidget)
        self.label5.setText("원주문번호")
        self.label5.setObjectName("label5")
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.label5)
        self.lineEdit5 = QtGui.QLineEdit(self.formLayoutWidget)
        self.lineEdit5.setEnabled(False)
        self.lineEdit5.setObjectName("lineEdit5")
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.lineEdit5)

        self.label6 = QtGui.QLabel(self.formLayoutWidget)
        self.label6.setText("계좌번호")
        self.label6.setObjectName("label6")
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.label6)
        self.lineEdit6 = QtGui.QLineEdit(self.formLayoutWidget)
        self.lineEdit6.setEnabled(False)
        self.lineEdit6.setObjectName("lineEdit6")
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.lineEdit6)

        self.comboBox = QtGui.QComboBox(self.formLayoutWidget)
        self.comboBox.setEnabled(False)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("1:   매   수")
        self.comboBox.addItem("2:   매   도")
        self.comboBox.addItem("3:   매수취소")
        self.comboBox.addItem("4:   매도취소")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.comboBox)

        self.GetInfoBtn = QtGui.QPushButton(self.groupBox1)
        self.GetInfoBtn.setText("종목정보")
        self.GetInfoBtn.setEnabled(False)
        self.GetInfoBtn.setGeometry(QtCore.QRect(15, 190, 75, 23))
        self.GetInfoBtn.setObjectName("GetInfoBtn")
        self.connect(self.GetInfoBtn, SIGNAL("clicked()"), self.btn_getTRInfo)

        self.SendOrder = QtGui.QPushButton(self.groupBox1)
        self.SendOrder.setText("주 문")
        self.SendOrder.setEnabled(False)
        self.SendOrder.setGeometry(QtCore.QRect(117, 190, 75, 23))
        self.SendOrder.setObjectName("SendOrder")
        self.connect(self.SendOrder, SIGNAL("clicked()"), self.btn_SendOrder)

        self.FindTRBtn = QtGui.QPushButton(self.groupBox2)
        self.FindTRBtn.setText("Low_PER && 거래량급증")
        self.FindTRBtn.setEnabled(False)
        self.FindTRBtn.setGeometry(QtCore.QRect(15, 30, 155, 23))
        self.FindTRBtn.setObjectName("FindTRBtn")
        self.connect(self.FindTRBtn, SIGNAL("clicked()"), self.btn_FindTRBtn)

        self.FindCondBtn = QtGui.QPushButton(self.groupBox2)
        self.FindCondBtn.setText("검색결과 부합종목")
        self.FindCondBtn.setEnabled(False)
        self.FindCondBtn.setGeometry(QtCore.QRect(15, 65, 155, 23))
        self.FindCondBtn.setObjectName("FindCondBtn")
        self.connect(self.FindCondBtn, SIGNAL("clicked()"), self.btn_FindCondBtn)

        self.LoginBtn = QtGui.QPushButton(Form)
        self.LoginBtn.setGeometry(QtCore.QRect(340, 475, 75, 23))
        self.LoginBtn.setObjectName("LoginBtn")
        self.connect(self.LoginBtn, SIGNAL("clicked()"), self.btn_login)
        self.LoginBtn.setText("로그인")

        self.AccInfoBtn = QtGui.QPushButton(Form)
        self.AccInfoBtn.setEnabled(False)
        self.AccInfoBtn.setGeometry(QtCore.QRect(420, 475, 75, 23))
        self.AccInfoBtn.setObjectName("AccInfoBtn")
        self.connect(self.AccInfoBtn, SIGNAL("clicked()"), self.btn_getAccInfo)
        self.AccInfoBtn.setText("계좌조회")

        self.QuitBtn = QtGui.QPushButton(Form)
        self.QuitBtn.setGeometry(QtCore.QRect(500, 475, 75, 23))
        self.QuitBtn.setObjectName("QuitBtn")
        self.connect(self.QuitBtn, SIGNAL("clicked()"), self.btn_Quit)
        self.QuitBtn.setText("종 료")

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = MainWindow()
    ui.UIsetup(Form)
    Form.show()
    sys.exit(app.exec_())