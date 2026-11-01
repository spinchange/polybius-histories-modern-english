import json
from pathlib import Path

flagships = {
    "cover_front": {
        "filename": "art/cover_front.png",
        "title": "The Historian Between Two Worlds",
        "aspect": "2:3",
        "ref": "Front Cover",
        "alt_text": "Polybius of Megalopolis stands upon an Aegean headland at dusk with papyrus scroll and bronze Arcadian helmet, his gaze directed between distant Greek temple ruins and approaching Roman warships.",
        "caption": "Polybius of Megalopolis between the Greek and Roman worlds."
    },
    "cover_back": {
        "filename": "art/cover_back.png",
        "title": "Ionic Column Fragment and Scroll",
        "aspect": "1:2.2",
        "ref": "Back Cover",
        "alt_text": "An antique engraving of a fluted Ionic column fragment embraced by an unrolled papyrus scroll, an olive branch, and a broken Roman pilum across its base against warm parchment.",
        "caption": "Ionic column fragment with unrolled scroll, olive branch, and broken Roman spear."
    },
    "hero_day": {
        "filename": "art/hero_day.png",
        "title": "The Fifty-Three Years",
        "aspect": "21:9",
        "ref": "Website Hero Banner",
        "alt_text": "A continuous engraved panoramic frieze chronicling Rome's rise across the Mediterranean, passing from quinqueremes boarding enemy galleys to Alpine elephant crossings, phalanxes, senatorial debates, and the burning of Carthage.",
        "caption": "The Fifty-Three Years (264–146 BC): Rome's rise from regional Italian republic to Mediterranean master."
    },
    "hero_night": {
        "filename": "art/hero_night.png",
        "title": "The Fifty-Three Years (Night Variant)",
        "aspect": "21:9",
        "ref": "Website Hero Banner (Night Variant)",
        "alt_text": "A panoramic night variant rendered in gold and cream engraving linework upon a deep umber background, depicting the historical sequence of Roman conquest across the Mediterranean basin.",
        "caption": "The Fifty-Three Years: Night variant rendered in gold and cream engraving linework."
    },
    "og_default": {
        "filename": "art/og_default.png",
        "title": "Polybius at His Desk",
        "aspect": "1.91:1",
        "ref": "Social / Open Graph Card",
        "alt_text": "An engraved portrait of the historian Polybius writing with a reed pen at a stone desk beside a terracotta oil lamp and astrolabe, with empty parchment space on the left.",
        "caption": "Polybius of Megalopolis drafting his Histories."
    },
    "headpiece": {
        "filename": "art/headpiece.png",
        "title": "Greek Meander and Olive Wreath Headpiece",
        "aspect": "4:1",
        "ref": "Chapter Headpiece",
        "alt_text": "A classical ornamental headpiece band featuring Greek meander borders and acanthus scrolls flanking a central roundel with an olive wreath encircling a crossed Macedonian sarissa and Roman pilum.",
        "caption": "Greek meander ornamental headpiece with olive wreath, crossed Macedonian pike, and Roman javelin."
    }
}

