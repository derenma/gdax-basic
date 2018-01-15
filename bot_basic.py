''' Our main gdax sdk and our sdk wrapper'''
import gdax
import logging, json, os, sys

''' General tools '''
class Tools(object):
    ''' Log handler '''
    def __init__(self):
        self.log = self.logInit()

    def logInit(self):
        log = logging.getLogger("BasicBot")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        log.addHandler(handler)
        # Pick your logging level
        log.setLevel(logging.DEBUG)
        #log.setLevel(logging.INFO)
        #log.setLevel(logging.ERROR)
        #log.setLeve(Logging.NONE)  # I _think_ 'NONE' is a thing.  May esplode if used....
        return log

    '''
    Currency floating point normalization
    (GDAX returns account values in 0.0000000000000000 format)
    '''
    def normalizeUSD(self, USD):
        USD = '{0:.2f}'.format(USD)
        return USD

    def normalizeCOIN(self, coin):
        coin = '{0:.8f}'.format(coin)
        return coin

'''
Client Wrapper
(We wrap the base SDK to better handle exceptions and logging MUCH better, you will thank me later.)
'''
class Client(object):
    def __init__(self, log, tools, passphrase=None, apiKey=None, apiSecret=None):
        self.authClient = ''
        self.log = log
        self.tools = tools
        self.passphrase = passphrase
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        try:
            self.authClient = gdax.AuthenticatedClient(apiKey, apiSecret, passphrase)
        except Exception as e:
            log.error("Failed to authenticate: %s" % e)
            exit()

        # Build our objects for innter classes...
        self.accounts = self.Accounts(self)
        self.table = self.Table(self)
        self.trade = self.Trade(self)

    '''
    Basically just placeholders if we need better exception handling later.
    If you wrap SDK methods, "You must have one class to bind them all" - Frodo
    '''

    def getOrders(self):
        return self.authClient.get_orders()

    def getOrder(self, tradeId):
        return self.authClient.get_order(tradeId)

    def getFills(self):
        return self.authClient.get_fills()

    def getProductOrderBook(self, market, **kwargs):
        return self.authClient.get_product_order_book(self.market, **kwargs)

    class Trade(object):
        def __init__(self, outer):
            self.authClient = outer.authClient

        ''' Main Actions '''
        def sell(self, sellPrice, qty, market):
            result = self.authClient.sell(price=sellPrice, size=qty, product_id=market, post_only=True)

            if 'id' not in result:
                self.log.error("Sell Failed for %s at %s with error %s" % (sellPrice, qty, json.dumps(result, indent=4)))
                return False
            else:
                print('Placed Sell: Price: {0} | Quantity: {1} | Market {2}').format(sellPrice, qty, market)

            return result

        def buy(self, buyPrice, qty, market):
            result = self.authClient.buy(price=buyPrice, size=qty, product_id=self.market, post_only=True)

            if 'id' not in result:
                self.log.error("Buy Failed for %s at %s with error %s" % (buyPrice, qty, json.dumps(result, indent=4)))
                return False
            else:
                print('Placed Buy: Price: {0} | Quantity: {1} | Market {2}').format(buyPrice, qty, market)

            return result

        def status(self, tradeId):
            try:
                status = self.authClient.get_order(tradeId)

                # Double check for canceled order... either condition is bad.
                if 'message' in status:
                    if 'NotFound' in status['message']:
                        return "NotFound"
                if 'id' not in status:
                    return "NotFound"

                # Did we do it? Did we do it? Did we do it? Did we do it? Did we do it? Did we do it? Did we do it? Did we do it? Did we do it? Did we do it? Did we do it?
                if 'settled' in status:
                    if status['settled'] is True:
                        sold = True
                        return "Settled"

                if 'status' in status:
                    if "done" in status['status']:
                        sold = True
                        return "Settled"

                return status

            except Exception as e:
                self.log.error("validateOrder failed with exception %s" % e)

        def settled(self, tradeId):
            if self.status(tradeId) is "Settled":
                return True
            else:
                return False


    class Accounts(object):
        def __init__(self, outer):
            self.authClient = outer.authClient
            self.log = outer.log

            ''' Global Account Data '''
            self.balance = {}
            self.orders = []
            self.accounts = []
            self.fills = {}

            ''' Inital Updating of all the data '''
            #self.update()

        def get(self):
            return self.authClient.get_accounts()

        def getHistory(self, accountId=None):
            if accountID is None:
                self.log.error("accounts.getHistory requires accountId be passed")
            else:
                return self.authClient.get_account_history(accountId)

        def available(self, coin):
            return self.balance[coin]['available']

        ''' Update ALL Financials '''
        def updateAll(self):
            self.log.infos("Updating balance, order, transfer and fill data.")
            self.updateBalances()
            self.updateOrders()
            self.updateTransfers()
            self.updateFills()

        def updateTransfers(self, coin):
            self.updateBalances()
            accountId = self.balance[coin]['id']

            print "Account id: %s" % accountId
            history = self.client.get_account_history(accountId)

            value = 0
            for pidx,page in enumerate(history):
                for tidx,xfer in enumerate(page):
                    if xfer['type'] == "transfer":
                        print xfer
                        value+=float(xfer['amount'])

            self.startFunds = value + self.ethFromBtc

        def updateBalances(self):
            accounts = self.authClient.get_accounts()

            for account in accounts:
                #self.log.info("account %s" % account)
                self.balance[account['currency']] = {'balance':'{:.20f}'.format(float(account['balance']))}
                self.balance[account['currency']].update({'available':'{:.20f}'.format(float(account['available']))})
                self.balance[account['currency']].update({'hold':'{:.20f}'.format(float(account['hold']))})
                self.balance[account['currency']].update({'profile_id':account['profile_id']})
                self.balance[account['currency']].update({'id':account['id']})

        def updateOrders(self):
            orders = self.authClient.get_orders()

            for order in orders:
                self.orders[order['id']] = {'id':order['id']}
                self.orders[order['id']].update({'price':order['price']})
                self.orders[order['id']].update({'size':order['size']})
                self.orders[order['id']].update({'status':order['status']})
                self.orders[order['id']].update({'settled':order['settled']})

        def updateFills(self, coin):
            fill_pages = self.authClient.get_fills(product_id=coin)

            idx = 0
            for pidx,page in enumerate(fill_pages):
                for tidx,trade in enumerate(page):
                    self.fills[idx] = trade
                    #print pidx,tidx,trade
                    idx+=1

    class Table(object):
        def __init__(self, outer):
            self.authClient = outer.authClient
            self.log = outer.log

            self.orders = {}
            self.spread = 0.00
            self.sellBottom = 0.00
            self.buyTop = 0.00

        def update(self, market):
            self.orders = self.authClient.getProductOrderBook(market,level=2)
            self.spread = float(self.orders['asks'][0][0]) - float(self.orders['bids'][0][0])
            self.sellBottom = float(self.orders['asks'][0][0])  # Lowest Sell Price
            self.buyTop = float(self.orders['bids'][0][0])      # Highest Buy Price

