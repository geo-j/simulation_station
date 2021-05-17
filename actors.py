"""
This file contains the classes referring to the variable 'actors' of the simulation: the cars and the cables, whose state changes
"""

class Car(object):
    def __init__(self, arrival_hour, connection_time, charging_time, charging_volume):
        self.arrival_hour = arrival_hour
        self.connection_time = connection_time
        self.charging_time = charging_time
        self.planned_departure = arrival_hour + connection_time
        self.charging_volume = charging_volume
        self.charging_rate = 0
        self.parking_spot = -1    # not parked yet

class Cable(object):
    def __init__(self, capacity, max_flow):
        # max_flow = -1, for infinite maximum flow
        self.min_load = 0
        self.capacity = capacity
        self.max_flow = max_flow
        self.load = 0
        self.blackout = 0   # > 10% overload
        self.overload = 0
        self.loads = [(0, 0)]   # (time, load)

    def add_charge(self, charge:int, time):
        # MAKE SURE IT CAN BECOME NEGATIVE
        old_load = self.load
        self.load += charge
        self.loads.append([time, self.load])

        print("Old Load: " + str(old_load))
        print("New Load: " + str(self.load))
        
        if old_load < self.capacity and self.load > self.capacity:
            self.overload -= time

        if old_load > self.capacity and self.load < self.capacity:
            self.overload += time

        if old_load < self.capacity * 1.1 and self.load > self.capacity * 1.1:
            self.blackout -= time

        if old_load > self.capacity * 1.1 and self.load < self.capacity * 1.1:
            self.blackout += time
        
        # print("Cable has load: " + str(self.load))
    
    # def __str__(self):
    #     return f'Cable:\n \tPercentage of Overload: {100 * self.overload / float(time)}\n \tPercentage of Blackout: {100 * self.blackout / float(time)}\n'