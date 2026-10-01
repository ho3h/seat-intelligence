#![allow(dead_code)]
#![allow(unused_imports)]
#![allow(unused_variables)]

use clap::{Arg, ArgAction, Command};
use ::hvm::{ast, cmp, hvm};
use std::fs;
use std::io::Write;
use std::path::PathBuf;
use std::process::Command as SysCommand;

#[cfg(feature = "c")]
extern "C" {
  fn hvm_c(book_buffer: *const u32);
}

#[cfg(feature = "cuda")]
extern "C" {
  fn hvm_cu(book_buffer: *const u32);
}

fn main() {
  let matches = Command::new("hvm")
    .about("HVM2: Higher-order Virtual Machine 2 (32-bit Version)")
    .version(env!("CARGO_PKG_VERSION"))
    .subcommand_required(true)
    .arg_required_else_help(true)
    .subcommand(
      Command::new("run")
        .about("Interprets a file (using Rust)")
        .arg(Arg::new("file").required(true)))
    .subcommand(
      Command::new("run-c")
        .about("Interprets a file (using C)")
        .arg(Arg::new("file").required(true))
        .arg(Arg::new("io")
          .long("io")
          .action(ArgAction::SetTrue)
          .help("Run with IO enabled"))
    )
    .subcommand(
      Command::new("run-cu")
        .about("Interprets a file (using CUDA)")
        .arg(Arg::new("file").required(true))
        .arg(Arg::new("io")
          .long("io")
          .action(ArgAction::SetTrue)
          .help("Run with IO enabled")))
    .subcommand(
      Command::new("gen-c")
        .about("Compiles a file with IO (to standalone C)")
        .arg(Arg::new("file").required(true))
        .arg(Arg::new("io")
          .long("io")
          .action(ArgAction::SetTrue)
          .help("Generate with IO enabled")))
    .subcommand(
      Command::new("gen-cu")
        .about("Compiles a file (to standalone CUDA)")
        .arg(Arg::new("file").required(true))
        .arg(Arg::new("io")
          .long("io")
          .action(ArgAction::SetTrue)
          .help("Generate with IO enabled")))
    .get_matches();

  match matches.subcommand() {
    Some(("run", sub_matches)) => {
      let file = sub_matches.get_one::<String>("file").expect("required");
      let code = fs::read_to_string(file).expect("Unable to read file");
      let book = ast::Book::parse(&code).unwrap_or_else(|er| panic!("{}",er)).build();
      run(&book);
    }
    Some(("run-c", sub_matches)) => {
      let file = sub_matches.get_one::<String>("file").expect("required");
      let code = fs::read_to_string(file).expect("Unable to read file");
      let book = ast::Book::parse(&code).unwrap_or_else(|er| panic!("{}",er)).build();
      let mut data : Vec<u8> = Vec::new();
      book.to_buffer(&mut data);
      #[cfg(feature = "c")]
      unsafe {
        hvm_c(data.as_mut_ptr() as *mut u32);
      }
      #[cfg(not(feature = "c"))]
      println!("C runtime not available!\n");
    }
    Some(("run-cu", sub_matches)) => {
      let file = sub_matches.get_one::<String>("file").expect("required");
      let code = fs::read_to_string(file).expect("Unable to read file");
      let book = ast::Book::parse(&code).unwrap_or_else(|er| panic!("{}",er)).build();
      let mut data : Vec<u8> = Vec::new();
      book.to_buffer(&mut data);
      #[cfg(feature = "cuda")]
      unsafe {
        hvm_cu(data.as_mut_ptr() as *mut u32);
      }
      #[cfg(not(feature = "cuda"))]
      println!("CUDA runtime not available!\n If you've installed CUDA and nvcc after HVM, please reinstall HVM.");
    }
    Some(("gen-c", sub_matches)) => {
      // Reads book from file
      let file = sub_matches.get_one::<String>("file").expect("required");
      let code = fs::read_to_string(file).expect("Unable to read file");
      let book = ast::Book::parse(&code).unwrap_or_else(|er| panic!("{}",er)).build();

      // Gets optimal core count
      let cores = num_cpus::get();
      let tpcl2 = (cores as f64).log2().floor() as u32;

      // Generates the interpreted book
      let mut book_buf : Vec<u8> = Vec::new();
      book.to_buffer(&mut book_buf);
      let bookb = format!("{:?}", book_buf).replace("[","{").replace("]","}");
      let bookb = format!("static const u8 BOOK_BUF[] = {};", bookb);

      // Generates the C file
      let hvm_c = include_str!("hvm.c");
      let hvm_c = format!("#define IO\n\n{hvm_c}");
      let hvm_c = hvm_c.replace("///COMPILED_INTERACT_CALL///", &cmp::compile_book(cmp::Target::C, &book));
      let hvm_c = hvm_c.replace("#define INTERPRETED", "#define COMPILED");
      let hvm_c = hvm_c.replace("//COMPILED_BOOK_BUF//", &bookb);
      let hvm_c = hvm_c.replace("#define WITHOUT_MAIN", "#define WITH_MAIN");
      let hvm_c = hvm_c.replace("#define TPC_L2 0", &format!("#define TPC_L2 {} // {} cores", tpcl2, cores));
      let hvm_c = format!("{hvm_c}\n\n{}", include_str!("run.c"));
      let hvm_c = hvm_c.replace(r#"#include "hvm.c""#, "");
      println!("{}", hvm_c);
    }
    Some(("gen-cu", sub_matches)) => {
      // Reads book from file
      let file = sub_matches.get_one::<String>("file").expect("required");
      let code = fs::read_to_string(file).expect("Unable to read file");
      let book = ast::Book::parse(&code).unwrap_or_else(|er| panic!("{}",er)).build();

      // Generates the interpreted book
      let mut book_buf : Vec<u8> = Vec::new();
      book.to_buffer(&mut book_buf);
      let bookb = format!("{:?}", book_buf).replace("[","{").replace("]","}");
      let bookb = format!("static const u8 BOOK_BUF[] = {};", bookb);

      //FIXME: currently, CUDA is faster on interpreted mode, so the compiler uses it.

      // Compile with compiled functions:
      //let hvm_c = include_str!("hvm.cu");
      //let hvm_c = hvm_c.replace("///COMPILED_INTERACT_CALL///", &cmp::compile_book(cmp::Target::CUDA, &book));
      //let hvm_c = hvm_c.replace("#define INTERPRETED", "#define COMPILED");
      
      // Generates the Cuda file
      let hvm_cu = include_str!("hvm.cu");
      let hvm_cu = format!("#define IO\n\n{hvm_cu}");
      let hvm_cu = hvm_cu.replace("//COMPILED_BOOK_BUF//", &bookb);
      let hvm_cu = hvm_cu.replace("#define WITHOUT_MAIN", "#define WITH_MAIN");
      let hvm_cu = format!("{hvm_cu}\n\n{}", include_str!("run.cu"));
      let hvm_cu = hvm_cu.replace(r#"#include "hvm.cu""#, "");
      println!("{}", hvm_cu);
    }
    _ => unreachable!(),
  }
}

pub fn run(book: &hvm::Book) {
  // Initializes the global net
  let net = hvm::GNet::new(1 << 29, 1 << 29);

  // Initializes threads
  let mut tm = hvm::TMem::new(0, 1);

  // GENOME TRACE: fact definitions are named fact_<k>
  tm.tr.fact_of_def = book.defs.iter().map(|d| {
    if let Some(r) = d.name.strip_prefix("fact_") { r.parse::<i32>().unwrap_or(-1) } else { -1 }
  }).collect();

  // Creates an initial redex that calls main
  let main_id = book.defs.iter().position(|def| def.name == "main").unwrap();
  tm.rbag.push_redex(hvm::Pair::new(hvm::Port::new(hvm::REF, main_id as u32), hvm::ROOT), 0, 0);
  net.vars_create(hvm::ROOT.get_val() as usize, hvm::NONE);

  // Starts the timer
  let start = std::time::Instant::now();

  // Evaluates
  let (rounds, width, work) = tm.evaluator_rounds(&net, &book);

  // Stops the timer
  let duration = start.elapsed();

  // Prints interactions and time
  let itrs = net.itrs.load(std::sync::atomic::Ordering::Relaxed);
  println!("- ITRS: {}", itrs);
  println!("- DEPTH: {}", rounds);
  println!("- WIDTH: {}", width);
  println!("- WORK: {}", work);
  println!("- TIME: {:.2}s", duration.as_secs_f64());
  println!("- MIPS: {:.2}", itrs as f64 / duration.as_secs_f64() / 1_000_000.0);
  println!("- TSETS: {}", tm.tr.nsets());
  println!("- TUNIONS: {}", tm.tr.n_union);
  println!("- TMEMOHITS: {}", tm.tr.n_memo_hit);
  println!("- TMEMOSIZE: {}", tm.tr.memo.len());
  println!("- TWORDS: {}", tm.tr.w);

  // Tainted readback (iterative; output is a preorder token stream)
  let mut out = String::new();
  let mut used: std::collections::BTreeSet<u32> = std::collections::BTreeSet::new();
  let rootidx = hvm::ROOT.get_val() as usize;
  let rp = net.vars_load(rootidx);
  let rt = tm.tr.vt[rootidx];
  let mut stack: Vec<(hvm::Port, u32)> = vec![(rp, rt)];
  while let Some((mut p, mut t)) = stack.pop() {
    let mut dead = false;
    while p.get_tag() == hvm::VAR {
      let v = net.vars_load(p.get_val() as usize);
      if v == hvm::NONE || v == hvm::Port(0) { dead = true; break; }
      t = tm.tr.un(t, tm.tr.vt[p.get_val() as usize]);
      p = v;
    }
    if dead { out.push_str("V "); continue; }
    used.insert(t);
    match p.get_tag() {
      hvm::NUM => { out.push_str(&format!("N{}:{} ", hvm::Numb(p.get_val()).get_u24(), t)); }
      hvm::ERA => { out.push_str(&format!("E:{} ", t)); }
      hvm::REF => { out.push_str(&format!("R{}:{} ", book.defs[(p.get_val() as usize) & 0xFFFFFFF].name, t)); }
      tag => {
        let c = match tag { hvm::CON => 'C', hvm::DUP => 'D', hvm::OPR => 'O', _ => 'S' };
        out.push_str(&format!("{}:{} ", c, t));
        let pr = net.node_load(p.get_val() as usize);
        let [t0, t1] = tm.tr.nt[p.get_val() as usize];
        stack.push((pr.get_snd(), t1));
        stack.push((pr.get_fst(), t0));
      }
    }
  }
  println!("TOKENS {}", out.trim_end());
  // taint sets referenced by the readback
  for id in used.iter() {
    let m = tm.tr.members(*id);
    println!("SET {} {}", id, m.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","));
  }
}
