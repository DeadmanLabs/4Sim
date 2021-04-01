import threading, json, queue, time
from datetime import datetime, timedelta
from oandapyV20 import API, V20Error
import oandapyV20.endpoints.pricing as pricing
from traderManager import threadManager

queueLock = threading.Lock()
traderQueue = queue.Queue(10)
traderManager = threadManager(traderQueue, 5, "ACCOUNT_ID", "API_TOKEN")
try:
    traderManager.start()
    while True:
        data = ""
        part = None
        while part == None:
            try:
                part = int(input("Which Trader would you like to perform? (0-" + str(len(traderManager.traders)) + "): "))
            except:
                print("Invalid Option!")
                part = None
        data += str(part) + '|'
        part = None
        while part not in actions:
            part = str(input("Which action would you like to take? ")).upper()
            if part not in actions and part != '?':
                print("Invalid Option! Enter '?' for a list of options.")
            if part == '?':
                print("Valid options are Enter, Exit, Info")
        data += str(part)
        if part == "EXIT":
            part = None
            while part == None:
                try:
                    part = int(input("What trade id would you like to close? "))
                    if part not in list(map(lambda x: x.id ,filter(lambda x: True if x.status == "" else False, traderManager.traders))):
                        part = None
                        raise Exception("Trade does not exist or is not open!")
                except:
                    print("Invalid Option!")
            data += '|' + str(part)
        elif part == "ENTER":
            extraParams = {}
            extraParams['price'] = None
            extraParams['tp'] = None
            extraParams['sl'] = None
            extraParams['timeInForce'] = ""
            extraParams['baseRates'] = None
            part = str(input("What symbol would you like to trade? "))
            sym = part
            data += '|' + part + '|'
            part = None
            while part == None:
                try:
                    part = int(input("How many units would you like to trade? "))
                except:
                    print("Invalid Option!")
                    part = None
            qty = part
            data += str(part) + '|'
                                                                                                #get market price
            r = pricing.PricingInfo(accountID=accId, params={'instruments': sym})
            rv = api.request(r)
            if qty > 0:
                data += r.response['prices'][0]['asks'][0]['price'] + '|'
            elif qty < 0:
                data += r.response['prices'][0]['bids'][0]['price'] + '|'
            
            print("For the following parameters, press Ctrl+C if you do not wish to enter them.")
            while extraParams['price'] == None:
                try:
                    extraParams['price'] = float(input("Enter your entry price: "))
                except KeyboardInterrupt:
                    extraParams['price'] = 0.0
                except:
                    print("Invalid Option!")
                    extraParams['price'] = None
            while extraParams['tp'] == None:
                try:
                    extraParams['tp'] = float(input("Enter your take profit level: "))
                except KeyboardInterrupt:
                    extraParams['tp'] = 0.0
                except:
                    print("Invalid Option!")
                    extraParams['tp'] = None
            while extraParams['sl'] == None:
                try:
                    extraParams['sl'] = float(input("Enter your stop loss level: "))
                except KeyboardInterrupt:
                    extraParams['sl'] = 0.0
                except:
                    print("Invalid Option!")
                    extraParams['sl'] = None
            times = ["GTC", "DTC"]                                                              #Add custom
            while extraParams['timeInForce'] not in times:
                try:
                    extraParams['timeInForce'] = str(input("Enter your order fill type: "))
                    if extraParams['timeInForce'] not in times:
                        raise Exception("Invalid Option!")
                except KeyboardInterrupt:
                    extraParams['timeInForce'] = "GTC"
                except:
                    print("Invalid Option!")
                    extraParams['timeInForce'] = ""
            
            if sym.split('_')[0] != "USD":
                rateSym = sym.split('_')[0] + "_USD"
                r = pricing.PricingInfo(accountID=accId, params={'instruments':rateSym})
                rv = api.request(r)
                extraParams['baseRates'] = { rateSym:{'bid': float(r.response['prices'][0]['bids'][0]['price']), 'ask': float(r.response['prices'][0]['asks'][0]['price'])} }
            
            data += json.dumps(extraParams)
            
        queueLock.acquire()
        traderQueue.put(data)
        queueLock.release()
        
        while not traderQueue.empty():
            pass
        
except KeyboardInterrupt:
    print("Escaped!")
    traderManager.stop()
