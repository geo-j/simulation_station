from events import StopTracking
from main import init
import strategies as s
import simulation
import pandas as pd
import csv
import constants as ct

def run_sim(run, strategy, scenario = 0):
    print(f'======= Run {run} for {strategy.__name__} in scenario {scenario} =======')
    sim = simulation.Simulation(strategy)
    init(sim)
    while not sim.events.empty():
        event_info = sim.events.get()
        sim.state.time = event_info[0]
        # print(sim.state.time)
        event = event_info[2]
        # print(event, sim.state.time)
        if type(event) is StopTracking:
            with open(f'Results/{strategy.__name__}/{strategy.__name__}_run_{run}.csv', 'a') as f:
                writer = csv.writer(f)
                # n_vehicles,percentage_delays,avg_delay,max_delay, total_delays, n_no_space
                writer.writerow((sim.state.n_vehicles, sim.state.n_delays / sim.state.n_vehicles ,sim.state.delays_sum / sim.state.n_vehicles / 3600 ,sim.state.max_delay / 3600, sim.state.delays_sum, sim.state.n_no_space))

            i = 0
            for cable in sim.state.cables:
                with open(f'Results/{strategy.__name__}/{strategy.__name__}_cables_{ct.SCENARIO}_run_{run}.csv', 'a') as f:
                    writer = csv.writer(f)
                    # max_load, % overload, % blackout
                    writer.writerow((max(cable.loads, key = lambda l: l[1])[1], 100 * cable.overload / (float(sim.state.time) + 1), 100 * cable.blackout / (float(sim.state.time) + 1)))
                i += 1
        event.event_handler(sim)

    i = 0
    for cable in sim.state.cables:
        with open(f'Results/{strategy.__name__}/{strategy.__name__}_cable_{i}_{ct.SCENARIO}_run_{run}.csv', 'a') as f:
            writer = csv.writer(f)
            # time, load
            writer.writerows(cable.loads)
        i += 1

if __name__ == '__main__':
    for run in range(100):
        for strategy in [s.BaseChargingStrategy, s.PriceDrivenChargingStrategy, s.FCFSChargingStrategy, s.ELFSChargingStrategy]:
            for scenario in range(5):
                ct.SCENARIO = scenario
                run_sim(run, strategy, scenario)
        
        