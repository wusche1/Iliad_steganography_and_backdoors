import Anthropic from "https://esm.sh/@anthropic-ai/sdk@0.128.0";

pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
const $ = (id) => document.getElementById(id);

// ---------- state ----------
const hash = new URLSearchParams(location.hash.slice(1));
const lectures = await fetch("data/lectures.json").then((r) => r.json());
const lecture = lectures.includes(hash.get("lecture")) ? hash.get("lecture") : lectures[0];
const lectureName = (l) => l[0].toUpperCase() + l.slice(1);
$("lecture").append(...lectures.map((l) => new Option(lectureName(l), l)));
$("lecture").value = lecture;
$("lecture").onchange = () => { location.hash = `lecture=${$("lecture").value}`; location.reload(); };
const [slides, papers, pdf] = await Promise.all([
  fetch(`data/${lecture}.json`).then((r) => r.json()),
  fetch("data/papers.json").then((r) => r.json()),
  pdfjsLib.getDocument({ url: `${lecture}.pdf`, disableAutoFetch: true, disableStream: true }).promise,
]);
const paperByKey = Object.fromEntries(papers.map((p) => [p.key, p]));
let page = 1, elements = [], renderTask = null, history = [], attachments = [], busy = false;

if (hash.get("key")) localStorage.setItem("anthropic_key", hash.get("key"));
if (hash.get("model")) localStorage.setItem("model", hash.get("model"));
$("model").value = localStorage.getItem("model") || "claude-opus-5-5";
$("model").onchange = () => localStorage.setItem("model", $("model").value);

const slideTitle = (s) => s.title || s.text.split("\n")[0].trim() || "Untitled";

// ---------- slide viewer ----------
let group = null;
for (const s of slides) {
  const label = s.chapter ? s.chapter.replace(/^\d+_/, "").replaceAll("_", " ") : "general";
  if (!group || group.label !== label) $("outline").append((group = Object.assign(document.createElement("optgroup"), { label })));
  group.append(new Option(`${s.page} · ${slideTitle(s)}`, s.page));
}
$("outline").onchange = () => goTo(+$("outline").value);
$("prev").onclick = () => goTo(page - 1);
$("next").onclick = () => goTo(page + 1);
document.addEventListener("keydown", (e) => {
  if (e.target.closest("textarea, input, select")) return;
  if (e.key === "ArrowLeft" || e.key === "PageUp") goTo(page - 1);
  if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ") { e.preventDefault(); goTo(page + 1); }
});
window.addEventListener("hashchange", () => {
  const n = +new URLSearchParams(location.hash.slice(1)).get("slide");
  if (n) goTo(n);
});
new ResizeObserver(() => render()).observe($("stage"));

function goTo(n) {
  page = Math.min(Math.max(n, 1), pdf.numPages);
  window.history.replaceState(null, "", `#lecture=${lecture}&slide=${page}`);
  render();
}

async function render() {
  const p = await pdf.getPage(page);
  const base = p.getViewport({ scale: 1 });
  const stage = $("stage").getBoundingClientRect();
  const pad = innerWidth > 860 ? 32 : 16;
  const scale = Math.min((stage.width - pad) / base.width, innerWidth > 860 ? (stage.height - pad) / base.height : Infinity);
  const vp = p.getViewport({ scale: scale * devicePixelRatio });
  const canvas = $("canvas");
  renderTask?.cancel();
  const off = Object.assign(document.createElement("canvas"), { width: vp.width, height: vp.height });
  renderTask = p.render({ canvasContext: off.getContext("2d"), viewport: vp });
  try { await renderTask.promise; } catch { return; }
  canvas.width = vp.width; canvas.height = vp.height;
  canvas.style.width = `${vp.width / devicePixelRatio}px`;
  canvas.style.height = `${vp.height / devicePixelRatio}px`;
  canvas.getContext("2d").drawImage(off, 0, 0);
  $("counter").textContent = `${page} / ${pdf.numPages}`;
  $("outline").value = page;
  elements = await extractElements(p);
}

