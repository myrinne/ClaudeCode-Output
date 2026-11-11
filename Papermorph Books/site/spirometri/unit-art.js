// Chalk sketches for the unit headers on the contents page, one per unit, drawn in the unit's colour.
// Each entry is the inside of an SVG with viewBox 0 0 600 180; keep the left ~200 px light (the unit title sits there
// on narrow screens). Classes, styled in lib/units.css:
//   d  a stroke that draws itself in when the unit scrolls into view (--k orders the strokes)
//   t  text or a filled shape that fades in
//   a  faint chalk white instead of the unit colour;  faint  even fainter
// A sketch may add one looping motion after it is drawn: give an element a class that lib/units.css animates (swap-a,
// hop, orbit, ride, spin, tilt, breathe, ...), or add your own .seen .unit-art .NAME rule and keyframes in a <style> in index.html.
'use strict';
(() => {
  let k = 0;
  const P = (d, cls = '', extra = '') => `<path class="d ${cls}" pathLength="1" style="--k:${k++}" d="${d}" ${extra}/>`;
  const Tx = (x, y, s, size = 24, cls = '', anchor = 'start') => `<text class="t ${cls}" style="--k:${k++}" x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}">${s}</text>`;
  const C = (cx, cy, r, cls = '') => `<circle class="d ${cls}" pathLength="1" style="--k:${k++}" cx="${cx}" cy="${cy}" r="${r}"/>`;
  const reset = s => { k = 0; return s; };

  window.UNIT_ART = [
    // 1 Spirometri Okupasi: a normal flow-volume curve and a scooped obstructive one, schematic.
    reset(
      P('M232 150H574', 'a') +
      P('M232 150V30', 'a') +
      P('M232 150 C236 90 240 44 256 40 L560 150', '') +
      P('M232 150 C236 118 240 92 256 88 C320 118 400 146 520 150', 'a') +
      Tx(574, 170, 'volume', 16, 'a', 'end') +
      Tx(240, 26, 'aliran', 16, 'a') +
      Tx(400, 76, 'normal', 18, '') +
      Tx(300, 136, 'obstruksi', 16, 'a')
    ),
  ];
})();
