import { rm } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
for (const directory of ["node_modules", ".npm-cache", ".render-tmp", ".inspect-tmp"]) {
  await rm(resolve(root, directory), { recursive: true, force: true });
}

console.log("Removed temporary dependencies, caches, and inspection frames.");
