import time
import pyupbit
import datetime

access = "YdCCrkQhmfJVMa9MvF2yOO8R217dlPmwjjWST3xm"
secret = "lynjwDcZXPZ98FmfgBPuwwcGfUQWzLBBqIPxXKMO"

set_time = "minute"
set_time_num = str(5)
set_time_end = 5
set_interval = set_time + set_time_num
set_count = 200 
set_ticker = "KRW-ETH"
set_ticker2 = "ETH"
kk = 0.2

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval=set_interval, count=2) # ---------------------------------------------------------------- 숫자 2로 고정. 바로 전 캔들 기준.
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval=set_interval, count=1)
    start_time = df.index[0]
    return start_time

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




# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETC")
        end_time = start_time + datetime.timedelta(minutes=set_time_end)    # ------------------------------------------------------------------- 캔들 시간 조정!!!

        df2 = pyupbit.get_ohlcv(set_ticker, interval=set_interval, count=set_count)
        df2['FastK'] = (df2['close'] - df2['low'].rolling(14).min()) / (df2['high'].rolling(14).max() - df2['low'].rolling(14).min()) * 100
        df2['SlowK'] = df2['FastK'].rolling(5).mean()
        df2['SlowD'] = df2['SlowK'].rolling(3).mean()


        target_price = get_target_price(set_ticker, kk)
        current_price = get_current_price(set_ticker)
        

        if start_time < now < end_time - datetime.timedelta(seconds=5):

            if target_price < current_price:
                if df2['SlowK'].iloc[-1] > df2['SlowD'].iloc[-1]:   # ------------------------------------------------------------------- 스토캐스틱 조건. SlowK 가 D보다 높을때.
                    krw = get_balance("KRW")
                    if krw > 6000:
                        upbit.buy_market_order(set_ticker, krw*0.9995)
        else:
            selling_target_value = pyupbit.get_ohlcv(set_ticker, interval=set_interval, count=3)
            selling_target = (selling_target_value['close'].iloc[0] + selling_target_value['close'].iloc[1]) / 2
            
            if df2['close'].iloc[-1] < selling_target:
                CCoin = get_balance(set_ticker2)
                if CCoin > 0.0001:
                    upbit.sell_market_order(set_ticker, CCoin*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)