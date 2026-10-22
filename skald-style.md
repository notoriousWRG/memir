---
title: "Skald Style"
type: reference
masthead: "THE SESSION SKALD"
tagline: "Everything that happened at the table, so you can sound like you were there."
reader: "Sarah"
editor_signoff: "— WR / Dungeon Master / Bellwether House, Ravencrest"
family_spotlight:
  artcoth: "Uncle Craig"
  gareth: "Zack"
  coriac: "Josh"
players:
  artcoth: "Craig"
  gareth: "Zack"
  coriac: "Josh"
  casus: "Chris"
  grimvald: "Jesse"
  shah-doh: "Corey"
session_length_words: "700-1000"
recap_length_words: "1800-2500"
---

# The Session Skald — style guide & template

A Skimm-style newsletter about Chance Encounters, written for **Sarah**, who knows D&D but
doesn't play in this game.
Three of the six PCs are her family: **Artcoth** (Uncle Craig), **Gareth** (Zack) and
**Coriac** (Josh). `/skald` reads this file. The frontmatter holds the settings; the body sets
the voice and the section skeletons for both editions.

This is not the chronicle. [[party-story]] is the record. The Skald is the group-chat version
of it: what happened, why it's funny, and what to ask Uncle Craig about at dinner.

---

## Voice

How theSkimm sounds, and how that maps onto the campaign:

- **Smart friend over coffee.** Second person, first person plural ("we"), present tense for
  what's happening now. Confident, warm, slightly conspiratorial.
- **Every news item gets a kicker.** One plain sentence of fact, then a short wry sentence that
  reacts to it. *"Bramwell the door-knocker was asked to announce the guests. He was bad at it."*
- **Parenthetical asides** carry about half the jokes. *"(No pressure, Casus.)"* *"(We have
  questions. So does Coriac.)"*
- **Pop-culture and real-life bridges.** Translate fantasy into her world: a haunted house is a
  fixer-upper with a tenant, a thieves' guild is an MLM with knives, a natural 20 is hitting
  every green light on the way home.
