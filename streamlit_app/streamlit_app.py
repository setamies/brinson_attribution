import streamlit as st
import pandas as pd
import numpy as np
import visualizations as viz
import data as data
import visualization_data as viz_data
import utils

import pyodide_http # https://github.com/whitphx/stlite/blob/main/packages/desktop/README.md
pyodide_http.patch_all()


def main():
    #! App configuration
    st.set_page_config(layout='wide', page_title='Portfolio Attribution App', initial_sidebar_state='expanded')

    # Show the description of the app before any the file has been uploaded
    if 'performance_data' not in st.session_state or st.session_state.performance_data is None:
        st.title('Portfolio Attribution Analysis')
        st.markdown("""
            This app performs portfolio attribution analysis, comparing portfolio performance against a benchmark.
            Upload the relevant Excel files to the fields in the side bar to get started.
        """)

    # Sidebar for file upload
    with st.sidebar:
        st.header('Upload Data Files')
        performance_data = st.file_uploader("Performance Data", type=['xlsx'], key="performance_data")

    # Check if the file has been uploaded
    if performance_data is not None:
        # Fetch sector and daily level data
        combined_df, daily_level_data = data.get_data(performance_data)

        # Main content
        st.title("Analysis Results")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Compounded Returns")
            st.plotly_chart(viz.plot_daily_compounded_returns(viz_data.daily_compounded_returns(daily_level_data)), use_container_width=True)

        with col2:
            st.subheader("Sector Effects - Allocation, Selection, and Interaction")
            st.plotly_chart(viz.plot_allocation_effects_per_sector(viz_data.get_compounded_sector_effects(combined_df)), use_container_width=True)

        st.subheader("Portfolio vs Benchmark Average Sector Weights")
        st.plotly_chart(viz.plot_sector_weights_comparison(viz_data.average_sector_weights(combined_df)), use_container_width=True)

        st.subheader("Attribution Effects and Excess Returns Over Time")
        st.plotly_chart(viz.plot_attribution_effects(viz_data.compounded_allocation_effects(daily_level_data)), use_container_width=True)

        with st.sidebar:
            st.subheader('Download Attribution Data')

            st.download_button(
                label='Download Sector-Level Data',
                data=utils.to_excel_download(combined_df.set_index('Date'), 'Sector Level Data'),
                file_name='sector_data.xlsx',
                mime='application/vnd.ms-excel',
                use_container_width=True
            )

            st.download_button(
                label='Download Daily-Level Data',
                data=utils.to_excel_download(daily_level_data, 'Daily Data'),
                file_name='daily_data.xlsx',
                mime='application/vnd.ms-excel',
                use_container_width=True
            )
            
            st.download_button(
                label='Download Attribution Effects',
                data=utils.to_excel_download(viz_data.compounded_allocation_effects(daily_level_data), 'Attribution Data'),
                file_name='attribution_data.xlsx',
                mime='application/vnd.ms-excel',
                use_container_width=True
            )
            

    else:
        st.info("Please upload subheader required files to proceed with the analysis.")

    # Footer or additional information
    st.markdown("---")
    st.markdown("© Performance Attribution Analysis - Rettig")

if __name__ == "__main__":
    main()