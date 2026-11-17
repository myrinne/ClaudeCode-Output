'use strict';
const PRE3 = 0.8;
function scene3(p, D) { const cam = paperCam(p, 'kertas'); stopClock(D, (q, f) => { cam.apply(q, f); }); }
