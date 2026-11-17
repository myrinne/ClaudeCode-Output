'use strict';
const PRE5 = 0.8;
function scene5(p, D) { const cam = paperCam(p, 'kertas'); stopClock(D, (q, f) => { cam.apply(q, f); }); }
