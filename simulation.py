from queue import PriorityQueue
import actors
import constants as ct

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
        self.cables = [actors.Cable(ct.CABLE_CAPACITY) for _ in range(ct.N_CABLES - 1)]
        self.cables.append(actors.Cable(ct.TRANSFORMER_CAPACITY))
        # , Cable(TRANSFORMER_CAPACITY)]
        self.parking_spots_used = [0] * ct.N_PARKING_SPOTS
        self.n_vehicles = 0     # # total vehicles
        self.n_delays   = 0     # # total amount of delayed cars
        self.n_no_space = 0     # # vehicles that couldn't park
        self.delays_sum = 0     # # total sum of the delays
        self.max_delay  = 0     # # maximum delay
    
    def __str__(self):
        return f'State:\n \tParking Spots in Use: {self.parking_spots_used}\n \tTotal # of Vehicles: {self.n_vehicles}\n \tTotal # of Delayed Vehicles: {self.n_delays}\n \tTotal # of Vehicles that Couldn\'t Park: {self.n_no_space}\n \tTotal Amount of Delay: {self.delays_sum}\n \tMax Delay: {self.max_delay}\n\n'

        # print('\tCables:')
        # print(cable for cable in self.cables)


class Simulation(object):
    def __init__(self):
        self.time = 0
        self.state = State()
        self.events = PriorityQueue()