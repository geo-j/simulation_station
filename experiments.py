from events import StopTracking
from main import init
import strategies as s
import simulation
import pandas as pd
import csv
import constants as ct

def run_sim(strategy):
    sim = simulation.Simulation(strategy)
    init(sim)
    while not sim.events.empty():
        event_info = sim.events.get()
        sim.state.time = event_info[0]
        # print(sim.state.time)
        event = event_info[2]
        # print(event, sim.state.time)
        if type(event) is StopTracking:
            with open(f'Results/{strategy.__name__}/{strategy.__name__}_{ct.SCENARIO}.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow((sim.state.n_vehicles, sim.state.n_delays / sim.state.n_vehicles ,sim.state.delays_sum / sim.state.n_vehicles / 3600 ,sim.state.max_delay / 3600, sim.state.n_no_space))

            i = 0
            for cable in sim.state.cables:
                with open(f'Results/{strategy.__name__}/{strategy.__name__}_cables_{ct.SCENARIO}.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow((100 * cable.overload / (float(sim.state.time) + 1), 100 * cable.blackout / (float(sim.state.time) + 1)))
                i += 1
        i = 0
        for cable in sim.state.cables:
            with open(f'Results/{strategy.__name__}/{strategy.__name__}_cable_{i}_{ct.SCENARIO}.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow((sim.state.time, cable.load))
            i += 1
        event.event_handler(sim)

if __name__ == '__main__':
    for strategy in [s.BaseChargingStrategy, s.PriceDrivenChargingStrategy]:            
        # run_sim(strategy)
        pass
        
    for strategy in [s.FCFSChargingStrategy, s.ELFSChargingStrategy]:
        for scenario in range(4):
            ct.SCENARIO = scenario
            run_sim(strategy)
        
        