"""Record the LinkedIn demo (1080x1350): python3 demo/luncheon/record_video.py [page url], with the page served locally
(python3 -m http.server 8765 --directory demo/luncheon). Needs Playwright with Chrome. Then encode:
  ffmpeg -f concat -safe 0 -i demo/luncheon/video/list.txt -vf "fps=30,format=yuv420p" -c:v libx264 -preset slow -crf 18 -movflags +faststart demo.mp4"""
import base64, os, sys
from playwright.sync_api import sync_playwright
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "video")   # frames + list.txt; then see the ffmpeg line at the end
W, H = 1080, 1350 + 87   # the screencast drops the bottom 87px, so the page is that much taller than the 1080x1350 frame
PAD = 87
URL = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/index.html") + "#video"
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith(".jpg") and f.startswith("f"): os.remove(os.path.join(OUT, f))
frames = []
PLAN = """() => { const L = window.__luncheon, z = L.st.puzzle, F = L.FREE, C = s => L.clashes({seatGuest: s, sec: z.groups}, z.judge).length;
  let seat = z.seat.slice(), out = [];
  for (let step = 0; step < 9 && C(seat) > 0; step++) {
    let best = null, n0 = C(seat);
    for (const a of F) for (const b of F) { if (a >= b) continue; const s = seat.slice(); const t = s[a]; s[a] = s[b]; s[b] = t; const n = C(s);
      if (n < n0 && (!best || n < best.n || (n === best.n && Math.abs(a - b) < Math.abs(best.a - best.b)))) best = { a, b, n }; }
    if (!best) break; const t = seat[best.a]; seat[best.a] = seat[best.b]; seat[best.b] = t; out.push([best.a, best.b]);
  }
  return out; }"""
SCREEN = """([k]) => { const L = window.__luncheon, p = L.seatXY(k), r = document.getElementById('stage').getBoundingClientRect();
  const wx = p.side * 190; return [r.left + innerWidth / 2 + (wx - L.cam.x) * L.cam.s, r.top + r.height / 2 + (p.y - L.cam.y) * L.cam.s]; }"""
CLOSEUP = """([a, c]) => { const L = window.__luncheon, ya = L.seatXY(a).y, yb = L.seatXY(c).y, top = 250, bot = 1070;
  const s = Math.min(1.42, (bot - top) / (Math.abs(ya - yb) + 140)), mid = (ya + yb) / 2;
  L.goTo(0, mid - ((top + bot) / 2 - innerHeight / 2) / s, s); }"""
def title(pg, b, s=""):
    pg.evaluate("([b, s]) => { const v = document.getElementById('vcap'); v.style.opacity = 0; setTimeout(() => { v.innerHTML = '<b>' + b + '</b>' + (s ? '<span>' + s + '</span>' : ''); v.style.opacity = 1; }, 300); }", [b, s])
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True, args=["--window-size=1200,1600"])
    pg = b.new_page(viewport={"width": W, "height": H}, screen={"width": 1200, "height": 1600}, device_scale_factor=1)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
    pg.add_init_script("window.__vidPad = 87;"); pg.add_init_script("Math.random = (function () { let s = 20260929; return function () { s = (s * 16807) % 2147483647; return s / 2147483647; }; })();")
    pg.goto(URL, timeout=60000); pg.wait_for_timeout(2500)
    pg.add_style_tag(content="body.video #vcap { bottom: 87px !important; padding: 22px 56px 40px !important; background: linear-gradient(rgba(251,251,249,0), rgba(251,251,249,.94) 26px); } body.video .toast { bottom: 317px !important; }")
    cdp = pg.context.new_cdp_session(pg)
    def on_frame(ev):
        frames.append((ev["metadata"]["timestamp"], ev["data"]))
        try: cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
        except Exception: pass
    cdp.on("Page.screencastFrame", on_frame)
    pg.mouse.move(W * 0.82, H * 0.72)
    # open straight on the action: the table scrambling, p(doom) already boiling, the title already up
    pg.evaluate("([b, t]) => { document.getElementById('vcap').innerHTML = '<b>' + b + '</b><span>' + t + '</span>'; window.__luncheon.story(1); }",
                ["Someone scrambles the seats", "Every clash pushes p(doom) past 1, which isn\u2019t how probability works."])
    cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "maxWidth": 1080, "maxHeight": 1350, "everyNthFrame": 1})
    pg.wait_for_timeout(3000)
    plan = pg.evaluate(PLAN); print("plan:", plan)
    title(pg, "Drag guests to swap seats", "Clear every clash and p(doom) drops to zero.")
    for a, c in plan:
        pg.evaluate(CLOSEUP, [a, c]); pg.wait_for_timeout(1250)
        x0, y0 = pg.evaluate(SCREEN, [a]); x1, y1 = pg.evaluate(SCREEN, [c])
        pg.mouse.move(x0, y0, steps=14); pg.wait_for_timeout(180)
        pg.mouse.down(); pg.wait_for_timeout(120)
        pg.mouse.move(x0 + (x1 - x0) * 0.1, y0 + (y1 - y0) * 0.1 + 6, steps=4)
        pg.mouse.move(x1, y1, steps=28); pg.wait_for_timeout(160)
        pg.mouse.up(); pg.wait_for_timeout(1200)
    print("after fixing:", pg.evaluate("() => { const z = window.__luncheon.st.puzzle; return [z.done, z.moves, z.pd]; }"))
    pg.mouse.move(W * 0.86, H * 0.8, steps=12)
    pg.evaluate("window.__luncheon.fit()")
    title(pg, "p(doom) 0.00. Lunch is served.", "That’s one timeline saved.")
    pg.wait_for_timeout(2800)
    pg.evaluate("window.__luncheon.story(4)"); pg.wait_for_timeout(60); pg.evaluate("window.__luncheon.goTo(0, 40, 0.045)")
    title(pg, "Now every other timeline", "Each host words the rules their own way. Red means p(doom) boiled over.")
    pg.wait_for_timeout(3800)
    pg.evaluate("window.__luncheon.wave('fixed')")
    title(pg, "Our tiny AI reads every host’s rules", "Nine in ten timelines saved.")
    pg.wait_for_timeout(5000)
    title(pg, "Seat Intelligence (SI)", "Play it at seat-intelligence.com")
    pg.wait_for_timeout(3000)
    cdp.send("Page.stopScreencast"); pg.wait_for_timeout(300)
    print("frames:", len(frames), "errors:", errs)
    b.close()
frames.sort(key=lambda f: f[0])
with open(f"{OUT}/list.txt", "w") as L:
    for i, (ts, data) in enumerate(frames):
        fn = f"{OUT}/f{i:05d}.jpg"; open(fn, "wb").write(base64.b64decode(data))
        dur = (frames[i + 1][0] - ts) if i + 1 < len(frames) else 1.0
        L.write(f"file '{fn}'\nduration {max(0.001, dur):.4f}\n")
    L.write(f"file '{OUT}/f{len(frames) - 1:05d}.jpg'\n")
print("span:", round(frames[-1][0] - frames[0][0], 1), "s")
