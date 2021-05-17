"""
This file contains the constants used throughout the project
"""


N_DAYS = 7
CAR_DEVIATION = 50
FRAME = 3600    # 1 unit of time = 1s
PARKING_CHECKS = 3
CHARGING_RATE = 6

CABLE_CAPACITY = 200
TRANSFORMER_CAPACITY = 1000
CABLE_PATHS = [     # each of the list indices correspond to a parking spot
                    # 9 marks the capacity of the transformer, all parking spots are connected to the transformer
    [0, 1, 9],      # P1 has cables 0 and 1
    [0, 2, 9],      # P2 has cables 0, and 2
    [0, 3, 9],      # P3 has cables 0, and 3
    [4, 9],         # P4 has cable 4
    [4, 6, 7, 9],   # P5 has cables 4, 6, 7
    [4, 6, 8, 9],   # P6 has cables 4, 6, 8
    [4, 5, 9]       # P7 has cables 4, 5
]

SOLAR_PANELS = [
    (0, []),
    (0, [5, 6]),
    (1, [5, 6]),
    (0, [0, 1, 5, 6]),
    (1, [0, 1, 5, 6])
]
 

N_CARS = 600
N_PARKING_SPOTS = 7
PARKING_SPOTS = [60, 80, 60, 70, 60, 60, 50]
PARKING_PREFERENCE = [0.15, 0.15, 0.15, 0.20, 0.15, 0.10, 0.10]
PRICE_PER_KWH = [16, 16, 18, 18, 22, 20]
N_CABLES = 10
