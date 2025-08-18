// const questionParams = {
//   speed: 60,
//   time: 2,
//   unitsSpeed: "km/h",
//   unitsTime: "s",
//   intermediate: {
//     conversionFactor: 0.27778,
//     convertedSpeed: 16.667,
//   },
//   arr: [1, 2, { x: 3 }],
// };

// const template = `
// Speed: [[params.speed]] [[params.unitsSpeed]]
// Converted: [[params.intermediate.convertedSpeed]]
// Item0: [[params.arr.0]] Item2.x: [[params.arr.2.x]]
// Legacy: {{params.time}} {{params.intermediate.conversionFactor}}
// Missing: [[params.not_there]]
// `;

type Options = {
  arrayMode?: string;
  arrayJoin?: string;
  serialize?: () => void;
};

import { roundToSigFigs } from "./mathHelpers";
function flattenParams(
  obj: unknown,
  prefix = "",
  out: Record<any, any> = {},
  opts: Options = {},
  rounding = true
) {
  const {
    arrayMode = "index", // "index" | "join" | "json"
    arrayJoin = ", ", // used when arrayMode === "join"
    serialize = (v: any) => v, // convert leaf values -> string/primitive
  } = opts;
  const base = (s: any) => (prefix ? `${prefix}.${s}` : s);

  if (Array.isArray(obj)) {
    if (arrayMode === "join") {
      out[prefix] = serialize(obj.join(arrayJoin));
      return out;
    }
    obj.forEach((item, i) => {
      const key = base(String(i)); // Uses the index
      if (item && typeof item === "object") {
        flattenParams(item, key, out, opts);
      }
    });
  }

  //   Iterates throught the object and replaces the parameters by recursively calling it
  if (obj && typeof obj === "object") {
    for (const k of Object.keys(obj)) {
      // Type guard to ensure obj is an object with string keys
      if (typeof obj === "object" && obj !== null && k in obj) {
        // Use type assertion to access property
        let v = (obj as Record<string, any>)[k];
        const key = base(k);
        //   console.log(key, v);
        if (v && typeof v === "object") {
          flattenParams(v, key, out, opts);
        } else {
          if (rounding && typeof v === "number") {
            v = roundToSigFigs(v, 3);
          }
          out[key] = serialize(v);
        }
      }
    }
    return out;
  }
  out[prefix] = serialize(obj);
  return out;
}

function applyPlaceHolders(
  template: string,
  data: any,
  {
    rootPrefix = "", // The root prefix is needed , for testing you need to apply the params directly
    onMissing = "keep",
    warn = console.warn,
    ...opts
  } = {}
) {
  const flat = flattenParams(data, rootPrefix, {}, opts); // Flattens the data so that we can use it
  const lookUp = new Map();
  for (const [path, val] of Object.entries(flat)) {
    const str = val == null ? "" : String(val);
    lookUp.set(`[[${path}]]`, str);
    lookUp.set(`{{${path}}}`, str);
  }
  return template.replace(
    /\[\[([^[\]]+)\]\]|\{\{([^{}]+)\}\}/g,
    (match, p1, p2) => {
      const key = p1 ? `[[${p1}]]` : `{{${p2}}}`;
      if (lookUp.has(key)) return lookUp.get(key);

      // Handle missing
      if (onMissing === "empty") return "";
      if (onMissing === "warn") warn?.(`No value for placeholder ${key}`);
      return match; // keep as-is
    }
  );
}
export default applyPlaceHolders;

// console.log(applyPlaceHolders(template, questionParams));
