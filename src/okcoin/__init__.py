import requests
import json
import getpass
import datetime
import hmac
import base64
import pandas as pd
import numpy as np
import configparser
import plotly.graph_objects as go

from okcoin.DataObjects import  _Candlestick
from okcoin.DataObjects import _Resp
from okcoin.DataObjects import _AccountInfo

# documentation following numpy: https://numpydoc.readthedocs.io/en/latest/example.html#example

CONTENT_TYPE = 'Content-Type'
OK_ACCESS_KEY = 'OK-ACCESS-KEY'
OK_ACCESS_SIGN = 'OK-ACCESS-SIGN'
OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE'
APPLICATION_JSON = 'application/json'
GET = 'GET'
POST = 'POST'
REST_API_URL = "https://www.okcoin.com"


class _Signature:
    """
    The Signature class is a private class that is used to create a signature to that enables users to
    interface with the okcoin API. It takes as inputs a config file that contains your
    API_KEY, SECRET_KEY, and an optional PASS_PHRASE. If the PASS_PHRASE is not specified, you
    will be prompted for it upon instantiating the account object.


    Parameters
    ----------
    config_file : A file containing the api_key, secret_key, and pass_phrase

    pass_phrase : If a pass_phrase is not specified in the config_file, it can be entered as a separate parameter
    or you will be prompted to enter it through your Python IDE.

    Attributes
    ----------
    """

    def __init__(self,
                 config_file=r'auth.config',
                 pass_phrase=None):

        config = configparser.ConfigParser()
        config.read(config_file)

        self.api_key = config['DEFAULT']['api_key']  # api_key
        self.secret_key = config['DEFAULT']['secret_key']  # secret_key
        self.REST_API_URL = REST_API_URL
        print("GetPass")
        print(config['DEFAULT']['pass_phrase'])
        if pass_phrase == None and config['DEFAULT']['pass_phrase'] == "":
            # print("HERE1")
            p = getpass.getpass(prompt='Enter your okcoin API pass phrase:')
            self.pass_phrase = p
        else:
            # print("HERE2")
            self.pass_phrase = config['DEFAULT']['pass_phrase']  # pass_phrase
        # self.query_result = query_result()

    def __get_timestamp(self):
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
        print(timestamp)
        return timestamp

    # signature
    def __get_signature(self, t, method, request_path, body=None):
        if str(body) == '{}' or str(body) == 'None' or body == None:
            body = ''
        message = str(t) + str.upper(method) + request_path + str(body)
        mac = hmac.new(bytes(self.secret_key, encoding='utf8'), bytes(message, encoding='utf-8'),
                       digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)

    # set request header
    def __get_header(self, sig, t):
        header = dict()
        header[CONTENT_TYPE] = APPLICATION_JSON
        header[OK_ACCESS_KEY] = self.api_key
        header[OK_ACCESS_SIGN] = sig
        header[OK_ACCESS_TIMESTAMP] = t
        header[OK_ACCESS_PASSPHRASE] = self.pass_phrase
        return header

    def __parse_params_to_str(self, params):
        url = '?'
        for key, value in params.items():
            url = url + str(key) + '=' + str(value) + '&'

        return url[0:-1]

    def query(self, type, request_path, body=''):
        #print(request_path)
        #print(type)
        #print(body)
        if type == "POST":
            body = json.dumps(body)
            print(body)
        else:
            if body != '':
                body = self.__parse_params_to_str(body)

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
        # self.get_timestamp()
        print(body)
        signature = self.__get_signature(timestamp, type, request_path, body)
        #signature = self.__get_signature(timestamp, type, request_path, body)
        #signature = self.__get_signature(timestamp, type, request_path, '')

        header = self.__get_header(signature, timestamp)
        # do request
        if type == 'GET':
            response = requests.get(self.REST_API_URL + request_path + body,
                                headers=header)
        else:
            print(self.REST_API_URL + request_path)
            response = requests.post(self.REST_API_URL + request_path, data=body,
                                    headers=header)

#data=body

        return response

