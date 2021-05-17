"""
This file contains the constants used throughout the project
"""


N_DAYS = 7
FRAME = 3600    # 1 unit of time = 1s
PARKING_CHECKS = 3
CHARGING_RATE = 6

CABLE_CAPACITY = 200
TRANSFORMER_CAPACITY = 1000

# 0 = transformer
# 1-7 = parking spot junction
# 8-14 = parking spot source
# 15-21 = parking spot sink
# 22, 23, 24 = junctions

SOLAR_PANELS = [
    (0, []),
    (0, [5, 6]),
    (1, [5, 6]),
    (0, [0, 1, 5, 6]),
    (1, [0, 1, 5, 6])
]
 

N_CARS = 750
N_PARKING_SPOTS = 7
PARKING_SPOTS = [60, 80, 60, 70, 60, 60, 50]
PARKING_PREFERENCE = [0.15, 0.15, 0.15, 0.20, 0.15, 0.10, 0.10]
PRICE_PER_KWH = [16, 16, 18, 18, 22, 20]
N_CABLES = 10
