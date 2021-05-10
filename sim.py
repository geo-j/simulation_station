import numpy as np
from queue import PriorityQueue
from itertools import count
unique = count()

N_DAYS = 7
CAR_DEVIATION = 50
FRAME = 3600    # 1 unit of time = 1s
PARKING_CHECKS = 3
CHARGING_RATE = 6

CABLE_CAPACITY = 200
TRANSFORMER_CAPACITY = 1000
CABLE_PATHS = [     # each of the list indices correspond to a parking spot
                    # 9 marks the capacity of the transformer, all parking spots are connected to the transformer
    [0, 1, 9],      # P1 has cables 0 and 1
    [0, 2, 9],      # P2 has cables 0, and 2
    [0, 3, 9],      # P3 has cables 0, and 3
    [4, 9],         # P4 has cable 4
    [4, 6, 7, 9],   # P5 has cables 4, 6, 7
    [4, 6, 8, 9],   # P6 has cables 4, 6, 8
    [4, 5, 9]       # P7 has cables 4, 5
]

SOLAR_PANELS = [
    (0, []),
    (0, [5, 6]),
    (1, [5, 6]),
    (0, [0, 1, 5, 6]),
    (1, [0, 1, 5, 6])
]

# CHARGING_STRATEGY = 

N_CARS = 50
N_PARKING_SPOTS = 7
PARKING_SPOTS = [60, 80, 60, 70, 60, 60, 50]
PARKING_PREFERENCE = [0.15, 0.15, 0.15, 0.20, 0.15, 0.10, 0.10]
PRICE_PER_KWH = [16, 16, 18, 18, 22, 20]
N_CABLES = 10

time = 0

class ChargingStrategy(object):
    def __init__(self):
        pass

    def start_charge(self):
        pass


class BaseChargingStrategy(ChargingStrategy):
    def __init__(self):
        pass

    def start_charge(self):
        # print(f'Car wants to charge at time {time}')
        return time

class PriceDrivenChargingStrategy(ChargingStrategy):
    def __init__(self):
        pass

    def start_charge(self):
        pass
        
        return 

class Car(object):
    def __init__(self, arrival_hour, connection_time, charging_time):
        self.arrival_hour = arrival_hour
        self.connection_time = connection_time
        self.charging_time = charging_time
        self.planned_departure = arrival_hour + connection_time
        self.parking_spot = -1    # not parked yet

class Event(object):
    def __init__(self):
        pass

    def event_handler(self):
        pass

class CarEvent(Event):
    def __init__(self, car:Car):
        self.car = car

class Arrival(CarEvent):
    def event_handler(self):
        parking_location = np.random.choice(a = len(PARKING_PREFERENCE), size = PARKING_CHECKS, replace = False, p = PARKING_PREFERENCE)
        
        found_spot = False        
        checks = -1
        #print("Some car arrived")
        while not found_spot and checks != 2:
            checks += 1
            found_spot = (PARKING_SPOTS[parking_location[checks]] > state.parking_spots_used[parking_location[checks]])       # check whether there is a free parking spot

        if found_spot:
            #print("Found spot")
            state.n_vehicles += 1
            self.car.parking_spot = parking_location[checks]
            state.parking_spots_used[self.car.parking_spot] += 1
            events.put((time, next(unique), StartCharging(self.car)))

            #print("A car wants to park from " + str(self.car.arrival_hour) + " until " + str(self.car.planned_departure) + " at " + str(parking_location[checks]))
            #print("There are now " + str(state.parking_spots_used[parking_location[checks]]) + " free spots remaining.")
            #print(f"A car wants to park from {str(self.car.arrival_hour)} until {str(self.car.planned_departure)} at {str(parking_location[checks])}")
        else:
            # print("Left")
            state.n_no_space += 1

class StartCharging(CarEvent):
    def event_handler(self):
        # print("We started charging")
        for i in CABLE_PATHS[self.car.parking_spot]:
            state.cables[i].add_charge(CHARGING_RATE)
        
        events.put((time + self.car.charging_time, next(unique), StopCharging(self.car)))

class StopCharging(CarEvent):
    def event_handler(self):
        # print("We stopped charging")
        for i in CABLE_PATHS[self.car.parking_spot]:
            state.cables[i].add_charge(-CHARGING_RATE)
            
        events.put((max(time, self.car.planned_departure), next(unique), Departure(self.car)))

