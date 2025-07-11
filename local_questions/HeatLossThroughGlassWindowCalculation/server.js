const math = require('mathjs');

const generate = (usePredefinedValues = 0) => {
    const unitSystems = ['si', 'uscs'];
    const units = {
        "si": {
            "dist": "m",
            "temperature": "K",
            "thermalConductivity": "W/m*K"
        },
        "uscs": {
            "dist": "feet",
            "temperature": "F",
            "thermalConductivity": "Btu/h*ft*F"
        }
    };

    let unitSel = usePredefinedValues === 1 ? 0 : math.randomInt(0, 2);
    const unitsDist = units[unitSystems[unitSel]].dist;
    const unitsTemperature = units[unitSystems[unitSel]].temperature;
    const unitsThermalConductivity = units[unitSystems[unitSel]].thermalConductivity;

    // Predefined values for testing (if needed)
    const predefinedValues = [
        { thickness: 0.01, T_outside: 278, T_inside: 293, height: 1.5, width: 2.0, k: 1.0 },
        { thickness: 0.012, T_outside: 275, T_inside: 290, height: 1.8, width: 2.5, k: 1.05 }
    ];

    // Use predefined values or generate random values
    const selectedValues = usePredefinedValues === 1 ? predefinedValues[0] : {
        thickness: math.random(0.005, 0.015),
        T_outside: math.random(270, 300),
        T_inside: math.random(280, 320),
        height: math.random(1.2, 2.0),
        width: math.random(1.5, 2.5),
        k: math.random(0.8, 1.5)
    };

    // Calculate the area
    const area = selectedValues.height * selectedValues.width;

    // Calculate temperature difference
    const delta_T = selectedValues.T_inside - selectedValues.T_outside;

    // Calculate heat loss (Q = k * A * (delta_T / d))
    const heatLoss = (selectedValues.k * area * (delta_T / selectedValues.thickness)).toFixed(3);

    const data = {
        params: {
            thickness: selectedValues.thickness,
            T_outside: selectedValues.T_outside,
            T_inside: selectedValues.T_inside,
            height: selectedValues.height,
            width: selectedValues.width,
            k: selectedValues.k,
            intermediate_calculations: {
                delta_T: delta_T,
                area: area
            },
            unitsDist: unitsDist,
            unitsTemperature: unitsTemperature,
            unitsThermalConductivity: unitsThermalConductivity
        },
        correct_answers: {
            heatLoss: heatLoss
        },
        nDigits: 3,
        sigfigs: 3
    };

    return data;
};
console.log(generate())
module.exports = { generate };