- **Puns in the kickers and headlines**, never in the facts.
- **Light on mechanics.** Sarah knows D&D, so "natural 20", "Insight check" and spell names
  are fine without a gloss. Use them when the roll *is* the story (a natural 20, a disastrous 1),
  not as a play-by-play. Homebrew mechanics (the Cypher, Ovaltine's potion) get one line of
  explanation.
- **Affectionate roast, never mean.** The players are the celebrities. Tease their choices, not
  them. Nothing that would embarrass someone in front of their family.
- **Family spotlight without favoritism.** Craig, Zack and Josh get the "what your family did"
  framing, but all six PCs show up. The other three players are named by first name the first
  time they appear ("Casus, played by Chris").

## Behind the screen

Sarah knows D&D and knows the game, and she won't spoil it. So the Skald is **not limited to
what the players know.** DM-side material is fair game when it's interesting and relevant:
it's what makes the Skald something to talk about together.

Good behind-the-screen material:
- **Dramatic irony.** What the party missed, and what it meant. *"Nobody at the table caught
  it, but those two guests in feathered cloaks were Odin's ravens."*
- **Prep vs. reality.** What the DM planned and what the players did instead. Scenes they
  skipped, encounters they talked their way out of, NPCs who were meant to die and didn't.
- **Lore that explains a moment.** A paragraph of canon that makes tonight's scene land harder.
- **What's coming.** A tease of a thread the DM has planned, pitched as a hint, not a plot
  summary.

How to use it:
- Keep the **table story first**. Behind-the-screen material is the commentary track: it lives
  in its own section (*Behind the Screen*) and in asides, not woven into the play-by-play as if
  the players knew it.
- **Label it.** Anything the party doesn't know is marked 🤫 so it's always clear what's
  safe to bring up at dinner and what isn't.
- **Interesting beats complete.** One sharp reveal is better than a lore dump. Pick what makes
  her go "oh no" or "wait, really?"
- Some threads are still the DM's to keep, even from Sarah (a twist he wants her to experience
  with the table, a reveal he hasn't decided). `/skald` lists the 🤫 items and the DM picks.

## Table moments

Real things the players said, out of character or in, are what make this personal.

- Source: the merged transcript (`session_audio/session-<N>-transcript.md`) when it exists.
- **Quotes must be verified by the DM.** Whisper garbles. Never print a line that reads oddly.
- Prefer short lines (under ~15 words) that stand alone without context.
- Tag the speaker as player-and-character: *"— Josh, as Coriac"* or *"— Zack, out of
  character"*.

---

## Session edition skeleton

Target 700–1000 words: a five-minute read. Sections in order. Leave out any that the session
can't fill honestly; never pad.

```markdown
---
title: "The Session Skald — Session <N>"
type: skald
edition: session
sessions: [<N>]
issue_date: "<YYYY-MM-DD>"
subject_line: "<the email-style subject: punchy, a little cryptic>"
quiz_answer: "<letter> — <one-line explanation>"
---

<Month D, YYYY> · Session <N>

# THE SESSION SKALD

**But first:** <one teaser line pointing at the funniest or strangest thing below>

### QUOTE OF THE NIGHT
## "<table quote>"
— <Player>, <as Character | out of character>. <one wry line of context>

---

**Good evening.** <2–4 sentences: a short personal aside from the DM about the session —
prep chaos, a moment that surprised him, the vibe at the table — then a one-line preview of
the big stories below.>

**— WR / Dungeon Master / Bellwether House, Ravencrest**

---

<KICKER IN CAPS, 1–3 WORDS>
## <Lead headline, Title Case>

**What's going on:** <the main event, 4–6 sentences. Who, where, what happened, told
straight with asides.>

**<Second bold label, e.g. "The stakes:", "Why it matters:", "Vibe check:">** <what it
means going forward, 3–5 sentences. End on a kicker.>

**Related:** <one cross-reference: an older moment this connects to>

---

## The News in <N>

🗞 <fact sentence>. <kicker sentence.>
🗞 ... (3–6 items: the smaller beats, NPC cameos, loot, money)

---

<KICKER>
## <Second story headline>

**What's going on:** ...
**<Label>:** ...

---

## Family Watch

**Artcoth (Uncle Craig):** <2–3 sentences, what he did and the best moment of his night>
**Gareth (Zack):** ...
**Coriac (Josh):** ...
<If one of the three missed the session, say so lightly.>

---

## Behind the Screen 🤫

<"I can't look away." energy. 1–3 short items from the DM side, each one a reveal or a
prep-vs-reality story: what the party missed, what was planned, the lore under tonight's
scene, or a hint of what's coming. Each item 2–4 sentences, ending on a kicker.
Nothing in here is known to the party.>

---

## Quick Hits

<emoji> <one-liner: a bit, a table moment, a minor NPC, a running joke. Kicker in the same line.>
(4–6 items)

---

## IN OUR ROTATION ✴︎

<1–2 in-world "sponsored" plugs, written like Skimm ads, for things that exist in the
campaign: an NPC's business, a magic item, Ovaltine's tonics.>*

---

## ON OUR CALENDAR

**<next session date or "TBD">** — <emoji> **Session <N+1>** — <one-line cliffhanger setup>
<emoji> **<in-world deadline or clock>** — <one line>

---

## KNOW IT ALL

**<a multiple-choice question about this session or the campaign so far>**

A. ...
B. ...
C. ...

*Last issue's answer: <from the previous issue's quiz_answer, if any>*

---

*Skimm'd by: WR. Fact-checked by Bramwell, who got most of it wrong.*
*\*PS: This is a sponsored post. No gold changed hands. Probably.*
```

## Recap edition skeleton ("The Story Til Now")

A one-off catch-up covering many sessions. Target 1800–2500 words. Same voice and furniture,
but organized by arc, with a cast list up front, and closer to a Sunday edition (chattier,
the "Deeply important information" energy).

```markdown
---
title: "The Session Skald — The Story Til Now"
type: skald
edition: recap
sessions: [1, ..., <N>]
issue_date: "<YYYY-MM-DD>"
subject_line: "..."
quiz_answer: "..."
---

<date> · Sessions 1–<N>

# THE SESSION SKALD
### Special Edition: The Story Til Now

**But first:** ...

**Happy <weekday>.** <editor's note: why this issue exists ("you asked what your family
does on game night"), and how to read it.>

**— WR / Dungeon Master / Bellwether House, Ravencrest**

---

## Meet the Party

<One entry per PC, family first. Two or three sentences each: who they are in one line,
the defining thing they've done, one tease. Format:>

**Artcoth** · played by Uncle Craig · <class with a wry gloss, e.g. "Rogue (professional sneak)">
<sentences>
🤫 <optional: one line on what the character doesn't know about themselves yet>

(... all six)

---

## Deeply Important Information
<4–6 one-liners: the setting in a nutshell (the world, the town, the house, the ship,
the money). The things you need to follow the rest.>

---

<KICKER>
## Arc 1 — <name, retitled as a headline>
**What's going on:** ...
**How it ended:** ...

(one story block per arc, 2–3 paragraphs each)

---

## The Greatest Hits
🗞 <the best individual moments across the whole campaign, 6–10 items, with kickers>

---

## Behind the Screen 🤫
<the "Send help." section. 3–5 items: the best dramatic irony and secret threads across the
campaign so far: what the party still hasn't figured out, plans that went sideways, and a
hint or two at where it's all heading. DM picks which secrets go in.>

---

## Where Things Stand
<present tense, one paragraph: where they are now, what's in motion. Ends with a hook
pointing at the next session edition.>

## ON OUR CALENDAR / KNOW IT ALL / sign-off
<as in the session edition>
```
