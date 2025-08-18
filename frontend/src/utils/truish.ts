
// Converst value to a boolean 
export function trueish(v: unknown): boolean {
  if (typeof v === "boolean") return v;
  if (typeof v === "number") return v != 0;
  if (typeof v === "string") {
    const s = v.trim().toLowerCase();
    return s === "true" || s === "1" || s === "yes" || s === "y" || s === "on";
  }
  return false;
}
