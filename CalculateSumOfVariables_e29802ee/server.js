const math = require('mathjs');

const generate = (usePredefinedValues = 0) => {
    // 1. Dynamic Parameter Selection: Selecting random values for a and b.
    let a, b;
    if (usePredefinedValues === 0) {
        a = math.randomInt(1, 101); // Random integer between 1 and 100
        b = math.randomInt(1, 101); // Random integer between 1 and 100
    } else {
        // Predefined values for testing purposes
        // Using the original question's values
        a = 5;
        b = 10;
    }

    // 2. Solution Synthesis:
    // Calculate c = a + b
    const c = a + b; // Directly compute the sum

    // Return structured data
    return {
        params: {
            a: a,
            b: b
        },
        correct_answers: {
            c: math.round(c, 3) // Round to 3 decimal places
        },
        nDigits: 3,
        sigfigs: 3
    };
};

module.exports = { generate };