// Text lines and images on a page, as fractional boxes {x, y, w, h} (top-left origin).
async function extractElements(p) {
  const vp = p.getViewport({ scale: 1 });
  const box = (x1, y1, x2, y2) => {
    const [a, b, c, d] = vp.convertToViewportRectangle([x1, y1, x2, y2]);
    return { x: Math.min(a, c) / vp.width, y: Math.min(b, d) / vp.height, w: Math.abs(c - a) / vp.width, h: Math.abs(d - b) / vp.height };
  };
  const lines = [];
  for (const it of (await p.getTextContent()).items) {
    if (!it.str.trim()) continue;
    const [, , , , x, y] = it.transform, h = it.height || 8;
    const l = lines.find((l) => Math.abs(l.y - y) < h * 0.6 && x - l.x2 < h * 1.5 && x >= l.x1 - h);
    if (l) Object.assign(l, { x2: Math.max(l.x2, x + it.width), h: Math.max(l.h, h), text: l.text + (x - l.x2 > h * 0.15 ? " " : "") + it.str });
    else lines.push({ x1: x, x2: x + it.width, y, h, text: it.str });
  }
  const out = lines.map((l) => ({ kind: "text", text: l.text, ...box(l.x1 - 2, l.y - l.h * 0.3, l.x2 + 2, l.y + l.h * 0.95) }));

  const ops = await p.getOperatorList(), O = pdfjsLib.OPS, stack = [];
  const paint = [O.paintImageXObject, O.paintInlineImageXObject, O.paintImageMaskXObject, O.paintJpegXObject];
  let ctm = [1, 0, 0, 1, 0, 0], n = 0;
  ops.fnArray.forEach((fn, i) => {
    const args = ops.argsArray[i];
    if (fn === O.save) stack.push(ctm);
    else if (fn === O.restore) ctm = stack.pop() ?? ctm;
    else if (fn === O.transform) ctm = pdfjsLib.Util.transform(ctm, args);
    else if (fn === O.paintFormXObjectBegin) { stack.push(ctm); if (args[0]) ctm = pdfjsLib.Util.transform(ctm, args[0]); }
    else if (fn === O.paintFormXObjectEnd) ctm = stack.pop() ?? ctm;
    else if (paint.includes(fn)) {
      const pts = [[0, 0], [1, 0], [0, 1], [1, 1]].map(([u, v]) => pdfjsLib.Util.applyTransform([u, v], ctm));
      const xs = pts.map((q) => q[0]), ys = pts.map((q) => q[1]);
      const b = box(Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys));
      if (b.w * b.h > 0.002 && b.w * b.h < 0.95) out.push({ kind: "image", index: n++, ...b });
    }
  });
  return out;
}

// ---------- picking elements ----------
const overlay = $("overlay");
const frac = (e) => {
  const r = overlay.getBoundingClientRect();
  return { x: (e.clientX - r.left) / r.width, y: (e.clientY - r.top) / r.height };
};
const hit = ({ x, y }) => elements
  .filter((el) => x >= el.x && x <= el.x + el.w && y >= el.y && y <= el.y + el.h)
  .sort((a, b) => a.w * a.h - b.w * b.h)[0];
const place = (div, b) => b
  ? Object.assign(div.style, { display: "block", left: `${b.x * 100}%`, top: `${b.y * 100}%`, width: `${b.w * 100}%`, height: `${b.h * 100}%` })
  : (div.style.display = "none");

let drag = null;
overlay.onpointerdown = (e) => { drag = frac(e); overlay.setPointerCapture(e.pointerId); };
overlay.onpointermove = (e) => {
  const q = frac(e);
  if (drag && Math.hypot(q.x - drag.x, q.y - drag.y) > 0.01) {
    place($("hl"), null);
    place($("sel"), { x: Math.min(q.x, drag.x), y: Math.min(q.y, drag.y), w: Math.abs(q.x - drag.x), h: Math.abs(q.y - drag.y) });
  } else if (!drag) place($("hl"), hit(q));
};
overlay.onpointerleave = () => place($("hl"), null);
overlay.onpointerup = (e) => {
  const q = frac(e), start = drag;
  drag = null;
  place($("sel"), null);
  if (!start) return;
  if (Math.hypot(q.x - start.x, q.y - start.y) > 0.01) {
    const b = { x: Math.min(q.x, start.x), y: Math.min(q.y, start.y), w: Math.abs(q.x - start.x), h: Math.abs(q.y - start.y) };
    const text = elements.filter((el) => el.kind === "text" && el.x >= b.x && el.y >= b.y && el.x + el.w <= b.x + b.w && el.y + el.h <= b.y + b.h).map((el) => el.text).join("\n");
    attach({ kind: "region", text, ...b });
  } else {
    const el = hit(q);
    el ? attach(el) : attachSlide();
  }
};
$("attach-slide").onclick = () => attachSlide();
const attachSlide = () => attach({ kind: "slide", x: 0, y: 0, w: 1, h: 1 });