class Account(_Signature):
    """
    The Account class is used to interface with you okcoin account. If contains functions that
    return your account value, the assets in contains, and its history. The Account class
    inherits from the Signature class, which takes as inputs a config file that contains your
    API_KEY, SECRET_KEY, and an optional PASS_PHRASE. If the PASS_PHRASE is not specified, you
    will be prompted for it upon instantiating the account object.


    Parameters
    ----------
    config_file : A file containing the api_key, secret_key, and pass_phrase

    pass_phrase : If a pass_phrase is not specified in the config_file, it can be entered as a separate parameter
    or you will be prompted to enter it through your Python IDE.

    Attributes
    ----------

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.

    >>> from okcoin import Account
    >>> acc = Account(config_file='auth.conf')
    <okcoin.Account object at 0x00000291A320A288>
    """

    def get_account_type(self):
        r"""Returns a dictionary of the different acount types and the
        numerical code that corresponds to them in okcoin.

        Returns
        -------
        account_tpye : dict
            A dictionary of account types (i.e. funding, trading, spot).

        Examples
        --------
        >>> account_type = acc.get_account_type()
        >>> print(account_type)
        {'spot': 1, 'margin': 5, 'funding': 6}
        """
        # In Account API
        account_type = {
            'spot': 1,
            'margin': 5,
            'funding': 6,
			'trading': 18,
        }
        #return pd.DataFrame(account_type, index=[0])
        return account_type

    def get_withdrawal_status(self):
        r"""Returns a dictionary of the withdrawal status and the
        numerical code that corresponds to them in okcoin.

        Returns
        -------
        withdrawal_status : dict
            A dictionary of withdrawal status (i.e. cancelled, failed, pending, etc.).

        Examples
        --------
        >>> withdrawal_status = acc.get_withdrwal_status()
        >>> print(withdrawal_status)
        {'Pending cancel': -3, 'Cancelled': -2, 'Failed': -1, 'Pending': 0, 'Sending': 1, 'Sent': 2,
        'Awaiting email verification': 3, 'Awaiting manual verification': 4,
        'Awaiting identity verification': 5}
        """
        # In Account API
        withdrawal_status = {
            'Pending cancel': -3,
            'Cancelled': -2,
            'Failed': -1,
            'Pending': 0,
            'Sending': 1,
            'Sent': 2,
            'Awaiting email verification': 3,
            'Awaiting manual verification': 4,
            'Awaiting identity verification': 5
        }
        #return pd.DataFrame(withdrawal_status, index=[0])
        return withdrawal_status

    def get_balance(self, currency=''):
        r"""Retrieves information on the balances of all of the assets that are
        available or on hold.

        Returns
        -------
        account_info : _AccountInfo
            A custom data structure that enables you to view you wallet as a dataframe,
            json, or plotly chart.

        Examples
        --------
        >>> acc = Account('auth.conf')
        >>> wallet = acc.get_wallet()
        >>> print(wallet.r)
        <Response [200]>
        >>> print(wallet.json)
        [{'balance': '0.00071305', 'available': '0.00071305', 'currency': 'BTC', 'hold': '0.00000000'}, {'balance': '793.99043577', 'available': '793.99043577', 'currency': 'STX', 'hold': '0.00000000'}]
        >>> print(wallet.df)
                balance     available currency        hold
        0    0.00071305    0.00071305      BTC  0.00000000
        1  793.99043577  793.99043577      STX  0.00000000
        """
        if currency:
            request_path = '/api/v5/account/balance?ccy='+currency
        else:
            request_path = '/api/v5/account/balances'
		#body = ''

        #resp = _AccountInfo(self.query(GET, request_path))

        #fig = go.Figure([go.Bar(x=resp.df['currency'].tolist(), y=resp.df['balance'].tolist())])
        #fig.update_layout(
        #    title='Funding Account Assets',
        #    yaxis_title='Asset',
        #    xaxis_title='Quantity')

        return _AccountInfo(self.query(GET, request_path)) #, fig

    def get_asset_valuation(self, currency=''):
        r"""Get the valuation of the total assets of the account in btc or fiat currency.

        Parameters
        ----------
        currency : 	The valuation according to a certain fiat currency.  The currency
            can only be one of the following: BTC, USD, CNY, JPY, KRW, RUB.
            The default unit is BTC.

        Returns
        -------
        account_info : _Resp
            A custom data structure that allows you to view the request status,
            the request response as json, and the request response as a dataframe.

        Examples
        --------
        >>> asset_val = acc.get_asset_valuation('USD')
        >>> print(asset_val.df)
        account_type                               0
        balance                               523.51
        valuation_currency                       USD
        timestamp           2021-05-13T02:21:30.061Z
        """
        if currency:
            request_path = '/api/v5/asset/asset-valuation?ccy='+currency
        else:
            request_path = '/api/v5/asset/asset-valuation'

        return _Resp(self.query(GET, request_path))

    # Sub account erroring
    def get_sub_account(self, account_name=''):
        r""" Obtains the fund balance information in each sub account in the users okcoint
        account.

        Parameters
        ----------
        account_name : 	The name of the sub-account.

        Returns
        -------
        account_info : _Resp
            A custom data structure that allows you to view the request status,
            the request response as json, and the request response as a dataframe.

        Examples
        --------
        >>> sub_account = acc.get_sub_account()
        >>> print(sub_account.json)
        {
            "data": {
                "sub_account": "Test",
                "asset_valuation": 0.00003463,
                "account_type:futures": [
                    {
                        "balance": 0.00000245,
                        "max_withdraw": 0.00000245,
                        "currency": "BTC",
                        "underlying": "BTC_USD",
                        "equity": 0.00000245
                    },
                    {
                        "balance": 1.053473,
                        "max_withdraw": 1.053473,
                        "currency": "XRP",
                        "underlying": "XRP_USD",
                        "equity": 1.053473
                    }
                ],
                "account_type:spot": [
                    {
                        "balance": 0.000312544038152,
                        "max_withdraw": 0.000312544038152,
                        "available": 0.000312544038152,
                        "currency": "USDT",
                        "hold": 0
                    }
                ]
            }
        }
        """
        if account_name:
            request_path = '/api/v5/users/subaccount/list'+account_name

        else:
            request_path = '/api/v5/users/subaccount/list'

        return _Resp(self.query(GET, request_path))

    def get_currency(self, token='BTC'):
        r""" Retrieves information for a single token in your account,
        including the remaining balance, and the amount available or on hold.

        Parameters
        ----------
        token : str
            The token you are querying.

        Returns
        -------
        token_info : _Resp
            A custom data structure that allows you to view the request status,
            the request response as json, and the request response as a dataframe.

        Examples
        --------
        >>> curr = acc.get_currency(token='BTC')
        >>> print(curr.df)
              balance   available currency        hold
        0  0.00076409  0.00076409      BTC  0.00000000
        """
        request_path = '/api/account/v5/wallet/' + token
        return _Resp(self.query(GET, request_path))

    ## Withdraw or Trade Permission
    def get_funds_transfer(self, ccy='BTC', amt='', origin='', destination=''):
        body = {'ccy': ccy,
                  'amt': amt,
                  'from': origin,
                  'to': destination}
        request_path = '/api/v5/asset/transfer'
        return _Resp(self.query(POST, request_path, body=body))

    def get_funds_transfer_state(self, transId='3693307', clientId=''):
        str(transId)
        print(transId,clientId)
        if transId:
            request_path = '/api/v5/asset/transfer-state?transId='+transId
        if clientId:
            request_path = '/api/v5/asset/transfer-state?clientId='+clientId
        else:
            request_path = '/api/v5/asset/transfer-state?transId=3693314'	
        print(request_path)
        return _Resp(self.query(GET, request_path))

    ## Withdraw or Trade Permission
    def withdraw(self, currency='', amount='', to_address='', fee=''):
        body = {'ccy': currency,
                  'amt': amount,
                  'destination': '4',
                  'toAddr': to_address,
                  'fee': fee}
        request_path = '/api/v5/asset/withdrawal'
        return _Resp(self.query(POST, request_path, body=body))

    def get_withdrawal_history(self, currency=''):
        r""" Retrieves the 100 most recent withdrawal records.

        Parameters
        ----------
        currency : 	str
            The currency that was withdrawn.

        Returns
        -------
        withdrawal_hist : _Resp
            A custom data structure that allows you to view the request status,
            the request response as json, and the request response as a dataframe.

        Examples
        --------
        >>> withdraw_hist = acc.get_withdrawal_history()
        >>> withdraw_hist.df
        Empty DataFrame
        Columns: []
        Index: []
        """
        if currency:
            request_path = '/api/v5/asset/withdrawal-history?ccy=' + currency
        else:
            request_path = '/api/v5/asset/withdrawal-history'
        return _Resp(self.query(GET, request_path))

    def get_ledger(self):
        r""" Retrieves the value of your account for the past month.


        Returns
        -------
        bills : _Resp
            A custom data structure that allows you to view the request status,
            the request response as json, and the request response as a dataframe.

        Examples
        --------
        >>> ledger = acc.get_ledger()
        >>> ledger.df
                   amount       balance  ...            typename                 timestamp
        0      0.00000611    0.00076409  ...                      2021-05-16T05:41:27.000Z
        1      0.00000793    0.00075798  ...                      2021-05-15T04:41:24.000Z
        2      0.00001004    0.00075005  ...                      2021-05-14T04:41:25.000Z
        3      0.00001777    0.00074001  ...                      2021-05-13T04:41:27.000Z
        [4 rows x 7 columns]
        """
        request_path = '/api/account/v5/ledger'
        ledger_resp = _Resp(self.query(GET, request_path))
        ledger_resp.df.amount = ledger_resp.df.amount.astype('float64')
        ledger_resp.df.balance = ledger_resp.df.balance.astype('float64')
        ledger_resp.df.fee = ledger_resp.df.fee.astype('float64')
        ledger_resp.df.ledger_id = ledger_resp.df.ledger_id.astype('int64')
        ledger_resp.df.timestamp = ledger_resp.df.timestamp.astype('datetime64')
        return ledger_resp

    def get_deposit_address(self, currency='BTC'):
        r""" Retrieves the deposit addresses of currencies, including previously used addresses.

        Parameters
        ----------
        currency : 	str
            The currency deposited.

        Returns
        -------
        account_info : _Resp
            A custom data structure that allows you to view the request status,
            the request response as json, and the request response as a dataframe.

        Examples
        --------
        >>> dep_addr = acc.get_deposit_address()
        >>> dep_addr.json
        {'code': 404,
         'data': {},
         'detailMsg': '',
         'error_code': '404',
         'error_message': 'Not Found',
         'msg': 'Not Found'}
        """

        request_path = '/api/v5/asset/deposit-address?ccy=' + currency
        print(request_path)
        return _Resp(self.query(GET, request_path))


    def get_total_deposit_value(self, start_date=None, end_date=None, currency='USD'):
        r""" Retrieves amount that has been deposited between two date.

        Parameters
        ----------
        start_date : 	str
            Start date of query in YYYY-MM-DD.

        end_date : str
            End date of query in YYYY-MM-DD

        currency : str
            Currency of deposit. Set to USD by default

        Returns
        -------
        value : float
            Value representing the amount deposited during that date range.

        Examples
        --------
        >>> ddep_value = acc.get_total_deposit_value('2021-04-12','2021-06-12')
        >>> print(dep_value)
            400.00
        """
        if start_date == None:
            start_date = '2000-01-01'
        if end_date == None:
            end_date = datetime.datetime.today().strftime('%Y-%m-%d')

        dep = self.get_deposit_history(currency)
        df = dep.df
        df['amount'] = pd.to_numeric(df['amount'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])

        mask = (df['updated_at'] > start_date) & (df['updated_at'] <= end_date)
        df = df.loc[mask]
        val = np.sum(df['amount'].to_list())

        return val


    def get_deposit_history(self, currency='USD'):
        r""" Retrieves the deposit history of all currencies,
        up to 100 recent records(Within one year).

        Parameters
        ----------
        currency : 	str
            The currency deposited.

        Returns
        -------
        account_info : _Resp
            A custom data structure that allows you to view the request status,
            the request response as json, and the request response as a dataframe.

        Examples
        --------
        >>> dep_hist = acc.get_deposit_history()
        >>> dep_hist.df
                 amount                updated_at  ...                 timestamp status
        0  200.00000000  2021-05-11T17:18:21.000Z  ...  2021-05-10T13:09:39.000Z      5
        1  100.00000000  2021-05-03T17:18:41.000Z  ...  2021-04-30T17:06:11.000Z      5
        2  100.00000000  2021-04-24T03:13:52.000Z  ...  2021-04-23T13:34:20.000Z      5
        3  100.00000000  2021-04-12T15:40:51.000Z  ...  2021-04-09T12:22:16.000Z      5
        [4 rows x 9 columns]
        """
        request_path = '/api/v5/asset/deposit-history?ccy='+currency

        return _Resp(self.query(GET, request_path))

    def get_currencies(self):
        r""" This retrieves a list of all currencies.

        Returns
        -------
        currency_info : _Resp
            An object containing the currencies currently supported by okcoin.

        Examples
        --------
        >>> currencies = acc.get_currencies()
        >>> print(currencies.df)
        can_internal                     name  ... can_deposit min_withdrawal
        0             0                US Dollar  ...           1
        1             0                     Euro  ...           1
        """
        request_path = '/api/v5/asset/currencies'
        return _Resp(self.query(GET, request_path))


    # This is buggy. You need to specify a currency to get anything back
    def get_withdrawal_fees(self, currency='BTC'):
        r"""

        Parameters
        ----------
        account_name : 	str
            The name of the sub-account.

        Returns
        -------
        fee : _Resp
            An object contianing the min and max fees for the withdrawal of the
            specified currency.

        Examples
        --------
        >>> withdraw_fee = acc.get_withdrawal_fees('STX')
        >>> print(withdraw_fee.df)
        min_fee     currency     max_fee
        0  1.00000000      STX  2.00000000
        """
        request_path = '/api/v5/asset/withdrawal/fee'
        if currency:
            body = {'currency':currency}
        else:
            body=''
        #body = json.dumps(p)
        #print(body)
        return _Resp(self.query(GET, request_path, body=body))

    def get_balance_from_ledger(self, df, currency='BTC'):
        r""" Returns a dataframe and Plotly chart that show the balance
        of the funding account.

        Parameters
        ----------
        df : 	dataframe
            The dataframe generated by the

        currency : str
            The currency that you are querying.

        Returns
        -------
        balance : _Resp
            A n object that...

        fig : Plotly chart
            A plotly chart of the balance of the funding account.

        Examples
        --------
        >>> ledger = account.get_ledger()
        >>> btc_balance = account.get_balance_from_ledger(ledger.df,'BTC')
        >>> print(btc_balance[0])
        >>> btc_balance[1].write_html('test.html', auto_open=True)
        """
        cur = df[df['currency']==currency]
        cur_balance = cur.groupby('timestamp')['balance'].max()
        balance = cur_balance.to_frame()
        balance.reset_index(inplace=True)

        fig = go.Figure(data=go.Scatter(
            x=balance.timestamp.tolist(),
            y=balance.balance.tolist(),
            mode='markers'
        ))

        fig.update_layout(
            title=currency,
            xaxis_title="Date",
            yaxis_title="Value in " + currency)

        return balance, fig
		
		
    def lightning_deposit(self, amount):
        request_path = '/api/v5/asset/deposit-lightning?ccy=BTC&amt='+str(amount)
        return _Resp(self.query(GET, request_path))

