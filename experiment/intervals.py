target_distance = {
    "very low": {"lower_end": 40, "center": 40, "upper_end": 80},
    "low": {"lower_end": 40, "center": 80, "upper_end": 120},
    "medium": {"lower_end": 80, "center": 120, "upper_end": 160},
    "high": {"lower_end": 120, "center": 160, "upper_end": 200},
    "very high": {"lower_end": 160, "center": 200, "upper_end": 200}
}

accel_crnt = {
    "strong negative": {"lower_end": -2, "center": -2, "upper_end": -1},
    "negative": {"lower_end": -2, "center": -1, "upper_end": 0},
    "zero": {"lower_end": -2, "center": 0, "upper_end": 2},
    "positive": {"lower_end": 0, "center": 1, "upper_end": 2},
    "strong positive": {"lower_end": 1, "center": 2, "upper_end": 2}
}


vel_crnt = {
    "very slow": {"lower_end": 8.33, "center": 8.33, "upper_end": 11.11},
    "slow": {"lower_end": 8.33, "center": 11.11, "upper_end": 13.89},
    "medium": {"lower_end": 8.33, "center": 13.89, "upper_end": 32},
    "fast": {"lower_end": 13.89, "center": 19.44, "upper_end": 25},
    "very fast": {"lower_end": 19.44, "center": 32, "upper_end": 32}
}

# input
settings = {
    "target_distance": [target_distance, "[ m ]"],
    "accel_crnt": [accel_crnt, "[ m/s2 ]"],
    "vel_crnt": [vel_crnt, "[ m/s ]"]
}

# m/s2 -> output intervals
accel = {
    "strong negative": {"lower_end": -2, "center": -2, "upper_end": -1},
    "negative": {"lower_end": -2, "center": -1, "upper_end": 0},
    "zero": {"lower_end": -1, "center": 0, "upper_end": 1},
    "positive": {"lower_end": 0, "center": 1, "upper_end": 2},
    "strong positive": {"lower_end": 1, "center": 2, "upper_end": 2}
}