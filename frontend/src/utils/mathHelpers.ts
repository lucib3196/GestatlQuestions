import * as math from "mathjs";

export function roundToSigFigs(num: number, sigfigs: number): number {
  if (num === 0) return 0;

  const digits = Math.floor(Math.log10(Math.abs(num))) + 1;
  const factor = Math.pow(10, sigfigs - digits);
  return Math.round(num * factor) / factor;
}

export function isCloseEnoug(
  correct: number,
  submitted: number,
  absTol = 1e-6,
  relTol = 1e-3
): boolean {
  const absError = Math.abs(submitted - correct);
  const relError = absError / Math.max(Math.abs(correct), 1e-12);
  return absError <= absTol || relError <= relTol;
}

export function shuffleArray(array: any[]) {
  // Fisher-Yates shuffle
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

/**
 * Return a random permutation of integers in range [0, num).
 */
export function getRandomPermutationRange(num: number): number[] {
  const A = Array.from({ length: num }, (_, i) => i);
  return getRandomPermutationArray(A);
}

/**
 * Return a random integer from [0, max).
 */
export function getRandomInt(max: number): number {
  return Math.floor(Math.random() * max);
}

/**
 * Return a random permutation of the input array.
 */
function getRandomPermutationArray<T>(arr: T[]): T[] {
  const copy = [...arr];
  const result: T[] = [];

  while (copy.length > 0) {
    const idx = math.randomInt(copy.length); // safe random index
    const [item] = copy.splice(idx, 1);
    result.push(item);
  }

  return result;
}
