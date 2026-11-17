'use strict';
const PRE4 = 0.8;
function scene4(p, D) { const cam = paperCam(p, 'kertas'); stopClock(D, (q, f) => { cam.apply(q, f); }); }