// Renders the current page at high resolution and crops the given fractional box to a PNG data URL.
async function crop(n, b, maxSide = 1568) {
  const p = await pdf.getPage(n);
  const base = p.getViewport({ scale: 1 });
  const scale = Math.min(6, maxSide / Math.max(base.width * b.w, base.height * b.h));
  const vp = p.getViewport({ scale });
  const full = Object.assign(document.createElement("canvas"), { width: vp.width, height: vp.height });
  await p.render({ canvasContext: full.getContext("2d"), viewport: vp }).promise;
  const pad = b.kind === "slide" ? 0 : 4;
  const sx = Math.max(0, b.x * vp.width - pad), sy = Math.max(0, b.y * vp.height - pad);
  const w = Math.min(vp.width - sx, b.w * vp.width + 2 * pad), h = Math.min(vp.height - sy, b.h * vp.height + 2 * pad);
  const out = Object.assign(document.createElement("canvas"), { width: Math.round(w), height: Math.round(h) });
  out.getContext("2d").drawImage(full, sx, sy, w, h, 0, 0, w, h);
  return out.toDataURL("image/png");
}

// Guess which \includegraphics/\paperfig/\fullfig in the frame source produced the n-th image on the page.
function imageFile(s, index) {
  const files = [...(s.source || "").matchAll(/\\(?:includegraphics(?:\[[^\]]*\])?|paperfig|fullfig)\{([^}]+)\}/g)].map((m) => m[1]);
  return files[index];
}

async function attach(el) {
  const s = slides[page - 1];
  const label = el.kind === "slide" ? `Slide ${page}` : el.kind === "text" ? el.text : el.kind === "image" ? `Figure on slide ${page}` : `Region of slide ${page}`;
  const a = { ...el, page, label, file: el.kind === "image" ? imageFile(s, el.index) : undefined, image: await crop(page, el) };
  attachments.push(a);
  renderChips();
  $("input").focus();
}

function renderChips() {
  $("chips").replaceChildren(...attachments.map((a, i) => {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.title = a.label;
    chip.innerHTML = `<img alt=""><span></span><button type="button" aria-label="Remove">×</button>`;
    chip.querySelector("img").src = a.image;
    chip.querySelector("span").textContent = a.kind === "text" ? `“${a.label}”` : a.label;
    chip.querySelector("button").onclick = () => { attachments.splice(i, 1); renderChips(); };
    return chip;
  }));
}

// ---------- context for Claude ----------
const b64 = (dataUrl) => ({ type: "image", source: { type: "base64", media_type: dataUrl.slice(5, dataUrl.indexOf(";")), data: dataUrl.split(",")[1] } });

function slideContext(n) {
  const s = slides[n - 1];
  if (!s.source) return `<slide page="${n}" generated="true">\n${s.text}\n</slide>`;
  return `<slide page="${n}" chapter="${s.chapter}" title="${s.title}" file="${s.file}" lines="${s.lines.join("-")}" papers="${s.refs.join(",")}">
<latex_source>
${s.source}
</latex_source>
</slide>`;
}

