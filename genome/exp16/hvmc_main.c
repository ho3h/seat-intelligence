// Native arm64 wall-clock path that does NOT compile the input into C (swing 20).
// It includes HVM2's own runtime source unmodified (physics/hvm2/src/hvm.c, INTERPRETED mode, no IO) and loads the book
// from a file holding exactly the buffer that `hvm run-c` would pass to hvm_c() (Book::to_buffer, extracted from gen-c's
// BOOK_BUF). The runtime is compiled once; every input is data. Build:
//   clang -O3 -mcpu=native -DTPC_L2=3 -I physics/hvm2/src -o runs/exp16/hvmc_arm64 genome/exp16/hvmc_main.c -lpthread -lm
#include "hvm.c"

int main(int argc, char** argv) {
  if (argc < 2) { fprintf(stderr, "usage: hvmc_arm64 book.bin\n"); return 2; }
  FILE* f = fopen(argv[1], "rb");
  if (!f) { perror("open"); return 2; }
  fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET);
  u32* buf = (u32*)malloc(sz + 8);
  if (fread(buf, 1, sz, f) != (size_t)sz) { perror("read"); return 2; }
  fclose(f);
  hvm_c(buf);
  free(buf);
  return 0;
}
