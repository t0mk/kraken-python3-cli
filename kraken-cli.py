#!/usr/bin/env python3

import krakenex
import argh
import os
import sys
import yaml
import pprint
import logging
import tabulate


ASSETS = ['KFEE', 'USDT', 'XDAO', 'XETC', 'XETH', 'XICN', 'XLTC', 'XMLN',
          'XNMC', 'XREP', 'XXBT', 'XXDG', 'XXLM', 'XXMR', 'XXRP', 'XXVN',
          'XZEC', 'ZCAD', 'ZEUR', 'ZGBP', 'ZJPY', 'ZKRW', 'ZUSD', 'EUR',
          'FEE', 'USDT', 'DAO', 'ETC', 'ETH', 'ICN', 'LTC', 'MLN', 'NMC',
          'REP', 'XBT', 'XDG', 'XLM', 'XMR', 'XRP', 'XVN', 'ZEC', 'CAD',
          'GBP', 'JPY', 'KRW', 'USD']

PAIRS = ['USDTZUSD', 'XETCXETH', 'XETCXXBT', 'XETCZEUR', 'XETCZUSD', 'XETHXXBT',
         'XETHXXBT.d', 'XETHZCAD', 'XETHZCAD.d', 'XETHZEUR', 'XETHZEUR.d',
         'XETHZGBP', 'XETHZGBP.d', 'XETHZJPY', 'XETHZJPY.d', 'XETHZUSD',
         'XETHZUSD.d', 'XICNXETH', 'XICNXXBT', 'XLTCXXBT', 'XLTCZEUR',
         'XLTCZUSD', 'XMLNXETH', 'XMLNXXBT', 'XREPXETH', 'XREPXXBT', 'XREPZEUR',
         'XREPZUSD', 'XXBTZCAD', 'XXBTZCAD.d', 'XXBTZEUR', 'XXBTZEUR.d',
         'XXBTZGBP', 'XXBTZGBP.d', 'XXBTZJPY', 'XXBTZJPY.d', 'XXBTZUSD',
         'XXBTZUSD.d', 'XXDGXXBT', 'XXLMXXBT', 'XXLMZEUR', 'XXLMZUSD',
         'XXMRXXBT', 'XXMRZEUR', 'XXMRZUSD', 'XXRPXXBT', 'XZECXXBT', 'XZECZEUR',
         'XZECZUSD', 'USDTUSD', 'ETCETH', 'ETCXBT', 'ETCEUR', 'ETCUSD',
         'ETHXBT', 'ETHXBT.d', 'ETHCAD', 'ETHCAD.d', 'ETHEUR', 'ETHEUR.d',
         'ETHGBP', 'ETHGBP.d', 'ETHJPY', 'ETHJPY.d', 'ETHUSD', 'ETHUSD.d',
         'ICNETH', 'ICNXBT', 'LTCXBT', 'LTCEUR', 'LTCUSD', 'MLNETH', 'MLNXBT',
         'REPETH', 'REPXBT', 'REPEUR', 'REPUSD', 'XBTCAD', 'XBTCAD.d', 'XBTEUR',
         'XBTEUR.d', 'XBTGBP', 'XBTGBP.d', 'XBTJPY', 'XBTJPY.d', 'XBTUSD',
         'XBTUSD.d', 'XDGXBT', 'XLMXBT', 'XLMEUR', 'XLMUSD', 'XMRXBT', 'XMREUR',
         'XMRUSD', 'XRPXBT', 'ZECXBT', 'ZECEUR', 'ZECUSD']

def obprint(d):
    asks = 

def guessprint(d):
    _d = dict(d)
    remove_keys = ['lot_decimals', 'fees', 'fee_volume_currency', 'aclass_quote',
                   'aclass_base', 'fees_maker']
    for k in d:
        _d[k]['asset'] = k
        for l in remove_keys:
            if l in _d[k]:
                del _d[k][l]
    print(tabulate.tabulate(_d.values(), headers='keys'))

def dictprint(d):
    _d = dict(d)
    for k in d:
        _d[k][k[0] + 'id'] = k
    print(tabulate.tabulate(_d.values(), headers='keys'))

def toughdictprint(d, key):
    _d = {k: v['descr'] for k,v in d.items()}
    for k in _d:
        #_d[k].pop('order')
        _d[k]['ordid'] = k
        if _d[k]['ordertype'] == 'market':
            _d[k]['price'] =  d[k]['price']
        _d[k][key+'time'] = d[k][key+'tm']
    tab = _d.values()
    print(tabulate.tabulate(tab, headers='keys'))

def process(api_method, res):
    if 'error' in res:
        raise Exception(res['error'])
    if 'result' in res:
        proces_map = {'Depth': obprint(result)}
        result = res['result']
        if api_method in process_map:
            process_map[api_method](result)
            return
        if type(result) is list:
            if type(result[0]) is dict:
                print(tabulate.tabulate(result, headers='keys'))
                return
        if type(result) is dict:

            simple_keys = ['ledger', 'trades']
            for k in simple_keys:
                if k in result:
                    dictprint(result[k])
                    return
            tough_keys = ['closed', 'open']
            for k in tough_keys:
                if k in result:
                    toughdictprint(result[k], k)
                    return

            guessprint(result)
            return

        pprint.pprint(res['result'])
        return
    raise Exception("Empty response: %s" % res)


class KX(object):
    __instance = None
    def __new__(cls):
        if KX.__instance is None:
            k = krakenex.API()
            k.load_key(os.environ.get("KRAKENKEY_FILE"))
            KX.__instance = k
        return KX.__instance

