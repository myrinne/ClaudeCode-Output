'use strict';
const PRE6 = 0.8;
function scene6(p, D) { const cam = paperCam(p, 'kertas'); stopClock(D, (q, f) => { cam.apply(q, f); }); }