books_data = [
    (1, "The corvus at Mylae", "1.22–23",
     "The Roman corvus boarding bridge in action at the Battle of Mylae (260 BC). Book I, 22–23.",
     "A Roman quinquereme drops its spiked corvus boarding bridge across the deck of a Carthaginian galley, allowing legionaries with tall scuta to charge aboard amid splintered oars and sea spray."),
    (2, "Telamon: Gauls caught between two Roman armies", "2.27–31",
     "The Battle of Telamon (225 BC): Celtic warriors surrounded by consular armies in Etruria. Book II, 27–31.",
     "An aerial view of an Etruscan coastal valley where bare-chested Gaesatae warriors with gold torcs and raised carnyx trumpets form a double-fronted battle line against encircling Roman legions."),
    (3, "Hannibal's army descends the Alps in snow", "3.50–56",
     "Hannibal pointing out the fertile plains of Italy to his exhausted army descending the snowbound Alps (218 BC). Book III, 50–56.",
     "A Carthaginian military column with pack mules and gaunt African war elephants winds down a snow-covered Alpine precipice while Hannibal gestures toward the sunlit Italian plains far below."),
    (4, "Byzantium and the Bosporus", "4.38–45",
     "Topographical view of Byzantium and the currents of the Bosporus. Book IV, 38–45.",
     "A detailed topographical panorama of ancient Byzantium perched upon its promontory, where merchant galleys navigate the swirling currents of the Bosporus between Europe and the distant Asian shore."),
    (5, "Raphia: African vs Indian elephants", "5.82–86",
     "The clash of African and Indian war elephants at the Battle of Raphia (217 BC). Book V, 82–86.",
     "Towered Seleucid Indian war elephants collide in a desert dust storm with smaller Ptolemaic African forest elephants, whose trunks and tusks entangle while archers exchange fire from wooden towers."),
    (6, "Roman funeral with ancestral masks", "6.53–54",
     "Actors wearing ancestral wax portrait masks (imagines) at a Roman aristocratic funeral in the Forum. Book VI, 53–54.",
     "In the Republican Roman Forum, actors impersonating illustrious ancestors sit upon ivory curule chairs wearing realistic wax masks and purple-bordered togas, observed with reverence by a young citizen."),
    (7, "The scaling of Sardis citadel", "7.15–18",
     "Lagoras and his commandos scaling the sheer rock of the citadel of Sardis (214 BC). Book VII, 15–18.",
     "Under cover of dawn mist, a daring assault party climbs ladders up the supposedly impregnable cliff of Sardis beneath roosting vultures, while oblivious sentries pace the ramparts above."),
    (8, "Archimedes' claw at Syracuse", "8.5–8",
     "Archimedes' mechanical grappling claw lifting a Roman warship from the sea at the siege of Syracuse (213–212 BC). Book VIII, 5–8.",
     "A massive timber crane atop the sea wall of Syracuse hoists a Roman quinquereme upright out of the water by its prow, while Archimedes observes calmly from the battlements."),
    (9, "Hannibal before the walls of Rome", "9.5–7",
     "Hannibal and the Carthaginian cavalry reconnoitring outside the Servian walls of Rome (211 BC). Book IX, 5–7.",
     "Hannibal leads a vanguard of Numidian and Carthaginian horsemen along the imposing stone ramparts of Rome at sunset, observing the anxious citizens and defenders manning the Servian walls."),
    (10, "Scipio wades the lagoon at New Carthage", "10.8–15",
     "Publius Cornelius Scipio directing the amphibious assault across the low-tide lagoon at New Carthage (209 BC). Book X, 8–15.",
     "Roman legionaries carrying scaling ladders wade through the shallow saltwater lagoon at ebb tide toward an uncrested city wall, while the youthful Scipio directs operations from an elevated rise."),
    (11, "Death of Hasdrubal at the Metaurus", "11.1–3",
     "The heroic death of Hasdrubal Barca, charging into the Roman ranks at the Battle of the Metaurus (207 BC). Book XI, 1–3.",
     "On a riverbank strewn with fallen soldiers and wounded elephants, Hasdrubal Barca spurs his horse alone into the closing ranks of Roman legionaries, choosing a soldier's death over captivity."),
    (12, "The historian's craft: Polybius vs Timaeus", "12 passim",
     "The contrast of historical methods: the library scholar Timaeus versus the eyewitness explorer Polybius. Book XII passim.",
     "A split allegorical composition showing an ivory-tower historian reading scrolls by lamplight on the left, contrasted with Polybius interviewing an ancient veteran on a wind-swept battlefield on the right."),
    (13, "Nabis and the mechanical \"Apega\"", "13.7",
     "The Spartan tyrant Nabis presenting his mechanical torture device constructed in the image of Queen Apega. Book XIII, 7.",
     "Within a dim Spartan chamber, the tyrant Nabis reveals a life-sized mechanical automaton dressed in royal robes, its outstretched wooden arms concealing sharp iron spikes beneath lavish drapery."),
    (14, "Night burning of Syphax's camps", "14.4–5",
     "The surprise night assault and burning of the Numidian and Carthaginian camps (203 BC). Book XIV, 4–5.",
     "Flames devour the thatched huts of a vast North African encampment under a night sky, sending panic-stricken warriors fleeing into the surrounding darkness where armed Roman troops wait in silence."),
    (15, "Zama: the elephant lanes", "15.9–14",
     "The Battle of Zama (202 BC): Roman maniples opening lanes to channel charging Carthaginian war elephants. Book XV, 9–14.",
     "Roman infantry maniples open clear vertical lanes through their battle lines, allowing Carthaginian war elephants to plunge harmlessly through the gaps under a hail of javelins and sounding horns."),
    (16, "The sea fight off Chios", "16.2–7",
     "The naval battle off Chios between Philip V of Macedon and the allied fleets of Rhodes and Pergamum (201 BC). Book XVI, 2–7.",
     "Oared warships clash amidst churning waters off Chios as a sleek Rhodian quadrireme shears through enemy oars and King Attalus runs his royal flagship ashore to escape Macedonian pursuers."),
    (17, "(lost) The empty scroll", "—",
     "Book XVII — Lost. Nothing of this book survives.",
     "A melancholy archival still life of an unrolled papyrus scroll with a completely blank, aged surface crumbling into dust beside a single green olive branch on a weathered stone plinth."),
    (18, "Freedom of the Greeks proclaimed at the Isthmus", "18.46",
     "Titus Quinctius Flamininus proclaiming the freedom of the Greeks at the Isthmian Games (196 BC). Book XVIII, 46.",
     "A crowded Isthmian stadium erupts in ecstatic jubilation as thousands of Greeks leap up and shower garlands onto a herald and the young Roman general Flamininus upon a stone podium."),
    (19, "(fragment) Shards and a torn scroll", "19.1–2",
     "Fragments of Book XIX: papyrus scraps and archaeological shards. Book XIX, 1–2.",
     "An archival arrangement of three torn Greek papyrus fragments and a chipped red-figure pottery sherd bearing a painted elephant silhouette, resting upon warm parchment with fine engraved shadows."),
    (20, "Antiochus's winter wedding at Chalcis", "20.8",
     "The luxurious winter wedding of Antiochus III at Chalcis while his army idles in quarters (192–191 BC). Book XX, 8.",
     "Inside a festive colonnade on the Euboean coast, an elderly diademed King Antiochus feasts with his young bride while his idle soldiers drink around campfires outside by the cold winter sea."),
    (21, "Smoking out the mines at Ambracia", "21.28",
     "The underground siege warfare at Ambracia: defenders smoking out Roman sappers with charcoal and feathers (189 BC). Book XXI, 28.",
     "An architectural cutaway view beneath city walls showing Greek defenders using a bellows to blow thick, suffocating smoke from burning charcoal and feathers into a Roman subterranean assault tunnel."),
    (22, "The Achaean League assembly", "22.7–10",
     "The federal assembly of the Achaean League in session before visiting Mediterranean embassies. Book XXII, 7–10.",
     "Achaean delegates in woollen himatia sit on stone tiers in an open-air sanctuary as a statesman addresses the assembly, flanked by silent envoys from Rome, Pergamum, and Alexandria."),
    (23, "Philopoemen's last night", "23.12",
     "The death of Philopoemen, 'the last of the Greeks', in the treasury dungeon of Messene (183 BC). Book XXIII, 12.",
     "Chained within a dark underground stone vault, the venerable Achaean general Philopoemen calmly receives a cup of hemlock from a remorseful jailer beneath the flickering glow of a single oil lamp."),
    (24, "Callicrates before the Senate", "24.9",
     "Callicrates of Leontion addressing the Roman Senate to urge Roman intervention in Greece (180 BC). Book XXIV, 9.",
     "The persuasive Achaean diplomat Callicrates delivers an impassioned address before rows of seated Roman senators in togas inside the Curia, while an older Greek delegate watches from the shadows in despair."),
    (25, "(fragment) Lycian envoys at Rome", "25.4",
     "Lycian envoys departing from their coastal tombs to plead their cause before Rome. Book XXV, 4.",
     "Two cloaked Lycian ambassadors stand before monumental rock-cut cliff tombs overlooking the Mediterranean Sea, pausing in somber contemplation before embarking on their diplomatic mission to the Roman Senate."),
    (26, "Antiochus \"Epimanes\" in the streets", "26.1",
     "King Antiochus IV Epiphanes wandering the streets of Antioch incognito in a candidate's toga. Book XXVI, 1.",
     "A flamboyant King Antiochus IV wearing a Roman candidate's white toga over royal robes mingles with astonished citizens in a bustling Antioch market, tossing coins and bantering with common artisans."),
    (27, "The cestros dart", "27.11",
     "The Macedonian cestros: a heavy catapult-dart launched from a sling during the Third Macedonian War (168 BC). Book XXVII, 11.",
     "An engraved technical demonstration showing a Macedonian slinger whirling a two-thonged sling to launch the winged cestros dart, accompanied by an exploded anatomical diagram of the wooden shaft and iron point."),
    (28, "Polybius speaks to the Achaeans", "28.7",
     "Polybius as Hipparch addressing the Achaean council in defense of moderate neutrality (169 BC). Book XXVIII, 7.",
     "A thirty-year-old Polybius in his Achaean cavalry commander's cloak stands before an assembly of elder statesmen and a watchful Roman commissioner, arguing with measured conviction for diplomatic caution."),
    (29, "Popilius draws the circle in the sand", "29.27",
     "Gaius Popilius Laenas drawing a circle around King Antiochus IV Epiphanes at Eleusis (168 BC). Book XXIX, 27.",
     "In the dusty sand outside Alexandria, an unarmed Roman legate traces a circle around the armoured Seleucid king Antiochus IV with a vine staff, demanding a treaty decision before he steps out."),
    (30, "The procession at Daphne", "30.25–26",
     "The opulent military and religious procession staged by Antiochus IV at Daphne near Antioch (166 BC). Book XXX, 25–26.",
     "A magnificent royal pageant winds through the sacred laurel groves of Daphne, featuring silver-shielded phalangites, caparisoned elephants, gilded ceremonial chariots, and women casting perfume from golden urns."),
    (31, "Demetrius slips away from Rome by night", "31.12–15",
     "Prince Demetrius escaping from Italy by night to claim the Seleucid throne, assisted by Polybius (162 BC). Book XXXI, 12–15.",
     "By the pale light of a dockside lantern, the disguised Syrian prince Demetrius boards a waiting Carthaginian merchant ship at Ostia while Polybius observes discreetly from the moonlit harbor quay."),
    (32, "Ariarathes' crown / Pergamum", "32.1, 32.12",
     "The restoration of King Ariarathes V of Cappadocia on the acropolis of Pergamum. Book XXXII, 1, 12.",
     "Upon a towering terrace of the Pergamene acropolis overlooking the steep theatre and altar, King Attalus invests his ally Ariarathes with the royal diadem against a sweeping panoramic mountain horizon."),
    (33, "The goat-milker and the sieve", "33.21",
     "The Greek proverb of the goat-milker and the sieve, symbolizing futile political labor. Book XXXIII, 21.",
     "An engraved circular emblem vignette depicting an ancient fable where one foolish rustic vigorously milks a male goat while another kneels patiently below holding an open wicker sieve."),
    (34, "Swordfish hunting at Scyllaeum", "34.3",
     "Harpooning swordfish in the treacherous currents of the Strait of Messina. Book XXXIV, 3.",
     "In the dawn waters of the Strait of Messina, a lookout perched on a high sea crag signals to fishermen as a bowman braces with a barbed harpoon above a leaping swordfish."),
    (35, "The \"fiery war\" in Celtiberia", "35.1",
     "The 'Fiery War' in Celtiberia: Spanish warriors resisting Roman legions in the mountain passes (153–151 BC). Book XXXV, 1.",
     "Celtiberian warriors armed with curved falcatas and round shields ambush a Roman infantry column in a rocky mountain defile beneath a sky filled with smoke from burning hilltop citadels."),
    (36, "Carthage surrenders its arms", "36.4–7",
     "The elders of Carthage surrendering their armour and catapults to the Roman consuls (149 BC). Book XXXVI, 4–7.",
     "Outside the majestic walls of Carthage, long lines of wagons deposit thousands of bronze breastplates, shields, and catapults before seated Roman consuls, while bareheaded Punic magistrates stand in silent mourning."),
    (37, "(fragment) Mouseion beneath Olympus", "37.1",
     "The sanctuary of the Muses at the foot of Mount Olympus. Book XXXVII, 1.",
     "A serene classical landscape showing the snow-crowned peaks of Mount Olympus rising through ethereal clouds above an intimate Doric sanctuary and sacred laurel grove dedicated to the Muses."),
    (38, "Scipio weeps over Carthage", "38.22",
     "Scipio Aemilianus weeping over the destruction of Carthage and quoting Homer to Polybius (146 BC). Book XXXVIII, 22.",
     "Standing upon an overlooking hill at twilight, a grieving Scipio Aemilianus clasps the hand of his friend Polybius as smoke and flames consume the circular naval harbour and citadel of Carthage."),
    (39, "Soldiers playing draughts on Corinth's paintings", "39.2",
     "Roman soldiers playing draughts upon discarded panel paintings after the sack of Corinth (146 BC). Book XXXIX, 2.",
     "In a devastated courtyard beneath the scorched Acrocorinth, indifferent Roman legionaries sit on stone ruins playing draughts upon priceless Greek panel paintings laid flat in the dirt, while Polybius watches aghast.")
]

