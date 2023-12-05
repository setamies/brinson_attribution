import numpy as np
import pandas as pd

def calculate_allocation_effect(df):
    return (df['Portfolio Weight'] - df['Benchmark Weight']) * (df['Benchmark Sector Performance'] - df['Benchmark Daily Total Return'])

def calculate_selection_effect(df):
    return df['Benchmark Weight'] * (df['Portfolio Sector Performance'] - df['Benchmark Sector Performance']) 

def calculate_interaction_effect(df):
    return (df['Portfolio Weight'] - df['Benchmark Weight']) * (df['Portfolio Sector Performance'] - df['Benchmark Sector Performance'])

def sum_of_effects(allocation, selection, interaction):
    return allocation + selection + interaction