# brinson_attribution

## Introduction
`brinson_attribution` is a Python library that leverages the Brinson model to conduct portfolio performance attribution. It serves as a tool for investment analysts and data scientists, enabling a detailed examination of how portfolio return drivers against benchmarks.

## Usage
The library is accessible via an interactive user interface. Analysts can input their data directly into the interface, making the process straightforward and efficient. The interface is designed to guide users through the data upload process.

## Data Input Format
The application accepts data input in the following structured format:

- **Portfolio Weights**: A file (CSV or Excel) with portfolio weights by sector.
- **Portfolio Returns**: A file (CSV or Excel) with returns for each sector in the portfolio.
- **Benchmark Weights**: A file (CSV or Excel) detailing the weights of each sector in the benchmark.
- **Benchmark Returns**: A file (CSV or Excel) with the returns of each sector in the benchmark.

While the app is optimized for sector-level input, users with data in different formats (like security-level data) can preprocess their data to aggregate it to the sector level before using the app.

## Interactive User Interface
The app features an interactive user interface that:

- Allows for data uploads through a web-based platform.
- Provides visualizations of the performance attribution after data processing.
- Offers customization options for the analysis, such as date range selection and sector-specific examination.

## Current Implementation Details
The initial release provides functionality for sector-level performance attribution, with the following key calculations included:

- **Allocation Effect**
- **Selection Effect**
- **Interaction Effect**
- **Sum of Effects**

## Visualization and Analysis Features
The app includes a suite of data visualizations that represent:

- Sector weights comparison between the portfolio and the benchmark.
- Attribution effects over time in a multi-line chart format.
- Attribution effects illustrated by sector from the entire time span of data.
