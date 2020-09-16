target_distance = {
    "very low": {"lower_end": 20, "center": 20, "upper_end": 40},
    "low": {"lower_end": 20, "center": 40, "upper_end": 60},
    "medium": {"lower_end": 40, "center": 60, "upper_end": 80},
    "high": {"lower_end": 60, "center": 80, "upper_end": 100},
    "very high": {"lower_end": 80, "center": 100, "upper_end": 100}
}

accel_crnt = {
    "strong negative": {"lower_end": -2, "center": -2, "upper_end": -1},
    "negative": {"lower_end": -2, "center": -1, "upper_end": 0},
    "zero": {"lower_end": -1, "center": 0, "upper_end": 1},
    "positive": {"lower_end": 0, "center": 1, "upper_end": 2},
    "strong positive": {"lower_end": 1, "center": 2, "upper_end": 2}
}


vel_crnt = {
    "very slow": {"lower_end": 0, "center": 2.78, "upper_end": 8.33},
    "slow": {"lower_end": 0, "center": 8.33, "upper_end": 13.89},
    "medium": {"lower_end": 8.33, "center": 13.89, "upper_end": 19.44},
    "fast": {"lower_end": 13.89, "center": 19.44, "upper_end": 25},
    "very fast": {"lower_end": 19.44, "center": 25, "upper_end": 52}
}

# input
settings = {
    "target_distance": target_distance,
    "accel_crnt": accel_crnt,
    "vel_crnt": vel_crnt
}

# m/s2 -> output intervals
accel = {
    "strong negative": {"lower_end": -2, "center": -2, "upper_end": -1},
    "negative": {"lower_end": -2, "center": -1, "upper_end": 0},
    "zero": {"lower_end": -1, "center": 0, "upper_end": 1},
    "positive": {"lower_end": 0, "center": 1, "upper_end": 2},
    "strong positive": {"lower_end": 1, "center": 2, "upper_end": 2}
}