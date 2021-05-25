"""
This file contains the classes referring to the variable 'actors' of the simulation: the cars and the cables, whose state changes
"""

class Car(object):
    def __init__(self, arrival_hour, connection_time, charging_volume):
        self.done_charging = False
        self.arrival_hour = arrival_hour
        self.connection_time = connection_time
        self.planned_departure = arrival_hour + connection_time
        self.charging_volume = charging_volume
        self.charging_rate = 0
        self.parking_spot = -1    # not parked yet
        self.started_charging = -1
    
    def __str__(self):
        return f'Car arrived at {self.arrival_hour}'

    def  __eq__(self, T):
         if self.arrival_hour == T.arrival_hour and self.charging_volume == T.charging_volume and self.parking_spot == T.parking_spot:
             return True
         else:
             return False


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
        # assumes no jumps of over 400 lol

        old_load = self.load
        self.load += charge
        self.loads.append([time, self.load])

        # if not (old_load == 0 and self.load == 0):
            # print(f"{old_load} => {self.load}")

        # print("Old Load: " + str(old_load))
        # print("New Load: " + str(self.load))
        
        if abs(old_load) < self.capacity and abs(self.load) > self.capacity:
            # print("entered overload")
            self.overload -= time

        if abs(old_load) > self.capacity and abs(self.load) < self.capacity:
            # print("exit overload")
            self.overload += time

        if abs(old_load) < self.capacity * 1.1 and abs(self.load) > self.capacity * 1.1:
            # print("entered blackout")
            self.blackout -= time

        if abs(old_load) > self.capacity * 1.1 and abs(self.load) < self.capacity * 1.1:
            # print("exit blackout")
            self.blackout += time
        
        # print("Cable has load: " + str(self.load))
    
    # def __str__(self):
    #     return f'Cable:\n \tPercentage of Overload: {100 * self.overload / float(time)}\n \tPercentage of Blackout: {100 * self.blackout / float(time)}\n'