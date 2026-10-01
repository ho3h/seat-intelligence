// Seating function for the luncheon page. A line-for-line port of genome/hero1/lang.py
// (parse, prep, ref_sections, violations, posted_assignment) and of the HERO-6 named words
// `avoid` and `pair` (genome/hero6/lang6.py). Checked against the Python reference by
// test_seating.js; the Python reference is itself checked against the verified net.
var Seating = (function () {
  var CATS = ["ai_lab", "big_tech", "chips", "software_security", "investor", "government", "unlabelled"];
  var CID = {}; CATS.forEach(function (c, i) { CID[c] = i; });
  var INF = (1 << 24) - 1, MAXCAP = 6;

  function uniqSorted(a) { return Array.from(new Set(a)).sort(function (x, y) { return x - y; }); }
  function canon(p) {
    var limits = p.limits.map(function (l) { return [uniqSorted(l[0]), l[1]]; });
    limits.sort(function (a, b) { return cmp(a, b); });
    var seen = {}, aparts = [];
    p.aparts.forEach(function (x) { var t = [Math.min(x[0], x[1]), Math.max(x[0], x[1])]; var k = t.join(","); if (!seen[k]) { seen[k] = 1; aparts.push(t); } });
    aparts.sort(function (a, b) { return cmp(a, b); });
    // named words are symmetric: smaller token first, sorted, duplicates removed (lang6.Policy6.canon)
    function named(xs) {
      var seen = {}, out = [];
      (xs || []).forEach(function (x) { var t = x[0] < x[1] ? [x[0], x[1]] : [x[1], x[0]]; var k = t.join("\u0000"); if (!seen[k]) { seen[k] = 1; out.push(t); } });
      out.sort(function (a, b) { return cmp(a, b); });
      return out;
    }
    return { cap: p.cap, togCompany: p.togCompany, togCats: uniqSorted(p.togCats), limits: limits, aparts: aparts, order: p.order.slice(), avoids: named(p.avoids), pairs: named(p.pairs) };
  }
  function cmp(a, b) {
    if (Array.isArray(a)) { for (var i = 0; i < Math.min(a.length, b.length); i++) { var c = cmp(a[i], b[i]); if (c) return c; } return a.length - b.length; }
    return a < b ? -1 : a > b ? 1 : 0;
  }
  function emptyPolicy() { return { cap: MAXCAP, togCompany: false, togCats: [], limits: [], aparts: [], order: [], avoids: [], pairs: [] }; }

  function parse(text) {
    var lines = text.trim().split("\n").map(function (l) { return l.trim(); }).filter(function (l) { return l && l.indexOf("```") !== 0; });
    if (!lines.length || (lines.length === 1 && lines[0] === "none")) return emptyPolicy();
    var cap = null, tc = false, tk = [], lim = [], apt = [], order = null, avd = [], par = [];
    lines.forEach(function (l) {
      var t = l.split(/\s+/), w = t[0];
      if (w === "size" && t.length === 2 && /^\d+$/.test(t[1])) {
        if (cap !== null) throw new Error("size given twice");
        cap = parseInt(t[1], 10);
        if (cap < 1 || cap > MAXCAP) throw new Error("size must be 1 to " + MAXCAP + ": " + l);
      } else if (w === "together" && t.length === 2) {
        if (t[1] === "company") tc = true;
        else if (t[1] in CID) tk.push(CID[t[1]]);
        else throw new Error("unknown category: " + l);
      } else if (w === "limit" && t.length >= 3 && /^\d+$/.test(t[t.length - 1]) && t.slice(1, -1).every(function (x) { return x in CID; })) {
        var k = parseInt(t[t.length - 1], 10);
        if (k < 1 || k > 6) throw new Error("limit must be 1 to 6: " + l);
        lim.push([t.slice(1, -1).map(function (x) { return CID[x]; }), k]);
      } else if (w === "apart" && t.length === 3 && t[1] in CID && t[2] in CID && t[1] !== t[2]) {
        apt.push([CID[t[1]], CID[t[2]]]);
      } else if (w === "order" && t.length >= 2 && t.slice(1).every(function (x) { return x in CID; })) {
        if (order !== null) throw new Error("order given twice");
        var ids = t.slice(1).map(function (x) { return CID[x]; });
        if (new Set(ids).size !== ids.length) throw new Error("category repeated in order");
        order = ids;
      } else if (w === "avoid" && t.length === 3 && t[1] !== t[2]) {
        avd.push([t[1], t[2]]);   // two named guests or companies, spaces written as _
      } else if (w === "pair" && t.length === 3 && t[1] !== t[2]) {
        par.push([t[1], t[2]]);   // same: these two sit in one section
      } else throw new Error("not a word I know: " + l);
    });
    return canon({ cap: cap === null ? MAXCAP : cap, togCompany: tc, togCats: tk, limits: lim, aparts: apt, order: order || [], avoids: avd, pairs: par });
  }

  function toText(p) {
    p = canon(p); var L = [];
    if (p.cap !== MAXCAP) L.push("size " + p.cap);
    if (p.togCompany) L.push("together company");
    p.togCats.forEach(function (c) { L.push("together " + CATS[c]); });
    p.limits.forEach(function (l) { L.push("limit " + l[0].map(function (c) { return CATS[c]; }).join(" ") + " " + l[1]); });
    p.aparts.forEach(function (a) { L.push("apart " + CATS[a[0]] + " " + CATS[a[1]]); });
    if (p.order.length) L.push("order " + p.order.map(function (c) { return CATS[c]; }).join(" "));
    (p.avoids || []).forEach(function (a) { L.push("avoid " + a[0] + " " + a[1]); });
    (p.pairs || []).forEach(function (a) { L.push("pair " + a[0] + " " + a[1]); });
    return L.length ? L.join("\n") : "none";
  }

  function rules(p) {
    var out = [];
    p.limits.forEach(function (l) { var m = 0; l[0].forEach(function (c) { m += 1 << c; }); out.push([m, 0, l[1]]); });
    p.aparts.forEach(function (a) { out.push([1 << a[0], 1 << a[1], INF]); });
    return out;
  }

  // guests: [{org, cat}]   -> sequence [{i, c, s}]
  function prep(guests, p) {
    var tk = {}; p.togCats.forEach(function (c) { tk[c] = 1; });
    var rank = {}; p.order.forEach(function (c, i) { rank[c] = i; });
    var R = p.order.length, members = new Map();
    guests.forEach(function (g, i) {
      var key = tk[g.cat] ? "c" + g.cat : (p.togCompany && g.org !== null ? "o" + g.org : "g" + i);
      if (!members.has(key)) members.set(key, []);
      members.get(key).push(i);
    });
    var units = [];
    members.forEach(function (ms) {
      var c = guests[ms[0]].cat;
      units.push({ r: (c in rank) ? rank[c] : R, first: ms[0], ms: ms, c: c });
    });
    units.sort(function (a, b) { return a.r - b.r || a.first - b.first; });
    // `pair X Y`: every unit holding a guest who matches X or Y is merged into one unit (union-find); the merged unit
    // sits at its earliest part's position, members = parts in position order (genome/hero6/lang6.py prep)
    if (p.pairs && p.pairs.length) {
      var par = units.map(function (u, k) { return k; });
      var find = function (x) { while (par[x] !== x) { par[x] = par[par[x]]; x = par[x]; } return x; };
      p.pairs.forEach(function (pr) {
        var hit = [];
        units.forEach(function (u, k) { if (u.ms.some(function (i) { return isWho(guests[i], pr[0]) || isWho(guests[i], pr[1]); })) hit.push(k); });
        for (var h = 1; h < hit.length; h++) { var a = find(hit[0]), b = find(hit[h]); if (a !== b) par[Math.max(a, b)] = Math.min(a, b); }
      });
      var groups = new Map();
      units.forEach(function (u, k) { var r0 = find(k); if (!groups.has(r0)) groups.set(r0, []); groups.get(r0).push(k); });
      var roots = Array.from(groups.keys()).sort(function (a, b) { return a - b; });
      units = roots.map(function (r0) { var ms = []; groups.get(r0).forEach(function (k) { ms = ms.concat(units[k].ms); }); return { ms: ms }; });
    }
    var seq = [];
    units.forEach(function (u) { u.ms.forEach(function (i, j) { seq.push({ i: i, c: guests[i].cat, s: j === 0 ? u.ms.length : 0 }); }); });
    return seq;
  }

  function refSections(cap, rl, elems, breaks) {
    var S = rl.map(function (r) { return [r[0], r[1], r[2], 0, 0]; });
    var sec = 0, size = 0, out = [];
    elems.forEach(function (e, idx) {
      var c = e.c, t = e.s > 0 ? e.s : 1, ok = size + t <= cap && !(breaks && breaks.indexOf(idx) >= 0);
      var ia = S.map(function (r) { return (r[0] >> c) & 1; }), ib = S.map(function (r) { return (r[1] >> c) & 1; });
      S.forEach(function (r, j) { if ((ia[j] && (r[3] + t > r[2] || r[4] > 0)) || (ib[j] && r[3] > 0)) ok = false; });
      if (!ok) { if (size > 0) sec++; size = 0; S.forEach(function (r) { r[3] = r[4] = 0; }); }
      S.forEach(function (r, j) { r[3] += ia[j]; r[4] += ib[j]; });
      size++; out.push(sec);
    });
    return out;
  }

  // `avoid A B` (Python reference: genome/hero6/lang6.py; verified tag-mask net: genome/hero6/sectioner6.py): A and B name a guest or a company, spaces as _.
  function key(x) { return x === null || x === undefined ? "" : String(x).replace(/[\s,]+/g, "_"); }
  function isWho(g, who) { return key(g.name) === who || key(g.org) === who; }
  function avoidSections(cap, rl, seq, guests, avoids, breaks) {
    var S = rl.map(function (r) { return [r[0], r[1], r[2], 0, 0]; }), A = avoids.map(function () { return [false, false]; });
    var sec = 0, size = 0, out = [];
    seq.forEach(function (e, idx) {
      var c = e.c, t = e.s > 0 ? e.s : 1, ok = size + t <= cap && !(breaks && breaks.indexOf(idx) >= 0);
      var ia = S.map(function (r) { return (r[0] >> c) & 1; }), ib = S.map(function (r) { return (r[1] >> c) & 1; });
      S.forEach(function (r, j) { if ((ia[j] && (r[3] + t > r[2] || r[4] > 0)) || (ib[j] && r[3] > 0)) ok = false; });
      var mem = e.s > 0 ? seq.slice(idx, idx + e.s).map(function (x) { return guests[x.i]; }) : [guests[e.i]];
      avoids.forEach(function (a, j) {
        var ua = mem.some(function (g) { return isWho(g, a[0]); }), ub = mem.some(function (g) { return isWho(g, a[1]); });
        if ((ua && A[j][1]) || (ub && A[j][0])) ok = false;
      });
      if (!ok) { if (size > 0) sec++; size = 0; S.forEach(function (r) { r[3] = r[4] = 0; }); A.forEach(function (x) { x[0] = x[1] = false; }); }
      S.forEach(function (r, j) { r[3] += ia[j]; r[4] += ib[j]; });
      avoids.forEach(function (a, j) { if (isWho(guests[e.i], a[0])) A[j][0] = true; if (isWho(guests[e.i], a[1])) A[j][1] = true; });
      size++; out.push(sec);
    });
    return out;
  }

  // page layout only (not in the Python reference): `breaks` are seat positions where the table itself ends a section
  // (the hosts' chairs, the foot of the table). Units are moved forward just enough that none straddles a break;
  // null if no such order exists. Without `breaks`, seat() is exactly the reference.
  function fitRuns(seq, breaks) {
    var units = [], out = [], pos = 0, b = 0;
    for (var i = 0; i < seq.length; i += seq[i].s) units.push(seq.slice(i, i + seq[i].s));
    while (units.length) {
      while (b < breaks.length && breaks[b] <= pos) b++;
      var room = b < breaks.length ? breaks[b] - pos : Infinity, j = 0;
      while (j < units.length && units[j].length > room) j++;
      if (j === units.length) return null;
      var u = units.splice(j, 1)[0]; out = out.concat(u); pos += u.length;
    }
    return out;
  }

  // -> {seq: guest indices in seating order, assign: section per guest}
  function seat(guests, p, breaks) {
    var seq = prep(guests, p);
    if (breaks) { var fit = fitRuns(seq, breaks); if (fit) seq = fit; else breaks = null; }
    var secs = (p.avoids && p.avoids.length) ? avoidSections(p.cap, rules(p), seq, guests, p.avoids, breaks)
      : refSections(p.cap, rules(p), seq.map(function (e) { return { c: e.c, s: e.s }; }), breaks);
    var assign = new Array(guests.length);
    seq.forEach(function (e, k) { assign[e.i] = secs[k]; });
    return { seq: seq.map(function (e) { return e.i; }), assign: assign };
  }

  function maxFit(p, c) { var m = p.cap; p.limits.forEach(function (l) { if (l[0].indexOf(c) >= 0) m = Math.min(m, l[1]); }); return m; }

  function violations(guests, p, assign) {
    var n = guests.length, secs = new Map();
    assign.forEach(function (s, i) { if (!secs.has(s)) secs.set(s, []); secs.get(s).push(i); });
    var v = { cap: 0, limit: 0, apart: 0, avoid: 0, pair: 0, together: 0, order: 0 }, bad = new Set();
    secs.forEach(function (ms, s) {
      var before = v.cap + v.limit + v.apart + v.avoid;
      v.cap += Math.max(0, ms.length - p.cap);
      var cc = {}; ms.forEach(function (i) { cc[guests[i].cat] = (cc[guests[i].cat] || 0) + 1; });
      p.limits.forEach(function (l) { var t = 0; l[0].forEach(function (c) { t += cc[c] || 0; }); v.limit += Math.max(0, t - l[1]); });
      p.aparts.forEach(function (a) { v.apart += (cc[a[0]] || 0) * (cc[a[1]] || 0); });
      (p.avoids || []).forEach(function (a) { var na = 0, nb = 0, both = 0; ms.forEach(function (i) { var x = isWho(guests[i], a[0]), y = isWho(guests[i], a[1]); if (x) na++; if (y) nb++; if (x && y) both++; }); v.avoid += na * nb - both; });
      if (v.cap + v.limit + v.apart + v.avoid > before) bad.add(s);
    });
    var units = new Map(), tk = {}; p.togCats.forEach(function (c) { tk[c] = 1; });
    guests.forEach(function (g, i) {
      var key = tk[g.cat] ? "c" + g.cat : (p.togCompany && g.org !== null ? "o" + g.org : null);
      if (key !== null) { if (!units.has(key)) units.set(key, []); units.get(key).push(i); }
    });
    units.forEach(function (ms) {
      var c = guests[ms[0]].cat, mf = maxFit(p, c), sp = new Set(ms.map(function (i) { return assign[i]; })).size;
      v.together += Math.max(0, sp - Math.ceil(ms.length / mf));
    });
    if (p.order.length) {
      var rank = {}; p.order.forEach(function (c, i) { rank[c] = i; });
      var R = p.order.length, rk = guests.map(function (g) { return (g.cat in rank) ? rank[g.cat] : R; });
      for (var g = 0; g < n; g++) for (var h = 0; h < n; h++) if (rk[g] < rk[h] && assign[h] < assign[g]) v.order++;
    }
    // pair: (x matches X, y matches Y, x != y) seated in different sections
    (p.pairs || []).forEach(function (a) {
      for (var x = 0; x < n; x++) if (isWho(guests[x], a[0])) for (var y = 0; y < n; y++) if (y !== x && isWho(guests[y], a[1]) && assign[x] !== assign[y]) v.pair++;
    });
    v.total = v.cap + v.limit + v.apart + v.avoid + v.pair + v.together + v.order;
    return { v: v, badSections: bad };
  }

  // the chart as posted: guests indexed left rows 0..16 then right rows 0..16; walk = left 0..16, right 16..0
  function walkGuest(k, n) { var half = n / 2; return k < half ? k : (k < 2 * half ? half + (2 * half - 1 - k) : k); }
  function postedAssignment(n, cap) { var a = new Array(n); for (var k = 0; k < n; k++) a[walkGuest(k, n)] = Math.floor(k / cap); return a; }

  return { CATS: CATS, CID: CID, parse: parse, toText: toText, seat: seat, violations: violations, postedAssignment: postedAssignment,
           walkGuest: walkGuest, emptyPolicy: emptyPolicy, MAXCAP: MAXCAP, isWho: isWho };
})();
if (typeof module !== "undefined") module.exports = Seating;
