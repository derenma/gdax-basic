''' Our main gdax sdk and our sdk wrapper'''
import gdax
import sys

try:
    authClient = gdax.AuthenticatedClient(apiKey, apiSecret, passphrase)
except Exception as e:
    print("Failed auth.")
    exit()

''' Sell '''
result = authClient.sell(price=sellPrice, size=qty, product_id=market, post_only=True)
if 'id' not in result:
    print("Sell Failed for %s at %s with error %s" % (sellPrice, qty, json.dumps(result, indent=4)))
else:
    print('Placed Sell: Price: {0} | Quantity: {1} | Market {2}').format(sellPrice, qty, market)

''' Buy '''
result = authClient.buy(price=buyPrice, size=qty, product_id=self.market, post_only=True)
if 'id' not in result:
    print("Buy Failed for %s at %s with error %s" % (buyPrice, qty, json.dumps(result, indent=4)))
else:
    print('Placed Buy: Price: {0} | Quantity: {1} | Market {2}').format(buyPrice, qty, market)
