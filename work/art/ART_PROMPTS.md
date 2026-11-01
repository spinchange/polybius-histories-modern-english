# Art Prompts — Polybius, *The Histories* (Modern English Edition)

Prompt pack for generating the edition's artwork with Gemini (Argon). Every scene
below was checked against the translated text, and each one notes the chapter it
illustrates.

Covers: print (PDF/paperback), EPUB, website (`build_html.py`), social cards.

---

## 0. How to use this pack

1. **Start every session with the Style Anchor (§1).** Paste it once and then send the
   scene prompts, or paste it in front of each prompt if the model drifts.
2. **Generate the cover and 3–4 book plates first.** Pick the best one and use it as
   the **reference image** for everything after it ("match the style, palette and
   linework of the attached image"). This is the most reliable way to keep 40+
   images looking like one series.
3. **Leave text out of the images.** Put titles, book numbers and captions on
   afterwards with the edition's own type (Georgia / a Greek-inscriptional
   display face). Image models still garble lettering, especially Greek. Every
   prompt therefore ends with the No-Text Clause.
4. **Generate large and crop down.** Make the master at the largest size the model
   offers, then crop it for each format (§2). Prompts that mention "safe margins"
   leave room for that cropping.
5. **Accuracy pass.** Before accepting an image, check it against the Period Guardrails
   (§1.3). Common failures are Imperial-era Roman armour, stirrups, horned
   helmets and medieval castles.

---

## 1. Style Anchor (paste first)

### 1.1 Series style

> You are illustrating a scholarly but handsome new English edition of Polybius's
> *Histories* (Greek historian, c. 200–118 BC, covering Rome's rise from 264 to
> 146 BC). All images belong to one coherent series.
>
> **Medium:** a hybrid of fine **copperplate engraving / etching linework** and
> restrained **watercolour washes**, like a 19th-century archaeological folio
> plate made with modern composition. Confident cross-hatching in the shadows,
> crisp contour lines, paper texture visible.
>
> **Palette (strict):** warm parchment ground **#FAF6EC**, iron-gall ink brown
> **#2B2117**, deep oxblood/umber accent **#5B3B2B**, burnished gold **#D7BD82**,
> muted earth **#7A6A55**. Allowed extras, used sparingly: Tyrian purple, Aegean
> blue-grey, terracotta red. No neon, no saturated modern colour, no glossy
> digital rendering.
>
> **Light:** low, raking Mediterranean light. Long shadows, dust or sea haze in the
> air, quiet drama. Think Jacques-Louis David's restraint with Piranesi's depth.
>
> **Mood:** serious, humane, observant. Polybius was an eyewitness and a
> statesman. Show causes, consequences and human faces rather than glorified
> gore. Violence is implied, not graphic.
>
> **Composition:** clear focal hierarchy, strong silhouette that reads at thumbnail
> size, generous negative space at the top for later typography.

### 1.2 No-Text Clause (end every prompt with this)

> No text, letters, inscriptions, captions, signatures, watermarks or logos
> anywhere in the image. Any shields or banners carry only abstract devices.

### 1.3 Period Guardrails (append when people or armies appear)

> Historical accuracy, 3rd–2nd century BC:
> - **Romans (Republic):** bronze Montefortino helmets with horsehair or feather
>   crests, **mail shirts or square bronze pectoral plates**, tall oval curved
>   *scutum*, *pilum*, short Spanish sword. **No** segmented plate armour
>   (lorica segmentata), no rectangular Imperial shields, no eagles on poles.
> - **Hellenistic Greeks/Macedonians:** linen or bronze cuirasses, Thracian or
>   Phrygian helmets, round bronze-faced shields, the **sarissa** pike (5–6 m) in
>   phalanx.
> - **Carthaginians:** mixed army of Libyan infantry, Numidian light cavalry
>   (no saddle, no bridle, javelins), Iberians in white tunics edged with purple,
>   Balearic slingers, Gauls.
> - **Gauls:** long swords, tall flat shields, torcs, trousers, some fighting
>   bare-chested. **No horned helmets.**
> - **Cavalry:** **no stirrups**, saddle-cloths only.
> - **Ships:** oared war galleys (triremes, quinqueremes) with bronze rams, painted
>   eyes on the bow, square sails stowed for battle.
> - **Architecture:** Doric/Ionic temples, ashlar city walls with towers,
>   Punic harbour architecture at Carthage. **No** medieval or Imperial-Roman
>   monumental buildings (no Colosseum, no domes).

