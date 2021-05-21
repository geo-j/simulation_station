"""
This file contains the events that drive the simulation
"""

from actors import Car
import constants as ct
from simulation import Simulation
from main import unique
import strategies
from copy import deepcopy

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
        # print("Some car arrived")
        while not found_spot and checks != 2:
            checks += 1
            found_spot = (ct.PARKING_SPOTS[parking_location[checks]] > simulation.state.parking_spots_used[parking_location[checks]])       # check whether there is a free parking spot

        if found_spot:
            simulation.state.n_vehicles += 1
            self.car.parking_spot = parking_location[checks]
            # print(str(self.car.parking_spot + 1) + ": " + str(simulation.state.parking_spots_used[self.car.parking_spot]) + " -> " + str(simulation.state.parking_spots_used[self.car.parking_spot] + 1))
            simulation.state.parking_spots_used[self.car.parking_spot] += 1

            if type(simulation.strategy) is strategies.BaseChargingStrategy or type(simulation.strategy) is strategies.PriceDrivenChargingStrategy:
                simulation.events.put((simulation.strategy.start_charge(simulation.state.time, self.car), next(unique), StartCharging(self.car)))
            else:
                simulation.state.parking_queues[self.car.parking_spot].put((self.car.arrival_hour, next(unique), self.car))
                scheduled_car = None
                for parking_lot in simulation.state.parking_queues:
                    if not parking_lot.empty():
                        curr_car = parking_lot.get(False)[2]
                        if  scheduled_car is None or curr_car.arrival_hour < scheduled_car.arrival_hour:
                            scheduled_car = curr_car
                        else:
                            parking_lot.put((curr_car.arrival_hour, next(unique), curr_car))

                simulation.events.put((simulation.strategy.start_charge(simulation.state.time, scheduled_car), next(unique), StartCharging(scheduled_car)))

            # put car in the parking spot queue
            # take first car of all the queues that can be charged, schedule its charging
            # if overload detected, stop its charging, put it as first in queue


            # print("A car wants to park from " + str(self.car.arrival_hour) + " until " + str(self.car.planned_departure) + " at " + str(parking_location[checks]))
            #print("There are now " + str(state.parking_spots_used[parking_location[checks]]) + " free spots remaining.")
            #print(f"A car wants to park from {str(self.car.arrival_hour)} until {str(self.car.planned_departure)} at {str(parking_location[checks])}")
        else:
            # print("Left")
            simulation.state.n_no_space += 1

class StartCharging(CarEvent):
    def event_handler(self, simulation):
        # print(simulation.state.charge_possible(self.car.parking_spot + 1, ct.CHARGING_RATE))
        if simulation.state.charge_possible(self.car.parking_spot + 1, ct.CHARGING_RATE):
            print(f"Charging at {self.car.parking_spot + 1}")
            self.car.started_charging = simulation.state.time
            simulation.state.add_charge(self.car.parking_spot, ct.CHARGING_RATE)
            self.car.charging_rate = ct.CHARGING_RATE
            simulation.events.put((simulation.state.time + 3600 * self.car.charging_volume / self.car.charging_rate, next(unique), StopCharging(self.car)))
            print()
        else:
            simulation.state.parking_queues[self.car.parking_spot].put((self.car.arrival_hour, next(unique), self.car))
        # check if a car needs to start / stop charging

class StopCharging(CarEvent):
    def event_handler(self, simulation):
        # print(str(self.car.charging_volume) + ", " + str(self.car.charging_rate * (simulation.state.time - self.car.started_charging)))
        if self.car.charging_volume <= round(self.car.charging_rate * (simulation.state.time - self.car.started_charging), 4):
            print(f"Finish charging at {self.car.parking_spot + 1}")
            simulation.state.add_charge(self.car.parking_spot, -ct.CHARGING_RATE)
            simulation.events.put((max(simulation.state.time, self.car.planned_departure), next(unique), Departure(self.car)))
        
        # check if a car needs to start / stop charging

class ChangeSolarEnergy(Event):
    def event_handler(self, simulation):
        expected_revenue = ct.SOLAR_PANEL_CAPACITY * simulation.solar_availability_factor[simulation.time / 3600 % 24][ct.SEASON]
        actual_revenue = np.random.normal(loc = expected_revenue, scale = 0.15 * expected_revenue)
        change = actual_revenue - simulation.solar_revenue
        for parking_spot in ct.N_PARKING_SPOTS:
            simulation.add_energy(parking_spot, change)
        # check if a car needs to start / stop charging
        simulation.solar_revenue = actual_revenue

class ChangeCharge(CarEvent):
    def event_handler(self, simulation, change):
        self.car.charging_volume -= self.car.charging_rate * (simulation.state.time - self.car.started_charging) / 3600
        simulation.state.add_charge(self.car.parking_spot, change)
        self.car.started_charging = simulation.state.time
        if self.car.charging_rate > 0:
            simulation.events.put((simulation.state.time + self.car.charging_volume / self.car.charging_rate, next(unique), StopCharging(self.car)))

        # check if a car needs to start / stop charging

class Departure(CarEvent):
    def event_handler(self, simulation):
        # print(str(self.car.parking_spot + 1) + ": " + str(simulation.state.parking_spots_used[self.car.parking_spot]) + " -> " + str(simulation.state.parking_spots_used[self.car.parking_spot] - 1))
        simulation.state.parking_spots_used[self.car.parking_spot] -= 1
        delay = simulation.state.time - self.car.planned_departure
        # print(f'Planned Departure: {self.car.planned_departure}, Actual Time: {simulation.state.time}')
        if delay > 0:
            simulation.state.n_delays += 1
            simulation.state.max_delay = max(simulation.state.max_delay, delay)
            simulation.state.delays_sum += delay