import React, { useState, useEffect, useMemo, useCallback, useRef } from "react";
import Papa from "papaparse";
import {
  ChevronRight,
  ChevronDown,
  Search,
  Plus,
  Upload,
  Star,
  Heart,
  X,
  Loader2,
  BookOpen,
  Feather,
  Trees,
  Sparkles,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/*  THEMES                                                             */
/* ------------------------------------------------------------------ */

const THEMES = {
  emerald: {
    label: "Emerald Athenaeum",
    bg: "#0c1f16",
    bg2: "#173321",
    surface: "#152b1d",
    surface2: "#1c3826",
    parchment: "#f6ecd4",
    parchmentDark: "#e9dcb8",
    primary: "#2d6a4f",
    primaryLight: "#4f9c78",
    accent: "#d4af37",
    accentSoft: "#eeda9a",
    text: "#f1e9d2",
    ink: "#2a2115",
    muted: "#a8c3b0",
    border: "#3d6b4f",
    trunk: "#4a3728",
    leaf: "#4f7a63",
    leafDark: "#24402f",
    flower: "#d4af37",
  },
  rose: {
    label: "Midnight Rose",
    bg: "#210c15",
    bg2: "#3a1626",
    surface: "#2c101c",
    surface2: "#3d1625",
    parchment: "#f7e9e4",
    parchmentDark: "#ecd3ca",
    primary: "#7a1f3d",
    primaryLight: "#b0446a",
    accent: "#d9a6a1",
    accentSoft: "#f0c9c2",
    text: "#f5e6ea",
    ink: "#2c1218",
    muted: "#c99aa8",
    border: "#5c2438",
    trunk: "#3d2418",
    leaf: "#6b2c42",
    leafDark: "#39131f",
    flower: "#e3bdb8",
  },
  sapphire: {
    label: "Sapphire Chronicles",
    bg: "#081522",
    bg2: "#152338",
    surface: "#0f1d30",
    surface2: "#182a45",
    parchment: "#eef2f9",
    parchmentDark: "#dbe3f0",
    primary: "#1d4e89",
    primaryLight: "#3d76bd",
    accent: "#c9d6e8",
    accentSoft: "#e7edf8",
    text: "#e8eef7",
    ink: "#101d2e",
    muted: "#9fb3cc",
    border: "#2a4870",
    trunk: "#2f2419",
    leaf: "#274472",
    leafDark: "#0f1d30",
    flower: "#dce6f4",
  },
  amethyst: {
    label: "Amethyst Grimoire",
    bg: "#170b25",
    bg2: "#2a1640",
    surface: "#1e0f34",
    surface2: "#2e1747",
    parchment: "#f2e9f7",
    parchmentDark: "#e2d1ee",
    primary: "#6b3fa0",
    primaryLight: "#9a6ecb",
    accent: "#c9a660",
    accentSoft: "#e5cb8f",
    text: "#ede4f7",
    ink: "#211031",
    muted: "#b79fd4",
    border: "#4a2a6e",
    trunk: "#3d2818",
    leaf: "#5b3a7a",
    leafDark: "#241238",
    flower: "#d8bd7a",
  },
};

const STATUS_OPTIONS = ["Want to Read", "Currently Reading", "Read"];
const FILTERS = ["All", "Favorites", "Read", "Currently Reading", "Want to Read"];

/* ------------------------------------------------------------------ */
/*  HELPERS                                                            */
/* ------------------------------------------------------------------ */

const uid = () => Math.random().toString(36).slice(2) + Date.now().toString(36);

function emptyBook(overrides = {}) {
  return {
    id: uid(),
    title: "",
    author: "",
    series: "",
    seriesNumber: "",
    genre: "",
    isbn: "",
    rating: 0,
    status: "Want to Read",
    favorite: false,
    cover: "",
    description: "",
    publisher: "",
    pages: "",
    dateRead: "",
    ...overrides,
  };
}

async function fetchCoverByISBN(isbn) {
  const clean = (isbn || "").replace(/[^0-9Xx]/g, "");
  if (!clean) return null;
  try {
    const res = await fetch(
      `https://openlibrary.org/api/books?bibkeys=ISBN:${clean}&format=json&jscmd=data`
    );
    const data = await res.json();
    const entry = data[`ISBN:${clean}`];
    if (entry && entry.cover) {
      return entry.cover.large || entry.cover.medium || entry.cover.small || null;
    }
  } catch (e) {
    /* ignore, fall through */
  }
  return null;
}

async function fetchFromGoogleBooks(title, author, isbn) {
  try {
    let q;
    if (isbn) {
      q = `isbn:${(isbn || "").replace(/[^0-9Xx]/g, "")}`;
    } else {
      q = `intitle:${title || ""}${author ? "+inauthor:" + author : ""}`;
    }
    const res = await fetch(
      `https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(q)}&maxResults=1`
    );
    const data = await res.json();
    const item = data.items && data.items[0];
    if (!item) return null;
    const info = item.volumeInfo || {};
    return {
      cover: info.imageLinks
        ? (info.imageLinks.thumbnail || info.imageLinks.smallThumbnail || "").replace(
            "http://",
            "https://"
          )
        : null,
      description: info.description || "",
      publisher: info.publisher || "",
      pages: info.pageCount || "",
      genre: (info.categories && info.categories[0]) || "",
    };
  } catch (e) {
    return null;
  }
}

async function lookupBookInfo({ title, author, isbn }) {
  let cover = await fetchCoverByISBN(isbn);
  let extra = null;
  if (!cover) {
    extra = await fetchFromGoogleBooks(title, author, isbn);
    if (extra && extra.cover) cover = extra.cover;
  }
  return { cover, extra };
}

function parseSeriesFromTitle(rawTitle) {
  const m = rawTitle.match(/^(.*?)\s*\(([^,()]+),\s*#?([\d.]+)\)\s*$/);
  if (m) {
    return { title: m[1].trim(), series: m[2].trim(), seriesNumber: m[3].trim() };
  }
  return { title: rawTitle.trim(), series: "", seriesNumber: "" };
}

function mapGoodreadsShelf(shelf) {
  const s = (shelf || "").toLowerCase();
  if (s.includes("currently")) return "Currently Reading";
  if (s.includes("read")) return "Read";
  return "Want to Read";
}

function buildTree(books) {
  const authors = {};
  books.forEach((b) => {
    const authorName = b.author && b.author.trim() ? b.author.trim() : "Unknown Author";
    if (!authors[authorName]) {
      authors[authorName] = { name: authorName, seriesMap: {}, standalone: [] };
    }
    if (b.series && b.series.trim()) {
      const sName = b.series.trim();
      if (!authors[authorName].seriesMap[sName]) {
        authors[authorName].seriesMap[sName] = { name: sName, books: [] };
      }
      authors[authorName].seriesMap[sName].books.push(b);
    } else {
      authors[authorName].standalone.push(b);
    }
  });
  Object.values(authors).forEach((a) => {
    Object.values(a.seriesMap).forEach((s) => {
      s.books.sort((x, y) => (parseFloat(x.seriesNumber) || 0) - (parseFloat(y.seriesNumber) || 0));
    });
  });
  return Object.values(authors).sort((a, b) => a.name.localeCompare(b.name));
}

function patternDataUri(color) {
  const c = encodeURIComponent(color);
  const svg =
    "<svg xmlns='http://www.w3.org/2000/svg' width='84' height='84'>" +
    `<g fill='none' stroke='${color}' stroke-width='1' opacity='0.10'>` +
    "<path d='M42 10 C50 24 64 26 42 42 C20 26 34 24 42 10 Z'/>" +
    "<circle cx='12' cy='64' r='2.4' fill='" + color + "' stroke='none' opacity='0.14'/>" +
    "<circle cx='72' cy='64' r='2.4' fill='" + color + "' stroke='none' opacity='0.14'/>" +
    "<path d='M0 74 C 14 68, 28 68, 42 74 C 56 68, 70 68, 84 74' opacity='0.08'/>" +
    "</g></svg>";
  return `url("data:image/svg+xml,${svg.replace(/#/g, "%23").replace(/'/g, "%27")}")`;
}

/* ------------------------------------------------------------------ */
/*  DECORATIVE PIECES                                                  */
/* ------------------------------------------------------------------ */

function Flourish({ compact }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10, margin: compact ? "6px 0 14px" : "4px 0 22px" }}>
      <svg width="70" height="14" viewBox="0 0 70 14">
        <path d="M0 7 C 20 1, 40 13, 68 7" fill="none" stroke="var(--accent)" strokeWidth="1.1" opacity="0.75" />
      </svg>
      <svg width="11" height="11" viewBox="0 0 11 11">
        <path d="M5.5 0 L8 4 L11 5.5 L8 7 L5.5 11 L3 7 L0 5.5 L3 4 Z" fill="var(--accent)" opacity="0.85" />
      </svg>
      <svg width="70" height="14" viewBox="0 0 70 14">
        <path d="M70 7 C 50 1, 30 13, 2 7" fill="none" stroke="var(--accent)" strokeWidth="1.1" opacity="0.75" />
      </svg>
    </div>
  );
}

