target_distance = {
    "very low": {"lower_end": 0, "center": 0, "upper_end": 20},
    "low": {"lower_end": 0, "center": 20, "upper_end": 40},
    "medium": {"lower_end": 20, "center": 40, "upper_end": 60},
    "high": {"lower_end": 40, "center": 60, "upper_end": 80},
    "very high": {"lower_end": 60, "center": 80, "upper_end": 100}
}

driver_type = {
    "aggressive": {"lower_end": 5, "center": 5, "upper_end": 15},
    "medium": {"lower_end": 15, "center": 20, "upper_end": 25},
    "defensive": {"lower_end": 25, "center": 30, "upper_end": 35}
}

change_of_distance = {
    "strong negative": {"lower_end": -15, "center": -15, "upper_end": -5},
    "negative": {"lower_end": -10, "center": -5, "upper_end": 0},
    "zero": {"lower_end": -5, "center": 0, "upper_end": 5},
    "positive": {"lower_end": 0, "center": 5, "upper_end": 10},
    "strong positive": {"lower_end": 5, "center": 10, "upper_end": 15},
}

# input
settings = {
    "target_distance": target_distance,
    "driver_type": driver_type,
    "change_of_distance": change_of_distance
}

# m/s2 -> output intervals
accel = {
    "strong negative": {"lower_end": -10, "center": -10, "upper_end": -5},
    "negative": {"lower_end": -10, "center": -5, "upper_end": 0},
    "zero": {"lower_end": -3, "center": 0, "upper_end": 3},
    "positive": {"lower_end": 0, "center": 5, "upper_end": 10},
    "strong positive": {"lower_end": 5, "center": 10, "upper_end": 10},
}