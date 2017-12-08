# Complete CLI for Kraken in Python 3

I tried to take https://www.kraken.com/help/api and express it in Python fucntion declaration. The functions are crunched by argh[0] and exposed to argument parser, rendering a relatively nice CLI which very closely follows the Kraken API doc.

In general, compulsory arguments are positional, and optional/reasonable-defaults arguments are passed by flag. E.g. to display order book of XXBTZEUR up to 15 items: `./kx Depth -c 15 XXBTZEUR`.

I wrote this because the other CLIs to Kraken seemed too complicated. This CLI is one file and has relatively few and standard dependencies.

[0] https://github.com/neithere/argh/

## Dependencies

`pip3 install requests tabulate argh python-dateutil`

If you want autocomplete in bash, you must install argcomplete:

```
pip3 install argcomplete
activate-global-python-argcomplete
```

## Usage

You can do whatever is at https://www.kraken.com/help/api. If unsure, see `./kx help <Method>`, e.g. `./kx help AddOrder`

### Authentication

If you want to use private API calls, you need to get API key and secret from https://www.kraken.com. Put it to a file on separate lines, first key and then secret, e.g.

```
xvjiddoff0942r029rj340r43GFDgDFgdfgdfgfdgDFGFDgdfgd46868
TgfopdgkdfGSFdg54$5gf45g+gbrgrtHY5imlkm98htfghdfh4h+516+fdh+g4hfgh+fg6hdfhdfhdf+gdfghD==
```

and then export path to this file in environment variable `KRAKENKEY_FILE`.

### One time passwords

In Kraken, you can set OTP for a particular API keys. You can even specify for which method groups you want to use OTP (Depositing, Withdrawing, Creating orders, Closing positions, Canceling orders).

You can istruct this scipt to use OTP. Just set env var `KRAKENAPI_USE_OTP` to a true-evaluating string. The script will then ask you for OTP, and will cache it for 90 seconds. 

### Examples

Show available assets.

```
./kx Assets
```

Show asset pairs

```
./kx AssetPairs
```

Show balance (private method), and ask for OTP:

```
KRAKENAPI_USE_OTP=1 ./kx Balance
```

Sell 0.001 BTC for EUR 

```
export KRAKENAPI_USE_OTP=1

# first just validate the order 
./kx AddOrder -v XXBTZEUR sell market 0.001

# If OK, then submit it
./kx AddOrder XXBTZEUR sell market 0.001
```

Place limit order to buy 0.1 BTC for 931.14 EUR

```
./kx AddOrder -p 931.14 XXBTZEUR buy limit 0.1
```

### Tips

- `AddOrder` has `-v` flag which will only validate the order, it will not create it.

### Using as a module

The HTTP connection to kraken API is cached within a process via requests.Session. Thus the TCP/SSL connection is opened only once for consequent requests in the same script.

It appears that the largest delay is in opening the connection. Once that's over, the API requests are quite fast.

You can call the functions from a Python script and process the results yourself if you want. You just need to tell `kraken_cli.py` not to print the response by setting the `KRAKENCLI_RAW_RESULT` env var to true-evaluating string.

To place a limit sell just below the lowest ask:

```
import kraken_cli as kx
import os

os.environ['KRAKENCLI_RAW_RESULT'] = "yeah"

# if you have otp enabled you must set this env var
os.environ['KRAKENAPI_USE_OTP'] = "yeah"

# also, if you use OTP, you don't want to be asked between the Depth and
# AddOrder calls, so do a dummy query for balance to put fresh OTP to cache
kx.Balance()

pair = "XXBTZEUR"

order_book = kx.Depth(pair)

asks = order_book[pair]['asks']
bids = order_book[pair]['bids']

res = kx.AddOrder(pair, 'sell', 'limit', 0.001, price=float(asks[0][0]) - .01)

print(res)

```

## TODO

- Nice shell completion in zsh/oh-my-zsh. Is there sth that could work with argh??
- Wrappers around AddOrder to sanitize the more common limit orders.
