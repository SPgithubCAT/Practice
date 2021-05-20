import time
import pyupbit
import datetime
import numpy as np

access = "YdCCrkQhmfJVMa9MvF2yOO8R217dlPmwjjWST3xm"
secret = "lynjwDcZXPZ98FmfgBPuwwcGfUQWzLBBqIPxXKMO"

set_ticker = "ADA"

set_time = "minute"
set_time_num = 5       # ------------------------------------------------------------------------------------------------------------ default and end time
set_count = 100
kk = 0.4

selling_time = 10 # seconds

stoch_lenth = 11
stoch_k = 5
stoch_d = 5

ma_switch = 1  # on:1, off:0
set_ma_count = 21

set_interval = set_time + str(set_time_num)

selling_version = 2 # normal:1, -1%ma2:2

rsi_ma = 14

#    """변동성 돌파 전략으로 매수 목표가 조회"""
def get_target_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker, interval=set_interval, count=2) # ---------------------------------------------------------------- 숫자 2로 고정. 바로 전 캔들 기준.
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

#    """시작 시간 조회"""
def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval=set_interval, count=1)
    start_time = df.index[0]
    return start_time

#    """잔고 조회"""
def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

#    """현재가 조회"""
def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

#    """이동 평균선 조회"""
def get_ma(ticker):
    df = pyupbit.get_ohlcv(ticker, interval=set_interval, count=set_ma_count)
    ma = df['low'].rolling(set_ma_count).mean().iloc[-1]
    return ma


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:

        df2 = pyupbit.get_ohlcv("KRW-"+set_ticker, interval=set_interval, count=set_count)
        df2['FastK'] = (df2['close'] - df2['low'].rolling(stoch_lenth).min()) / (df2['high'].rolling(stoch_lenth).max() - df2['low'].rolling(stoch_lenth).min()) * 100
        df2['SlowK'] = df2['FastK'].rolling(stoch_k).mean()
        df2['SlowD'] = df2['SlowK'].rolling(stoch_d).mean()

        df3 = pyupbit.get_ohlcv("KRW-"+set_ticker, interval=set_interval, count=set_count)
        df3['U'] = np.where(df3['close'].diff(1) > 0, df3['close'].diff(1), 0)
        df3['D'] = np.where(df3['close'].diff(1) < 0, (df3['close'].diff(1) * (-1)), 0)
        df3['AU'] = df3['U'].rolling(rsi_ma).mean()
        df3['AD'] = df3['D'].rolling(rsi_ma).mean()
        rsi_au = df3['AU']
        rsi_ad = df3['AD']
        rsi = (rsi_au / (rsi_au + rsi_ad))
        set_rsi = rsi.iloc[-1]

        # ma terms
        ma = get_ma("KRW-"+set_ticker)
        current_price = get_current_price("KRW-"+set_ticker)

        now = datetime.datetime.now()
        start_time = get_start_time("KRW-"+set_ticker)
        end_time = start_time + datetime.timedelta(minutes=set_time_num)    # --------------------------------- selling time

        target_price = get_target_price("KRW-"+set_ticker, kk)

        if ma_switch == 1 and  current_price > ma: # ------------------------------------------------------ ma
            if start_time < now < end_time - datetime.timedelta(seconds=selling_time):
                if target_price < current_price: # ---------------------------------------------------------------- target price
                    if df2['SlowK'].iloc[-1] > df2['SlowD'].iloc[-1]:   # ----------------------------------------- stochastic terms - SlowK > D
                        if df2['SlowK'].iloc[-1] < 80: # ---------------------------------------------------------- K가 80이하. 손해 줄이기 위함. 이익도 줄어 들 수 있음.
                            krw = get_balance("KRW")
                            if krw > 6000:
                                upbit.buy_market_order("KRW-"+set_ticker, krw*0.9995)
            else:
                if set_rsi > 0.75:      # ------------------------------------------------------------------------------------------- RSI 0.75 이상일때 무조건 팔기.
                    CCoin = get_balance(set_ticker)
                    if CCoin > 0.0001:
                        upbit.sell_market_order("KRW-"+set_ticker, CCoin*0.9995)                        
                if selling_version == 1:
                    CCoin = get_balance(set_ticker)
                    if CCoin > 0.0001:
                        upbit.sell_market_order("KRW-"+set_ticker, CCoin*0.9995)
                if selling_version == 2:
                    if current_price < df2['close'].iloc[-2] - (df2['close'].iloc[-2] * 0.01): # ----------------------------------------- 💥 -0.1% 기준. 10분봉일경우. 분봉이 길경우 더 높게 설정할 필요가 있음.
                        CCoin = get_balance(set_ticker)
                        if CCoin > 0.0001:
                            upbit.sell_market_order("KRW-"+set_ticker, CCoin*0.9995)
                    else:
                        selling_target_value = pyupbit.get_ohlcv("KRW-"+set_ticker, interval=set_interval, count=3)
                        selling_target = (selling_target_value['close'].iloc[0] + selling_target_value['close'].iloc[1]) / 2
                        
                        if df2['close'].iloc[-1] < selling_target:
                            CCoin = get_balance(set_ticker)
                            if CCoin > 0.0001:
                                upbit.sell_market_order("KRW-"+set_ticker, CCoin*0.9995)
            time.sleep(1)

        else :
            if start_time < now < end_time - datetime.timedelta(seconds=selling_time):
                if target_price < current_price:
                    if df2['SlowK'].iloc[-1] > df2['SlowD'].iloc[-1]:   # ------------------------------------------------------------------- 스토캐스틱 조건. SlowK 가 D보다 높을때.
                        if df2['SlowK'].iloc[-1] < 80: # ------------------------------------------------------------------- K가 80이하. 손해 줄이기 위함. 이익도 줄어 들 수 있음.
                            krw = get_balance("KRW")
                            if krw > 6000:
                                upbit.buy_market_order("KRW-"+set_ticker, krw*0.9995)

            else:
                if set_rsi > 0.75: # ------------------------------------------------------------------------------------------- RSI 0.75 이상일때 무조건 팔기.
                    CCoin = get_balance(set_ticker)
                    if CCoin > 0.0001:
                        upbit.sell_market_order("KRW-"+set_ticker, CCoin*0.9995)      
                if selling_version == 1:
                    CCoin = get_balance(set_ticker)
                    if CCoin > 0.0001:
                        upbit.sell_market_order("KRW-"+set_ticker, CCoin*0.9995)
                if selling_version == 2:
                    if current_price < df2['close'].iloc[-2] - (df2['close'].iloc[-2] * 0.01): # ----------------------------------------- 💥 -0.1% 기준. 10분봉일경우. 분봉이 길경우 더 높게 설정할 필요가 있음.
                        CCoin = get_balance(set_ticker)
                        if CCoin > 0.0001:
                            upbit.sell_market_order("KRW-"+set_ticker, CCoin*0.9995)
                    else:
                        selling_target_value = pyupbit.get_ohlcv("KRW-"+set_ticker, interval=set_interval, count=3)
                        selling_target = (selling_target_value['close'].iloc[0] + selling_target_value['close'].iloc[1]) / 2
                        
                        if df2['close'].iloc[-1] < selling_target:
                            CCoin = get_balance(set_ticker)
                            if CCoin > 0.0001:
                                upbit.sell_market_order("KRW-"+set_ticker, CCoin*0.9995)
            time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)
