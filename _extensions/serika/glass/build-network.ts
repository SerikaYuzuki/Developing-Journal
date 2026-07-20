// Build a lightweight knowledge graph from Quarto source files.
// Run as a Quarto post-render script so a single-page preview stays incremental.

type NodeRecord = {
  id: string;
  href: string;
  title: string;
  description: string;
  categories: string[];
  section: string;
  date: string;
};

type EdgeRecord = {
  source: string;
  target: string;
  type: "link" | "related";
  weight: number;
};

const root = Deno.cwd();
const outputDir = Deno.env.get("QUARTO_PROJECT_OUTPUT_DIR") || "_site";
const outputRoot = outputDir.startsWith("/") ? outputDir : `${root}/${outputDir}`;
const excludedDirectories = new Set([
  ".git", ".quarto", ".venv", "node_modules", "renv", outputDir.split(/[\\/]/).filter(Boolean).pop() || "_site",
  "_extensions", "_freeze", "_templates",
]);

function posixPath(value: string): string {
  return value.replaceAll("\\", "/").replace(/^\.\//, "");
}

async function collectQmdFiles(directory: string, relative = ""): Promise<string[]> {
  const files: string[] = [];
  for await (const entry of Deno.readDir(directory)) {
    if (entry.name.startsWith(".") || excludedDirectories.has(entry.name)) continue;
    const nextRelative = posixPath(relative ? `${relative}/${entry.name}` : entry.name);
    const fullPath = `${directory}/${entry.name}`;
    if (entry.isDirectory) files.push(...await collectQmdFiles(fullPath, nextRelative));
    else if (entry.isFile && entry.name.toLowerCase().endsWith(".qmd") && !entry.name.startsWith("_")) files.push(nextRelative);
  }
  return files.sort((a, b) => a.localeCompare(b, "ja"));
}

function unquote(value: string): string {
  const trimmed = value.trim();
  if ((trimmed.startsWith('"') && trimmed.endsWith('"')) ||
      (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function frontMatter(source: string): Record<string, string | string[]> {
  const normalized = source.replaceAll("\r\n", "\n");
  if (!normalized.startsWith("---\n")) return {};
  const end = normalized.indexOf("\n---", 4);
  if (end < 0) return {};
  const result: Record<string, string | string[]> = {};
  const lines = normalized.slice(4, end).split("\n");
  let listKey = "";
  for (const line of lines) {
    const pair = line.match(/^([A-Za-z][\w-]*):\s*(.*)$/);
    if (pair) {
      const key = pair[1].toLowerCase();
      const value = pair[2].trim();
      listKey = "";
      if (/^\[.*\]$/.test(value)) {
        result[key] = value.slice(1, -1).split(",").map(unquote).map((item) => item.trim()).filter(Boolean);
      } else {
        result[key] = unquote(value);
        if (!value) {
          result[key] = [];
          listKey = key;
        }
      }
      continue;
    }
    const item = listKey && line.match(/^\s+-\s+(.+)$/);
    if (item) (result[listKey] as string[]).push(unquote(item[1]));
  }
  return result;
}

function arrayValue(value: string | string[] | undefined): string[] {
  if (Array.isArray(value)) return value;
  return value ? [value] : [];
}

function isFalse(value: string | string[] | undefined): boolean {
  return typeof value === "string" && /^(false|no|off)$/i.test(value.trim());
}

function outputHref(path: string): string {
  return posixPath(path.replace(/\.qmd$/i, ".html"));
}

function nodeId(path: string): string {
  return posixPath(path.replace(/\.qmd$/i, ""));
}

function sectionName(path: string): string {
  const parts = posixPath(path).split("/");
  if (parts[0] === "posts" && parts[1]) return parts[1];
  return parts.length > 1 ? parts[0] : "site";
}

function plainDescription(source: string): string {
  const body = source.replace(/^---[\s\S]*?\n---\s*/, "")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/[#>*_`{}$|]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  return body.length > 120 ? `${body.slice(0, 119)}…` : body;
}

function linkedTargets(source: string): string[] {
  const targets: string[] = [];
  const markdownLink = /(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+["'][^"']*["'])?\)/g;
  const wikiLink = /\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]/g;
  for (const match of source.matchAll(markdownLink)) targets.push(match[1]);
  for (const match of source.matchAll(wikiLink)) targets.push(match[1]);
  return targets;
}

function resolveTarget(fromPath: string, rawTarget: string, known: Map<string, string>): string | null {
  if (!rawTarget || rawTarget.startsWith("#") || /^(?:[a-z]+:|\/\/)/i.test(rawTarget)) return null;
  let target = rawTarget.split("#")[0].split("?")[0];
  try { target = decodeURIComponent(target); } catch { /* retain the original */ }
  if (!target || /\.(?:png|jpe?g|gif|svg|webp|pdf|zip|bib|csv|json)$/i.test(target)) return null;
  const fromParts = posixPath(fromPath).split("/");
  fromParts.pop();
  const parts = target.startsWith("/") ? [] : fromParts;
  for (const part of posixPath(target).replace(/^\//, "").split("/")) {
    if (!part || part === ".") continue;
    if (part === "..") parts.pop();
    else parts.push(part);
  }
  let candidate = parts.join("/").replace(/\.html$/i, ".qmd");
  if (!/\.qmd$/i.test(candidate)) candidate += ".qmd";
  return known.get(candidate.toLocaleLowerCase("ja")) || null;
}

const qmdFiles = await collectQmdFiles(root);
const sources = new Map<string, string>();
const metadata = new Map<string, Record<string, string | string[]>>();
const includedFiles: string[] = [];

for (const path of qmdFiles) {
  const source = await Deno.readTextFile(`${root}/${path}`);
  const meta = frontMatter(source);
  if (isFalse(meta.graph) || /^(true|yes|on)$/i.test(String(meta.draft || ""))) continue;
  sources.set(path, source);
  metadata.set(path, meta);
  includedFiles.push(path);
}

const known = new Map(includedFiles.map((path) => [path.toLocaleLowerCase("ja"), path]));
const nodes: NodeRecord[] = includedFiles.map((path) => {
  const meta = metadata.get(path) || {};
  const source = sources.get(path) || "";
  const categories = [...new Set([...arrayValue(meta.categories), ...arrayValue(meta.tags)])]
    .map((item) => item.trim()).filter(Boolean);
  return {
    id: nodeId(path),
    href: outputHref(path),
    title: String(meta.title || nodeId(path).split("/").pop() || path),
    description: String(meta.description || plainDescription(source)),
    categories,
    section: sectionName(path),
    date: String(meta.date || ""),
  };
});

const explicitEdges: EdgeRecord[] = [];
const edgeKeys = new Set<string>();
for (const path of includedFiles) {
  const sourceId = nodeId(path);
  for (const rawTarget of linkedTargets(sources.get(path) || "")) {
    const resolved = resolveTarget(path, rawTarget, known);
    if (!resolved || resolved === path) continue;
    const targetId = nodeId(resolved);
    const key = [sourceId, targetId].sort().join("\u0000");
    if (edgeKeys.has(key)) continue;
    edgeKeys.add(key);
    explicitEdges.push({ source: sourceId, target: targetId, type: "link", weight: 3 });
  }
}

const relatedEdges: EdgeRecord[] = [];
const usefulCategories = (node: NodeRecord) => node.categories.filter((item) => !/^\d{4}$/.test(item));
for (const node of nodes) {
  const candidates = nodes.filter((other) => other.id !== node.id).map((other) => {
    const shared = usefulCategories(node).filter((item) => usefulCategories(other).some((value) => value.toLocaleLowerCase("ja") === item.toLocaleLowerCase("ja"))).length;
    const sameDirectory = node.id.includes("/") && node.id.slice(0, node.id.lastIndexOf("/")) === other.id.slice(0, other.id.lastIndexOf("/"));
    return { other, score: shared * 4 + (sameDirectory ? 2 : 0) };
  }).filter((item) => item.score >= 2)
    .sort((a, b) => b.score - a.score || a.other.id.localeCompare(b.other.id, "ja"))
    .slice(0, 2);
  for (const candidate of candidates) {
    const key = [node.id, candidate.other.id].sort().join("\u0000");
    if (edgeKeys.has(key)) continue;
    edgeKeys.add(key);
    relatedEdges.push({ source: node.id, target: candidate.other.id, type: "related", weight: Math.min(2, candidate.score / 4) });
  }
}

const comparable = { version: 1, nodes, edges: [...explicitEdges, ...relatedEdges] };
const destination = `${outputRoot}/assets/serika-graph.json`;
let previousComparable = "";
try {
  const previous = JSON.parse(await Deno.readTextFile(destination));
  previousComparable = JSON.stringify({ version: previous.version, nodes: previous.nodes, edges: previous.edges });
} catch { /* first build */ }

if (previousComparable !== JSON.stringify(comparable)) {
  await Deno.mkdir(`${outputRoot}/assets`, { recursive: true });
  const payload = JSON.stringify({ ...comparable, generatedAt: new Date().toISOString() });
  const temporary = `${destination}.tmp`;
  await Deno.writeTextFile(temporary, `${payload}\n`);
  await Deno.rename(temporary, destination);
  console.log(`Serika network: ${nodes.length} nodes, ${explicitEdges.length} links, ${relatedEdges.length} related edges`);
}
