import numpy as np
import pandas as pd

def calculate_allocation_effect(df):
    return (df['Portfolio Weight'] - df['Benchmark Weight']) * (df['Benchmark Sector Performance'] - df['Benchmark Daily Total Return'])

def calculate_selection_effect(df):
    return df['Portfolio Weight'] * (df['Portfolio Sector Performance'] - df['Benchmark Sector Performance']) 
    # If you want to include interaction effect, use the line below
    # return df['Benchmark Weight'] * (df['Portfolio Sector Performance'] - df['Benchmark Sector Performance'])

# def calculate_interaction_effect(df):
#    return 0
    # If you want to calculate interaction effect, use the line below
    # return (df['Benchmark Weight'] - df['Benchmark Weight']) * (df['Portfolio Sector Performance'] - df['Benchmark Sector Performance'])

# Include interaction effect if you opt to use it.
def sum_of_effects(allocation, selection):
    return allocation + selection

def carino_scaling_coefficient(df):

    dividend = (np.log(1 + df['Portfolio Weighted Returns']) - np.log(1 + df['Benchmark Weighted Returns'])) / (df['Portfolio Weighted Returns'] - df['Benchmark Weighted Returns'])
    divisor = (np.log(1 + df['Portfolio Weighted Returns'].iloc[-1]) - np.log(1 + df['Benchmark Weighted Returns'].iloc[-1])) / (df['Portfolio Weighted Returns'].iloc[-1] - df['Benchmark Weighted Returns'].iloc[-1])
    return dividend / divisor