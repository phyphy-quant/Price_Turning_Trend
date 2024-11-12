import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from fetch_kline import fetch_kline_price_data
from get_direction import get_direction
from backtesting import backtesting
from plot_chart import plot_chart
from plot_daily_pnl import plot_daily_pnl
from process_results import process_results
from calc_metrics import calc_metrics

if __name__=='__main__':

    ticker = 'BTCUSDT'
    time_interval = '15m'
    start_date = '2024-06-08'
    end_date = '2024-09-04'
    filename = f'BTCUSDT_historical_data_{start_date}_to_{end_date}.csv'
    turning_pct = 0.05
    atr_mode = True
    chart_type = 'OHLC'
    start_filter_date = '2024-06-08 16:00:00'
    end_filter_date = '2024-09-04 00:00:00'
    # 爬取數據
    # df = fetch_kline_price_data(ticker=ticker, time_interval=time_interval, start_date=start_date, filename=filename)

    #讀取csv file
    df = pd.read_csv('BTCUSDT_historical_from_outsample.csv')

    # 過濾數據
    df['date'] = pd.to_datetime(df['Open time'])
    df = df[(df['date'] >= start_filter_date) & (df['date'] < end_filter_date)]
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'atr']
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    df = df[df['atr'].notna()]
    # 以3倍atr為基準
    df['atr'] = df['atr'] * 3
    df = df.reset_index(drop=True)
    # print(df.head(100))

    # 計算方向
    df, tops, bottoms = get_direction(df, turning_pct, atr_mode, chart_type)
    directions = df['direction']
    # print(df.head(100))

    # 執行回測
    df, balance = backtesting(df, directions, turning_pct, atr_mode, chart_type)

    # DataFrame 做四捨五入
    df = df.round(2)
    print("Final Balance:", balance)
    print(df.head(500))


    # 處理數據
    processed_df = process_results(df)

    #保存成csv
    processed_df.to_csv('transaction_outsample_details_BTCUSDT.csv', index = False)

    # 策略分析
    metrics_df = calc_metrics(processed_df)
    print(metrics_df)
    print(processed_df.head(100))

    # # 繪製 Balance Growth 圖表
    # fig1, ax = plot_chart(processed_df)
    # plt.show()

    # 測試 處理 Daily 柱狀圖數據
    exit_list = df[['date', 'entry price', 'signal', 'exit price', 'PnL']]
    exit_list2 = pd.DataFrame(exit_list)

    exit_list2.to_csv('results.csv', index=False)

    print("Exit list saved to 'exit_list2_results.csv'")

    results = pd.read_csv('results.csv')
    # 將 'date' 列轉換為日期時間格式
    results['date'] = pd.to_datetime(results['date'])
    # 按日期分組並計算每日的盈虧總和
    daily_pnl = results.groupby(results['date'].dt.date)['PnL'].sum().reset_index()
    # 重命名列
    daily_pnl.columns = ['date', 'net_PnL']
    # 過濾掉淨盈虧為 0 的行
    daily_pnl = daily_pnl[daily_pnl['net_PnL'] != 0]

    # 新的 DataFrame
    new_daily_df = pd.DataFrame(daily_pnl)
    print(new_daily_df.head(100))

    # 繪製 Balance Growth 圖表
    fig1, ax = plot_chart(processed_df)
    # plt.show()

    # 繪製 daily PnL Figure
    # 繪製圖表
    fig2 = plot_daily_pnl(daily_pnl)
    print("Plot generated successfully.")
    plt.show()