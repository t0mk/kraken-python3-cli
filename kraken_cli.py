#!/usr/bin/env python3

# All you need to use https://www.kraken.com/help/api in one file with a lot of
# dependencies.

# PYTHON_ARGCOMPLETE_OK

import os
import sys
import copy
import time
import calendar
import pprint
import logging
import getpass
import datetime
import urllib
import functools
import dateutil.parser
import hashlib
import hmac
import base64
import collections

import argh
import requests
import tabulate


KRAKEN_API_URL = "https://api.kraken.com"


OTP_CACHE_FILE = os.path.expanduser("~/.kraken_otp")


KRAKENKEY_FILE_ENV_VAR = "KRAKENKEY_FILE"


#ASSETS = ['KFEE', 'USDT', 'XDAO', 'XETC', 'XETH', 'XICN', 'XLTC', 'XMLN',
#          'XNMC', 'XREP', 'XXBT', 'XXDG', 'XXLM', 'XXMR', 'XXRP', 'XXVN',
#          'XZEC', 'ZCAD', 'ZEUR', 'ZGBP', 'ZJPY', 'ZKRW', 'ZUSD', 'EUR',
#          'FEE', 'USDT', 'DAO', 'ETC', 'ETH', 'ICN', 'LTC', 'MLN', 'NMC',
#          'REP', 'XBT', 'XDG', 'XLM', 'XMR', 'XRP', 'XVN', 'ZEC', 'CAD',
#          'GBP', 'JPY', 'KRW', 'USD']

ASSETS = [
        "XXLM",
        "XXBT",
        "XNMC",
        "DASH",
        "XREP",
        "XICN",
        "XXRP",
        "XZEC",
        "XETH",
        "ZKRW",
        "KFEE",
        "USDT",
        "XXDG",
        "ZJPY",
        "XLTC",
        "ZGBP",
        "EOS",
        "ZUSD",
        "XETC",
        "XDAO",
        "BCH",
        "ZCAD",
        "ZEUR",
        "GNO",
        "XXMR",
        "XMLN",
        "XXVN"]

PAIRS = [
        "XXBTZCAD",
        "USDTZUSD",
        "XMLNXXBT",
        "XETHZUSD.d",
        "XXBTZJPY",
        "GNOXBT",
        "BCHXBT",
        "XETHZUSD",
        "XZECZJPY",
        "XETCZEUR",
        "XXBTZGBP",
        "XXLMZEUR",
        "DASHUSD",
        "XETHZGBP.d",
        "XETHZCAD.d",
        "XETHXXBT.d",
        "XXBTZJPY.d",
        "XXRPZEUR",
        "XREPZEUR",
        "XXRPZCAD",
        "XXLMXXBT",
        "DASHEUR",
        "XMLNXETH",
        "XICNXXBT",
        "XLTCZUSD",
        "GNOUSD",
        "XETCZUSD",
        "XXBTZGBP.d",
        "XETHZGBP",
        "XXRPZJPY",
        "EOSETH",
        "XICNXETH",
        "XREPXETH",
        "BCHUSD",
        "DASHXBT",
        "XXLMZUSD",
        "XETHZCAD",
        "XXBTZEUR",
        "GNOETH",
        "XXBTZCAD.d",
        "XREPXXBT",
        "XZECXXBT",
        "XETHZEUR.d",
        "XXBTZUSD",
        "XXRPXXBT",
        "XETHZJPY",
        "EOSXBT",
        "XXRPZUSD",
        "XXBTZUSD.d",
        "GNOEUR",
        "BCHEUR",
        "EOSUSD",
        "XXDGXXBT",
        "XETCXXBT",
        "XLTCZEUR",
        "XZECZUSD",
        "XETHZJPY.d",
        "EOSEUR",
        "XXBTZEUR.d",
        "XETHXXBT",
        "XREPZUSD",
        "XETHZEUR",
        "XZECZEUR",
        "XETCXETH",
        "XXMRZEUR",
        "XXMRXXBT",
        "XLTCXXBT",
        "XXMRZUSD"]

CLOSETIMES = ['open', 'close', 'both']


TRADETYPES = ["all", "any position", "closed position", "closing position",
              "no position"]


LEDGERTYPES = ['all', 'deposit', 'withdrawal', 'trade', 'margin']


BSTYPES = ['buy', 'sell']


ORDERTYPES = ['market', 'limit', 'stop-loss', 'take-profit',
              'stop-loss-profit', 'stop-loss-profit-limit', 'stop-loss-limit',
              'take-profit-limit', 'trailing-stop', 'trailing-stop-limit',
              'stop-loss-and-limit', 'settle-position']


def prettytime(ts):
    dt = datetime.datetime.utcfromtimestamp(float(ts))
    return dt.isoformat()[:22].replace("T", "_")


