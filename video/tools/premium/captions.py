# Example from the bread explainer: builds word-by-word caption chunks (web/chunks.json) from faster-whisper
# words.json + cuts.json + offsets.json. Edit FIX (mis-heard words), EMOJI and KEYS per video.
import json, re
W = json.load(open("words.json")); O = json.load(open("offsets.json"))
cuts = json.load(open("cuts.json"))
FIX = {"Shubaika": "Shubayqa", "needed,": "kneaded,", "flower": "flour", "Club": "club-rush.", "Rush.": None}
EMOJI = {"flatbread": "🫓", "farming.": "🌾", "farming?": "🌾", "Desert,": "🏜️", "crumbs": "🍞", "microscope": "🔬", "dough": "🫓",
         "einkorn,": "🌾", "club-rush.": "🌿", "work.": "💪", "baked.": "🔥", "Phew!": "😮‍💨", "occasions.": "🎉", "grindstones": "🪨",
         "flour": "🌾", "ferns.": "🌿", "question.": "🤔", "Jordan's": "📍", "Europe,": "🌍"}
KEYS = {"flatbread", "14,400", "farming.", "farming?", "Jordan's", "Desert,", "crumbs", "Shubayqa", "microscope", "air", "pockets", "einkorn,",
        "club-rush.", "work.", "de-husked,", "ground,", "kneaded,", "baked.", "Phew!", "special", "occasions.", "Europe,", "30,000-year-old",
        "grindstones", "flour", "cattails", "ferns.", "open", "question.", "bread"}
words = []
for k, (i, a, b) in enumerate(cuts):
    for s, e, w in W[str(i)]:
        w = w.strip()
        if w in FIX:
            w = FIX[w]
            if w is None: words[-1]["e"] = round(e - a + O["offsets"][k], 3); continue
        s, e = s - a + O["offsets"][k], e - a + O["offsets"][k]
        if words and re.match(r"^[,\-][0-9A-Za-z]", w):
            words[-1]["w"] += w; words[-1]["e"] = round(e, 3)
            words[-1]["key"] = words[-1]["w"] in KEYS; words[-1]["emo"] = EMOJI.get(words[-1]["w"], ""); continue
        words.append({"w": w, "s": round(max(s, O["offsets"][k]), 3), "e": round(e, 3), "key": w in KEYS, "emo": EMOJI.get(w, "")})
# "a sign. They" -> keep as is but drop the stray period
for x in words:
    if x["w"] == "sign.": x["w"] = "sign"
    if x["w"] == "They": x["w"] = "they"
# chunking: break at punctuation, pause > 0.25s, 3 words or > 17 chars, scene boundary
chunks, cur = [], []
bounds = set(round(o, 3) for o in O["offsets"])
for i, x in enumerate(words):
    if cur and (len(cur) >= 3 or sum(len(y["w"]) for y in cur) + len(x["w"]) > 17 or x["s"] - cur[-1]["e"] > 0.25
                or any(cur[-1]["e"] <= b <= x["s"] + 0.01 for b in bounds) or re.search(r"[.,!?]$", cur[-1]["w"])):
        chunks.append(cur); cur = []
    cur.append(x)
chunks.append(cur)
json.dump(chunks, open("web/chunks.json", "w"), ensure_ascii=False)
for c in chunks: print(f'{c[0]["s"]:6.2f}', " ".join(y["w"] + y["emo"] for y in c))
