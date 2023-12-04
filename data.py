import pandas as pd
import utils
import attribution as attr

#! ---------------------------- Portfolio data functions ----------------------------

def prepare_portfolio_weights(weight_excel):
    portofolio_weights = pd.read_excel(weight_excel)

    # Drop the last row of the dataframe (Total)
    portofolio_weights = portofolio_weights.iloc[:-1]
    portofolio_weights = portofolio_weights.melt(id_vars=['Instrument', 'Instr. Type', 'Sector 1', 'Ccy'], var_name='Date', value_name='Weight')
    
    return portofolio_weights

# Takes an excel file, returns cleaned return data
def prepare_portfolio_returns(return_excel):
    portfolio_returns = pd.read_excel(return_excel)

    # Drop the last row of the dataframe (Total)
    portfolio_returns = portfolio_returns.iloc[:-1]
    portfolio_returns = portfolio_returns.melt(id_vars=['Instrument', 'Instr. Type', 'Sector 1', 'Ccy'], var_name='Date', value_name='Return')
    return portfolio_returns

def combine_portfolio_data(portfolio_weights, portfolio_returns):
    portfolio_df = (pd.merge(portfolio_weights, portfolio_returns, on=['Instrument', 'Instr. Type', 'Sector 1', 'Ccy', 'Date'], how='inner')
                    .rename(columns={'Sector 1': 'GICS Sector'}))
    return portfolio_df

def lag_portfolio_weights(df):
    portfolio_weights = df.groupby('GICS Sector')['Weight'].shift(1)
    
    return calculate_weighted_returns(portfolio_weights)

# Function that turns security level daily returns to GICS Sector level daily returns
def transform_to_sector_level_returns(portfolio_df):
    sector_returns = portfolio_df.groupby(['Date', 'GICS Sector']).sum()

    sector_returns = sector_returns.reset_index()
    sector_returns.drop(columns=['Instrument', 'Instr. Type', 'Ccy'], inplace=True)
    
    return sector_returns

# Function that returns daily sector weights
def calculate_daily_sector_weights(df):
    sector_weights = df.groupby(['Date', 'GICS Sector'])['Weight'].sum()
    sector_weights = sector_weights.reset_index()
    
    return sector_weights

def get_portfolio_data(portfolio_weight_xlsx, portfolio_return_xlsx):
    # Call all the three functions above to get the portfolio data
    portfolio_weights = prepare_portfolio_weights(portfolio_weight_xlsx)
    portfolio_returns = prepare_portfolio_returns(portfolio_return_xlsx)
    portfolio_df = combine_portfolio_data(portfolio_weights, portfolio_returns)
    portfolio_df['Weighted Returns'] = calculate_weighted_returns(portfolio_df)
    
    # Get sector level daily weights
    sector_weights = calculate_daily_sector_weights(portfolio_df)
    portfolio_df = portfolio_df.merge(sector_weights, on=['Date', 'GICS Sector'], how='left', suffixes=('', '_Sector'))
    portfolio_df['Asset Weight in Sector'] = portfolio_df['Weight'] / portfolio_df['Weight_Sector']
    
    # Calculate asset level sector contribution. Turns into sector return during the next step
    portfolio_df['Sector Return'] = portfolio_df['Asset Weight in Sector'] * portfolio_df['Return']
    portfolio_df.drop(columns=['Weight_Sector', 'Asset Weight in Sector'], inplace=True) # Columns no longer needed
    
    portfolio_df = transform_to_sector_level_returns(portfolio_df)
    portfolio_df['Date'] = utils.return_datetime_column(portfolio_df['Date'])
    return portfolio_df

#! ---------------------------- Benchmark data functions ----------------------------

def prepare_benchmark_weights(weight_excel):
    benchmark_weights = pd.read_excel(weight_excel)
    benchmark_weights.rename(columns={benchmark_weights.columns[0]: "GICS Sector"}, inplace=True)
    benchmark_weights = benchmark_weights.melt(id_vars=['GICS Sector'], var_name='Date', value_name='Weight')
    
    return benchmark_weights

def prepare_benchmark_returns(return_excel):
    benchmark_returns = pd.read_excel(return_excel)
    benchmark_returns.rename(columns={benchmark_returns.columns[0]: "GICS Sector"}, inplace=True)
    benchmark_returns = benchmark_returns.iloc[:-1]
    benchmark_returns = benchmark_returns.melt(id_vars=['GICS Sector'], var_name='Date', value_name='Return')
    
    return benchmark_returns

def combine_benchmark_data(benchmark_weights, benchmark_returns):
    benchmark_df = pd.merge(benchmark_weights, benchmark_returns, on=['GICS Sector', 'Date'], how='inner')

    return benchmark_df

