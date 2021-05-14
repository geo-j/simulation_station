"""
This file contains the constants used throughout the project
"""

N_DAYS = 7
CAR_DEVIATION = 50
FRAME = 3600    # 1 unit of time = 1s
PARKING_CHECKS = 3
CHARGING_RATE = 6

CABLE_CAPACITY = 200
SOLAR_PANEL_CAPACITY = 200
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

SEASON = 0 # 0 = winter, 1 = summer
SOLAR_PARKING_SPOTS = 1   # 0 = no solar panels; 1 = solar panels on P6, P7; 2 = solar panels on P1, P2, P6, P7

SOLAR_ENERGY_PATHS = [
    # P1
    [
        [],
        [1, 2],
        [1, 3],
        [1, 0, 4],
        [1, 0, 4, 6, 7],
        [1, 0, 4, 6, 8],
        [1, 0, 4, 5]
    ],

    # P2
    [
        [2, 1],
        [],
        [2, 3],
        [2, 0, 4],
        [2, 0, 4, 6, 7],
        [2, 0, 4, 6, 8],
        [2, 0, 4, 5]
    ],

    # P3
    [
        [],
        [],
        [],
        [],
        [],
        [],
        []
    ],

    # P4
    [
        [],
        [],
        [],
        [],
        [],
        [],
        []
    ],

    # P5
    [
        [],
        [],
        [],
        [],
        [],
        [],
        []
    ],

    # P6
    [
        [8, 6, 4, 0, 1],
        [8, 6, 4, 0, 2],
        [8, 6, 4, 0, 3],
        [8, 6],
        [8, 7],
        [],
        [8, 6, 5]
    ],

    # P7
    [
        [5, 4, 0, 1],
        [5, 4, 0, 2],
        [5, 4, 0, 3],
        [5],
        [5, 6, 7],
        [5, 6, 8],
        []
    ]
]

SOLAR_PANELS = [[], [5, 6], [0, 1, 5, 6]
    # (season, [parking spots])
        # 0 = winter; 1 = summer
    # (0, []),
    # (0, [5, 6]),
    # (1, [5, 6]),
    # (0, [0, 1, 5, 6]),
    # (1, [0, 1, 5, 6])
]
 

N_CARS = 600
N_PARKING_SPOTS = 7
PARKING_SPOTS = [60, 80, 60, 70, 60, 60, 50]
PARKING_PREFERENCE = [0.15, 0.15, 0.15, 0.20, 0.15, 0.10, 0.10]
PRICE_PER_KWH = [16, 16, 18, 18, 22, 20]
N_CABLES = 10