function CornerFlourish({ corner }) {
  const flips = {
    tl: "scaleX(1) scaleY(1)",
    tr: "scaleX(-1) scaleY(1)",
    bl: "scaleX(1) scaleY(-1)",
    br: "scaleX(-1) scaleY(-1)",
  };
  const pos = {
    tl: { top: -2, left: -2 },
    tr: { top: -2, right: -2 },
    bl: { bottom: -2, left: -2 },
    br: { bottom: -2, right: -2 },
  };
  return (
    <svg
      width="46"
      height="46"
      viewBox="0 0 46 46"
      style={{ position: "absolute", ...pos[corner], transform: flips[corner], pointerEvents: "none" }}
    >
      <path
        d="M2 2 C 2 20, 6 30, 26 34 C 14 34, 4 30, 2 44"
        fill="none"
        stroke="var(--accent)"
        strokeWidth="1.4"
        opacity="0.65"
      />
      <path d="M2 2 C 14 2, 24 6, 30 18" fill="none" stroke="var(--accent)" strokeWidth="1.4" opacity="0.65" />
      <circle cx="2" cy="2" r="2.6" fill="var(--accent)" opacity="0.85" />
      <circle cx="26" cy="34" r="1.8" fill="var(--accent)" opacity="0.6" />
      <circle cx="30" cy="18" r="1.8" fill="var(--accent)" opacity="0.6" />
    </svg>
  );
}

function OrnateFrame({ children, style }) {
  return (
    <div
      style={{
        position: "relative",
        border: "1px solid var(--border)",
        borderRadius: 18,
        boxShadow:
          "0 0 0 1px rgba(212,175,55,0.18), 0 18px 40px rgba(0,0,0,0.45), inset 0 0 40px rgba(0,0,0,0.25)",
        ...style,
      }}
    >
      <CornerFlourish corner="tl" />
      <CornerFlourish corner="tr" />
      <CornerFlourish corner="bl" />
      <CornerFlourish corner="br" />
      {children}
    </div>
  );
}

function SectionTitle({ children }) {
  return (
    <div style={{ textAlign: "center" }}>
      <div
        style={{
          fontFamily: "'Berkshire Swash', cursive",
          fontSize: 24,
          color: "var(--accentSoft)",
          textShadow: "0 2px 10px rgba(0,0,0,0.4)",
        }}
      >
        {children}
      </div>
      <Flourish compact />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  SMALL UI PIECES                                                    */
/* ------------------------------------------------------------------ */

function Stars({ value, onChange, size = 16 }) {
  return (
    <div style={{ display: "flex", gap: 2 }}>
      {[1, 2, 3, 4, 5].map((n) => (
        <Star
          key={n}
          size={size}
          onClick={onChange ? () => onChange(n === value ? 0 : n) : undefined}
          style={{
            cursor: onChange ? "pointer" : "default",
            fill: n <= value ? "var(--accent)" : "transparent",
            color: "var(--accent)",
            filter: n <= value ? "drop-shadow(0 0 3px rgba(212,175,55,0.5))" : "none",
          }}
        />
      ))}
    </div>
  );
}

function Cover({ book, width = 64 }) {
  const height = Math.round(width * 1.5);
  const spineWidth = Math.max(3, Math.round(width * 0.07));
  if (book.cover) {
    return (
      <div style={{ position: "relative", width, height, flexShrink: 0 }}>
        <img
          src={book.cover}
          alt={book.title}
          width={width}
          height={height}
          style={{
            objectFit: "cover",
            borderRadius: "2px 5px 5px 2px",
            boxShadow: "3px 5px 14px rgba(0,0,0,0.55), 0 0 0 1px rgba(0,0,0,0.35)",
            display: "block",
          }}
        />
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            bottom: 0,
            width: spineWidth,
            background: "linear-gradient(90deg, rgba(0,0,0,0.55), rgba(0,0,0,0))",
            borderRadius: "2px 0 0 2px",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            borderRadius: "2px 5px 5px 2px",
            boxShadow: "inset 0 0 0 1px rgba(255,255,255,0.08)",
          }}
        />
      </div>
    );
  }
  return (
    <div
      style={{
        width,
        height,
        borderRadius: "2px 5px 5px 2px",
        background:
          "repeating-linear-gradient(135deg, var(--surface2), var(--surface2) 6px, var(--bg2) 6px, var(--bg2) 12px)",
        border: "1px solid var(--border)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        boxShadow: "3px 5px 14px rgba(0,0,0,0.5)",
        flexShrink: 0,
      }}
    >
      <Feather size={Math.round(width * 0.34)} color="var(--accent)" opacity={0.7} />
    </div>
  );
}

