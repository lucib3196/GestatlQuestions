import random
import math

def generate(use_predefined_values=1):
    # Predefined values based on the original question
    predefined_values = [
        {'a': 10, 'b': 10}  # Using the values from the original question
    ]

    if use_predefined_values == 1:
        values = predefined_values[0]
    else:
        # Dynamically generate values for a and b
        values = {
            'a': round(random.uniform(0, 100), 3),  # Example range for a
            'b': round(random.uniform(0, 100), 3)   # Example range for b
        }

    # Calculate c
    c = values['a'] + values['b']
    print("Some new message")

    # Prepare the output data structure
    output = {
        'params': {
            'a': values['a'],
            'b': values['b'],
        },
        'correct_answers': {
            'c': round(c, 3)
        },
        'nDigits': 3,
        'sigfigs': 3
    }


    return output