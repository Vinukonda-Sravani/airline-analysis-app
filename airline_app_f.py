import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Airlines Route & Cost Analysis",
    page_icon="✈️",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("airline_route_profitability.csv")
    df['Flight_Date'] = pd.to_datetime(df['Flight_Date'])
    df['Month'] = df['Flight_Date'].dt.strftime('%B')
    df['day_type'] = df['Flight_Date'].dt.dayofweek.apply(
        lambda x: 'Weekend' if x >= 5 else 'Weekday'
    )
    return df

df = load_data()

# Title
st.title("✈️ Airlines Route & Cost Analysis")
st.markdown("**Analyzing 7,974 flights from Dubai (DXB) across 30 destinations and 6 aircraft types**")
st.divider()

# Sidebar filters
st.sidebar.header("🔍 Filters")
aircraft_filter = st.sidebar.multiselect(
    "Aircraft Type",
    options=df['Aircraft_Type'].unique(),
    default=df['Aircraft_Type'].unique()
)
season_filter = st.sidebar.multiselect(
    "Season",
    options=df['Season'].unique(),
    default=df['Season'].unique()
)
route_filter = st.sidebar.multiselect(
    "Route Category",
    options=df['Route_Category'].unique(),
    default=df['Route_Category'].unique()
)

# Apply filters
filtered = df[
    (df['Aircraft_Type'].isin(aircraft_filter)) &
    (df['Season'].isin(season_filter)) &
    (df['Route_Category'].isin(route_filter))
]

# KPI Cards
st.subheader("📊 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Flights", f"{len(filtered):,}")
col2.metric("Avg Revenue", f"€{filtered['Total_Revenue'].mean():,.0f}")
col3.metric("Avg Cost", f"€{filtered['Total_Cost'].mean():,.0f}")
col4.metric("Avg Profit Margin", f"{filtered['Profit_Margin'].mean():.1f}%")
col5.metric("Avg Load Factor", f"{filtered['Load_Factor'].mean():.2f}")

st.divider()

# Row 1 — Two charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Profit Margin by Aircraft")
    aircraft_profit = filtered.groupby('Aircraft_Type')['Profit_Margin'].mean().reset_index().sort_values('Profit_Margin', ascending=True)
    colors = ['red' if x < 0 else 'lightblue' if x < 5 else 'steelblue' if x < 15 else 'darkblue'
              for x in aircraft_profit['Profit_Margin']]
    fig1 = px.bar(
        aircraft_profit,
        x='Profit_Margin',
        y='Aircraft_Type',
        orientation='h',
        title="Red = Losing Money",
        color='Profit_Margin',
        color_continuous_scale=['red', 'yellow', 'green'],
        labels={'Profit_Margin': 'Profit Margin (%)', 'Aircraft_Type': ''}
    )
    fig1.add_vline(x=0, line_color="black", line_width=2)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Profit Margin by Season")
    season_profit = filtered.groupby('Season')['Profit_Margin'].mean().reset_index()
    season_order = ['Low', 'Normal', 'Shoulder', 'Peak']
    season_profit['Season'] = pd.Categorical(season_profit['Season'], categories=season_order, ordered=True)
    season_profit = season_profit.sort_values('Season')
    fig2 = px.bar(
        season_profit,
        x='Season',
        y='Profit_Margin',
        color='Profit_Margin',
        color_continuous_scale=['red', 'yellow', 'green'],
        title="Low Season = Negative Margin",
        labels={'Profit_Margin': 'Profit Margin (%)'}
    )
    fig2.add_hline(y=0, line_color="black", line_width=2)
    st.plotly_chart(fig2, use_container_width=True)

# Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("Monthly Profit Trend by Aircraft")
    monthly = filtered.groupby(['Month', 'Aircraft_Type'])['Profit'].mean().reset_index()
    month_order = ['January','February','March','April','May','June',
                   'July','August','September','October','November','December']
    monthly['Month'] = pd.Categorical(monthly['Month'], categories=month_order, ordered=True)
    monthly = monthly.sort_values('Month')
    fig3 = px.line(
        monthly,
        x='Month',
        y='Profit',
        color='Aircraft_Type',
        title="Seasonal Profit Patterns",
        labels={'Profit': 'Avg Profit (€)'}
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("Top 10 Routes by Profit Margin")
    route_profit = filtered.groupby('Destination')['Profit_Margin'].mean().reset_index().sort_values('Profit_Margin', ascending=False).head(10)
    fig4 = px.bar(
        route_profit,
        x='Profit_Margin',
        y='Destination',
        orientation='h',
        color='Profit_Margin',
        color_continuous_scale='Blues',
        title="FRA, SIN, CDG lead profitability",
        labels={'Profit_Margin': 'Profit Margin (%)', 'Destination': ''}
    )
    st.plotly_chart(fig4, use_container_width=True)

# Row 3
col1, col2 = st.columns(2)

with col1:
    st.subheader("Load Factor vs Profit Margin")
    fig5 = px.scatter(
        filtered,
        x='Load_Factor',
        y='Profit_Margin',
        color='Aircraft_Type',
        size='Aircraft_Capacity',
        title="Does higher occupancy = more profit?",
        labels={'Load_Factor': 'Load Factor', 'Profit_Margin': 'Profit Margin (%)'},
        hover_data=['Destination', 'Season']
    )
    fig5.add_hline(y=0, line_color="red", line_dash="dash")
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    st.subheader("Cost Breakdown")
    cost_cols = ['Fuel_Cost', 'Crew_Cost', 'Maintenance_Cost',
                 'Airport_Fees', 'Catering_Cost', 'Marketing_Cost',
                 'IT_Systems_Cost', 'Handling_Cost']
    cost_data = filtered[cost_cols].mean().reset_index()
    cost_data.columns = ['Cost Type', 'Average Cost']
    cost_data = cost_data.sort_values('Average Cost', ascending=False)
    fig6 = px.treemap(
        cost_data,
        path=['Cost Type'],
        values='Average Cost',
        title="Where Does The Money Go?",
        color='Average Cost',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig6, use_container_width=True)

# Waterfall chart
st.subheader("💰 Revenue to Profit Waterfall")
avg_data = filtered.mean(numeric_only=True)
waterfall_data = {
    'Category': ['Total Revenue', 'Fuel Cost', 'Crew Cost',
                 'Maintenance', 'Airport Fees', 'Catering',
                 'Marketing', 'Other Costs', 'Net Profit'],
    'Amount': [
        avg_data['Total_Revenue'],
        -avg_data['Fuel_Cost'],
        -avg_data['Crew_Cost'],
        -avg_data['Maintenance_Cost'],
        -avg_data['Airport_Fees'],
        -avg_data['Catering_Cost'],
        -avg_data['Marketing_Cost'],
        -(avg_data['Total_Cost'] - avg_data['Fuel_Cost'] - avg_data['Crew_Cost'] -
          avg_data['Maintenance_Cost'] - avg_data['Airport_Fees'] -
          avg_data['Catering_Cost'] - avg_data['Marketing_Cost']),
        avg_data['Profit']
    ]
}
wf = pd.DataFrame(waterfall_data)
fig7 = go.Figure(go.Waterfall(
    name="Profit Breakdown",
    orientation="v",
    measure=["absolute", "relative", "relative", "relative",
             "relative", "relative", "relative", "relative", "total"],
    x=wf['Category'],
    y=wf['Amount'],
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "red"}},
    increasing={"marker": {"color": "green"}},
    totals={"marker": {"color": "blue"}}
))
fig7.update_layout(title="Where Does Revenue Go? (Average per Flight)")
st.plotly_chart(fig7, use_container_width=True)

# Key Insights
st.divider()
st.subheader("🔍 Key Business Insights")
col1, col2 = st.columns(2)

with col1:
    st.error("⚠️ **Loss-Making Aircraft**\n\nBoeing 737-800: **-9.50%** margin\n\nAirbus A320: **-7.87%** margin\n\nCombined 1,973 flights losing money annually.")
    st.success("✅ **Star Performer**\n\nAirbus A380: **23.18%** margin\n\nHighest revenue AND highest profit.\n\nNearly full on every flight (85% load factor).")

with col2:
    st.warning("⚠️ **Season Risk**\n\nLow season margin: **-8.50%**\n\nAirline loses money in low season.\n\nFuel costs barely change — revenue collapses.")
    st.info("💡 **Route Recommendation**\n\nFrankfurt (FRA): **46%** margin vs JFK: **15.7%**\n\nSwitch JFK routes from A380 to Boeing 787-9\n\nto reduce fuel cost and increase margin.")

# Raw data
with st.expander("📋 View Raw Data"):
    st.dataframe(filtered.head(100))
    