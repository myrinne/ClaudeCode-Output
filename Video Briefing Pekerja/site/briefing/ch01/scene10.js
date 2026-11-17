'use strict';
const PRE10 = 0.8;
function scene10(p, D) { const cam = paperCam(p, 'kertas'); stopClock(D, (q, f) => { cam.apply(q, f); }); }
