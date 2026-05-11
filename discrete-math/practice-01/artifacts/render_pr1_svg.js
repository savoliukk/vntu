const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const inputPdf = path.resolve(__dirname, "../../input/04_Практичні та лабораторні/ПР1.pdf");
const outDir = path.resolve(__dirname, "svg_pages");

function multiply(m1, m2) {
  return [
    m1[0] * m2[0] + m1[2] * m2[1],
    m1[1] * m2[0] + m1[3] * m2[1],
    m1[0] * m2[2] + m1[2] * m2[3],
    m1[1] * m2[2] + m1[3] * m2[3],
    m1[0] * m2[4] + m1[2] * m2[5] + m1[4],
    m1[1] * m2[4] + m1[3] * m2[5] + m1[5],
  ];
}

function transform(m, x, y) {
  return [m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]];
}

function fmt(n) {
  return Number.isFinite(n) ? Number(n.toFixed(3)).toString() : "0";
}

function colorFromStack(stack) {
  const vals = stack.splice(0).map(Number);
  if (vals.length >= 3) {
    const rgb = vals.slice(-3).map((v) => Math.max(0, Math.min(255, Math.round(v * 255))));
    return `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
  }
  if (vals.length >= 1) {
    const g = Math.max(0, Math.min(255, Math.round(vals[vals.length - 1] * 255)));
    return `rgb(${g},${g},${g})`;
  }
  return "rgb(0,0,0)";
}

function tokenize(content) {
  const tokens = [];
  const re = /\/[^\s<>\[\](){}%]+|[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[Ee][-+]?\d+)?|[A-Za-z\*']+|./g;
  let m;
  while ((m = re.exec(content))) {
    const t = m[0];
    if (/^\s$/.test(t)) continue;
    if (t === "%") {
      while (re.lastIndex < content.length && content[re.lastIndex] !== "\n") re.lastIndex++;
      continue;
    }
    tokens.push(t);
  }
  return tokens;
}

function parsePdfObjects(pdfBinary) {
  const objects = new Map();
  const re = /(\d+)\s+(\d+)\s+obj([\s\S]*?)endobj/g;
  let m;
  while ((m = re.exec(pdfBinary))) {
    objects.set(Number(m[1]), m[3]);
  }
  return objects;
}

function extractStream(body) {
  const sIdx = body.indexOf("stream");
  const eIdx = body.indexOf("endstream");
  if (sIdx < 0 || eIdx <= sIdx) return "";

  let start = sIdx + "stream".length;
  if (body[start] === "\r" && body[start + 1] === "\n") start += 2;
  else if (body[start] === "\n") start += 1;

  let end = eIdx;
  while (end > start && (body[end - 1] === "\r" || body[end - 1] === "\n")) end--;

  const stream = Buffer.from(body.slice(start, end), "latin1");
  if (/\/Filter\s*\/FlateDecode/.test(body)) {
    return zlib.inflateSync(stream).toString("latin1");
  }
  return stream.toString("latin1");
}

function extractPageDefs(objects) {
  const pages = [];
  for (const [objNum, body] of objects) {
    if (!/\/Type\s*\/Page\b/.test(body)) continue;
    const contentsMatch = body.match(/\/Contents\s*\[([\s\S]*?)\]/);
    if (!contentsMatch) continue;
    const refs = [];
    const refRe = /(\d+)\s+0\s+R/g;
    let ref;
    while ((ref = refRe.exec(contentsMatch[1]))) refs.push(Number(ref[1]));

    const cropMatch = body.match(/\/(?:CropBox|MediaBox)\s*\[\s*([^\]]+)\]/);
    const box = cropMatch ? cropMatch[1].trim().split(/\s+/).map(Number) : [0, 0, 612, 792];
    pages.push({ objNum, refs, box });
  }
  pages.sort((a, b) => a.objNum - b.objNum);
  return pages;
}

function renderContentToSvg(content, width, height) {
  const tokens = tokenize(content);
  const stateStack = [];
  let state = {
    ctm: [1, 0, 0, 1, 0, 0],
    fill: "rgb(0,0,0)",
    stroke: "rgb(0,0,0)",
    lineWidth: 1,
  };
  let stack = [];
  let pathD = "";
  let current = [0, 0];
  const svgParts = [
    `<rect x="0" y="0" width="${fmt(width)}" height="${fmt(height)}" fill="white"/>`,
  ];

  function paint(kind, evenOdd) {
    if (!pathD.trim()) {
      stack = [];
      return;
    }
    const fillRule = evenOdd ? ` fill-rule="evenodd"` : "";
    if (kind === "stroke") {
      svgParts.push(`<path d="${pathD.trim()}" fill="none" stroke="${state.stroke}" stroke-width="${fmt(state.lineWidth)}"/>`);
    } else if (kind === "both") {
      svgParts.push(`<path d="${pathD.trim()}" fill="${state.fill}"${fillRule} stroke="${state.stroke}" stroke-width="${fmt(state.lineWidth)}"/>`);
    } else {
      svgParts.push(`<path d="${pathD.trim()}" fill="${state.fill}"${fillRule} stroke="none"/>`);
    }
    pathD = "";
    stack = [];
  }

  function numberStack(n) {
    const vals = stack.splice(-n).map(Number);
    if (vals.length !== n || vals.some((v) => Number.isNaN(v))) return null;
    return vals;
  }

  for (const token of tokens) {
    if (/^[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[Ee][-+]?\d+)?$/.test(token) || token.startsWith("/")) {
      stack.push(token);
      continue;
    }

    switch (token) {
      case "q":
        stateStack.push({ ...state, ctm: state.ctm.slice() });
        stack = [];
        break;
      case "Q":
        state = stateStack.pop() || state;
        stack = [];
        break;
      case "cm": {
        const vals = numberStack(6);
        if (vals) state.ctm = multiply(state.ctm, vals);
        stack = [];
        break;
      }
      case "rg":
      case "g":
        state.fill = colorFromStack(stack);
        break;
      case "RG":
      case "G":
        state.stroke = colorFromStack(stack);
        break;
      case "w": {
        const vals = numberStack(1);
        if (vals) state.lineWidth = Math.max(0.1, Math.abs(vals[0]));
        stack = [];
        break;
      }
      case "m": {
        const vals = numberStack(2);
        if (vals) {
          current = transform(state.ctm, vals[0], vals[1]);
          pathD += `M ${fmt(current[0])} ${fmt(current[1])} `;
        }
        stack = [];
        break;
      }
      case "l": {
        const vals = numberStack(2);
        if (vals) {
          current = transform(state.ctm, vals[0], vals[1]);
          pathD += `L ${fmt(current[0])} ${fmt(current[1])} `;
        }
        stack = [];
        break;
      }
      case "c": {
        const vals = numberStack(6);
        if (vals) {
          const p1 = transform(state.ctm, vals[0], vals[1]);
          const p2 = transform(state.ctm, vals[2], vals[3]);
          current = transform(state.ctm, vals[4], vals[5]);
          pathD += `C ${fmt(p1[0])} ${fmt(p1[1])} ${fmt(p2[0])} ${fmt(p2[1])} ${fmt(current[0])} ${fmt(current[1])} `;
        }
        stack = [];
        break;
      }
      case "v": {
        const vals = numberStack(4);
        if (vals) {
          const p2 = transform(state.ctm, vals[0], vals[1]);
          const p3 = transform(state.ctm, vals[2], vals[3]);
          pathD += `C ${fmt(current[0])} ${fmt(current[1])} ${fmt(p2[0])} ${fmt(p2[1])} ${fmt(p3[0])} ${fmt(p3[1])} `;
          current = p3;
        }
        stack = [];
        break;
      }
      case "y": {
        const vals = numberStack(4);
        if (vals) {
          const p1 = transform(state.ctm, vals[0], vals[1]);
          const p3 = transform(state.ctm, vals[2], vals[3]);
          pathD += `C ${fmt(p1[0])} ${fmt(p1[1])} ${fmt(p3[0])} ${fmt(p3[1])} ${fmt(p3[0])} ${fmt(p3[1])} `;
          current = p3;
        }
        stack = [];
        break;
      }
      case "h":
        pathD += "Z ";
        stack = [];
        break;
      case "re": {
        const vals = numberStack(4);
        if (vals) {
          const [x, y, w, h] = vals;
          const p1 = transform(state.ctm, x, y);
          const p2 = transform(state.ctm, x + w, y);
          const p3 = transform(state.ctm, x + w, y + h);
          const p4 = transform(state.ctm, x, y + h);
          pathD += `M ${fmt(p1[0])} ${fmt(p1[1])} L ${fmt(p2[0])} ${fmt(p2[1])} L ${fmt(p3[0])} ${fmt(p3[1])} L ${fmt(p4[0])} ${fmt(p4[1])} Z `;
        }
        stack = [];
        break;
      }
      case "S":
        paint("stroke", false);
        break;
      case "s":
        pathD += "Z ";
        paint("stroke", false);
        break;
      case "f":
      case "F":
        paint("fill", false);
        break;
      case "f*":
        paint("fill", true);
        break;
      case "B":
        paint("both", false);
        break;
      case "B*":
        paint("both", true);
        break;
      case "b":
        pathD += "Z ";
        paint("both", false);
        break;
      case "b*":
        pathD += "Z ";
        paint("both", true);
        break;
      case "n":
        pathD = "";
        stack = [];
        break;
      default:
        stack = [];
        break;
    }
  }

  return svgParts.join("\n");
}

fs.mkdirSync(outDir, { recursive: true });

const pdf = fs.readFileSync(inputPdf).toString("latin1");
const objects = parsePdfObjects(pdf);
const pages = extractPageDefs(objects);

for (let i = 0; i < pages.length; i++) {
  const page = pages[i];
  const content = page.refs.map((ref) => extractStream(objects.get(ref) || "")).join("\n");
  const [x0, y0, x1, y1] = page.box;
  const width = x1 - x0;
  const height = y1 - y0;
  const body = renderContentToSvg(content, width, height);
  const svg = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<svg xmlns="http://www.w3.org/2000/svg" width="${fmt(width)}pt" height="${fmt(height)}pt" viewBox="0 0 ${fmt(width)} ${fmt(height)}">`,
    body,
    `</svg>`,
  ].join("\n");
  fs.writeFileSync(path.join(outDir, `page_${String(i + 1).padStart(2, "0")}.svg`), svg, "utf8");
}

console.log(`Rendered ${pages.length} SVG pages into ${outDir}`);
