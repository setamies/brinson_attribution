import pandas as pd
import utils
import attribution as attr

#! ---------------------------- Portfolio data functions ----------------------------

def prepare_portfolio_weights(performance_data):
    portfolio_weights = pd.read_excel(performance_data, sheet_name="Portfolio Weights")

    # Transpose the data frame and reset the index
    df_transposed = portfolio_weights.set_index('Instrument').T
    df_transposed.reset_index(inplace=True)
    df_transposed.rename(columns={df_transposed.columns[0]: "Instrument"}, inplace=True)

    # Remove the last row of the data frame
    df_transposed = df_transposed.iloc[:-1]

    # Reshape the data frame
    portofolio_weights = df_transposed.melt(id_vars=['Instrument', 'Instr. Type', 'Sector 1', 'Ccy'], var_name='Date', value_name='Weight')
    portofolio_weights['Date'] = pd.to_datetime(portofolio_weights['Date'], format='%d.%m.%Y')

    return portofolio_weights

def prepare_portfolio_returns(performance_data): 
    portfolio_returns = pd.read_excel(performance_data, sheet_name="Portfolio Returns")

    df_transposed = portfolio_returns.set_index('Instrument').T
    df_transposed.reset_index(inplace=True)
    df_transposed.rename(columns={df_transposed.columns[0]: "Instrument"}, inplace=True)
    df_transposed = df_transposed.iloc[:-1]
    return_df = df_transposed.melt(id_vars=['Instrument', 'Instr. Type', 'Sector 1', 'Ccy'], var_name='Date', value_name='Return')
    return_df['Date'] = pd.to_datetime(return_df['Date'], format='%d.%m.%Y')

    return return_df

def combine_portfolio_data(portfolio_weights, portfolio_returns):
    portfolio_df = (pd.merge(portfolio_weights, portfolio_returns, on=['Instrument', 'Instr. Type', 'Sector 1', 'Ccy', 'Date'], how='inner')
                    .rename(columns={'Sector 1': 'GICS Sector'}))
    
    return portfolio_df

def lag_portfolio_weights(df):
    # Lag the portfolio weights by one day for each instrument
    df['Weight'] = df.groupby('Instrument')['Weight'].shift(1)
    return df

# Function that turns security level daily returns to GICS Sector level daily returns
def transform_to_sector_level_returns(portfolio_df):
    portfolio_df.drop(columns=['Instrument', 'Instr. Type', 'Ccy'], inplace=True)
    sector_returns = portfolio_df.groupby(['Date', 'GICS Sector']).sum()
    sector_returns = sector_returns.reset_index()

    return sector_returns

# Function that returns daily sector weights
def calculate_daily_sector_weights(df):
    sector_weights = df.groupby(['Date', 'GICS Sector'])['Weight'].sum()
    sector_weights = sector_weights.reset_index()

    return sector_weights

def handle_multi_industry_assets(portfolio_df, performance_data, benchmark_df):
    # Prepare multi_ind dataframe
    multi_ind_df = pd.read_excel(performance_data, sheet_name="Multi-Industry Weights")
    multi_ind_df.rename(columns={multi_ind_df.columns[0]: "Instrument"}, inplace=True)
    multi_ind_df = multi_ind_df.melt(id_vars=['Instrument'], var_name='GICS Sector', value_name='BM Weight')
    # Create new column that connects Instrument and GICS Sector columns
    multi_ind_df['Instrument_GICS'] = multi_ind_df['Instrument'] + ' - ' + multi_ind_df['GICS Sector']

    multi_ind_df = multi_ind_df.merge(portfolio_df, on=['Instrument'], how='inner', suffixes=('', '_Portfolio'))
    multi_ind_df['New Weights'] = multi_ind_df['Weight'] * multi_ind_df['BM Weight']

    # Store the original instrument names to be deleted later
    original_instruments = multi_ind_df['Instrument'].unique()

    # Drop unecessary columns
    multi_ind_df.drop(columns=['Instrument', 'BM Weight', 'Weight', 'Return', 'GICS Sector_Portfolio'], inplace=True)
    multi_ind_df = multi_ind_df.merge(benchmark_df, on=['Date', 'GICS Sector'], how='inner')
    multi_ind_df = (multi_ind_df.drop(columns=['Weight', 'Weighted Returns'])
                 .rename(columns={'New Weights': 'Weight', 'Instrument_GICS':'Instrument'}))

    # Delete the original tickers from portfolio_df and then concat multi_ind_df to it
    portfolio_df = portfolio_df[portfolio_df['Instrument'].isin(original_instruments) == False]
    new_portfolio_df = pd.concat([portfolio_df, multi_ind_df]).sort_values(by=['Date', 'GICS Sector'], ignore_index=True)

    return new_portfolio_df

