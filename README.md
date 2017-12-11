# Demo Stuff

## Obligitory cat gif
![](https://imgur.com/vp24Vr4.gif)

## Tools and Logging
```
tools = Tools()
log = tools.log  # We are referencing a class object! (or class variable, whatever makes you happy)
```

## Auth and Client Init
```
gdax = Client(log, tools, passphrase="", apiKey="", apiSecret="")
```


## Class and subclass access example
```
gdax.trade.buy(..)
gdax.trade.sell(..)
gdax.table.update("BTC-ETH")
gdax.accounts.get()
# Etc, etc...
```

## Currency and floating points

### Normalizing Floats
```
normalizedCoin = tools.normalizeCOIN("0.0000000000000000") # Returns "0.00000000"
```
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

### Basic trading and validation
#### Sell Example Basic
```
gdax.trade.sell(buyprice, quantity, "ETH-BTC")
```
#### Sell with logic
```
result = gdax.trade.sell(sellprice, quantity, "ETH-BTC")
if result is False:
    print "OMG"
    exit()
else:
    print result
```

### Class Data
```
# update our class variables instead of making direct API calls
gdax.table.update("ETH-BTC")
for order in gdax.table.orders():
    print order
```

### The dirty Raw
Direct access to account information.
GDAX JSON is dumb; Keys are not based off of currency type:
```
    [
    {
        "available": "0.00000362110355",
        "balance": "0.0000036211035500",
        "currency": "USD",
        "hold": "0.0000000000000000",
        "id": "asdfsadfsadf",
        "profile_id": "sadfsadfsadf"
    }, ....
```
#### Raw JSON stuffs.
```
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
```

#### Better than raw
```
print "---------------------------------  Python Dictionary Access"
''' Much cleaner access to account data in python "dictonaries" '''
gdax.accounts.updateBalances()   # Call our method to make an API call...
print "Full dictionary:"
print gdax.accounts.balance['USD']              # All the USD things!
print "Single Value:"
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
```

#### Simple Complexity
```
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
```

# You can't tell me what to do.
Want to call back to the API directly?  Init your client, then leverage Client().authClient for direct API calls.
Read more here: https://docs.gdax.com/
```
gdax = Client(log, tools, passphrase="", apiKey="", apiSecret="")
orderInfo = gdax.authClient.get_order("mi_tradeId")
```

# Class Structure
```
class Tools(object):
    def __init__(self):
    def logInit(self):
    def normalizeUSD(self, USD):
    def normalizeCOIN(self, coin):

class Client(object):
    def __init__(self, log, tools, passphrase=None, apiKey=None, apiSecret=None):
        self.authClient = ''
        self.log = log
        self.tools = tools
        self.passphrase = passphrase
        self.apiKey = apiKey
        self.apiSecret = apiSecret
    def getOrders(self):
    def getOrder(self, tradeId):
    def getFills(self):
    def getProductOrderBook(self, market, kwargs):

    class Trade(object):
        def __init__(self, outer):
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
```

# Oh yeah.  Because Crypto.
![](https://media.giphy.com/media/7EY1y7VE3kgqA/giphy.gif)
