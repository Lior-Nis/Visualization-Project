import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# region intro
st.set_page_config(page_title='Unicorn Startup Analysis',
                   initial_sidebar_state='expanded',
                   layout="wide")

custom_theme = """
    <style>
    :root {
        --primary-color: purple;
    }
    </style>
    """

st.markdown(custom_theme, unsafe_allow_html=True)

# Data Loading
data = pd.read_csv('./WWUS.csv')

# Parameters
sectors = data['Industry'].unique().tolist()
dates = data['Date'].unique().tolist().sort()
countries = data['Country'].unique().tolist()

# Title and Description
col, _, _ = st.columns((3, 1, 1))
with col:
    st.title('🦄 Unicorn Startup Analysis')
col, _, _ = st.columns((3, 1, 1))
with col:
    st.subheader('Information Visualization Project')
col, _, _ = st.columns((3, 1, 1))
with col:
    st.markdown("Creator: Lior Nisimov")


col, _, _ = st.columns((3, 1, 1))
with col:
    st.markdown(
        "<p>Welcome to my exploration of unicorn startups - \
            privately held companies with valuations exceeding $1 billion.\
            We'll dive into the world of high-value entrepreneurial ventures, \
            examining key details such as company name, valuation, date, country, city, industry, and investors.\
            Join us as we uncover insights into the global landscape of unicorn startups, \
            their industry sectors, investment patterns, and notable players</p>",
        unsafe_allow_html=True
    )
# endregion

# ======================================================================================================================

# region first plot
st.markdown("#### **Identifying the most common countries in each sector**")
st.markdown("This plot displays a choropleth map showing the distribution of\
             unicorn startups across different countries in the selected sector.\
             The color intensity represents the number of companies in each country.\
             You can select a specific sector from the dropdown menu to view the corresponding distribution.")

_, col1, _ = st.columns((0.1, 2, 0.1))
with col1:
    selected_sector = st.selectbox('**Select Sector**', sectors, key=0)


# Create the graph
if not selected_sector:
    country_counts = pd.DataFrame({'Country': ['No sector was selected'], 'Company': [0]}, index=['Country'])
else:
    filtered_data = data[data['Industry'] == selected_sector]
    country_counts = filtered_data.groupby(['Country']).agg('count')

# Create the graph
fig = px.choropleth(country_counts, locations=country_counts.index, 
                    locationmode='country names', color='Company', range_color=(1, 15))

fig.update_layout(geo=dict(bgcolor= 'rgba(0,0,0,0)'))

fig.update_layout(
    coloraxis_colorbar=dict(
        title='Company Count',
        tickvals=[1, 3, 5, 7, 10, 15],
        ticktext=['1', '3', '5', '7', '10', '15+']
    ),
    xaxis=dict(title='Country'),
    yaxis=dict(title='Number of Companies')
)

st.plotly_chart(fig, use_container_width=True)
# endregion

# ======================================================================================================================

# region second plot
st.markdown("#### **Identifying and comparing sector startups trends**")
st.markdown("This plot visualizes the cumulative count of unicorn startups over time for the selected sectors.\
            If only one sector is selected, a line chart shows the growth of startups in that sector over the selected time range.\
             If multiple sectors are selected, individual line charts are displayed for each sector, allowing for easy comparison.")

_, col1, col2, _ = st.columns((0.1, 2, 2, 0.1))
with col1:
    selected_sectors = st.multiselect('**Select Sector**', sectors, max_selections=5, default=sectors[0], key=1)
with col2:
    time_range = st.slider('**Select Time Range**', key = 2, min_value=2007, max_value=2021, value=(2007, 2021), step=1)

# Create the graph
if not selected_sectors:
    filtered_data = pd.DataFrame({'Year': ['No sector was selected'], 'Company': [0]}, index=['Year'])
elif len(selected_sectors) == 1:
    filtered_data = data[data['Industry'] == selected_sectors[0]]
    years = filtered_data['Date'].apply(lambda x: x[-4:])
    filtered_data['Year'] = years.astype(int)
    filtered_data = filtered_data[(filtered_data['Year'] >= time_range[0]) & (filtered_data['Year'] <= time_range[1])]
    filtered_data = filtered_data.groupby(['Year']).agg('count')
    filtered_data = filtered_data.cumsum()
    # Create the graph
    fig = px.scatter(filtered_data, x=filtered_data.index, y='Company')
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['Company'],
                            mode='lines',
                            line=dict(width=1),
                            showlegend=False))
    fig.update_traces(marker_color='#5C5CFF')
    st.plotly_chart(fig, use_container_width=True)
