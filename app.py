import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import visualizations as viz
import data as data
import visualization_data as viz_data
import plotly.graph_objects as go


# App configuration
st.set_page_config(layout='wide', page_title='Portfolio Attribution App', initial_sidebar_state='collapsed')

# Title and description
st.title('Portfolio Attribution Analysis')
st.markdown("""
    This app performs portfolio attribution analysis, comparing portfolio performance against a benchmark.
    Upload the relevant Excel files to the fields in the side bar to get started.
""")

# Sidebar for file upload
with st.sidebar:
    st.header('Upload Data Files')
    portfolio_weight_xlsx = st.file_uploader("Portfolio Weights", type=['xlsx'], key="portfolio_weight")
    portfolio_return_xlsx = st.file_uploader("Portfolio Returns", type=['xlsx'], key="portfolio_return")
    benchmark_weight_xlsx = st.file_uploader("Benchmark Weights", type=['xlsx'], key="benchmark_weight")
    benchmark_return_xlsx = st.file_uploader("Benchmark Returns", type=['xlsx'], key="benchmark_return")

# Check if all file uploaders have a file uploaded
all_files = [portfolio_weight_xlsx, portfolio_return_xlsx, benchmark_weight_xlsx, benchmark_return_xlsx]
if all(file is not None for file in all_files):
    # Fetch sector and daily level data
    combined_df, daily_level_data = data.get_data(portfolio_weight_xlsx, portfolio_return_xlsx, benchmark_weight_xlsx, benchmark_return_xlsx)
    
    # Main content
    st.header("Analysis Results")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Compounded Returns")
        st.plotly_chart(viz.plot_daily_compounded_returns(viz_data.daily_compounded_returns(daily_level_data)), use_container_width=True)

    with col2:
        st.subheader("Attribution Effects")
        st.plotly_chart(viz.plot_allocation_effects_per_sector(viz_data.get_compounded_sector_effects(combined_df)), use_container_width=True)

    st.header("Sector Weights Comparison")
    st.plotly_chart(viz.plot_sector_weights_comparison(viz_data.average_sector_weights(combined_df)), use_container_width=True)

    st.header("Historical Attribution")
    st.plotly_chart(viz.plot_attribution_effects(viz_data.compounded_allocation_effects(daily_level_data)), use_container_width=True)
else:
    st.info("Please upload all required files to proceed with the analysis.")

# Footer or additional information
st.markdown("---")
st.markdown("© 2023 Portfolio Attribution Analysis App")