def demo():

    ''' Initalize our general tools and log handlers '''
    tools = Tools()
    log = tools.log  # We are referencing a class object! (or class variable, whatever makes you happy)


    ''' Authenticate and initalize our client object '''
    # (log, tools, passphrase=None, apiKey=None, apiSecret=None)
    gdax = Client(log, tools, passphrase="X", apiKey="X", apiSecret="")


    '''
    Class and subclass access:
        gdax.trade.buy(..)
        gdax.trade.sell(..)
        gdax.table.update("BTC-ETH")
        gdax.accounts.get()
    '''

    '''
    Currency and floating points:
        normalizedCoin = tools.normalizeCOIN("0.0000000000000000") # Returns "0.00000000"

        ProTip: If you don't know if a variable needs to be normalized, just fucking normalize it.
                If you don't know if a variable is a float type, just fucking make it a float.

                GDAX loves to give back 20x place floats, but will bork if you try and send one back
                to its API.  Fuck you GDAX.
                This is ESPECIALLY useful after math:
                    buyQuantity = tools.normalizeCOIN(float(buyQuantity) - float(errorMargin))

                Normalization WILL round up.  This can cause a trade to fail if you attempt to
                execute a trade that consumes 100% of your funds.

                float() your variables during math ALWAYS.

                You want to pass a str back to API ALWAYS.
    '''


    ''' Basic trading and validation
        result = gdax.trade.sell(sellprice, quantity, "ETH-BTC")
        if result is False:
            print "OMG"
            exit()
        else:
            print result

        gdax.trade.sell(buyprice, quantity, "ETH-BTC")


        # Again, we update our class variables instead of making direct API calls
        gdax.table.update("ETH-BTC")
        for order in gdax.table.orders():
            print order
    '''


    '''
    Direct access to account information.
    GDAX JSON is dumb:
        [ <- JSON array
        { <- JSON object
            "available": "0.00000362110355",
            "balance": "0.0000036211035500",
            "currency": "USD",
            "hold": "0.0000000000000000",
            "id": "254c1864-d0bd-4752-916c-868c7faef9fe",
            "profile_id": "7cfa144d-f376-4cbe-92bc-b139ffc234b9"
        }, ....
    '''
    print "----------------------------------  Raw API Data Access"
    print gdax.accounts.get()       # Raw print
    balances = gdax.accounts.get()  # Store in python "list" aka "array"
    print json.dumps(balances, indent=4, sort_keys=True, default=str) # Pretty print JSON
    print balances[0]['available']  # Access each JSON element from direct API call....
    print balances[0]['balance']
    print balances[0]['currency']
    print balances[0]['hold']
    print balances[0]['id']
    print balances[0]['profile_id']


    print "---------------------------------  Python Dictionary Access"
    ''' Much cleaner access to account data in python "dictonaries" '''
    gdax.accounts.updateBalances()   # Call our method to make an API call...
    print gdax.accounts.balance['USD']              # All the USD things!
    print gdax.accounts.balance['USD']['available'] # All the available USD!


    print "--------------------------------- Single Coin Access"
    ''' Shortcut for single coin available balance '''
    coin = gdax.accounts.available("USD")
    print "Variable Type: %s | Value: %s" % (type(coin), coin)

    print "--------------------------------- Normzlizezed Values"
    ''' Shortcut for single coin available balance '''
    print "For USD (str!!!!):"
    print "%s" % tools.normalizeUSD(float(coin))
    print "For Coin (str!!!!):"
    print "%s" % tools.normalizeCOIN(float(coin))

    '''
    # I love writing shortcut methods.  Gramatical programming helps a TON with my ADD

    # method to return the raw status of the order..
    status = gdax.trade.status("mi_tradeid")

    # I shortcut with methods like this:
    if gdax.trade.filled("mi_tradeid") is True:
        print "Win!"
    else
    '''

    print "--------------------------------- Nice Logging"
    log.debug("Logging is Cute!")



def main():
    demo()



if __name__ == "__main__":
    main()
