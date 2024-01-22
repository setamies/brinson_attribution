import datetime as dt
import pandas as pd
import numpy as np
import io

def return_datetime_column(df_series):
    # Turn the df_series into a datetime 
    # The format '%d.%m.%Y' matches the date format 'day.month.year'
    df_series = pd.to_datetime(df_series, format='%d.%m.%Y')
    return df_series

def calculate_compounded_change(series_from_df):
    return np.exp(np.log(1 + series_from_df).cumsum()) - 1

def to_excel_download(dataframe, sheet_name='Sheet1'):
    """
    Converts a dataframe to an Excel file in memory and returns the bytes.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, sheet_name=sheet_name, index=True)
    return output.getvalue()

def filter_data_by_dates(df, dates):
    # Ensure that 'dates' is a list of pandas Timestamps
    start_date, end_date = pd.to_datetime(dates[0]), pd.to_datetime(dates[1])
    
    df['Date'] = pd.to_datetime(df['Date'])

    df_filtered = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    return df_filtered
