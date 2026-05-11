const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const inputPdf = path.resolve(__dirname, "../../input/04_Практичні та лабораторні/ПР1.pdf");
const outDir = path.resolve(__dirname, "rendered_pages");
const SCALE = Number(process.argv[2] || 3);

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) {
    c ^= buf[i];
    for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xedb88320 & -(c & 1));
  }
  return (c ^ 0xffffffff) >>> 0;
}

function pngChunk(type, data) {
  const t = Buffer.from(type, "ascii");
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([t, data])), 0);
  return Buffer.concat([len, t, data, crc]);
}

function writeGrayPng(file, width, height, pixels) {
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 0;
  ihdr[10] = 0;
  ihdr[11] = 0;
  ihdr[12] = 0;

  const rows = Buffer.alloc((width + 1) * height);
  for (let y = 0; y < height; y++) {
    rows[y * (width + 1)] = 0;
    pixels.copy(rows, y * (width + 1) + 1, y * width, (y + 1) * width);
  }

  fs.writeFileSync(
    file,
    Buffer.concat([
      signature,
      pngChunk("IHDR", ihdr),
      pngChunk("IDAT", zlib.deflateSync(rows, { level: 9 })),
      pngChunk("IEND", Buffer.alloc(0)),
    ])
  );
}

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

function grayFromStack(stack) {
  const vals = stack.splice(0).map(Number);
  if (vals.length >= 3) {
    const [r, g, b] = vals.slice(-3);
    return Math.max(0, Math.min(255, Math.round((0.299 * r + 0.587 * g + 0.114 * b) * 255)));
  }
  if (vals.length >= 1) return Math.max(0, Math.min(255, Math.round(vals[vals.length - 1] * 255)));
  return 0;
}

function tokenize(content) {
  const tokens = [];
  const re = /\/[^\s<>\[\](){}%]+|[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[Ee][-+]?\d+)?|[A-Za-z\*']+|[\[\]]|%|./g;
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
  while ((m = re.exec(pdfBinary))) objects.set(Number(m[1]), m[3]);
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
  if (/\/Filter\s*\/FlateDecode/.test(body)) return zlib.inflateSync(stream).toString("latin1");
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
    const boxMatch = body.match(/\/(?:CropBox|MediaBox)\s*\[\s*([^\]]+)\]/);
    const box = boxMatch ? boxMatch[1].trim().split(/\s+/).map(Number) : [0, 0, 612, 792];
    pages.push({ objNum, refs, box });
  }
  pages.sort((a, b) => a.objNum - b.objNum);
  return pages;
}

function flattenCubic(p0, p1, p2, p3) {
  const dx = p3[0] - p0[0];
  const dy = p3[1] - p0[1];
  const chord = Math.sqrt(dx * dx + dy * dy);
  const steps = Math.max(6, Math.min(18, Math.ceil(chord * SCALE / 6)));
  const pts = [];
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    const mt = 1 - t;
    const x =
      mt * mt * mt * p0[0] +
      3 * mt * mt * t * p1[0] +
      3 * mt * t * t * p2[0] +
      t * t * t * p3[0];
    const y =
      mt * mt * mt * p0[1] +
      3 * mt * mt * t * p1[1] +
      3 * mt * t * t * p2[1] +
      t * t * t * p3[1];
    pts.push([x, y]);
  }
  return pts;
}

function makeCanvas(width, height) {
  const w = Math.ceil(width * SCALE);
  const h = Math.ceil(height * SCALE);
  return { w, h, pixels: Buffer.alloc(w * h, 255) };
}

function flipY(canvas) {
  const flipped = Buffer.alloc(canvas.pixels.length);
  for (let y = 0; y < canvas.h; y++) {
    for (let x = 0; x < canvas.w; x++) {
      flipped[(canvas.h - 1 - y) * canvas.w + x] = canvas.pixels[y * canvas.w + x];
    }
  }
  canvas.pixels = flipped;
  return canvas;
}

