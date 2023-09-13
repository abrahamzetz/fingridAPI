# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
pd.set_option('display.max_columns', None)



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

def get_fingrid_data(url):
    """fetching Fingrid data as a dataframe, with full url as the parameter"""
    headers = {'x-api-key': 'VKzlMiSNpW6HYJxEh4Xs2PFOdl6P9HSana1aGQJf'}

    response = requests.get(url=url, headers=headers)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

    return pd.json_normalize((data))

def aggregate_df(df, aggregate_by):
    """aggregate df by D (daily) or M (monthly)"""
    if aggregate_by in ['D', 'M']:
        agg_df = df.resample(aggregate_by).sum()
        offset = pd.offsets.Day(-1) if aggregate_by == 'D' else pd.offsets.MonthBegin(-1)
        agg_df.index += offset
        agg_df['wind_pcg'] = agg_df['value_wind_generation'] / agg_df['value_consumption']
        return agg_df
    else:
        print('Value of aggregate_by needs to be "D" or "M"')


def show_wind_pcg(df):
    """show a linechart with wind energy production percentages, requires df from get_fingrid_data"""
    sns.lineplot(data=df,
                 x='start_time',
                 y='wind_pcg')
    plt.title('Wind Generation Coverage of Total Energy Consumption in Finland')
    plt.show()

def show_wind_vs_consumption(df):
    """show a linechart with 2 lines to show wind energy production vs energy consumption. Requires df from get_fingrid_data()"""
    sns.lineplot(data=df,
                 x='start_time',
                 y='value_wind_generation',
                 label='Wind Energy Generation')

    sns.lineplot(data=df,
                 x='start_time',
                 y='value_consumption',
                 label='Energy Consumption')

    plt.title('Energy Consumption in Finland vs Wind Production')
    plt.legend()
    plt.show()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    consumption_url = 'https://api.fingrid.fi/v1/variable/124/events/json?start_time=2023-01-01T00%3A00%3A00Z&end_time=2023-08-31T23%3A59%3A59Z'
    wind_generation_url = 'https://api.fingrid.fi/v1/variable/75/events/json?start_time=2023-01-01T00%3A00%3A00Z&end_time=2023-08-31T23%3A59%3A59Z'

    consumption_df = get_fingrid_data(consumption_url)
    wind_generation_df = get_fingrid_data(wind_generation_url)

    energy_df = pd.merge(consumption_df, wind_generation_df, how='left', on=['start_time', 'end_time'], suffixes=('_consumption', '_wind_generation'))
    energy_df['other_source'] = energy_df['value_consumption'] - energy_df['value_wind_generation']
    energy_df['wind_pcg'] = energy_df['value_wind_generation'] / energy_df['value_consumption']

    energy_df.drop(columns='end_time', inplace=True)
    energy_df['start_time'] = pd.to_datetime(energy_df['start_time'])
    energy_df = energy_df.set_index('start_time')


    agg_df = energy_df.resample('D').sum()
    agg_df.index = agg_df.index + pd.offsets.Day(-1)
    agg_df['wind_pcg'] = agg_df['value_wind_generation'] / agg_df['value_consumption']
    print(agg_df)

    daily_energy = aggregate_df(energy_df, 'D')

    monthly_energy = aggregate_df(energy_df, aggregate_by='M')

    show_wind_vs_consumption(daily_energy)
    #show_wind_pcg(daily_energy)

#    show_wind_vs_consumption(monthly_energy)
#    show_wind_pcg(monthly_energy)
