import random


def generate(use_predefined_values=0):
    # Define unit types
    unitSystems = ["si", "uscs"]
    units = {
        "si": {"span": "m", "force": "N", "dist": "m", "stress": "mPa"},
        "uscs": {"span": "feet", "force": "lb", "dist": "inches", "stress": "PSI"},
    }

    # Select a random unit system
    unitSel = random.randint(0, 1)
    unitsSpan = units[unitSystems[unitSel]]["span"]
    unitsForce = units[unitSystems[unitSel]]["force"]
    unitsDist = units[unitSystems[unitSel]]["dist"]
    unitsStress = units[unitSystems[unitSel]]["stress"]

    # Predefined values for testing (if usage flag is set)
    if use_predefined_values:
        span = 5 if unitSel == 0 else 15  # 5m or 15ft
        load = 20000 if unitSel == 0 else 50000  # 20000N or 50000lb
        width = 300 if unitSel == 0 else 12  # 300mm or 12in
        height = 500 if unitSel == 0 else 20  # 500mm or 20in
    else:
        # Dynamic random values generation
        span = random.uniform(2, 10) * (
            1 if unitSel == 0 else 3.281
        )  # 2-10m or 6.56-32.8ft
        load = random.uniform(1000, 30000) * (
            1 if unitSel == 0 else 0.225
        )  # 1000-30000N or approx 225-6750lb
        width = random.uniform(0.1, 0.5) * (
            1000 if unitSel == 0 else 1
        )  # 100-500mm or 4-20in
        height = random.uniform(0.1, 1) * (
            1000 if unitSel == 0 else 1
        )  # 100-1000mm or 4-40in

    # Calculate bending properties
    moment = (
        load * span / 4
    )  # M = load * span / 4 // Bending moment for a point load at center
    I = (
        width * height**3
    ) / 12  # I = (width * height**3) / 12 // Moment of inertia for a rectangular cross-section
    c = height / 2  # c = height / 2 // Distance from neutral axis to outer fiber
    S = (width * height**2) / 6  # S = (width * height**2) / 6 // Section modulus
    max_bending_stress = moment * c / I  # Maximum bending stress formula

    # Convert to MPa if SI unit selected
    if unitSel == 0:
        max_bending_stress = max_bending_stress / 1e6  # Convert to MPa from Pa

    return {
        "params": {
            "span": span,
            "load": load,
            "width": width,
            "height": height,
            "unitsSpan": unitsSpan,
            "unitsForce": unitsForce,
            "unitsDist": unitsDist,
            "unitsStress": unitsStress,
            "intermediate": {
                "moment": moment,
                "moment_of_inertia": I,
                "section_modulus": S,
            },
        },
        "correct_answers": {
            "maxBendingStress": round(
                max_bending_stress, 3
            ),  # Round to 3 decimal places
        },
        "nDigits": 3,
        "sigfigs": 3,
    }