const SYSTEM = `You are the teaching assistant for a course on steganography and backdoors in AI systems (Iliad Intensive). Participants browse the slides of the "${lectureName(lecture)}" lecture on a website and ask you questions in a side panel.

What you have:
- The slide outline below. Every slide's LaTeX source (including the lecturer's speaker notes in \\note{...}) is available through get_slide, which also returns a rendered image of the slide.
- When the participant clicks an element of a slide, drags a box over part of a slide, or attaches a whole slide, their message contains the slide's LaTeX source and a cropped image of what they selected. Figures included as figures/<paperkey>/<name>.png were taken from the paper with that citation key, and \\source{key} / \\cite{key} name the papers a slide draws on.
- The course literature listed below. search_literature does keyword search over the full text of every paper; read_paper reads a paper's full text in chunks; view_paper_figure shows figures the lecturer captured from a paper.

How to answer:
- Ground answers in the slides and the papers. Before stating specifics about a paper (numbers, methods, claims, figure details), check them with search_literature or read_paper rather than relying on memory. If the literature does not cover something, say so and answer from general knowledge, flagged as such.
- Cite papers as [key] (e.g. [chen2025b]); refer to slides as "slide N". Both become clickable links.
- The speaker notes are the lecturer's own words and are fine to use, but speak as a TA, not as the lecturer.
- Be concise and conversational; participants are reading on the side of the slides. Use LaTeX math with $...$ and $$...$$.

<slide_outline>
${slides.map((s) => `${s.page}. ${s.chapter ? `[${s.chapter}] ` : ""}${slideTitle(s)}${s.refs?.length ? ` (papers: ${s.refs.join(", ")})` : ""}`).join("\n")}
</slide_outline>

<literature>
${papers.map((p) => `<paper key="${p.key}" year="${p.year}" fulltext_chars="${p.chars}">
${p.title} (${p.author} et al.) ${p.url}
${p.abstract}${p.figures.length ? `\nCaptured figures: ${p.figures.join(", ")}` : ""}
</paper>`).join("\n")}
</literature>`;

const TOOLS = [
  {
    name: "get_slide",
    description: "Get a slide's LaTeX source (with speaker notes), its papers, and a rendered image of it.",
    input_schema: { type: "object", properties: { page: { type: "integer", description: "Slide number (1-based)" } }, required: ["page"] },
  },
  {
    name: "search_literature",
    description: "Keyword search over the full text of all course papers. Returns the best-matching passages with their paper key and character offset (use read_paper with that offset to read around a hit).",
    input_schema: {
      type: "object",
      properties: {
        query: { type: "string", description: "Keywords or a short phrase" },
        keys: { type: "array", items: { type: "string" }, description: "Optional: restrict to these paper keys" },
      },
      required: ["query"],
    },
  },
  {
    name: "read_paper",
    description: "Read a paper's full text (markdown) in chunks of 20000 characters, starting at offset.",
    input_schema: { type: "object", properties: { key: { type: "string" }, offset: { type: "integer", default: 0 } }, required: ["key"] },
  },
  {
    name: "view_paper_figure",
    description: "View a figure the lecturer captured from a paper (names are listed under 'Captured figures').",
    input_schema: { type: "object", properties: { key: { type: "string" }, name: { type: "string" } }, required: ["key", "name"] },
  },
];

const fulltexts = {};
const fulltext = (key) => (fulltexts[key] ??= fetch(`bib/${key}/${key}_fulltext.md`).then((r) => (r.ok ? r.text() : Promise.reject(new Error(`No full text for ${key}`)))));

