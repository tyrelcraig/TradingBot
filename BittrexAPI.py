#!/usr/bin/env python3

"""
Bittrex API
https://bittrex.com/home/api
"""

import requests
import time
import hmac
import hashlib
import json

# Bittrex API URL
BASE_URL = "https://bittrex.com/api/v1.1/"
# Total retries on a failed connection.
CONNECT_RETRIES = 10
# Delay between failed connection requests.
CONNECT_WAIT = 5

# Used to input the type of orderbook information required back.
BUY_ORDERBOOK = "buy"
SELL_ORDERBOOK = "sell"
BOTH_ORDERBOOK = "both"


class BittrexApiRequest(object):
	"""
	Used for requesting Bittrex with API Key & API Secret.
	"""
	def __init__(self, secrets, options):
		"""

		"""
		api_key = secrets["bittrex"]["bittrexKey"]
		api_secret = secrets["bittrex"]["bittrexSecret"]
		self.api_key = str(api_key) if api_key is not None else ""
		self.api_secret = str(api_secret) if api_secret is not None else ""
		"""options = options  TBC once I have added in parameters for trading strategies"""

	def api_request_query(self, method, params=dict, headers=None, signed=False) :
		"""
		Constructs and sends a HTTP Request using the Bittrex API. 
		Standard HMAC-SHA512 signing is used. 

		ARGS:
			Args:
			method (str):
				URI resource that references a Bittrex API service.
			params (dict):
				Dictionary that contains name/value parameters (optional).
			headers (dict):
				Dictionary that contains HTTP header key/values (optional).
			signed (bool):
				Authenticate using a signed header (optional).
		RETURNS:
			(dict) JSON Response from Bittrex.
		"""

		# Add parameters required for signed requests.
		if signed == True:
			params['apikey'] = self.api_key
			params['nonce'] = str(int(time.time()))

		# Create query string from parameter items.
		query_str = []
		for name, value in params.iteritems():
			query_str.append(name + '=' + str(value))

		# Format the URL with the query string.
		uri = [BittrexApiRequest.BASE_URL + method]
		uri.append('?' + '&'.join(query_str))
		request_url = ''.join(uri)

		# Create the signed HTTP header.
		if headers is None:
			headers = {}

		if signed == True:
			headers['apisign'] = BittrexApiRequest._sign(self.api_secret, request_url)

		# Send the API request.
		for i in range(BittrexApiRequest.CONNECT_RETRIES):
			try:
				req = requests.get(request_url, headers=headers)
			except requests.exceptions.ConnectionError:
				time.sleep(BittrexApiRequest.CONNECT_WAIT)
			else:
				break

		res = req.json()

		if res == None or not res['result']:
			print >> sys.stderr, 'Script Failure: Connection timeout'
			sys.exit(1)

		if res['success'] == False:
			print >> sys.stderr, "Bittrex response: %s" % res['message']
			sys.exit(1)

		# Return list of dicts.
		return res['result']


	@staticmethod
	def _sign(secret, message):
		"""
		Return signed message using the HMAC algorithm.
		Args:
			secret (str):
				Bittrex issued API secret.
			message (str):
				Message to convert.
		Returns:
			str
		.. seealso:: https://www.bittrex.com/Manage#sectionApi
		"""
		return hmac.new(secret, message, hashlib.sha512).hexdigest()
	"""
	All public Bittrex APIs
	"""
	def public_markets(self):
		"""
		Used to get the open and available trading markets at Bittrex along with other meta data.

		Parameters: None
		Returns:
			(dict) Available market information in JSON 
		"""
		return self.api_request_query('public/getmarkets')

	def public_currencies(self):
		"""
		Used to get all supported currencies at Bittrex along with other meta data.

		Paramaters: None
		Returns:
			(dict) Supported currencies and metadata in JSON.
		"""
		return self.api_request_query('public/getcurrencies')

	def public_ticker(self, market):
		"""
		Used to get the current tick values for a market.

		Parameters:
			market (str): String literal (ex. BTC-LTC).
		Returns:
			(dict) Current values for given market in JSON
		"""
		return self.api_request_query('public/getticker', {'market': market})

	def public_market_summaries(self):
		"""
		Used to get the last 24 hour summary of all active exchanges.
		Parameters: None
		Returns:
			(dict) Summaries of all active exchanges in JSON
		"""
		return self.api_request_query('public/getmarketsummaries')

	def public__market_summary(self, market):
		"""
		Used to get the last 24 hour summary of all active exchanges.
		Parameters:
			market (str): String literal (ex. BTC-LTC).
		Returns:
			(dict) Summary of a given exchange in JSON
		"""
		return self.api_request_query('public/getmarketsummary', {'market': market})

	def public_market_history(self, market):
		"""
		Used to get the latest trades that have occured for a specific market.
		Parameters:
			market (str): String literal (ex. BTC-LTC).
		Returns:
			(dict) Market history of a given exchange in JSON
		"""
		return self.api_request_query('public/getmarkethistory', {'market': market})

	def public_orderbook(self, market, book_type):
		"""
		Get the orderbook for a given market.
		Parameters:
			market (str): String literal (ex. BTC-LTC).
			book_type (str): "buy", "sell" or "both" to identify the type of orderbook.
		Returns:
			(dict) Orderbook of market in JSON
		"""
		return self.api_request_query('public/getorderbook', {'market': market, 'type': book_type})
	"""
	All market Bittrex APIs
	"""
	def market_buy_limit(self, market, quantity, rate):
		"""
		Send a buy order in a specific market.
		Parameters:
			market (str):
				String literal (ex. BTC-LTC).
			quantity (float):
				The amount to purchase.
			rate (float):
				Rate at which to place the order.
		Returns:
			(dict) Order uuid
		"""
		return self.api_request_query('market/buylimit', {'market': market, 'quantity': quantity, 'rate': rate}, signed=True)

	def market_sell_limit(self, market, quantity, rate):
		"""
		Send a sell order in a specific market.
		Parameters:
			market (str):
				String literal (ex. BTC-LTC). If omitted, return all markets.
			quantity (float):
				The amount to sell.
			rate: (float)
				Rate at which to place the order.
		Returns:
			(dict) Order uuid
		"""
		return self.api_request_query('market/selllimit', {'market': market, 'quantity': quantity, 'rate': rate}, signed=True)

	def market_cancel(self, uuid):
		"""
		Send a cancel a buy or sell order.
		Parameters:
			uuid (str):
				UUID of buy or sell order.
		Returns: (dict) null
		"""
		return self.api_request_query('market/cancel', {'uuid': uuid}, signed=True)

	def market_open_orders(self, market):
		"""
		Get all orders that you currently have opened.
		Parameters:
			market (str):
				String literal (ex. BTC-LTC). If omitted, return all markets.
		Returns:
			(dict) Open orders info in JSON
		"""
		return self.api_request_query('market/getopenorders', {'market': market}, signed=True)
	"""
	All account Bittrex APIs
	"""
	def account_balances(self):
		"""
		Get all balances from your account.
		Parameters: None
		Returns:
			(dict) Balances info in JSON
		"""
		return self.api_request_query('account/getbalances', signed=True)

	def account_balance(self, currency):
		"""
		Get the balance from your account for a specific currency.
		Parameters:
			currency (float):
				String literal (ex. BTC). If omitted, return all currency.
		Returns:
			(dict) Balance info in JSON
		"""
		return self.api_request_query('account/getbalance', {'currency': currency}, signed=True)

	def account_deposit_address(self, currency):
		"""
		Get existing, or generate new address for a specific currency.
		Parameters:
			currency (float):
				String literal (ex. BTC). If omitted, return all currency.
		Returns:
			(dict) Address info in JSON
		"""
		return self.api_request_query('account/getdepositaddress', {'currency': currency}, signed=True)

	def account_withdraw(self, currency, quantity, address, paymentid):
		"""
		Send request to withdraw funds from your account.
		Parameters:
			currency (float):
				String literal (ex. BTC). If omitted, return all currency.
			quantity (str):
				The amount to withdrawl.
			address (str):
				The address where to send the funds.
			paymentid (str):
				CryptoNotes/BitShareX/Nxt field (memo/paymentid optional).
		Returns:
			(dict) withdrawal uuid
		"""
		return self.api_request_query('account/withdraw', {'currency': currency, 'quantity': quantity, 'address': address, 'paymentid': paymentid}, signed=True)

	def account_order(self, uuid):
		"""
		Get a single order by uuid.
		Parameters:
			uuid (str):
				UUID of buy or sell order.
		Return:
			(dict) 
		"""
		return self.api_request_query('account/getorder', {'uuid': uuid}, signed=True)

	def account_order_history(self, market):
		"""
		Get order history.
		Parameters:
			market (str):
				String literal (ex. BTC-LTC). If omitted, return all markets.
		Returns:
			(dict) order history in JSON
		"""
		return self.api_request_query('account/getorderhistory', {'market': market}, signed=True)

	def account_deposit_history(self, currency):
		"""
		Get deposit history.
		Parameters:
			currency (float):
				String literal (ex. BTC). If omitted, return all currency.
		Returns:
			(dict)
		"""
		return self.api_request_query('account/getdeposithistory', {'currency': currency}, signed=True)

	def account_withdrawal_history(self, currency):
		"""
		Get withdrawal history.
		Parameters:
			currency (float):
				String literal (ex. BTC). If omitted, return all currency.
		Returns:
			(dict)
		"""
		return self.api_request_query('account/getwithdrawalhistory', {'currency': currency}, signed=True)
