import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"

const UNHELD_LABEL = "Salvage & set aside"

const ItemGallery: QuartzComponent = ({ allFiles }: QuartzComponentProps) => {
  const items = allFiles
    .filter((f) => f.frontmatter?.type === "item" && f.slug?.startsWith("items/"))
    .sort((a, b) => {
      const nameA = (a.frontmatter?.title as string) ?? ""
      const nameB = (b.frontmatter?.title as string) ?? ""
      return nameA.localeCompare(nameB)
    })

  if (items.length === 0) return null

  // Map a holder slug (e.g. "coriac") to that PC's display name, so item groups
  // read as character names rather than bare slugs.
  const pcTitleBySlug = new Map<string, string>()
  for (const f of allFiles) {
    if (f.frontmatter?.type === "pc" && f.slug?.startsWith("pcs/")) {
      const base = f.slug.slice("pcs/".length)
      pcTitleBySlug.set(base, (f.frontmatter?.title as string) ?? base)
    }
  }

  // Bucket by holder. Held items group under the PC; unheld items fall together.
  const order: string[] = []
  const buckets = new Map<string, typeof items>()
  for (const item of items) {
    const holder = ((item.frontmatter?.current_holder as string) ?? "").trim()
    const label = holder ? pcTitleBySlug.get(holder) ?? holder : UNHELD_LABEL
    if (!buckets.has(label)) {
      buckets.set(label, [])
      order.push(label)
    }
    buckets.get(label)!.push(item)
  }

  // Held PCs alphabetical, with the unheld group always last.
  order.sort((a, b) => {
    if (a === UNHELD_LABEL) return 1
    if (b === UNHELD_LABEL) return -1
    return a.localeCompare(b)
  })

  return (
    <div class="item-gallery">
      <h2 class="gallery-heading">What They Carry</h2>
      {order.map((label) => (
        <div class="gallery-group">
          <h3 class="gallery-group-label">{label}</h3>
          <ul class="gallery-grid">
            {buckets.get(label)!.map((item) => {
              const name = (item.frontmatter?.title as string) ?? item.slug ?? ""
              const rarity = (item.frontmatter?.rarity as string) ?? ""
              return (
                <li class="gallery-card">
                  <a href={`/${item.slug}`} class="internal gallery-card-name">
                    {name}
                  </a>
                  {rarity && rarity !== "unknown" ? (
                    <span class="gallery-card-badge">{rarity}</span>
                  ) : null}
                </li>
              )
            })}
          </ul>
        </div>
      ))}
    </div>
  )
}

export default (() => ItemGallery) satisfies QuartzComponentConstructor