const runTool = {
  async get_slide({ page: n }) {
    if (!slides[n - 1]) throw new Error(`No slide ${n}`);
    return [{ type: "text", text: slideContext(n) }, b64(await crop(n, { kind: "slide", x: 0, y: 0, w: 1, h: 1 }, 1200))];
  },
  async search_literature({ query, keys }) {
    const terms = query.toLowerCase().match(/[\p{L}\p{N}-]{3,}/gu) || [];
    const pool = papers.filter((p) => p.fulltext && (!keys?.length || keys.includes(p.key)));
    const hits = [];
    for (const p of pool) {
      const text = await fulltext(p.key).catch(() => "");
      for (let off = 0; off < text.length; off += 600) {
        const chunk = text.slice(off, off + 1200), low = chunk.toLowerCase();
        const counts = terms.map((t) => low.split(t).length - 1);
        const score = counts.reduce((s, c) => s + Math.log1p(c), 0) * counts.filter(Boolean).length + (low.includes(query.toLowerCase()) ? 5 : 0);
        if (score > 0) hits.push({ key: p.key, off, score, chunk });
      }
    }
    hits.sort((a, b) => b.score - a.score);
    const top = [];
    for (const h of hits) if (top.length < 8 && top.filter((t) => t.key === h.key).length < 2 && !top.some((t) => t.key === h.key && Math.abs(t.off - h.off) < 1200)) top.push(h);
    return top.length ? top.map((h) => `<hit key="${h.key}" offset="${h.off}">\n${h.chunk}\n</hit>`).join("\n") : "No matches.";
  },
  async read_paper({ key, offset = 0 }) {
    const text = await fulltext(key);
    const end = Math.min(text.length, offset + 20000);
    return `[${key}: characters ${offset}-${end} of ${text.length}${end < text.length ? `; continue with offset=${end}` : ""}]\n\n${text.slice(offset, end)}`;
  },
  async view_paper_figure({ key, name }) {
    const img = new Image();
    img.src = `bib/${key}/figures/${name}.png`;
    await img.decode().catch(() => { throw new Error(`No figure ${key}/${name}`); });
    const s = Math.min(1, 1568 / Math.max(img.width, img.height));
    const c = Object.assign(document.createElement("canvas"), { width: img.width * s, height: img.height * s });
    c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
    return [b64(c.toDataURL("image/png"))];
  },
};

const toolLabel = {
  get_slide: (i) => `looked at slide ${i.page}`,
  search_literature: (i) => `searched the literature for “${i.query}”${i.keys?.length ? ` in ${i.keys.join(", ")}` : ""}`,
  read_paper: (i) => `read ${paperByKey[i.key]?.title || i.key}${i.offset ? ` (from char ${i.offset})` : ""}`,
  view_paper_figure: (i) => `viewed figure ${i.name} from ${i.key}`,
};

// ---------- chat ----------
const apiKey = () => localStorage.getItem("anthropic_key");
function showKeyForm() { $("keyform").hidden = !!apiKey(); }
$("keyform").onsubmit = (e) => {
  e.preventDefault();
  localStorage.setItem("anthropic_key", $("keyinput").value.trim());
  showKeyForm();
};
showKeyForm();

$("new-chat").onclick = () => {
  history = [];
  $("messages").replaceChildren();
};
$("input").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); $("composer").requestSubmit(); }
});
$("input").addEventListener("input", (e) => { e.target.style.height = "auto"; e.target.style.height = `${e.target.scrollHeight}px`; });
$("composer").onsubmit = (e) => { e.preventDefault(); send(); };

function addMsg(cls, html = "") {
  $("messages").querySelector(".empty")?.remove();
  const div = Object.assign(document.createElement("div"), { className: `msg ${cls}` });
  div.innerHTML = html;
  $("messages").append(div);
  div.scrollIntoView({ block: "end" });
  return div;
}

function markdown(text) {
  const math = [];
  const keep = (m) => `%%MATH${math.push(m) - 1}%%`;
  text = text
    .replace(/\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\)|\$[^$\n]+?\$/g, keep)
    .replace(/\[([\w-]+)\](?!\()/g, (m, k) => (paperByKey[k] ? `[[${k}]](${paperByKey[k].url || "#"} "${paperByKey[k].title.replaceAll('"', "'")}")` : m))
    .replace(/\b([Ss]lides?) (\d+)\b/g, (m, w, n) => `[${w} ${n}](#slide=${n})`);
  const html = DOMPurify.sanitize(marked.parse(text)).replace(/%%MATH(\d+)%%/g, (m, i) => math[i].replace(/&/g, "&amp;").replace(/</g, "&lt;"));
  return html;
}

function renderMarkdown(div, text) {
  div.innerHTML = markdown(text);
  renderMathInElement(div, {
    delimiters: [{ left: "$$", right: "$$", display: true }, { left: "\\[", right: "\\]", display: true }, { left: "$", right: "$", display: false }, { left: "\\(", right: "\\)", display: false }],
    throwOnError: false,
  });
  div.querySelectorAll('a[href^="http"]').forEach((a) => (a.target = "_blank"));
}