function StatusPill({ status }) {
  const colors = {
    Read: "var(--primaryLight)",
    "Currently Reading": "var(--accent)",
    "Want to Read": "var(--muted)",
  };
  return (
    <span
      style={{
        fontSize: 10.5,
        letterSpacing: 0.8,
        textTransform: "uppercase",
        fontFamily: "'Cormorant Garamond', serif",
        fontWeight: 600,
        padding: "3px 10px",
        borderRadius: 999,
        border: `1px solid ${colors[status] || "var(--muted)"}`,
        color: colors[status] || "var(--muted)",
        whiteSpace: "nowrap",
        background: "rgba(0,0,0,0.15)",
      }}
    >
      {status}
    </span>
  );
}

/* ------------------------------------------------------------------ */
/*  WILLOW TREE HEADER SVG                                             */
/* ------------------------------------------------------------------ */

function WillowTree() {
  // Canopy built from soft overlapping masses (not a scatter of tiny twigs)
  const canopy = [
    { x: 410, y: 55, r: 72 },
    { x: 300, y: 72, r: 54 },
    { x: 520, y: 72, r: 54 },
    { x: 205, y: 96, r: 42 },
    { x: 615, y: 96, r: 42 },
    { x: 130, y: 118, r: 32 },
    { x: 690, y: 118, r: 32 },
  ];

  // Hanging strands: fewer, longer, gracefully curved, leaf tuft only at the tip
  const strands = [
    { x: 130, y: 128, len: 92, sway: -18 },
    { x: 178, y: 116, len: 118, sway: 14 },
    { x: 235, y: 104, len: 96, sway: -12 },
    { x: 300, y: 96, len: 130, sway: 10 },
    { x: 360, y: 90, len: 108, sway: -14 },
    { x: 410, y: 88, len: 140, sway: 6 },
    { x: 460, y: 90, len: 108, sway: 14 },
    { x: 520, y: 96, len: 130, sway: -10 },
    { x: 585, y: 104, len: 96, sway: 12 },
    { x: 642, y: 116, len: 118, sway: -14 },
    { x: 690, y: 128, len: 92, sway: 18 },
  ];

  return (
    <svg viewBox="0 0 820 270" width="100%" height="100%" style={{ display: "block" }}>
      <defs>
        <radialGradient id="willowGlow" cx="50%" cy="28%" r="55%">
          <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.18" />
          <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="canopyGrad" cx="38%" cy="30%" r="75%">
          <stop offset="0%" stopColor="var(--leaf)" />
          <stop offset="65%" stopColor="var(--leaf)" />
          <stop offset="100%" stopColor="var(--leafDark)" />
        </radialGradient>
      </defs>

      <ellipse cx="410" cy="95" rx="330" ry="100" fill="url(#willowGlow)" />

      {/* Hanging strands — drawn first so the canopy overlaps their tops */}
      <g>
        {strands.map((s, i) => (
          <g key={i}>
            <path
              d={`M${s.x} ${s.y} C ${s.x + s.sway * 0.4} ${s.y + s.len * 0.45}, ${s.x - s.sway * 0.3} ${
                s.y + s.len * 0.8
              }, ${s.x + s.sway * 0.15} ${s.y + s.len}`}
              fill="none"
              stroke="var(--leaf)"
              strokeWidth="1.6"
              strokeLinecap="round"
              opacity="0.75"
            />
            <ellipse
              cx={s.x + s.sway * 0.15}
              cy={s.y + s.len}
              rx="6"
              ry="3"
              fill={i % 4 === 0 ? "var(--flower)" : "var(--leaf)"}
              opacity="0.9"
              transform={`rotate(${s.sway > 0 ? 30 : -30} ${s.x + s.sway * 0.15} ${s.y + s.len})`}
            />
          </g>
        ))}
      </g>

      {/* Trunk — a single tapered filled shape, not a stroked line */}
      <path
        d="M394 244 C 389 205, 384 168, 392 128 C 396 104, 388 84, 400 40
           L 412 40 C 421 84, 414 104, 419 128 C 428 168, 424 205, 420 244 Z"
        fill="var(--trunk)"
      />
      <path
        d="M356 246 C 372 220, 390 220, 396 244 M 414 244 C 420 220, 438 220, 456 246"
        fill="none"
        stroke="var(--trunk)"
        strokeWidth="7"
        strokeLinecap="round"
        opacity="0.85"
      />
      <path d="M401 190 C 399 160, 403 130, 400 100" fill="none" stroke="var(--bg)" strokeWidth="1.2" opacity="0.25" />

      {/* Canopy — soft overlapping masses */}
      <g>
        {canopy.map((c, i) => (
          <circle key={"shadow" + i} cx={c.x + 5} cy={c.y + 7} r={c.r} fill="var(--leafDark)" opacity="0.35" />
        ))}
        {canopy.map((c, i) => (
          <circle key={"base" + i} cx={c.x} cy={c.y} r={c.r} fill="url(#canopyGrad)" />
        ))}
        {canopy.map((c, i) => (
          <circle
            key={"hi" + i}
            cx={c.x - c.r * 0.32}
            cy={c.y - c.r * 0.35}
            r={c.r * 0.5}
            fill="var(--accentSoft)"
            opacity="0.14"
          />
        ))}
      </g>

      {/* Sparse blossoms across the canopy */}
      {[
        [340, 45], [410, 30], [480, 45], [260, 78], [560, 78], [200, 105], [620, 105],
      ].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="3.4" fill="var(--flower)" opacity="0.85" />
      ))}

      {/* Base vine flourish under the trunk */}
      <path
        d="M300 258 C 340 248, 380 256, 410 250 C 440 256, 480 248, 520 258"
        fill="none"
        stroke="var(--accent)"
        strokeWidth="1.3"
        opacity="0.6"
      />
      {[330, 375, 410, 445, 490].map((x, i) => (
        <circle key={i} cx={x} cy={i % 2 === 0 ? 253 : 250} r="2.2" fill="var(--accent)" opacity="0.7" />
      ))}
    </svg>
  );
}

