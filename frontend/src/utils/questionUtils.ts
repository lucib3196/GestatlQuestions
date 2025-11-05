import type { questionRel } from "../types/questionTypes";

export function handleRelationshipValue(value: string | questionRel) {
  if (typeof value === "string") {
    return value;
  } else if (typeof value === typeof "object" && "name" in value) {
    return value.name;
  } else {
    throw "Could not determine type ";
  }
}

export function handleRelationshipValues(value: string[] | questionRel[]) {
  return value.map((v) => handleRelationshipValue(v));
}
