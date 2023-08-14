import re
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt

# Create a dictionary for translating German city names to English

city_translation = {
    'München': 'Munich',
    'Köln': 'Cologne',
    'Nürnberg': 'Nuremberg',
    'Hannover': 'Hanover',
    'Braunschweig': 'Brunswick',
    'Konstanz': 'Constance',
    'Münster (Westfalen)': 'Münster',
    'Friedberg (Hessen)': 'Friedberg',
    'Oldenburg (Oldenburg)': 'Oldenburg',
    'Verden (Aller)': 'Verden an der Aller',
    'Kempten (Allgäu)': 'Kempten',
    'Leer (Ostfriesland)': 'Leer',
    'Hansestadt Stendal': 'Stendal',
}

# Preprocess and clean the data

def preprocess_city_name(city):
    if "Berlin" in city:
        return "Berlin"
    elif city in city_translation:
        return city_translation[city]
    return city

def clean_city_name(cleaned_city):

    # Define replacement patterns and apply replacements
    replacements = {
        r'v\.d\.': 'v. d.',
        r'a\.d\.': 'an der',
        r'i\.d\.': 'in der',
        r'i\. OB': 'in Oberbayern',
        r'i\.Bay\.': 'in Bayern',
        r'in der OPf': 'in der Oberpfalz',
        r'Hansestadt': '',
    }

    for pattern, replacement in replacements.items():
        cleaned_city = re.sub(pattern, replacement, cleaned_city)

    return cleaned_city

# Merge the insolvency data with additional information

def merge_info_to_pivot(df1, df2, key):
    df2 = df2.rename(columns={'name':'City'})
    merged_pivot = df1.merge(df2, on=key, how='left')
    merged_pivot.columns = [x.capitalize() for x in merged_pivot.columns]
    return merged_pivot

# Aggregate and sort the data for each city

def create_city_pivot(path):
    
    # Read the CSV file
    df = pd.read_csv(path, header=None)

    # Preprocess city names
    df[2] = df[2].apply(preprocess_city_name)
    df[2] = df[2].apply(clean_city_name)

    # Create a pivot table with the count for each city
    pivot_table = df.pivot_table(index=2, aggfunc='size')

    # Sort the pivot table by count in descending order
    sorted_pivot_table = pivot_table.sort_values(ascending=False)
    result = sorted_pivot_table.to_frame().reset_index()
    result.columns = ['City', 'Count']

    return result

# Aggregate and sort the data for each state

def create_regional_pivot(path):
    regional_pivot = path.groupby('State')['Count'].sum().sort_values(ascending=False).to_frame().reset_index()
    return regional_pivot

# Aggregate and sort the data by periods (daily, weekly, monthly)

def create_pivot_by_periods(data_path):
    
    # Read the CSV file with scraped data
    df = pd.read_csv(data_path, names = ['Empty', 'ID', 'Court', 'Subject', 'Address', 'Register', 'Publication Date'])

    # Convert 'Publication date' column to datetime
    df['Publication Date'] = pd.to_datetime(df['Publication Date'], dayfirst=True)

    # Determine the default date range based on the minimum and maximum publication dates in the dataset
    # You can manually adjust the start and end dates as needed
    start_date = df['Publication Date'].min()
    end_date = df['Publication Date'].max()

    # Filter data based on the specified date range
    filtered_data = df[(df['Publication Date'] >= start_date) & (df['Publication Date'] <= end_date)]

    # Calculate the timedelta between start and end dates
    timedelta = end_date - start_date

    # Determine the period based on the timedelta
    if timedelta < pd.Timedelta(weeks=3):
        period = 'D'
        period_label = 'Days'
    elif timedelta < pd.Timedelta(weeks=12):
        period = '1W'
        period_label = 'Weeks'
    else:
        period = 'M'
        period_label = 'Months'
        
    # Group data by the specified period and count cases
    grouped_data = filtered_data.groupby(pd.Grouper(key='Publication Date', freq=period)).size().reset_index(name='Count')
    return grouped_data, period, period_label, start_date, end_date


# Load city and regional data
pd.options.display.max_columns = 10
city_info = pd.read_json("city_data.json")
state_info = pd.read_csv("regional_data.csv", names = ['State', 'Population'])

# Calculate insolvency rates for each city
city_pivot_table = create_city_pivot('insolvenz_data.csv')
city_merged_pivot = merge_info_to_pivot(city_pivot_table, city_info, 'City')
city_merged_pivot['Insolvency Rate'] = city_merged_pivot['Count'] / city_merged_pivot['Population']

# Calculate insolvency rates and total insolvency counts for each region
regional_pivot = create_regional_pivot(city_merged_pivot)
regional_merged_pivot = merge_info_to_pivot(regional_pivot, state_info, 'State')
regional_merged_pivot['Insolvency Rate'] = regional_merged_pivot['Count'] / regional_merged_pivot['Population']

# Perform analysis on city insolvency rates
city_summary_stats = city_merged_pivot.describe()

# Perform analysis on regional insolvency rates
regional_summary_stats = regional_merged_pivot.describe()

# Perform time analysis on insolvency counts
periods_info, period, period_label, start_date, end_date = create_pivot_by_periods('insolvenz_data.csv')

# Automaticly label counts where it's neccessary 
def autolabel_counts(ax, rects):
    fontsize = 5 if len(rects) == 16 else (6 if len(rects) < 16 else 4)

    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.0f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 2),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=fontsize)


