/* forearm.js: one drawing of a forearm for every icon that shows "lengan bawah" (video utama, pengingat).
   A palm-up forearm lying horizontally: elbow on the left, wrist crease, palm, four fingers and a thumb on the right.
   About 252 wide and 88 tall, centred on (0, 0) like the other paper icons; pf() is the paper-filtered group of cast.js.
   FOREARM({ tat: true })    adds a small blue star tattoo on the inner forearm
   FOREARM({ sleeve: true }) adds a green work-uniform sleeve at the elbow end
   Load after cast.js. */
'use strict';
function FOREARM({ tat = false, sleeve = false } = {}) {
  const skin = '#e8be98', light = '#f3d6b8', shade = '#cf9f79';
  const fingers = [[-22, 50], [-7, 56], [8, 50], [22, 40]]
    .map(([y, len]) => `<rect x="92" y="${y - 7}" width="${len}" height="14" rx="7" fill="${skin}"/>`).join('');
  const thumb = `<ellipse cx="60" cy="-31" rx="25" ry="11" transform="rotate(-32 60 -31)" fill="${skin}"/>`;
  const body = `<path d="M-112,-30 Q-112,-44 -96,-43 C-50,-44 0,-34 42,-27 L42,27 C0,34 -50,44 -96,43 Q-112,44 -112,30 Z" fill="${skin}"/>`;
  const inner = `<path d="M-92,-9 C-40,-19 0,-15 40,-9 L40,9 C0,15 -40,19 -92,9 Z" fill="${light}" opacity=".6"/>`;
  const palm = `<ellipse cx="72" cy="0" rx="34" ry="30" fill="${skin}"/>`;
  const crease = `<path d="M44,-24 q8,24 0,48" stroke="${shade}" stroke-width="3.5" fill="none" stroke-linecap="round"/>`
    + `<path d="M58,-6 q18,6 34,-2" stroke="${shade}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".7"/>`;
  let svg = pf(thumb + fingers + palm + body + inner + crease);
  if (tat) svg += `<g transform="translate(-34 0) scale(1.15)"><path d="M0,-15 L4.5,-4.5 L16,-4.5 L7,2.5 L10,14 L0,7.5 L-10,14 L-7,2.5 L-16,-4.5 L-4.5,-4.5 Z" fill="#2f4a8a"/></g>`;
  if (sleeve) svg += pf(`<rect x="-122" y="-47" width="66" height="94" rx="16" fill="#4f9a6a"/><path d="M-70,-44 v88" stroke="#f4f1ea" stroke-width="5"/>`);
  return svg;
}
