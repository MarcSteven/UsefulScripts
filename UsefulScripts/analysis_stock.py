import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def analyze_buy_points(ticker, period='1y'):
    """
    多维度股票买点分析工具
    参数：
        ticker: 股票代码（如'AAPL'）
        period: 数据周期（默认1年）
    返回：
        包含买点标记的DataFrame
        可视化图表
    """
    # 获取数据
    data = yf.download(ticker, period=period)
    if data.empty:
        raise ValueError(f"无法获取 {ticker} 数据，请检查代码是否正确")

    # 计算技术指标
    data = calculate_indicators(data)
    
    # 识别买点
    data = identify_buy_signals(data)
    
    # 可视化
    plot_signals(data, ticker)
    
    return data

def calculate_indicators(df):
    """计算关键技术指标"""
    # 趋势指标
    df['ema_20'] = ta.trend.EMAIndicator(df['Close'], window=20).ema_indicator()
    df['ema_50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
    df['macd'] = ta.trend.MACD(df['Close']).macd()
    df['macd_signal'] = ta.trend.MACD(df['Close']).macd_signal()
    
    # 动量指标
    df['rsi'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['stoch_k'] = ta.momentum.StochasticOscillator(
        df['High'], df['Low'], df['Close'], window=14).stoch()
    
    # 量价指标
    df['obv'] = ta.volume.OnBalanceVolumeIndicator(
        df['Close'], df['Volume']).on_balance_volume()
    df['vwap'] = ta.volume.VolumeWeightedAveragePrice(
        df['High'], df['Low'], df['Close'], df['Volume']).volume_weighted_average_price()
    
    # 波动率指标
    df['atr'] = ta.volatility.AverageTrueRange(
        df['High'], df['Low'], df['Close'], window=14).average_true_range()
    
    return df

def identify_buy_signals(df):
    """识别7种经典买点"""
    df['buy_signal'] = 0
    
    # 1. 金叉策略
    df.loc[(df['ema_20'] > df['ema_50']) & 
           (df['ema_20'].shift(1) <= df['ema_50'].shift(1)), 'buy_signal'] = 1
    
    # 2. MACD零上金叉
    df.loc[(df['macd'] > df['macd_signal']) & 
           (df['macd'].shift(1) <= df['macd_signal'].shift(1)) & 
           (df['macd'] > 0), 'buy_signal'] = 2
    
    # 3. RSI超卖反弹
    df.loc[(df['rsi'] < 30) & 
           (df['rsi'].shift(1) < df['rsi']), 'buy_signal'] = 3
    
    # 4. 放量突破VWAP
    df.loc[(df['Close'] > df['vwap']) & 
           (df['Volume'] > 1.5 * df['Volume'].rolling(20).mean()), 'buy_signal'] = 4
    
    # 5. 布林带下轨反弹
    bollinger = ta.volatility.BollingerBands(df['Close'])
    df['lower_band'] = bollinger.bollinger_lband()
    df.loc[(df['Close'] <= df['lower_band']) & 
           (df['Close'].shift(1) > df['lower_band'].shift(1)), 'buy_signal'] = 5
    
    # 6. 缩量回踩EMA50
    df.loc[(abs(df['Close'] - df['ema_50']) / df['ema_50'] < 0.02) & 
           (df['Volume'] < 0.8 * df['Volume'].rolling(20).mean()), 'buy_signal'] = 6
    
    # 7. 口袋支点（机构买点）
    df.loc[(df['Close'] > df['High'].shift(1)) & 
           (df['Volume'] > df['Volume'].rolling(50).mean()), 'buy_signal'] = 7
    
    return df

def plot_signals(df, ticker):
    """可视化买点"""
    plt.figure(figsize=(16, 10))
    
    # 绘制价格和均线
    plt.plot(df.index, df['Close'], label='Close', color='black', alpha=0.8)
    plt.plot(df.index, df['ema_20'], label='EMA 20', color='blue', linestyle='--')
    plt.plot(df.index, df['ema_50'], label='EMA 50', color='red', linestyle='--')
    
    # 标记买点
    signals = df[df['buy_signal'] > 0]
    colors = {1:'gold', 2:'cyan', 3:'lime', 4:'orange', 5:'pink', 6:'purple', 7:'red'}
    
    for signal_type, color in colors.items():
        points = signals[signals['buy_signal'] == signal_type]
        plt.scatter(points.index, points['Close'], color=color, 
                   label=f'Buy {signal_type}', s=100, marker='^')
    
    plt.title(f'{ticker} 买点分析 (EMA20:蓝, EMA50:红)')
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    stock = input("请输入股票代码(如AAPL): ").upper()
    try:
        result = analyze_buy_points(stock)
        print("\n最近5个买点出现日期:")
        print(result[result['buy_signal'] > 0].tail(5)[['Close', 'buy_signal']])
        
        print("\n买点类型说明:")
        print("1:EMA金叉 2:MACD金叉 3:RSI超卖 4:放量突破VWAP")
        print("5:布林下轨 6:缩量回踩EMA50 7:口袋支点")
    except Exception as e:
        print(f"分析出错: {e}")