export const XP_THRESHOLDS = [
  0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
  85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000,
]

export function xpProgress(xp: number, level: number): number {
  if (level >= 20) return 1
  const floor = XP_THRESHOLDS[level - 1] ?? 0
  const ceil = XP_THRESHOLDS[level] ?? floor
  if (ceil === floor) return 1
  return Math.min(1, Math.max(0, (xp - floor) / (ceil - floor)))
}