books = []
for b_num, scene, ref, caption, alt_text in books_data:
    books.append({
        "book": b_num,
        "filename": f"art/book_{b_num:02d}_plate.png",
        "scene": scene,
        "ref": ref,
        "caption": caption,
        "alt_text": alt_text
    })

manifest = {
    "title": "Polybius: The Histories (Modern English Edition) Art Manifest",
    "edition": "Modern English Translation",
    "style": {
        "medium": "19th-century archaeological copperplate engraving with restrained watercolour washes",
        "palette": {
            "parchment_ground": "#FAF6EC",
            "iron_gall_ink": "#2B2117",
            "oxblood_umber": "#5B3B2B",
            "burnished_gold": "#D7BD82",
            "muted_earth": "#7A6A55",
            "dark_ground": "#1D1813",
            "dark_ink_gold": "#D7BD82",
            "dark_ink_cream": "#E8DDC8"
        },
        "license": "CC0 1.0 Universal Public Domain Dedication"
    },
    "flagships": flagships,
    "books": books
}

# Validation
all_items = list(flagships.items()) + [(f"book_{b['book']}", b) for b in books]
errors = []
for name, item in all_items:
    alt = item["alt_text"]
    words = alt.split()
    wc = len(words)
    if wc < 25 or wc > 45:
        errors.append(f"{name} alt_text word count out of range (25-45): {wc} words: '{alt}'")
    if "image of" in alt.lower() or "picture of" in alt.lower():
        errors.append(f"{name} alt_text contains forbidden phrase: '{alt}'")

print(f"Total items checked: {len(all_items)}")
print(f"Errors found: {len(errors)}")

if errors:
    for e in errors:
        print("  ERROR:", e)
    raise SystemExit(1)

out_path = Path("work/art/manifest.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {out_path} ({out_path.stat().st_size} bytes)")
