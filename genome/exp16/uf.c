// Hand-written union-find baseline in C (native arm64), same contract as uf.rs.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
static uint32_t find(uint32_t* p, uint32_t x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }
int main() {
  long n, tau, m; if (scanf("%ld %ld %ld", &n, &tau, &m) != 3) return 1;
  uint32_t *E = malloc(sizeof(uint32_t) * 3 * m);
  for (long i = 0; i < 3 * m; i++) { long x; if (scanf("%ld", &x) != 1) return 1; E[i] = (uint32_t)x; }
  uint32_t *p = malloc(4 * n), *canon = malloc(4 * n);
  const int REPS = 20; struct timespec a, b; clock_gettime(CLOCK_MONOTONIC, &a);
  for (int r = 0; r < REPS; r++) {
    for (long i = 0; i < n; i++) p[i] = i;
    for (long i = 0; i < m; i++) {
      if (E[3*i+2] < tau) continue;
      uint32_t ra = find(p, E[3*i]), rb = find(p, E[3*i+1]);
      if (ra != rb) { if (ra < rb) p[ra] = rb; else p[rb] = ra; }
    }
    for (long i = 0; i < n; i++) canon[i] = find(p, i);
  }
  clock_gettime(CLOCK_MONOTONIC, &b);
  uint64_t h = 0; for (long i = 0; i < n; i++) h = h * 1000003ull + (canon[i] ^ (uint64_t)i);
  printf("secs %.9f\ncanon %llu\n", ((b.tv_sec - a.tv_sec) + (b.tv_nsec - a.tv_nsec) / 1e9) / REPS, (unsigned long long)h);
  return 0;
}
