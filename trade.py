from datetime import datetime, timedelta
class Trade:
    
    def __init__(self, symbol, qty, price, tp, sl, timeInForce, id, margin, time=None, marketPrice=None):
        self.unrealizedPL = 0.0
        self.realizedPL = 0.0
        self.atRisk = 0.0
        self.potProfit = 0.0
        self.exitPrice = 0.0
        self.exitDatetime = None
        self._overUnder = None
        
        self.id = id
        self.takeProfit = tp
        self.stopLoss = sl
        self.symbol = symbol
        self.qty = qty
        self.symbol = symbol
        self.margin = margin
        if timeInForce == "GTC":
            self.expiry = None
        elif timeInForce == "DTC":
            self.expiry = time + timedelta(days=1)
        elif timeInForce == "Custom":
            self.expiry = time
        if price != marketPrice:
            self.entryPrice = price
            if price > marketPrice:
                self._overUnder = "OVER"
            elif price < marketPrice:
                self._overUnder = "UNDER"
            self.entryDatetime = None
            self.status = "WAITING"
        else:
            self.entryPrice = price
            self.entryDatetime = time
            self.atRisk = (sl - self.entryPrice) * self.qty
            self.potProfit = (tp - self.entryPrice) * self.qty
            self.status = "OPEN"
        
    def step(self, time, bid, ask):
        if self.status == "WAITING":
            if self.expiry != None and self.expiry < time:
                self.status = "CLOSED"
            else:
                if self.qty > 0:
                    if self._overUnder == "OVER":
                        if self.ask >= self.entryPrice:
                            self.entryDatetime = time
                            self.status = "OPEN"
                            self.atRisk = (self.stopLoss - self.entryPrice) * self.qty
                            self.potProfit = (self.takeProfit - self.entryPrice) * self.qty
                    if self._overUnder == "UNDER":
                        if self.ask <= self.entryPrice:
                            self.entryDatetime = time
                            self.status = "OPEN"
                            self.atRisk = (self.stopLoss - self.entryPrice) * self.qty
                            self.potProfit = (self.takeProfit - self.entryPrice) * self.qty
                elif self.qty < 0:
                    if self._overUnder == "OVER":
                        if self.bid >= self.entryPrice:
                            self.entryDatetime = time
                            self.status = "OPEN"
                            self.atRisk = (self.stopLoss - self.entryPrice) * self.qty
                            self.potProfit = (self.takeProfit - self.entryPrice) * self.qty
                    if self._overUnder == "UNDER":
                        if self.bid <= self.entryPrice:
                            self.entryDatetime = time
                            self.status = "OPEN"
                            self.atRisk = (self.stopLoss - self.entryPrice) * self.qty
                            self.potProfit = (self.takeProfit - self.entryPrice) * self.qty
        if self.status == "OPEN":
            if self.qty > 0:
                self.unrealizedPL = (bid - self.entryPrice) * self.qty
                if bid >= self.takeProfit and self.takeProfit != 0.0:
                    self.close(time, bid, ask)
                    return True
                elif bid <= self.stopLoss and self.stopLoss != 0.0:
                    self.close(time, bid, ask)
                    return True
            elif self.qty < 0:
                self.unrealizedPL = (ask - self.entryPrice) * self.qty
                if ask <= self.takeProfit and self.takeProfit != 0.0:
                    self.close(time, bid, ask)
                    return True
                elif ask >= self.stopLoss and self.stopLoss != 0.0:
                    self.close(time, bid, ask)
                    return True
        
    def close(self, time, bid, ask):
        self.step(time, bid, ask)
        self.realizedPL = self.unrealizedPL
        self.exitDatetime = time
        self.status = "CLOSED"
        if self.qty > 0:
            self.exitPrice = bid
        elif self.qty < 0:
            self.exitPrice = ask
