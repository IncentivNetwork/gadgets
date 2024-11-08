from dash import Dash, dcc, html, Input, Output, MATCH, ALL
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

app = Dash(__name__)

input_style = {'margin-bottom': '20px', 'display': 'block'}
label_style = {'margin-bottom': '5px', 'display': 'block'}
slider_container_style = {
    'margin-bottom': '40px',
    'width': '500px'  # Constrain slider width
}

app.layout = html.Div([
    html.H1('Incentiv Staking APY Calculator'),
    
    html.Div([
        html.Div([
            html.Label('Starting Total Supply', style=label_style),
            dcc.Input(id='total-supply', value=92e9, type='number')
        ], style=input_style),
        
        html.Div([
            html.Label('Yearly Inflation (%)', style=label_style),
            dcc.Slider(
                id='inflation-rate',
                min=0,
                max=100,
                step=0.5,
                value=7,
                marks={
                    0: '0%',
                    25: '25%',
                    50: '50%',
                    75: '75%',
                    100: '100%'
                },
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style=slider_container_style),
        
        html.Div([
            html.Label('Initial Circulating Supply (% of Total)', style=label_style),
            dcc.Slider(
                id='circulating-percent',
                min=0,
                max=100,
                step=1,
                value=20,
                marks={
                    0: '0%',
                    25: '25%',
                    50: '50%',
                    75: '75%',
                    100: '100%'
                },
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style=slider_container_style),
        
        html.Div([
            html.Label('Staking Rate (% of circulating)', style=label_style),
            dcc.Slider(
                id='staking-rate',
                min=0,
                max=100,
                step=0.1,
                value=50,
                marks={
                    0: '0%',
                    25: '25%',
                    50: '50%',
                    75: '75%',
                    100: '100%'
                },
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style=slider_container_style),
        
        html.Div([
            html.Label('Number of Validators', style=label_style),
            dcc.Input(id='validator-count', value=100, type='number', min=1)
        ], style=input_style),
    ], style={'padding': '20px'}),
    
    html.Div([
        html.H2('Current APY:'),
        html.H3(id='apy-output', style={'color': '#2196F3'}),  # Added color for emphasis
        html.Div(id='summary-stats')
    ]),
    
    html.Div([
        dcc.Graph(id='analysis-charts')
    ])
])

@app.callback(
    [Output('apy-output', 'children'),
     Output('analysis-charts', 'figure'),
     Output('summary-stats', 'children')],
    [Input('total-supply', 'value'),
     Input('inflation-rate', 'value'),
     Input('circulating-percent', 'value'),
     Input('staking-rate', 'value'),
     Input('validator-count', 'value')]
)
def update_output(total_supply, inflation_rate, circulating_percent, 
                 staking_rate, validator_count):
    
    # Calculate circulating supply
    circulating_supply = total_supply * (circulating_percent / 100)
    
    # Calculate APY
    inflation_amount = total_supply * (inflation_rate / 100)
    staked_amount = circulating_supply * (staking_rate / 100)
    apy = (inflation_amount / staked_amount) * 100 if staked_amount > 0 else 0
    
    # Calculate per-validator stake and rewards
    per_validator_stake = staked_amount / validator_count if validator_count > 0 else 0
    per_validator_rewards = (inflation_amount / validator_count) if validator_count > 0 else 0
    per_validator_apy = (per_validator_rewards / per_validator_stake) * 100 if per_validator_stake > 0 else 0
    
    # Create subplots
    fig = make_subplots(rows=1, cols=2, 
                       subplot_titles=('APY vs Staking Rate', 
                                     'APY Distribution per Validator'))
    
    # First plot: APY vs Staking Rate
    staking_rates = np.linspace(1, 100, 100)
    apys = [total_supply * (inflation_rate/100) / (circulating_supply * (rate/100)) * 100 
            for rate in staking_rates]
    
    fig.add_trace(
        go.Scatter(x=staking_rates, y=apys, name='APY vs Staking Rate',
                  mode='lines',
                  hovertemplate="Staking Rate: %{x:.1f}%<br>APY: %{y:.1f}%<extra></extra>"),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=[staking_rate], y=[apy], name='Current Point',
                  mode='markers', marker=dict(size=15, color='red'),
                  hovertemplate="Current Rate: %{x:.1f}%<br>APY: %{y:.1f}%<extra></extra>"),
        row=1, col=1
    )
    
    # Second plot: APY Distribution
    validator_ranges = np.linspace(max(10, validator_count/2), validator_count*2, 50)
    distributed_apys = [total_supply * (inflation_rate/100) / 
                       (staked_amount / v) * 100 if v > 0 else 0 
                       for v in validator_ranges]
    
    fig.add_trace(
        go.Scatter(x=validator_ranges, y=distributed_apys,
                  name='APY vs Validator Count', mode='lines',
                  hovertemplate="Validators: %{x:.0f}<br>APY: %{y:.1f}%<extra></extra>"),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=[validator_count], y=[apy],
                  name='Current Validators', mode='markers',
                  marker=dict(size=15, color='red'),
                  hovertemplate="Current Validators: %{x:.0f}<br>APY: %{y:.1f}%<extra></extra>"),
        row=1, col=2
    )
    
    # Update layout
    fig.update_xaxes(title_text='Staking Rate (%)', row=1, col=1)
    fig.update_xaxes(title_text='Number of Validators', row=1, col=2)
    fig.update_yaxes(title_text='APY (%)', row=1, col=1)
    fig.update_yaxes(title_text='APY (%)', row=1, col=2)
    fig.update_layout(height=600, showlegend=True)
    
    # Summary stats
    summary = html.Div([
        html.P(f"Circulating Supply: {circulating_supply:,.0f} ({circulating_percent:.1f}% of total)"),
        html.P(f"Total Staked Amount: {staked_amount:,.0f}"),
        html.P(f"Yearly Inflation Amount: {inflation_amount:,.0f}"),
        html.P(f"Average Stake per Validator: {per_validator_stake:,.0f}"),
        html.P(f"Average APY per Validator: {per_validator_apy:.2f}%"),
        html.P(f"Average Yearly Rewards per Validator: {per_validator_rewards:,.0f}")
    ])
    
    return f"{apy:.2f}%", fig, summary

if __name__ == '__main__':
    app.run_server(debug=True)