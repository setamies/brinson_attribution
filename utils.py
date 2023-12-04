import datetime as dt
import pandas as pd
import numpy as np

def return_datetime_column(df_series):
    # Turn the df_series into a datetime 
    # The format '%d.%m.%Y' matches the date format 'day.month.year'
    df_series = pd.to_datetime(df_series, format='%d.%m.%Y')
    return df_series

def get_zero_return_dates(df):
    # Calculate daily benchmark total and identify zero return dates
    daily_benchmark_total = df.groupby('Date')['Benchmark Return'].sum()
    zero_return_dates = daily_benchmark_total[daily_benchmark_total == 0].index
    return zero_return_dates

def calculate_compounded_change(series_from_df):
    return np.exp(np.log(series_from_df + 1).cumsum()) - 1