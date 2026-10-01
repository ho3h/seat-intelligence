// GENOME TRACE: provenance ("taint") state. Taint sets are bitsets over input facts, hash-consed.
// Sets are per PORT SLOT (node aux slot, wire substitution, redex end), never stored in the 32-bit port itself.
use std::collections::HashMap;

pub struct Tr {
  pub mode: u8,               // 1 = data provenance, 2 = full (data + control) provenance
  pub w: usize,               // words per set
  pub arena: Vec<u64>,        // set id -> w words
  pub map: HashMap<Vec<u64>, u32>,
  pub memo: HashMap<u64, u32>,
  pub singles: Vec<u32>,      // fact id -> set id (0 = not made yet)
  pub nt: Vec<[u32; 2]>,      // taint of each node's two aux slots
  pub vt: Vec<u32>,           // taint of the port stored in each wire
  pub fact_of_def: Vec<i32>,  // def id -> fact id or -1
  pub n_union: u64,
  pub n_memo_hit: u64,
}

impl Tr {
  pub fn new() -> Self {
    let mode: u8 = std::env::var("GENOME_TR").ok().and_then(|s| s.parse().ok()).unwrap_or(2);
    let nf: usize = std::env::var("GENOME_TR_F").ok().and_then(|s| s.parse().ok()).unwrap_or(64);
    let w = ((nf + 63) / 64).max(1);
    let mut t = Tr {
      mode, w,
      arena: vec![0u64; w],
      map: HashMap::new(),
      memo: HashMap::new(),
      singles: vec![0u32; nf.max(1)],
      nt: vec![[0u32; 2]; 1usize << 29],
      vt: vec![0u32; 1usize << 29],
      fact_of_def: Vec::new(),
      n_union: 0, n_memo_hit: 0,
    };
    t.map.insert(vec![0u64; w], 0);
    t
  }

  fn intern(&mut self, v: Vec<u64>) -> u32 {
    if let Some(&i) = self.map.get(&v) { return i; }
    let id = (self.arena.len() / self.w) as u32;
    self.arena.extend_from_slice(&v);
    self.map.insert(v, id);
    id
  }

  pub fn sing(&mut self, k: usize) -> u32 {
    if k >= self.singles.len() { self.singles.resize(k + 1, 0); }
    if self.singles[k] != 0 { return self.singles[k]; }
    let need = (k / 64) + 1;
    if need > self.w { panic!("fact id {} exceeds GENOME_TR_F", k); }
    let mut v = vec![0u64; self.w];
    v[k / 64] |= 1u64 << (k % 64);
    let id = self.intern(v);
    self.singles[k] = id;
    id
  }

  pub fn un(&mut self, a: u32, b: u32) -> u32 {
    if a == b || b == 0 { return a; }
    if a == 0 { return b; }
    let (x, y) = if a < b { (a, b) } else { (b, a) };
    let key = ((x as u64) << 32) | y as u64;
    self.n_union += 1;
    if let Some(&r) = self.memo.get(&key) { self.n_memo_hit += 1; return r; }
    let w = self.w;
    let (ax, ay) = (x as usize * w, y as usize * w);
    let mut v = vec![0u64; w];
    let (mut eqx, mut eqy) = (true, true);
    for i in 0..w {
      let xs = self.arena[ax + i]; let ys = self.arena[ay + i];
      let s = xs | ys; v[i] = s;
      if s != xs { eqx = false; }
      if s != ys { eqy = false; }
    }
    let r = if eqx { x } else if eqy { y } else { self.intern(v) };
    self.memo.insert(key, r);
    r
  }

  pub fn members(&self, id: u32) -> Vec<usize> {
    let mut out = Vec::new();
    let base = id as usize * self.w;
    for i in 0..self.w {
      let mut x = self.arena[base + i];
      while x != 0 { let b = x.trailing_zeros() as usize; out.push(i * 64 + b); x &= x - 1; }
    }
    out
  }

  pub fn nsets(&self) -> usize { self.arena.len() / self.w }
}