def query(qtype, api_method, params=None):
    assert(qtype in ['private', 'public'])
    if os.environ.get("OTP"):
        params['otp'] = os.environ.get("OTP")
    logging.debug(api_method)
    logging.debug(params)
    new_params = {k.replace("_","-"): v for (k,v) in params.items()}
    if qtype == 'private':
        result = KX().query_private(api_method, new_params)
    else:
        result = KX().query_public(api_method, new_params)
    logging.debug(result)
    return result

if __name__ == '__main__':

    set_values = lambda _d: {k:v for k,v in _d.items()
                             if v is not None and not k.startswith("_")}

    # https://www.kraken.com/help/api

    @argh.arg("-a", "--asset", choices=ASSETS + [None])
    def Assets(info=None, aclass=None, asset=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('public',_fname,set_values(locals())))
    
    @argh.arg("-i", "--info", choices=['info', 'leverage','fees', 'margin'])
    @argh.arg("-p", "--pair", choices=PAIRS + [None])
    def AssetPairs(info='info', pair=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('public',_fname, set_values(locals())))

    @argh.arg("pair", choices=PAIRS)
    def Ticker(pair):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('public',_fname,set_values(locals())))

    @argh.arg("pair", choices=PAIRS)
    def Depth(pair, count:int = 100):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('public',_fname,set_values(locals())))

    @argh.arg("pair", choices=PAIRS)
    @argh.arg("-i", "--interval", choices=[1,5,15,30,60,240,10080,21600])
    def OHLC(pair, interval=1, since=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('public',_fname, set_values(locals())))

    @argh.arg("pair", choices=PAIRS)
    def Trades(pair, since=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('public',_fname, set_values(locals())))

    @argh.arg("pair", choices=PAIRS)
    def Spread(pair, since=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('public',_fname, set_values(locals())))

    def Time():
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('public',_fname))
    
    @argh.aliases('balance','bal')
    def Balance():
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname))

    @argh.arg("asset", choices=ASSETS)
    def TradeBalance(asset, aclass=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    def OpenOrders(trades=False, userref=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    CLOSETIMES = ['open', 'close', 'both']
    @argh.arg("-c", "--closetime", choices=CLOSETIMES + [None])
    def ClosedOrders(trades=False, userref=None, start=None, end=None, ofs=None,
                     closetime='both'):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    # txid is e.g. OZMY26-UBBFP-BFQOFG[,OYQ373-PCW3O-GKM4PM] ...
    def QueryOrders(txid, trades=False, userref=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    def QueryTrades(txid, trades=False):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    # Ledger id is e.g. OZMY26-UBBFP-BFQOFG[,OYQ373-PCW3O-GKM4PM] ...
    def QueryLedgers(id):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    def OpenPositions(txid=None, docalcs=False):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    TRADETYPES = ["all", "any position", "closed position", "closing position",
                  "no position"]
    @argh.arg("-t", "--type", choices=TRADETYPES + [None])
    def TradesHistory(type=None, start=None, end=None, ofs=None,
                      trades=False):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    LEDGERTYPES = ['all', 'deposit', 'withdrawal', 'trade', 'margin']

    @argh.arg("-t", "--type", choices=LEDGERTYPES + [None])
    @argh.arg("-a", "--asset", choices=ASSETS + [None])
    def Ledgers(asset=None, type=None, aclass=None, start=None, end=None,
                ofs=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    @argh.arg("pair", choices=PAIRS)
    def TradeVolume(pair, fee_info=False):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname, set_values(locals())))
    
    BSTYPES = ['buy', 'sell']
    ORDERTYPES = ['market', 'limit', 'stop-loss', 'take-profit',
        'stop-loss-profit', 'stop-loss-profit-limit', 'stop-loss-limit',
        'take-profit-limit', 'trailing-stop', 'trailing-stop-limit',
        'stop-loss-and-limit', 'settle-position']

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
    def AddOrder(pair, type, ordertype, price:float, price2:float=0.,
            volume:float=0., leverage=None, oflags=None, starttm=0, expiretm=0,
            userref=None,validate=False):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname, set_values(locals())))

    def CancelOrder(txid):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    @argh.arg("asset", choices=ASSETS)
    def DepositMethods(asset, aclass=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))
    
    # method is 'Bitcoin', or 
    @argh.arg("asset", choices=ASSETS)
    def DepositAddresses(asset, method, aclass=None, new=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    @argh.arg("asset", choices=ASSETS)
    def DepositStatus(asset, method, aclass=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    @argh.arg("asset", choices=ASSETS)
    def WithdrawInfo(asset, key, amount:float, aclass=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    @argh.arg("asset", choices=ASSETS)
    def Withdraw(asset, key, amount:float, aclass=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    @argh.arg("asset", choices=ASSETS)
    def WithdrawStatus(asset, method=None, aclass=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    @argh.arg("asset", choices=ASSETS)
    def WithdrawCancel(asset, refid, aclass=None):
        _fname = sys._getframe().f_code.co_name
        process(_fname,query('private',_fname,set_values(locals())))

    # Not very DRY
    exposed = [
               Time, Assets, AssetPairs, Ticker, OHLC, Depth, Trades,
               Spread, Balance, TradeBalance, OpenOrders, ClosedOrders,
               QueryOrders, TradesHistory, QueryTrades, OpenPositions,
               Ledgers, QueryLedgers, TradeVolume, AddOrder, DepositMethods,
               DepositAddresses, DepositStatus, WithdrawInfo, Withdraw, 
               WithdrawStatus, WithdrawCancel
              ]

    if os.environ.get("DEBUG"):
        logging.basicConfig(level=logging.DEBUG)
   
    parser = argh.ArghParser()
    parser.add_commands(exposed)
    parser.dispatch()

