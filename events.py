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

    def schedule_new_car(self, simulation:Simulation) -> bool:
        scheduled_car = None
        # print("")
        for parking_lot in range(ct.N_PARKING_SPOTS):
            # print(simulation.state.parking_queues[parking_lot].qsize())
            if not simulation.state.parking_queues[parking_lot].empty():
                curr_car = simulation.state.parking_queues[parking_lot].get(False)[2]
                # take first car that can be charged
                # print("Checking Charge...")
                # print(simulation.state.charge_possible(curr_car.parking_spot + 1, ct.CHARGING_RATE))
                if  simulation.state.charge_possible(curr_car.parking_spot + 1, ct.CHARGING_RATE):
                    # print(f'Charge possible at {curr_car.parking_spot + 1}')
                    scheduled_car = curr_car
                    break
                else:
                    simulation.state.parking_queues[parking_lot].put((curr_car.arrival_hour, next(unique), curr_car))

        if scheduled_car is not None:
            # print(f'New car scheduled at {simulation.state.time}')
            simulation.events.put((simulation.state.time, next(unique), StartCharging(scheduled_car)))

            # print("Charging new car")
            return True
        
        return False

class StartTracking(Event):
    def event_handler(self, simulation: Simulation):
        pass
        simulation.state.n_vehicles_start = 0
        for i in len(ct.N_PARKING_SPOTS):
            simulation.state.n_vehicles_start += simulation.state.parking_spots_used[i]
        
        # reset variables
        simulation.state.n_delays = 0
        simulation.state.n_no_space = 0
        simulation.state.delays_sum = 0
        simulation.state.max_delay = 0

        for cable in simulation.state.cables:
            if cable.capacity < cable.load:
                cable.overload = -simulation.state.time
            else:
                cable.overload = 0

            if cable.capacity * 1.1 < cable.load:
                cable.blackout = -simulation.state.time
            else: cable.blackout = 0

class StopTracking(Event):
    def __init__(self):
        print("Planned stop tracking")
    def event_handler(self, simulation: Simulation):
        i = 0
        for cable in simulation.state.cables:        
            if cable.capacity < cable.load:
                cable.overload += simulation.state.time
            if cable.capacity * 1.1 < cable.load:
                cable.blackout += -simulation.state.time
            print(f'Cable: {i}\n \t Current Load: {cable.load}\n \tPercentage of Overload: {100 * cable.overload / float(simulation.state.time)}\n \tPercentage of Blackout: {100 * cable.blackout / float(simulation.state.time)}\n')
            i += 1  
        
        print(simulation.state)

        print(f"Arrivals: {ct.ARRIVALS}")
        print(f"Starts: {ct.STARTS}")
        print(f"Changes: {ct.CHANGES}")
        print(f"Stops: {ct.STOPS}")
        print(f"Departures: {ct.DEPARTURES}")


class CarEvent(Event):
    def __init__(self, car:Car):
        self.car = car


