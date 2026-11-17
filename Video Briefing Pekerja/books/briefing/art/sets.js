// Paper sets, drawn once and baked to bitmaps: uv run --with playwright --with pillow python SKILL/scripts/bake_sets.py
//   books/<book>/art/sets.js site/<book>
// The paper filters are too heavy to run on large layers every frame. Each set is a function returning a list of
// layers back to front: {name, k, box: [x, y, w, h] in world px, scale, svg, soft?}.
//   k      parallax: 1 moves with the puppets' plane, below 1 is farther (slides less when the camera pans).
//   scale  bitmap pixels per world px (1.2 is plenty for a 1600 x 900 frame; raise it for layers a close-up fills).
//   soft   false skips the blurred -soft copy (use it for small foreground pieces); the camera swaps the copy in for
//          shallow focus on close shots.
//   stage  true: the puppets stand in front of this layer (paperCam's default `after`).
// Without a stage mark the puppets stand on the first k = 1 layer ('floor' below) and in front of it; layers after it
// hide them (the table). Mark another layer when the puppets belong further forward, e.g. in front of a tree that is
// itself in front of the bank, with the water and the near bank still over them.
// Give a layer more room than the 1600 x 900 frame (here -100 … 1700) so a pan or shake never shows its edge.
// These sketches are a finished look on their own (free) and the composition reference an image model repaints:
// bake one, give the picture to paint.py as a reference, and put the result in with painted.py.
const DEFS = `<defs>
  <filter id="paper" x="-15%" y="-15%" width="130%" height="135%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="3" result="warp"/>
    <feDisplacementMap in="SourceGraphic" in2="warp" scale="3.5" xChannelSelector="R" yChannelSelector="G" result="cut"/>
    <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="3" seed="7" result="fib"/>
    <feColorMatrix in="fib" type="matrix" values="0 0 0 0 .25  0 0 0 0 .17  0 0 0 0 .08  .5 0 0 0 -.14" result="tint"/>
    <feComposite in="tint" in2="cut" operator="in" result="grain"/>
    <feMerge result="tex"><feMergeNode in="cut"/><feMergeNode in="grain"/></feMerge>
    <feDropShadow in="tex" dx="2.5" dy="3.5" stdDeviation="2.2" flood-color="#2a1608" flood-opacity=".38"/>
  </filter>
  <filter id="paperBig" x="-5%" y="-10%" width="110%" height="125%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="5" result="warp"/>
    <feDisplacementMap in="SourceGraphic" in2="warp" scale="5" xChannelSelector="R" yChannelSelector="G" result="cut"/>
    <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="3" seed="11" result="fib"/>
    <feColorMatrix in="fib" type="matrix" values="0 0 0 0 .25  0 0 0 0 .17  0 0 0 0 .08  .5 0 0 0 -.15" result="tint"/>
    <feComposite in="tint" in2="cut" operator="in" result="grain"/>
    <feMerge result="tex"><feMergeNode in="cut"/><feMergeNode in="grain"/></feMerge>
    <feDropShadow in="tex" dx="4" dy="6" stdDeviation="5" flood-color="#2a1608" flood-opacity=".32"/>
  </filter>
</defs>`;
// Wrap shapes in the paper filter: 'paper' for pieces, 'paperBig' for large flat areas.
const P = (body, f = 'paper') => `<g filter="url(#${f})">${body}</g>`;
const win = (x, y, w, h, glass = '#9cc6de', frame = '#f4f1ea') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${glass}"/><path d="M${x},${y} h${w} v${h} h${-w} Z M${x + w / 2},${y} v${h}" fill="none" stroke="${frame}" stroke-width="6"/>`;

