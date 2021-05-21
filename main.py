"""
This is the main runnable file of the project
"""

import simulation
import actors
import constants as ct
import events as e

import numpy as np
from itertools import count
unique = count()

sim = simulation.Simulation()

def init():
    global sim
    arrival_hours = []
    connection_times = []
    charging_volumes = []

    with open('Data/arrival_hours.csv', 'r') as f:
        arrival_hours = [float(line.strip().split(';')[1].replace(',', '.')) for line in f if 'Arrival' not in line]
    
    with open('Data/connection_time.csv', 'r') as f:
        connection_times = [float(line.strip().split(';')[1].replace(',', '.')) for line in f if 'Connection' not in line]

    with open('Data/charging_volume.csv', 'r') as f:
        charging_volumes = [float(line.strip().split(';')[1].replace(',', '.')) for line in f if 'Charging' not in line]
        charging_volumes = [volume / sum(charging_volumes) for volume in charging_volumes]      # normalise charging probabilities
    
    with open('Data/solar.csv', 'r') as f:
        sim.solar_availability_factor = [tuple(map(float, line.strip().split(',')[1:])) for line in f if 'AVG' not in line]

    for _ in range(ct.N_DAYS):
        # TODO: generate connection_time such that connection_time * 0.7 > charging_time
        n_cars = int(np.random.poisson(lam = ct.N_CARS))
        # print(n_cars)
        
        for i in range(n_cars):
            charging_volume = np.random.choice(a = len(charging_volumes), p = charging_volumes)
            charging_time = int(charging_volume * ct.FRAME + (ct.FRAME * np.random.default_rng().random()) / ct.CHARGING_RATE)      # generate a connection time from the aggregate interval, and add a generate subunit of hour for each car, and then convert it to the charging time
            connection_time = max(np.random.choice(a = len(connection_times), p = connection_times) * ct.FRAME + (ct.FRAME * np.random.default_rng().random()), charging_time / 0.7) # generate a connection time from the aggregate interval, and add a generated subunit of hour 
            arrival_hour = i * 24 + np.random.choice(a = len(arrival_hours), p = arrival_hours) * ct.FRAME + (ct.FRAME * np.random.default_rng().random())                        # generate increasing arrival times for each of the N_DAYS
        
            # print(connection_time)

            sim.events.put((arrival_hour, next(unique), 
                        e.Arrival(actors.Car(arrival_hour = arrival_hour,    
                            connection_time = connection_time,   
                            charging_volume = charging_volume))))
    

if __name__ == '__main__':
    init()
    while not sim.events.empty():
        event_info = sim.events.get()
        sim.state.time = event_info[0]
        # print(sim.state.time)
        event = event_info[2]
        event.event_handler(sim)

    i = 0
    for cable in sim.state.cables:
        # if sim.state.time > 0:
        print(f'Cable: {i}\n \t Current Load: {cable.load}\n \tPercentage of Overload: {100 * cable.overload / float(sim.state.time)}\n \tPercentage of Blackout: {100 * cable.blackout / float(sim.state.time)}\n')
        i += 1
    print(sim.state)

