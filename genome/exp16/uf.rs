// Hand-written union-find baseline (swing 20): accepted edges (s >= tau), canonical id = largest member.
// Input on stdin: "n tau m" then m lines "u v s". Prints "secs <t>" (union + canon only) and "canon <sum-hash>".
use std::io::Read;
fn find(p: &mut Vec<u32>, mut x: u32) -> u32 {
    while p[x as usize] != x { let g = p[p[x as usize] as usize]; p[x as usize] = g; x = g; }
    x
}
fn main() {
    let mut s = String::new(); std::io::stdin().read_to_string(&mut s).unwrap();
    let v: Vec<u64> = s.split_ascii_whitespace().map(|t| t.parse().unwrap()).collect();
    let (n, tau, m) = (v[0] as usize, v[1], v[2] as usize);
    let t = std::time::Instant::now();
    let mut reps = 0u32; let mut h = 0u64;
    let mut canon = vec![0u32; n];
    for _ in 0..REPS {
        let mut p: Vec<u32> = (0..n as u32).collect();
        for i in 0..m {
            let (a, b, sc) = (v[3 + 3 * i] as u32, v[4 + 3 * i] as u32, v[5 + 3 * i]);
            if sc < tau { continue; }
            let (ra, rb) = (find(&mut p, a), find(&mut p, b));
            if ra != rb { if ra < rb { p[ra as usize] = rb } else { p[rb as usize] = ra } }
        }
        // union by larger id keeps the root = largest member
        for i in 0..n { canon[i] = find(&mut p, i as u32); }
        reps += 1;
    }
    let secs = t.elapsed().as_secs_f64() / reps as f64;
    for (i, c) in canon.iter().enumerate() { h = h.wrapping_mul(1_000_003).wrapping_add(*c as u64 ^ i as u64); }
    println!("secs {:.9}\ncanon {}", secs, h);
}
const REPS: usize = 20;
