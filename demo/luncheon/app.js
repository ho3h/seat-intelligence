(function () {
  var S = Seating;
  var N = 34, HALF = 17, ROW0 = -354, PITCH = 44.25, PX = 820, PY = 1120;
  var TABLE = "#2e2e2b", INK = "#151515", MUTE = "#6b6b68", RED = "#a8322a", BAD = INK, GOOD = INK, BLUE = INK;
  var TINT = ["#efeeea", "#e1dfd9"];
  var FONT = '"Libre Caslon Text", Georgia, serif', TEXT = '"Source Serif 4", Georgia, serif';
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  var real = DATA.guests.map(function (g) {
    return { name: g.name, org: g.org, cat: S.CID[g.category], label: g.org ? g.name + " – " + g.org : g.name };
  });
  var realEng = real.map(function (g) { return { org: g.org, cat: g.cat, name: g.name }; });
  var potusGi = real.findIndex(function (g) { return g.name === "POTUS"; });
  var shows = DATA.shows, C = DATA.chat;
  shows.forEach(function (sh) { sh.emitted_canon = S.toText(S.parse(sh.emitted)); sh.gold_canon = S.toText(S.parse(sh.gold)); });

  function seatXY(k) { var side = k < HALF ? -1 : 1, row = k < HALF ? k : N - 1 - k; return { side: side, row: row, x: side * 95, y: ROW0 + PITCH * row }; }
  function hitSeat(wx, wy) {
    var ax = Math.abs(wx); if (ax < 58 || ax > 345) return -1;
    var row = Math.round((wy - ROW0) / PITCH); if (row < 0 || row > HALF - 1 || Math.abs(wy - (ROW0 + PITCH * row)) > 22.2) return -1;
    return wx < 0 ? row : N - 1 - row;
  }
  function rng(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; var t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function shuffle(a, r) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(r() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }

  // ---------- rules used by the puzzle and the endless lunches (the tiny AI read each sentence correctly in our tests)
  var H6 = {}; (DATA.h6 || []).forEach(function (r) { H6[r.sentence] = r; });
  var LEVELS = [
    { name: "Easy", sentence: "AI labs and big tech apart. Sections of 5.", prog: "size 5\napart ai_lab big_tech" },
    { name: "Rivals", sentence: "No two government officials in one section, and keep Elon Musk away from OpenAI and from Mark Zuckerberg.", prog: "limit government 1\navoid Elon_Musk OpenAI\navoid Elon_Musk Mark_Zuckerberg" },
    { name: "The busy man", note: "Musk has public history with all three.", sentence: "Keep Elon Musk away from Jeff Bezos, Mark Zuckerberg and OpenAI.", prog: "avoid Elon_Musk Jeff_Bezos\navoid Elon_Musk Mark_Zuckerberg\navoid Elon_Musk OpenAI", minScramble: 1 },
    { name: "The reunion", note: "Amodei and Brown worked at OpenAI before co-founding Anthropic.", sentence: "Put Greg Brockman, Dario Amodei and Tom Brown in the same section.", prog: "pair Greg_Brockman Dario_Amodei\npair Greg_Brockman Tom_Brown", minScramble: 1 },
    { name: "The podcast", note: "Sacks and Palihapitiya co-host the All-In podcast.", sentence: "Seat David Sacks and Chamath Palihapitiya in the same section.", prog: "pair David_Sacks Chamath_Palihapitiya", minScramble: 1 },
    { name: "It\u2019s complicated", note: "Microsoft is OpenAI\u2019s biggest backer. Google makes Gemini, a rival.", sentence: "Keep Microsoft and OpenAI together, and keep Google away from both.", prog: "pair Microsoft OpenAI\navoid Google Microsoft\navoid Google OpenAI", minScramble: 1 },
    { name: "Hard", sentence: "Keep colleagues together, sections of at most four, and never put two government officials in the same section.", prog: "size 4\ntogether company\nlimit government 1" }];
  LEVELS.forEach(function (L) { var r = H6[L.sentence]; if (r && r.ok) { L.prog = r.program; L.secs = r.secs; } });
  var MARK = { 5: ["G", INK, "government official", "government officials"], 0: ["A", INK, "AI lab guest", "AI lab guests"], 1: ["T", "#2f7d4f", "big tech guest", "big tech guests"] };
  // the President and Vice President keep their posted seats, facing each other mid-table; everyone else is seated by the rules
  var vpotusGi = real.findIndex(function (g) { return g.name === "VPOTUS"; });
  var HOSTSEAT = {}; HOSTSEAT[N - 1 - 8] = potusGi; HOSTSEAT[8] = vpotusGi;          // right row 8 and left row 8, as posted
  var FREE = [], GUESTS = [], POS = {};
  for (var k0 = 0; k0 < N; k0++) if (!(k0 in HOSTSEAT)) FREE.push(k0);
  real.forEach(function (g, i) { if (i !== potusGi && i !== vpotusGi) { POS[i] = GUESTS.length; GUESTS.push(i); } });
  var ENG = GUESTS.map(function (i) { return realEng[i]; });
  function isHostSeat(k) { return k in HOSTSEAT; }
  function seatRule(p) {
    var r = S.seat(ENG, p), seat = new Array(N), groups = new Array(N), n = 0;
    r.seq.forEach(function (j) { var k = FREE[n++]; seat[k] = GUESTS[j]; groups[k] = r.assign[j]; });
    Object.keys(HOSTSEAT).forEach(function (k) { seat[k] = HOSTSEAT[k]; groups[k] = null; });
    return { seat: seat, groups: groups };
  }
  function shuffleFree(seat, r) { var vals = FREE.map(function (k) { return seat[k]; }), sh = shuffle(vals, r), out = seat.slice(); FREE.forEach(function (k, n) { out[k] = sh[n]; }); return out; }
  function solve(prog) {
    var p = S.parse(prog), a = seatRule(p);
    return { judge: p, ai: a.seat, groups: a.groups };
  }
  function evalSeats(judge, groups, seat) {
    var assign = new Array(GUESTS.length);
    for (var k = 0; k < N; k++) { var gi = seat[k]; if (gi >= 0 && groups[k] !== null && groups[k] !== undefined && POS[gi] !== undefined) assign[POS[gi]] = groups[k]; }
    var v = S.violations(ENG, judge, assign);
    return { total: v.v.total, bad: v.badSections, v: v.v };
  }
  function markers(judge) {
    var cats = {}, m = {}, cnt = {};
    judge.limits.forEach(function (l) { l[0].forEach(function (c) { cats[c] = 1; }); });
    judge.aparts.forEach(function (a) { cats[a[0]] = 1; cats[a[1]] = 1; });
    real.forEach(function (g) { if (g.org) cnt[g.org] = (cnt[g.org] || 0) + 1; });
    var who = {}, pw = {}; (judge.avoids || []).forEach(function (a) { who[a[0]] = 1; who[a[1]] = 1; }); (judge.pairs || []).forEach(function (a) { pw[a[0]] = 1; pw[a[1]] = 1; });
    real.forEach(function (g, i) {
      if (i === potusGi || i === vpotusGi) return;
      if (Object.keys(pw).some(function (w) { return S.isWho(g, w); })) m[i] = ["P", INK, "must sit together", "must sit together"];
      else if (Object.keys(who).some(function (w) { return S.isWho(g, w); })) m[i] = ["R", INK, "rival", "rivals"];
      else if (cats[g.cat] && MARK[g.cat]) m[i] = MARK[g.cat];
      else if (judge.togCompany && g.org && cnt[g.org] > 1) m[i] = ["C", INK, "colleague", "colleagues (same company)"];
    });
    return m;
  }

  // ---------- state
  var st = { puzzle: null, saved: null, chat: null, rule: null, ruleSel: -1, intended: false, marks: null };
  var sea = null;

  function newPuzzle(lv) {
    var L = LEVELS[lv], s = solve(L.prog), r = rng((Math.random() * 1e9) | 0), seat = s.ai;
    var want = L.minScramble || 4; for (var t = 0; t < 120; t++) { seat = shuffleFree(s.ai, r); if (evalSeats(s.judge, s.groups, seat).total >= want) break; }
    return { lv: lv, judge: s.judge, groups: s.groups, ai: s.ai, seat: seat, moves: 0, t0: 0, secs: 0, done: false, gaveUp: false, over: false, pd: 0, fp0: 0, pick: -1, marks: markers(s.judge), ev: null };
  }
  function initSea() {
    var s = solve("limit government 1");
    sea = { judge: s.judge, groups: s.groups, ai: s.ai, mode: "scrambled", waveT0: 0, waveR: -1, waveMax: 0, cache: new Map() };
  }
  initSea();

  // a chatbot answer drawn as given: seats in order, empty chairs for anyone it left out, repeats dropped after the first
  function chatArrange(secs, judge) {
    var seatGuest = [], sec = [], bad = new Set(), placed = {};
    var isGov = real.map(function (g) { return g.cat === S.CID.government; });
    secs.forEach(function (ids, si) {
      var gov = 0; ids.forEach(function (i) { if (isGov[i]) gov++; });
      if (gov > 1 || ids.length > (judge ? judge.cap : 6)) bad.add(si);
      ids.forEach(function (i) { if (seatGuest.length < N && !placed[i]) { placed[i] = 1; seatGuest.push(i); sec.push(si); } });
    });
    while (seatGuest.length < N) { seatGuest.push(-1); sec.push(null); }
    return { seatGuest: seatGuest, sec: sec, bad: bad, broken: true };
  }
  function ruleArrange() {
    var R = st.rule, a = seatRule(R.exec), ev = evalSeats(R.judge, a.groups, a.seat);
    R.vA = ev.v; R.vP = ev.v;
    return { seatGuest: a.seat, sec: a.groups, bad: ev.bad };
  }
  function postedArrange() { var P = []; for (var k = 0; k < N; k++) P.push(S.walkGuest(k, N)); return { seatGuest: P, sec: null, bad: null }; }
  function mainArrange() {
    var z = st.puzzle;
    if (z) { z.ev = evalSeats(z.judge, z.groups, z.seat); return { seatGuest: z.seat.slice(), sec: z.groups, bad: z.ev.bad }; }
    if (st.chat) return chatArrange(st.chat, null);
    if (st.rule) return ruleArrange();
    return postedArrange();
  }

  // ---------- main table layout and animation
  var mainClashes = [], mainArr = null, cur = [], anim = null, tgtPos = [];
  function targetPos(arr) {
    var t = new Array(N);
    for (var k = 0; k < N; k++) { var gi = arr.seatGuest[k], s = seatXY(k); if (gi >= 0 && !t[gi]) t[gi] = { side: s.side, x: s.x, y: s.y, k: k }; }
    var j = 0; for (var g = 0; g < N; g++) if (!t[g]) { t[g] = { side: 0, x: 0, y: 402 + 22 * j, k: -1 }; j++; }
    return t;
  }
  function relayout(animate) {
    var prev = cur.length ? cur.map(function (p) { return { side: p.side, x: p.x, y: p.y }; }) : null;
    mainArr = mainArrange(); tgtPos = targetPos(mainArr);
    var jd = st.puzzle ? st.puzzle.judge : st.rule ? st.rule.judge : st.chat ? S.parse("limit government 1") : null; mainClashes = clashes(mainArr, jd);
    anim = animate && prev && !reduce ? { t0: performance.now(), dur: 480, from: prev, to: tgtPos } : null;
    cur = anim ? prev.map(function (p, i) { return { side: p.side, x: p.x, y: p.y, k: tgtPos[i].k }; }) : tgtPos.map(function (p) { return { side: p.side, x: p.x, y: p.y, k: p.k }; });
    dirty = true; live();
  }
  function stepAnim(now) {
    if (!anim) return false;
    var p = Math.min(1, (now - anim.t0) / anim.dur), e = p < .5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
    for (var gi = 0; gi < N; gi++) { var a = anim.from[gi], b = anim.to[gi]; cur[gi] = { side: p < .5 ? a.side : b.side, x: a.x + (b.x - a.x) * e, y: a.y + (b.y - a.y) * e, k: b.k }; }
    if (p >= 1) { anim = null; cur = tgtPos.map(function (q) { return { side: q.side, x: q.x, y: q.y, k: q.k }; }); }
    return true;
  }

  // ---------- camera
  var cv = document.getElementById("cv"), ctx = cv.getContext("2d"), stage = document.getElementById("stage");
  var W = 0, H = 0, dpr = 1, cam = { x: 0, y: -30, s: 0.5 }, dirty = true, camAnim = null, SMIN = 0.008, SMAX = 3;
  function resize() { dpr = Math.min(window.devicePixelRatio || 1, 2); var r = stage.getBoundingClientRect(); W = r.width; H = r.height; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); dirty = true; }
  function fitScale() { return W < 600 ? (W - 8) / 700 : Math.min((W - 24) / 780, (H - 16) / 1040); }
  function goTo(x, y, s, instant) {
    s = Math.max(SMIN, Math.min(SMAX, s));
    if (instant || reduce) { cam.x = x; cam.y = y; cam.s = s; camAnim = null; dirty = true; }
    else camAnim = { t0: performance.now(), dur: 900, a: { x: cam.x, y: cam.y, ls: Math.log(cam.s) }, b: { x: x, y: y, ls: Math.log(s) } };
  }
  function fit() {
    if (document.body.classList.contains("card")) return;
    var capE = document.getElementById("cap"), side = W >= 900 && capE ? capE.offsetWidth : 0;
    var ch = side ? 0 : (capE ? capE.offsetHeight + 16 : 0), top = 12, avail = Math.max(120, H - ch - top), aw = W - side;
    var l = -390, r = 390;
    if (bubblesOn()) BUBBLES.forEach(function (b) { var p = tgtPos[real.findIndex(function (g) { return g.name === b.who; })]; if (p && p.side > 0) r = 720; else if (p && p.side < 0) l = -720; });
    var s = W < 600 ? (W - 8) / 700 : Math.min((aw - 32) / (r - l), avail / 1060);
    // the chart sits in the space the caption leaves: the right-hand side on desktop, above the card on phones
    goTo((l + r) / 2 - (side / 2) / s, -40 + (ch - top) / 2 / s, s);
  }
  function toWorld(cx, cy) { var r = stage.getBoundingClientRect(); return { x: cam.x + (cx - r.left - W / 2) / cam.s, y: cam.y + (cy - r.top - H / 2) / cam.s }; }

  // ---------- drawing
  function rr(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
  // the posted chart's chair icon: a light D-shaped seat, a backrest line and two small arm tabs on the table side, mirrored per side
  function chair(x, side, y, hi, detail) {
    ctx.strokeStyle = INK;
    if (!detail) { ctx.fillStyle = hi ? INK : "#fff"; ctx.lineWidth = 1.6; ctx.fillRect(x - 8, y - 10, 16, 20); ctx.strokeRect(x - 8, y - 10, 16, 20); return; }
    ctx.save(); ctx.translate(x, y); ctx.scale(side, 1);
    ctx.lineWidth = 1.15; ctx.fillStyle = hi ? INK : "#fff";
    ctx.beginPath(); ctx.moveTo(-6, -10); ctx.lineTo(2, -10); ctx.arcTo(9, -10, 9, -3, 6); ctx.lineTo(9, 3); ctx.arcTo(9, 10, 2, 10, 6); ctx.lineTo(-6, 10); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-2.5, -8); ctx.lineTo(-2.5, 8); ctx.stroke();
    ctx.fillStyle = "#fff"; ctx.fillRect(-9.5, -12, 5, 4); ctx.strokeRect(-9.5, -12, 5, 4); ctx.fillRect(-9.5, 8, 5, 4); ctx.strokeRect(-9.5, 8, 5, 4);
    ctx.restore();
  }


  var hatch = null;
  function hatchPattern() {
    if (hatch) return hatch;
    var c = document.createElement("canvas"); c.width = c.height = 10; var x = c.getContext("2d");
    x.strokeStyle = "rgba(21,21,21,.42)"; x.lineWidth = 1.4; x.beginPath(); x.moveTo(-2, 12); x.lineTo(12, -2); x.moveTo(8, 12); x.lineTo(12, 8); x.moveTo(-2, 2); x.lineTo(2, -2); x.stroke();
    hatch = ctx.createPattern(c, "repeat"); return hatch;
  }
  function strips(arr, lod) {
    var k = 0;
    while (k < N) {
      if (arr.sec[k] === null || arr.sec[k] === undefined) { k++; continue; }
      var s0 = seatXY(k), sec = arr.sec[k], m = k;
      while (m + 1 < N && arr.sec[m + 1] === sec && seatXY(m + 1).side === s0.side) m++;
      var a = seatXY(k), b = seatXY(m), top = Math.min(a.y, b.y) - 21.5, bot = Math.max(a.y, b.y) + 21.5, x0 = s0.side < 0 ? -332 : 64, w = 268;
      ctx.strokeStyle = "#d8d6cf"; ctx.lineWidth = 1; rr(x0, top + 1, w, bot - top - 2, 6); ctx.stroke();
      k = m + 1;
    }
  }
  // who clashes with whom: two people in one section who break a rule together, or two who must sit together but don't
  function clashes(arr, judge) {
    if (!arr || !arr.sec || !judge) return [];
    var kOf = {}, bySec = {}, out = [];
    for (var k = 0; k < N; k++) { var gi = arr.seatGuest[k], sc = arr.sec[k]; if (gi < 0 || sc === null || sc === undefined) continue; kOf[gi] = k; (bySec[sc] = bySec[sc] || []).push(gi); }
    var yOf = function (gi) { return seatXY(kOf[gi]).y; };
    var nearest = function (a, B) { var best = B[0]; B.forEach(function (b) { if (Math.abs(yOf(b) - yOf(a)) < Math.abs(yOf(best) - yOf(a))) best = b; }); return best; };
    Object.keys(bySec).forEach(function (sc) {
      var m = bySec[sc].slice().sort(function (a, b) { return kOf[a] - kOf[b]; });
      judge.limits.forEach(function (l) { var hit = m.filter(function (gi) { return l[0].indexOf(real[gi].cat) >= 0; }); if (hit.length > l[1]) for (var i = 1; i < hit.length; i++) out.push({ a: hit[i - 1], b: hit[i], kind: "same", g: "s" + sc }); });
      judge.aparts.forEach(function (ap) { var A = m.filter(function (g) { return real[g].cat === ap[0]; }), B = m.filter(function (g) { return real[g].cat === ap[1]; }); if (B.length) A.forEach(function (a) { out.push({ a: a, b: nearest(a, B), kind: "same", g: "s" + sc }); }); });
      (judge.avoids || []).forEach(function (av) { m.forEach(function (a) { if (!S.isWho(real[a], av[0])) return; m.forEach(function (b) { if (a !== b && S.isWho(real[b], av[1])) out.push({ a: a, b: b, kind: "same", g: "s" + sc }); }); }); });
    });
    var placed = Object.keys(kOf).map(Number);
    (judge.pairs || []).forEach(function (pr, pi) { placed.forEach(function (a) { if (!S.isWho(real[a], pr[0])) return; placed.forEach(function (b) { if (a !== b && S.isWho(real[b], pr[1]) && arr.sec[kOf[a]] !== arr.sec[kOf[b]]) out.push({ a: a, b: b, kind: "split", g: "p" + pi }); }); }); });
    // a group that must sit together only clashes when it is split more ways than the section size forces
    var units = {}, tk = {}; (judge.togCats || []).forEach(function (c) { tk[c] = 1; });
    placed.forEach(function (gi) { var g = real[gi], key = tk[g.cat] ? "c" + g.cat : (judge.togCompany && g.org ? "o" + g.org : null); if (key) (units[key] = units[key] || []).push(gi); });
    Object.keys(units).forEach(function (key) {
      var g = units[key].sort(function (a, b) { return kOf[a] - kOf[b]; }), mf = judge.cap;
      judge.limits.forEach(function (l) { if (l[0].indexOf(real[g[0]].cat) >= 0) mf = Math.min(mf, l[1]); });
      var sp = {}; g.forEach(function (gi) { sp[arr.sec[kOf[gi]]] = 1; });
      if (Object.keys(sp).length <= Math.ceil(g.length / mf)) return;
      for (var i = 1; i < g.length; i++) if (arr.sec[kOf[g[i]]] !== arr.sec[kOf[g[i - 1]]]) out.push({ a: g[i - 1], b: g[i], kind: "split", g: "u" + key });
    });
    out.kOf = kOf; return out;
  }
  // one red comb per clash: a line in the margin with a tick at each person involved (dashed when they should be together but aren't)
  function drawClashes(list) {
    if (!list || !list.length) return;
    var groups = {}, order = [];
    list.forEach(function (c) { var G = groups[c.g]; if (!G) { G = groups[c.g] = { kind: c.kind, who: {} }; order.push(G); } G.who[c.a] = 1; G.who[c.b] = 1; });
    var lanes = { "-1": [], "1": [] }, under = 0;
    var lane = function (side, top, bot) { var L = lanes[side], i = 0; while (L[i] !== undefined && L[i] > top - 6) i++; L[i] = bot; return side * (344 + i * 8); };
    order.map(function (G) {
      var ys = { "-1": [], "1": [] }; Object.keys(G.who).forEach(function (gi) { var s = seatXY(list.kOf[gi]); ys[s.side].push(s.y); });
      return { G: G, ys: ys, top: Math.min.apply(null, ys["-1"].concat(ys["1"])) };
    }).sort(function (p, q) { return p.top - q.top; }).forEach(function (it) {
      var both = it.ys["-1"].length && it.ys["1"].length, yb = both ? Math.max.apply(null, it.ys["-1"].concat(it.ys["1"])) + 30 + 8 * under++ : 0, xs = {};
      ctx.strokeStyle = RED; ctx.lineWidth = 2.2; ctx.setLineDash(it.G.kind === "split" ? [5, 5] : []);
      ["-1", "1"].forEach(function (sd) {
        var Y = it.ys[sd]; if (!Y.length) return;
        var t = Math.min.apply(null, Y), bt = both ? yb : Math.max.apply(null, Y), x = xs[sd] = lane(sd, t, bt), tick = -Number(sd) * 10;
        ctx.beginPath(); ctx.moveTo(x, t); ctx.lineTo(x, bt); Y.forEach(function (y) { ctx.moveTo(x, y); ctx.lineTo(x + tick, y); }); ctx.stroke();
      });
      if (both) { ctx.beginPath(); ctx.moveTo(xs["-1"], yb); ctx.lineTo(xs["1"], yb); ctx.stroke(); }
    });
    ctx.setLineDash([]);
  }
  function mark(mk, x, y) {
    ctx.fillStyle = mk[1]; ctx.beginPath(); ctx.arc(x, y, 9, 0, 6.2832); ctx.fill();
    ctx.fillStyle = "#fff"; ctx.font = "600 11px " + TEXT; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(mk[0], x, y + 0.5);
  }
  function nameAt(label, x, y, side, mk, color) {
    ctx.font = "italic 13.5px " + FONT; ctx.fillStyle = color || INK; ctx.textBaseline = "middle"; ctx.textAlign = side < 0 ? "right" : "left";
    var tw = ctx.measureText(label).width; if (tw > 222) { ctx.font = "italic " + (13.5 * 222 / tw).toFixed(2) + "px " + FONT; tw = 222; }
    ctx.fillText(label, x, y);
    if (mk) { mark(mk, side < 0 ? x - tw - 13 : x + tw + 13, y); }
  }
  function header() {
    ctx.fillStyle = MUTE; ctx.font = "italic 15px " + FONT; ctx.textAlign = "left"; ctx.textBaseline = "middle";
    ctx.fillText("Super Intelligence Luncheon", -372, -518); ctx.fillText("Tuesday, September 29, 2026", -372, -498);
    ctx.fillStyle = INK; ctx.font = "700 20px " + FONT; ctx.textAlign = "center"; ctx.fillText("Seating Chart \u00b7 East Room", 0, -492);
  }
  function frame(color, lw) { ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.strokeRect(-345, -472, 690, 944); }
  function tableShape(lod) { ctx.fillStyle = lod >= 1 ? TABLE : "#bdbbb5"; ctx.strokeStyle = INK; ctx.lineWidth = 2.5; if (lod >= 1) { rr(-62, -370, 124, 740, 26); ctx.fill(); ctx.stroke(); } else ctx.fillRect(-62, -370, 124, 740); }

  var BUBBLES = [
    { who: "Mark Zuckerberg", text: "Send Me Location", src: "Zuckerberg on Instagram, June 2023", dy: 0 },
    { who: "Elon Musk", text: "I’m up for a cage match if he is", src: "Musk on Twitter, June 2023", dy: 0 }];
  function bubblesOn() { var z = st.puzzle; if (document.body.classList.contains("card")) return true; return W >= 600 && ((mode === "story" && (chap === 0 || (chap === 1 && z && z.moves === 0))) || (mode === "play" && z && z.lv === 1 && z.moves === 0)); }
  function drawBubbles() {
    var list = BUBBLES;
    if (document.body.classList.contains("card")) {
      var ym = cur[real.findIndex(function (g) { return g.name === "Elon Musk"; })].y, yz = cur[real.findIndex(function (g) { return g.name === "Mark Zuckerberg"; })].y, up = ym < yz ? -26 : 26;
      list = [{ who: "Elon Musk", text: "I\u2019m up for a cage match if he is", src: "Musk on Twitter, June 2023", dy: up }, { who: "Mark Zuckerberg", text: "Send Me Location", src: "Zuckerberg on Instagram, June 2023", dy: -up }];
    }
    list.forEach(function (b) {
      var gi = real.findIndex(function (g) { return g.name === b.who; }), p = cur[gi]; if (!p || p.side === 0) return;
      ctx.font = "italic 16px " + FONT; var w1 = ctx.measureText("\u201c" + b.text + "\u201d").width; ctx.font = "12px " + TEXT; var tw = Math.max(w1, ctx.measureText(b.src).width) + 28;
      var y = p.y + b.dy, x0 = p.side > 0 ? 380 : -380 - tw, h = 46, ty = Math.max(y - h / 2 + 8, Math.min(y + h / 2 - 8, p.y));
      ctx.fillStyle = "#fff"; ctx.strokeStyle = INK; ctx.lineWidth = 1.6;
      rr(x0, y - h / 2, tw, h, 12); ctx.fill(); ctx.stroke();
      var ex = p.side > 0 ? x0 : x0 + tw, tip = p.side * (st.puzzle ? 360 : 350);
      ctx.beginPath(); ctx.moveTo(ex, ty - 7); ctx.lineTo(tip, p.y); ctx.lineTo(ex, ty + 7); ctx.fillStyle = "#fff"; ctx.fill();
      ctx.beginPath(); ctx.moveTo(ex, ty - 7); ctx.lineTo(tip, p.y); ctx.lineTo(ex, ty + 7); ctx.stroke();
      ctx.fillStyle = "#fff"; ctx.fillRect(ex - 1, ty - 6, 2, 12);
      ctx.textAlign = "left"; ctx.textBaseline = "middle";
      ctx.fillStyle = INK; ctx.font = "italic 16px " + FONT; ctx.fillText("“" + b.text + "”", x0 + 13, y - 8);
      ctx.fillStyle = MUTE; ctx.font = "12px " + TEXT; ctx.fillText(b.src, x0 + 13, y + 12);
    });
  }
  var drag = null;
  function drawMain(lod) {
    var asPosted = !st.puzzle && !st.chat && !st.rule;
    if (asPosted || lod < 1) {
      frame("#000", Math.max(9, 2.2 / cam.s));
      [100, 138, 565, 688, 725, 883].forEach(function (yy) { var y = -472 + (yy - 62) / 945 * 944; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(-372, y); ctx.lineTo(-318, y); ctx.stroke(); });
    }
    if (lod >= 1) header();
    else { ctx.fillStyle = INK; ctx.font = "600 " + (18 / cam.s) + "px " + FONT; ctx.textAlign = "center"; ctx.textBaseline = "bottom"; ctx.fillText("The real lunch", 0, -472 - 10 / cam.s); }
    if (mainArr.sec && lod >= 1) strips(mainArr, lod);
    tableShape(lod);
    if (lod < 1) return;
    var z = st.puzzle, marks = z ? z.marks : st.marks, hiK = cur[potusGi] ? cur[potusGi].k : -1;
    for (var k = 0; k < N; k++) { var s = seatXY(k); chair(s.side * 79, s.side, s.y, k === hiK, lod >= 2); }
    if (z && z.pick >= 0) { var ps = seatXY(z.pick); ctx.strokeStyle = BLUE; ctx.lineWidth = 3.5; rr(ps.side < 0 ? -334 : 62, ps.y - 20, 272, 40, 8); ctx.stroke(); }
    if (drag && drag.active && drag.hover >= 0 && drag.hover !== drag.k) { var hs = seatXY(drag.hover); ctx.strokeStyle = BLUE; ctx.lineWidth = 3.5; ctx.setLineDash([8, 6]); rr(hs.side < 0 ? -334 : 62, hs.y - 20, 272, 40, 8); ctx.stroke(); ctx.setLineDash([]); }
    if (lod >= 1 && bubblesOn()) drawBubbles();
    var red = {}; (mainClashes || []).forEach(function (c) { red[c.a] = 1; red[c.b] = 1; });
    if (lod >= 1) drawClashes(mainClashes);
    if (lod < 2 && !z) return;
    for (var gi = 0; gi < N; gi++) {
      if (drag && drag.active && drag.gi === gi) continue;
      var p = cur[gi];
      if (p.side === 0) { ctx.font = "italic 15px " + FONT; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillStyle = MUTE; ctx.fillText(real[gi].label + " — no seat", p.x, p.y); continue; }
      nameAt(real[gi].label, p.x, p.y, p.side, marks && marks[gi], red[gi] ? RED : null);
    }
    if (drag && drag.active) {
      var lab = real[drag.gi].label; ctx.font = "italic 16px " + FONT; var tw = ctx.measureText(lab).width + 40;
      ctx.save(); ctx.shadowColor = "rgba(0,0,0,.28)"; ctx.shadowBlur = 14; ctx.shadowOffsetY = 4; ctx.fillStyle = "#fff";
      rr(drag.wx - tw / 2, drag.wy - 18, tw, 36, 18); ctx.fill(); ctx.restore();
      ctx.strokeStyle = BLUE; ctx.lineWidth = 2; rr(drag.wx - tw / 2, drag.wy - 18, tw, 36, 18); ctx.stroke();
      ctx.font = "italic 16px " + FONT; ctx.fillStyle = INK; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(lab, drag.wx + 8, drag.wy);
      var mk = z && z.marks[drag.gi]; if (mk) mark(mk, drag.wx - tw / 2 + 16, drag.wy);
    }
  }

  // ---------- endless lunches: copies of this lunch, each scrambled differently
  var budgetEnd = 0, fixedArr = null;
  function copyScramble(i, j) {
    var key = i + "," + j, c = sea.cache.get(key);
    if (c) return c;
    if (performance.now() > budgetEnd) return null;
    if (sea.cache.size > 60000) sea.cache.clear();
    var seat = shuffleFree(sea.ai, rng((Math.imul(i, 73856093) ^ Math.imul(j, 19349663) ^ 0x5bd1e995) >>> 0));
    var ev = evalSeats(sea.judge, sea.groups, seat);
    c = { seatGuest: seat, sec: sea.groups, bad: ev.bad, broken: ev.total > 0 }; sea.cache.set(key, c);
    return c;
  }
  function copyArr(i, j) {
    var d = Math.hypot(i, j * PY / PX);
    if (sea.mode !== "scrambled" && d <= sea.waveR) {
      if (sea.mode === "fixed") {
        // each timeline's host words the rule their own way: one of the tiny AI's 360 real readings decides its fate
        var rd = reading(i, j);
        if (!rd.ok) return copyScramble(i, j);
        if (!fixedArr) fixedArr = { seatGuest: sea.ai, sec: sea.groups, bad: new Set(), broken: false }; return fixedArr;
      }
      var idx = ((Math.imul(i, 2654435761) ^ Math.imul(j, 40503)) >>> 0) % C.answers.length;
      return chatArrange(C.answers[idx], sea.judge);
    }
    return copyScramble(i, j);
  }
  var RD = DATA.readings, RDN = RD.passed.length * 5;
  function reading(i, j) { var r = ((Math.imul(i, 374761393) ^ Math.imul(j, 668265263)) >>> 0) % RDN, p = Math.floor(r / 5); return { text: RD.texts[p], ok: !!RD.passed[p][r % 5] }; }
  function drawCopy(i, j, lod) {
    var a = copyArr(i, j);
    ctx.save(); ctx.translate(i * PX, j * PY);
    frame(a ? (a.broken ? RED : "#a9a8a3") : "#dcdbd6", a && a.broken ? (lod >= 2 ? 6 : Math.max(6, 2.2 / cam.s)) : (lod >= 2 ? 3 : Math.max(3, 1 / cam.s)));
    if (a && lod >= 1) strips(a, lod);
    tableShape(lod);
    if (lod >= 1 && sea.mode === "fixed" && Math.hypot(i, j * PY / PX) <= sea.waveR) {
      var rd = reading(i, j), txt = "\u201c" + rd.text + "\u201d";
      ctx.font = "italic 22px " + FONT; ctx.fillStyle = rd.ok ? MUTE : RED; ctx.textAlign = "center"; ctx.textBaseline = "bottom";
      while (ctx.measureText(txt).width > 700 && txt.length > 20) txt = txt.slice(0, -3).replace(/\s+\S*$/, "") + "\u2026\u201d";
      ctx.fillText(txt, 0, -482);
    }
    if (a && lod >= 1) {
      for (var k = 0; k < N; k++) { var s = seatXY(k); if (lod >= 2 || a.seatGuest[k] >= 0) chair(s.side * 79, s.side, s.y, a.seatGuest[k] === potusGi, lod >= 2); }
      if (lod >= 2) { for (var k2 = 0; k2 < N; k2++) { var gi = a.seatGuest[k2]; if (gi < 0) continue; var s2 = seatXY(k2); nameAt(real[gi].label, s2.x, s2.y, s2.side, null); } }
    }
    ctx.restore();
  }
  function visibleRange() {
    var x0 = cam.x - W / 2 / cam.s, x1 = cam.x + W / 2 / cam.s, y0 = cam.y - H / 2 / cam.s, y1 = cam.y + H / 2 / cam.s;
    return { i0: Math.floor((x0 - 400) / PX), i1: Math.ceil((x1 + 400) / PX), j0: Math.floor((y0 - 560) / PY), j1: Math.ceil((y1 + 560) / PY) };
  }
  function seaStats() {
    var R = visibleRange(), n = 0, broken = 0, known = 0;
    for (var i = R.i0; i <= R.i1; i++) for (var j = R.j0; j <= R.j1; j++) {
      if (i === 0 && j === 0) continue;
      var a = copyArr(i, j); n++; if (a) { known++; if (a.broken) broken++; }
    }
    return { n: n, broken: broken, known: known };
  }
  function showCopies() { return (mode === "story" && chap >= 4) || cam.s < 0.2; }
  function render(now) {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, cv.width, cv.height);
    var s = cam.s; ctx.setTransform(dpr * s, 0, 0, dpr * s, dpr * (W / 2 - cam.x * s), dpr * (H / 2 - cam.y * s));
    var lod = s >= 0.3 ? 2 : s >= 0.06 ? 1 : 0, R = visibleRange(), pending = false;
    budgetEnd = now + 10;
    for (var i = R.i0; i <= R.i1; i++) for (var j = R.j0; j <= R.j1; j++) {
      if (i === 0 && j === 0) continue;
      if (!showCopies()) continue;
      drawCopy(i, j, lod); if (sea.mode === "scrambled" && !sea.cache.has(i + "," + j)) pending = true;
    }
    ctx.save(); drawMain(lod); ctx.restore();
    if (pending) dirty = true;
  }

  // ---------- puzzle actions
  function startPuzzle(lv) { overEl.hidden = true; st.chat = null; st.rule = null; st.marks = null; st.puzzle = newPuzzle(lv); lastInc = ""; relayout(true); paint(); fit(); }
  function swapSeats(a, b, fromDrag) {
    var z = st.puzzle; if (!z || z.done || a === b || isHostSeat(a) || isHostSeat(b)) return;
    if (z.over) return;
    if (!z.t0) z.t0 = performance.now();
    var ga = z.seat[a], gb = z.seat[b]; z.seat[a] = gb; z.seat[b] = ga; z.moves++; z.pick = -1;
    var dropX = fromDrag ? drag.wx : 0, dropY = fromDrag ? drag.wy : 0;
    relayout(true); afterMove(); if (!z.done) stepDoom(z);
    if (fromDrag && anim) { anim.from[ga] = { side: seatXY(b).side, x: dropX, y: dropY }; cur[ga] = { side: seatXY(b).side, x: dropX, y: dropY, k: b }; }
    if (z.ev.total === 0) { z.done = true; z.pd = 0; overEl.hidden = true; z.secs = (performance.now() - z.t0) / 1000; toast("p(doom) = 0. Apocalypse averted in " + z.moves + " swap" + (z.moves === 1 ? "" : "s") + "."); paint(); }
  }
  function letAI() { var z = st.puzzle; if (!z) return; z.seat = z.ai.slice(); z.pick = -1; z.done = true; z.gaveUp = true; z.over = false; overEl.hidden = true; relayout(true); paint(); }
  // p(doom): starts high on a scrambled table, climbs when a swap makes things worse, falls when it helps; 1.00 is game over
  var overEl = document.getElementById("over");
  function flashpoints(z) { var arr = { seatGuest: z.seat, sec: z.groups }; return clashes(arr, z.judge).length; }
  function rivalsTogether(z) { return incidents(z).filter(function (t) { return t.indexOf("Musk") === 0; }).length; }
  function startDoom(z) { z.fp0 = flashpoints(z); z.riv0 = rivalsTogether(z); z.pd = Math.min(0.72, 0.22 + 0.08 * z.fp0 + 0.05 * z.riv0); }
  function stepDoom(z) {
    var before = z.pd, fp = flashpoints(z), riv = rivalsTogether(z), d = fp - z.fp0, dr = riv - z.riv0;
    if (fp === 0) z.pd = 0;
    else z.pd = Math.max(0.01, Math.min(1, z.pd + (d > 0 ? 0.14 * d : d < 0 ? 0.1 * d : 0.025) + (dr > 0 ? 0.12 * dr : 0)));
    z.fp0 = fp; z.riv0 = riv;
    if (Math.abs(z.pd - before) > 0.004) pulse(z.pd - before, d > 0 || dr > 0);
    if (z.pd >= 1) gameOver();
  }
  var pulseT = 0, flashCls = "", deltaTxt = "";
  function pulse(delta, clash) {
    flashCls = delta > 0 && clash ? " up" : delta < 0 ? " down" : " tick";
    deltaTxt = (delta > 0 ? "+" : "\u2212") + Math.abs(delta).toFixed(2);
    var cc = document.getElementById("capclock"); hud.className = "hud"; if (cc) cc.className = "capclock"; void hud.offsetWidth;   // restart the animation
    clearTimeout(pulseT); pulseT = setTimeout(function () { flashCls = ""; deltaTxt = ""; live(); }, 1200);
    live();
  }
  function gameOver() {
    var z = st.puzzle; z.over = true; z.pd = 1; z.pick = -1; drag = null;
    overEl.hidden = false; paint(); dirty = true;
  }
  document.getElementById("retry").onclick = function () { overEl.hidden = true; startPuzzle(st.puzzle ? st.puzzle.lv : 1); };
  document.getElementById("showai").onclick = letAI;
  var toastT = 0;
  function toast(msg) { var t = document.getElementById("toast"); t.textContent = msg; t.classList.add("on"); clearTimeout(toastT); if (!document.body.classList.contains("card")) toastT = setTimeout(function () { t.classList.remove("on"); }, 2200); }

  // ---------- endless lunches actions
  function wave(m) {
    sea.mode = m; sea.waveT0 = performance.now(); sea.waveR = 0;
    var R = visibleRange(); sea.waveMax = Math.max(Math.abs(R.i0), Math.abs(R.i1), Math.abs(R.j0 * PY / PX), Math.abs(R.j1 * PY / PX)) + 2;
    if (reduce) sea.waveR = Infinity;
    dirty = true; paint();
  }
  function stepWave(now) {
    if (sea.mode === "scrambled" || sea.waveR === Infinity) return false;
    var p = Math.min(1, (now - sea.waveT0) / 3200); sea.waveR = sea.waveMax * p * p;
    if (p >= 1) { sea.waveR = Infinity; }
    return true;
  }
  function resetSea() { sea.mode = "scrambled"; sea.waveR = -1; dirty = true; }

  // ---------- pointer: drag people, tap to swap, pan, zoom
  var ptrs = new Map(), pinch0 = null;
  stage.addEventListener("pointerdown", function (e) {
    if (e.target.closest(".nav, #cap, .hud, .credit, .over, #sheet, .toast")) return;
    try { stage.setPointerCapture(e.pointerId); } catch (err) {} ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY }); camAnim = null;
    var z = st.puzzle;
    if (ptrs.size === 1 && z && !z.done && !z.over && cam.s >= 0.12) {
      var w = toWorld(e.clientX, e.clientY), k = hitSeat(w.x, w.y);
      if (k >= 0 && z.seat[k] >= 0 && !isHostSeat(k)) { drag = { k: k, gi: z.seat[k], wx: w.x, wy: w.y, active: false, hover: -1, sx: e.clientX, sy: e.clientY }; return; }
    }
    stage.classList.add("drag");
    if (ptrs.size === 2) { drag = null; var a = Array.from(ptrs.values()); pinch0 = { d: Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y), s: cam.s }; }
  });
  stage.addEventListener("pointermove", function (e) {
    if (!ptrs.has(e.pointerId)) {
      var z = st.puzzle;
      if (z && !z.done && !z.over && cam.s >= 0.12) { var w0 = toWorld(e.clientX, e.clientY); stage.classList.toggle("can-pick", hitSeat(w0.x, w0.y) >= 0); }
      return;
    }
    var p = ptrs.get(e.pointerId), dx = e.clientX - p.x, dy = e.clientY - p.y; p.x = e.clientX; p.y = e.clientY;
    if (drag) {
      if (!drag.active && Math.hypot(e.clientX - drag.sx, e.clientY - drag.sy) > 5) { drag.active = true; st.puzzle.pick = -1; }
      if (drag.active) { var w = toWorld(e.clientX, e.clientY); drag.wx = w.x; drag.wy = w.y; drag.hover = hitSeat(w.x, w.y); if (isHostSeat(drag.hover)) drag.hover = -1; dirty = true; }
      return;
    }
    if (ptrs.size === 1) { cam.x -= dx / cam.s; cam.y -= dy / cam.s; dirty = true; }
    else if (ptrs.size === 2 && pinch0) {
      var a = Array.from(ptrs.values()), d = Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y);
      zoomAt((a[0].x + a[1].x) / 2, (a[0].y + a[1].y) / 2, pinch0.s * d / pinch0.d);
    }
  });
  function endPtr(e) {
    ptrs.delete(e.pointerId); pinch0 = null;
    if (drag) {
      var d = drag, z = st.puzzle;
      if (d.active) { if (d.hover >= 0 && d.hover !== d.k) swapSeats(d.k, d.hover, true); drag = null; dirty = true; }
      else if (e.type === "pointerup" && z) {
        drag = null;
        if (z.pick < 0) z.pick = d.k; else if (z.pick === d.k) z.pick = -1; else swapSeats(z.pick, d.k, false);
        dirty = true;
      } else drag = null;
    }
    if (!ptrs.size) stage.classList.remove("drag");
  }
  stage.addEventListener("pointerup", endPtr); stage.addEventListener("pointercancel", endPtr);
  function zoomAt(px, py, ns) {
    ns = Math.max(SMIN, Math.min(SMAX, ns)); var w = toWorld(px, py), r = stage.getBoundingClientRect();
    cam.s = ns; cam.x = w.x - (px - r.left - W / 2) / ns; cam.y = w.y - (py - r.top - H / 2) / ns; dirty = true;
  }
  stage.addEventListener("wheel", function (e) { if (e.target.closest("#cap, .over, #sheet")) return; e.preventDefault(); camAnim = null; zoomAt(e.clientX, e.clientY, cam.s * Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0015))); }, { passive: false });
  document.getElementById("fit").addEventListener("click", fit);
  document.getElementById("far").addEventListener("click", function () { goTo(0, 0, 0.02); });

  // ---------- caption strip, frame HUD and the "How it works" sheet
  var capEl = document.getElementById("cap"), hud = document.getElementById("hud"), sheet = document.getElementById("sheet"), mode = "story", chap = 0;
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function stash() { if (overEl) overEl.hidden = true; if (st.puzzle) st.saved = st.puzzle; st.puzzle = null; st.chat = null; st.rule = null; st.marks = null; }
  function setRule(prog, judge) { st.rule = { exec: S.parse(prog), judge: S.parse(judge || prog) }; }
  function dot(c, l) { return '<span class="dot" style="background:' + c + '">' + l + "</span>"; }
  function keyLine(z) {
    var has = {}; Object.keys(z.marks).forEach(function (i) { has[z.marks[i][0]] = z.marks[i]; });
    var parts = [];
    if (has.G) parts.push(dot(has.G[1], "G") + "officials");
    if (has.R) parts.push(dot(has.R[1], "R") + "keep apart");
    if (has.P) parts.push(dot(has.P[1], "P") + "keep together");
    if (has.A) parts.push(dot(has.A[1], "A") + "AI labs");
    if (has.T) parts.push(dot(has.T[1], "T") + "big tech");
    if (has.C) parts.push(dot(has.C[1], "C") + "colleagues");
    return parts.join(" ");
  }
  var lastInc = "", lastMins = -1;
  function live() {
    var z = st.puzzle, showHud = !!(z && z.ev), cc = document.getElementById("capclock");
    hud.hidden = !showHud;
    if (showHud) {
      if (z.pd === 0 && !z.done && z.ev && flashpoints(z) > 0 && !z.moves) startDoom(z);
      var fp = flashpoints(z), pd = z.done ? 0 : z.over ? 1 : z.pd;
      document.getElementById("doomt").textContent = "p(doom) " + (pd === 1 ? "1.00" : pd.toFixed(2));
      document.getElementById("doombar").style.width = Math.round(pd * 100) + "%";
      document.getElementById("hudred").textContent = z.done ? (z.gaveUp ? "The program saved this one" : "You saved this timeline") : z.over ? "Game over" : fp + (fp === 1 ? " clash" : " clashes") + " at the table";
      var cls = (z.done ? " ok" : pd >= 0.75 ? " late" : "") + (z.done || z.over ? "" : flashCls);
      hud.className = "hud" + cls; document.getElementById("hudd").textContent = z.done || z.over ? "" : deltaTxt;
      if (cc) { cc.className = "capclock" + cls; cc.innerHTML = "<b>" + document.getElementById("doomt").textContent + "</b>" + (deltaTxt && !z.done && !z.over ? '<span class="delta">' + deltaTxt + "</span>" : "") + " " + document.getElementById("hudred").textContent; }
    }
    var ss = document.getElementById("seastat");
    if (ss) { var q = seaStats(); ss.textContent = q.n.toLocaleString("en-US") + " lunches on screen, " + q.broken.toLocaleString("en-US") + " breaking the rule" + (q.known < q.n ? " (counting)" : "") + "."; }
  }
  function afterMove() {
    var z = st.puzzle; if (!z || z.done) return;
    var inc = incidents(z), fresh = inc.filter(function (t) { return lastInc.indexOf(t) < 0; });
    if (fresh.length) toast(fresh[0]);
    lastInc = inc.join("|");
  }
  // wry consequences, one per kind of broken rule (the rivalries are public record; the rest is a joke)
  function incidents(z) {
    var assign = new Array(N), out = [];
    for (var k = 0; k < N; k++) if (z.seat[k] >= 0) assign[z.seat[k]] = z.groups[k];
    function share(a, b) { for (var i = 0; i < N; i++) for (var j = 0; j < N; j++) if (i !== j && S.isWho(real[i], a) && S.isWho(real[j], b) && assign[i] === assign[j]) return true; return false; }
    (z.judge.avoids || []).forEach(function (a) {
      if (!share(a[0], a[1])) return;
      if (a[1] === "Mark_Zuckerberg") out.push("Musk and Zuckerberg share a section. Someone has mentioned the Octagon.");
      else if (a[1] === "OpenAI") out.push("Musk and OpenAI share a section. The lawyers have been notified.");
      else if (a[1] === "Jeff_Bezos") out.push("Musk and Bezos share a section. Someone has brought up rockets.");
      else if (a[0] === "Google") out.push("Google is sitting with " + a[1].replace(/_/g, " ") + ". Awkward.");
      else out.push(a[0].replace(/_/g, " ") + " and " + a[1].replace(/_/g, " ") + " share a section. Tension rising.");
    });
    var splitPair = {}; (z.judge.pairs || []).forEach(function (a) { if (!share(a[0], a[1])) splitPair[a[0] + "|" + a[1]] = 1; });
    if (splitPair["David_Sacks|Chamath_Palihapitiya"]) out.push("Sacks and Palihapitiya are in different sections. This week\u2019s episode is cancelled.");
    if (splitPair["Greg_Brockman|Dario_Amodei"] || splitPair["Greg_Brockman|Tom_Brown"]) out.push("The reunion is off. Somebody has to sit next to a stranger.");
    if (splitPair["Microsoft|OpenAI"]) out.push("Microsoft and OpenAI are sitting apart. It\u2019s complicated.");
    if (z.ev.v.limit) out.push("Two officials in one section. A subcommittee has formed.");
    if (z.ev.v.apart) out.push("AI labs and big tech share a section. Someone is talking about compute.");
    if (z.ev.v.together) out.push("Colleagues split up. Nobody knows who has the slides.");
    return out;
  }

  var CH = [
    { go: function () { st.puzzle = null; st.saved = null; st.chat = null; st.rule = null; st.marks = null; resetSea(); relayout(true); fit(); if (W < 600) quoteToasts(); },
      cap: function () {
        return "<h1>I trained a tiny model to stop AI leaders from causing the apocalypse.</h1><p class=\"lede\">It does this by fixing the seating chart.</p><p>This is the real seating chart from the White House lunch with AI leaders on 29 September 2026. Every seating plan has rules, and this room comes with some history: a few of these guests have been arguing in public for years.</p>" +
          "<p>Seat these people badly and it’s game over: p(doom) goes to 1, and the AI apocalypse starts somewhere between the soup and the main course. Most versions of this lunch end that way. Your job is to find the one that doesn’t, and then we’ll see whether a small chatbot or our tiny AI can do the same.</p>" +
          '';
      }, foot: 'A game. The quotes are real public posts; the rest is made up. Not affiliated with anyone at the table. Quotes: <a href="https://www.cnn.com/2023/06/22/tech/musk-zuckerberg-cage-fight/index.html" target="_blank" rel="noopener">source</a>. The code, the tiny model and every experiment are on <a href="https://github.com/ho3h/seat-intelligence" target="_blank" rel="noopener">GitHub</a>.', next: "Scramble the table" },
    { go: function () { st.chat = null; st.rule = null; st.marks = null; if (st.saved) { st.puzzle = st.saved; st.saved = null; relayout(true); fit(); } else if (!st.puzzle) { st.puzzle = newPuzzle(1); lastInc = ""; relayout(true); fit(); } },
      cap: function () {
        var z = st.puzzle;
        if (z.over) return "<h1>p(doom) = 1. Game over.</h1><p>With " + flashpoints(z) + (flashpoints(z) === 1 ? " clash" : " clashes") + " still at the table, the AI apocalypse began somewhere between the soup and the main course. Have another go, or let the program show you how it’s done.</p>";
        if (z.done) return "<h1>" + (z.gaveUp ? "Here’s the program’s answer." : "p(doom) = 0. Apocalypse averted.") + "</h1><p>" + (z.gaveUp ? "No rules broken and no cage match. The next two steps show how it got there, and how a chatbot does with the same job." : "In this timeline, at least. You cleared it in " + z.moves + " swaps. Lunch is served, and nobody has mentioned the Octagon. Next, let’s see how a chatbot does.") + "</p>";
        return "<h1>You’re the host</h1><p class=\"rule\">“" + esc(LEVELS[z.lv].sentence) + "”</p><p>Someone has scrambled the seats. The President and Vice President keep their places at the middle of the table; everyone else is fair game. The faint boxes are sections of neighbouring seats. Put two people in one section who shouldn\u2019t be there together, and their names turn red, a red line joins them, and p(doom) climbs. Drag a guest onto another seat to swap them. Clear every clash and p(doom) falls to zero; let it reach 1 and it\u2019s game over.</p><p><span class=\"keyl\">" + keyLine(z) + "</span></p>";
      }, extra: function () { var z = st.puzzle; return z && z.over ? '<button class="btn" type="button" id="again">Try again</button>' : z && !z.done ? '<button class="btn" type="button" id="giveup">Give up</button>' : ""; }, next: "Next" },
    { go: function () { stash(); st.chat = C.show.secs; st.marks = markers(S.parse(LEVELS[1].prog)); relayout(true); fit(); },
      cap: function () { return "<h1>Now ask a chatbot</h1><p>We gave the officials part of that rule to an ordinary small chatbot and asked it 20 times.</p><p>Every one of its " + C.n + " answers broke the rule. " + C.dup + " seated someone twice, " + C.miss + " left someone without a seat, and between them there were " + C.distinct + " different seatings for the same question. The chart shows one: " + C.show.miss.length + " guests have no seat, which is one way to avoid arguments.</p>"; }, next: "Next" },
    { go: function () { stash(); setRule(LEVELS[1].prog); st.marks = markers(S.parse(LEVELS[1].prog)); relayout(true); fit(); },
      cap: function () {
        return "<h1>Our tiny AI splits the job in two</h1><p>First, a tiny AI reads the rule. It’s an openly available model, small enough to run on a laptop, that we retrained until it speaks only in a handful of instruction words, including the names of the guests. It doesn’t seat anyone. Given the whole rule, Musk clause and all, it wrote this in " + (LEVELS[1].secs ? LEVELS[1].secs.toFixed(1) : "0.4") + " seconds:</p><span class=\"code\">" + esc(LEVELS[1].prog) + "</span>" +
          "<p>Then a program built from tested building blocks, one per instruction word, does the seating. No rule is broken, and you get the same seating every time you ask. <button class=\"link\" type=\"button\" data-sheet>How it’s built</button></p>" +
          '<p class="fine">Recorded on a laptop; the tiny AI isn\u2019t running on this page. Asked 20 times, it wrote the same three lines 20 times.</p>';
      }, next: "Next" },
    { go: function () { stash(); setRule(LEVELS[1].prog); relayout(false); resetSea(); goTo(0, 0, 0.02); },
      cap: function () {
        if (sea.mode === "scrambled") return "<h1>Every other timeline</h1><p>Here is the same lunch in thousands of other timelines, each one seated a different way and each with its own host, who words the rules their own way. A red frame means p(doom) hit 1 at that table. You saved one by hand. Now let the tiny AI read every host\u2019s rules and try to save the rest.</p><p class=\"fine\" id=\"seastat\"></p>";
        if (sea.mode === "fixed") return "<h1>Nine in ten timelines saved</h1><p>Each timeline here gets one of 360 real readings by our tiny AI of rules written by someone else; zoom in to see each host\u2019s wording above their table. It read 321 of them correctly. Where it read the rule right, the timeline is saved, and every saved table ends up with exactly the same seating. Where it misread, p(doom) stays at 1.</p><p class=\"fine\" id=\"seastat\"></p>";
        return "<h1>The chatbot’s timelines</h1><p>These are the chatbot’s 20 real answers, repeated across the copies. None of them follows the rule, and between them there are 17 different seatings: seventeen different endings, none of them happy.</p><p class=\"fine\" id=\"seastat\"></p>";
      },
      extra: function () { return sea.mode === "fixed" ? '<button class="btn" type="button" id="chatall">Let the chatbot try</button>' : '<button class="btn" type="button" id="fixall">Let the tiny AI try</button>'; }, next: "Next" },
    { go: function () { stash(); var r = H6[shows[3].sentence] || { program: shows[3].emitted, intended: shows[3].gold }; setRule(r.program, r.intended); relayout(true); fit(); },
      cap: function () { var r = H6[shows[3].sentence] || { program: shows[3].emitted, intended: shows[3].gold };
        return "<h1>Where it can go wrong</h1><p>The tiny AI isn’t perfect. Given this longer rule:</p><p class=\"rule\">“" + esc(shows[3].sentence) + "”</p><p>it wrote</p><span class=\"code\">" + esc(r.program) + "</span><p>which mangles the officials part and drops “colleagues together” and “investors first”. The seating program then followed those wrong instructions exactly.</p>" +
          "<p>On rules worded by a writer it had never seen, it gets about 9 in 10 right. It can also trip on a surname it has never met: mention “Su” and it may invent a guest nobody is called, so the rule quietly does nothing. That’s why it always shows you the lines it wrote, so a person can catch a misreading before anyone sits down.</p>"; }, next: "Your turn" }
  ];

  function paint() {
    var html, bar;
    if (mode === "story") {
      var c = CH[chap], dots = "";
      for (var i = 0; i < CH.length; i++) dots += '<i class="' + (i === chap ? "on" : "") + '"></i>';
      html = c.cap();
      bar = '<div class="bar"><button class="link" type="button" id="back"' + (chap ? "" : " hidden") + '>Back</button><span class="dots" role="img" aria-label="Step ' + (chap + 1) + " of " + CH.length + '">' + dots + '</span><span class="sp"></span>' + (c.extra ? c.extra() : "") + '<button class="btn primary" type="button" id="next">' + c.next + "</button></div>";
    } else {
      var z = st.puzzle;
      html = z.over ? "<h1>p(doom) = 1. Game over.</h1><p>" + flashpoints(z) + " clashes were still at the table when the apocalypse started. Try again, or let the program show you.</p>" : z.done ? "<h1>" + (z.gaveUp ? "The program’s answer" : "p(doom) = 0. Apocalypse averted.") + "</h1><p>" + (z.gaveUp ? "No rules broken. Try another level, or scramble this one again and beat it yourself." : "You fixed it in " + z.moves + " swaps and " + Math.max(1, Math.round(z.secs)) + " seconds. Lunch is served. Try another rule, or let the tiny AI loose on every other timeline.") + "</p>"
        : "<h1>Your turn</h1><p class=\"rule\">“" + esc(LEVELS[z.lv].sentence) + "”</p>" + (LEVELS[z.lv].note ? "<p class=\"fine\">" + esc(LEVELS[z.lv].note) + "</p>" : "") + "<p>Drag guests to swap seats and clear every clash, the red names joined by red lines. Each wrong move pushes p(doom) towards 1. Use the arrows for another rule; there are seven, each written in plain English and read by the tiny AI.</p><p><span class=\"keyl\">" + keyLine(z) + "</span></p>";
      bar = '<div class="bar"><span class="stepper"><button class="btn small" type="button" data-lv="' + ((z.lv + LEVELS.length - 1) % LEVELS.length) + '" aria-label="Previous rule">\u2039</button><span class="lvname">' + esc(LEVELS[z.lv].name) + ' <span class="fine">' + (z.lv + 1) + ' of ' + LEVELS.length + '</span></span><button class="btn small" type="button" data-lv="' + ((z.lv + 1) % LEVELS.length) + '" aria-label="Next rule">\u203a</button></span><span class="sp"></span>' +
        (z.done || z.over ? '<button class="btn primary" type="button" id="again">' + (z.over ? 'Try again' : 'New scramble') + '</button>' : '<button class="btn" type="button" id="giveup">Give up</button>') + "</div>" +
        '<div class="links"><button class="link" type="button" id="thousands">Let the tiny AI save the other timelines</button><button class="link" type="button" data-sheet>How it works</button><button class="link" type="button" id="replay">Watch the story again</button></div>';
    }
    var clockLine = st.puzzle && (mode === "play" || chap === 1) ? '<div class="capclock" id="capclock"></div>' : "";
    var footer = mode === "story" && CH[chap].foot ? '<p class="capfoot">' + CH[chap].foot + "</p>" : "";
    capEl.innerHTML = clockLine + '<div class="cap-in">' + html + '</div><div class="morehint" aria-hidden="true">More \u2193</div>' + bar + footer;
    var ci = capEl.querySelector(".cap-in"), check = function () { var more = ci.scrollHeight - ci.scrollTop - ci.clientHeight > 6; ci.classList.toggle("more", more); capEl.classList.toggle("has-more", more); };
    ci.addEventListener("scroll", check); setTimeout(check, 0); setTimeout(check, 400);
    bind();
    live();
  }
  function bind() {
    var q = function (id) { return document.getElementById(id); };
    if (q("next")) q("next").onclick = function () { if (chap === CH.length - 1) play(); else story(chap + 1); };
    if (q("back")) q("back").onclick = function () { story(chap - 1); };
    if (q("giveup")) q("giveup").onclick = letAI;
    if (q("again")) q("again").onclick = function () { startPuzzle(st.puzzle.lv); };
    if (q("fixall")) q("fixall").onclick = function () { wave("fixed"); };
    if (q("chatall")) q("chatall").onclick = function () { wave("chat"); };
    if (q("replay")) q("replay").onclick = function () { story(0); };
    if (q("thousands")) q("thousands").onclick = function () { goTo(0, 0, 0.02); setTimeout(function () { wave("fixed"); }, reduce ? 0 : 900); };
    Array.prototype.forEach.call(capEl.querySelectorAll("[data-lv]"), function (b) { b.onclick = function () { startPuzzle(+b.dataset.lv); }; });
    Array.prototype.forEach.call(capEl.querySelectorAll("[data-sheet]"), function (b) { b.onclick = openSheet; });
  }
  function panel() { paint(); fitSoon(); }
  var fitT = 0;
  function fitSoon() { clearTimeout(fitT); fitT = setTimeout(function () { if (!camAnim && (mode !== "story" || chap !== 4)) fit(); }, 30); }
  function story(i) { mode = "story"; chap = Math.max(0, Math.min(CH.length - 1, i)); sheet.hidden = true; CH[chap].go(); paint(); fitSoon(); }
  function play() { mode = "play"; st.chat = null; st.rule = null; st.marks = null; if (!st.puzzle) { st.puzzle = st.saved || newPuzzle(0); st.saved = null; } resetSea(); relayout(true); paint(); fitSoon(); }
  function openSheet() { sheet.hidden = false; document.getElementById("sheetbody").innerHTML = aboutHTML(); sheet.scrollTop = 0; document.getElementById("sheetclose").focus(); }
  document.getElementById("sheetclose").onclick = function () { sheet.hidden = true; };
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") sheet.hidden = true; });
  var QUOTES = [["Elon Musk on Zuckerberg", "I’m up for a cage match if he is."], ["Mark Zuckerberg’s reply", "Send Me Location."]];
  function quoteToasts() { QUOTES.forEach(function (q, i) { setTimeout(function () { if (mode === "story" && chap === 0) toast(q[0] + ": “" + q[1] + "”"); }, 600 + i * 2600); }); }
  var ABOUT = '<div class="pane"><p class="kicker">Seat Intelligence (SI) \u00b7 How it works</p><h1>What we built, and why</h1><p class="fine">A game. The quotes are real public posts; the rest is made up. Not affiliated with anyone at the table.</p>' +
      "<p>Computers follow exact instructions. People describe rules in everyday words, usually over lunch. The small chatbots we tested went straight from the words to a seating, and slipped. We put a tiny AI in the middle that only translates, and let a checked program do the rest.</p>" +
      '<div class="flow"><div class="box"><b>Your rule, in plain words</b><span>“No two government officials in one section.”</span></div><div class="arrow">↓</div>' +
      '<div class="box hi"><b>Tiny AI: translate</b><span>A small model that runs on a laptop. Under half a second, one to four short lines out.</span></div><div class="arrow">↓</div>' +
      '<div class="box"><b>Instruction</b><span class="code">limit government 1</span><span>Seven instruction words (size, together, limit, apart, order, and two for named guests: avoid and pair) cover every rule on this page.</span></div><div class="arrow">↓</div>' +
      '<div class="box hi"><b>Tested seating program (no AI): seat and check</b><span>No AI in this step. The part that splits guests into sections was tested against thousands of cases. Same answer every time.</span></div><div class="arrow">↓</div>' +
      '<div class="box"><b>The seating, and a count of broken rules</b><span>If the AI misreads, you can see the instruction and catch it.</span></div></div>' +
      "<h2>How it’s built</h2><p><b>The tiny AI</b> is an openly available small model that we retrained on 9,000 example rules, each paired with the right instructions. It learned one narrow skill: turning a sentence into those instructions.</p><p><b>The building blocks</b> are small programs, one per instruction word. The seating program is simply the blocks the AI picked, snapped together in order.</p><svg class=\"fig\" viewBox=\"0 0 300 232\" role=\"img\" aria-label=\"The instruction words as building blocks stacked between guests in and seating out\"><text x=\"150\" y=\"14\" text-anchor=\"middle\" class=\"t\">guests in</text><path d=\"M150 20 V38\" class=\"w\"/><rect x=\"40\" y=\"40\" width=\"220\" height=\"40\" class=\"b\"/><text x=\"150\" y=\"65\" text-anchor=\"middle\" class=\"m\">together company</text><path d=\"M150 80 V98\" class=\"w\"/><rect x=\"40\" y=\"100\" width=\"220\" height=\"40\" class=\"b\"/><text x=\"150\" y=\"125\" text-anchor=\"middle\" class=\"m\">limit government 1</text><path d=\"M150 140 V158\" class=\"w\"/><rect x=\"40\" y=\"160\" width=\"220\" height=\"40\" class=\"b\"/><text x=\"150\" y=\"185\" text-anchor=\"middle\" class=\"m\">size 4</text><path d=\"M150 200 V218\" class=\"w\"/><text x=\"150\" y=\"231\" text-anchor=\"middle\" class=\"t\">seating out</text></svg><p class=\"fine\">The Hard puzzle’s rule as three blocks. Every block was tested on its own before use, including every possible case on small tables.</p><p><b>The code the blocks are written in</b> is unusual. It’s called an interaction net. Instead of lines of text, a program is a wiring diagram, and the computer runs it by rewriting pairs of connected pieces, over and over, until nothing is left to rewrite.</p><svg class=\"fig\" viewBox=\"0 0 300 96\" role=\"img\" aria-label=\"Two connected pieces meet and are replaced by a direct wire\"><path d=\"M10 30 H48 M10 66 H48\" class=\"w\"/><polygon points=\"48,22 48,74 88,48\" class=\"n\"/><path d=\"M88 48 H112\" class=\"w a\"/><polygon points=\"152,22 152,74 112,48\" class=\"n\"/><path d=\"M152 30 H176 M152 66 H176\" class=\"w\"/><text x=\"196\" y=\"53\" class=\"t\">→</text><path d=\"M214 30 C250 30 250 30 290 30 M214 66 C250 66 250 66 290 66\" class=\"w\"/></svg><p class=\"fine\">One rewrite step: two pieces joined head to head disappear, and their wires connect directly.</p><p>Every step is small and happens in one spot, so programs are easy to test and to snap together.</p><p><b>Why it matters.</b> The pattern fits any job made of rules: a tiny AI that only picks from tested blocks, and a program you can read. We first built it for tidying lists of people and companies, like merging duplicate contacts.</p>" +
      "<h2>The numbers</h2>" +
      '<div class="bars"><div class="lab"><span>Chatbot: answers that seat everyone once and follow the rule</span><span>0 of 400</span></div><div class="track"><div class="fill" style="width:0%"></div></div>' +
      '<div class="lab"><span>Tiny AI + seating program: answers that seat everyone once and follow the rule</span><span>400 of 400</span></div><div class="track"><div class="fill" style="width:100%"></div></div>' +
      '<p class="fine">The same 20 rules, 20 tries each, measured with the first version of the tiny AI, before it learned names. The chatbot is an ordinary small model on the same laptop, about twice the size of our tiny AI. We did not test the big online chatbots.</p></div>' +
      '<div class="facts"><div class="fact"><b>9 in 10</b><span>rules naming guests, worded by a separate AI writer, read correctly (321 of 360)</span></div>' +
      '<div class="fact"><b>1 answer</b><span>per rule, every time; the chatbot gave about 18 different ones</span></div>' +
      '<div class="fact"><b>&lt;0.5 s</b><span>for the tiny AI to write its instructions</span></div>' +
      '<div class="fact"><b>100,000</b><span>made-up guests seated with no broken rules in 1.5 to 3 seconds, not counting setup</span></div></div>' +
      "<h2>How we got here</h2><p>This began as a research question: can AI write programs in a new kind of code made for machines, closer to a wiring diagram than to words?</p><ul>" +
      "<li><b>AI can write it.</b> Off-the-shelf models wrote working programs for 176 of 200 test problems we wrote; each was checked by running it on test cases.</li>" +
      "" +
      "<li><b>Mistakes were in the planning, not the details.</b> So we built checked building blocks and let the AI choose and combine them.</li>" +
      "<li><b>That made a tiny AI work.</b> Writing whole programs, a small AI got about 1 in 7 tasks right. Choosing from checked building blocks, it got nearly all right when the wording was familiar, and 4 to 8 in 10 when it wasn’t.</li></ul>" +
      "<h2>What runs on this page</h2><p>The seating program runs live in your browser. It is a JavaScript copy of our checked program, tested to give identical answers on 400 random cases and every recorded example.</p><p>The tiny AI does not run in your browser. Its readings of these sentences were recorded on a laptop beforehand. The chatbot’s answers are its real answers from our test. The name words are new: avoid is now one of the checked building blocks, and pair is handled before the blocks run.</p>";
  function aboutHTML() { return ABOUT + '<h2>The code</h2><p>Everything is open: the tiny model, the seating program, the test sets, and every experiment that worked or didn\u2019t, with the write-ups. <a href="https://github.com/ho3h/seat-intelligence" target="_blank" rel="noopener">github.com/ho3h/seat-intelligence</a></p><p class="fine">Made by Theo Hopkinson: <a href="https://github.com/ho3h" target="_blank" rel="noopener">GitHub</a>, <a href="https://www.linkedin.com/in/theohopkinson/" target="_blank" rel="noopener">LinkedIn</a>, <a href="https://x.com/theohopkinson" target="_blank" rel="noopener">X</a>.</p></div>'; }
  // ---------- loop
  var liveT = 0;
  function frameLoop(now) {
    if (camAnim) {
      var p = Math.min(1, (now - camAnim.t0) / camAnim.dur), e = p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
      cam.x = camAnim.a.x + (camAnim.b.x - camAnim.a.x) * e; cam.y = camAnim.a.y + (camAnim.b.y - camAnim.a.y) * e; cam.s = Math.exp(camAnim.a.ls + (camAnim.b.ls - camAnim.a.ls) * e);
      dirty = true; if (p >= 1) camAnim = null;
    }
    if (stepAnim(now)) dirty = true;
    if (stepWave(now)) dirty = true;
    if (dirty) { dirty = false; render(now); }
    if (now - liveT > 200) { liveT = now; live(); }
    requestAnimationFrame(frameLoop);
  }
  window.addEventListener("resize", function () { resize(); fitSoon(); });
  if (document.fonts && document.fonts.load) Promise.all([document.fonts.load('italic 15px "Libre Caslon Text"'), document.fonts.load('700 20px "Libre Caslon Text"'), document.fonts.load('12px "Source Serif 4"'), document.fonts.load('700 20px "Courier Prime"')]).then(function () { dirty = true; }, function () {});
  var CARD = /^#card(-sq)?$/.test(location.hash), SQ = location.hash === "#card-sq";
  resize(); cam.s = fitScale();
  relayout(false); story(0);
  if (CARD) setTimeout(makeCard, 50);
  function makeCard() {
    document.body.classList.add("card"); if (SQ) document.body.classList.add("sq");
    story(1); var z = st.puzzle;
    var idx = function (n) { return real.findIndex(function (g) { return g.name === n; }); };
    var M = idx("Elon Musk"), Z = idx("Mark Zuckerberg");
    // put Musk and Zuckerberg in one section on the right-hand side of the table, where the picture looks
    var right = []; for (var k = HALF; k < N; k++) right.push(k);
    var tgt = null;
    for (var i = 0; i < right.length && !tgt; i++) for (var j = 0; j < right.length; j++) { var a1 = right[i], b1 = right[j]; if (a1 !== b1 && z.groups[a1] === z.groups[b1] && Math.abs(seatXY(a1).row - 8) <= 4 && Math.abs(seatXY(a1).row - seatXY(b1).row) === 1) { tgt = [a1, b1]; break; } }
    if (tgt) { if (z.seat[tgt[0]] !== M) swapSeats(z.seat.indexOf(M), tgt[0], false); if (z.seat[tgt[1]] !== Z) swapSeats(z.seat.indexOf(Z), tgt[1], false); }
    for (var t = 0; t < 400 && z.pd < 0.8 && !z.over; t++) {
      var a = Math.floor(Math.random() * N), b = Math.floor(Math.random() * N);
      if (a === b || [z.seat[a], z.seat[b]].some(function (g) { return g === M || g === Z; })) continue;
      var before = flashpoints(z); swapSeats(a, b, false); if (flashpoints(z) < before) swapSeats(a, b, false);
    }
    anim = null; cur = tgtPos.map(function (q) { return { side: q.side, x: q.x, y: q.y, k: q.k }; });
    var p = cur[M];
    if (SQ) goTo(255, 30, 1.27, true);
    else goTo(300, p.y + 10, 1.2, true);
    var el = document.getElementById("cardtext");
    el.innerHTML = '<span>Seat Intelligence (SI)</span>';
    var tt = document.getElementById("toast"); tt.textContent = "Musk and Zuckerberg share a section. Someone has mentioned the Octagon."; tt.classList.add("on"); clearTimeout(toastT); toastT = 0;
    live();
    el.hidden = false; dirty = true;
  }
  requestAnimationFrame(frameLoop);
  window.__luncheon = { st: st, sea: sea, cam: cam, story: story, play: play, swap: swapSeats, letAI: letAI, wave: wave, stepWave: stepWave,
    render: function () { render(performance.now()); }, sheet: openSheet, clashes: clashes, newPuzzle: newPuzzle, evalSeats: evalSeats, FREE: FREE };
})();