else:
    def filter_and_aggregate_data(data, sectors, time_range):
        filtered_data = []
        for sector in sectors:
            fd = data[data['Industry'] == sector]
            years = fd['Date'].apply(lambda x: x[-4:])
            fd['Year'] = years.astype(int)
            fd = fd[(fd['Year'] >= time_range[0]) & (fd['Year'] <= time_range[1])]
            fd = fd.groupby(['Year']).agg('count')
            fd = fd.cumsum()
            filtered_data.append(fd)
        return filtered_data
    
    trend_dict = {}

    for sector in selected_sectors:
        trend_dict[sector] = filter_and_aggregate_data(data, [sector], time_range)


    # Create the graph
    t_list = []
    red_colors = ['#5C5CFF', '#0000D1', '#2E2EFF', '#8A8AFF', '#006DFF']
    for i, sector in enumerate(selected_sectors):
        t_list.append(go.Scatter(x=trend_dict[sector][0].index, 
                                y=trend_dict[sector][0]['Company'], 
                                name=sector, mode='lines+markers',
                                line=dict(color=red_colors[i]),
                                marker=dict(color=red_colors[i])))
    fig = go.Figure(data=t_list)

    fig.update_layout(
    xaxis=dict(title='Year'),
    yaxis=dict(title='Cumulative Company Count'))


    st.plotly_chart(fig, use_container_width=True)
# endregion

# ======================================================================================================================

# region third plot
st.markdown("#### **Top Investors and Their Investments by Sector**")
st.markdown("This plot provides insights into the top investors and their investments in the selected sectors over time.\
             It visualizes the distribution of investments made by the top investors across different sectors, \
            allowing you to identify the key players and their areas of focus.")

st.markdown("The plot displays a bar chart where the x-axis represents the investors,\
             and the y-axis represents the number of investments. Each bar is color-coded based\
             on the sector in which the investments were made. By adjusting the parameters below,\
             you can choose the number of top investors to display, the time range of investments, and the sectors of interest.")



_, col1, col2, _ = st.columns((0.1, 2, 2, 0.1))
with col1:
    topn = st.slider('**Select Top N**', key = 3.1, min_value=1, max_value=10, value=5, step=1)
with col2:
    time_range = st.slider('**Select Time Range**', key = 3.2, min_value=2007, max_value=2021, value=(2007, 2021), step=1)

_ , col1, _ = st.columns((0.1, 2, 0.1))
with col1:
    selected_sectors = st.multiselect('**Select Sector**', sectors, max_selections=5, default=sectors[0:3], key=3.3)

# Create the graph
years = data['Date'].apply(lambda x: x[-4:]).astype(int)
filtered_data = data[(years >= time_range[0]) & (years <= time_range[1])]
filtered_data = filtered_data[filtered_data['Industry'].isin(selected_sectors)]

investors_dict = {}
for i, investors in enumerate(filtered_data['Investors']):
    for investor in eval(investors):
        investors_dict[investor] = investors_dict.get(investor, []) + [filtered_data.iloc[i]['Industry']]    

investors_list = sorted(list(investors_dict.items()), key=lambda x: len(x[1]), reverse=True)
topn_investors_dict = dict(investors_list[:topn])

plt_df = pd.DataFrame(columns=['Investor', 'Sector', 'Count'])

for investor in topn_investors_dict.keys():
    for sector in topn_investors_dict[investor]:
        # use concat to add a new row
        plt_df = pd.concat([plt_df, pd.DataFrame([[investor, sector, 1]], columns=['Investor', 'Sector', 'Count'])])


# Create the graph
custom_colors = ['#000075', '#0000FF', '#8A8AFF', '#7EC8E3', '#0E86D4']
fig = px.bar(plt_df, x='Investor', y='Count', color='Sector', color_discrete_sequence=custom_colors)


fig.update_layout(
    xaxis=dict(title='Investor'),
    yaxis=dict(title='Number of Investments')
)

st.plotly_chart(fig, use_container_width=True)
# endregion

# ======================================================================================================================

# region fourth plot
st.markdown("#### **Compare log valuation distribution across sectors**")
st.markdown("This plot shows the distribution of unicorn startup valuations on a logarithmic scale for the selected sectors.\
             Each sector is represented by a violin plot, with the x-axis indicating the industry and the y-axis representing\
             the logarithmic valuation. The width of the violin plot indicates the density of valuations at different levels.")

_, col1, _ = st.columns((0.1, 2, 0.1))

with col1:
    selected_sectors = st.multiselect('**Select Sector**', sectors, key=5.1, max_selections=5, default=sectors[0])


filtered_data = data[data['Industry'].isin(selected_sectors)]
filtered_data['Log Valuation'] = filtered_data['Valuation'].apply(lambda x: round(np.log(x), 2))

# sort filtered data based on log valuation
filtered_data = filtered_data.sort_values(by=['Log Valuation'], ascending=False)

# Create the graph
# Create the pie chart using Plotly Express
fig = px.violin(filtered_data, x='Industry', y='Log Valuation', 
                hover_data=['Valuation'])

agg_data = filtered_data.groupby(['Industry']).agg('mean')
agg_data = agg_data.sort_values(by=['Valuation'], ascending=False)
agg_data['Valuation'] = agg_data['Valuation'].apply(lambda x: round(x, 2))



fig.add_trace(go.Bar(
    x=agg_data.index,
    y=agg_data['Log Valuation'],
    text=agg_data['Valuation'],
    hovertemplate='Industry: %{x}<br>Mean Valuation: %{text:.2s}B',
    marker_color='#B82E2E',
    width=0.1,
    name='Average'
))


fig.update_traces(marker_color='#5C5CFF')

fig.update_layout(
    xaxis=dict(title='Industry'),
    yaxis=dict(title='Log Valuation (Billions)')
)

st.plotly_chart(fig, use_container_width=True)
# endregion


# ======================================================================================================================
