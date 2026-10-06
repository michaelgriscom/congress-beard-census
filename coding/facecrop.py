import cv2, numpy as np
from PIL import Image, ImageOps
_front = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
_prof = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
MIN_WEIGHT = 2.0   # Haar level weight below this is usually a false detection

def _best(cascade, g, minsz, H):
    rects, _, weights = cascade.detectMultiScale3(g, 1.05, 6, minSize=(minsz, minsz), outputRejectLevels=True)
    best = None
    for (x, y, w, h), wt in zip(rects, np.ravel(weights) if len(rects) else []):
        if y + h / 2 > 0.65 * H or wt < MIN_WEIGHT:   # faces sit in the upper part of a portrait
            continue
        if best is None or wt * w > best[1] * best[0][2]:
            best = ((x, y, w, h), wt)
    return best

def load_cropped(path):
    """Return (image, cropped?) cropped to head, chin and beard; the full image if no confident face."""
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    g = cv2.equalizeHist(cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2GRAY))
    W, H = im.size; minsz = max(20, min(W, H) // 12)
    best = _best(_front, g, minsz, H) or _best(_prof, g, minsz, H)
    if not best:
        return im, False
    x, y, w, h = best[0]
    if w * h > 0.2 * W * H:            # already a close-up
        return im, False
    box = (max(0, x - 0.7 * w), max(0, y - 0.6 * h), min(W, x + 1.7 * w), min(H, y + 2.3 * h))
    return im.crop(tuple(int(v) for v in box)), True
