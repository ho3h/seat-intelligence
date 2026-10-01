(function () {
  var S = Seating;
  var N = 34, HALF = 17, ROW0 = -354, PITCH = 44.25, PX = 820, PY = 1120;
  var TABLE = "#2e2e2b", INK = "#151515", MUTE = "#6b6b68", RED = "#a8322a", BAD = INK, GOOD = INK, BLUE = INK;
  var TINT = ["#efeeea", "#e1dfd9"];
  var FONT = '"Cormorant Garamond", "EB Garamond", Georgia, serif', TEXT = '"Source Serif 4", Georgia, serif';
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
    { name: "Hard", sentence: "Keep colleagues together, sections of at most four, and never put two government officials in the same section.", prog: "size 4\ntogether company\nlimit government 1" }];
  LEVELS.forEach(function (L) { var r = H6[L.sentence]; if (r && r.ok) { L.prog = r.program; L.secs = r.secs; } });
  var MARK = { 5: ["G", INK, "government official", "government officials"], 0: ["A", INK, "AI lab guest", "AI lab guests"], 1: ["T", "#2f7d4f", "big tech guest", "big tech guests"] };
  function solve(prog) {
    var p = S.parse(prog), r = S.seat(realEng, p);
    return { judge: p, ai: r.seq.slice(), groups: r.seq.map(function (i) { return r.assign[i]; }) };
  }
  function evalSeats(judge, groups, seat) {
    var assign = new Array(N);
    for (var k = 0; k < N; k++) if (seat[k] >= 0) assign[seat[k]] = groups[k];
    var v = S.violations(realEng, judge, assign);
    return { total: v.v.total, bad: v.badSections, v: v.v };
  }
  function markers(judge) {
    var cats = {}, m = {}, cnt = {};
    judge.limits.forEach(function (l) { l[0].forEach(function (c) { cats[c] = 1; }); });
    judge.aparts.forEach(function (a) { cats[a[0]] = 1; cats[a[1]] = 1; });
    real.forEach(function (g) { if (g.org) cnt[g.org] = (cnt[g.org] || 0) + 1; });
    var who = {}; (judge.avoids || []).forEach(function (a) { who[a[0]] = 1; who[a[1]] = 1; });
    real.forEach(function (g, i) {
      if (Object.keys(who).some(function (w) { return S.isWho(g, w); })) m[i] = ["R", INK, "rival", "rivals (Musk, OpenAI, Zuckerberg)"];
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
    for (var t = 0; t < 80; t++) { seat = shuffle(s.ai, r); if (evalSeats(s.judge, s.groups, seat).total >= 4) break; }
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
    var R = st.rule, r = S.seat(realEng, R.exec), sec = r.seq.map(function (i) { return r.assign[i]; });
    var pa = S.postedAssignment(N, R.exec.cap), vp = S.violations(realEng, R.judge, pa), va = S.violations(realEng, R.judge, r.assign);
    R.vP = vp.v; R.vA = va.v;
    return { seatGuest: r.seq, sec: sec, bad: va.badSections };
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
  var mainArr = null, cur = [], anim = null, tgtPos = [];
  function targetPos(arr) {
    var t = new Array(N);
    for (var k = 0; k < N; k++) { var gi = arr.seatGuest[k], s = seatXY(k); if (gi >= 0 && !t[gi]) t[gi] = { side: s.side, x: s.x, y: s.y, k: k }; }
    var j = 0; for (var g = 0; g < N; g++) if (!t[g]) { t[g] = { side: 0, x: 0, y: 402 + 22 * j, k: -1 }; j++; }
    return t;
  }
  function relayout(animate) {
    var prev = cur.length ? cur.map(function (p) { return { side: p.side, x: p.x, y: p.y }; }) : null;
    mainArr = mainArrange(); tgtPos = targetPos(mainArr);
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
    var capE = document.getElementById("cap"), ch = capE ? capE.offsetHeight + 16 : 0, top = 12, avail = Math.max(120, H - ch - top);
    var l = -390, r = 390;
    if (bubblesOn()) BUBBLES.forEach(function (b) { var p = tgtPos[real.findIndex(function (g) { return g.name === b.who; })]; if (p && p.side > 0) r = 720; else if (p && p.side < 0) l = -720; });
    var s = W < 600 ? (W - 8) / 700 : Math.min((W - 24) / (r - l), avail / 1060);
    goTo((l + r) / 2, -40 + (ch - top) / 2 / s, s);
  }
  function toWorld(cx, cy) { var r = stage.getBoundingClientRect(); return { x: cam.x + (cx - r.left - W / 2) / cam.s, y: cam.y + (cy - r.top - H / 2) / cam.s }; }

  // ---------- drawing
  function rr(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
  function chair(x, side, y, hi, detail) {
    ctx.fillStyle = hi ? INK : "#fff"; ctx.strokeStyle = INK;
    if (!detail) { ctx.lineWidth = 2.2; ctx.fillRect(x - 10, y - 12, 20, 24); ctx.strokeRect(x - 10, y - 12, 20, 24); return; }
    ctx.lineWidth = 1.5; rr(x - 11, y - 13, 22, 26, 3); ctx.fill(); ctx.stroke(); ctx.strokeRect(x - 6, y - 8, 12, 16);
    ctx.lineWidth = 3.2; ctx.beginPath(); var bx = x + side * 10; ctx.moveTo(bx, y - 12); ctx.lineTo(bx, y + 12); ctx.stroke();
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
      var bad = arr.bad && arr.bad.has(sec);
      if (bad) { ctx.fillStyle = "rgba(168,50,42,.06)"; rr(x0, top + 1, w, bot - top - 2, 6); ctx.fill(); }
      ctx.strokeStyle = bad ? RED : "#c9c7c0"; ctx.lineWidth = bad ? 2.2 : 1.2; rr(x0, top + 1, w, bot - top - 2, 6); ctx.stroke();
      if (lod >= 2) {
        ctx.font = "600 12px " + TEXT; ctx.textBaseline = "middle"; ctx.fillStyle = bad ? RED : MUTE; ctx.textAlign = s0.side < 0 ? "left" : "right";
        ctx.fillText(String(sec + 1), s0.side < 0 ? x0 + 7 : x0 + w - 7, top + 11);
      }
      k = m + 1;
    }
  }
  function mark(mk, x, y) {
    ctx.fillStyle = mk[1]; ctx.beginPath(); ctx.arc(x, y, 9, 0, 6.2832); ctx.fill();
    ctx.fillStyle = "#fff"; ctx.font = "600 11px " + TEXT; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(mk[0], x, y + 0.5);
  }
  function nameAt(label, x, y, side, mk) {
    ctx.font = "italic 500 17px " + FONT; ctx.fillStyle = INK; ctx.textBaseline = "middle"; ctx.textAlign = side < 0 ? "right" : "left";
    ctx.fillText(label, x, y);
    if (mk) { var tw = ctx.measureText(label).width; mark(mk, side < 0 ? x - tw - 13 : x + tw + 13, y); }
  }
  function header() {
    ctx.fillStyle = MUTE; ctx.font = "italic 17px " + FONT; ctx.textAlign = "left"; ctx.textBaseline = "middle";
    ctx.fillText("Super Intelligence Luncheon", -372, -518); ctx.fillText("Tuesday, September 29, 2026", -372, -498);
    ctx.fillStyle = INK; ctx.font = "600 23px " + FONT; ctx.textAlign = "center"; ctx.fillText("Seating Chart \u00b7 East Room", 0, -492);
  }
  function frame(color, lw) { ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.strokeRect(-345, -472, 690, 944); }
  function tableShape(lod) { ctx.fillStyle = lod >= 1 ? TABLE : "#bdbbb5"; ctx.strokeStyle = INK; ctx.lineWidth = 2.5; if (lod >= 1) { rr(-62, -370, 124, 740, 26); ctx.fill(); ctx.stroke(); } else ctx.fillRect(-62, -370, 124, 740); }

  var BUBBLES = [
    { who: "Mark Zuckerberg", text: "Send Me Location", src: "Zuckerberg on Instagram, June 2023", dy: 0 },
    { who: "Elon Musk", text: "I’m up for a cage match if he is", src: "Musk on Twitter, June 2023", dy: -32 },
    { who: "Elon Musk", text: "Not what I intended at all.", src: "Musk on OpenAI, on X, Feb 2023", dy: 32 }];
  function bubblesOn() { var z = st.puzzle; return W >= 600 && ((mode === "story" && (chap === 0 || (chap === 1 && z && z.moves === 0))) || (mode === "play" && z && z.lv === 1 && z.moves === 0)); }
  function drawBubbles() {
    BUBBLES.forEach(function (b) {
      var gi = real.findIndex(function (g) { return g.name === b.who; }), p = cur[gi]; if (!p || p.side === 0) return;
      ctx.font = "italic 500 18px " + FONT; var w1 = ctx.measureText("\u201c" + b.text + "\u201d").width; ctx.font = "12px " + TEXT; var tw = Math.max(w1, ctx.measureText(b.src).width) + 28;
      var y = p.y + b.dy, x0 = p.side > 0 ? 372 : -372 - tw, h = 46, ty = Math.max(y - h / 2 + 8, Math.min(y + h / 2 - 8, p.y));
      ctx.fillStyle = "#fff"; ctx.strokeStyle = INK; ctx.lineWidth = 1.6;
      rr(x0, y - h / 2, tw, h, 12); ctx.fill(); ctx.stroke();
      var ex = p.side > 0 ? x0 : x0 + tw, tip = p.side > 0 ? 350 : -350;
      ctx.beginPath(); ctx.moveTo(ex, ty - 7); ctx.lineTo(tip, p.y); ctx.lineTo(ex, ty + 7); ctx.fillStyle = "#fff"; ctx.fill();
      ctx.beginPath(); ctx.moveTo(ex, ty - 7); ctx.lineTo(tip, p.y); ctx.lineTo(ex, ty + 7); ctx.stroke();
      ctx.fillStyle = "#fff"; ctx.fillRect(ex - 1, ty - 6, 2, 12);
      ctx.textAlign = "left"; ctx.textBaseline = "middle";
      ctx.fillStyle = INK; ctx.font = "italic 500 18px " + FONT; ctx.fillText("“" + b.text + "”", x0 + 13, y - 8);
      ctx.fillStyle = MUTE; ctx.font = "12px " + TEXT; ctx.fillText(b.src, x0 + 13, y + 12);
    });
  }
  var drag = null;
  function drawMain(lod) {
    frame("#000", Math.max(9, 2.2 / cam.s));
    [100, 138, 565, 688, 725, 883].forEach(function (yy) { var y = -472 + (yy - 62) / 945 * 944; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(-372, y); ctx.lineTo(-318, y); ctx.stroke(); });
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
    if (lod < 2 && !z) return;
    for (var gi = 0; gi < N; gi++) {
      if (drag && drag.active && drag.gi === gi) continue;
      var p = cur[gi];
      if (p.side === 0) { ctx.font = "italic 500 17px " + FONT; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillStyle = MUTE; ctx.fillText(real[gi].label + " — no seat", p.x, p.y); continue; }
      nameAt(real[gi].label, p.x, p.y, p.side, marks && marks[gi]);
    }
    if (drag && drag.active) {
      var lab = real[drag.gi].label; ctx.font = "italic 500 18px " + FONT; var tw = ctx.measureText(lab).width + 40;
      ctx.save(); ctx.shadowColor = "rgba(0,0,0,.28)"; ctx.shadowBlur = 14; ctx.shadowOffsetY = 4; ctx.fillStyle = "#fff";
      rr(drag.wx - tw / 2, drag.wy - 18, tw, 36, 18); ctx.fill(); ctx.restore();
      ctx.strokeStyle = BLUE; ctx.lineWidth = 2; rr(drag.wx - tw / 2, drag.wy - 18, tw, 36, 18); ctx.stroke();
      ctx.font = "italic 500 18px " + FONT; ctx.fillStyle = INK; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(lab, drag.wx + 8, drag.wy);
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
    var seat = shuffle(sea.ai, rng((Math.imul(i, 73856093) ^ Math.imul(j, 19349663) ^ 0x5bd1e995) >>> 0));
    var ev = evalSeats(sea.judge, sea.groups, seat);
    c = { seatGuest: seat, sec: sea.groups, bad: ev.bad, broken: ev.total > 0 }; sea.cache.set(key, c);
    return c;
  }
  function copyArr(i, j) {
    var d = Math.hypot(i, j * PY / PX);
    if (sea.mode !== "scrambled" && d <= sea.waveR) {
      if (sea.mode === "fixed") { if (!fixedArr) fixedArr = { seatGuest: sea.ai, sec: sea.groups, bad: new Set(), broken: false }; return fixedArr; }
      var idx = ((Math.imul(i, 2654435761) ^ Math.imul(j, 40503)) >>> 0) % C.answers.length;
      return chatArrange(C.answers[idx], sea.judge);
    }
    return copyScramble(i, j);
  }
  function drawCopy(i, j, lod) {
    var a = copyArr(i, j);
    ctx.save(); ctx.translate(i * PX, j * PY);
    frame(a ? (a.broken ? RED : "#a9a8a3") : "#dcdbd6", a && a.broken ? (lod >= 2 ? 6 : Math.max(6, 2.2 / cam.s)) : (lod >= 2 ? 3 : Math.max(3, 1 / cam.s)));
    if (a && lod >= 1) strips(a, lod);
    tableShape(lod);
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
    var z = st.puzzle; if (!z || z.done || a === b) return;
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
  function flashpoints(z) { return z.ev ? z.ev.bad.size + (z.ev.v.together ? 1 : 0) : 0; }
  function rivalsTogether(z) { return incidents(z).filter(function (t) { return t.indexOf("Musk") === 0; }).length; }
  function startDoom(z) { z.fp0 = flashpoints(z); z.riv0 = rivalsTogether(z); z.pd = Math.min(0.72, 0.22 + 0.08 * z.fp0 + 0.05 * z.riv0); }
  function stepDoom(z) {
    var fp = flashpoints(z), riv = rivalsTogether(z), d = fp - z.fp0, dr = riv - z.riv0;
    if (fp === 0) z.pd = 0;
    else z.pd = Math.max(0.01, Math.min(1, z.pd + (d > 0 ? 0.14 * d : d < 0 ? 0.1 * d : 0.025) + (dr > 0 ? 0.12 * dr : 0)));
    z.fp0 = fp; z.riv0 = riv;
    if (z.pd >= 1) gameOver();
  }
  function gameOver() {
    var z = st.puzzle; z.over = true; z.pd = 1; z.pick = -1; drag = null;
    overEl.hidden = false; paint(); dirty = true;
  }
  document.getElementById("retry").onclick = function () { overEl.hidden = true; startPuzzle(st.puzzle ? st.puzzle.lv : 1); };
  document.getElementById("showai").onclick = letAI;
  var toastT = 0;
  function toast(msg) { var t = document.getElementById("toast"); t.textContent = msg; t.classList.add("on"); clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove("on"); }, 2200); }

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
    if (e.target.closest(".nav")) return;
    try { stage.setPointerCapture(e.pointerId); } catch (err) {} ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY }); camAnim = null;
    var z = st.puzzle;
    if (ptrs.size === 1 && z && !z.done && !z.over && cam.s >= 0.12) {
      var w = toWorld(e.clientX, e.clientY), k = hitSeat(w.x, w.y);
      if (k >= 0 && z.seat[k] >= 0) { drag = { k: k, gi: z.seat[k], wx: w.x, wy: w.y, active: false, hover: -1, sx: e.clientX, sy: e.clientY }; return; }
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
      if (drag.active) { var w = toWorld(e.clientX, e.clientY); drag.wx = w.x; drag.wy = w.y; drag.hover = hitSeat(w.x, w.y); dirty = true; }
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
  stage.addEventListener("wheel", function (e) { e.preventDefault(); camAnim = null; zoomAt(e.clientX, e.clientY, cam.s * Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0015))); }, { passive: false });
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
    if (has.R) parts.push(dot(has.R[1], "R") + "Musk and his rivals");
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
      document.getElementById("hudred").textContent = z.done ? (z.gaveUp ? "The program saved this one" : "You saved this timeline") : z.over ? "Game over" : fp + " flashpoint" + (fp === 1 ? "" : "s");
      var cls = "hud" + (z.done ? " ok" : pd >= 0.75 ? " late" : "");
      hud.className = cls;
      if (cc) { cc.className = "capclock" + (z.done ? " ok" : pd >= 0.75 ? " late" : ""); cc.innerHTML = "<b>" + document.getElementById("doomt").textContent + "</b> " + document.getElementById("hudred").textContent; }
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
      else out.push(a[0].replace(/_/g, " ") + " and " + a[1].replace(/_/g, " ") + " share a section. Tension rising.");
    });
    if (z.ev.v.limit) out.push("Two officials in one section. A subcommittee has formed.");
    if (z.ev.v.apart) out.push("AI labs and big tech share a section. Someone is talking about compute.");
    if (z.ev.v.together) out.push("Colleagues split up. Nobody knows who has the slides.");
    return out;
  }

  var CH = [
    { go: function () { st.puzzle = null; st.saved = null; st.chat = null; st.rule = null; st.marks = null; resetSea(); relayout(true); fit(); if (W < 600) quoteToasts(); },
      cap: function () {
        return "<h1>Who sits next to whom?</h1><p>This is the real seating chart from the White House lunch with AI leaders on 29 September 2026. Every seating plan has rules, and this room comes with some history: a few of these guests have been arguing in public for years.</p>" +
          "<p>Seat these people badly and it’s game over: p(doom) goes to 1, and the AI apocalypse starts somewhere between the soup and the main course. Most versions of this lunch end that way. Your job is to find the one that doesn’t, and then we’ll see whether a small chatbot or our tiny AI can do the same.</p>" +
          '<p class="fine">A game. The quotes are real public posts; the rest is made up. Not affiliated with anyone at the table. <a href="https://x.com/elonmusk/status/1626516035863212034" target="_blank" rel="noopener">Source</a>, <a href="https://www.cnn.com/2023/06/22/tech/musk-zuckerberg-cage-fight/index.html" target="_blank" rel="noopener">source</a>.</p>';
      }, next: "Scramble the table" },
    { go: function () { st.chat = null; st.rule = null; st.marks = null; if (st.saved) { st.puzzle = st.saved; st.saved = null; relayout(true); fit(); } else if (!st.puzzle) { st.puzzle = newPuzzle(1); lastInc = ""; relayout(true); fit(); } },
      cap: function () {
        var z = st.puzzle;
        if (z.over) return "<h1>p(doom) = 1. Game over.</h1><p>With " + flashpoints(z) + " flashpoint" + (flashpoints(z) === 1 ? "" : "s") + " still burning, the AI apocalypse began somewhere between the soup and the main course. Have another go, or let the program show you how it’s done.</p>";
        if (z.done) return "<h1>" + (z.gaveUp ? "Here’s the program’s answer." : "p(doom) = 0. Apocalypse averted.") + "</h1><p>" + (z.gaveUp ? "No rules broken and no cage match. The next two steps show how it got there, and how a chatbot does with the same job." : "In this timeline, at least. You cleared it in " + z.moves + " swaps. Lunch is served, and nobody has mentioned the Octagon. Next, let’s see how a chatbot does.") + "</p>";
        return "<h1>You’re the host</h1><p class=\"rule\">“" + esc(LEVELS[z.lv].sentence) + "”</p><p>Someone has scrambled the seats. Each outlined box is a section of neighbouring seats, and a section that breaks the rule turns red: that\u2019s a flashpoint. Drag a guest onto another seat and the two swap places. Clear a flashpoint and p(doom) falls; make a new one and it climbs. If it reaches 1, it\u2019s game over.</p><p><span class=\"keyl\">" + keyLine(z) + "</span></p>";
      }, extra: function () { var z = st.puzzle; return z && z.over ? '<button class="btn" type="button" id="again">Try again</button>' : z && !z.done ? '<button class="btn" type="button" id="giveup">Give up</button>' : ""; }, next: "Next" },
    { go: function () { stash(); st.chat = C.show.secs; st.marks = markers(S.parse(LEVELS[1].prog)); relayout(true); fit(); },
      cap: function () { return "<h1>Now ask a chatbot</h1><p>We gave the officials part of that rule to an ordinary small chatbot and asked it 20 times. We spared it the Musk clause.</p><p>Every one of its " + C.n + " answers broke the rule. " + C.dup + " seated someone twice, " + C.miss + " left someone without a seat, and between them there were " + C.distinct + " different seatings for the same question. The chart shows one: " + C.show.miss.length + " guests have no seat, which is one way to avoid arguments.</p>"; }, next: "Next" },
    { go: function () { stash(); setRule(LEVELS[1].prog); st.marks = markers(S.parse(LEVELS[1].prog)); relayout(true); fit(); },
      cap: function () {
        return "<h1>Our tiny AI splits the job in two</h1><p>First, a tiny AI reads the rule. It’s an openly available model, small enough to run on a laptop, that we retrained until it speaks only in a handful of instruction words, including the names of the guests. It doesn’t seat anyone. Given the whole rule, Musk clause and all, it wrote this in " + (LEVELS[1].secs ? LEVELS[1].secs.toFixed(1) : "0.4") + " seconds:</p><span class=\"code\">" + esc(LEVELS[1].prog) + "</span>" +
          "<p>Then a program built from tested building blocks, one per instruction word, does the seating. No rule is broken, and you get the same seating every time you ask. <button class=\"link\" type=\"button\" data-sheet>How it’s built</button></p>" +
          '<p class="fine">Recorded on a laptop; the tiny AI isn\u2019t running on this page. Asked 20 times, it wrote the same three lines 20 times.</p>';
      }, next: "Next" },
    { go: function () { stash(); setRule(LEVELS[1].prog); relayout(false); resetSea(); goTo(0, 0, 0.02); },
      cap: function () {
        if (sea.mode === "scrambled") return "<h1>Every other timeline</h1><p>Here is the same lunch in thousands of other timelines, each one seated a different way. A red frame means p(doom) hit 1 at that table. You saved one by hand. These need saving too, and this is where a program earns its keep.</p><p class=\"fine\" id=\"seastat\"></p>";
        if (sea.mode === "fixed") return "<h1>Every timeline saved</h1><p>Every copy is fixed, and every copy ends up with exactly the same seating. However the lunch started, the program finds its way to the same safe ending.</p><p class=\"fine\" id=\"seastat\"></p>";
        return "<h1>The chatbot’s timelines</h1><p>These are the chatbot’s 20 real answers, repeated across the copies. None of them follows the rule, and between them there are 17 different seatings: seventeen different endings, none of them happy.</p><p class=\"fine\" id=\"seastat\"></p>";
      },
      extra: function () { return sea.mode === "fixed" ? '<button class="btn" type="button" id="chatall">Let the chatbot try</button>' : '<button class="btn" type="button" id="fixall">Save every timeline</button>'; }, next: "Next" },
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
      html = z.over ? "<h1>p(doom) = 1. Game over.</h1><p>" + flashpoints(z) + " flashpoints were still burning when the apocalypse started. Try again, or let the program show you.</p>" : z.done ? "<h1>" + (z.gaveUp ? "The program’s answer" : "p(doom) = 0. Apocalypse averted.") + "</h1><p>" + (z.gaveUp ? "No rules broken. Try another level, or scramble this one again and beat it yourself." : "You fixed it in " + z.moves + " swaps and " + Math.max(1, Math.round(z.secs)) + " seconds. Lunch is served. Try a harder level, or save every other timeline at once.") + "</p>"
        : "<h1>Your turn</h1><p class=\"rule\">“" + esc(LEVELS[z.lv].sentence) + "”</p><p>Drag guests to swap seats and clear every red flashpoint. Each wrong move pushes p(doom) towards 1. Pick a level below; Hard adds a rule about keeping colleagues together.</p><p><span class=\"keyl\">" + keyLine(z) + "</span></p>";
      bar = '<div class="bar"><span class="chips">' + LEVELS.map(function (L, i) { return '<button class="btn small chip" type="button" data-lv="' + i + '" aria-pressed="' + (i === z.lv) + '">' + L.name + "</button>"; }).join("") + '</span><span class="sp"></span>' +
        (z.done || z.over ? '<button class="btn primary" type="button" id="again">' + (z.over ? 'Try again' : 'New scramble') + '</button>' : '<button class="btn" type="button" id="giveup">Give up</button>') + "</div>" +
        '<div class="links"><button class="link" type="button" id="thousands">Save every timeline</button><button class="link" type="button" data-sheet>How it works</button><button class="link" type="button" id="replay">Watch the story again</button></div>';
    }
    var clockLine = st.puzzle && (mode === "play" || chap === 1) ? '<div class="capclock" id="capclock"></div>' : "";
    capEl.innerHTML = clockLine + '<div class="cap-in">' + html + "</div>" + bar;
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
  var QUOTES = [["Elon Musk on OpenAI", "Not what I intended at all."], ["Elon Musk on Zuckerberg", "I’m up for a cage match if he is."], ["Mark Zuckerberg’s reply", "Send Me Location."]];
  function quoteToasts() { QUOTES.forEach(function (q, i) { setTimeout(function () { if (mode === "story" && chap === 0) toast(q[0] + ": “" + q[1] + "”"); }, 600 + i * 2600); }); }
  var ABOUT = '<div class="pane"><p class="kicker">How it works</p><h1>What we built, and why</h1>' +
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
  function aboutHTML() { return ABOUT + "</div>"; }
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
  if (document.fonts && document.fonts.load) Promise.all([document.fonts.load('italic 500 17px "Cormorant Garamond"'), document.fonts.load('600 23px "Cormorant Garamond"'), document.fonts.load('12px "Source Serif 4"')]).then(function () { dirty = true; }, function () {});
  resize(); cam.s = fitScale();
  relayout(false); story(0);
  requestAnimationFrame(frameLoop);
  window.__luncheon = { st: st, sea: sea, cam: cam, story: story, play: play, swap: swapSeats, letAI: letAI, wave: wave, stepWave: stepWave,
    render: function () { render(performance.now()); }, sheet: openSheet };
})();