/* ------------------------------------------------------------------ */
/*  STAT ORNAMENT                                                      */
/* ------------------------------------------------------------------ */

function StatOrnament({ label, value, icon: Icon }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <svg width="18" height="20" viewBox="0 0 18 20" style={{ marginBottom: -2 }}>
        <path d="M9 0 L9 14" stroke="var(--accent)" strokeWidth="1" opacity="0.6" />
        <path d="M2 14 Q 9 20 16 14" fill="none" stroke="var(--accent)" strokeWidth="1" opacity="0.5" />
      </svg>
      <div
        style={{
          position: "relative",
          width: 92,
          height: 92,
          borderRadius: "50%",
          background: "radial-gradient(circle at 32% 28%, var(--surface2), var(--surface) 70%)",
          border: "2px solid var(--accent)",
          boxShadow:
            "0 6px 16px rgba(0,0,0,0.4), inset 0 0 14px rgba(0,0,0,0.35), 0 0 0 4px rgba(212,175,55,0.08)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 2,
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 4,
            borderRadius: "50%",
            border: "1px solid var(--accent)",
            opacity: 0.4,
          }}
        />
        <Icon size={15} color="var(--accent)" />
        <div
          style={{
            fontFamily: "'Berkshire Swash', cursive",
            fontSize: 21,
            color: "var(--accentSoft)",
            lineHeight: 1,
            textShadow: "0 1px 6px rgba(0,0,0,0.5)",
          }}
        >
          {value}
        </div>
        <div
          style={{
            fontSize: 9,
            letterSpacing: 0.8,
            textTransform: "uppercase",
            color: "var(--muted)",
            fontFamily: "'Cormorant Garamond', serif",
          }}
        >
          {label}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  ADD / EDIT BOOK FORM                                               */
/* ------------------------------------------------------------------ */

function Field({ label, children, full }) {
  return (
    <div style={{ gridColumn: full ? "1 / -1" : "auto" }}>
      <label
        style={{
          fontSize: 11.5,
          letterSpacing: 0.9,
          textTransform: "uppercase",
          color: "var(--muted)",
          marginBottom: 6,
          display: "block",
          fontFamily: "'Cormorant Garamond', serif",
        }}
      >
        {label}
      </label>
      {children}
    </div>
  );
}

function BookForm({ initial, onSave, onCancel }) {
  const [book, setBook] = useState(initial || emptyBook());
  const [looking, setLooking] = useState(false);

  const set = (field) => (e) => setBook((b) => ({ ...b, [field]: e && e.target ? e.target.value : e }));

  const doLookup = async () => {
    if (!book.title && !book.isbn) return;
    setLooking(true);
    const { cover, extra } = await lookupBookInfo(book);
    setBook((b) => ({
      ...b,
      cover: cover || b.cover,
      description: b.description || (extra && extra.description) || "",
      publisher: b.publisher || (extra && extra.publisher) || "",
      pages: b.pages || (extra && extra.pages) || "",
      genre: b.genre || (extra && extra.genre) || "",
    }));
    setLooking(false);
  };

  const inputStyle = {
    width: "100%",
    padding: "10px 4px",
    borderRadius: 0,
    border: "none",
    borderBottom: "1.5px solid var(--border)",
    background: "transparent",
    color: "var(--text)",
    fontFamily: "'EB Garamond', serif",
    fontSize: 16,
    outline: "none",
    transition: "border-color 0.2s",
  };

  return (
    <OrnateFrame style={{ background: "linear-gradient(180deg, var(--surface), var(--surface2))", padding: 30 }}>
      <SectionTitle>{initial ? "Revise This Volume" : "A New Leaf"}</SectionTitle>
      <div style={{ display: "flex", gap: 26, flexWrap: "wrap" }}>
        <div style={{ flexShrink: 0, margin: "0 auto" }}>
          <Cover book={book} width={120} />
          <button
            onClick={doLookup}
            disabled={looking}
            style={{
              marginTop: 12,
              width: 120,
              fontSize: 12,
              padding: "7px 4px",
              borderRadius: 999,
              border: "1px solid var(--accent)",
              background: "transparent",
              color: "var(--accentSoft)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 5,
              fontFamily: "'Cormorant Garamond', serif",
              letterSpacing: 0.4,
            }}
          >
            {looking ? <Loader2 size={13} className="spin" /> : <Sparkles size={13} />}
            {looking ? "Seeking…" : "Find Cover"}
          </button>
        </div>

        <div style={{ flex: 1, minWidth: 280, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
          <Field label="Title" full>
            <input style={inputStyle} value={book.title} onChange={set("title")} placeholder="The Enchanted Bindery" />
          </Field>
          <Field label="Author">
            <input style={inputStyle} value={book.author} onChange={set("author")} />
          </Field>
          <Field label="Genre">
            <input style={inputStyle} value={book.genre} onChange={set("genre")} />
          </Field>
          <Field label="Series">
            <input style={inputStyle} value={book.series} onChange={set("series")} placeholder="optional" />
          </Field>
          <Field label="Series No.">
            <input style={inputStyle} value={book.seriesNumber} onChange={set("seriesNumber")} placeholder="optional" />
          </Field>
          <Field label="ISBN">
            <input style={inputStyle} value={book.isbn} onChange={set("isbn")} />
          </Field>
          <Field label="Status">
            <select style={inputStyle} value={book.status} onChange={set("status")}>
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s} style={{ background: "var(--surface)" }}>
                  {s}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Publisher">
            <input style={inputStyle} value={book.publisher} onChange={set("publisher")} />
          </Field>
          <Field label="Pages">
            <input style={inputStyle} value={book.pages} onChange={set("pages")} />
          </Field>
          <Field label="Date Read">
            <input type="date" style={inputStyle} value={book.dateRead} onChange={set("dateRead")} />
          </Field>
          <Field label="Favorite">
            <button
              type="button"
              onClick={() => setBook((b) => ({ ...b, favorite: !b.favorite }))}
              style={{ background: "none", border: "none", cursor: "pointer", padding: "8px 0" }}
            >
              <Heart
                size={22}
                style={{
                  fill: book.favorite ? "var(--primaryLight)" : "transparent",
                  color: "var(--primaryLight)",
                }}
              />
            </button>
          </Field>
          <Field label="My Rating" full>
            <Stars value={book.rating} onChange={(v) => setBook((b) => ({ ...b, rating: v }))} size={21} />
          </Field>
          <Field label="Description" full>
            <textarea
              style={{ ...inputStyle, minHeight: 76, resize: "vertical", border: "1px solid var(--border)", borderRadius: 8, padding: 10 }}
              value={book.description}
              onChange={set("description")}
            />
          </Field>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "center", gap: 14, marginTop: 28 }}>
        <button onClick={onCancel} className="btn-ghost">
          Cancel
        </button>
        <button onClick={() => book.title.trim() && onSave(book)} className="btn-gold">
          Save to the Tree
        </button>
      </div>
    </OrnateFrame>
  );
}

