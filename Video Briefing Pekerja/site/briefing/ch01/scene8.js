'use strict';
const PRE8 = 0.8;
function scene8(p, D) { const cam = paperCam(p, 'kertas'); stopClock(D, (q, f) => { cam.apply(q, f); }); }
