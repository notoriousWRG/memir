import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { XP_THRESHOLDS, xpProgress } from "./xpUtils"

const PCStats: QuartzComponent = ({ fileData }: QuartzComponentProps) => {
  const fm = fileData.frontmatter
  if (fm?.type !== "pc" || !fm?.level) return null

  const cls = (fm.class as string) ?? ""
  const level = Number(fm.level)
  const xp = Number(fm.xp ?? 0)
  const progress = xpProgress(xp, level)
  const pct = Math.round(progress * 100)
  const nextThreshold = XP_THRESHOLDS[level] ?? null

  return (
    <div class="pc-stats">
      <span class="pc-stats-class">{cls}</span>
      <span class="pc-stats-level-badge">Level {level}</span>
      <div class="pc-stats-xp-row">
        <div class="pc-stats-xp-track" title={`${xp.toLocaleString()} XP — ${pct}% to next level`}>
          <div class="pc-stats-xp-fill" style={`width:${pct}%`} />
        </div>
        <span class="pc-stats-xp-label">
          {xp.toLocaleString()} XP
          {nextThreshold ? ` / ${nextThreshold.toLocaleString()} to Lv ${level + 1}` : ""}
        </span>
      </div>
    </div>
  )
}

PCStats.css = `
.pc-stats {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin: 0.25rem 0 1.25rem;
  padding: 0.75rem 1rem;
  border: 1px solid var(--lightgray);
  border-radius: 6px;
  background: var(--light);
}

.pc-stats-class {
  font-size: 0.8rem;
  color: var(--gray);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.pc-stats-level-badge {
  font-family: var(--headerFont);
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--tertiary);
}

.pc-stats-xp-row {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.pc-stats-xp-track {
  height: 6px;
  background: var(--lightgray);
  border-radius: 3px;
  overflow: hidden;
}

.pc-stats-xp-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--secondary), var(--tertiary));
  border-radius: 3px;
}

.pc-stats-xp-label {
  font-size: 0.7rem;
  color: var(--gray);
}
`

export default (() => PCStats) satisfies QuartzComponentConstructor
