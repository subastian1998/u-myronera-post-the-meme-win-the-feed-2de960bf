// Entry for make.fun's "Post the Meme, Win the Feed" (Node 22, standard
// library only). The entry is the X post itself: this program copies
// POST.json from the repository root to /output/POST.json, where the gate
// reads it. That is the scored part.
//
// Best-effort extra: it also regenerates the meme PNG deterministically
// (repo/meme.py -> /output/entry.png). The image is not scored; if the
// regeneration fails (e.g. no python3 here), the copy above has already
// succeeded and the program still exits 0.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(join(BOT_DIR, 'POST.json'), join(OUTPUT_DIR, 'POST.json'));
} catch (err) {
  console.error(`POST.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
try {
  execFileSync('python3', [join(BOT_DIR, 'meme.py'), join(OUTPUT_DIR, 'entry.png')],
    { stdio: 'pipe' });
} catch (err) {
  console.error(`meme.png regeneration skipped: ${(err as Error).message}`);
}