## Spot Trading Account Info
class Spot(_Signature):
    """
    The Spot class is used to interface with you okcoin spot trading account. If contains functions that
    return your account value and your trading history. It also contains functions that return the current
    crypto market conditions, such as trading pairs, asset prices, ad asset history. The Spot class
    inherits from the Signature class, which takes as inputs a config file that contains your
    API_KEY, SECRET_KEY, and an optional PASS_PHRASE. If the PASS_PHRASE is not specified, you
    will be prompted for it upon instantiating the account object.


    Parameters
    ----------
    config_file : A file containing the api_key, secret_key, and pass_phrase

    pass_phrase : If a pass_phrase is not specified in the config_file, it can be entered as a separate parameter
    or you will be prompted to enter it through your Python IDE.

    Attributes
    ----------

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.

    >>> from okcoin import Spot
    >>> spot = Spot(config_file='auth.conf')

    """

    def get_account_chart(self, df):
        fig = go.Figure([go.Bar(x=df['currency'].tolist(), y=df['balance'].tolist())])
        fig.show()

    def get_order_status(self):
        # In Spot API
        r""" Returns the status of an order and the numeric value that corresponds to it
        in the Okcoin API.

        Returns
        -------
        order_status : A dictionary object of order status values.

        Examples
        --------
        >>> status = spot.get_order_status()
        """
        order_status = {
            'Failed': -2,
            'Canceled': -1,
            'Open': 0,
            'Partially Filled': 1,
            'Fully Filled': 2,
            'Submitting': 3,
            'Cancelling': 4,
            'Incomplete': 6,
            'Complete': 7
        }
        #return pd.DataFrame(order_status, index=[0])
        return order_status

    def get_accounts(self, currency='BTC'):
        r""" Returns a list of assets, (with non-zero balance),
        remaining balance, and amount available in the spot trading account.

        Parameters
        ----------
        currency : 	str
            Optional parameter specifying which asset you want to return

        Returns
        -------
        resp : _Resp
            A query response object that contains the query result as a dictionary or dataframe

        fig : figure
            A Plotly figure displaying the valuation of the assets in the account

        Examples
        --------
        >>> accounts = spot.get_accounts()
        >>> accounts[1].write_html('temp.html', auto_open=True)
        """
        request_path = '/api/v5/account/balance'
        if currency:
            request_path + "?ccy=" + currency

        resp = _Resp(self.query(GET, request_path))



        return resp

    def get_bills(self, currency=''):
        r""" Returns the spot account bills dating back the past 3 months.
        Pagination is supported and the response is sorted
        with most recent first in reverse chronological order.

        Parameters
        ----------
        currency : 	str
            Currency being queried

        Returns
        -------
        balance : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe

        Examples
        --------
        >>> currency = spot.get_ledger('USD')
        >>> currency.df
        """
        request_path = '/api/v5/account/bills'
        if currency:
            request_path + '?ccy=' + currency
        return _Resp(self.query(GET, request_path))
		
    def get_bills_archive(self, currency=''):
        r""" Returns the spot account bills dating back the past 3 months.
        Pagination is supported and the response is sorted
        with most recent first in reverse chronological order.

        Parameters
        ----------
        currency : 	str
            Currency being queried

        Returns
        -------
        balance : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe

        Examples
        --------
        >>> currency = spot.get_ledger('USD')
        >>> currency.df
        """
        request_path = '/api/v5/account/bills-archive'
        if currency:
            request_path + '?ccy=' + currency
        return _Resp(self.query(GET, request_path))

    def place_order(self, side='', trading_pair='', limit_or_market='', size='', price='', client_id=''):
        r""" Returns This the list of your orders from
        the most recent 3 months. This request supports paging
        and is stored according to the order time in chronological
        order from latest to earliest.

        Parameters
        ----------
        side : str
            'buy' or 'sell'

        trading_pair : str
            The trading pair that was ordered

        limit_or_market : str
            'limit' or 'market' order

        size : float
            Quantity to be bought or sold.

        price : float
            The price you want to purchase the asset at

        amount_to_spend : float
            Amount to spend. Required for market buys.

        client_id : str
            A user defined ID that you can give your order


        Returns
        -------
        orders : _Resp
            A query response object that contains the query result as a dictionary and as a dataframe

        Examples
        --------
        >>> order = spot.place_order('buy', 'MIA-USD','0','limit',1000, .04)
        >>> order.df
        """
        request_path = '/api/v5/trade/order'#?instrument_id='+trading_pair+'&state='+str(state)
        # Using the "body" doesn't work

        if limit_or_market == 'market':
            body = {'instId': trading_pair,
                 'tdMode':"cash",
				 'clOrdId': client_id,
                 'side': side,
                 'ordType': limit_or_market,
                 'type': 'market',
                 'sz':str(size)}
        else:
            body = {'instId': trading_pair,
                 'tdMode':"cash",
				 'clOrdId': client_id,
                 'side': side,
                 'ordType': limit_or_market,
                 'type': 'limit',
                 'sz':str(size),
                 'px':str(price)}

        return _Resp(self.query(POST, request_path, body=body))

    def cancel_order(self, order_id, trading_pair):
        r""" Cancels an existing trade.

                Parameters
                ----------
                order_id : str
                    The ID for the order you would like to cancel.

                trading_pair : str
                    The trading pair that was ordered.


                Returns
                -------
                orders : _Resp
                    A query response object that contains the query result as a dictionary and as a dataframe

                Examples
                --------
                >>> order = spot.cancel_order('5468800', 'MIA-USD')
                >>> order.df
                """
        request_path = '/api/spot/v5/cancel_orders'#?instrument_id='+trading_pair+'&state='+str(state)
        body = {'instrument_id': trading_pair.lower()}

        return _Resp(self.query(POST, request_path + '/' + str(order_id), body=body))

    def get_order_list(self, trading_pair='STX-USD', state=0):
        r""" Returns This the list of your orders from
        the most recent 3 months. This request supports paging
        and is stored according to the order time in chronological
        order from latest to earliest.

        Parameters
        ----------
        trading_pair : str
            The trading pair that was ordered

        state : int
            The state of the order, represented as an integer.


        Returns
        -------
        orders : _Resp
            A query response object that contains the query result as a dictionary and as a dataframe

        Examples
        --------
        >>> orders = spot.get_order_list('STX-USD')
        >>> orders.df
        """
        request_path = '/api/spot/v5/orders'#?instrument_id='+trading_pair+'&state='+str(state)
        body = {'instrument_id': trading_pair,
                'state': str(state)}
        return _Resp(self.query(GET, request_path, body=body))

    def get_orders_pending(self, trading_pair='BTC-USD'):
        r""" Returns the list of your current open orders.
        Pagination is supported and the response
        is sorted with most recent first in reverse chronological order.

        Parameters
        ----------
        trading_pair : str
            The trading pair that was ordered.


        Returns
        -------
        orders : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe


        Examples
        --------
        >>> pending = spot.get_orders_pending('STX-USD')
        >>> pending.df
        """
        request_path = '/api/spot/v5/orders_pending'
        body = {'instrument_id':trading_pair.lower()}
        return _Resp(self.query(GET, request_path, body=body))

    def get_order_details(self, order_id, trading_pair='BTC-USDT'):
        r""" Returns order details by order ID.Can get order information for nearly 3 months。
        Unfilled orders will be kept in record for only
        two hours after it is canceled.

        Parameters
        ----------
        order_id : int
            The specific order ID that you want to query

        trading_pair : str
            The trading pair that was ordered


        Returns
        -------
        orders : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe


        Examples
        --------
        >>> details = spot.get_order_details(order_id, 'BTC-USD')
        >>> details.df
        """
        request_path = '/api/spot/v5/orders/' + str(order_id)
        body = {'instrument_id': trading_pair.lower()}
        return _Resp(self.query(GET, request_path, body=body))

    def get_trade_fee(self,instType='SPOT'):
        r""" Returns the transaction fee rate corresponding to
        your current account transaction level. The sub-account
        rate under the parent account
        is the same as the parent account.
        Update every day at 0am

        Returns
        -------
        fee : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe


        Examples
        --------
        >>> fees = spot.get_trade_fee()
        >>> fees.json
        {'category': '1', 'maker': '0.001', 'taker': '0.002', 'timestamp': '2021-06-11T02:41:44.149Z'}
        """
        request_path = '/api/v5/account/trade-fee?instType='+instType
        return _Resp(self.query(GET, request_path))

    def get_filled_orders(self, trading_pair='BTC-USDT'):
        r""" Returns recently filled transaction details.
        This request supports paging and is stored according
        to the transaction time in chronological order from
        latest to earliest.
        Data for up to 3 months can be retrieved.

        Parameters
        ----------
        trading_pair : 	str
            The trading pair that was ordered


        Returns
        -------
        orders : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe

        Examples
        --------
        >>> filled = spot.get_filled_orders('STX-USD')
        >>> filled.df
                  created_at        currency  ...                 timestamp trade_id
        0   2021-04-02T15:20:37.000Z      USD  ...  2021-04-02T15:20:37.000Z   103932
        1   2021-04-02T15:20:37.000Z      BTC  ...  2021-04-02T15:20:37.000Z   103932
        """
        request_path = '/api/spot/v5/fills'
        body = {'instrument_id': trading_pair.lower()}
        return _Resp(self.query(GET, request_path, body=body))

