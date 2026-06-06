import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"

const XP_THRESHOLDS = [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]

function xpProgress(xp: number, level: number): number {
  if (level >= 20) return 1
  const floor = XP_THRESHOLDS[level - 1] ?? 0
  const ceil = XP_THRESHOLDS[level] ?? floor
  if (ceil === floor) return 1
  return Math.min(1, Math.max(0, (xp - floor) / (ceil - floor)))
}

const PartyRoster: QuartzComponent = ({ allFiles }: QuartzComponentProps) => {
  const pcs = allFiles
    .filter((f) => f.frontmatter?.type === "pc" && f.slug?.startsWith("pcs/"))
    .sort((a, b) => {
      const nameA = (a.frontmatter?.title as string) ?? ""
      const nameB = (b.frontmatter?.title as string) ?? ""
      return nameA.localeCompare(nameB)
    })

  if (pcs.length === 0) return null

  return (
    <div class="party-roster">
      <h2 class="roster-heading">The Party</h2>
      <ul class="roster-list">
        {pcs.map((pc) => {
          const name = (pc.frontmatter?.title as string) ?? pc.slug ?? ""
          const cls = (pc.frontmatter?.class as string) ?? ""
          const level = Number(pc.frontmatter?.level ?? 1)
          const xp = Number(pc.frontmatter?.xp ?? 0)
          const progress = xpProgress(xp, level)
          const pct = Math.round(progress * 100)

          return (
            <li class="roster-entry">
              <div class="roster-name-row">
                <a href={`/${pc.slug}`} class="internal roster-name">
                  {name}
                </a>
                <span class="roster-class">{cls}</span>
                <span class="roster-level-badge">Lv {level}</span>
              </div>
              <div class="xp-bar-track" title={`${xp.toLocaleString()} XP — ${pct}% to next level`}>
                <div class="xp-bar-fill" style={`width:${pct}%`} />
              </div>
              <div class="xp-label">{xp.toLocaleString()} XP</div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

PartyRoster.css = `
.party-roster {
  margin: 1.5rem 0 2rem;
  border: 1px solid var(--lightgray);
  border-radius: 6px;
  padding: 1.25rem 1.5rem;
  background: var(--light);
}

.roster-heading {
  font-family: var(--headerFont);
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--secondary);
  margin: 0 0 1rem;
  border-bottom: 1px solid var(--lightgray);
  padding-bottom: 0.5rem;
}

.roster-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.roster-entry {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.roster-name-row {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

a.internal.roster-name {
  font-family: var(--headerFont);
  font-size: 1rem;
  font-weight: 600;
  color: var(--dark);
  text-decoration: none;
}

a.internal.roster-name:hover {
  color: var(--secondary);
}

.roster-class {
  font-size: 0.8rem;
  color: var(--gray);
  flex: 1;
}

.roster-level-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--tertiary);
  background: color-mix(in srgb, var(--tertiary) 15%, transparent);
  border: 1px solid color-mix(in srgb, var(--tertiary) 35%, transparent);
  border-radius: 4px;
  padding: 0.1rem 0.4rem;
  white-space: nowrap;
}

.xp-bar-track {
  height: 6px;
  background: var(--lightgray);
  border-radius: 3px;
  overflow: hidden;
}

.xp-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--secondary), var(--tertiary));
  border-radius: 3px;
  transition: width 0.3s ease;
}

.xp-label {
  font-size: 0.7rem;
  color: var(--gray);
}
`

export default (() => PartyRoster) satisfies QuartzComponentConstructor
