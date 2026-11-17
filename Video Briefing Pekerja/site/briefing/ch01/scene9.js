'use strict';
const PRE9 = 0.8;
function scene9(p, D) { const cam = paperCam(p, 'kertas'); stopClock(D, (q, f) => { cam.apply(q, f); }); }
