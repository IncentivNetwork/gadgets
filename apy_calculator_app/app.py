import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

# Page config
st.set_page_config(page_title="Incentiv Staking APY Calculator", layout="wide")

st.title('Staking APY Calculator')
st.text('Powered by Incentiv')
#st.header('Calculate the APY for a staking network')
st.markdown("---")
st.subheader('Select Network Parameters')

# Input columns
col1, col2 = st.columns(2)

with col1:
    total_supply = st.number_input('Starting Total Supply', value=92e9, format="%.0f")
    inflation_rate = st.slider('Yearly Inflation (%)', 0.0, 100.0, 7.0, 0.5)
    circulating_percent = st.slider('Circulating Supply (%)', 0.0, 100.0, 20.0, 0.5)

with col2:
    staking_rate = st.slider('Staking Rate (% of Circulating)', 0.0, 100.0, 50.0, 0.5)
    validator_count = st.number_input('Number of Validators', value=50, min_value=1)

# Calculations
circulating_supply = total_supply * (circulating_percent / 100)
inflation_amount = total_supply * (inflation_rate / 100)
staked_amount = circulating_supply * (staking_rate / 100)
apy = (inflation_amount / staked_amount) * 100 if staked_amount > 0 else 0

per_validator_stake = staked_amount / validator_count if validator_count > 0 else 0
per_validator_rewards = (inflation_amount / validator_count) if validator_count > 0 else 0

# Create subplots
fig = make_subplots(rows=1, cols=2, 
                    subplot_titles=('APY vs Staking Rate', 
                                  'APY Distribution per Validator'))

# First plot: APY vs Staking Rate
staking_rates = np.linspace(15, 100, 100)
apys = [total_supply * (inflation_rate/100) / (circulating_supply * (rate/100)) * 100 
        for rate in staking_rates]

fig.add_trace(
    go.Scatter(x=staking_rates, y=apys, name='APY vs Staking Rate',
              mode='lines',
              hovertemplate="Staking Rate: %{x:.1f}%<br>APY: %{y:.1f}%<extra></extra>"),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(x=[staking_rate], y=[apy], name='Current',
              mode='markers', marker=dict(size=12, color='red'),
              hovertemplate="Current Staking Rate: %{x:.1f}%<br>APY: %{y:.1f}%<extra></extra>"),
    row=1, col=1
)

# Second plot: APY Distribution
validator_ranges = np.linspace(max(10, validator_count/2), validator_count*2, 50)
distributed_apys = [apy / (v/validator_count) if v > 0 else 0 for v in validator_ranges]
fig.add_trace(
    go.Scatter(x=validator_ranges, y=distributed_apys, name='Validator APY',
              mode='lines'),
    row=1, col=2
)

fig.add_trace(
    go.Scatter(x=[validator_count], y=[apy], name='Current',
              mode='markers', marker=dict(size=12, color='blue'),
              hovertemplate="Current Staking Rate: %{x:.1f}%<br>APY: %{y:.1f}%<extra></extra>"),
    row=1, col=2
)

# Update layout
fig.update_xaxes(title_text='Staking Rate (%)', row=1, col=1)
fig.update_xaxes(title_text='Number of Validators', row=1, col=2)
fig.update_yaxes(title_text='APY (%)', row=1, col=1)
fig.update_yaxes(title_text='APY (%)', row=1, col=2)
fig.update_layout(height=600, showlegend=True)

# Display results
st.header('Current APY:')
st.subheader(f"{apy:.2f}%")

# Summary stats
st.header('Summary Statistics')
col1, col2 = st.columns(2)

with col1:
    st.write(f"Circulating Supply: {circulating_supply:,.0f} ({circulating_percent:.1f}% of total)")
    st.write(f"Total Staked Amount: {staked_amount:,.0f}")
    st.write(f"Yearly Inflation Amount: {inflation_amount:,.0f}")

with col2:
    st.write(f"Average Stake per Validator: {per_validator_stake:,.0f}")
    st.write(f"Average Yearly Rewards per Validator: {per_validator_rewards:,.0f}")

# Display charts
st.plotly_chart(fig, use_container_width=True)