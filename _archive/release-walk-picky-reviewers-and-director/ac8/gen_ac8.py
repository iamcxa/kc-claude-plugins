import sys, json, shutil
from pathlib import Path
sys.path.insert(0, sys.argv[2])
import test_release_acceptance as T
from PIL import Image, ImageDraw

OUT = Path(sys.argv[1])
if OUT.exists():
    shutil.rmtree(OUT)
wf, folder = T.build_world(OUT / "world_tmp", with_walk=False)
shutil.move(str(OUT / "world_tmp/wf"), str(OUT / "world"))
shutil.rmtree(OUT / "world_tmp")
folder = OUT / "world/.spacedock-state/r1-acceptance"
walk = folder / "walk"

def pic(name, title, body, blocks=(), cut=False):
    img = Image.new("RGB", (800, 520), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 800, 40], fill=(40, 60, 110))
    d.text((12, 14), "Neighborhood Library  |  Reader view", fill="white")
    d.text((20, 60), title, fill="black")
    y = 90
    for line in body:
        d.text((20, y), line, fill=(30, 30, 30)); y += 22
    for (x0, y0, x1, y1, label, fill) in blocks:
        d.rectangle([x0, y0, x1, y1], fill=fill, outline="black")
        d.text((x0 + 8, y0 + 8), label, fill="black")
    if cut:
        d.rectangle([0, 500, 800, 520], fill=(200, 200, 200))
        d.text((12, 504), "(bottom edge of the window at 1366x768, nothing below is visible without scrolling)", fill="black")
    (walk).mkdir(parents=True, exist_ok=True)
    img.save(walk / name)

grey, green, red, amber = (210, 210, 210), (170, 220, 170), (240, 170, 170), (245, 220, 150)
pic("shot.png", "Library home", ["Search the catalogue", "Your reservations: 1"], [(20, 200, 300, 250, "Reserve a copy", green)])
pic("o1.png", "Reservation 'Dune' - status", ["Status: Checking...  (spinner has run for 2 minutes)", "The 'Check if ready' button is greyed out."],
    [(20, 200, 260, 250, "Check if ready (disabled)", grey), (20, 280, 400, 330, "Status: Checking...", amber)])
pic("s1.png", "Reservation 'Dune' - status", ["Status: Checking...", "Pressing 'Check if ready' does nothing; no message appears."],
    [(20, 200, 260, 250, "Check if ready (disabled)", grey), (20, 280, 400, 330, "Status: Checking...", amber)])
pic("o2.png", "Reserve a copy", ["Pick a title, a branch and a pickup day.", "Long form with five fields...", "Field 1  Field 2  Field 3  Field 4  Field 5"],
    [(20, 130, 700, 480, "(form fields)", (235, 235, 245))], cut=True)
pic("s2.png", "Reserve a copy", ["The Reserve button is not on screen; I had to Tab through every field to find it."],
    [(20, 130, 700, 480, "(form fields)", (235, 235, 245))], cut=True)
pic("s3.png", "Reservation 'Dune' - reader view", ["Status: Ready at the front desk", "Hold deadline: Friday", "There is no link or button to collect the book."],
    [(20, 200, 300, 250, "Back to my reservations", grey)])
pic("o3.png", "Reservation list", ["Label reads 'Reserve a copy' on one page and 'Hold a book' on another."],
    [(20, 200, 300, 250, "Hold a book", green)])
pic("s4.png", "Reservation 'Dune' - status", ["Status: Ready at the front desk", "(page fully loaded; the picture carries no timings)"],
    [(20, 200, 300, 250, "Back to my reservations", grey)])
pic("o-collect.png", "Reservation 'Dune' - desk staff view", ["Status: Ready at the front desk", "Signed in as desk staff"],
    [(20, 200, 300, 250, "Collect (staff only)", green)])

o, s = T.reviewer_o(), T.reviewer_s()
fix = {"o1": "o1.png", "o2": "o2.png", "o3": "o3.png", "s1": "s1.png", "s2": "s2.png", "s3": "s3.png", "s4": "s4.png"}
for r in (o, s):
    for c in r["complaints"]:
        c["evidence"] = [fix[c["id"]]]
o["stories"][2]["evidence"] = ["o-collect.png"]
o["stories"][2]["entry"] = "signed in as desk staff"
s["stories"][2]["entry"] = "reader view"
o["complaints"][0]["seen"] = "The status stays on 'Checking...' for two minutes and the Check button is disabled, so I cannot tell if my book is ready."
s["complaints"][0]["seen"] = "Check if ready does nothing; I never learn whether the book is ready."
o["complaints"][1]["seen"] = "Reserve button is below the fold at laptop size."
s["complaints"][1]["seen"] = "Could not see the Reserve button without tabbing through five fields."
s["complaints"][2]["seen"] = "As a reader I found no way to collect the book from the reservation page."
s["complaints"][3]["seen"] = "The page felt like it took about ten seconds to load."
o["complaints"][2]["seen"] = "Two labels for the same action: 'Reserve a copy' and 'Hold a book'."
T.write_walk(folder, [o, s])
for p in list(walk.glob("ruling-sonnet.json")):
    p.unlink()
(walk / "shot.png").exists()
print(folder)
