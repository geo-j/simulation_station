"""
This file contains the data structures of the simulation:
- Simulation: class containing the time, event queue and state
- State: class containing all the state properties
"""

from queue import PriorityQueue, Queue, LifoQueue
import actors
import constants as ct
import strategies


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
    def __init__(self, time):
        self.cables = [actors.Cable(ct.CABLE_CAPACITY, -1) for _ in range(ct.N_CABLES - 1)]
        self.cables.append(actors.Cable(ct.TRANSFORMER_CAPACITY, -1))
        self.time = time

        self.cable_network = [
            # [(destination, cable, direction)]
                # direction = 1 away from the transformer
                #            -1 towards the destination
            [(8, self.cables[9], 1)], # 0: Transformer
            [(9, self.cables[1], -1), # 1: Parking Spot
             (15, actors.Cable(0, -1), 0)],
            [(9, self.cables[2], -1), # 2: Parking Spot
             (16, actors.Cable(0, -1), 0)],
            [(9, self.cables[3], -1), # 3: Parking Spot
             (17, actors.Cable(0, -1), 0)],
            [(8, self.cables[4], -1), # 4: Parking Spot
             (7, self.cables[5], 1),
             (10, self.cables[6], 1),
             (18, actors.Cable(0, -1), 0)],
            [(10, self.cables[7], -1), # 5: Parking Spot
             (19, actors.Cable(0, -1), 0)],
            [(10, self.cables[8], -1), # 6: Parking Spot
             (20, actors.Cable(0, -1), 0)],
            [(4, self.cables[5], -1), # 7: Parking Spot
             (21, actors.Cable(0, -1), 0)],
            [(9, self.cables[0], 1), # 8: Junction
             (4, self.cables[4], 1)],
            [(8, self.cables[0], -1), # 9: Junction
             (1, self.cables[1], 1),
             (2, self.cables[2], 1),
             (3, self.cables[3], 1)],
            [(4, self.cables[6], -1), # 10: Junction
             (5, self.cables[7], 1),
             (6, self.cables[8], 1)],
            [(1, actors.Cable(0, 0), 1)], # 11: P1 Source
            [(2, actors.Cable(0, 0), 1)], # 12: P2 Source
            [(6, actors.Cable(0, 0), 1)], # 13: P6 Source
            [(7, actors.Cable(0, 0), 1)], # 14: P7 Source
            [(23, actors.Cable(0, 0), 1)], # 15: P1 Sink
            [(23, actors.Cable(0, 0), 1)], # 16: P2 Sink
            [(23, actors.Cable(0, 0), 1)], # 17: P3 Sink
            [(23, actors.Cable(0, 0), 1)], # 18: P4 Sink
            [(23, actors.Cable(0, 0), 1)], # 19: P5 Sink
            [(23, actors.Cable(0, 0), 1)], # 20: P6 Sink
            [(23, actors.Cable(0, 0), 1)], # 21: P7 Sink
            [(11, actors.Cable(0, -1), 0), # 22: Solar Energy Source
             (12, actors.Cable(0, -1), 0),
             (13, actors.Cable(0, -1), 0),
             (14, actors.Cable(0, -1), 0)],
             # No path from SE source to transformer, that is a secondary source
            [] # 23: Overall Sink
        ]
 
        # , Cable(TRANSFORMER_CAPACITY)]
        self.n_vehicles_start = 0
        self.parking_spots_used = [0] * ct.N_PARKING_SPOTS
        self.n_vehicles = 0     # # total vehicles
        self.n_delays   = 0     # # total amount of delayed cars
        self.n_no_space = 0     # # vehicles that couldn't park
        self.delays_sum = 0     # # total sum of the delays
        self.max_delay  = 0     # # maximum delay
        self.parking_queues = [PriorityQueue() for _ in range(ct.N_PARKING_SPOTS)]
        self.charging_cars = [LifoQueue() for _ in range(ct.N_PARKING_SPOTS)]



    def add_charge(self, parking_spot, charge):
        self.cable_network[15 + parking_spot][0][1].max_flow += charge
        self.calc_flow()
        
    def add_energy(self, parking_spot, energy):
        # give index 0...6
        # 1: 0
        # 2: 1
        # 6: 2
        # 7: 3
        index = parking_spot
        if(parking_spot >= 2 and parking_spot <= 4):
            return
        if(parking_spot > 5):
            index -= 3
        self.cable_network[11 + index][0][1].max_flow += energy
        if self.cable_network[11 + index][0][1].max_flow < 1 / float(1000000):
            self.cable_network[11 + index][0][1].max_flow = 0
        self.calc_flow()

    def causes_overload(self, parking_spot):
        # return True to test if overload is allowed
        sources = [11, 12, 13, 14, 0]

        for source in sources:
            (cables, bottleneck) = self.bfs(source, parking_spot)
            for i in range(len(cables)):
                if (cables[i][1].load * cables[i][2] > 0 ) and cables[i][1].capacity != 0 and abs(cables[i][1].load) > cables[i][1].capacity:
                    # print(f"Cable: {cables[i]} with {cables[i][1].load} and direction {cables[i][2]} > 0 and {abs(cables[i][1].load)} > {cables[i][1].capacity}")
                    return True
            
        return False

    # Not used right now - extension to fit changecharge to prevent overload exactly
    def overload_amount(self, parking_spot):
        # return amount of overload on path
        sources = [11, 12, 13, 14, 0]

        maximum = 0
        for source in sources:
            (cables, bottleneck) = self.bfs(source, parking_spot)
            for i in range(len(cables)):
                if (cables[i][1].load * cables[i][2] > 0 ) and cables[i][1].capacity != 0 and abs(cables[i][1].load) > cables[i][1].capacity:
                    maximum = max(maximum, abs(cables[i][1].load) - cables[i][1].capacity)
            
        return maximum

    def charge_possible(self, parking_spot, rate):
        # return True to test if overload is allowed
        (cables, bottleneck) = self.bfs(22, parking_spot)
        if(bottleneck == 0):
            (cables, bottleneck) = self.bfs(0, parking_spot)

        if bottleneck < rate and bottleneck >= 0:
            return False
        
        for i in range(len(cables)):
            if cables[i][1].load * cables[i][2] + rate > cables[i][1].capacity:
                return False
            
        return True

    def calc_flow(self):
        #Could be optimised: call add_charge once per cable per calc_flow
        start = 22
        transformer = 0
        goal = 23
        
        for i in range(len(self.cable_network)):
            for j in range(len(self.cable_network[i])):
                self.cable_network[i][j][1].add_charge(-self.cable_network[i][j][1].load, self.time)

        # Uses all solar energy
        (cables, bottleneck) = self.bfs(start, goal)
        while bottleneck > 0:
            for i in range(len(cables)):
                cables[i][1].add_charge(bottleneck * cables[i][2], self.time)
            
            (cables, bottleneck) = self.bfs(start, goal)

        # Uses transformer
        (cables, bottleneck) = self.bfs(transformer, goal)
        while bottleneck > 0:
            for i in range(len(cables)):
                cables[i][1].add_charge(bottleneck * cables[i][2], self.time)
            
            (cables, bottleneck) = self.bfs(transformer, goal)

        (cables, bottleneck) = self.bfs(start, transformer)
        while bottleneck > 0:
            for i in range(len(cables)):
                cables[i][1].add_charge(bottleneck * cables[i][2], self.time)
            
            (cables, bottleneck) = self.bfs(start, transformer)

    def bfs(self, start, goal):
        visited = [False] * len(self.cable_network)
        previous = [(-1, ())] * len(self.cable_network)
        bottleneck = [-1] * len(self.cable_network)
        queue = Queue()
        queue.put(start)

        epsilon = 1 / (float)(1000000)

        def visit(vertex):
            if vertex == goal:
                path = []
                backtracking = previous[goal]
                while backtracking[0] >= 0:
                    path.append(backtracking[1])
                    backtracking = previous[backtracking[0]]
                return (path, bottleneck[goal])

            visited[vertex] = True
            for i in range(len(self.cable_network[vertex])):
                cable = self.cable_network[vertex][i][1]
                target = self.cable_network[vertex][i][0]
                if (not visited[target] and (abs(cable.load) < cable.max_flow or cable.max_flow < 0)):
                    queue.put(target)
                    previous[target] = (vertex, self.cable_network[vertex][i])
                    if cable.max_flow < 0:
                        bottleneck[target] = bottleneck[vertex]
                    elif bottleneck[vertex] < 0:
                        bottleneck[target] = cable.max_flow - abs(cable.load)
                    else:
                        bottleneck[target] = min(bottleneck[vertex], cable.max_flow - abs(cable.load))

            return ([], 0)

        while(not queue.empty()):
            result = visit(queue.get())
            if (abs(result[1]) > epsilon):
                return result
        
        return ([], 0)
        
    def __str__(self):
        return f'State:\n \tParking Spots in Use: {self.parking_spots_used}\n \tTotal # of Vehicles: {self.n_vehicles}\n \tTotal # of Delayed Vehicles: {self.n_delays}\n \tTotal # of Vehicles that Couldn\'t Park: {self.n_no_space}\n \tTotal Amount of Delay: {self.delays_sum}\n \tMax Delay: {self.max_delay}\n\n'


class Simulation(object):
    def __init__(self, strategy):
        self.start_time = 0
        self.state = State(time = 0)
        self.events = PriorityQueue()
        self.strategy = strategy
        self.solar_availability_factors = []
        self.solar_revenue = 0