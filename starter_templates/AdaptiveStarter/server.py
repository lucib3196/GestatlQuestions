import random
import math

def generate(use_predefined_values=0):
    # Predefined values for testing
    predefined_values = [{'a': 5, 'b': 10}]

    if use_predefined_values == 1:
        values = predefined_values[0]
    else:
        values = {
            'a': round(random.uniform(0, 100), 3),
            'b': round(random.uniform(0, 100), 3)
        }

    c = values['a'] + values['b']

    return {
        'params': values,
        'correct_answers': {'c': round(c, 3)},
        'nDigits': 3,
        'sigfigs': 3
    }