class Arrival(CarEvent):
    def schedule_new_car(self, simulation: Simulation):
        scheduled_car = None
        for parking_lot in range(ct.N_PARKING_SPOTS):
            if not simulation.state.parking_queues[parking_lot].empty():
                curr_car = simulation.state.parking_queues[parking_lot].get(False)[2]
                if  scheduled_car is None or curr_car.arrival_hour < scheduled_car.arrival_hour:
                    scheduled_car = curr_car
                else:
                    simulation.state.parking_queues[parking_lot].put((curr_car.arrival_hour, next(unique), curr_car))

        simulation.events.put((simulation.state.time, next(unique), StartCharging(scheduled_car)))

    def event_handler(self, simulation):
        parking_location = np.random.choice(a = len(ct.PARKING_PREFERENCE), size = ct.PARKING_CHECKS, replace = False, p = ct.PARKING_PREFERENCE)
        
        found_spot = False        
        checks = -1
        # print("Some car arrived")
        while not found_spot and checks != 2:
            checks += 1
            found_spot = (ct.PARKING_SPOTS[parking_location[checks]] > simulation.state.parking_spots_used[parking_location[checks]])       # check whether there is a free parking spot

        if found_spot:
            ct.ARRIVALS += 1
            # print(f"Arrivals: {ct.ARRIVALS}")
            simulation.state.n_vehicles += 1
            self.car.parking_spot = parking_location[checks]
            # print(str(self.car.parking_spot + 1) + ": " + str(simulation.state.parking_spots_used[self.car.parking_spot]) + " -> " + str(simulation.state.parking_spots_used[self.car.parking_spot] + 1))
            simulation.state.parking_spots_used[self.car.parking_spot] += 1

            if type(simulation.strategy) is strategies.BaseChargingStrategy or type(simulation.strategy) is strategies.PriceDrivenChargingStrategy:
                simulation.events.put((simulation.state.time, next(unique), StartCharging(self.car)))
            else:   # if the car cannot be parked
                # add car to parking spot queue
                simulation.state.parking_queues[self.car.parking_spot].put((self.car.arrival_hour, next(unique), self.car))
                simulation.events.put((simulation.state.time, next(unique), ChangeNetwork()))

                # schedule another car from the already existing queues
                # self.schedule_new_car(simulation)

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
        if simulation.state.charge_possible(self.car.parking_spot + 1, ct.CHARGING_RATE) or type(simulation.strategy) is strategies.BaseChargingStrategy or type(simulation.strategy) is strategies.PriceDrivenChargingStrategy:
            # print(f"Charging at {self.car.parking_spot + 1}")
            ct.STARTS += 1
            
            self.car.charging_volume -= self.car.charging_rate * (simulation.state.time - self.car.started_charging) / ct.FRAME
            self.car.started_charging = simulation.state.time
            simulation.state.add_charge(self.car.parking_spot, ct.CHARGING_RATE)
            self.car.charging_rate = ct.CHARGING_RATE
            simulation.events.put((simulation.state.time + ct.FRAME * self.car.charging_volume / self.car.charging_rate, next(unique), StopCharging(self.car)))
            simulation.state.charging_cars[self.car.parking_spot].put((self.car.arrival_hour, next(unique), self.car))
            # print()
        else:
            simulation.state.parking_queues[self.car.parking_spot].put((self.car.arrival_hour, next(unique), self.car))
        # check if a car needs to start / stop charging
        if type(simulation.strategy) is not strategies.BaseChargingStrategy and type(simulation.strategy) is not strategies.PriceDrivenChargingStrategy:
            simulation.events.put((simulation.state.time, next(unique), ChangeNetwork()))

class StopCharging(CarEvent):
    def event_handler(self, simulation):
        # print(str(self.car.charging_volume) + ", " + str(self.car.charging_rate * (simulation.state.time - self.car.started_charging)))
        
        # round too?
        if self.car.charging_volume - 1/(float)(1000000) <= self.car.charging_rate * (simulation.state.time - self.car.started_charging) / ct.FRAME:

            print(f"Volume: {self.car.charging_volume}, Rate: {self.car.charging_rate}, Time: {simulation.state.time - self.car.started_charging}")
            print(f"{self.car.charging_volume - 1/(float)(1000000)} <= {self.car.charging_rate * (simulation.state.time - self.car.started_charging) / ct.FRAME}")
            ct.STOPS += 1
            # print(f"Stops: {ct.STOPS}")
            # print(f"Finish charging at {self.car.parking_spot + 1}")
            simulation.state.add_charge(self.car.parking_spot, -ct.CHARGING_RATE)
            simulation.events.put((max(simulation.state.time, self.car.planned_departure), next(unique), Departure(self.car)))
        
            # checking if another car can start charging
                # check overload
                # take the first car that can charge from all the queues
            # if type(simulation.strategy) is not strategies.BaseChargingStrategy or type(simulation.strategy) is not strategies.PriceDrivenChargingStrategy:
            #     self.schedule_new_car(simulation)
        else: 
            print(f"Volume: {self.car.charging_volume}, Rate: {self.car.charging_rate}, Time: {simulation.state.time - self.car.started_charging}") 
            print(f"REJECTED: {self.car.charging_volume - 1/(float)(1000000)} <= {self.car.charging_rate * (simulation.state.time - self.car.started_charging) / ct.FRAME}")

        if type(simulation.strategy) is not strategies.BaseChargingStrategy and type(simulation.strategy) is not strategies.PriceDrivenChargingStrategy:
            simulation.events.put((simulation.state.time, next(unique), ChangeNetwork()))

        # check if a car needs to start / stop charging

