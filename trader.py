from datetime import datetime, timedelta
from trade import Trade
class Trader:

    def __init__(self, initial, symbol, commission=0.00, margin_rate=500):
        self.state = {'bid': 0.0, 'ask': 0.0, 'date': datetime.strptime("1970-01-01T00:00:00.000", "%Y-%m-%dT%H:%M:%S.%f")}
        self.initial = initial
        self.balance = initial
        self.equity = initial
        self.commission = commission
        self.symbol = symbol
        self.marginRate = 500
        self.freeMargin = initial
        self.usedMargin = 0
        self.trades = []
        self._specialitySymbols = []

    def _calculateMargin(self, symbol, qty, marginRate, baseRates=None):
        baseHome = symbol.split('_')
        if baseHome[0] == "USD":
            return abs(qty) / marginRate
        else:
            marginSymbol = baseHome[0] + '_' + "USD"              #This has really cool properties with how tickers work, basically
            if qty > 0:                                           #you will never have margin in JPY so all USD pairs are ___USD
                return (abs(qty) * baseRates[marginSymbol]['bid']) / marginRate #except for the USDJPY pair
            elif qty < 0:
                return (abs(qty) * baseRates[marginSymbol]['ask']) / marginRate

    def open(self, symbol, qty, marketPrice, price=0.0, tp=0.0, sl=0.0, timeInForce="GTC", baseRates=None):
        margin = 0
        id = len(self.trades)
        if symbol.split('_')[0] != 'USD':
            margin = self._calculateMargin(symbol, qty, self.marginRate, baseRates)
        else:
            margin = self._calculateMargin(symbol, qty, self.marginRate)
        self.freeMargin -= margin
        self.usedMargin += margin
        print("price: " + str(price) + " marketPrice: " + str(marketPrice))
        if price != 0.0:
            self.trades.append(Trade(symbol, qty, price, tp, sl, timeInForce, id, margin, time, self.state['date'], marketPrice))
        else:
            self.trades.append(Trade(symbol, qty, marketPrice, tp, sl, timeInForce, id, margin, self.state['date'], marketPrice))

    def close(self, id, bid=0.0, ask=0.0):
        for trade in self.trades:
            if trade.id == id:
                if bid == 0.0 or ask == 0.0:
                    trade.close(state['date'], state['bid'], state['ask'])
                    self.freeMargin += trade.margin
                    self.usedMargin -= trade.margin
                else:
                    trade.close(state['date'], bid, ask)
                    self.freeMargin += trade.margin
                    self.usedMargin += trade.margin

    def step(self, bid, ask, date):
        self.state = {'bid': bid, 'ask': ask, 'date':datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")}
        for trade in self.trades:
            retVal = trade.step(self.state['date'], self.state['bid'], self.state['ask'])
            if retVal == True:
                self.freeMargin += trade.margin
                self.usedMargin -= trade.margin

    def __str__(self):
        result = ""
        result += "Initial Capital: " + str(self.initial) + "\n"
        result += "Current Balance: " + str(self.balance) + "\n"
        result += "Current Equity:  " + str(self.equity) + "\n"
        result += "Net Change:      " + str(round(((self.balance - self.initial) / self.initial) * 100, 4)) + "%" + "\n"
        result += "Free Margin:     " + str(self.freeMargin) + "\n"
        result += "Used Margin:     " + str(self.usedMargin) + "\n"
        result += "Total Trades:    " + str(len(self.trades)) + "\n"
        result += "Open Trades:     " + str(len(list(filter(lambda x: True if x.status == "open" else False, self.trades)))) + "\n"
        result += "Unrealized P&L:  " + str(sum(list(filter(lambda x: x.unrealizedPL if x.status == "open" else 0.0, self.trades)))) + "\n"
        return result

    def view(self):
        result = ""
        for trade in self.trades:
            result += trade.symbol

