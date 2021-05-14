"""
This file contains the events that drive the simulation
"""

from actors import Car
import constants as ct
from simulation import Simulation
from main import unique

import numpy as np

class Event(object):
    def __init__(self):
        pass

    def event_handler(self, simulation:Simulation):
        pass

class CarEvent(Event):
    def __init__(self, car:Car):
        self.car = car

class Arrival(CarEvent):
    def event_handler(self, simulation):
        parking_location = np.random.choice(a = len(ct.PARKING_PREFERENCE), size = ct.PARKING_CHECKS, replace = False, p = ct.PARKING_PREFERENCE)
        
        found_spot = False        
        checks = -1
        #print("Some car arrived")
        while not found_spot and checks != 2:
            checks += 1
            found_spot = (ct.PARKING_SPOTS[parking_location[checks]] > simulation.state.parking_spots_used[parking_location[checks]])       # check whether there is a free parking spot

        if found_spot:
            #print("Found spot")
            simulation.state.n_vehicles += 1
            self.car.parking_spot = parking_location[checks]
            simulation.state.parking_spots_used[self.car.parking_spot] += 1
            simulation.events.put((simulation.strategy.start_charge(simulation.time, self.car), next(unique), StartCharging(self.car)))

            # print("A car wants to park from " + str(self.car.arrival_hour) + " until " + str(self.car.planned_departure) + " at " + str(parking_location[checks]))
            #print("There are now " + str(state.parking_spots_used[parking_location[checks]]) + " free spots remaining.")
            #print(f"A car wants to park from {str(self.car.arrival_hour)} until {str(self.car.planned_departure)} at {str(parking_location[checks])}")
        else:
            #print("Left")
            simulation.state.n_no_space += 1

class StartCharging(CarEvent):
    def event_handler(self, simulation):
        # print("We started charging")
        car.charging_start = simulation.time
        car.charging_rate = ct.CHARGING_RATE
        # charging rate should be initiated to 6
        simulation.parking_spots_electricity[car.parking_spot] += car.charging_rate
        for i in ct.CABLE_PATHS[self.car.parking_spot]:
            simulation.state.cables[i].add_charge(ct.CHARGING_RATE, simulation.time)
        
        simulation.events.put((simulation.time + self.car.charging_time, next(unique), StopCharging(self.car)))

class StopCharging(CarEvent):
    # check if charging is complete, if not reschedule start charging at the same time
    def event_handler(self, simulation):
        # print("We stopped charging")
        for i in ct.CABLE_PATHS[self.car.parking_spot]:
            simulation.state.cables[i].add_charge(-ct.CHARGING_RATE, simulation.time)

        car.charging_start = simulation.time
        car.charging_rate = 0
        car.charging_time = -1
        simulation.parking_spots_electricity[car.parking_spot] -= car.charging_rate
            
        simulation.events.put((max(simulation.time, self.car.planned_departure), next(unique), Departure(self.car)))

class ChangeCharging(CarEvent): # changes charging rate
    # how to continue to make sure it speeds up again?
    # when more energy becomes available
    # some state?
    def event_handler(self, simulation: Simulation, charge):
        charging_volume = car.charging_time * car.charging_rate # back to this...
        car.charging_time -= (simulation.time - car.charging_start)
        
        car.charging_start = simulation.time
        car.charging_rate = charge
        if car.charging_rate == 0:
            car.charging_time = -1
        else:
            car.charging_time = charging_volume / car.charging_rate

        # TODO: no stat updates yet

class Departure(CarEvent):
    def event_handler(self, simulation):
        simulation.state.parking_spots_used[self.car.parking_spot] -= 1
        # print(state.parking_spots_used[self.car.parking_spot])
        delay = simulation.time - self.car.planned_departure
        if delay > 0:
            simulation.state.n_delays += 1
            simulation.state.max_delay = max(simulation.state.max_delay, delay)
            simulation.state.delays_sum += delay


class ChangeSolarCharge(Event):
    def event_handler(self, simulation):
        expected_revenue = ct.SOLAR_PANEL_CAPACITY * simulation.solar_availability_factor[simulation.time / 3600 % 24][ct.SEASON]
        actual_revenue = np.random.normal(loc = expected_revenue, scale = 0.15 * expected_revenue)

        # energy decreases:
            # more energy would be required from the transformer
            # some cables may be even more loaded
        # energy increases:
            # less energy would be required from the transformer
            # some cables may be less loaded
