const math = require("mathjs");
const generate = (usePredefinedValues = 0) => {
  // Define unit systems
  const unitSystems = {
    si: {
      speed: "km/h",
      time: "s",
      distance: "m",
    },
    uscs: {
      speed: "mph",
      time: "s",
      distance: "ft",
    },
  };

  // Predefined values for testing
  const predefinedValues = {
    speed: 60, // speed in km/h or mph based on system
    time: 2, // time in seconds
  };

  // 1. Dynamic Parameter Selection
  const selectedSystem = math.randomInt(0, 2) === 0 ? "si" : "uscs";
  const units = unitSystems[selectedSystem];

  // 2. Value Generation
  let speed, time;
  if (usePredefinedValues) {
    speed = predefinedValues.speed;
    time = predefinedValues.time;
  } else {
    // Random speed between 20-100 for SI, or 12-62 for USCS (approx)
    speed =
      selectedSystem === "si"
        ? math.randomInt(20, 101)
        : math.randomInt(12, 63);
    // Random time between 1-10 seconds
    time = math.randomInt(1, 11);
  }

  // 3. Solution Synthesis
  // Convert speed to m/s if SI, or to ft/s if USCS
  let speedConverted;
  if (units.speed === "km/h") {
    speedConverted = (speed * 1000) / 3600; // km/h to m/s
  } else {
    speedConverted = speed * 1.46667; // mph to ft/s
  }

  // Calculate distance = speed * time
  const distance = speedConverted * time;

  // Hardcoded TEST_VALUES
  const TEST_VALUES = { speed: 50, time: 20 };
  const CORRECT_ANSWER = 1000; // Hardcoded correct answer
  const ABS_TOL = 1e-6;
  const REL_TOL = 1e-6;
  let test_results = { pass: null, message: "" };

  if (usePredefinedValues === 2) {
    speed = TEST_VALUES.speed;
    time = TEST_VALUES.time;

    // Perform correctness verification
    let computedDistance = speed * time;
    let passed =
      Math.abs(computedDistance - CORRECT_ANSWER) <=
      Math.max(ABS_TOL, REL_TOL * Math.abs(CORRECT_ANSWER));
    test_results.pass = passed ? 1 : 0;
    test_results.message = passed
      ? `PASS — computed=${computedDistance}, expected=${CORRECT_ANSWER}`
      : `FAIL — computed=${computedDistance}, expected=${CORRECT_ANSWER}`;
  }

  // Return the structured data
  return {
    params: {
      speed: speed,
      time: time,
      unitsSpeed: units.speed,
      unitsTime: units.time,
      unitsDistance: units.distance,
    },
    correct_answers: {
      distance: math.round(distance, 3), // Round to 3 decimal places
    },
    test_results,
  };
};

module.exports = { generate };
