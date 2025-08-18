const math = require("mathjs");

/**
 * Generates physics question parameters and answers.
 * @param {0|1|2} case_ - 0=random values, 1=predefined values, 2=test values + verification
 */
const generate = (case_ = 0) => {
  // ---- Unit Systems ----
  const unitSystems = {
    si:  { speed: "km/h", time: "s", distance: "m"  },
    uscs:{ speed: "mph",  time: "s", distance: "ft" },
  };

  // ---- Hardcoded Values ----
  const PREDEFINED_VALUES = { speed: 60, time: 2 };    // Units match chosen system
  const TEST_VALUES       = { speed: 50, time: 20 };   // Units match TEST_UNIT_SYSTEM
  const TEST_UNIT_SYSTEM  = "si";                      // Lock test runs to SI for determinism

  // IMPORTANT: CORRECT_ANSWER must be in the test distance units (m for SI, ft for USCS)
  const CORRECT_ANSWER = 277.7777777778;               // Example: (50 km/h -> 13.888... m/s) * 20 s ≈ 277.7778 m

  const ABS_TOL = 1e-6;
  const REL_TOL = 1e-6;

  // ---- Select Unit System ----
  // Case 0/1: keep randomness like your example; Case 2: lock to TEST_UNIT_SYSTEM
  const selectedSystem =
    case_ === 2 ? TEST_UNIT_SYSTEM : (math.randomInt(0, 2) === 0 ? "si" : "uscs");
  const units = unitSystems[selectedSystem];

  let speed, time;

  /** @type {{pass: 1|0|null, message: string}} */
  let test_results = { pass: null, message: "" };

  // ---- Value Assignment ----
  if (case_ === 0) {
    // Random values
    speed = selectedSystem === "si" ? math.randomInt(20, 101) : math.randomInt(12, 63);
    time  = math.randomInt(1, 11); // seconds
  } else if (case_ === 1) {
    // Predefined
    speed = PREDEFINED_VALUES.speed;
    time  = PREDEFINED_VALUES.time;
  } else if (case_ === 2) {
    if (typeof CORRECT_ANSWER === "undefined") {
      throw new Error("Test case unavailable: CORRECT_ANSWER not provided");
    }
    // Test values EXACTLY as defined for the locked unit system
    speed = TEST_VALUES.speed;
    time  = TEST_VALUES.time;
  } else {
    throw new Error(`Unknown case_: ${case_}`);
  }

  // ---- Convert speed into distance units per second (so distance ends in units.distance) ----
  const toDistancePerSecond = (v, speedUnit) => {
    if (speedUnit === "km/h")  return (v * 1000) / 3600; // m/s
    if (speedUnit === "mph")   return v * 1.46667;       // ft/s
    return v; // fallback (shouldn't hit)
  };

  const speedPerSec = toDistancePerSecond(speed, units.speed);

  // ---- Calculate distance in the system's distance units ----
  const distance = speedPerSec * time; // => "m" for SI, "ft" for USCS

  // ---- Verification (only in Case 2) ----
  if (case_ === 2) {
    const expected = CORRECT_ANSWER; // expected is defined in the same units as 'units.distance'
    const diff = Math.abs(distance - expected);
    const tol  = Math.max(ABS_TOL, REL_TOL * Math.abs(expected));
    const passed = diff <= tol;

    test_results.pass = passed ? 1 : 0;
    test_results.message = passed
      ? `PASS — computed=${distance} ${units.distance}, expected=${expected} ${units.distance}`
      : `FAIL — computed=${distance} ${units.distance}, expected=${expected} ${units.distance}`;
  }

  // ---- Return structured result ----
  // In Case 2, params and correct_answers reflect the EXACT test setup and the exact computed value used in the verification.
  return {
    params: {
      speed,
      time,
      unitsSpeed: units.speed,
      unitsTime: units.time,
      unitsDistance: units.distance,
    },
    correct_answers: {
      distance: Number(math.round(distance, 12)), // same value used for verification path
    },
    test_results,
  };
};

// Example runs
// console.log(generate(0)); // random, test_results.pass === null
// console.log(generate(1)); // predefined, test_results.pass === null
// console.log(generate(2)); // test, params/answers in locked system; pass 1 or 0

module.exports = { generate };

console.log(generate(1))