/* ------------------------------------------------------------------ */
/*  BOOK ROW / CARD                                                     */
/* ------------------------------------------------------------------ */

function BookRow({ book, onToggleFavorite, onClick }) {
  return (
    <div onClick={onClick} className="book-row">
      <Cover book={book} width={44} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: 17.5, color: "var(--text)", fontWeight: 600 }}>
          {book.title}
          {book.seriesNumber ? <span style={{ color: "var(--muted)", fontSize: 13, fontWeight: 400 }}> · Vol. {book.seriesNumber}</span> : null}
        </div>
        <div style={{ fontSize: 13, color: "var(--muted)", display: "flex", gap: 10, flexWrap: "wrap", marginTop: 3, alignItems: "center", fontFamily: "'EB Garamond', serif", fontStyle: "italic" }}>
          <span>{book.genre || "Unclassified"}</span>
          {book.rating ? <Stars value={book.rating} size={11} /> : null}
        </div>
      </div>
      <StatusPill status={book.status} />
      <button
        onClick={(e) => {
          e.stopPropagation();
          onToggleFavorite(book.id);
        }}
        style={{ background: "none", border: "none", cursor: "pointer", flexShrink: 0 }}
      >
        <Heart size={17} style={{ fill: book.favorite ? "var(--primaryLight)" : "transparent", color: "var(--primaryLight)" }} />
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  TREE VIEW                                                          */
/* ------------------------------------------------------------------ */

/* ---- Genealogy-style node chart ---- */

function TreeNode({ title, subtitle, icon: Icon, kind, open, onClick, badge }) {
  const kindStyles = {
    root: {
      minWidth: 168,
      padding: "16px 22px",
      background: "radial-gradient(circle at 30% 25%, var(--surface2), var(--surface))",
      border: "2.5px solid var(--accent)",
      fontFamily: "'Berkshire Swash', cursive",
      fontSize: 20,
      boxShadow: "0 8px 22px rgba(0,0,0,0.5), 0 0 0 5px rgba(212,175,55,0.08)",
    },
    author: {
      minWidth: 148,
      padding: "12px 18px",
      background: "linear-gradient(135deg, var(--surface2), var(--surface))",
      border: "2px solid var(--accent)",
      fontFamily: "'Cormorant Garamond', serif",
      fontWeight: 700,
      fontSize: 16.5,
      boxShadow: "0 6px 16px rgba(0,0,0,0.4)",
    },
    series: {
      minWidth: 128,
      padding: "9px 15px",
      background: "rgba(0,0,0,0.22)",
      border: "1.5px solid var(--border)",
      fontFamily: "'Cormorant Garamond', serif",
      fontStyle: "italic",
      fontWeight: 600,
      fontSize: 14.5,
      boxShadow: "0 4px 10px rgba(0,0,0,0.3)",
    },
  };
  const st = kindStyles[kind];
  return (
    <button onClick={onClick} className="tree-node" style={{ ...st, position: "relative" }}>
      {badge != null && (
        <span
          style={{
            position: "absolute",
            top: -9,
            right: -9,
            background: "var(--primary)",
            color: "#fff",
            border: "1.5px solid var(--accent)",
            borderRadius: 999,
            fontSize: 10.5,
            fontFamily: "'Cormorant Garamond', serif",
            padding: "1px 7px",
            fontWeight: 700,
          }}
        >
          {badge}
        </span>
      )}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 7 }}>
        {Icon && <Icon size={kind === "root" ? 17 : 14} color="var(--accent)" />}
        <span style={{ color: kind === "root" ? "var(--accentSoft)" : "var(--text)" }}>{title}</span>
        {onClick && (open ? <ChevronDown size={13} color="var(--muted)" /> : <ChevronRight size={13} color="var(--muted)" />)}
      </div>
      {subtitle && <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 2, fontFamily: "'EB Garamond', serif", fontStyle: "italic" }}>{subtitle}</div>}
    </button>
  );
}

// Simple connector: a vertical stem down from parent, horizontal rail across children, vertical drops into each child
function Branches({ children }) {
  const count = React.Children.count(children);
  if (count === 0) return null;
  return (
    <div style={{ position: "relative", width: "100%" }}>
      <div className="branch-stem" />
      {count > 1 && (
        <div
          style={{
            height: 1.5,
            background: "var(--accent)",
            opacity: 0.5,
            margin: "0 auto",
            maxWidth: `${Math.min(94, count * 15)}%`,
          }}
        />
      )}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: 28,
          flexWrap: "wrap",
          paddingTop: 14,
        }}
      >
        {children}
      </div>
    </div>
  );
}

function Twig({ children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", position: "relative" }}>
      <div style={{ width: 1.5, height: 14, background: "var(--accent)", opacity: 0.6 }} />
      {children}
    </div>
  );
}