def prettify_time_in_list_of_dicts(l):
    _l = copy.deepcopy(l)
    for i in _l:
        for k in i:
            if 'time' in k:
                i[k] = prettytime(i[k])
    return _l

def to_ordered(list_of_dicts):
    _l = []
    for d in list_of_dicts:
        _l.append(collections.OrderedDict(sorted(d.items())))
    return _l

def tabprint(l, sortkey='time'):
    _l = list(l)
    if not _l:
        print("empty response")
        return
    if sortkey in _l[0]:
        _l = sorted(_l, key=lambda i: i[sortkey])
    tab = prettify_time_in_list_of_dicts(_l)
    tab = to_ordered(tab)
    print(tabulate.tabulate(tab, headers='keys'))


def ohlcprint(d, pair):
    l = d[pair]
    # <time>, <open>, <high>, <low>, <close>, <vwap>, <volume>, <count>
    l = [(prettytime(t), o, h, l, c, vw, v, c)
         for t, o, h, l, c, vw, v, c in l]
    keys = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']
    print(tabulate.tabulate(l, headers=keys))
    if 'last' in d:
        print("Last: %d, %s" % (d['last'], prettytime(d['last'])))


def spreadprint(d, pair):
    l = d[pair]
    l = [(prettytime(ti), float(t) - float(b), float(b), float(t))
         for ti, b, t in l]
    # price, volume, time
    keys = ['time', 'diff', 'bottom', 'top']
    print(tabulate.tabulate(l, headers=keys))
    if 'last' in d:
        print("Last: %d, %s" % (d['last'], prettytime(d['last'])))


def tradesprint(d, pair):
    l = d[pair]
    # price, volume, time
    keys = ['price', 'volume', 'time', 'buy/sell', 'lim/mark', 'note']
    l = [(p, v, prettytime(t), bs, lm, n) for p, v, t, bs, lm, n in l]
    print(tabulate.tabulate(l, headers=keys))
    if 'last' in d:
        ts = int(d['last']) / 10e8
        print("Last: %d, %s" % (int(d['last']), prettytime(ts)))


def obprint(d, pair):
    d = d[pair]
    rasks = sorted(d['asks'], reverse=True)
    rasks = [(p, v, prettytime(t)) for p, v, t in rasks]
    bids = [(p, v, prettytime(t)) for p, v, t in d['bids']]
    keys = ['price', 'volume', 'timestamp']
    print(tabulate.tabulate(rasks, headers=keys))
    print("------")
    print("ASKS ^")
    print("------")
    print("BIDS v")
    print("------")
    print(tabulate.tabulate(bids, headers=keys))


def guessprint(d):
    _d = dict(d)
    remove_keys = ['lot_decimals', 'fees', 'fee_volume_currency',
                   'aclass_quote', 'aclass_base', 'fees_maker']
    for k in d:
        _d[k]['asset'] = k
        for l in remove_keys:
            if l in _d[k]:
                del _d[k][l]
    tabprint(_d.values())


def dictprint(d):
    _d = dict(d)
    for k in d:
        _d[k]['id'] = k
    tabprint(_d.values())


def toughdictprint(d, key):
    if key == 'closed':
        key = 'close'
    _d = {k: v['descr'] for k, v in d.items()}
    for k in _d:
        _d[k]['ordid'] = k
        if _d[k]['ordertype'] == 'market':
            _d[k]['price'] = d[k]['price']
        _d[k][key + 'time'] = d[k][key + 'tm']
    tabprint(_d.values(), key + 'time')


class HTTPSession(object):
    __instance = None

    def __new__(cls):
        if HTTPSession.__instance is None:
            s = requests.Session()
            HTTPSession.__instance = s
        return HTTPSession.__instance


def iso_to_unix(isodatetime):
    d = dateutil.parser.parse(isodatetime)
    ts = calendar.timegm(d.timetuple())
    return int(ts)


def api_query_public(api_method, params):
    urlbase = KRAKEN_API_URL + "/0/public/"
    r = HTTPSession().get(urlbase + api_method, params=params)
    return r.json()


def get_otp(prompt):
    if os.path.isfile(OTP_CACHE_FILE):
        if os.path.getmtime(OTP_CACHE_FILE) > time.time() - 90:
            with open(OTP_CACHE_FILE) as f:
                return f.read()
    otp = getpass.getpass(prompt)
    with open(OTP_CACHE_FILE, "w") as f:
        f.write(otp)
    os.chmod(OTP_CACHE_FILE, 0o600)
    return otp


