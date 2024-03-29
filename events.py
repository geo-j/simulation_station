"""
This file contains the events that drive the simulation
"""

from actors import Car
import constants as ct
from simulation import Simulation
from main import unique
import strategies
from queue import LifoQueue, PriorityQueue

import numpy as np

def remove_car(simulation, car: Car, queued_cars):
    tmp_stack = type(queued_cars)()
    curr_car = queued_cars.get(False)[2]

    while curr_car != car and not queued_cars.empty():
        tmp_stack.put((simulation.strategy.start_charge(simulation.state.time, curr_car), next(unique), curr_car))
        curr_car = queued_cars.get(False)[2]

    if queued_cars.empty() and curr_car != car:
        print('here')
        queued_cars.put((simulation.strategy.start_charge(simulation.state.time, curr_car), next(unique), curr_car))

    while not tmp_stack.empty():
        car = tmp_stack.get(False)[2]
        queued_cars.put((simulation.strategy.start_charge(simulation.state.time, car), next(unique), car))

class Event(object):
    def __init__(self):
        pass

    def event_handler(self, simulation:Simulation):
        pass

    def schedule_new_car(self, simulation:Simulation) -> bool:
        scheduled_car = None

        for parking_lot in range(ct.N_PARKING_SPOTS):
            if not simulation.state.parking_queues[parking_lot].empty():
                curr_car = simulation.state.parking_queues[parking_lot].get(False)[2]
                # take first car that can be charged
                if  simulation.state.charge_possible(curr_car.parking_spot + 1, ct.CHARGING_RATE) and (scheduled_car is None or simulation.strategy.start_charge(simulation.state.time, curr_car) < simulation.strategy.start_charge(simulation.state.time, scheduled_car)):
                    scheduled_car = curr_car
                
                simulation.state.parking_queues[parking_lot].put((simulation.strategy.start_charge(simulation.state.time, curr_car), next(unique), curr_car))

        if scheduled_car is not None:
            simulation.events.put((simulation.state.time, next(unique), StartCharging(scheduled_car)))
            remove_car(simulation, scheduled_car, simulation.state.parking_queues[scheduled_car.parking_spot])

            return True
        
        return False

class StartTracking(Event):
    def event_handler(self, simulation: Simulation):
        simulation.state.n_vehicles_start = 0
        for i in range(ct.N_PARKING_SPOTS):
            simulation.state.n_vehicles_start += simulation.state.parking_spots_used[i]
        
        # reset variables
        simulation.state.start_time = simulation.state.time
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
        pass
    def event_handler(self, simulation: Simulation):
        i = 0
        for cable in simulation.state.cables:        
            if cable.load > cable.capacity:
                cable.overload += simulation.state.time
            if cable.load > cable.capacity * 1.1:
                cable.blackout += simulation.state.time
            print(f'Cable: {i}\n \t Current Load: {cable.load}\n \tPercentage of Overload {cable.overload}: {100 * cable.overload / float(simulation.state.time - simulation.state.start_time)}\n \tPercentage of Blackout {cable.blackout}: {100 * cable.blackout / float(simulation.state.time - simulation.state.start_time)}\n')
            i += 1  
        
        print(simulation.state)

        print(f"Arrivals: {ct.ARRIVALS}")
        print(f"Starts: {ct.STARTS}")
        print(f"Changes: {ct.CHANGES}")
        print(f"Stops: {ct.STOPS}")
        print(f"Rejects: {ct.REJECTS}")
        print(f"Departures: {ct.DEPARTURES}")


class CarEvent(Event):
    def __init__(self, car:Car):
        self.car = car


class Arrival(CarEvent):
    def event_handler(self, simulation):
        parking_location = np.random.choice(a = len(ct.PARKING_PREFERENCE), size = ct.PARKING_CHECKS, replace = False, p = ct.PARKING_PREFERENCE)
        
        found_spot = False        
        checks = -1
        while not found_spot and checks != 2:
            checks += 1
            found_spot = (ct.PARKING_SPOTS[parking_location[checks]] > simulation.state.parking_spots_used[parking_location[checks]])       # check whether there is a free parking spot

        if found_spot:
            ct.ARRIVALS += 1
            simulation.state.n_vehicles += 1
            self.car.parking_spot = parking_location[checks]
            simulation.state.parking_spots_used[self.car.parking_spot] += 1

            if type(simulation.strategy) is strategies.BaseChargingStrategy or type(simulation.strategy) is strategies.PriceDrivenChargingStrategy:
                simulation.events.put((simulation.strategy.start_charge(simulation.state.time, self.car), next(unique), StartCharging(self.car)))
            else:   # if the car cannot be parked
                # add car to parking spot queue
                simulation.state.parking_queues[self.car.parking_spot].put((simulation.strategy.start_charge(simulation.state.time, self.car), next(unique), self.car))
                simulation.events.put((simulation.state.time, next(unique), ChangeNetwork()))

                # schedule another car from the already existing queues
                # self.schedule_new_car(simulation)

            # put car in the parking spot queue
            # take first car of all the queues that can be charged, schedule its charging
            # if overload detected, stop its charging, put it as first in queue
        else:
            simulation.state.n_no_space += 1

