import * as math from "mathjs";

const generate = (usePredefinedValues = 0) => {
  const unitSystems = ["si", "uscs"];
  const units = {
    si: {
      span: "m",
      load: "N",
      width: "m",
      height: "m",
      stress: "MPa",
    },
    uscs: {
      span: "ft",
      load: "lb",
      width: "ft",
      height: "ft",
      stress: "psi",
    },
  };

  const unitSel = math.randomInt(0, 2);
  const unitsSpan = units[unitSystems[unitSel]].span;
  const unitsForce = units[unitSystems[unitSel]].load;
  const unitsDist = units[unitSystems[unitSel]].width;
  const unitsStress = units[unitSystems[unitSel]].stress;

  let span, load, width, height;

  if (usePredefinedValues) {
    span = 6; // Predefined value in meters or feet
    load = 10000; // Predefined point load
    width = 0.3; // Predefined width in meters or feet
    height = 0.5; // Predefined height in meters or feet
  } else {
    span = math.random(4, 10); // Random span between 4 to 10 meters or feet
    load = math.random(1000, 20000); // Random load between 1000 to 20000 N or lb
    width = math.random(0.1, 0.5); // Random width between 0.1 to 0.5 m or ft
    height = math.random(0.1, 0.5); // Random height between 0.1 to 0.5 m or ft
  }

  // Calculate Moment of Inertia (I) for a rectangular section
  const I = (width * math.pow(height, 3)) / 12;
  // Calculate Maximum Bending Moment (M) which is load * (span / 4)
  const M = load * (span / 4);
  // Distance from the neutral axis to the outer surface
  const c = height / 2;
  // Calculate Section Modulus (S)
  const S = (width * math.pow(height, 2)) / 6;
  // Bending stress formula: sigma = M*c/I
  const bendingStress = (M * c) / I;

  // Convert bendingStress to MPa or psi
  // Conversion factors:
  // - 1 Pa = 1E-6 MPa
  // - 1 Pa = 0.000145038 psi
  const bendingStressMPa =
    unitSel === 0 ? bendingStress / 1e6 : bendingStress / 6894.76; // Conversion from Pa to MPa or psi

  return {
    params: {
      span,
      load,
      width,
      height,
      unitsSpan,
      unitsForce,
      unitsDist,
      unitsStress,
      intermediate: {
        moment: M, // Maximum Bending Moment
        inertia: I, // Moment of Inertia
        sectionModulus: S, // Section Modulus
      },
    },
    correct_answers: {
      maxBendingStress: math.round(bendingStressMPa, 3),
    },
    nDigits: 3,
    sigfigs: 3,
  };
};

console.log(generate());

export default generate;