class Earn(_Signature):
    """
    The Earn class is used to learn about yeild bearing offers on Okcoin and place orders.



        Parameters
        ----------
        config_file : A file containing the api_key, secret_key, and pass_phrase

        pass_phrase : If a pass_phrase is not specified in the config_file, it can be entered as a separate parameter
        or you will be prompted to enter it through your Python IDE.

        Attributes
        ----------

        Examples
        --------
        These are written in doctest format, and should illustrate how to
        use the function.

        >>> from okcoin import Earn
        >>> earn = Earn(config_file='auth.conf')

        """
    def get_offers(self, investment_currency="MIA", protocol_name="MiamiCoin"):
        r""" Returns the listing of offerings on Okcoin Earn.

        Parameters
        ----------
        investment_currency : 	str
            The currency you want to stake

        protocol_name : str
            The protocal listed for the currency


        Returns
        -------
        orders : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe

        Examples
        --------
        >>> offers = earn.get_offers("STX", "stacks")
        >>> offers.df
        max_invest_amount min_invest_amount  ... annual_interest_rate protocol_name
        0                         50.00000000  ...               0.1000        stacks
        [1 rows x 10 columns]
        """
        request_path = '/api/earning/v5/offers'
        body = {'investment_currency': investment_currency.upper(),
                'protocol_name': protocol_name}
        return _Resp(self.query(GET, request_path, body=body))

    def deposit(self, investment_currency="MIA", protocol_name="MiamiCoin", amount=50, cycles=1):
        r""" Returns the listing of offerings on Okcoin Earn.

        Parameters
        ----------
        investment_currency : 	str
            The currency you want to stake

        protocol_name : str
            The protocal listed for the currency

        amount : float
            The amount you want to deposit

        cycles : int
            The number of staking cycles, usually 1 or 12


        Returns
        -------
        orders : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe

        Examples
        --------
        >>> deposit = earn.get_offers("STX", "stacks", 100, 12)
        >>> deposit.df
        """
        request_path = '/api/earning/v5/purchase'
        body = {'investment_currency': investment_currency.upper(),
                'protocol_name': protocol_name.lower(),
                'amount':str(amount),
                'cycles':str(cycles)}
        return _Resp(self.query(POST, request_path, body=body))

    def cancel(self, order_id):
        r""" Cancel a deposit order that has been placed on Earn.

        Parameters
        ----------
        order_id : 	str
            The ID of the order to cancel.

        Returns
        -------
        orders : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe

        Examples
        --------
        >>> order = earn.cancel("1234")
        >>> order.df
        """
        request_path = '/api/earning/v5/cancel'
        body = {'order_id': str(order_id)}
        return _Resp(self.query(POST, request_path, body=body))

    def get_positions(self, investment_currency="MIA", protocol_name="MiamiCoin"):
        r""" Returns the the list of your assets currently earning yeild.

        Parameters
        ----------
        investment_currency : 	str
            The currency you want to stake

        protocol_name : str
            The protocal listed for the currency


        Returns
        -------
        orders : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe

        Examples
        --------
        >>> positions = earn.get_positions("STX", "stacks")
        >>> positions.df
        """
        request_path = '/api/earning/v5/positions'
        body = {'investment_currency': investment_currency.upper(),
                'protocol_name': protocol_name}
        return _Resp(self.query(GET, request_path, body=body))

    def get_order_details(self, investment_currency=None, protocol_name=None, status=None):
        r""" Returns the last 100 orders placed into Earn.

        Parameters
        ----------
        investment_currency : 	str
            The currency you want to stake

        protocol_name : str
            The protocal listed for the currency

        status : int
            An integer representing the status. This can be retrieved from the
            earn.status dictionary object.

        Returns
        -------
        orders : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe

        Examples
        --------
        >>> orders = earn.get_positions("STX", "stacks")
        >>> orders.df
        """
        request_path = '/api/earning/v5/orders'
        if investment_currency:
            body = {'investment_currency': investment_currency.upper()}
        elif investment_currency and protocol_name:
            body = {'investment_currency': investment_currency.upper(),
                    'protocol_name': protocol_name}
        elif status and investment_currency and protocol_name:
            body = {'investment_currency': investment_currency.upper(),
                'protocol_name': protocol_name,
                'status':status}
        else:
            body = ""

        resp = _Resp(self.query(GET, request_path, body=body))
        resp.df.replace({"status": self.order_status()},inplace=True)
        return resp
        #return _Resp(self.query(GET, request_path, body=body))

    def redeem_order(self, order_id, early_redemption_permit=False):
        r""" Redeeming flexible or fixed orders from Earn. This function only takes one order at a time.
        This will be updated to take a list of orders.

        Parameters
        ----------
        order_id : 	str or list
            The order(s) to redeem. If it is a single order, the order_id should be a string, for example, '1234'.
            If it is multiple orders, the order_id should be a list of string, for example, ['1234', '2345', '3456']

        early_redemption_permit : bool
            Permission for early redemption. Set to false by default. If submitting multiple orders, the single
            value will be applied to all orders.

        Returns
        -------
        orders : _Resp
            A query response opbect that contains the query result as a dictionary and as a dataframe

        Examples
        --------
        >>> redeem = earn.redeem_order("oid1234",True)
        >>> redeem.df
        """
        request_path = '/api/earning/v5/redeem'

        if type(order_id) == str:
            body = [{'order_id': order_id,
                    'early_redemption_permit':str(early_redemption_permit)}]
        elif type(order_id) == list:
            body = []
            for oid in order_ids:
                body.append({'order_id': str(oid),
                            'early_redemption_permit': str(early_redemption_permit).lower()})
        else:
            print('ERROR: order_id is not a list or a string.')

        return _Resp(self.query(POST, request_path, body=body))

    def order_status(self):
        return {'8': 'Pending',
            '13': 'Cancelling',
            '17': 'Cancelled',
            '9': 'Onchain',
            '1': 'Earning',
            '4': 'Redeem Pending',
            '2': 'Redeeming',
            '3': 'Redeemed'}