async function send() {
  const text = $("input").value.trim();
  if (busy || (!text && !attachments.length)) return;
  if (!apiKey()) return showKeyForm();
  const content = [];
  for (const n of new Set(attachments.map((a) => a.page))) content.push({ type: "text", text: slideContext(n) });
  for (const a of attachments) {
    const what = { slide: `the whole slide ${a.page}`, text: `this text element on slide ${a.page}: "${a.text}"`, image: `a figure on slide ${a.page}${a.file ? ` (most likely ${a.file})` : ""}`, region: `a region of slide ${a.page}${a.text ? ` containing the text:\n${a.text}` : ""}` }[a.kind];
    content.push({ type: "text", text: `The participant selected ${what}` }, b64(a.image));
  }
  content.push({ type: "text", text: `[Participant is currently viewing slide ${page}: ${slideTitle(slides[page - 1])}]\n\n${text || "Can you explain this?"}` });
  const before = history.length;
  history.push({ role: "user", content });

  const bubble = addMsg("user");
  if (attachments.length) {
    const thumbs = Object.assign(document.createElement("div"), { className: "thumbs" });
    for (const a of attachments) thumbs.append(Object.assign(new Image(), { src: a.image, title: a.label }));
    bubble.append(thumbs);
  }
  bubble.append(text || "Can you explain this?");
  attachments = [];
  renderChips();
  $("input").value = "";
  $("input").style.height = "auto";
  busy = $("send").disabled = true;
  try { await runTurn(); }
  catch (err) {
    addMsg("error").textContent = err.status === 401 ? "The API key was rejected. Check the key in your course link." : `Error: ${err.message}`;
    if (err.status === 401) { localStorage.removeItem("anthropic_key"); showKeyForm(); }
    history.length = before;
  }
  busy = $("send").disabled = false;
}

async function runTurn() {
  const client = new Anthropic({ apiKey: apiKey(), dangerouslyAllowBrowser: true });
  const model = $("model").value;
  for (;;) {
    let textDiv = null, text = "", think = null;
    const stream = client.beta.messages.stream({
      model,
      max_tokens: 32000,
      thinking: { type: "adaptive", display: "summarized" },
      output_config: { effort: "medium" },
      system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
      cache_control: { type: "ephemeral" },
      tools: TOOLS,
      messages: history,
      ...(model.includes("haiku") ? {} : { betas: ["server-side-fallback-2026-07-01"], fallbacks: "default" }),
    });
    stream.on("streamEvent", (ev) => {
      if (ev.type === "content_block_start" && ev.content_block.type === "thinking") {
        think = addMsg("think-wrap");
        think.innerHTML = `<details class="think"><summary>Thinking…</summary><div></div></details>`;
      } else if (ev.type === "content_block_delta" && ev.delta.type === "thinking_delta" && think) {
        think.querySelector("div").textContent += ev.delta.thinking;
      } else if (ev.type === "content_block_start" && ev.content_block.type === "text") {
        textDiv = addMsg("assistant cursor");
        text = "";
      } else if (ev.type === "content_block_delta" && ev.delta.type === "text_delta" && textDiv) {
        text += ev.delta.text;
        renderMarkdown(textDiv, text);
        $("messages").scrollTop = $("messages").scrollHeight;
      } else if (ev.type === "content_block_stop") {
        textDiv?.classList.remove("cursor");
        if (think && !think.querySelector("div").textContent) think.remove();
        if (think) think.querySelector("summary").textContent = "Thought";
        think = null;
      }
    });
    const msg = await stream.finalMessage();
    history.push({ role: "assistant", content: msg.content });
    if (msg.stop_reason === "refusal") addMsg("error").textContent = "Claude declined to answer this one. Try rephrasing.";
    if (msg.stop_reason !== "tool_use") return;
    const results = await Promise.all(msg.content.filter((b) => b.type === "tool_use").map(async (b) => {
      addMsg("tool").textContent = toolLabel[b.name]?.(b.input) ?? b.name;
      try {
        const out = await runTool[b.name](b.input);
        return { type: "tool_result", tool_use_id: b.id, content: out };
      } catch (err) {
        return { type: "tool_result", tool_use_id: b.id, content: err.message, is_error: true };
      }
    }));
    history.push({ role: "user", content: results });
  }
}

goTo(+hash.get("slide") || 1);