// Dapur Instalasi Gizi: ubin krem, rak panci, kompor dengan api, meja stainless, jendela.
function dapur() {
  const tiles = Array.from({ length: 22 }, (_, i) => `<path d="M${-100 + i * 90},-60 v800" stroke="#e2d6bb" stroke-width="3"/>`).join('')
    + Array.from({ length: 9 }, (_, i) => `<path d="M-100,${i * 90 - 40} h1800" stroke="#e2d6bb" stroke-width="3"/>`).join('');
  const wall = P(`<rect x="-100" y="-60" width="1800" height="800" fill="#f1e7cf"/>${tiles}`, 'paperBig')
    + P(`${win(1180, 90, 280, 250, '#bfe0ee')}`)
    + P(`<rect x="60" y="120" width="620" height="14" rx="5" fill="#8b949a"/>${[0, 1, 2, 3].map(i => `<path d="M${130 + i * 150},134 v34" stroke="#8b949a" stroke-width="5"/><path d="M${100 + i * 150},168 h60 v70 q-30,16 -60,0 Z" fill="${['#c9d1d6', '#9aa4ab', '#d9a05b', '#c9d1d6'][i]}"/>`).join('')}`);
  const back = P(`<rect x="-100" y="470" width="1800" height="240" fill="#b9c2c7"/><rect x="-100" y="456" width="1800" height="26" fill="#d6dde1"/>
      ${Array.from({ length: 9 }, (_, i) => `<rect x="${-60 + i * 200}" y="500" width="170" height="190" rx="8" fill="none" stroke="#9aa4ab" stroke-width="5"/>`).join('')}
      <rect x="150" y="360" width="400" height="100" rx="10" fill="#6c757b"/>
      ${[0, 1, 2].map(i => `<ellipse cx="${230 + i * 130}" cy="450" rx="46" ry="12" fill="#2d3336"/><path d="M${210 + i * 130},440 q20,-60 40,0 q-20,-18 -40,0 Z" fill="#f08a2c"/><path d="M${222 + i * 130},440 q8,-34 16,0 Z" fill="#ffd36b"/>`).join('')}`);
  const floor = P(`<rect x="-100" y="700" width="1800" height="320" fill="#b88b63"/>${Array.from({ length: 8 }, (_, i) => `<path d="M-100,${730 + i * 36} h1800" stroke="#a37a55" stroke-width="3"/>`).join('')}`, 'paperBig');
  return [
    { name: 'wall', k: .85, box: [-100, -60, 1800, 800], scale: 1.2, svg: wall },
    { name: 'back', k: .92, box: [-100, 350, 1800, 360], scale: 1.2, svg: back },
    { name: 'floor', k: 1, box: [-100, 690, 1800, 330], scale: 1.2, svg: floor },
  ];
}
// Ruang istirahat/pemeriksaan: dinding biru-hijau lembut, AC, bangku, pintu, poster.
function ruang() {
  const wall = P(`<rect x="-100" y="-60" width="1800" height="800" fill="#d6ebe9"/>`, 'paperBig')
    + P(`<rect x="120" y="90" width="520" height="120" rx="14" fill="#f4f7f7"/>${[0, 1, 2, 3, 4].map(i => `<path d="M${180 + i * 90},215 q10,28 0,56" stroke="#8cc7d9" stroke-width="5" fill="none" stroke-linecap="round"/>`).join('')}`)
    + P(`<rect x="1060" y="150" width="250" height="330" rx="8" fill="#f4f1ea"/><rect x="1085" y="180" width="200" height="90" fill="#7ec0e0"/><path d="M1085,270 l50,-50 l45,35 l50,-40 l55,55 Z" fill="#6f9a6a"/><path d="M1090,310 h190 M1090,345 h150 M1090,380 h170" stroke="#9aa9aa" stroke-width="8" stroke-linecap="round"/>`)
    + P(`<rect x="1380" y="220" width="200" height="480" rx="6" fill="#b9d0cd"/><circle cx="1405" cy="470" r="9" fill="#8a9a98"/>`);
  const floor = P(`<rect x="-100" y="700" width="1800" height="320" fill="#e6d9c0"/>${Array.from({ length: 8 }, (_, i) => `<path d="M-100,${730 + i * 36} h1800" stroke="#d6c8ac" stroke-width="3"/>`).join('')}`, 'paperBig');
  const bench = P(`<rect x="170" y="600" width="520" height="34" rx="8" fill="#9a7b58"/><rect x="200" y="634" width="26" height="150" fill="#7d6044"/><rect x="630" y="634" width="26" height="150" fill="#7d6044"/>`);
  return [
    { name: 'wall', k: .85, box: [-100, -60, 1800, 800], scale: 1.2, svg: wall },
    { name: 'floor', k: 1, box: [-100, 690, 1800, 330], scale: 1.2, svg: floor },
    { name: 'bench', k: 1, box: [130, 560, 600, 260], scale: 1.4, soft: false, svg: bench },
  ];
}
// Kertas polos hangat untuk infografik dan formulir (tokoh boleh berdiri di depannya).
function kertas() {
  const wall = P(`<rect x="-100" y="-60" width="1800" height="1000" fill="#f6efdc"/>`, 'paperBig')
    + P(`<path d="M-100,160 Q400,120 800,170 T1700,150 V-60 H-100 Z" fill="#ecdfc0"/>`);
  const floor = P(`<rect x="-100" y="760" width="1800" height="260" fill="#e8d9b8"/>`, 'paperBig');
  return [
    { name: 'wall', k: .9, box: [-100, -60, 1800, 1000], scale: 1.1, svg: wall },
    { name: 'floor', k: 1, box: [-100, 750, 1800, 270], scale: 1.1, svg: floor },
  ];
}

const SETS = { dapur, ruang, kertas };
if (typeof window !== 'undefined') window.SETS = SETS, window.SET_DEFS = DEFS;
