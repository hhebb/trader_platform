from .base_exhange import Exchange
from PyQt5.QAxContainer import *
import pythoncom
import queue
import time
import pandas as pd
from datetime import datetime, timedelta

class KiwoomExchange:
    def __init__(self):
        # super().__init__()
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self.OnEventConnect)
        self.ocx.OnReceiveTrData.connect(self.OnReceiveTrData)
        self.login = False
        self.tr = False
        self.tr_queue = list() # buffer
        self.buffer = list()
        # self.tr_data = dict()

    def connect(self):
        self.CommConnect()
    

    def set_preference(self, preference):
        self.preference = preference

    def get_data(self):
        # 마지막 처리 필요
        self.start_date = self.preference.range[0]
        self.end_date = self.preference.range[1]
        self.cur_date = None
        
        # buffer = list()
        self.next = 0

        for code in self.preference.items:
            cur_date = None
            info = ('stock', 'candle', '1s', code)
            while True:
                self.SetInputValue("종목코드", code)
                self.SetInputValue("틱범위", "1")
                self.SetInputValue("수정주가구분", "0")
                self.CommRqData("ex", "opt10080", self.next, "0101")

                df = pd.DataFrame(self.buffer[::-1], columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                yield df, info

                time.sleep(.5)

                ######################################

                # # 현재 날짜 초기화
                # if cur_date == None:
                #     cur_date = datetime.strptime(self.tr_queue[0][0], "%Y%m%d%H%M%S").date()
                
                # # 하나씩 비우다가 날짜 바뀌면 내보냄
                # while self.tr_queue:
                #     popped = self.tr_queue.pop(0)
                #     buffer.append(popped)
                    
                #     if cur_date != datetime.strptime(popped[0], "%Y%m%d%H%M%S").date():
                #         print(cur_date)
                #         info = ('stock', 'candle', '1s', code, buffer[0][0])
                #         yield buffer, info
                #         buffer = list()
                #         cur_date = datetime.strptime(popped[0], "%Y%m%d%H%M%S").date()
                        
                # no more data, no more loop
                if self.next == '2':
                    self.next = 2
                    self.tr = True
                else:
                    break
                

    #####################################################
    # API dependent

    def CommConnect(self):
        self.ocx.dynamicCall("CommConnect()")
        while self.login is False:
            pythoncom.PumpWaitingMessages()

    def OnEventConnect(self, code):
        self.login = True
        print("login is done", code)

    def OnReceiveTrData(self, screen, rqname, trcode, record, next):
        # rqname 에 ex 붙여서 통째로 받는 방법도 만들어놓기
        self.tr = True

        rows = self.GetRepeatCnt(trcode, record)
        if rows == 0:
            rows = 1

        data = list()
        for row in range(rows):
            date = self.GetCommData(trcode, rqname, row, "체결시간")
            open = self.GetCommData(trcode, rqname, row, "시가")
            high = self.GetCommData(trcode, rqname, row, "고가")
            low  = self.GetCommData(trcode, rqname, row, "저가")
            close = self.GetCommData(trcode, rqname, row, "현재가")
            volume = self.GetCommData(trcode, rqname, row, "거래량")

            data.append((date, open, high, low, close, volume))
        # self.tr_queue.extend(data)
        self.buffer = data
        self.next = next

    def GetCodeListByMarket(self, market):
        ret = self.ocx.dynamicCall("GetCodeListByMarket(QString)", market)
        codes = ret.split(';')[:-1]
        return codes

    def GetMasterCodeName(self, code):
        ret = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
        return ret

    def SetInputValue(self, id, value):
        self.ocx.dynamicCall("SetInputValue(QString, QString)", id, value)

    def CommRqData(self, rqname, trcode, next, screen):
        self.tr = False
        self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen)
        while self.tr is False:
            pythoncom.PumpWaitingMessages()

    def GetCommData(self, trcode, rqname, index, item):
        data = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, index, item)
        return data.strip()
    
    def GetCommDataEx(self, trcode, rqname):
        data = self.ocx.dynamicCall("GetCommDataEx(QString, QString)", trcode, rqname)
        return data


    def GetRepeatCnt(self, trcode, record):
        data = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, record)
        return data        