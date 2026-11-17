'use strict';
const PRE11 = 0.8;
function scene11(p, D) { const cam = paperCam(p, 'kertas'); stopClock(D, (q, f) => { cam.apply(q, f); }); }
