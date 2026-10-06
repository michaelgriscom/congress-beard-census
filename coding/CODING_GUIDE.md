# Facial-hair coding guide

Each contact sheet shows up to 24 portraits in a 6 x 4 grid. Each cell has a black
label with its position number, 0 to 23, reading left to right, top to bottom.
Give every cell exactly one code letter:

| Code | Meaning | Examples |
| ---- | ------- | -------- |
| F | Full beard: hair on the chin AND a mustache, with the beard running along the jaw or cheeks (any length, including short trimmed beards) | Grant, Garfield, Hayes |
| G | Goatee or Van Dyke: mustache plus a beard on the chin only, with the cheeks and jaw clearly shaved | |
| B | Beard with NO mustache: chin beard, chin curtain or neck beard with a shaved upper lip | Lincoln, Horace Greeley |
| S | Sideburns or mutton chops: whiskers on the cheeks that do NOT join across the chin, with or without a mustache | Chester Arthur, Burnside |
| M | Mustache only | Theodore Roosevelt, Taft |
| C | Clean-shaven (stubble counts as clean-shaven) | McKinley |
| W | Woman | |
| X | Unusable: no single face visible, blank cell, a scene or group, or too small or blurry to judge | |

Rules:
- Judge only what is visible. If you can't tell, pick the most likely code; use X only
  when there is genuinely nothing to judge.
- A thin fringe of whiskers under the jaw with a shaved chin front and upper lip is B.
- Engravings and paintings count; judge them the same way as photographs.
- If a beard covers the chin and you can't see whether there's a mustache, use F.
- Portraits are automatically cropped to the face. If a crop missed and the cell shows
  no face (only a body, hands, a chair), code X; those get re-checked uncropped.
