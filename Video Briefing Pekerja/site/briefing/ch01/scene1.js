'use strict';
const PRE1 = 0.8;
function scene1(p, D) { const cam = paperCam(p, 'kertas'); stopClock(D, (q, f) => { cam.apply(q, f); }); }
