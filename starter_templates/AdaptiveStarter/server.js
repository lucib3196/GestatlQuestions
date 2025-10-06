const math = require('mathjs');

const generate = (usePredefinedValues = 0) => {
  let a, b;

  if (usePredefinedValues === 0) {
    a = math.randomInt(1, 101);
    b = math.randomInt(1, 101);
  } else {
    a = 5;
    b = 10;
  }

  const c = a + b;

  return {
    params: { a, b },
    correct_answers: { c: math.round(c, 3) },
    nDigits: 3,
    sigfigs: 3
  };
};

module.exports = { generate };