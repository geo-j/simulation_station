class ChargingStrategy(object):
    def __init__(self):
        pass

    def start_charge(self):
        pass


class BaseChargingStrategy(ChargingStrategy):
    def __init__(self):
        pass

    def start_charge(self, time):
        # print(f'Car wants to charge at time {time}')
        return time

class PriceDrivenChargingStrategy(ChargingStrategy):
    def __init__(self):
        pass

    def start_charge(self):
        pass
        
        return 
