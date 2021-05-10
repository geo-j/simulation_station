import numpy as np
from queue import PriorityQueue
from itertools import count
unique = count()

N_DAYS = 7
CAR_DEVIATION = 50
FRAME = 10000
PARKING_CHECKS = 3

N_CARS = 50
N_PARKING_SPOTS = 7
PARKING_SPOTS = [60, 80, 60, 70, 60, 60, 50]
PARKING_PREFERENCE = [0.15, 0.15, 0.15, 0.20, 0.15, 0.10, 0.10]
PRICE_PER_KWH = [16, 16, 18, 18, 22, 20]
N_CABLES = 9

class Car(object):
    def __init__(self, arrival_hour, connection_time, charging_volume):
        self.arrival_hour = arrival_hour
        self.connection_time = connection_time
        self.charging_volume = charging_volume
        self.planned_departure = arrival_hour + connection_time

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
        while not found_spot and checks != 2:
            checks += 1
            found_spot = (PARKING_SPOTS[parking_location[checks]] > state.parking_spots_used[parking_location[checks]])       # check whether there is a free parking spot

        if found_spot:
            state.parking_spots_used[parking_location[checks]] += 1
            print("A car wants to park from " + str(self.car.arrival_hour) + " until " + str(self.car.planned_departure) + " at " + str(parking_location[checks]))
            print("There are now " + str(state.parking_spots_used[parking_location[checks]]) + " free spots remaining.")
            print(f"A car wants to park from {str(self.car.arrival_hour)} until {str(self.car.planned_departure)} at {str(parking_location[checks])}")
        else:
            print("A car left")
        # print(parking_location.len)
        # 
        # either leave, or park

class StartCharging(CarEvent):
        pass

class StopCharging(CarEvent):
    pass

class Departure(CarEvent):
    pass

class Cable(object):
    def __init__(self):
        self.load = 0
        self.overload = 0   # > 10% overload
        self.total_overload = 0
        self.loads = [(0, 0)]   # (time, load)

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
        self.cables = [Cable()] * N_CABLES
        self.parking_spots_used = [0] * N_PARKING_SPOTS
        self.n_vehicles = 0     # # total vehicles
        self.n_delays   = 0     # # total amount of delayed cars
        self.n_no_space = 0     # # vehicles that couldn't park
        self.delays_sum = 0     # # total sum of the delays

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

    for i in range(N_DAYS):
        n_cars = int(np.random.normal(loc = N_CARS, scale = CAR_DEVIATION))
        cars = [Car(arrival_hour = i * 24 + np.random.randint(len(arrival_hours)) + np.random.randint(FRAME) / float(FRAME),    # generate increasing arrival times for each of the N_DAYS
        connection_time = np.random.randint(len(connection_times)) + np.random.randint(FRAME) / float(FRAME),                   # generate a connection time from the aggregate interval, and add a generated subunit of hour 
        charging_volume = np.random.randint(len(charging_volumes)) + np.random.randint(FRAME) / float(FRAME)) for i in range(n_cars)] # generate a connection time from the aggregate interval, and add a generate subunit of hour for each car
        for car in cars:
            events.put((car.arrival_hour, next(unique), Arrival(car)))
    

if __name__ == '__main__':
    init()
    while not events.empty():
        event = events.get()[2]
        event.event_handler()
