from datetime import datetime, timedelta
from trader import Trader
from oandapyV20 import API, V20Error
import oandapyV20.endpoints.pricing as pricing
import threading

class threadManager (threading.Thread):
    def __init__(self, q, tradersCount, accId, apiKey):
        threading.Thread.__init__(self)
        self.q = q
        self.traders = []
        for i in range(tradersCount):
            self.traders.append(Trader(1000, "XAU_USD", margin_rate=50))
        self.streamHandler = None
        self.accId = accId
        self.api = API(access_token=apiKey)
       
    def run(self):
        self.streamHandler = pricing.PricingStream(accountID=self.accId, params={'instruments':"XAU_USD"})
        rv = self.api.request(self.streamHandler)
        maxrecs = 100
        queueLock = threading.Lock()
        for ticks in rv:
            if ticks['type'] == 'PRICE':
                queueLock.acquire()
                if not traderQueue.empty():
                    data = self.q.get()
                    queueLock.release()
                    
                    data = data.split('|')
                    if data[1] == 'INFO':
                        print(str(self.traders[int(data[0])]))
                    elif data[1] == 'ENTER':
                        extraParams = json.loads(data[5])        #This is ugly but I dont have time to baby this shit
                        price = 0.0
                        sl = 0.0
                        tp = 0.0
                        timeInForce = "GTC"
                        baseRates = None
                        for param in extraParams:
                            if param == "price":
                                price = float(extraParams[param])
                            elif param == "sl":
                                sl = float(extraParams[param])
                            elif param == "tp":
                                tp = float(extraParams[param])
                            elif param == "timeInForce":
                                timeInForce = extraParams[param]
                            elif param == "baseRates":
                                baseRates = extraParams[param]
                        self.traders[int(data[0])].open(data[2], int(data[3]), float(data[4]), price=price, sl=sl, tp=tp, timeInForce=timeInForce, baseRates=baseRates)
                            
                    elif data[1] == 'EXIT':
                        if len(data) > 3:
                            self.traders[int(data[0])].exit(int(data[2]), float(data[3]), float(data[4]))
                        else:
                            self.traders[int(data[0])].exit(int(data[2]))
                else:
                    queueLock.release()
                    
                for trader in self.traders:
                    trader.step(float(ticks['bids'][0]['price']), float(ticks['asks'][0]['price']), ticks['time'][0:-4])
                    
                if maxrecs == 0:
                    self.streamHandler.terminate("maxrecs records received")
            
    def stop(self):
        self.streamHandler.terminate("Stream Closed!")
