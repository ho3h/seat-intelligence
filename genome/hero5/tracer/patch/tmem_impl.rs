impl TMem {
  pub fn new(tid: u32, tids: u32) -> Self {
    TMem {
      tid,
      tids,
      tick: 0,
      itrs: 0,
      nput: 0,
      vput: 0,
      nloc: vec![0; 0xFFF], // FIXME: move to a constant
      vloc: vec![0; 0xFFF],
      rbag: RBag::new(),
      tr: Tr::new(),
    }
  }

  pub fn node_alloc(&mut self, net: &GNet, num: usize) -> usize {
    let mut got = 0;
    for _ in 0..net.nlen {
      self.nput += 1; // index 0 reserved
      if self.nput < net.nlen-1 || net.is_node_free(self.nput % net.nlen) {
        self.nloc[got] = self.nput % net.nlen;
        got += 1;
      }
      if got >= num {
        break;
      }
    }
    return got
  }

  pub fn vars_alloc(&mut self, net: &GNet, num: usize) -> usize {
    let mut got = 0;
    for _ in 0..net.vlen {
      self.vput += 1; // index 0 reserved for FREE
      if self.vput < net.vlen-1 || net.is_vars_free(self.vput % net.vlen) {
        self.vloc[got] = self.vput % net.nlen;
        got += 1;
      }
      if got >= num {
        break;
      }
    }
    got
  }

  pub fn get_resources(&mut self, net: &GNet, _need_rbag: usize, need_node: usize, need_vars: usize) -> bool {
    let got_node = self.node_alloc(net, need_node);
    let got_vars = self.vars_alloc(net, need_vars);
    got_node >= need_node && got_vars >= need_vars
  }

  // GENOME TRACE: follow a chain of substituted wires, accumulating the taint stored on each hop.
  pub fn enter_t(&mut self, net: &GNet, mut var: Port, mut t: u32) -> (Port, u32) {
    while var.get_tag() == VAR {
      let idx = var.get_val() as usize;
      let val = net.vars_exchange(idx, NONE);
      if val == NONE || val == Port(0) {
        break;
      }
      let tv = self.tr.vt[idx];
      net.vars_take(idx);
      t = self.tr.un(t, tv);
      var = val;
    }
    (var, t)
  }

  // Atomically Links `A ~ B`; ta/tb are the taints of the agents (or wires) at each end.
  pub fn link(&mut self, net: &GNet, a: Port, ta: u32, b: Port, tb: u32) {
    let (mut a, mut ta, mut b, mut tb) = (a, ta, b, tb);
    loop {
      if a.get_tag() != VAR && b.get_tag() == VAR {
        std::mem::swap(&mut a, &mut b);
        std::mem::swap(&mut ta, &mut tb);
      }
      if a.get_tag() != VAR {
        self.rbag.push_redex(Pair::new(a, b), ta, tb);
        break;
      }
      let (nb, ntb) = self.enter_t(net, b, tb);
      b = nb; tb = ntb;
      let idx = a.get_val() as usize;
      let a_ = net.vars_exchange(idx, b);
      if a_ == NONE {
        self.tr.vt[idx] = self.tr.un(tb, ta);
        break;
      }
      let told = self.tr.vt[idx];
      net.vars_take(idx);
      a = a_;
      ta = self.tr.un(told, ta);
    }
  }

  // taint of a static port of a definition being instantiated with base taint `bt`
  fn dtaint(&mut self, p: Port, bt: u32) -> u32 {
    match p.get_tag() {
      VAR => 0,
      REF => {
        let fid = (p.get_val() as usize) & 0xFFFFFFF;
        let k = self.tr.fact_of_def[fid];
        if k >= 0 { let s = self.tr.sing(k as usize); self.tr.un(bt, s) } else { bt }
      }
      _ => bt,
    }
  }

  pub fn interact_link(&mut self, net: &GNet, a: Port, ta: u32, b: Port, tb: u32) -> bool {
    if !self.get_resources(net, 1, 0, 0) {
      return false;
    }
    self.link(net, a, ta, b, tb);
    true
  }

  pub fn interact_call(&mut self, net: &GNet, a: Port, ta: u32, b: Port, tb: u32, book: &Book) -> bool {
    let fid = (a.get_val() as usize) & 0xFFFFFFF;
    let def = &book.defs[fid];

    if b.get_tag() == DUP {
      if def.safe {
        return self.interact_eras(net, a, ta, b, tb);
      } else {
        println!("ERROR: attempt to clone a non-affine global reference.\n");
        std::process::exit(0);
      }
    }

    if !self.get_resources(net, def.rbag.len() + 1, def.node.len(), def.vars as usize) {
      return false;
    }

    for i in 0..def.vars {
      net.vars_create(self.vloc[i], NONE);
    }

    // base taint of everything this call instantiates
    let mut bt = ta;
    let k = self.tr.fact_of_def[fid];
    if k >= 0 { let s = self.tr.sing(k as usize); bt = self.tr.un(bt, s); }

    for i in 0..def.node.len() {
      net.node_create(self.nloc[i], def.node[i].adjust_pair(self));
      let t0 = self.dtaint(def.node[i].get_fst(), bt);
      let t1 = self.dtaint(def.node[i].get_snd(), bt);
      let loc = self.nloc[i];
      self.tr.nt[loc] = [t0, t1];
    }

    for pair in &def.rbag {
      let adj = pair.adjust_pair(self);
      let t0 = self.dtaint(pair.get_fst(), bt);
      let t1 = self.dtaint(pair.get_snd(), bt);
      self.link(net, adj.get_fst(), t0, adj.get_snd(), t1);
    }
    let rt = self.dtaint(def.root, bt);
    let rootp = def.root.adjust_port(self);
    self.link(net, rootp, rt, b, tb);

    true
  }

  pub fn interact_void(&mut self, _net: &GNet, _a: Port, _b: Port) -> bool {
    true
  }

  // ERA / NUM / REF (a) against a node (b): a is copied onto both aux ports (ERA copies carry no provenance).
  pub fn interact_eras(&mut self, net: &GNet, a: Port, ta: u32, b: Port, tb: u32) -> bool {
    if !self.get_resources(net, 2, 0, 0) {
      return false;
    }
    if net.node_load(b.get_val() as usize).0 == 0 {
      return false;
    }
    let b_ = net.node_exchange(b.get_val() as usize, Pair(0));
    let b1 = b_.get_fst();
    let b2 = b_.get_snd();
    let [tb1, tb2] = self.tr.nt[b.get_val() as usize];
    let tc = if a.get_tag() == ERA { 0 } else if self.tr.mode == 2 { self.tr.un(ta, tb) } else { ta };
    self.link(net, a, tc, b1, tb1);
    self.link(net, a, tc, b2, tb2);
    true
  }

  pub fn interact_anni(&mut self, net: &GNet, a: Port, ta: u32, b: Port, tb: u32) -> bool {
    if !self.get_resources(net, 2, 0, 0) {
      return false;
    }
    if net.node_load(a.get_val() as usize).0 == 0 || net.node_load(b.get_val() as usize).0 == 0 {
      return false;
    }
    let a_ = net.node_take(a.get_val() as usize);
    let a1 = a_.get_fst();
    let a2 = a_.get_snd();
    let [ta1, ta2] = self.tr.nt[a.get_val() as usize];
    let b_ = net.node_take(b.get_val() as usize);
    let b1 = b_.get_fst();
    let b2 = b_.get_snd();
    let [tb1, tb2] = self.tr.nt[b.get_val() as usize];
    let t = if self.tr.mode == 2 { self.tr.un(ta, tb) } else { 0 };
    let (ta1, ta2, tb1, tb2) = if t != 0 {
      (self.tr.un(ta1, t), self.tr.un(ta2, t), self.tr.un(tb1, t), self.tr.un(tb2, t))
    } else { (ta1, ta2, tb1, tb2) };
    self.link(net, a1, ta1, b1, tb1);
    self.link(net, a2, ta2, b2, tb2);
    true
  }

  pub fn interact_comm(&mut self, net: &GNet, a: Port, ta: u32, b: Port, tb: u32) -> bool {
    if !self.get_resources(net, 4, 4, 4) {
      return false;
    }
    if net.node_load(a.get_val() as usize).0 == 0 || net.node_load(b.get_val() as usize).0 == 0 {
      return false;
    }
    let a_ = net.node_take(a.get_val() as usize);
    let a1 = a_.get_fst();
    let a2 = a_.get_snd();
    let [ta1, ta2] = self.tr.nt[a.get_val() as usize];
    let b_ = net.node_take(b.get_val() as usize);
    let b1 = b_.get_fst();
    let b2 = b_.get_snd();
    let [tb1, tb2] = self.tr.nt[b.get_val() as usize];

    net.vars_create(self.vloc[0], NONE);
    net.vars_create(self.vloc[1], NONE);
    net.vars_create(self.vloc[2], NONE);
    net.vars_create(self.vloc[3], NONE);

    net.node_create(self.nloc[0], Pair::new(Port::new(VAR, self.vloc[0] as u32), Port::new(VAR, self.vloc[1] as u32)));
    net.node_create(self.nloc[1], Pair::new(Port::new(VAR, self.vloc[2] as u32), Port::new(VAR, self.vloc[3] as u32)));
    net.node_create(self.nloc[2], Pair::new(Port::new(VAR, self.vloc[0] as u32), Port::new(VAR, self.vloc[2] as u32)));
    net.node_create(self.nloc[3], Pair::new(Port::new(VAR, self.vloc[1] as u32), Port::new(VAR, self.vloc[3] as u32)));
    for i in 0..4 { let l = self.nloc[i]; self.tr.nt[l] = [0, 0]; }

    let (tcb, tca) = if self.tr.mode == 2 { let t = self.tr.un(ta, tb); (t, t) } else { (tb, ta) };
    let (n0, n1, n2, n3) = (self.nloc[0], self.nloc[1], self.nloc[2], self.nloc[3]);
    self.link(net, Port::new(b.get_tag(), n0 as u32), tcb, a1, ta1);
    self.link(net, Port::new(b.get_tag(), n1 as u32), tcb, a2, ta2);
    self.link(net, Port::new(a.get_tag(), n2 as u32), tca, b1, tb1);
    self.link(net, Port::new(a.get_tag(), n3 as u32), tca, b2, tb2);
    true
  }

  pub fn interact_oper(&mut self, net: &GNet, a: Port, ta: u32, b: Port, tb: u32) -> bool {
    if !self.get_resources(net, 1, 1, 0) {
      return false;
    }
    if net.node_load(b.get_val() as usize).0 == 0 {
      return false;
    }
    assert_eq!(a.get_tag(), NUM);
    let av = a.get_val();
    let b_ = net.node_take(b.get_val() as usize);
    let b1 = b_.get_fst();
    let [tb1, tb2] = self.tr.nt[b.get_val() as usize];
    let (b2, tb2) = self.enter_t(net, b_.get_snd(), tb2);

    if b1.get_tag() == NUM {
      let bv = b1.get_val();
      let cv = Numb::operate(Numb(av), Numb(bv));
      let mut tr = self.tr.un(ta, tb1);
      if self.tr.mode == 2 { tr = self.tr.un(tr, tb); }
      self.link(net, Port::new(NUM, cv.0), tr, b2, tb2);
    } else {
      net.node_create(self.nloc[0], Pair::new(Port::new(a.get_tag(), Numb(a.get_val()).0), b2));
      let loc = self.nloc[0];
      self.tr.nt[loc] = [ta, tb2];
      let tnew = if self.tr.mode == 2 { self.tr.un(ta, tb) } else { 0 };
      self.link(net, b1, tb1, Port::new(OPR, loc as u32), tnew);
    }
    true
  }

  pub fn interact_swit(&mut self, net: &GNet, a: Port, ta: u32, b: Port, tb: u32) -> bool {
    if !self.get_resources(net, 1, 2, 0) {
      return false;
    }
    if net.node_load(b.get_val() as usize).0 == 0 {
      return false;
    }
    let av = Numb(a.get_val()).get_u24();
    let b_ = net.node_take(b.get_val() as usize);
    let b1 = b_.get_fst();
    let b2 = b_.get_snd();
    let [tb1, tb2] = self.tr.nt[b.get_val() as usize];
    let full = self.tr.mode == 2;
    let t = if full { self.tr.un(ta, tb) } else { 0 };

    if av == 0 {
      net.node_create(self.nloc[0], Pair::new(b2, Port::new(ERA,0)));
      let loc = self.nloc[0];
      self.tr.nt[loc] = [tb2, 0];
      self.link(net, Port::new(CON, loc as u32), t, b1, tb1);
    } else {
      net.node_create(self.nloc[0], Pair::new(Port::new(ERA,0), Port::new(CON, self.nloc[1] as u32)));
      net.node_create(self.nloc[1], Pair::new(Port::new(NUM, Numb::new_u24(av-1).0), b2));
      let (l0, l1) = (self.nloc[0], self.nloc[1]);
      let tnum = if full { t } else { ta };
      self.tr.nt[l0] = [0, t];
      self.tr.nt[l1] = [tnum, tb2];
      self.link(net, Port::new(CON, l0 as u32), t, b1, tb1);
    }
    true
  }

  // Pops a local redex and performs a single interaction.
  pub fn interact(&mut self, net: &GNet, book: &Book) -> bool {
    let (redex, mut ta, mut tb) = match self.rbag.pop_redex() {
      Some(r) => r,
      None => return true,
    };

    let mut a = redex.get_fst();
    let mut b = redex.get_snd();
    let mut rule = Port::get_rule(a, b);

    if a.get_tag() == REF && b == ROOT {
      rule = CALL;
    } else if Port::should_swap(a,b) {
      std::mem::swap(&mut a, &mut b);
      std::mem::swap(&mut ta, &mut tb);
    }

    let success = match rule {
      LINK => self.interact_link(net, a, ta, b, tb),
      CALL => self.interact_call(net, a, ta, b, tb, book),
      VOID => self.interact_void(net, a, b),
      ERAS => self.interact_eras(net, a, ta, b, tb),
      ANNI => self.interact_anni(net, a, ta, b, tb),
      COMM => self.interact_comm(net, a, ta, b, tb),
      OPER => self.interact_oper(net, a, ta, b, tb),
      SWIT => self.interact_swit(net, a, ta, b, tb),
      _    => panic!("Invalid rule"),
    };

    if !success {
      self.rbag.push_redex(redex, ta, tb);
      false
    } else if rule != LINK {
      self.itrs += 1;
      true
    } else {
      true
    }
  }

  // GENOME INSTRUMENT (unchanged scheduler): fires every currently ready redex once per round.
  pub fn evaluator_rounds(&mut self, net: &GNet, book: &Book) -> (u64, u64, u64) {
    let mut rounds: u64 = 0;
    let mut max_width: u64 = 0;
    let mut work: u64 = 0;
    let mut batch: Vec<(Pair,u32,u32)> = Vec::new();
    batch.extend(self.rbag.hi.drain(..));
    batch.extend(self.rbag.lo.drain(..));
    while !batch.is_empty() {
      let mut next: Vec<(Pair,u32,u32)> = Vec::new();
      let mut real = 0u64;
      for r in batch {
        let mut stack: Vec<(Pair,u32,u32)> = vec![r];
        while let Some(x) = stack.pop() {
          let is_link = Port::get_rule(x.0.get_fst(), x.0.get_snd()) == LINK;
          self.rbag.hi.clear(); self.rbag.lo.clear();
          self.rbag.push_redex(x.0, x.1, x.2);
          if !self.interact(net, book) { panic!("resource exhaustion in depth oracle"); }
          if !is_link { real += 1; }
          let made: Vec<(Pair,u32,u32)> = self.rbag.hi.drain(..).chain(self.rbag.lo.drain(..)).collect();
          for y in made {
            if Port::get_rule(y.0.get_fst(), y.0.get_snd()) == LINK { stack.push(y); } else { next.push(y); }
          }
        }
      }
      if real > 0 { rounds += 1; work += real; if real > max_width { max_width = real; } }
      batch = next;
    }
    net.itrs.fetch_add(self.itrs as u64, Ordering::Relaxed);
    self.itrs = 0;
    (rounds, max_width, work)
  }