class Fiat(_Signature):
    """
    The Fiat class is used to withdraw and deposit money into your okcoin account. It enables you to
    understand your deposit and withdrawal history. It also enables you to withdraw and deposit currency
    if you have created an API key that enables trading. The Fiat class
    inherits from the Signature class, which takes as inputs a config file that contains your
    API_KEY, SECRET_KEY, and an optional PASS_PHRASE. If the PASS_PHRASE is not specified, you
    will be prompted for it upon instantiating the account object.


    Parameters
    ----------
    config_file : A file containing the api_key, secret_key, and pass_phrase

    pass_phrase : If a pass_phrase is not specified in the config_file, it can be entered as a separate parameter
    or you will be prompted to enter it through your Python IDE.

    Attributes
    ----------

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.

    >>> from okcoin import Fiat
    >>> fiat = Fiat(config_file='auth.conf')

    """

    def get_deposit_history(self):
        r""" Returns the details of a deposit given the
        deposit ID.

        Parameters
        ----------
        deposit_id : str
            The dataframe generated by the


        Returns
        -------
        deposit_hist : _Resp
            A query response object that contains the query result as a dictionary and as a dataframe


        Examples
        --------
        >>>
        """
        request_path = '/api/v5/asset/deposit-history'
        return _Resp(self.query(GET, request_path))

    def get_channel_info(self):
        r""" Returns the status of an order and the numeric value that corresponds to it
        in the Okcoin API.

        Parameters
        ----------
        df : 	dataframe
            The dataframe generated by the


        Returns
        -------
        balance : _Resp
            A n object that...

        Examples
        --------
        >>>
        """
        request_path = '/api/account/v5/fiat/channel'
        return _Resp(self.query(GET, request_path))

    def get_withdrawal_history(self):
        r""" Returns the status of an order and the numeric value that corresponds to it
        in the Okcoin API.

        Parameters
        ----------
        df : 	dataframe
            The dataframe generated by the


        Returns
        -------
        balance : _Resp
            A n object that...

        Examples
        --------
        >>>
        """
        request_path = '/api/account/v5/fiat/withdraw/details'
        return __Resp(self.query(GET, request_path))
