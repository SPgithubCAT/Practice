import time
import pyupbit
import datetime

access = "YdCCrkQhmfJVMa9MvF2yOO8R217dlPmwjjWST3xm"
secret = "lynjwDcZXPZ98FmfgBPuwwcGfUQWzLBBqIPxXKMO"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=100)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

# def get_start_time(ticker):
#     """시작 시간 조회"""
#     df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
#     start_time = df.index[0]
#     return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


df2 = pyupbit.get_ohlcv("KRW-ADA", interval="minute60", count=100)
df2['FastK'] = (df2['close'] - df2['low'].rolling(14).min()) / (df2['high'].rolling(14).max() - df2['low'].rolling(14).min()) * 100
df2['SlowK'] = df2['FastK'].rolling(3).mean()
df2['SlowD'] = df2['SlowK'].rolling(3).mean()



# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        # now = datetime.datetime.now()
        # start_time = get_start_time("KRW-ETC")
        # end_time = start_time + datetime.timedelta(days=1)

        
        target_price = get_target_price("KRW-ADA", 0.1)
        current_price = get_current_price("KRW-ADA")
        c1 = df2['open'].count()-1
            
        if target_price < current_price and df2.iloc[c1,7] > df2.iloc[c1,8]:
           krw = get_balance("KRW")
           if krw > 6000:
                upbit.buy_market_order("KRW-ADA", krw*0.9995)
        else:
            CCoin = get_balance("ADA")
            if CCoin > 0.001:
                upbit.sell_market_order("KRW-ADA", CCoin*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
