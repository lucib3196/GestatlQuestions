import math
import random


def generate(case_=0):
    # Predefined values
    PREDEFINED_VALUES = {
        "speed": 10,
        "unitsSpeed": "m/s",
        "time": 20,
        "unitsTime": "s",
        "unitsDist": "meters",
    }

    TEST_VALUES = {
        "speed": 10,
        "unitsSpeed": "m/s",
        "time": 20,
        "unitsTime": "s",
        "unitsDist": "meters",
    }

    CORRECT_ANSWER = 200  # provided in code
    ABS_TOL = 1e-6
    REL_TOL = 1e-6

    test_results = {"pass": None, "message": ""}

    # Case handling
    if case_ == 0:
        # Random generation based on reasonable ranges for each parameter
        params = {
            "speed": random.uniform(5, 50),  # speed in m/s (or equivalent)
            "unitsSpeed": random.choice(["m/s", "km/h", "ft/s"]),
            "time": random.uniform(1, 60),  # time in seconds (or equivalent)
            "unitsTime": "s",
            "unitsDist": random.choice(["meters", "kilometers", "feet"]),
        }
    elif case_ == 1:
        params = PREDEFINED_VALUES
    elif case_ == 2:
        params = TEST_VALUES
    else:
        raise ValueError(f"Unknown case_: {case_}")

    # Convert speed to m/s for calculations
    if params["unitsSpeed"] == "km/h":
        speed_m_s = params["speed"] / 3.6  # convert km/h to m/s
    elif params["unitsSpeed"] == "ft/s":
        speed_m_s = params["speed"] * 0.3048  # convert ft/s to m/s
    else:
        speed_m_s = params["speed"]  # already in m/s

    # Store intermediate speed value in params
    params["intermediate"] = {"speed_m_s": round(speed_m_s, 3)}

    # Calculate distance based on speed and time
    distance = speed_m_s * params["time"]  # Distance = speed * time

    # Test the answer only for case 2
    if case_ == 2:
        computed_distance = distance
        passed = abs(computed_distance - CORRECT_ANSWER) <= max(
            ABS_TOL, REL_TOL * abs(CORRECT_ANSWER)
        )

        test_results["pass"] = 1 if passed else 0
        test_results["message"] = (
            f"PASS — computed={computed_distance}, expected={CORRECT_ANSWER}"
            if passed
            else f"FAIL — computed={computed_distance}, expected={CORRECT_ANSWER}"
        )
    print("hello world")

    # Return the results according to the specified format
    return {
        "params": {
            "speed": round(params["speed"], 3),
            "unitsSpeed": params["unitsSpeed"],
            "time": round(params["time"], 3),
            "unitsTime": params["unitsTime"],
            "unitsDist": params["unitsDist"],
            "calculated_distance": round(distance, 3),
            "intermediate": params["intermediate"],
        },
        "correct_answers": {"distance": round(distance, 3)},
        "test_results": test_results,
    }


# Examples
if __name__ == "__main__":
    print(generate(0))  # random values
    print(generate(1))  # predefined values
    print(generate(2))  # test values and verification