---

## 2. Format & Size Specs

Ask the model for the aspect ratio; resize or crop later.

| Use | Aspect | Target px | Notes |
|---|---|---|---|
| Print front cover (6×9 in) | 2:3 | 1800×2700+ (300 dpi) | Top 35% kept quiet for title |
| Print full wrap (cover+spine+back) | ~2.1:1 | per printer template | Generate wide, place focal on right |
| EPUB cover | 1:1.6 | 1600×2560 | Must read at 160 px thumbnail |
| Book frontispieces / plates | 2:3 or 4:5 | 1600×2400 | One per book, §4 |
| Chapter headpieces | 4:1 | 2400×600 | Ornamental band, §5 |
| Tailpieces / fleurons | 1:1 | 800×800 | Transparent or parchment bg |
| Website hero | 16:9 / 21:9 | 2560×1440 / 2560×1100 | Must work in light & dark mode |
| Open Graph / social card | 1.91:1 | 1200×630 | Text overlay added later on left 45% |
| Square social (Instagram) | 1:1 | 1080×1080 | |
| Story / vertical | 9:16 | 1080×1920 | |

**Dark-mode note:** the site switches to a dark theme (`#1D1813` bg, `#E8DDC8` ink).
For hero and inline art, make a second variant with the prompt modifier:
*"Night variant: the same composition rendered as a gold-and-cream line engraving
on a deep umber-black ground (#1D1813), lines in #D7BD82 and #E8DDC8."*

---

## 3. Flagship Images

### 3.1 Front cover — "The Historian Between Two Worlds"
> Aspect 2:3, portrait. A Greek historian in his fifties, Polybius of Megalopolis:
> lean, weathered, close-cropped grey beard, plain travelling cloak over a chiton.
> He stands on a rocky headland at dusk, seen from slightly below, one hand
> holding a half-unrolled papyrus scroll and the other resting on a bronze
> Arcadian cavalry helmet set on a rock. Behind him the Mediterranean opens out.
> On the left horizon is the faint silhouette of a Greek city with a Doric
> temple; on the right, Roman galleys with bronze rams catch the last light. His
> gaze is steady and searching, looking out of the frame. The top third is open
> sky in warm parchment haze, kept clear for a title. Engraving linework with
> watercolour wash in the series palette. *[Style Anchor] [Period Guardrails]
> [No-Text Clause]*

**Alt cover A — "The Oikoumene" (typographic-friendly):**
> Aspect 2:3. An antique engraved map of the Mediterranean world c. 150 BC, from
> Iberia to Syria and Egypt, drawn as one interconnected whole. Thin gold lines
> trace routes between Rome, Carthage, Corinth, Alexandria and Antioch and come
> together toward Rome like threads drawn into a single knot. Sea in parchment
> tone with fine engraved wave hatching; land in pale umber wash; small
> pictorial vignettes of a galley, an elephant, a phalanx and a temple. Central
> upper area left clear. *[No-Text Clause — no place names; labels will be
> typeset later]*

**Alt cover B — "Fortune's Wheel" (symbolic):**
> Aspect 2:3. A bronze relief medallion, as if cast in antiquity and then
> engraved, showing Tyche (Fortune) as a calm crowned woman holding a ship's
> rudder and a cornucopia. Around her rim, small relief scenes of rising and
> falling powers: Carthage, Macedon, Syria, Rome. The medallion sits on parchment
> with ink-hatched shadow and a subtle gold leaf highlight. *[No-Text Clause]*

### 3.2 Back cover / spine companion
> Aspect 1:2.2 (tall strip). A single Ionic column fragment wrapped by a
> half-unrolled scroll, olive branch and broken Roman pilum laid across its base,
> parchment ground, engraving style, centred with vast negative space above and
> below. *[No-Text Clause]*

### 3.3 Website hero — "The Fifty-Three Years"
> Aspect 21:9, ultra-wide panorama. One continuous engraved frieze that moves
> left to right through Rome's rise: Roman boarding bridges crashing onto
> Carthaginian galleys; elephants crossing snowbound Alpine passes; a Macedonian
> phalanx bristling with sarissas in hill fog; a Roman senator in a toga
> receiving foreign envoys; and finally a burning harbour city at the far right,
> with a lone Roman general and a Greek companion watching from a rise. The
> scenes run together seamlessly like a Parthenon-style frieze, with
> watercolour wash fading to parchment at both ends for responsive cropping.
> *[Style Anchor] [Period Guardrails] [No-Text Clause]*
> Then request the **Night variant**.

### 3.4 Default social card (Open Graph)
> Aspect 1.91:1. Right half: a close three-quarter engraved portrait of a Greek
> historian (Polybius) lit from the right, quill in hand, scroll spread on a
> stone table with a small bronze astrolabe-like instrument and a clay lamp. Left
> 45%: empty warm parchment with faint engraved wave-hatching texture, reserved
> for a title overlay. High contrast so it survives compression at small sizes.
> *[No-Text Clause]*

---

## 4. Book Plates (frontispiece for each book)

One plate per book, used as the EPUB/print section opener, the website book header
and that book's social card. Use the **Style Anchor + Period Guardrails +
No-Text Clause** for every plate, and a **2:3 portrait** unless noted.
Reference chapters are given for fact-checking and captions.

| Book | Scene | Ref |
|---|---|---|
| 1 | The corvus at Mylae | 1.22–23 |
| 2 | Telamon: Gauls caught between two Roman armies | 2.27–31 |
| 3 | Hannibal's army descends the Alps in snow | 3.50–56 |
| 4 | Byzantium and the Bosporus | 4.38–45 |
| 5 | Raphia: African vs Indian elephants | 5.82–86 |
| 6 | Roman funeral with ancestral masks | 6.53–54 |
| 7 | The scaling of Sardis citadel | 7.15–18 |
| 8 | Archimedes' claw at Syracuse | 8.5–8 |
| 9 | Hannibal before the walls of Rome | 9.5–7 |
| 10 | Scipio wades the lagoon at New Carthage | 10.8–15 |
| 11 | Death of Hasdrubal at the Metaurus | 11.1–3 |
| 12 | The historian's craft: Polybius vs Timaeus | 12 passim |
| 13 | Nabis and the mechanical "Apega" | 13.7 |
| 14 | Night burning of Syphax's camps | 14.4–5 |
| 15 | Zama: the elephant lanes | 15.9–14 |
| 16 | The sea fight off Chios | 16.2–7 |
| 17 | *(lost)* The empty scroll | — |
| 18 | Freedom of the Greeks proclaimed at the Isthmus | 18.46 |
| 19 | *(fragment)* Shards and a torn scroll | 19.1–2 |
| 20 | Antiochus's winter wedding at Chalcis | 20.8 |
| 21 | Smoking out the mines at Ambracia | 21.28 |
| 22 | The Achaean League assembly | 22.7–10 |
| 23 | Philopoemen's last night | 23.12 |
| 24 | Callicrates before the Senate | 24.9 |
| 25 | *(fragment)* Lycian envoys at Rome | 25.4 |
| 26 | Antiochus "Epimanes" in the streets | 26.1 |
| 27 | The *cestros* dart | 27.11 |
| 28 | Polybius speaks to the Achaeans | 28.7 |
| 29 | Popilius draws the circle in the sand | 29.27 |
| 30 | The procession at Daphne | 30.25–26 |
| 31 | Demetrius slips away from Rome by night | 31.12–15 |
| 32 | Ariarathes' crown / Pergamum | 32.1, 32.12 |
| 33 | The goat-milker and the sieve | 33.21 |
| 34 | Swordfish hunting at Scyllaeum | 34.3 |
| 35 | The "fiery war" in Celtiberia | 35.1 |
| 36 | Carthage surrenders its arms | 36.4–7 |
| 37 | *(fragment)* Mouseion beneath Olympus | 37.1 |
| 38 | Scipio weeps over Carthage | 38.22 |
| 39 | Soldiers playing draughts on Corinth's paintings | 39.2 |

### Prompts

**Book 1 — The corvus at Mylae (260 BC)**
> A Roman quinquereme in close action. Its hinged boarding bridge, the *corvus*,
> a long plank with railings and a heavy iron spike at its tip, has just
> slammed down onto the deck of a Carthaginian galley and pinned it fast.
> Legionaries pour across in a column, shields raised. Spray, splintered oars,
> painted eye on the Carthaginian bow. Viewed from a high angle so the bridge
> forms a strong diagonal.

**Book 2 — Telamon (225 BC)**
> Aerial, map-like engraved view of an Etruscan coastal plain. A huge Gallic
> army is drawn up facing **both ways** at once, with Roman legions closing from
> north and south. In the foreground, a front rank of Gaesatae warriors stand
> bare-chested with gold torcs and long shields, and carnyx war-trumpets with
> boar-head bells are raised over them. Dust, gleam of gold, tension before
> impact.

**Book 3 — Crossing the Alps (218 BC)**
> A narrow, icy mountain ledge in heavy snow. A column of Carthaginian soldiers,
> pack mules and a few gaunt African elephants picks its way downward. Below, a
> sunlit view opens onto the green plains of Italy. A cloaked commander (Hannibal)
> stands on a rock pointing toward the plains, his men's faces turned to follow.
> Cold blue-grey wash in the shadows set against warm gold in the distance.

**Book 4 — Byzantium and the Bosporus**
> A sweeping engraved topographical view of a walled Greek city on a promontory
> above a strait running with strong currents, which are drawn as swirling
> hatching. Merchant ships ride the current from the Black Sea; tunny shoals
> glint below the surface; the far Asian shore is visible. A scholarly
> "geographer's plate" feel with fine detail.

**Book 5 — Raphia (217 BC)**
> Two lines of war elephants collide head-on. On one side are larger Indian
> elephants with towers (Seleucid); on the other, smaller African forest
> elephants (Ptolemaic), which recoil in fear. Tusks interlock, and archers and
> pikemen fight in the towers. Dust clouds glow in desert light. Show the
> difference in size clearly.

**Book 6 — The ancestral masks (Roman funeral)**
> A Roman aristocratic funeral in the Forum. Actors wearing lifelike wax
> portrait masks of the family's ancestors (*imagines*) sit on ivory curule
> chairs in togas with purple borders, preceded by lictors carrying rods. A young
> Roman watches from the crowd, visibly moved and inspired. Solemn, eerie,
> civic. Early Republican Forum with modest temples, no marble Imperial
> grandeur.
> *Alt plate (4:5): engraved bird's-eye plan of a Roman marching camp, a perfect
> square grid of tents, streets and the commander's tent, rendered like an
> antique diagram.*

**Book 7 — The scaling of Sardis (214 BC)**
> A sheer cliff below a citadel at dawn mist. A small party of soldiers climbs
> scaling ladders up the cliff face at its most "impregnable" point, where
> vultures roost on the rocks. Sentries above are looking the other way.
> Vertical composition that stresses height and daring.

**Book 8 — Archimedes' claw (213–212 BC)**
> The sea wall of Syracuse. From behind the battlements a giant wooden crane
> with an iron grappling claw has seized the prow of a Roman galley and is
> hoisting it upright out of the water. Rowers are tumbling, and a second ship
> is being smashed by dropped stones. On the wall, an old bearded man in
> plain Greek dress (Archimedes) watches calmly. Machine drawn with
> Leonardo-like engineering clarity.

**Book 9 — Hannibal before Rome (211 BC)**
> Evening outside Rome's Servian walls. Carthaginian cavalry ride slowly along
> the walls with Hannibal at their head in profile. The city's hills, early
> temples and crowded defenders line the ramparts. Tension without battle:
> the threat itself is the subject.

**Book 10 — New Carthage (209 BC)**
> At low tide, Roman soldiers wade waist-deep across a shallow lagoon toward an
> undefended stretch of city wall, holding ladders above their heads. Behind
> them a young commander (Scipio, clean-shaven, early twenties) watches from a
> rise. The water reflects the walls. Luminous afternoon light.
> *Inset/tailpiece option: Polybius's torch-signal system, two walls with
> rows of torches raised in patterns at night.*

**Book 11 — Metaurus (207 BC)**
> End of a lost battle on a riverbank. A Carthaginian general (Hasdrubal,
> Hannibal's brother) in fine armour charges alone into the Roman ranks rather
> than flee, sword raised. Behind him are fallen elephants and a broken line.
> Heroic, tragic, restrained.

**Book 12 — The historian's craft**
> Split composition. On the left, a pale scholar sits in a lamp-lit library
> among piled scrolls, never having left his room (Timaeus). On the right,
> under open sky, a travel-worn historian (Polybius) walks the actual ground of
> a battlefield, questioning an old veteran and taking notes. The two halves
> meet at a central column. Allegorical, intellectual.

**Book 13 — Nabis and the "Apega"**
> A dim chamber in Sparta. A tyrant (Nabis) presents to a nervous wealthy
> citizen a life-sized, richly dressed statue in the likeness of his queen. Its
> arms open as if for an embrace, and hidden iron nails glint under its gown.
> Menacing, Gothic undertone, **no injury shown**.

**Book 14 — Burning the camps (203 BC)**
> Night in North Africa. Huts of reed and timber in a vast Numidian camp go up
> in flames. Half-dressed soldiers run out in confusion, and Roman troops wait
> in the darkness at the edge. Orange firelight against deep ink-blue shadow.
> The only plate where the palette may push to strong warm contrast.

**Book 15 — Zama (202 BC)**
> Battlefield from a raised viewpoint. Carthaginian war elephants charge, but the
> Roman maniples have opened **lanes** in their formation, and the beasts run
> harmlessly down the corridors as trumpets blare. Velites throw javelins from
> the sides. Two commanders, Scipio and Hannibal, are faintly visible on
> opposite rises.

**Book 16 — Chios (201 BC)**
> A chaotic naval melee. Macedonian and Rhodian/Pergamene galleys ram and grapple.
> One Rhodian ship shears off a row of enemy oars. In the foreground a royal
> flagship is run aground, its king (Attalus) escaping. Bright sea light and
> foam.

**Book 17 — Lost**
> Aspect 2:3. Still life: a papyrus scroll lies unrolled on a stone ledge.
> Its surface is **blank** and faded, the edges crumbling into dust that drifts
> away in a beam of light. A small olive twig rests beside it. Melancholy,
> quiet, much negative space. This plate marks a book of which nothing survives.

**Book 18 — Freedom of the Greeks (196 BC)**
> A packed stadium at the Isthmian Games near Corinth. A herald on a raised
> platform has just announced Rome's proclamation that the Greeks are free. The
> crowd erupts: thousands rise with arms upraised, garlands and ribbons fly,
> and birds startle from the sky. A Roman commander (Flamininus, young,
> clean-shaven) stands near the herald. Joyous light, a sense of irony for
> knowing readers.
> *Alt: Cynoscephalae: a Macedonian phalanx coming over a fog-bound ridge, Roman
> maniples hitting it in the flank.*

**Book 19 — Fragment**
> Still life: three torn papyrus fragments and a broken red-figure pot shard
> lie on parchment, arranged like a museum plate with engraved shadows. A faint
> elephant silhouette shows on one shard. Quiet, archival. *(Shares visual
> family with Books 17, 25, 37.)*

**Book 20 — The wedding at Chalcis (192/191 BC)**
> Winter on the Euboean coast. An aging Hellenistic king (Antiochus III,
> diademed) holds a lavish wedding feast with a young local bride, with
> garlands, musicians and wine, while through an open colonnade his idle army
> can be seen drinking in winter quarters. Ironic warmth inside, grey sea
> outside.

**Book 21 — The mines at Ambracia (189 BC)**
> Cutaway section of the ground beneath a besieged city wall, drawn like an
> engineering diagram. Roman sappers dig a tunnel; defenders have dug a
> counter-mine to meet them. Defenders pump burning feathers and charcoal
> smoke from a large jar with a bellows into the Roman tunnel, and men choke
> and retreat. Ingenious, technical.

**Book 22 — The Achaean League in assembly**
> An open-air assembly in a Peloponnesian sanctuary. Delegates in cloaks sit on
> stone tiers. A speaker stands, and foreign envoys (Roman, Pergamene, Egyptian)
> wait to one side. Democratic deliberation, hills beyond. Calm and civic.

**Book 23 — Philopoemen's fall (183 BC)**
> A dark underground treasury chamber in Messene. The aged Achaean general
> Philopoemen, chained but dignified, receives a cup of poison from a jailer by
> lamplight and asks calmly after his cavalry. Strong chiaroscuro.
> *Companion tailpiece: a funeral procession with a young man carrying a
> garlanded urn. Tradition holds that the young Polybius carried
> Philopoemen's ashes.*

**Book 24 — Callicrates before the Senate (180 BC)**
> The Roman Senate in session in a modest Republican curia. A Greek statesman
> (Callicrates), smooth and persuasive, addresses rows of senators in togas,
> urging Rome to intervene in Greek affairs. In shadow at the back an older
> Achaean listens in dismay. Political drama in the faces.

**Book 25 — Fragment**
> A Lycian rock-cut tomb façade carved into a cliff above the sea. Two envoys in
> travel cloaks pause before it before embarking for Rome. Small, contemplative.

**Book 26 — Antiochus "Epimanes" (the Madman)**
> A Hellenistic king (Antiochus IV) in a white toga worn over his royal robes,
> wandering without bodyguards through an Antioch street. He jokes with
> artisans, tosses coins and gemstones to startled strangers and mimics a Roman
> candidate shaking hands. Crowd reactions range from delight to alarm. Light
> satirical tone, like a Hogarth engraving.

**Book 27 — The *cestros* (168 BC)**
> Technical engraved plate: a Macedonian slinger whirling a two-thonged sling to
> launch the *cestros*, a heavy dart with a short wooden shaft and three
> fins, shown also in an inset as an exploded diagram. Field background of
> the war with Perseus.

**Book 28 — Polybius speaks**
> An Achaean council chamber, 169 BC. A man in his thirties, Polybius, in the
> cloak of a cavalry commander (hipparch), stands to argue for a careful,
> neutral course. Older statesmen listen and a Roman envoy watches. The historian
> as actor in his own history.

**Book 29 — The circle of Popilius (168 BC)**
> A dusty plain outside Alexandria (Eleusis). A stern Roman envoy (Gaius
> Popilius Laenas, in a toga, unarmed) has drawn a **circle in the sand** around
> a richly armoured Hellenistic king (Antiochus IV) with the tip of a vine
> stick, demanding an answer before he steps out. The king's courtiers and
> army stand frozen behind him. A low camera angle on the circle, which is the
> visual centre. One of the most iconic plates; make it strong.

**Book 30 — The procession at Daphne (166 BC)**
> A lavish parade through a sacred grove of laurels and cypress near Antioch:
> silver-shielded troops, elephants in caparisons, gilded chariots, hundreds of
> women sprinkling perfume from golden jars, statues of gods carried high. At the
> edge, a slightly ridiculous king rides about personally directing everything.
> Opulent, crowded, glittering gold leaf.

**Book 31 — Demetrius's escape (162 BC)**
> Night at a Tiber river-mouth harbour. A young Seleucid prince (Demetrius),
> cloaked and hooded, slips aboard a small Carthaginian merchant ship by
> lantern light. On the quay, a Greek friend (Polybius) watches from the
> shadows, having passed him a warning note. Conspiratorial, moonlit.
> *Alt: Polybius and the young Scipio Aemilianus walking together, the moment
> they pledge friendship (31.23–24).*

**Book 32 — Ariarathes & Pergamum**
> Pergamum's acropolis on its steep hill: theatre carved into the slope, the
> great altar, the library. A Cappadocian king (Ariarathes V) is restored by
> his ally Attalus with a royal diadem in a small ceremony on a terrace. Grand
> architecture, small humans.

**Book 33 — The goat-milker and the sieve**
> A wry allegorical vignette from a Greek proverb: in a rustic courtyard one
> man milks a he-goat while another holds a sieve under it. Two fools, one
> futile effort. Engraved like an emblem-book plate, in a round medallion
> frame. Humour, wisdom.

**Book 34 — Swordfish hunting at Scyllaeum**
> The Strait of Messina at dawn. Small two-man rowing boats glide over the
> water; a lookout on a high rock signals; in one boat a harpooner braces with a
> long barbed harpoon above a great swordfish breaking the surface. Distant
> Sicilian coast and smoking Etna. Geographic plate feel.

**Book 35 — The "fiery war" (153–151 BC)**
> A Celtiberian hill-country battle that keeps flaring up. Spanish warriors with
> round shields, falcata swords and dark cloaks raid down a ravine against Roman
> troops, under a smoky red sky, with burning hill-forts in the distance.
> The plate should feel unending and relentless.

**Book 36 — Carthage gives up its arms (149 BC)**
> Outside the walls of Carthage. A long line of carts and porters bring out
> thousands of weapons and armour sets, which form great heaps before the
> seated Roman consuls. Carthaginian elders in long robes stand bareheaded,
> not yet knowing the final demand. The tragedy lies in the quiet.

**Book 37 — Fragment: Mouseion beneath Olympus**
> Aspect 2:3. Mount Olympus rising through cloud above a small sanctuary of the
> Muses at its foot, with a few Doric columns and laurel trees. Serene,
> otherworldly, much negative space. Fragment family style.

**Book 38 — Scipio weeps over Carthage (146 BC)**
> A hilltop at dusk overlooking Carthage in flames: the circular military
> harbour, burning houses, smoke rising into a red-gold sky. In the foreground,
> the Roman general Scipio Aemilianus (late thirties, clean-shaven, plain
> armour, cloak) stands with tears on his face, gripping the hand of his older
> Greek friend Polybius, who looks at him rather than the city. The general is
> reciting Homer: "A day will come when sacred Troy shall perish." Grief, not
> triumph. This is the **emotional climax** of the series.

**Book 39 — Corinth (146 BC)**
> Ruined Corinth after the sack. In a courtyard, bored Roman soldiers sit
> playing draughts on great painted panel paintings thrown flat on the ground.
> The masterpieces' faces look up past the game pieces. At the edge, a Greek
> eyewitness (Polybius) stands and stares. The Acrocorinth rises
> behind, scorched columns. Irony, loss of culture.

---

## 5. Ornaments, Maps & Diagrams

**Headpiece band (chapter openers)**
> Aspect 4:1. A horizontal ornamental band in engraving style: a Greek meander
> (key) pattern border, a central small roundel with an olive wreath around a
> crossed sarissa and pilum, and acanthus scrolls tapering to each end.
> Ink-brown on parchment, gold accents. Must tile or centre cleanly.
> *[No-Text Clause]*

**Tailpiece fleurons (set of 6)**
> Square 1:1, small engraved vignettes on plain parchment, each self-contained
> and symmetrical: (1) a galley ram's bronze head; (2) an elephant in a laurel
> roundel; (3) a Corinthian helmet on an olive branch; (4) a rolled scroll tied
> with a cord; (5) a Rhodian rose; (6) a Tyche wheel. Consistent line weight
> across the set. *[No-Text Clause]*

**Drop caps (frame only)**
> Square 1:1. An empty decorative square frame for a drop capital, filled with
> fine engraved vine and acanthus, the centre left **blank parchment** for a
> typeset letter. Generate 3 variants (naval, military, civic motifs).

**Maps (generate as base art; add labels in Inkscape/Affinity)**
> Aspect 3:2. An engraved antique-style relief map of the **[REGION]** around
> **[DATE]**, without any lettering: hachured mountains, stippled seas with
> engraved wave lines, rivers as fine ink lines, small pictorial symbols for
> cities (tiny walls), and **[FEATURE, e.g., the route of Hannibal's army as a
> dotted gold line]**. Parchment ground, gold and umber washes.
> Suggested regions: Western Mediterranean 264 BC · Italy & the Alps 218 BC ·
> Greece & the Aegean 200 BC · Hellenistic East 190 BC · Carthage & its harbours
> 146 BC.

**Diagram plates (Book 6, Book 10)**
> Aspect 1:1. Antique engraved technical diagram of **[the Roman marching camp
> layout / the torch-signalling board with five tablets of letters / the
> maniple formation of hastati, principes, triarii]**, seen from above, clear
> geometry, numbered markers as **empty circles** only.

---

## 6. Social Media Series

Reuse the book plates first. For campaigns, these extra prompts fit the format:

**"Polybius said it" quote cards (1:1 and 9:16)**
> A tightly cropped detail from an engraved scene, such as **[a hand gripping a
> scroll / a Roman crest against sky / an elephant's eye / a galley ram
> breaking a wave]**. Strong texture, the bottom 50% fading into plain
> parchment for a quote overlay. *[No-Text Clause]*

**Portrait gallery (1:1), one per figure**
> An engraved bust portrait in a laurel-wreathed oval frame, like a coin or
> cameo, of **[NAME]**: **[DESCRIPTION]**. Parchment ground, single gold accent.
> - Hannibal: Carthaginian general, short beard, intense eyes, simple helmet
> - Scipio Africanus: Roman, clean-shaven, confident, early Republic armour
> - Philip V of Macedon: diademed, curled beard, restless energy
> - Antiochus III: mature Hellenistic king with a diadem, broad face
> - Philopoemen: weathered Arcadian soldier-statesman, plain dress
> - Archimedes: elderly mathematician, bearded, absorbed in thought
> - Scipio Aemilianus: thoughtful young Roman noble
> - Polybius: lean Greek in his forties, short beard, observant gaze
> *(Base these on coin portraits or busts where those exist; for Polybius,
> optionally reference the Kleitor stele relief.)*

**"On this day / This happened" series (1.91:1)**
> Reuse the book plates. Ask the model to **outpaint** each 2:3 plate to 1.91:1,
> extending the scene to the left into soft parchment for a headline.

---

## 7. Iteration Phrases (useful follow-ups)

- "Same image, but reduce the colour wash by half; let the linework dominate."
- "Keep the composition; correct the armour to Roman Republic Montefortino
  helmets and mail. Remove segmented armour."
- "Remove all lettering from shields, banners and the sky."
- "Push the engraving texture: finer cross-hatching, visible plate mark border."
- "Outpaint to 16:9, extending sky and sea; keep the subject at the right third."
- "Create the night variant in gold line on umber-black (#1D1813)."
- "Match the style of the attached reference exactly; new subject: …"

---

## 8. Production checklist

- [x] Cover + 3 plates generated and approved as the style reference
- [x] All 39 book plates generated (17, 19, 25, 37 in the "fragment" family)
- [x] Night variants for website hero + any inline web art
- [x] Each image checked against §1.3 Period Guardrails
- [x] No embedded text (zoom to 100%)
- [x] Files named `art/book_NN_plate.png`, `art/cover_front.png`, `art/og_default.png`, etc.
- [x] Image rights / AI-generation disclosure added to the edition colophon
- [x] Alt text written for every image (EPUB accessibility, epubcheck)