def get_portfolio_data(performance_data, benchmark_df):
    # Call all the three functions above to get the portfolio data
    portfolio_weights = prepare_portfolio_weights(performance_data)
    portfolio_returns = prepare_portfolio_returns(performance_data)
    portfolio_df = combine_portfolio_data(portfolio_weights, portfolio_returns)    

    # Handle multi-industry weights
    portfolio_df = handle_multi_industry_assets(portfolio_df, performance_data, benchmark_df)

    portfolio_df = lag_portfolio_weights(portfolio_df)    
    portfolio_df['Weighted Returns'] = calculate_weighted_returns(portfolio_df)
    
    # Get sector level daily weights
    sector_weights = calculate_daily_sector_weights(portfolio_df)
    portfolio_df = portfolio_df.merge(sector_weights, on=['Date', 'GICS Sector'], how='left', suffixes=('', '_Sector'))

    # Drop rows where Weight_Sector is 0
    portfolio_df = portfolio_df[portfolio_df['Weight_Sector'] != 0]
    portfolio_df['Asset Weight in Sector'] = portfolio_df['Weight'] / portfolio_df['Weight_Sector']

    # Calculate asset level sector contribution. Turns into sector return during the next step
    portfolio_df['Sector Return'] = portfolio_df['Asset Weight in Sector'] * portfolio_df['Return']
    portfolio_df.drop(columns=['Weight_Sector', 'Asset Weight in Sector'], inplace=True) # Columns no longer needed

    portfolio_df = transform_to_sector_level_returns(portfolio_df)
    portfolio_df['Date'] = utils.return_datetime_column(portfolio_df['Date'])

    return portfolio_df

#! ---------------------------- Benchmark data functions ----------------------------

def prepare_benchmark_weights(performance_data):
    benchmark_weights = pd.read_excel(performance_data, sheet_name="Benchmark Weights")
    benchmark_weights.rename(columns={benchmark_weights.columns[0]: "Date"}, inplace=True)
    benchmark_weights = benchmark_weights.melt(id_vars=['Date'], var_name=['GICS Sector'], value_name='Weight')

    benchmark_weights['Date'] = pd.to_datetime(benchmark_weights['Date'], format='%d.%m.%Y')

    return benchmark_weights    

def prepare_benchmark_returns(performance_data): 
    benchmark_returns = pd.read_excel(performance_data, sheet_name="Benchmark Returns")
    benchmark_returns.rename(columns={benchmark_returns.columns[0]: "Date"}, inplace=True)

    benchmark_returns = benchmark_returns.melt(id_vars=['Date'], var_name=['GICS Sector'],value_name='Return')
    benchmark_returns['Date'] = pd.to_datetime(benchmark_returns['Date'], format='%d.%m.%Y')
    return benchmark_returns

# Lagging benchmarkweights and calculating weighted returns
def lag_benchmark_weights(df): 
    df['Weight'] = df.groupby('GICS Sector')['Weight'].shift(1)

    return df

def combine_benchmark_data(benchmark_weights, benchmark_returns):
    benchmark_df = pd.merge(benchmark_weights, benchmark_returns, on=['GICS Sector', 'Date'], how='inner')

    return benchmark_df

