'use strict';
const PRE2 = 0.8;
function scene2(p, D) { const cam = paperCam(p, 'kertas'); stopClock(D, (q, f) => { cam.apply(q, f); }); }
