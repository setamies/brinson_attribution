import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Defining a consistent color palette
color_palette = {
    'Portfolio': 'rgba(94,162,186,255)',  
    'Benchmark': 'rgba(110,128,144,255)',    
    'Allocation': 'rgba(114,194,136,255)',  
    'Selection': 'rgba(61,121,144,255)',  
#    'Interaction': 'rgba(38,88,76,255)', 
    'Excess Returns': 'rgba(184,214,225,255)' 
}

def plot_daily_compounded_returns(df):
    # Updated color scheme
    portfolio_color = color_palette['Portfolio']
    benchmark_color = color_palette['Benchmark']

    # Create the figure
    fig = px.line(
        df, 
        x=df.index, 
        y=['Portfolio Compounded Returns', 'Benchmark Compounded Returns'],
        labels={'value': 'Returns', 'variable': 'Series'},  # Update axis title and legend title
        color_discrete_map={
            'Portfolio Compounded Returns': portfolio_color,
            'Benchmark Compounded Returns': benchmark_color
        }
    )

    # Update legend names
    new_names = {
        'Portfolio Compounded Returns': 'Portfolio', 
        'Benchmark Compounded Returns': 'Benchmark'
    }
    fig.for_each_trace(lambda t: t.update(name=new_names[t.name]))
    
    # Update y-axis title and position the legend horizontally at the top right
    fig.update_layout(
        yaxis_title='Returns',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ), 
        yaxis=dict(
            tickformat = ',.1%'
        )
    )

    return fig

# Plot for sector weight comparison
def plot_sector_weights_comparison(df):
    # Updated color scheme
    portfolio_color = color_palette['Portfolio']
    benchmark_color = color_palette['Benchmark']
    
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Portfolio Average Sector Weight'],
        name='Portfolio',
        marker_color=portfolio_color
    ))

    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Benchmark Average Sector Weight'],
        name='Benchmark',
        marker_color=benchmark_color
    ))

    fig.update_layout(
        yaxis=dict(
            tickformat = ',.1%'
        ),
        xaxis_tickangle=-45,
        xaxis_title='GICS Sector',
        yaxis_title='Average Sector Weight',
        barmode='group',
        legend_title='Weights',
        plot_bgcolor='white'
    )

    return fig

def plot_allocation_effects_per_sector(df):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['GICS Sector'],
        x=df['Allocation Effect'],
        name='Allocation',
        orientation='h',
        marker_color=color_palette['Allocation']
    ))

    fig.add_trace(go.Bar(
        y=df['GICS Sector'],
        x=df['Selection Effect'],
        name='Selection',
        orientation='h',
        marker_color=color_palette['Selection']
    ))

    fig.update_layout(
        barmode='group',
        xaxis_title='Effect Value',
        yaxis={'categoryorder':'total ascending'},
        legend_title='Effect Types',
        plot_bgcolor='white'
    )

    fig.update_layout(
        xaxis=dict(
            tickformat = ',.1%'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
    ))

    return fig

def plot_attribution_effects(df):
    # Dictionary to map the old effect names to the new shorter names
    effect_names_map = {
        'Allocation Effect': 'Allocation',
        'Selection Effect': 'Selection',
        'Excess Returns': 'Excess Returns'  # Keeping this the same
    }

    traces = []
    for effect in effect_names_map.keys():
        traces.append(go.Scatter(
            x=df.index, 
            y=df[effect], 
            name=effect_names_map[effect],
            line=dict(color=color_palette[effect_names_map[effect]]) # Use the new color
        ))

    fig = go.Figure(traces)
    fig.update_layout(
        xaxis=dict(title='Date'),
        yaxis=dict(title='Effect Value', tickformat = ',.1%'),
        legend_title='Performance Metrics',
        hovermode='x unified'
    )

    return fig
