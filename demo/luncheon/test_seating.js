const S = require("./seating.js"), fs = require("fs");
const cases = JSON.parse(fs.readFileSync(__dirname + "/cases.json"));
let bad = 0;
const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);
cases.forEach((c, k) => {
  const p = S.parse(c.prog), r = S.seat(c.guests, p), vv = S.violations(c.guests, p, r.assign);
  const ok = eq(r.assign, c.assign) && eq(r.seq, c.seq) && eq(S.toText(p), c.canon) &&
    Object.keys(c.v).every(f => vv.v[f] === c.v[f]) &&
    (c.posted === null || eq(S.postedAssignment(c.guests.length, p.cap), c.posted));
  if (!ok) { bad++; if (bad < 4) console.log("MISMATCH", k, c.prog); }
});
const nNamed = cases.filter(c => c.named).length, badNamed = cases.filter((c, k) => c.named && !(() => { const p = S.parse(c.prog), r = S.seat(c.guests, p); return eq(r.assign, c.assign) && eq(r.seq, c.seq) && eq(S.toText(p), c.canon); })()).length;
console.log("random cases:", cases.length - bad, "/", cases.length, "match the Python reference (of which with avoid/pair:", nNamed - badNamed, "/", nNamed + ")");
// the five recorded showcase sentences on the real chart
const real = JSON.parse(fs.readFileSync(__dirname + "/../../data/hero/luncheon.json")).seats;
const guests = real.map(s => ({ org: s.org, cat: S.CID[s.category] }));
const show = JSON.parse(fs.readFileSync(__dirname + "/../../runs/hero1/showcase.json")).showcase;
let sb = 0;
show.forEach(s => {
  const progs = [["emitted", s.emitted_program, s.assignment_by_guest, s.violations_of_stated_rules]];
  if (s.assignment_by_guest_if_gold_program) progs.push(["gold", s.gold_program, s.assignment_by_guest_if_gold_program, s.violations_of_stated_rules_if_gold_program]);
  progs.forEach(([tag, prog, expect]) => {
    const p = S.parse(prog), r = S.seat(guests, p);
    const mine = {}; real.forEach((g, i) => { mine[g.name] = r.assign[i]; });
    const same = eq(mine, expect);
    // the recorded posted count is scored against the STATED rules (the gold program when the model misread)
    const judge = S.parse(s.gold_program);
    const posted = S.violations(guests, judge, S.postedAssignment(34, p.cap)).v.total;
    const okPosted = tag === "emitted" ? posted === s.posted_arrangement_violation_count : true;
    if (!same || !okPosted) { sb++; console.log("SHOWCASE MISMATCH", s.id, tag, same, posted, s.posted_arrangement_violation_count); }
  });
});
console.log("showcase programs:", "all match the net-verified assignments and posted counts" , sb ? "(" + sb + " mismatches)" : "");
if (bad || sb) process.exit(1);
// `avoid` also against an independent brute-force count on random cases (the Python reference check is above)
{
  let bad2 = 0, R = 0;
  const rnd = (n) => Math.floor(Math.random() * n);
  for (let t = 0; t < 400; t++) {
    const n = 20 + rnd(20), g = [];
    for (let i = 0; i < n; i++) g.push({ org: rnd(3) ? "co" + rnd(6) : null, cat: rnd(7), name: "p" + i });
    const a = "p" + rnd(n), b = rnd(2) ? "co" + rnd(6) : "p" + rnd(n);
    if (a === b) continue;
    const prog = (rnd(2) ? "size " + (2 + rnd(5)) + "\n" : "") + (rnd(2) ? "together company\n" : "") + (rnd(2) ? "limit government 1\n" : "") + "avoid " + a + " " + b;
    const p = S.parse(prog), r = S.seat(g, p), vv = S.violations(g, p, r.assign);
    let cnt = 0; for (let x = 0; x < n; x++) for (let y = 0; y < n; y++) if (x !== y && S.isWho(g[x], a) && S.isWho(g[y], b) && r.assign[x] === r.assign[y]) cnt++;
    const bothInOneUnit = p.togCompany && g.some((gx, x) => S.isWho(gx, a) && gx.org && g.some((gy) => gy.org === gx.org && S.isWho(gy, b)));
    if (vv.v.avoid !== cnt || (!bothInOneUnit && cnt !== 0)) { bad2++; if (bad2 < 3) console.log("AVOID MISMATCH", prog, vv.v.avoid, cnt); }
    R++;
  }
  console.log("avoid cases:", R - bad2, "/", R, "count correctly and keep the pair apart");
  if (bad2) process.exit(1);
}