class Departure(CarEvent):
    def event_handler(self):
        state.parking_spots_used[self.car.parking_spot] -= 1
        delay = time - self.car.planned_departure
        if delay > 0:
            state.n_delays += 1
            state.max_delay = max(state.max_delay, delay)
            state.delays_sum += delay

class Cable(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.load = 0
        self.blackout = 0   # > 10% overload
        self.overload = 0
        self.loads = [(0, 0)]   # (time, load)

    def add_charge(self, charge:int):
        old_load = self.load
        self.load += charge
        self.loads.append([time, self.load])
        
        if old_load < self.capacity and self.load > self.capacity:
            self.overload -= time

        if old_load > self.capacity and self.load < self.capacity:
            self.overload += time

        if old_load < self.capacity * 1.1 and self.load > self.capacity * 1.1:
            self.blackout -= time

        if old_load > self.capacity * 1.1 and self.load < self.capacity * 1.1:
            self.blackout += time
    
    def __str__(self):
        return f'Cable:\n \tPercentage of Overload: {100 * self.overload / float(time)}\n \tPercentage of Blackout: {100 * self.blackout / float(time)}\n'

class State(object):
    """- load for each cable
    - >= 10\% overload time per cable
    - overload for each cable
    - overload >= 10\%
    - \# delayed vehicles
    - \# total vehicles
    - total sum of delays
    - \# vehicles that can't find a parking place
    - \# parking spots used for each parking place
    - planned departure time for each vehicle
    - charging volume for each vehicle"""
    def __init__(self):
        self.cables = [Cable(CABLE_CAPACITY) for _ in range(N_CABLES - 1)]
        self.cables.append(Cable(TRANSFORMER_CAPACITY))
        # , Cable(TRANSFORMER_CAPACITY)]
        self.parking_spots_used = [0] * N_PARKING_SPOTS
        self.n_vehicles = 0     # # total vehicles
        self.n_delays   = 0     # # total amount of delayed cars
        self.n_no_space = 0     # # vehicles that couldn't park
        self.delays_sum = 0     # # total sum of the delays
        self.max_delay  = 0     # # maximum delay
    
    def __str__(self):
        return f'State:\n \tParking Spots in Use: {self.parking_spots_used}\n \tTotal # of Vehicles: {self.n_vehicles}\n \tTotal # of Delayed Vehicles: {self.n_delays}\n \tTotal # of Vehicles that Couldn\'t Park: {self.n_no_space}\n \tTotal Amount of Delay: {self.delays_sum}\n \tMax Delay: {self.max_delay}\n\n'

        # print('\tCables:')
        # print(cable for cable in self.cables)

events = PriorityQueue()
state = State()

def init():
    arrival_hours = []
    connection_times = []
    charging_volumes = []
    cars = []
    global events

    with open('Data/arrival_hours.csv', 'r') as f:
        arrival_hours = [float(line.strip().split(';')[1].replace(',', '.')) for line in f if 'Arrival' not in line]
    
    with open('Data/connection_time.csv', 'r') as f:
        connection_times = [float(line.strip().split(';')[1].replace(',', '.')) for line in f if 'Connection' not in line]

    with open('Data/charging_volume.csv', 'r') as f:
        charging_volumes = [float(line.strip().split(';')[1].replace(',', '.')) for line in f if 'Charging' not in line]

    for _ in range(N_DAYS):
        # TODO: generate connection_time such that connection_time * 0.7 > charging_time
        n_cars = int(np.random.normal(loc = N_CARS, scale = CAR_DEVIATION))
        cars = [Car(arrival_hour = i * 24 + np.random.randint(len(arrival_hours)) * FRAME + np.random.randint(FRAME),    # generate increasing arrival times for each of the N_DAYS
        connection_time = np.random.randint(len(connection_times)) * FRAME + np.random.randint(FRAME),                   # generate a connection time from the aggregate interval, and add a generated subunit of hour 
        charging_time   = int(np.random.randint(len(charging_volumes)) * FRAME + np.random.randint(FRAME)) / CHARGING_RATE) for i in range(n_cars)] # generate a connection time from the aggregate interval, and add a generate subunit of hour for each car, and then convert it to the charging time
        for car in cars:
            events.put((car.arrival_hour, next(unique), Arrival(car)))
    

if __name__ == '__main__':
    init()
    while not events.empty():
        event_info = events.get()
        time = event_info[0]
        event = event_info[2]
        event.event_handler()

    print(state)
    for cable in state.cables:
        print(f'{cable}')

