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
