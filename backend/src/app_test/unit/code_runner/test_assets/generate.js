const math = require("mathjs");

const generate = (usePredefinedValues = 0) => {
  const unitSystems = {
    si: {
      speed: "km/h",
      distance: "m",
      time: "s",
    },
    uscs: {
      speed: "mph",
      distance: "ft",
      time: "s",
    },
  };

  // 1. Dynamic Parameter Selection
  const selectedSystem = math.randomInt(0, 2) === 0 ? "si" : "uscs";
  const units = unitSystems[selectedSystem];

  // 2. Value Generation
  let speed, time;
  if (usePredefinedValues === 0) {
    // Generate random values
    speed = math.randomInt(30, 121); // Speed between 30 and 120 units
    time = math.randomInt(1, 11); // Time between 1 and 10 units
  } else {
    // Use predefined values for testing
    speed = 60; // 60 speed in either unit
    time = 5; // 5 seconds
  }

  // 3. Intermediate Speed Conversion
  let convertedSpeed;
  let conversionFactor;
  if (units.speed === "km/h") {
    // Speed conversion from km/h to m/s
    conversionFactor = 1000 / 3600;
    convertedSpeed = speed * conversionFactor; // convert to m/s
  } else if (units.speed === "mph") {
    // Speed conversion from mph to ft/s
    conversionFactor = 1.46667;
    convertedSpeed = speed * conversionFactor; // convert to ft/s
  }

  // Create an intermediate object to hold conversion details
  const intermediate = {
    convertedSpeed: math.round(convertedSpeed, 3), // Round to 3 decimal places
    conversionFactor: conversionFactor,
  };

  // 4. Solution Synthesis
  let distance;
  if (units.speed === "km/h") {
    distance = convertedSpeed * time; // Distance in meters
  } else if (units.speed === "mph") {
    distance = convertedSpeed * time; // Distance in feet
  }

  console.log("This is me syaing hello");

  // Return structured data
  return {
    params: {
      speed: speed,
      time: time,
      intermediate: intermediate,
      unitsSpeed: units.speed,
      unitsDistance: units.distance,
      unitsTime: units.time,
    },
    correct_answers: {
      distance: math.round(distance, 3), // Round to 3 decimal places
    },
    nDigits: 3,
    sigfigs: 3,
  };
};
module.exports = { generate };
