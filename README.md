''' General tools '''
class Tools(object):
    ''' Log handler '''
    def __init__(self):
    def logInit(self):
    def normalizeUSD(self, USD):
    def normalizeCOIN(self, coin):

''' Main Client Stuffs '''
class Client(object):
    def __init__(self, log, tools, passphrase=None, apiKey=None, apiSecret=None):
        self.log = self.logInit()
    def getOrders(self):
    def getOrder(self, tradeId):
    def getFills(self):
    def getProductOrderBook(self, market, kwargs):

    class Trade(object):
        def __init__(self, outer):
            self.authClient = ''
            self.log = log
            self.tools = tools
            self.passphrase = passphrase
            self.apiKey = apiKey
            self.apiSecret = apiSecret
        def sell(self, sellPrice, qty, market):
        def buy(self, buyPrice, qty, market):
        def status(self, tradeId):
        def settled(self, tradeId):

    class Accounts(object):
        def __init__(self, outer):
            self.balance = {}
            self.orders = []
            self.accounts = []
            self.fills = {}

        def get(self):
        def getHistory(self, accountId=None):
        def available(self, coin):
        def updateAll(self):
        def updateTransfers(self, coin):
        def updateBalances(self):
        def updateOrders(self):
        def updateFills(self, coin):

    class Table(object):
        def __init__(self, outer):
            self.orders = {}
            self.spread = 0.00
            self.sellBottom = 0.00
            self.buyTop = 0.00

        def update(self, market):