class StartCharging(CarEvent):
    def event_handler(self, simulation):
        if simulation.state.charge_possible(self.car.parking_spot + 1, ct.CHARGING_RATE - self.car.charging_rate) or type(simulation.strategy) is strategies.BaseChargingStrategy or type(simulation.strategy) is strategies.PriceDrivenChargingStrategy:
            ct.STARTS += 1
            
            self.car.charging_volume -= self.car.charging_rate * (simulation.state.time - self.car.started_charging) / ct.FRAME
            self.car.started_charging = simulation.state.time
            simulation.state.add_charge(self.car.parking_spot, ct.CHARGING_RATE - self.car.charging_rate)
            self.car.charging_rate = ct.CHARGING_RATE
            
            simulation.events.put((simulation.state.time + ct.FRAME * self.car.charging_volume / self.car.charging_rate, next(unique), StopCharging(self.car)))
            simulation.state.charging_cars[self.car.parking_spot].put((simulation.strategy.start_charge(simulation.state.time, self.car), next(unique), self.car))
        else:
            simulation.state.parking_queues[self.car.parking_spot].put((simulation.strategy.start_charge(simulation.state.time, self.car), next(unique), self.car))
        # check if a car needs to start / stop charging
        if type(simulation.strategy) is not strategies.BaseChargingStrategy and type(simulation.strategy) is not strategies.PriceDrivenChargingStrategy:
            simulation.events.put((simulation.state.time, next(unique), ChangeNetwork()))

class StopCharging(CarEvent):
    def event_handler(self, simulation):
        if not self.car.done_charging and self.car.charging_volume - 1/float(100000000000) <= self.car.charging_rate * (simulation.state.time - self.car.started_charging) / ct.FRAME:

            self.car.done_charging = True
            ct.STOPS += 1
            self.car.charging_rate = 0
            simulation.state.add_charge(self.car.parking_spot, -ct.CHARGING_RATE)
            simulation.events.put((max(simulation.state.time, self.car.planned_departure), next(unique), Departure(self.car)))
            remove_car(simulation, self.car, simulation.state.charging_cars[self.car.parking_spot])
        # 
        
            # checking if another car can start charging
                # check overload
                # take the first car that can charge from all the queues
            # if type(simulation.strategy) is not strategies.BaseChargingStrategy or type(simulation.strategy) is not strategies.PriceDrivenChargingStrategy:
            #     self.schedule_new_car(simulation)
        else: 
            ct.REJECTS += 1

        if type(simulation.strategy) is not strategies.BaseChargingStrategy and type(simulation.strategy) is not strategies.PriceDrivenChargingStrategy:
            simulation.events.put((simulation.state.time, next(unique), ChangeNetwork()))

        # check if a car needs to start / stop charging

class ChangeSolarEnergy(Event):
    def event_handler(self, simulation):
        expected_revenue = ct.SOLAR_PANEL_CAPACITY * simulation.solar_availability_factors[round(simulation.state.time / 3600 % 24)][ct.SOLAR_PANELS[ct.SCENARIO][0]]
        actual_revenue = np.random.normal(loc = expected_revenue, scale = 0.15 * expected_revenue)
        change = actual_revenue - simulation.solar_revenue
        for parking_spot in ct.SOLAR_PANELS[ct.SCENARIO][1]:
            simulation.state.add_energy(parking_spot, change)
        simulation.solar_revenue = actual_revenue
        # check if a car needs to start / stop charging
            # check for preemption
                # stack for each parking spot
                # if preemption allowed, we should check whether a preempted car actually causes an overload; if that is the case, remove vehicle that arrived latest
        simulation.events.put((simulation.state.time, next(unique), ChangeNetwork()))


class ChangeNetwork(Event):
    def event_handler(self, simulation):
        # try to preempt cars
        if type(simulation.strategy) is not strategies.BaseChargingStrategy and type(simulation.strategy) is not strategies.PriceDrivenChargingStrategy:
            scheduled_car = None
            reduce = ct.CHARGING_RATE
            for parking_lot in range(ct.N_PARKING_SPOTS):
                if simulation.state.causes_overload(parking_lot + 1):
                    if not simulation.state.charging_cars[parking_lot].empty():
                        car = simulation.state.charging_cars[parking_lot].get(False)[2]
                        if scheduled_car is None or simulation.strategy.start_charge(simulation.state.time, car) < simulation.strategy.start_charge(simulation.state.time, scheduled_car):
                            scheduled_car = car
                            # If you want to calculate how much to reduce, like fitting to overload
                            # reduce = min(reduce, simulation.state.overload_amount(parking_lot + 1))
                        simulation.state.charging_cars[parking_lot].put((simulation.strategy.start_charge(simulation.state.time, car), next(unique), car))
            
            if scheduled_car is not None:
                simulation.events.put((simulation.state.time, next(unique), ChangeCharge(scheduled_car, -reduce)))
                remove_car(simulation, scheduled_car, simulation.state.charging_cars[scheduled_car.parking_spot])
        
        # try to schedule new cars
            self.schedule_new_car(simulation)

        

class ChangeCharge(CarEvent):
    def __init__(self, car: Car, change):
        super().__init__(car)
        self.change = change

    def event_handler(self, simulation):
        ct.CHANGES += 1
        self.car.charging_volume -= self.car.charging_rate * (simulation.state.time - self.car.started_charging) / ct.FRAME
        self.car.charging_rate += self.change
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
    # def __str__(self):
        #return f'car arrived at {self.car.arrival_hour} with charging volume {self.car.charging_volume} leaving from {self.car.parking_spot + 1}'
    def event_handler(self, simulation):
        simulation.state.parking_spots_used[self.car.parking_spot] -= 1
        ct.DEPARTURES += 1
        delay = simulation.state.time - self.car.planned_departure
        if delay > 0:
            simulation.state.n_delays += 1
            simulation.state.max_delay = max(simulation.state.max_delay, delay)
            simulation.state.delays_sum += delay