function setPixel(canvas, x, y, gray) {
  const ix = Math.round(x);
  const iy = Math.round(y);
  if (ix >= 0 && ix < canvas.w && iy >= 0 && iy < canvas.h) canvas.pixels[iy * canvas.w + ix] = gray;
}

function drawLine(canvas, a, b, gray, lineWidth) {
  let x0 = a[0] * SCALE;
  let y0 = a[1] * SCALE;
  const x1 = b[0] * SCALE;
  const y1 = b[1] * SCALE;
  const dx = x1 - x0;
  const dy = y1 - y0;
  const steps = Math.max(1, Math.ceil(Math.sqrt(dx * dx + dy * dy)));
  const radius = Math.max(0, Math.ceil((lineWidth * SCALE) / 2));
  for (let i = 0; i <= steps; i++) {
    const x = x0 + (dx * i) / steps;
    const y = y0 + (dy * i) / steps;
    for (let yy = -radius; yy <= radius; yy++) {
      for (let xx = -radius; xx <= radius; xx++) setPixel(canvas, x + xx, y + yy, gray);
    }
  }
}

function fillContours(canvas, contours, gray, evenOdd) {
  const scaled = contours
    .map((contour) => contour.map(([x, y]) => [x * SCALE, y * SCALE]))
    .filter((contour) => contour.length >= 3);
  if (!scaled.length) return;

  let minY = Infinity;
  let maxY = -Infinity;
  for (const contour of scaled) {
    for (const [, y] of contour) {
      minY = Math.min(minY, y);
      maxY = Math.max(maxY, y);
    }
  }
  const yStart = Math.max(0, Math.floor(minY));
  const yEnd = Math.min(canvas.h - 1, Math.ceil(maxY));

  for (let y = yStart; y <= yEnd; y++) {
    const scanY = y + 0.5;
    const xs = [];
    for (const contour of scaled) {
      for (let i = 0; i < contour.length; i++) {
        const p1 = contour[i];
        const p2 = contour[(i + 1) % contour.length];
        if (Math.abs(p1[1] - p2[1]) < 0.0001) continue;
        const minEdgeY = Math.min(p1[1], p2[1]);
        const maxEdgeY = Math.max(p1[1], p2[1]);
        if (scanY < minEdgeY || scanY >= maxEdgeY) continue;
        const x = p1[0] + ((scanY - p1[1]) * (p2[0] - p1[0])) / (p2[1] - p1[1]);
        const wind = p2[1] > p1[1] ? 1 : -1;
        xs.push([x, wind]);
      }
    }
    xs.sort((a, b) => a[0] - b[0]);

    if (evenOdd) {
      for (let i = 0; i + 1 < xs.length; i += 2) {
        const x0 = Math.max(0, Math.ceil(xs[i][0]));
        const x1 = Math.min(canvas.w - 1, Math.floor(xs[i + 1][0]));
        canvas.pixels.fill(gray, y * canvas.w + x0, y * canvas.w + x1 + 1);
      }
    } else {
      let winding = 0;
      let startX = null;
      for (const [x, wind] of xs) {
        const prev = winding;
        winding += wind;
        if (prev === 0 && winding !== 0) startX = x;
        else if (prev !== 0 && winding === 0 && startX !== null) {
          const x0 = Math.max(0, Math.ceil(startX));
          const x1 = Math.min(canvas.w - 1, Math.floor(x));
          if (x1 >= x0) canvas.pixels.fill(gray, y * canvas.w + x0, y * canvas.w + x1 + 1);
          startX = null;
        }
      }
    }
  }
}

