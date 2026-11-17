"""camera.py - take one fresh photo and find the item on the blue tray.

The camera is a Logitech C270 USB webcam, 640 x 480, 35 cm above the tray,
looking straight down. The tray is blue and no item is blue, so the item is
"everything that is not tray blue".
"""
import numpy as np

try:
    import cv2
except ImportError:          # lets the bill and filter tests run on a machine without OpenCV
    cv2 = None

WIDTH, HEIGHT = 640, 480
WARM_UP_FRAMES = 5           # thrown away after opening: exposure settles
FLUSH_FRAMES = 4             # buffered frames thrown away before each photo
MIN_ITEM_PIXELS = 400        # a smaller blob is a speck, not an item

# The tray in HSV colour space: hue 90..130 is blue (OpenCV hue runs 0..179).
TRAY_LOW = (90, 80, 50)
TRAY_HIGH = (130, 255, 255)


class Camera:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError(f"camera {index} not found (is it plugged in? is /dev/video{index} there?)")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        for _ in range(WARM_UP_FRAMES):          # the first frames are often too dark
            self.cap.read()

    def take_photo(self):
        """One fresh BGR frame (480, 640, 3), or None if the camera failed."""
        for _ in range(FLUSH_FRAMES):            # drop frames that waited in the queue
            self.cap.grab()
        ok, frame = self.cap.read()              # this one is taken now
        return frame if ok else None

    def close(self):
        self.cap.release()


class FakeCamera:
    """For laptop demos: draws a blue tray with a coloured round 'item' on it."""

    def __init__(self, seed=0):
        self.rng = np.random.default_rng(seed)
        self.colour = (40, 40, 200)             # BGR, set by the demo

    def take_photo(self):
        frame = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
        frame[:] = (200, 120, 40)                # tray blue in BGR
        cx, cy = self.rng.integers(220, 420), self.rng.integers(160, 320)
        cv2.circle(frame, (int(cx), int(cy)), int(self.rng.integers(45, 80)), self.colour, -1)
        return frame

    def close(self):
        pass


def find_item_box(bgr):
    """The box (x, y, w, h) around the biggest non-blue blob, or None if the tray looks empty."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    tray = cv2.inRange(hsv, TRAY_LOW, TRAY_HIGH)            # 255 where the pixel is tray blue
    item = cv2.bitwise_not(tray)                            # 255 where it is NOT tray blue
    kernel = np.ones((5, 5), np.uint8)
    item = cv2.morphologyEx(item, cv2.MORPH_OPEN, kernel)   # remove specks smaller than 5 x 5
    contours, _ = cv2.findContours(item, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    biggest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(biggest) < MIN_ITEM_PIXELS:
        return None
    return cv2.boundingRect(biggest)                        # (x, y, w, h)


if __name__ == "__main__":
    # On the Pi: take one photo, find the box, save both. On a laptop: use the fake camera.
    try:
        cam = Camera(0)
    except Exception as e:
        print("no real camera:", e, "- using the fake camera")
        cam = FakeCamera()
    photo = cam.take_photo()
    box = find_item_box(photo)
    print("photo", photo.shape, "item box", box)
    if box:
        x, y, w, h = box
        cv2.rectangle(photo, (x, y), (x + w, y + h), (0, 165, 255), 2)
    cv2.imwrite("camera_test.jpg", photo)
    cam.close()
