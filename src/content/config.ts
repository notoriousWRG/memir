import { defineCollection, z } from 'astro:content';
import { docsSchema } from '@astrojs/starlight/schema';

// Entity type discriminator
const entityType = z.enum([
  'npc',
  'location',
  'item',
  'monster',
  'story',
  'session',
  'pc',
  'ledger-entry',
  // Added during M2 canon import — real friction from Ældor world notes
  'god',
  'race',
  'faction',
  'history-entry',
]);

export const collections = {
  docs: defineCollection({
    schema: docsSchema({
      extend: z.object({
        // Every entity except bare index pages carries a type
        type: entityType.optional(),

        // ── NPC ──────────────────────────────────────────────────────────────
        race: z.string().optional(),
        role: z.string().optional(),
        voice: z.string().optional(),
        attitude: z.enum(['friendly', 'neutral', 'wary', 'hostile']).optional(),
        location: z.string().optional(),   // slug of their home location

        // ── Location ─────────────────────────────────────────────────────────
        // tier: 1 (hamlet) → 5 (capital/dungeon final chamber)
        tier: z.number().int().min(1).max(5).optional(),
        region: z.string().optional(),
        // BLeeM-influenced environment fields — required for type:location
        escalation_triggers: z.array(z.string()).optional(),
        active_clocks: z.array(z.string()).optional(),

        // ── Item ─────────────────────────────────────────────────────────────
        rarity: z
          .enum(['common', 'uncommon', 'rare', 'very rare', 'legendary', 'artifact'])
          .optional(),
        attunement: z.boolean().optional(),
        item_type: z.string().optional(),  // weapon, wondrous, etc.

        // ── Monster ───────────────────────────────────────────────────────────
        cr: z.union([z.number(), z.string()]).optional(),
        monster_type: z.string().optional(),  // undead, beast, fiend, etc.
        habitat: z.string().optional(),

        // ── Story ─────────────────────────────────────────────────────────────
        premise: z.string().optional(),
        canon_hooks: z.array(z.string()).optional(),
        status: z.enum(['draft', 'ready', 'retired']).optional(),

        // ── Session ───────────────────────────────────────────────────────────
        session_number: z.number().int().optional(),
        session_date: z.string().optional(),  // ISO date string
        story: z.string().optional(),         // slug of parent story
        party: z.string().optional(),         // slug of campaign/party
        pcs_present: z.array(z.string()).optional(),

        // ── PC ────────────────────────────────────────────────────────────────
        player: z.string().optional(),
        class_level: z.string().optional(),   // e.g. "Rogue 5 / Wizard 2"
        pc_race: z.string().optional(),       // separate from npc race to avoid collision

        // ── God ───────────────────────────────────────────────────────────────
        domains: z.array(z.string()).optional(),
        // Aesir/Vanir = traditional pantheon; Antagonist = Loki's children etc.
        allegiance: z
          .enum(['Aesir', 'Vanir', 'Antagonist', 'Neutral', 'Primordial'])
          .optional(),
        symbol: z.string().optional(),

        // ── Race ──────────────────────────────────────────────────────────────
        lineage: z.string().optional(),     // ancestral origin, e.g. "Ice Giant"
        homebrew: z.boolean().optional(),   // true if custom to Ældor

        // ── Faction ───────────────────────────────────────────────────────────
        faction_alignment: z.string().optional(),
        faction_goal: z.string().optional(),

        // ── History Entry ─────────────────────────────────────────────────────
        era: z.string().optional(),         // which age this belongs to
        period: z.string().optional(),      // rough descriptor

        // ── Ledger Entry ──────────────────────────────────────────────────────
        // Every field here is load-bearing for the creative-pain mechanic.
        // Do not restructure without explicit direction.
        choice: z.string().optional(),
        cost: z.string().optional(),
        ripple: z.string().optional(),
        session: z.string().optional(),       // slug of the session this came from
        pcs_involved: z.array(z.string()).optional(),
      }),
    }),
  }),
};