function rasterize(content, width, height) {
  const canvas = makeCanvas(width, height);
  const tokens = tokenize(content);
  const stateStack = [];
  let state = { ctm: [1, 0, 0, 1, 0, 0], fill: 0, stroke: 0, lineWidth: 1 };
  let stack = [];
  let contours = [];
  let currentContour = null;
  let current = [0, 0];
  let contourStart = [0, 0];

  function startContour(p) {
    currentContour = [p];
    contours.push(currentContour);
    current = p;
    contourStart = p;
  }

  function addPoint(p) {
    if (!currentContour) startContour(current);
    currentContour.push(p);
    current = p;
  }

  function closeContour() {
    if (currentContour && currentContour.length > 1) {
      const last = currentContour[currentContour.length - 1];
      if (Math.abs(last[0] - contourStart[0]) > 0.001 || Math.abs(last[1] - contourStart[1]) > 0.001) {
        currentContour.push(contourStart);
      }
    }
    current = contourStart;
    currentContour = null;
  }

  function paint(kind, evenOdd) {
    if (kind === "stroke" || kind === "both") {
      for (const contour of contours) {
        for (let i = 0; i + 1 < contour.length; i++) drawLine(canvas, contour[i], contour[i + 1], state.stroke, state.lineWidth);
      }
    }
    if (kind === "fill" || kind === "both") fillContours(canvas, contours, state.fill, evenOdd);
    contours = [];
    currentContour = null;
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
    if (token === "[" || token === "]") continue;

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
        state.fill = grayFromStack(stack);
        break;
      case "RG":
      case "G":
        state.stroke = grayFromStack(stack);
        break;
      case "w": {
        const vals = numberStack(1);
        if (vals) state.lineWidth = Math.max(0.1, Math.abs(vals[0]));
        stack = [];
        break;
      }
      case "m": {
        const vals = numberStack(2);
        if (vals) startContour(transform(state.ctm, vals[0], vals[1]));
        stack = [];
        break;
      }
      case "l": {
        const vals = numberStack(2);
        if (vals) addPoint(transform(state.ctm, vals[0], vals[1]));
        stack = [];
        break;
      }
      case "c": {
        const vals = numberStack(6);
        if (vals) {
          const p1 = transform(state.ctm, vals[0], vals[1]);
          const p2 = transform(state.ctm, vals[2], vals[3]);
          const p3 = transform(state.ctm, vals[4], vals[5]);
          for (const p of flattenCubic(current, p1, p2, p3)) addPoint(p);
        }
        stack = [];
        break;
      }
      case "v": {
        const vals = numberStack(4);
        if (vals) {
          const p2 = transform(state.ctm, vals[0], vals[1]);
          const p3 = transform(state.ctm, vals[2], vals[3]);
          for (const p of flattenCubic(current, current, p2, p3)) addPoint(p);
        }
        stack = [];
        break;
      }
      case "y": {
        const vals = numberStack(4);
        if (vals) {
          const p1 = transform(state.ctm, vals[0], vals[1]);
          const p3 = transform(state.ctm, vals[2], vals[3]);
          for (const p of flattenCubic(current, p1, p3, p3)) addPoint(p);
        }
        stack = [];
        break;
      }
      case "h":
        closeContour();
        stack = [];
        break;
      case "re": {
        const vals = numberStack(4);
        if (vals) {
          const [x, y, w, h] = vals;
          startContour(transform(state.ctm, x, y));
          addPoint(transform(state.ctm, x + w, y));
          addPoint(transform(state.ctm, x + w, y + h));
          addPoint(transform(state.ctm, x, y + h));
          closeContour();
        }
        stack = [];
        break;
      }
      case "S":
        paint("stroke", false);
        break;
      case "s":
        closeContour();
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
        closeContour();
        paint("both", false);
        break;
      case "b*":
        closeContour();
        paint("both", true);
        break;
      case "n":
        contours = [];
        currentContour = null;
        stack = [];
        break;
      default:
        stack = [];
        break;
    }
  }
  return canvas;
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
  const canvas = flipY(rasterize(content, width, height));
  const file = path.join(outDir, `page_${String(i + 1).padStart(2, "0")}.png`);
  writeGrayPng(file, canvas.w, canvas.h, canvas.pixels);
  console.log(`Wrote ${file}`);
}
