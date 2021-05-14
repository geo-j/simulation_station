"""
This file contains the implementation of the different charging strategies applied in the simulation
"""
from actors import Car
import constants as ct

class ChargingStrategy(object):
    def __init__(self):
        pass

    def start_charge(self, time, car:Car):
        pass


class BaseChargingStrategy(ChargingStrategy):
    def __init__(self):
        pass

    def start_charge(self, time, car):
        # print(f'Car wants to charge at time {time}')
        return time

class PriceDrivenChargingStrategy(ChargingStrategy):
    def __init__(self):
        pass

    def start_charge(self, time, car:Car):
        # check:
        ## start charging at arrival time
        ## start charging at value change
        ## end charging at value change

        # the time in seconds of four hours
        hour_frame_time = 24 * 3600 / len(ct.PRICE_PER_KWH)

        best = (time, self.value_time(time, car))
        
        for i in range(len(ct.PRICE_PER_KWH)): # each possible start time
            start_time = time + hour_frame_time - (time % (hour_frame_time)) + i * hour_frame_time
            cost = self.value_time(start_time, car)
            if cost < best[1] and self.valid_time(start_time, car):
                best = (start_time, cost)

        for i in range(len(ct.PRICE_PER_KWH)): # each possible end time
            # bit of a hack: add and then modulo to prevent underflow
            start_time = ((24 * 3600) + time + hour_frame_time - (time % hour_frame_time) + i * hour_frame_time - car.charging_time) % (24 * 3600)
            cost = self.value_time(start_time, car)
            if cost < best[1] and self.valid_time(start_time, car):
                best = (start_time, cost)
        
        # starting latest possible moment. no modulo needed as it should never be cheaper unless it is on first day
        start_time = car.planned_departure - car.charging_time
        cost = self.value_time(start_time, car)
        if cost < best[1] and self.valid_time(start_time, car):
            best = (start_time, cost)

        # print(f'cost: {best[1] / 3600}')
        return best[0]

    def value_time(self, start_time, car:Car):
        """
        Calculates the cost for charging a car based on its desired starting time
        """
        current_time = start_time
        time_left = car.charging_time

        # the hour frame is calculated based on the start time (in seconds) converted into the hour of a 24-hour day
            # by dividing by 4, the hour frame is chosen as one of the [00:00 - 04:00], [04:00 - 08:00], [08:00 - 16:00], [16:00 - 20:00], [20:00 - 00:00], each with their own price range
        hour_frame = int(((start_time / 3600) % 24) / 4)
        hour_frame_time = 24 * 3600 / len(ct.PRICE_PER_KWH)   
        cost = 0
        
        while time_left > 0:
            # time span calculates the time spent in each hour frame
                # takes the minimum between how much time is left to charge completely, and how much time is left in the current hour frame
                # the time in the current hour frame is always a value between 0 and 4 hours
            time_span = min(time_left, (hour_frame + 1) * hour_frame_time - (current_time % (24 * 3600)))
            time_left -= time_span

            # the cost is calculated by adding the prices for each of the price ranges the charging time spans
            cost += ct.PRICE_PER_KWH[hour_frame] * time_span
            hour_frame = (hour_frame + 1) % 6
            current_time += time_span

        return cost


    def valid_time(self, start_time, car:Car):
        return (start_time + car.charging_time < car.planned_departure)

class FCFSChargingStrategy(ChargingStrategy):
    def __init__(self):
        pass

    def start_charge(self, time, car):
        return time

class ELFSChargingStrategy(ChargingStrategy):
    def __init__(self):
        pass

    def start_charge(self, time, car):
        return time