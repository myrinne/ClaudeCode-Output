# Long corridor: image prompts (Gemini / ChatGPT)

One continuous corridor, same shell everywhere, a different clinician at each station.
Generate 4 segments at 3:1 (about 2172 x 724). Attach `images/corridor-01-ortho.png` to every request as the STYLE reference.

## Shared block (paste at the top of every prompt)

Style: semi-flat vector illustration, soft gradient shading, no outlines, matte, muted teal and warm cream palette with ONE coral accent. Isometric cutaway of a long clinic corridor, same wall colour, same floor, same lighting, same camera angle as the attached image. NO dividing walls and NO end walls: the corridor continues past both the left and right edge of the picture. A single flat coral ribbon, about 8 percent of the image height, runs along the back wall at a fixed height (centre at 39 percent from the top) and leaves the left and right edges at exactly that height. Minimal faces, every person drawn differently, no hijab on the clinicians. Patients are workers (one in a hard hat or hi-vis vest). Generic corridor, not a specialty clinic: only the clinician's equipment shows the specialty. 3:1 panorama.

## Segment 1: orthopaedic surgeon
Left to right: a worker with a wrist or knee injury sits on an exam stool; an orthopaedic surgeon in teal scrubs points at a lit X-ray of a spine on the wall and holds a clipboard; a small bone model on a trolley. Open doorway frames at the far left and far right edges, no door shut.

## Segment 2: physiotherapist
A physiotherapist in a teal polo guides a worker walking between parallel bars; a second worker does a leg press on a rehab machine; a few steps for stair practice; a knee-flexion poster.

## Segment 3: occupational doctor / nurse (vaccination)
A nurse gives an injection into the upper arm of a seated worker in a hi-vis vest; a small table with vials and a vaccination schedule card; a fridge cabinet; a hand-wash station.

## Segment 4: acupuncturist
An acupuncturist in a cream tunic places fine needles in the back of a worker lying face down on a treatment table; a small moxa stick with a curl of smoke; a meridian chart on the wall; a folded towel.

## Joining the segments
- Edge rule: the last 5 percent of segment N and the first 5 percent of segment N+1 must show the same empty corridor wall, floor and the coral ribbon at 39 percent height.
- Better join: after segment 1, ask "extend this image to the right by 100 percent, same style, new scene: [segment 2 description]" instead of a new image. Repeat for 3 and 4, then crop.
