const math = require('mathjs');

const unitSystems = {
    si: {
        speed: 'm/s',
        distance: 'm',
        time: 's'
    },
    uscs: {
        speed: 'ft/s',
        distance: 'ft',
        time: 's'
    }
};

const convertToSI = (speed, unit) => {
    // Convert speed to meters per second if needed
    if (unit === 'ft/s') {
        return speed * 0.3048;
    }
    return speed; // Assume already in SI if not USCS
};

const generate = (case_ = 0) => {
    const units = unitSystems.si; // Using SI system since speed and time are in SI

    let speed, time;
    let test_results = { pass: null, message: "" };

    const CORRECT_ANSWER = 200; // Hardcoded correct answer
    const ABS_TOL = 1e-6;
    const REL_TOL = 1e-6;

    if (case_ === 0) {
        // Random values
        speed = math.randomInt(10, 61); // Random speed
        time = math.randomInt(1, 21);   // Random time
    } else if (case_ === 1) {
        // Predefined values
        speed = 10;
        time = 20;
    } else if (case_ === 2) {
        // Test case
        speed = 10;
        time = 20;

        const computedDistance = speed * time; // distance = speed * time
        const diff = Math.abs(computedDistance - CORRECT_ANSWER);
        const passed = diff <= Math.max(ABS_TOL, REL_TOL * Math.abs(CORRECT_ANSWER));

        test_results.pass = passed ? 1 : 0;
        test_results.message = passed
            ? `✅ PASS — computed=${computedDistance}, expected=${CORRECT_ANSWER}`
            : `❌ FAIL — computed=${computedDistance}, expected=${CORRECT_ANSWER}`;
    } else {
        throw new Error(`Unknown case_: ${case_}`);
    }

    const speedInSI = convertToSI(speed, units.speed); // Convert speed to SI if needed
    const distance = speedInSI * time; // distance calculation

    return {
        params: {
            speed: speed,
            time: time,
            unitsSpeed: units.speed,
            unitsDist: units.distance,
            unitsTime: units.time,
            intermediate: {
                computedDistance: math.round(distance, 3), // Computed distance
                speed_m_s: math.round(speedInSI, 3)        // Speed in m/s
            }
        },
        correct_answers: {
            distance: math.round(distance, 3)
        },
        test_results
    };
};

module.exports = { generate };

console.log(generate(2))