function TreeView({ tree, onToggleFavorite, onOpenBook }) {
  const [expandedAuthors, setExpandedAuthors] = useState(new Set());
  const [expandedSeries, setExpandedSeries] = useState(new Set());
  const [focusedBooks, setFocusedBooks] = useState(null); // { title, books }

  const toggleAuthor = (name) =>
    setExpandedAuthors((s) => {
      const n = new Set(s);
      n.has(name) ? n.delete(name) : n.add(name);
      return n;
    });
  const toggleSeries = (key) =>
    setExpandedSeries((s) => {
      const n = new Set(s);
      n.has(key) ? n.delete(key) : n.add(key);
      return n;
    });

  if (tree.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "60px 20px", color: "var(--muted)" }}>
        <Trees size={40} color="var(--accent)" style={{ marginBottom: 10 }} />
        <div style={{ fontFamily: "'Berkshire Swash', cursive", fontSize: 22, color: "var(--accentSoft)" }}>
          Your tree awaits its first leaf
        </div>
        <div style={{ marginTop: 6, fontFamily: "'EB Garamond', serif", fontStyle: "italic" }}>
          Add a book to begin growing your library.
        </div>
      </div>
    );
  }

  return (
    <div style={{ overflowX: "auto", paddingBottom: 10 }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", minWidth: 640 }}>
        {/* Root */}
        <TreeNode title="My Library" icon={Trees} kind="root" />

        {/* Authors */}
        <Branches>
          {tree.map((author) => {
            const authorOpen = expandedAuthors.has(author.name);
            const seriesList = Object.values(author.seriesMap);
            const totalBooks = author.standalone.length + seriesList.reduce((n, s) => n + s.books.length, 0);
            return (
              <Twig key={author.name}>
                <TreeNode
                  title={author.name}
                  icon={Feather}
                  kind="author"
                  open={authorOpen}
                  badge={totalBooks}
                  onClick={() => toggleAuthor(author.name)}
                />

                {authorOpen && (
                  <Branches>
                    {seriesList.map((s) => {
                      const key = author.name + "::" + s.name;
                      const seriesOpen = expandedSeries.has(key);
                      return (
                        <Twig key={key}>
                          <TreeNode
                            title={s.name}
                            icon={BookOpen}
                            kind="series"
                            open={seriesOpen}
                            badge={s.books.length}
                            onClick={() => toggleSeries(key)}
                          />
                          {seriesOpen && (
                            <Branches>
                              {s.books.map((b) => (
                                <Twig key={b.id}>
                                  <div onClick={() => onOpenBook(b)} style={{ cursor: "pointer" }}>
                                    <Cover book={b} width={58} />
                                    <div
                                      style={{
                                        marginTop: 4,
                                        maxWidth: 76,
                                        fontSize: 11,
                                        textAlign: "center",
                                        color: "var(--muted)",
                                        fontFamily: "'Cormorant Garamond', serif",
                                      }}
                                    >
                                      Vol. {b.seriesNumber || "–"}
                                    </div>
                                  </div>
                                </Twig>
                              ))}
                            </Branches>
                          )}
                        </Twig>
                      );
                    })}
                    {author.standalone.map((b) => (
                      <Twig key={b.id}>
                        <div onClick={() => onOpenBook(b)} style={{ cursor: "pointer" }}>
                          <Cover book={b} width={58} />
                        </div>
                      </Twig>
                    ))}
                  </Branches>
                )}
              </Twig>
            );
          })}
        </Branches>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  IMPORT PANEL                                                       */
/* ------------------------------------------------------------------ */

function ImportPanel({ onImport }) {
  const [status, setStatus] = useState("");
  const [progress, setProgress] = useState(null);
  const fileRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    setStatus("Reading file…");
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (results) => {
        const rows = results.data;
        setStatus(`Parsed ${rows.length} rows. Fetching covers…`);
        const newBooks = [];
        for (let i = 0; i < rows.length; i++) {
          const row = rows[i];
          const rawTitle = row["Title"] || row["title"] || "";
          if (!rawTitle.trim()) continue;
          const { title, series, seriesNumber } = parseSeriesFromTitle(rawTitle);
          const isbn = (row["ISBN13"] || row["ISBN"] || row["isbn"] || "").replace(/[="]/g, "");
          const book = emptyBook({
            title,
            author: row["Author"] || row["author"] || "",
            series,
            seriesNumber,
            genre: row["Genre"] || row["Bookshelves"] || "",
            isbn,
            rating: parseInt(row["My Rating"] || row["Rating"] || "0", 10) || 0,
            status: mapGoodreadsShelf(row["Exclusive Shelf"] || row["Shelf"] || row["shelf"]),
            publisher: row["Publisher"] || "",
            pages: row["Number of Pages"] || row["Pages"] || "",
            dateRead: row["Date Read"] || "",
          });
          setProgress({ current: i + 1, total: rows.length });
          const cover = await fetchCoverByISBN(book.isbn);
          book.cover = cover || "";
          newBooks.push(book);
        }
        setProgress(null);
        setStatus(`Woven ${newBooks.length} books into your tree.`);
        onImport(newBooks);
      },
      error: () => setStatus("Something went wrong reading that file."),
    });
  };

  return (
    <OrnateFrame style={{ background: "linear-gradient(180deg, var(--surface), var(--surface2))", padding: 34, textAlign: "center" }}>
      <Upload size={28} color="var(--accent)" style={{ marginBottom: 8 }} />
      <SectionTitle>Import Your Library</SectionTitle>
      <p style={{ color: "var(--muted)", maxWidth: 460, margin: "0 auto 20px", fontFamily: "'EB Garamond', serif", fontSize: 16, lineHeight: 1.6, fontStyle: "italic" }}>
        Bring in a CSV export from Goodreads or any compatible library file. Series, series numbers,
        and covers will be discovered automatically.
      </p>
      <input ref={fileRef} type="file" accept=".csv" style={{ display: "none" }} onChange={(e) => handleFile(e.target.files[0])} />
      <button onClick={() => fileRef.current && fileRef.current.click()} className="btn-gold">
        Choose CSV File
      </button>
      {status && (
        <div style={{ marginTop: 18, color: "var(--accentSoft)", fontFamily: "'EB Garamond', serif" }}>
          {status}
          {progress && (
            <div style={{ marginTop: 10, fontSize: 13, color: "var(--muted)" }}>
              <div style={{ width: 220, height: 4, background: "var(--surface2)", borderRadius: 4, margin: "0 auto", overflow: "hidden" }}>
                <div style={{ width: `${(progress.current / progress.total) * 100}%`, height: "100%", background: "var(--accent)", transition: "width 0.2s" }} />
              </div>
              <div style={{ marginTop: 6 }}>{progress.current} / {progress.total}</div>
            </div>
          )}
        </div>
      )}
    </OrnateFrame>
  );
}

/* ------------------------------------------------------------------ */
/*  MAIN APP                                                           */
/* ------------------------------------------------------------------ */

export default function MyBookTree() {
  const [themeKey, setThemeKey] = useState("emerald");
  const [books, setBooks] = useState([]);
  const [view, setView] = useState("tree");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const [editingBook, setEditingBook] = useState(null);
  const [loaded, setLoaded] = useState(false);

  const theme = THEMES[themeKey];

  useEffect(() => {
    (async () => {
      try {
        const b = await window.storage.get("books", false);
        if (b && b.value) setBooks(JSON.parse(b.value));
      } catch (e) {}
      try {
        const t = await window.storage.get("theme", false);
        if (t && t.value) setThemeKey(t.value);
      } catch (e) {}
      setLoaded(true);
    })();
  }, []);

  useEffect(() => {
    if (!loaded) return;
    window.storage.set("books", JSON.stringify(books), false).catch(() => {});
  }, [books, loaded]);

  useEffect(() => {
    if (!loaded) return;
    window.storage.set("theme", themeKey, false).catch(() => {});
  }, [themeKey, loaded]);

  const stats = useMemo(() => {
    const authors = new Set(books.map((b) => b.author || "Unknown Author"));
    const series = new Set(books.filter((b) => b.series).map((b) => b.author + "::" + b.series));
    return {
      books: books.length,
      authors: authors.size,
      series: series.size,
      read: books.filter((b) => b.status === "Read").length,
      favorites: books.filter((b) => b.favorite).length,
    };
  }, [books]);

  const filteredBooks = useMemo(() => {
    let list = books;
    if (filter === "Favorites") list = list.filter((b) => b.favorite);
    else if (filter !== "All") list = list.filter((b) => b.status === filter);
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (b) =>
          (b.title || "").toLowerCase().includes(q) ||
          (b.author || "").toLowerCase().includes(q) ||
          (b.series || "").toLowerCase().includes(q) ||
          (b.genre || "").toLowerCase().includes(q)
      );
    }
    return list;
  }, [books, filter, search]);

  const tree = useMemo(() => buildTree(filteredBooks), [filteredBooks]);

  const toggleFavorite = useCallback((id) => {
    setBooks((bs) => bs.map((b) => (b.id === id ? { ...b, favorite: !b.favorite } : b)));
  }, []);

  const saveBook = (book) => {
    setBooks((bs) => {
      const exists = bs.some((b) => b.id === book.id);
      return exists ? bs.map((b) => (b.id === book.id ? book : b)) : [...bs, book];
    });
    setEditingBook(null);
    setView("tree");
  };

  const importBooks = (newBooks) => {
    setBooks((bs) => [...bs, ...newBooks]);
  };

  const cssVars = {
    "--bg": theme.bg,
    "--bg2": theme.bg2,
    "--surface": theme.surface,
    "--surface2": theme.surface2,
    "--primary": theme.primary,
    "--primaryLight": theme.primaryLight,
    "--accent": theme.accent,
    "--accentSoft": theme.accentSoft,
    "--text": theme.text,
    "--muted": theme.muted,
    "--border": theme.border,
    "--trunk": theme.trunk,
    "--leaf": theme.leaf,
    "--leafDark": theme.leafDark,
    "--flower": theme.flower,
  };

  const navBtn = (key, label, Icon) => (
    <button
      onClick={() => {
        setEditingBook(null);
        setView(key);
      }}
      className={`nav-pill ${view === key ? "active" : ""}`}
    >
      <Icon size={14} />
      {label}
    </button>
  );

  return (
    <div
      style={{
        ...cssVars,
        minHeight: "100vh",
        background: `radial-gradient(ellipse 900px 500px at 50% 0%, var(--bg2), var(--bg) 65%), ${patternDataUri(theme.accent)}`,
        backgroundBlendMode: "normal, overlay",
        backgroundSize: "auto, 84px 84px",
      }}
      className="book-tree-app"
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,500&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap');
        .book-tree-app * { box-sizing: border-box; }
        .book-tree-app { font-family: 'EB Garamond', serif; }
        .book-row {
          display: flex; gap: 13px; align-items: center;
          padding: 10px 12px; border-radius: 10px; cursor: pointer;
          transition: background 0.18s, transform 0.18s;
          border: 1px solid transparent;
        }
        .book-row:hover { background: var(--surface2); border-color: var(--border); transform: translateX(2px); }
        .tree-node {
          border-radius: 12px;
          cursor: pointer;
          text-align: center;
          transition: transform 0.18s, box-shadow 0.18s, border-color 0.18s;
        }
        .tree-node:hover { transform: translateY(-2px); border-color: var(--accentSoft); }
        .branch-stem {
          width: 1.5px;
          height: 22px;
          background: var(--accent);
          opacity: 0.6;
          margin: 0 auto;
        }
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }
        ::selection { background: var(--accent); color: var(--ink); }
        input:focus, select:focus, textarea:focus { border-color: var(--accent) !important; outline: none; }
        input, select, textarea { font-family: 'EB Garamond', serif; }

        .nav-pill {
          display: flex; align-items: center; gap: 7px;
          padding: 9px 18px; border-radius: 999px;
          border: 1px solid var(--border);
          background: rgba(0,0,0,0.15);
          color: var(--muted);
          cursor: pointer;
          font-family: 'Cormorant Garamond', serif;
          font-size: 15.5px; font-weight: 600; letter-spacing: 0.3px;
          transition: all 0.2s;
        }
        .nav-pill:hover { border-color: var(--accent); color: var(--accentSoft); }
        .nav-pill.active {
          border-color: var(--accent);
          background: linear-gradient(135deg, var(--surface2), var(--surface));
          color: var(--accentSoft);
          box-shadow: 0 3px 12px rgba(0,0,0,0.35), inset 0 0 0 1px rgba(212,175,55,0.15);
        }

        .btn-gold {
          padding: 11px 30px; border-radius: 999px; border: 1px solid var(--accent);
          background: linear-gradient(135deg, var(--primary), var(--primaryLight));
          color: #fff; cursor: pointer; font-weight: 700;
          font-family: 'Cormorant Garamond', serif; font-size: 16px; letter-spacing: 0.4px;
          box-shadow: 0 6px 18px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.25);
          transition: transform 0.15s, box-shadow 0.15s;
        }
        .btn-gold:hover { transform: translateY(-1px); box-shadow: 0 8px 22px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.3); }
        .btn-ghost {
          padding: 11px 24px; border-radius: 999px; border: 1px solid var(--border);
          background: transparent; color: var(--muted); cursor: pointer;
          font-family: 'Cormorant Garamond', serif; font-size: 16px;
          transition: all 0.15s;
        }
        .btn-ghost:hover { color: var(--accentSoft); border-color: var(--accent); }

        .theme-select {
          appearance: none; -webkit-appearance: none; background-image: none;
        }
      `}</style>

      <div style={{ maxWidth: 900, margin: "0 auto", padding: "36px 20px 90px" }}>
        {/* Theme dropdown */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 8 }}>
          <select
            className="theme-select"
            value={themeKey}
            onChange={(e) => setThemeKey(e.target.value)}
            style={{
              padding: "8px 18px",
              borderRadius: 999,
              border: "1px solid var(--accent)",
              background: "linear-gradient(135deg, var(--surface2), var(--surface))",
              color: "var(--accentSoft)",
              fontFamily: "'Cormorant Garamond', serif",
              fontSize: 14.5,
              cursor: "pointer",
              boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
            }}
          >
            {Object.entries(THEMES).map(([key, t]) => (
              <option key={key} value={key} style={{ background: t.surface, color: t.text }}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        {/* Header */}
        <div style={{ textAlign: "center" }}>
          <h1
            style={{
              fontFamily: "'Berkshire Swash', cursive",
              fontSize: "clamp(40px, 6.4vw, 62px)",
              color: "var(--accentSoft)",
              margin: 0,
              textShadow: "0 3px 22px rgba(0,0,0,0.5), 0 0 40px rgba(212,175,55,0.15)",
              letterSpacing: 0.6,
            }}
          >
            My Book Tree
          </h1>
        </div>
        <div style={{ height: 200, margin: "-8px 0 4px" }}>
          <WillowTree />
        </div>

        {/* Stats ornaments */}
        <div style={{ display: "flex", justifyContent: "center", gap: 16, flexWrap: "wrap", marginBottom: 34, marginTop: 4 }}>
          <StatOrnament label="Books" value={stats.books} icon={BookOpen} />
          <StatOrnament label="Authors" value={stats.authors} icon={Feather} />
          <StatOrnament label="Series" value={stats.series} icon={Trees} />
          <StatOrnament label="Read" value={stats.read} icon={Sparkles} />
          <StatOrnament label="Favorites" value={stats.favorites} icon={Heart} />
        </div>

        {/* Nav */}
        <div style={{ display: "flex", justifyContent: "center", gap: 10, flexWrap: "wrap", marginBottom: 26 }}>
          {navBtn("tree", "Book Tree", Trees)}
          {navBtn("books", "All Books", BookOpen)}
          {navBtn("add", "Add Book", Plus)}
          {navBtn("import", "Import Library", Upload)}
        </div>

        {/* Search + filter */}
        {(view === "tree" || view === "books") && (
          <div style={{ marginBottom: 22 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                background: "linear-gradient(135deg, var(--surface), var(--surface2))",
                border: "1px solid var(--border)",
                borderRadius: 999,
                padding: "11px 20px",
                marginBottom: 14,
                boxShadow: "inset 0 2px 8px rgba(0,0,0,0.25)",
              }}
            >
              <Search size={16} color="var(--accent)" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search title, author, series, or genre…"
                style={{
                  border: "none",
                  outline: "none",
                  background: "transparent",
                  color: "var(--text)",
                  fontSize: 15.5,
                  flex: 1,
                  fontStyle: "italic",
                }}
              />
              {search && <X size={15} color="var(--muted)" style={{ cursor: "pointer" }} onClick={() => setSearch("")} />}
            </div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center" }}>
              {FILTERS.map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  style={{
                    padding: "6px 15px",
                    borderRadius: 999,
                    border: `1px solid ${filter === f ? "var(--accent)" : "var(--border)"}`,
                    background: filter === f ? "var(--surface2)" : "transparent",
                    color: filter === f ? "var(--accentSoft)" : "var(--muted)",
                    fontSize: 13,
                    cursor: "pointer",
                    fontFamily: "'Cormorant Garamond', serif",
                  }}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Content */}
        {(view === "tree" || view === "books") && (
          <OrnateFrame style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.14), rgba(0,0,0,0.22))", padding: 24 }}>
            {view === "tree" && <TreeView tree={tree} onToggleFavorite={toggleFavorite} onOpenBook={setEditingBook} />}
            {view === "books" && (
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                {filteredBooks.length === 0 && (
                  <div style={{ textAlign: "center", padding: 40, color: "var(--muted)", fontStyle: "italic" }}>
                    No books match yet.
                  </div>
                )}
                {filteredBooks.map((b) => (
                  <BookRow key={b.id} book={b} onToggleFavorite={toggleFavorite} onClick={() => setEditingBook(b)} />
                ))}
              </div>
            )}
          </OrnateFrame>
        )}

        {view === "add" && !editingBook && <BookForm onSave={saveBook} onCancel={() => setView("tree")} />}
        {view === "import" && <ImportPanel onImport={importBooks} />}

        {editingBook && (
          <div
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(0,0,0,0.65)",
              backdropFilter: "blur(3px)",
              display: "flex",
              alignItems: "flex-start",
              justifyContent: "center",
              padding: "40px 16px",
              overflowY: "auto",
              zIndex: 50,
            }}
            onClick={(e) => e.target === e.currentTarget && setEditingBook(null)}
          >
            <div style={{ width: "100%", maxWidth: 720 }}>
              <BookForm initial={editingBook} onSave={saveBook} onCancel={() => setEditingBook(null)} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
