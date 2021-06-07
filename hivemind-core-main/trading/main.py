from hivemind_trading import Investopedia
import json


def get_account_balance():
    account = Investopedia()
    balance = account.get_portfolio().account_value
    return balance


def place_order(order_info):
    account = Investopedia()
    account.get_stock_info(order_info["stock_name"])
    response = account.place_order(order_info)
    return response


def get_balance(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    balance      = get_account_balance()
    return json.dumps({"account_balance": float(balance)})


def trade(request):
    order_info = {
        "stock_name": "GOOG",
        "quantity": 12,
        "order_type": "buy"
    }
    order_response = place_order(order_info)
    if order_response is not None:
        return order_response
    else:
        return f'Order was unsuccessful'


def open_trade(request):
    account = Investopedia()
    portfolio = account.get_portfolio()

    open_orders = []

    for order in portfolio.open_orders:
        order_dict = {k: v for k, v in vars(order).items() if k not in ["cancel_fn"]}
        order_dict["order_price"] = float(order_dict["order_price"])
        order_dict["order_date"] = str(order_dict["order_date"])

        open_orders.append(order_dict)

    return json.dumps(open_orders)
