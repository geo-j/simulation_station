import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm, sem
import strategies as s
import constants as ct


CONFIDENCE_LEVEL = 0.95
DEGREES_FREEDOM = 20

def all_cis():
    df = pd.read_csv('Results/all_runs_stats.csv', names = ['run', 'strategy', 'scenario', 'n_vehicles', 'percentage_delays', 'hour_avg_delays', 'hour_max_delays', 'total_delays', 'n_no_space'])
    df['total_delays'] = df['total_delays'].divide(3600)
    significant_dfs = set()
    # print(df[df['strategy'] == 'BaseChargingStrategy'])
    # print(df.groupby(['strategy', 'run', 'scenario']).head())
    measure = 'hour_max_delays'
    for strategy1 in df.strategy.unique():
        for scenario1 in df.scenario.unique():
            for strategy2 in df.strategy.unique():
                for scenario2 in df.scenario.unique():
                    if strategy1 != strategy2 and scenario1 != scenario2:
                        df_strategy1 = df[df['strategy'] == strategy1]
                        # print(df_strategy1)
                        df_strategy1 = df_strategy1[df_strategy1['scenario'] == scenario1]
                        mean1 = df_strategy1[measure].mean()
                        sem1 = sem(df_strategy1[measure])
                        ci1 = norm.interval(CONFIDENCE_LEVEL, mean1, sem1)
                        # plt.hist(df_strategy1[measure])
                        # plt.show()

                        df_strategy2 = df[df['strategy'] == strategy2]
                        df_strategy2 = df_strategy2[df_strategy2['scenario'] == scenario2]
                        # print(df_strategy2)
                        mean2 = df_strategy2[measure].mean()
                        sem2 = sem(df_strategy2[measure])
                        ci2 = norm.interval(CONFIDENCE_LEVEL,  mean2, sem2)
                        # plt.hist(df_strategy2[measure])
                        # plt.show()

                        # print(ci2)
                        # print(ci1, ci2, max(ci1, ci2, key = lambda c: c[1])[0], min(ci1, ci2, key = lambda c: c[1])[1])

                        if max(ci1, ci2, key = lambda c: c[1])[0] > min(ci1, ci2, key = lambda c: c[1])[1]:
                            print(ci1, ci2)
                            significant_dfs.add((strategy1, scenario1))
                            significant_dfs.add((strategy2, scenario2))

    plots = []
    for (strategy, scenario) in significant_dfs:
        df_strategy = df[df['strategy'] == strategy]
                        # print(df_strategy1)
        df_strategy = df_strategy[df_strategy['scenario'] == scenario]
        # print(df_strategy[measure])
        # df_strategy[measure].boxplot(by = measure)
        plots.append(df_strategy[measure])
        # plt.show()
        # if i == 2:
        #     break
    plt.boxplot(plots)
    plt.show()

# TODO: plot the load over time for each cable for each strategy, maybe choose the extremes - no solar panels, all solar panels in summer + overload axes for 1 run
def load_over_time():
    for strategy in [s.BaseChargingStrategy, s.PriceDrivenChargingStrategy, s.FCFSChargingStrategy, s.ELFSChargingStrategy]:
        for scenario in range(5):
            for i in range(10):
                df_cables = pd.read_csv(f'Results/{strategy.__name__}_cable_{i}.csv', names = ['n_run', 'scenario', 'time', 'load', 'overload', 'blackout'])
                df_cables = df_cables[df_cables['scenario'] == scenario]
                df_cables = df_cables[df_cables['n_run'] == 0]
                df_cables = df_cables['time'].div(3600)


                if i < 9:
                    df_cables = df_cables[['load', 'overload', 'blackout']].div(200)
                    plt.plot(df_cables['load'], label = f'cable {i}')
                else:
                    df_cables = df_cables[['load', 'overload', 'blackout']].div(1000)
                    plt.plot(df_cables['load'], label = 'transformer')


                plt.axhline(y = 1, color = 'r', linestyle = '-', label = 'overload')
                plt.axhline(y = 1.1, color = 'black', linestyle = '-', label = 'blackout')
                plt.legend(loc = 'best')
                plt.xlabel('time')
                plt.ylabel('% load')
                plt.title(f'Cable Load Over Time for Strategy {strategy.__name__} in Scenario {scenario}')
                plt.show()


# TODO: plot used parking spots in time for 1 run
def parking_spots_occupation():
    df_parking_spots = pd.read_csv(f'Results/parking_spots.csv', names = ['n_run', 'strategy', 'scenario', 'time', 'parking_spot', 'n_spots'])
    for strategy in df_parking_spots.strategy.unique():
        for scenario in df_parking_spots.scenario.unique():
            df = df_parking_spots[df_parking_spots['strategy'] == strategy]
            df = df[df['scenario'] == scenario]

            for parking_spot in df.parking_spot.unique():
                df_p = df[df['parking_spot'] == parking_spot]
                df_p = df_p['n_spots'].div(ct.PARKING_SPOTS[parking_spot])

                plt.plot(df_p['n_spots'], label = f'P{parking_spot + 1}, max {ct.PARKING_SPOTS[parking_spot]} cars')
            
            plt.show()
            
# TODO: table avg max delay for each strategy + each season
def avg_max_delay():
    df = pd.read_csv('Results/all_runs_stats.csv', names = ['run', 'strategy', 'scenario', 'n_vehicles', 'percentage_delays', 'hour_avg_delays', 'hour_max_delays', 'total_delays', 'n_no_space'])
    df.groupby(['strategy', 'scenario'])['hour_max_delays'].to_csv('max_delays_table.csv')

# TODO: table with average #delayed/(#total+#delayed) for each strategy + each season 
def avg_delayed():
    df = pd.read_csv('Results/all_runs_stats.csv', names = ['run', 'strategy', 'scenario', 'n_vehicles', 'percentage_delays', 'hour_avg_delays', 'hour_max_delays', 'total_delays', 'n_no_space'])
    df = df.groupby(['strategy', 'scenario'])
    df['avg_delayed'] = df['percentage_delays'] / (df['percentage_delays'] + df['n_vehicles'])
    df['hour_max_delays'].to_csv('avg_delayed_table.csv')

# TODO: allpairwise comparison - table
def pairwise_comparison():
    df_runs = pd.read_csv('Results/all_runs_stats.csv', names = ['run', 'strategy', 'scenario', 'n_vehicles', 'percentage_delays', 'hour_avg_delays', 'hour_max_delays', 'total_delays', 'n_no_space'])
    df_cables = pd.read_csv('Results/all_runs_cables_stats.csv', names = ['run', 'strategy', 'scenario', 'cable', 'max_load'])
    df = df_runs.merge(df_cables, how = 'inner')

    for cable in df.cable.unique():
        if cable < 10:
            df = df[df['cable'] == cable]['max_load'].div(ct.CABLE_CAPACITY)
        else:
            df = df[df['cable'] == cable]['max_load'].div(ct.TRANSFORMER_CAPACITY)


    w1 = 0.5
    w2 = 0.5
    df['custom_measure'] = df['percentage_delays'] * w1 + df['max_load'] * w2