def get_benchmark_data(benchmark_weight_xlsx, benchmark_return_xlsx):
    benchmark_weights = prepare_benchmark_weights(benchmark_weight_xlsx)
    benchmark_returns = prepare_benchmark_returns(benchmark_return_xlsx)
    benchmark_df = combine_benchmark_data(benchmark_weights, benchmark_returns)
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

def redistribute_portfolio_returns(df_input):
    df = df_input.copy()

    zero_return_dates = utils.get_zero_return_dates(df)
    
    # Initialize 'Next Active Date' for days with zero benchmark return
    df['Next Active Date'] = None
    for zero_date in zero_return_dates:
        next_date = df[(df['Date'] > zero_date) & (df['Benchmark Return'] != 0)]['Date'].min()
        if pd.notnull(next_date):
            df.loc[df['Date'] == zero_date, 'Next Active Date'] = next_date

    # Initialize a dictionary to store the returns to redistribute
    returns_to_redistribute = {}

    # Collect returns to redistribute for zero benchmark return dates
    for zero_date in zero_return_dates:
        next_active_date = df.loc[df['Date'] == zero_date, 'Next Active Date'].iloc[0]
        if pd.notnull(next_active_date):
            # Loop through the sectors on the zero return date
            for _, row in df[df['Date'] == zero_date].iterrows():
                sector = row['GICS Sector']
                return_to_add = row['Portfolio Return']
                key = (next_active_date, sector)
                returns_to_redistribute[key] = returns_to_redistribute.get(key, 0) + return_to_add

    # Redistribute the collected returns to the next active dates
    for (next_active_date, sector), value_to_add in returns_to_redistribute.items():
        # Add the returns to redistribute to the 'Portfolio Return' on the next active date for the same sector
        df.loc[(df['Date'] == next_active_date) & (df['GICS Sector'] == sector), 'Portfolio Return'] += value_to_add

    df = df.drop('Next Active Date', axis=1)

    return df

def clean_combined_data(df):
    combined_df = redistribute_portfolio_returns(df)
    
    # Drop dates with 0 returns in benchmark
    merged_df = combined_df[~combined_df['Date'].isin(utils.get_zero_return_dates(combined_df))]
    
    # Calculate weighted returns
    merged_df = (merged_df.merge(calculate_daily_total_returns(merged_df), on='Date', how='left', suffixes=('', '_daily_total'))
          .rename(columns={'Portfolio Weighted Returns_daily_total': 'Portfolio Daily Total Return',
                           'Benchmark Weighted Returns_daily_total': 'Benchmark Daily Total Return'}))
    
    merged_df['Total Excess Return'] = calculate_daily_excess_return(merged_df)
    
    merged_df = merged_df.rename(columns={'Sector Return': 'Portfolio Sector Performance', 'Benchmark Return': 'Benchmark Sector Performance'})
    
    return merged_df

def get_attribution_effects(df):
    #! This could be made better, so that it doesn't directly manipulate original df
    df['Allocation Effect'] = attr.calculate_allocation_effect(df)
    df['Selection Effect'] = attr.calculate_selection_effect(df)
    df['Interaction Effect'] = attr.calculate_interaction_effect(df)
    df['Sum of Effects'] = attr.sum_of_effects(df['Allocation Effect'], df['Selection Effect'], df['Interaction Effect'])
    
    return df

def calculate_daily_total_returns(df):
    temp_df = df[['Date', 'Portfolio Weighted Returns', 'Benchmark Weighted Returns']]
    daily_total_returns = temp_df.groupby(['Date']).sum().reset_index()
    
    return daily_total_returns

# Lagging benchmarkweights and calculating weighted returns
def lag_benchmark_weights(df):
    benchmark_weights = df.groupby('GICS Sector')['Benchmark Weight'].shift(1)
    
    return calculate_weighted_returns(benchmark_weights)

def calculate_weighted_returns(portfolio_df):
    return portfolio_df['Weight'] * portfolio_df['Return']

def calculate_daily_excess_return(df):
    return df['Portfolio Daily Total Return'] - df['Benchmark Daily Total Return']

#! ---------------------------- Function that gets called from app.py, returns basic form of data ----------------------------

def get_data(portfolio_weight_xlsx, portfolio_return_xlsx, benchmark_weight_xlsx, benchmark_return_xlsx):
    # Returns two dataframes, one for sector level data and one for daily level data
    
    portfolio_df = get_portfolio_data(portfolio_weight_xlsx, portfolio_return_xlsx)
    benchmark_df = get_benchmark_data(benchmark_weight_xlsx, benchmark_return_xlsx)

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
                                    'Interaction Effect', 
                                    'Sum of Effects']].groupby('Date').sum()
    
    daily_level_data['Excess Return'] = daily_level_data['Portfolio Weighted Returns'] - daily_level_data['Benchmark Weighted Returns']

    return combined_df, daily_level_data