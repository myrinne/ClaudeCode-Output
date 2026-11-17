'use strict';
const PRE7 = 0.8;
function scene7(p, D) { const cam = paperCam(p, 'kertas'); stopClock(D, (q, f) => { cam.apply(q, f); }); }