# Create visualizations for periods and cities
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Settings for time analysis on insolvency counts (labels)
sns.set_palette(sns.color_palette("viridis", n_colors=len(periods_info)))
sns.barplot(data=periods_info, x='Publication Date', y='Count', ax=ax1)   
date_labels = []
for idx, row in periods_info.iterrows():
    if period == 'D':
        date_range = row['Publication Date'].strftime('%d.%m.%Y')
    elif period == '1W':
        if idx == 0:
            date_range = f"{start_date.strftime('%d.%m.%Y')} - {(row['Publication Date'] + pd.Timedelta(days=0)).strftime('%d.%m.%Y')}"
        elif idx == len(periods_info) - 1:
            date_range = f"{(row['Publication Date'] - pd.Timedelta(days=6)).strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
        else:
            date_range = f"{(row['Publication Date'] - pd.Timedelta(days=6)).strftime('%d.%m.%Y')} - {(row['Publication Date'] + pd.Timedelta(days=0)).strftime('%d.%m.%Y')}"
    else:
        if idx == 0:
            date_range = f"{start_date.strftime('%d.%m.%Y')} - {(row['Publication Date'] + pd.DateOffset(months=1)).strftime('%d.%m.%Y')}"
        elif idx == len(grouped_data) - 1:
            date_range = f"{(row['Publication Date'] - pd.DateOffset(months=1)).strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
        else:
            date_range = f"{(row['Publication Date'] - pd.DateOffset(months=1)).strftime('%d.%m.%Y')} - {(row['Publication Date'] + pd.DateOffset(months=1)).strftime('%d.%m.%Y')}"
    date_labels.append(date_range)
ax1.set_xticklabels(date_labels, rotation=45, ha='right')
ax1.set_xlabel(f'{period_label}')
ax1.set_ylabel('Total Cases')
ax1.set_title(f'Insolvency Cases by {period_label} between {start_date.strftime("%d.%m.%Y")} and {end_date.strftime("%d.%m.%Y")}')
autolabel_counts(ax1, ax1.patches)


# Top cities with highest total insolvency counts
sns.set_palette(sns.color_palette("viridis", n_colors=25))
top_cities_total_count = city_merged_pivot.nlargest(25, 'Count')
sns.barplot(data=top_cities_total_count, x='City', y='Count', ax=ax2)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
ax2.set_title('Top Cities with Highest Total Insolvency Counts')
ax2.set_xlabel('City')
ax2.set_ylabel('Total Insolvency Count')

# Add labels inside the bars
autolabel_counts(ax2, ax2.patches)

plt.tight_layout()

# Create visualizations for states
fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(12, 6))

# States with highest insolvency rates
regional_merged_pivot = regional_merged_pivot.replace({'North Rhine-Westphalia': 'NRW', 'Mecklenburg-Western Pomerania': 'Mecklenburg'})
top_states_rates = regional_merged_pivot.nlargest(16, 'Insolvency Rate')
sns.set_palette(sns.color_palette("viridis", n_colors=16))
sns.barplot(data=top_states_rates, x='State', y='Insolvency Rate', ax=ax3)
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right')
ax3.set_title('German States Ordered by Insolvency Rates')
ax3.set_xlabel('State')
ax3.set_ylabel('Insolvency Rate')

# States with highest total insolvency counts
top_states_total_count = regional_merged_pivot.nlargest(25, 'Count')
sns.barplot(data=top_states_total_count, x='State', y='Count', ax=ax4)
ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45, ha='right')
ax4.set_title('German States Ordered by Total Insolvency Counts')
ax4.set_xlabel('State')
ax4.set_ylabel('Total Insolvency Count')

# Add labels inside the bars
autolabel_counts(ax4, ax4.patches)

plt.tight_layout()
plt.show()

# Create a scatter plot on a geographic map using Plotly Express
fig = px.scatter_geo(city_merged_pivot,
                     lat=city_merged_pivot['Coords'].apply(lambda x: float(x['lat']) if isinstance(x, dict) and 'lat' in x else None),
                     lon=city_merged_pivot['Coords'].apply(lambda x: float(x['lon']) if isinstance(x, dict) and 'lon' in x else None),
                     color='Count',
                     hover_name='City',
                     size='Count',
                     projection='natural earth',
                     title='Insolvency Cases in German Cities',
                     color_continuous_scale='Viridis'
                     )

# Update the geographical scope and axis ranges
fig.update_geos(scope='europe',
                lataxis_range=[47, 55],  # Latitude range for Germany
                lonaxis_range=[5, 16],   # Longitude range for Germany
                )
# Update marker settings for the plot
fig.update_traces(marker=dict(sizemode='diameter', size=city_merged_pivot['Count'] * 0.15, sizemin=2))

# Alternatively, you can use fig.show() to display the plot using the default web browser
def show_in_window(fig):

    """
    Display a Plotly figure in a separate window.

    Parameters:
        fig (plotly.graph_objs.Figure): The Plotly figure to display.

    Note:
        This function uses PyQt5 to display the Plotly figure in a web browser window.
        It saves the figure as an HTML file, loads it in a QWebEngineView widget,
        and shows the widget in a separate window.

    Requires:
        - PyQt5 library
        - plotly.offline library

    Example usage:
        show_in_window(fig)
    """
    
    import sys, os
    import plotly.offline
    from PyQt5.QtCore import QUrl
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtWidgets import QApplication
    
    plotly.offline.plot(fig, filename='name.html', auto_open=False)
    
    app = QApplication(sys.argv)
    web = QWebEngineView()
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "name.html"))
    web.load(QUrl.fromLocalFile(file_path))
    web.show()
    sys.exit(app.exec_())


show_in_window(fig)
#fig.show()
