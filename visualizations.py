import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def make_plot(df):
    fig = px.scatter(df, x='Portfolio Weight', y='Benchmark Weight')
    return fig


# Plot for daily compounded returns
def plot_daily_compounded_returns(df):
    fig = px.line(df, x=df.index, y=['Portfolio Compounded Returns', 'Benchmark Compounded Returns'])
    return fig

# Plot for sector weight comparison
def plot_sector_weights_comparison(df):
    # Create a bar chart with Portfolio and Benchmark weights for each sector
    fig = go.Figure()

    # Add Portfolio bars
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Portfolio Average Sector Weight'],
        name='Portfolio Average Sector Weight',
        marker_color='indianred'
    ))

    # Add Benchmark bars
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Benchmark Average Sector Weight'],
        name='Benchmark Average Sector Weight',
        marker_color='lightblue'
    ))

    # Customize the layout
    fig.update_layout(
        title='Portfolio vs Benchmark Average Sector Weights',
        xaxis_tickangle=-45,
        xaxis_title='GICS Sector',
        yaxis_title='Average Sector Weight',
        barmode='group',
        legend_title='Weights',
        plot_bgcolor='white'
    )

    return fig

def plot_allocation_effects_per_sector(df):
    # Create a grouped bar chart with all effects for each GICS sector
    fig = go.Figure()

    # Add Allocation Effect bars
    fig.add_trace(go.Bar(
        y=df['GICS Sector'],
        x=df['Allocation Effect'],
        name='Allocation Effect',
        orientation='h',
        marker=dict(color='rgba(50, 171, 96, 0.7)', line=dict(color='rgba(50, 171, 96, 1.0)', width=1))
    ))

    # Add Selection Effect bars
    fig.add_trace(go.Bar(
        y=df['GICS Sector'],
        x=df['Selection Effect'],
        name='Selection Effect',
        orientation='h',
        marker=dict(color='rgba(219, 64, 82, 0.7)', line=dict(color='rgba(219, 64, 82, 1.0)', width=1))
    ))

    # Add Interaction Effect bars
    fig.add_trace(go.Bar(
        y=df['GICS Sector'],
        x=df['Interaction Effect'],
        name='Interaction Effect',
        orientation='h',
        marker=dict(color='rgba(55, 128, 191, 0.7)', line=dict(color='rgba(55, 128, 191, 1.0)', width=1))
    ))

    # Customize the layout
    fig.update_layout(
        barmode='group',
        title='Sector Effects - Allocation, Selection, and Interaction',
        xaxis_title='Effect Value',
        yaxis_title='GICS Sector',
        yaxis={'categoryorder':'total ascending'},
        legend_title='Effect Types',
        plot_bgcolor='white'
    )

    # Customize the legend to be at the top for better readability
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))

    return fig

def plot_attribution_effects(df):
    # Create traces for each effect and excess return
    traces = []
    for effect in ['Allocation Effect', 'Selection Effect', 'Interaction Effect', 'Excess Returns']:
        traces.append(go.Scatter(
            x=df.index, 
            y=df[effect], 
            name=effect
        ))

    # Create the figure with all traces
    fig = go.Figure(traces)

    # Update the layout of the figure
    fig.update_layout(
        title='Attribution Effects and Excess Returns Over Time',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Effect Value'),
        legend_title='Effect Type',
        hovermode='x unified'
    )

    return fig

