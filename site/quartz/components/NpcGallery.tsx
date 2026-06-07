import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"

// Attitude groups, in display order, with player-facing labels.
const ATTITUDE_GROUPS: { key: string; label: string }[] = [
  { key: "friendly", label: "Allies" },
  { key: "neutral", label: "Encountered" },
  { key: "wary", label: "Uneasy ground" },
  { key: "hostile", label: "Adversaries" },
]

const NpcGallery: QuartzComponent = ({ allFiles }: QuartzComponentProps) => {
  const npcs = allFiles
    .filter((f) => f.frontmatter?.type === "npc" && f.slug?.startsWith("npcs/"))
    .sort((a, b) => {
      const nameA = (a.frontmatter?.title as string) ?? ""
      const nameB = (b.frontmatter?.title as string) ?? ""
      return nameA.localeCompare(nameB)
    })

  if (npcs.length === 0) return null

  // Bucket by attitude, preserving the declared group order; anything with an
  // unrecognized attitude falls into a trailing "Encountered" bucket.
  const groups = ATTITUDE_GROUPS.map((g) => ({
    ...g,
    members: npcs.filter((n) => ((n.frontmatter?.attitude as string) ?? "neutral") === g.key),
  })).filter((g) => g.members.length > 0)

  return (
    <div class="npc-gallery">
      <h2 class="gallery-heading">People They've Met</h2>
      {groups.map((g) => (
        <div class="gallery-group">
          <h3 class="gallery-group-label">{g.label}</h3>
          <ul class="gallery-grid">
            {g.members.map((npc) => {
              const name = (npc.frontmatter?.title as string) ?? npc.slug ?? ""
              const role = (npc.frontmatter?.role as string) ?? ""
              return (
                <li class="gallery-card">
                  <a href={`/${npc.slug}`} class="internal gallery-card-name">
                    {name}
                  </a>
                  {role ? <span class="gallery-card-sub">{role}</span> : null}
                </li>
              )
            })}
          </ul>
        </div>
      ))}
    </div>
  )
}

export default (() => NpcGallery) satisfies QuartzComponentConstructor
