import pandas as pd
import numpy as np
import utils

# Function that returns daily compounded returns 
def daily_compounded_returns(daily_data):
    # calculate the daily compounded returns for the portfolio and benchmark
    p_comp_returns = utils.calculate_compounded_change(daily_data['Portfolio Weighted Returns'])
    b_comp_returns = utils.calculate_compounded_change(daily_data['Benchmark Weighted Returns'])
    
    # Return as a separate dataframe with the same index as the daily_data dataframe
    comp_returns = pd.DataFrame({'Portfolio Compounded Returns': p_comp_returns, 'Benchmark Compounded Returns': b_comp_returns}, index=daily_data.index)
    
    # Make both start from 0. 
    comp_returns = comp_returns - comp_returns.iloc[0]
    
    return comp_returns

def average_sector_weights(sector_level_data):
    # Calculate the average sector weights for the portfolio and benchmark
    p_avg_sector_weights = sector_level_data.groupby('GICS Sector')['Portfolio Weight'].mean()
    b_avg_sector_weights = sector_level_data.groupby('GICS Sector')['Benchmark Weight'].mean()
    
    # Return as a separate dataframe
    avg_sector_weights = pd.DataFrame({'Portfolio Average Sector Weight': p_avg_sector_weights, 'Benchmark Average Sector Weight': b_avg_sector_weights})
    
    return avg_sector_weights

def get_last_compounded_effects(df, effect_column):
    last_effects = {}
    for sector in df['GICS Sector'].unique():
        sector_df = df[df['GICS Sector'] == sector]
        last_effects[sector] = (1 + sector_df[effect_column]).cumprod().iloc[-1] - 1
    return last_effects

def get_compounded_sector_effects(df):
    # Manually calculate the last compounded effect for each sector
    allocation_last = get_last_compounded_effects(df, 'Allocation Effect')
    selection_last = get_last_compounded_effects(df, 'Selection Effect')
    interaction_last = get_last_compounded_effects(df, 'Interaction Effect')

    # Combine the results into a single DataFrame
    results_df = pd.DataFrame({
        'GICS Sector': allocation_last.keys(),
        'Allocation Effect': allocation_last.values(),
        'Selection Effect': selection_last.values(),
        'Interaction Effect': interaction_last.values()
    })

    return results_df

def compounded_allocation_effects(df):
    # Make sure the date index is sorted
    df = df.sort_index()

    allocation_effects = utils.calculate_compounded_change(df['Allocation Effect'])
    selection_effects = utils.calculate_compounded_change(df['Selection Effect'])
    interaction_effects = utils.calculate_compounded_change(df['Interaction Effect'])
    excess_returns = utils.calculate_compounded_change(df['Excess Return'])

    # Combine the results into a single DataFrame, same index as in df
    results_df = pd.DataFrame({
        'Allocation Effect': allocation_effects,
        'Selection Effect': selection_effects,
        'Interaction Effect': interaction_effects,
        'Excess Returns': excess_returns
    }, index=df.index)

    # Make all start from 0
    results_df = results_df - results_df.iloc[0]

    return results_df