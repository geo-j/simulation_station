import simulation
import actors
import constants as ct
import events as e

import numpy as np
from itertools import count
unique = count()

sim = simulation.Simulation()

def init():
    arrival_hours = []
    connection_times = []
    charging_volumes = []
    global events

    with open('Data/arrival_hours.csv', 'r') as f:
        arrival_hours = [float(line.strip().split(';')[1].replace(',', '.')) for line in f if 'Arrival' not in line]
    
    with open('Data/connection_time.csv', 'r') as f:
        connection_times = [float(line.strip().split(';')[1].replace(',', '.')) for line in f if 'Connection' not in line]

    with open('Data/charging_volume.csv', 'r') as f:
        charging_volumes = [float(line.strip().split(';')[1].replace(',', '.')) for line in f if 'Charging' not in line]
        charging_volumes = [volume / sum(charging_volumes) for volume in charging_volumes]      # normalise charging probabilities

    for _ in range(ct.N_DAYS):
        # TODO: generate connection_time such that connection_time * 0.7 > charging_time
        n_cars = int(np.random.normal(loc = ct.N_CARS, scale = ct.CAR_DEVIATION))
        
        for i in range(n_cars):
            connection_time = np.random.choice(a = len(connection_times), p = connection_times) * ct.FRAME + np.random.randint(ct.FRAME) # generate a connection time from the aggregate interval, and add a generated subunit of hour 
            charging_time = int(min(np.random.choice(a = len(charging_volumes), p = charging_volumes) * ct.FRAME + np.random.randint(ct.FRAME) / ct.CHARGING_RATE, connection_time * 0.7))      # generate a connection time from the aggregate interval, and add a generate subunit of hour for each car, and then convert it to the charging time
            arrival_hour = i * 24 + np.random.choice(a = len(arrival_hours), p = arrival_hours) * ct.FRAME + np.random.randint(ct.FRAME)                        # generate increasing arrival times for each of the N_DAYS
        
            print(connection_time)

            sim.events.put((arrival_hour, next(unique), 
                        e.Arrival(actors.Car(arrival_hour = arrival_hour,    
                            connection_time = connection_time,                  
                            charging_time   = charging_time))))
    

if __name__ == '__main__':
    init()
    while not sim.events.empty():
        event_info = sim.events.get()
        sim.time = event_info[0]
        event = event_info[2]
        event.event_handler(sim)

    print(sim.state)
    for cable in sim.state.cables:
        print(f'Cable:\n \tPercentage of Overload: {100 * cable.overload / float(sim.time)}\n \tPercentage of Blackout: {100 * cable.blackout / float(sim.time)}\n')