def api_query_private(api_method, params):
    if os.environ.get("KRAKENAPI_USE_OTP"):
        params['otp'] = get_otp("OTP for %s, params %s: " %
                                (api_method, params))
    urlpath = "/0/private/" + api_method
    key_file_path = os.environ.get(KRAKENKEY_FILE_ENV_VAR)
    if key_file_path:
        with open(key_file_path, 'r') as f:
            key = f.readline().strip()
            secret = f.readline().strip()
    else:
        msg = ("To access private API, you need to download API key and"
               " secret from kraken.com, and put it to a file, specified in"
               " the %s environment variable. Put the key on first line,"
               " and the secret on second line" % KRAKENKEY_FILE_ENV_VAR)
        raise Exception(msg)

    # based on
    # https://github.com/veox/python3-krakenex/tree/master/krakenex/api.py
    params['nonce'] = int(1000 * time.time())
    postdata = urllib.parse.urlencode(params)
    encoded = (str(params['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    signature = hmac.new(base64.b64decode(secret),
                         message, hashlib.sha512)
    sigdigest = base64.b64encode(signature.digest())

    headers = {
        'API-Key': key,
        'API-Sign': sigdigest.decode()
    }

    r = HTTPSession().post(KRAKEN_API_URL + urlpath, data=params,
                           headers=headers)
    return r.json()


def query(qtype, api_method, params={}):
    if os.environ.get("DEBUG"):
        logging.basicConfig(level=logging.DEBUG)
    assert(qtype in ['private', 'public'])
    if params.get('start'):
        params['start'] = iso_to_unix(params['start'])
    if params.get('end'):
        params['end'] = iso_to_unix(params['end'])
    if params.get('since'):
        try:
            params['since'] = iso_to_unix(params['since'].replace("_", "T"))
            if api_method == 'Trades':
                params['since'] = int(params['since'] * 10e8)
        except Exception as e:
            logging.debug(e)

    logging.debug("sending")
    logging.debug(api_method)
    logging.debug(params)
    new_params = {k.replace("_", "-"): v for (k, v) in params.items()}
    if qtype == 'private':
        res = api_query_private(api_method, new_params)
    else:
        res = api_query_public(api_method, new_params)
    logging.debug("obtained")
    logging.debug(res)

    if 'error' in res:
        if res['error']:
            msg = ", ".join(res['error'])
            if 'EAPI:Invalid signature' in res['error']:
                msg += ", perhaps a missing/wrong/old OTP?"
            if 'EAPI:Invalid key' in res['error']:
                msg += (", perhaps you try to call private API method and you"
                        " did not export path to your key file to env var %s"
                        " or your key has expired" % KRAKENKEY_FILE_ENV_VAR)
            raise Exception(msg)

    if 'result' in res:
        result = res['result']
        if os.environ.get("KRAKENCLI_RAW_RESULT"):
            return result
        if api_method == 'Depth':
            obprint(result, pair=params['pair'])
        elif api_method == 'OHLC':
            ohlcprint(result, pair=params['pair'])
        elif api_method == 'Trades':
            tradesprint(result, pair=params['pair'])
        elif api_method == 'Spread':
            spreadprint(result, pair=params['pair'])
        elif api_method == 'Assets':
            dictprint(result)
        elif api_method == 'AssetPairs':
            guessprint(result)
        elif api_method == 'Ledgers':
            dictprint(result['ledger'])
        elif api_method == 'TradesHistory':
            dictprint(result['trades'])
        elif api_method == 'OpenOrders':
            toughdictprint(result['open'], 'open')
        elif api_method == 'ClosedOrders':
            # not a typo ...
            toughdictprint(result['closed'], 'close')
        elif isinstance(result, list):
            if result == []:
                print("Got empty list as a result.")
            else:
                tabprint(result)
        else:
            pprint.pprint(res['result'])


def set_values(_d):
    return {k: v for k, v in _d.items()
            if v is not None and not k.startswith("_")}


@argh.arg("-a", "--asset", choices=ASSETS + [None])
def Assets(info=None, aclass=None, asset=None):
    _fname = sys._getframe().f_code.co_name
    return query('public', _fname, set_values(locals()))


@argh.arg("-i", "--info", choices=['info', 'leverage', 'fees', 'margin'])
@argh.arg("-p", "--pair", choices=PAIRS + [None])
def AssetPairs(info='info', pair=None):
    _fname = sys._getframe().f_code.co_name
    return query('public', _fname, set_values(locals()))


@argh.arg("pair", choices=PAIRS)
def Ticker(pair):
    _fname = sys._getframe().f_code.co_name
    return query('public', _fname, set_values(locals()))


@argh.arg("pair", choices=PAIRS)
def Depth(pair, count:int=20):
    _fname = sys._getframe().f_code.co_name
    return query('public', _fname, set_values(locals()))


@argh.arg("pair", choices=PAIRS)
@argh.arg("-i", "--interval", choices=[1, 5, 15, 30, 60, 240, 10080, 21600])
def OHLC(pair, interval=1, since=None):
    _fname = sys._getframe().f_code.co_name
    return query('public', _fname, set_values(locals()))


@argh.arg("pair", choices=PAIRS)
def Trades(pair, since=None):
    _fname = sys._getframe().f_code.co_name
    return query('public', _fname, set_values(locals()))


@argh.arg("pair", choices=PAIRS)
def Spread(pair, since=None):
    _fname = sys._getframe().f_code.co_name
    return query('public', _fname, set_values(locals()))


def Time():
    _fname = sys._getframe().f_code.co_name
    return query('public', _fname)


@argh.aliases('balance', 'bal')
def Balance():
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname)


@argh.arg("asset", choices=ASSETS)
def TradeBalance(asset, aclass=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


def OpenOrders(trades=None, userref=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


@argh.arg("-c", "--closetime", choices=CLOSETIMES + [None])
def ClosedOrders(trades=None, userref=None, start=None, end=None, ofs=None,
                 closetime='both'):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


# txid is e.g. OZMY26-UBBFP-BFQOFG[,OYQ373-PCW3O-GKM4PM] ...
def QueryOrders(txid, trades=None, userref=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


def QueryTrades(txid, trades=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


# Ledger id is e.g. LZMY26-UBBFP-BFQOFG[,LYQ373-PCW3O-GKM4PM] ...
def QueryLedgers(id):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


def OpenPositions(txid=None, docalcs=False):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


@argh.arg("-t", "--type", choices=TRADETYPES + [None])
def TradesHistory(type=None, start=None, end=None, ofs=None,
                  trades=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


@argh.arg("-t", "--type", choices=LEDGERTYPES + [None])
@argh.arg("-a", "--asset", choices=ASSETS + [None])
def Ledgers(asset=None, type=None, aclass=None, start=None, end=None,
            ofs=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


@argh.arg("pair", choices=PAIRS)
def TradeVolume(pair, fee_info=False):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


# oflags can be a list of
#   viqc = volume in quote currency (not available for leveraged orders)
#   fcib = prefer fee in base currency
#   fciq = prefer fee in quote currency
#   nompp = no market price protection
#   post = post only order (available when ordertype = limit)
#
# starttm = scheduled start time (optional):
#    0 = now (default)
#    +<n> = schedule start time <n> seconds from now
#    <n> = unix timestamp of start time
#
# expiretm = expiration time (optional):
#    0 = no expiration (default)
#    +<n> = expire <n> seconds from now
#    <n> = unix timestamp of expiration time
#
# userref = user reference id.  32-bit signed number.  (optional)
#
# validate = validate inputs only.  do not submit order (optional)

@argh.arg("pair", choices=PAIRS)
@argh.arg("type", choices=BSTYPES)
@argh.arg("ordertype", choices=ORDERTYPES)
@argh.arg("-v", "--validate")
@argh.arg("-p", "--price")
@argh.arg("-p2", "--price2")
def AddOrder(pair, type, ordertype, volume, price=None, price2=None,
             leverage=None, oflags=None, starttm=None, expiretm=None,
             userref=None, validate=False):
    if not validate:
        validate = None
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


def CancelOrder(txid):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


@argh.arg("asset", choices=ASSETS)
def DepositMethods(asset, aclass=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


# method is 'Bitcoin', or ???
@argh.arg("asset", choices=ASSETS)
def DepositAddresses(asset, method, aclass=None, new=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


@argh.arg("asset", choices=ASSETS)
def DepositStatus(asset, method, aclass=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


@argh.arg("asset", choices=ASSETS)
def WithdrawInfo(asset, key, amount: float, aclass=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


@argh.arg("asset", choices=ASSETS)
def Withdraw(asset, key, amount: float, aclass=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


@argh.arg("asset", choices=ASSETS)
def WithdrawStatus(asset, method=None, aclass=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


@argh.arg("asset", choices=ASSETS)
def WithdrawCancel(asset, refid, aclass=None):
    _fname = sys._getframe().f_code.co_name
    return query('private', _fname, set_values(locals()))


if __name__ == '__main__':
    exposed = [Time, Assets, AssetPairs, Ticker, OHLC, Depth, Trades,
               Spread, Balance, TradeBalance, OpenOrders, ClosedOrders,
               QueryOrders, TradesHistory, QueryTrades, OpenPositions,
               Ledgers, QueryLedgers, TradeVolume, AddOrder, DepositMethods,
               DepositAddresses, DepositStatus, WithdrawInfo, Withdraw,
               WithdrawStatus, WithdrawCancel, CancelOrder]

    parser = argh.ArghParser()
    parser.add_commands(exposed)
    parser.dispatch()