def get_benchmark_data(performance_data):
    benchmark_weights = prepare_benchmark_weights(performance_data)
    benchmark_returns = prepare_benchmark_returns(performance_data)
    
    benchmark_df = combine_benchmark_data(benchmark_weights, benchmark_returns)
        
    benchmark_df = lag_benchmark_weights(benchmark_df)
    benchmark_df['Weighted Returns'] = calculate_weighted_returns(benchmark_df)
    benchmark_df['Date'] = utils.return_datetime_column(benchmark_df['Date'])

    return benchmark_df

#! ---------------------------- Combined data functions ----------------------------

def combine_portfolio_and_benchmark_data(portfolio_df, benchmark_df):
    combined_df = (portfolio_df.merge(benchmark_df, on=['Date', 'GICS Sector'], how='outer', suffixes=('_Portfolio', '_Benchmark'))
                   .sort_values(by=['Date', 'GICS Sector'], ignore_index=True)
                    .fillna(0)
                    .rename(columns={'Weight_Portfolio': 'Portfolio Weight',
                                    'Weight_Benchmark': 'Benchmark Weight',
                                    'Return_Portfolio': 'Portfolio Return',
                                    'Return_Benchmark': 'Benchmark Return',
                                    'Weighted Returns_Portfolio': 'Portfolio Weighted Returns',
                                    'Weighted Returns_Benchmark': 'Benchmark Weighted Returns'}))
    return combined_df

def clean_combined_data(df):

    # Calculate weighted returns
    merged_df = (df.merge(calculate_daily_total_returns(df), on='Date', how='left', suffixes=('', '_daily_total'))
          .rename(columns={'Portfolio Weighted Returns_daily_total': 'Portfolio Daily Total Return',
                           'Benchmark Weighted Returns_daily_total': 'Benchmark Daily Total Return'}))

    merged_df['Total Excess Return'] = calculate_daily_excess_return(merged_df)

    merged_df = merged_df.rename(columns={'Sector Return': 'Portfolio Sector Performance', 'Benchmark Return': 'Benchmark Sector Performance'})

    return merged_df

def get_attribution_effects(df):
    #! Include interaction effect if you opt to use it. Also include it in sum of effects
    df['Allocation Effect'] = attr.calculate_allocation_effect(df)
    df['Selection Effect'] = attr.calculate_selection_effect(df)
    # df['Interaction Effect'] = attr.calculate_interaction_effect(df)
    df['Sum of Effects'] = attr.sum_of_effects(df['Allocation Effect'], df['Selection Effect'])

    return df

def calculate_daily_total_returns(df):
    temp_df = df[['Date', 'Portfolio Weighted Returns', 'Benchmark Weighted Returns']]
    daily_total_returns = temp_df.groupby(['Date']).sum().reset_index()

    return daily_total_returns

def calculate_weighted_returns(portfolio_df):
    return portfolio_df['Weight'] * portfolio_df['Return']

def calculate_daily_excess_return(df):
    return df['Portfolio Daily Total Return'] - df['Benchmark Daily Total Return']

#! ---------------------------- Function that gets called from app.py, returns basic form of data ----------------------------

def get_data(performance_data):
    # Read all the different sheets in xlsx and create unique dataframes from each
    
    benchmark_df = get_benchmark_data(performance_data)
    portfolio_df = get_portfolio_data(performance_data, benchmark_df)

    combined_df = combine_portfolio_and_benchmark_data(portfolio_df, benchmark_df)
    combined_df = clean_combined_data(combined_df)

    combined_df = get_attribution_effects(combined_df)

    # Daily level
    daily_level_data = combined_df[['Date', 
                                    'Portfolio Weight', 
                                    'Benchmark Weight', 
                                    'Portfolio Weighted Returns', 
                                    'Benchmark Weighted Returns', 
                                    'Allocation Effect', 
                                    'Selection Effect', 
                                    'Sum of Effects']].groupby('Date').sum()

    daily_level_data['Excess Return'] = daily_level_data['Portfolio Weighted Returns'] - daily_level_data['Benchmark Weighted Returns']

    return combined_df, daily_level_data