class ChangeSolarEnergy(Event):
    def event_handler(self, simulation):
        expected_revenue = ct.SOLAR_PANEL_CAPACITY * simulation.solar_availability_factors[round(simulation.state.time / 3600 % 24)][ct.SEASON]
        actual_revenue = np.random.normal(loc = expected_revenue, scale = 0.15 * expected_revenue)
        # print(f'{actual_revenue}')
        change = actual_revenue - simulation.solar_revenue
        for parking_spot in range(ct.N_PARKING_SPOTS):
            simulation.state.add_energy(parking_spot, change)
        simulation.solar_revenue = actual_revenue
        # check if a car needs to start / stop charging
            # check for preemption
                # stack for each parking spot
                # if preemption allowed, we should check whether a preempted car actually causes an overload; if that is the case, remove vehicle that arrived latest
        simulation.events.put((simulation.state.time, next(unique), ChangeNetwork()))


class ChangeNetwork(Event):
    def event_handler(self, simulation):
        # i = 0
        # for cable in simulation.state.cables:
        #     print(f"{i}: {cable.load}")
        #     i += 1

        # print("")
        # try to preempt cars
        if type(simulation.strategy) is not strategies.BaseChargingStrategy and type(simulation.strategy) is not strategies.PriceDrivenChargingStrategy:
            for parking_lot in range(ct.N_PARKING_SPOTS):
                if simulation.state.causes_overload(parking_lot + 1):
                    #if not simulation.state.charging_cars[parking_lot].empty():
                        print(f"Preempting car at {parking_lot} with {simulation.state.parking_spots_used[parking_lot]} cars")
                        car = simulation.state.charging_cars[parking_lot].get(False)[2]
                        simulation.events.put((simulation.state.time, next(unique), ChangeCharge(car, -ct.CHARGING_RATE)))
        
        # try to schedule new cars
            self.schedule_new_car(simulation)

        

class ChangeCharge(CarEvent):
    def __init__(self, car: Car, change):
        super().__init__(car)
        self.change = change

    def event_handler(self, simulation):
        ct.CHANGES += 1
        # print(f"Changes: {ct.CHANGES}")
        self.car.charging_volume -= self.car.charging_rate * (simulation.state.time - self.car.started_charging) / ct.FRAME
        self.car.charging_rate += self.change
        print(f"New Rate: {self.car.charging_rate}")
        simulation.state.add_charge(self.car.parking_spot, self.change)
        self.car.started_charging = simulation.state.time
        if self.car.charging_rate > 0:
            simulation.events.put((simulation.state.time + ct.FRAME * self.car.charging_volume / self.car.charging_rate, next(unique), StopCharging(self.car)))
        else:
            simulation.events.put((simulation.state.time, next(unique), StartCharging(self.car)))

        if type(simulation.strategy) is not strategies.BaseChargingStrategy and type(simulation.strategy) is not strategies.PriceDrivenChargingStrategy:
            simulation.events.put((simulation.state.time, next(unique), ChangeNetwork()))

        # check if a car needs to start / stop charging

class Departure(CarEvent):
    def event_handler(self, simulation):
        # print(str(self.car.parking_spot + 1) + ": " + str(simulation.state.parking_spots_used[self.car.parking_spot]) + " -> " + str(simulation.state.parking_spots_used[self.car.parking_spot] - 1))
        simulation.state.parking_spots_used[self.car.parking_spot] -= 1
        ct.DEPARTURES += 1
        # print(f"Departures: {ct.DEPARTURES}")
        delay = simulation.state.time - self.car.planned_departure
        # print(f'Planned Departure: {self.car.planned_departure}, Actual Time: {simulation.state.time}')
        if delay > 0:
            simulation.state.n_delays += 1
            simulation.state.max_delay = max(simulation.state.max_delay, delay)
            simulation.state.delays_sum += delay