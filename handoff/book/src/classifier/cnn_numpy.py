"""cnn_numpy.py - the whole image classifier of the kiosk, written with NumPy only.

This one file is used in two places:
  * on the laptop, train.py imports it to TRAIN the network,
  * on the Raspberry Pi, kiosk_app.py imports it to PREDICT one photo.
Because both sides import the same file, the layers can never drift apart.

Shapes used everywhere:
  a batch of pictures  x : (N, C, H, W) = (how many, channels, rows, columns)
  a batch of scores      : (N, 12)

Every layer has two methods:
  forward(x)   takes the input, remembers what it needs, returns the output
  backward(d)  takes "how much the loss changes with my output" (d) and returns
               "how much the loss changes with my input"; on the way it stores
               the gradients of its own weights in self.dW and self.db
"""
import numpy as np

# The 12 classes in their fixed order. Index 0 is Apple, index 11 is Tomato.
# This order is baked into the trained weights, so it must never change.
CLASSES = ["Apple", "Beetroot", "Brinjal", "Brinjal White", "Coconut", "Guava",
           "Lemon", "Mosambi", "Onion", "Pomegranate", "Potato", "Tomato"]

IMAGE_SIZE = 64      # the network sees 64 x 64 pictures
CROP_MARGIN = 0.10   # every item box is grown by 10% on each side before cropping


# ----------------------------------------------------------------------------
# Image preparation (the only part that uses OpenCV)
# ----------------------------------------------------------------------------
def crop_with_margin(bgr, box, margin=CROP_MARGIN):
    """Cut the box (x, y, w, h) out of a photo, grown by a margin on each side."""
    x, y, w, h = box
    mx, my = int(round(w * margin)), int(round(h * margin))
    rows, cols = bgr.shape[:2]
    x0, y0 = max(0, x - mx), max(0, y - my)
    x1, y1 = min(cols, x + w + mx), min(rows, y + h + my)
    return bgr[y0:y1, x0:x1]


def prepare_image(bgr):
    """Turn one BGR crop of any size into the block the network eats.

    Steps: pad to a square with the border colour -> BGR to RGB ->
    resize to 64 x 64 -> float32 in 0..1 -> shape (1, 3, 64, 64).
    The SAME function is used for training crops and for kiosk photos.
    """
    import cv2  # imported here so the maths below also works without OpenCV
    h, w = bgr.shape[:2]
    # The colour of the crop's outer frame of pixels (the tray), one value per channel.
    border = np.concatenate([bgr[0], bgr[-1], bgr[:, 0], bgr[:, -1]])
    colour = [int(v) for v in np.median(border, axis=0)]
    # Pad the short side equally on both ends so the item keeps its true shape.
    side = max(h, w)
    top, left = (side - h) // 2, (side - w) // 2
    square = cv2.copyMakeBorder(bgr, top, side - h - top, left, side - w - left,
                                cv2.BORDER_CONSTANT, value=colour)
    rgb = cv2.cvtColor(square, cv2.COLOR_BGR2RGB)
    small = cv2.resize(rgb, (IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_AREA)
    x = small.astype(np.float32) / 255.0          # 0..255 -> 0..1
    x = x.transpose(2, 0, 1)                      # (64, 64, 3) -> (3, 64, 64)
    return x[None]                                # add the batch axis -> (1, 3, 64, 64)


# ----------------------------------------------------------------------------
# A slow convolution, only for understanding and for testing the fast one
# ----------------------------------------------------------------------------
def conv_forward_slow(x, W, b):
    """Convolution of ONE picture x (C, H, W) with plain Python loops.

    W is (F, C, k, k): F filters, each C channels deep and k x k wide.
    This is the textbook definition. It is far too slow to train with.
    """
    F, C, k, _ = W.shape
    H_out, W_out = x.shape[1] - k + 1, x.shape[2] - k + 1
    out = np.zeros((F, H_out, W_out), x.dtype)
    for f in range(F):                      # every filter
        for r in range(H_out):              # every output row
            for c in range(W_out):          # every output column
                patch = x[:, r:r + k, c:c + k]            # the k x k window, all channels
                out[f, r, c] = np.sum(patch * W[f]) + b[f]
    return out


# ----------------------------------------------------------------------------
# The layers
# ----------------------------------------------------------------------------
class Conv:
    """Convolution layer, k x k filters, no padding, stride 1."""

    def __init__(self, c_in, c_out, k=3, rng=None, dtype=np.float32, need_dx=True):
        rng = rng or np.random.default_rng(0)
        fan_in = c_in * k * k                               # inputs feeding one output number
        # He initialisation: random numbers with spread sqrt(2 / fan_in).
        self.W = (rng.standard_normal((c_out, c_in, k, k)) * np.sqrt(2.0 / fan_in)).astype(dtype)
        self.b = np.zeros(c_out, dtype)
        self.k = k
        self.need_dx = need_dx      # the first layer has nobody to pass blame to

    def forward(self, x):
        self.x = x                                          # remember the input for backward
        N, C, H, W = x.shape
        k = self.k
        Ho, Wo = H - k + 1, W - k + 1
        out = np.zeros((N, self.W.shape[0], Ho, Wo), x.dtype)
        # Loop over the 9 cells of the filter, NOT over the pixels.
        # For cell (i, j): take the input shifted by (i, j) and multiply it by
        # that cell's weights for all pictures, channels and positions at once.
        for i in range(k):
            for j in range(k):
                shifted = x[:, :, i:i + Ho, j:j + Wo]       # (N, C, Ho, Wo)
                out += np.einsum("nchw,fc->nfhw", shifted, self.W[:, :, i, j], optimize=True)
        out += self.b[None, :, None, None]
        return out

    def backward(self, d):
        x, k = self.x, self.k
        Ho, Wo = d.shape[2], d.shape[3]
        self.dW = np.zeros_like(self.W)
        self.db = d.sum(axis=(0, 2, 3))                     # each bias touched every output of its map
        dx = np.zeros_like(x) if self.need_dx else None
        for i in range(k):
            for j in range(k):
                shifted = x[:, :, i:i + Ho, j:j + Wo]
                # Blame for weight (f, c, i, j) = sum of (blame of output) x (input it multiplied).
                self.dW[:, :, i, j] = np.einsum("nfhw,nchw->fc", d, shifted, optimize=True)
                if self.need_dx:
                    # Blame for the input = blame of every output it fed, times the weight used.
                    dx[:, :, i:i + Ho, j:j + Wo] += np.einsum(
                        "nfhw,fc->nchw", d, self.W[:, :, i, j], optimize=True)
        return dx


class ReLU:
    """Keep positive numbers, turn negative numbers into 0."""

    def forward(self, x):
        self.keep = x > 0
        return x * self.keep

    def backward(self, d):
        return d * self.keep            # blame passes only where the input was positive


class MaxPool:
    """2 x 2 max pooling: keep the biggest of every 2 x 2 block."""

    def forward(self, x):
        N, C, H, W = x.shape
        Ho, Wo = H // 2, W // 2                              # an odd last row/column is dropped
        self.in_shape = x.shape
        blocks = x[:, :, :2 * Ho, :2 * Wo].reshape(N, C, Ho, 2, Wo, 2)
        blocks = blocks.transpose(0, 1, 2, 4, 3, 5).reshape(N, C, Ho, Wo, 4)   # 4 numbers per block
        winner = blocks.argmax(axis=4)                       # which of the 4 was biggest
        self.mask = np.arange(4) == winner[..., None]        # True at the winner only
        return blocks.max(axis=4)

    def backward(self, d):
        N, C, H, W = self.in_shape
        Ho, Wo = H // 2, W // 2
        blocks = self.mask * d[..., None]                    # all blame to the winner, 0 to the rest
        blocks = blocks.reshape(N, C, Ho, Wo, 2, 2).transpose(0, 1, 2, 4, 3, 5)
        dx = np.zeros(self.in_shape, d.dtype)
        dx[:, :, :2 * Ho, :2 * Wo] = blocks.reshape(N, C, 2 * Ho, 2 * Wo)
        return dx


class Flatten:
    """Unroll (N, C, H, W) into (N, C*H*W). No maths, only a new shape."""

    def forward(self, x):
        self.in_shape = x.shape
        return x.reshape(x.shape[0], -1)

    def backward(self, d):
        return d.reshape(self.in_shape)


class Dense:
    """Fully connected layer: every input is joined to every output."""

    def __init__(self, n_in, n_out, rng=None, dtype=np.float32):
        rng = rng or np.random.default_rng(0)
        self.W = (rng.standard_normal((n_in, n_out)) * np.sqrt(2.0 / n_in)).astype(dtype)
        self.b = np.zeros(n_out, dtype)

    def forward(self, x):
        self.x = x
        return x @ self.W + self.b

    def backward(self, d):
        self.dW = self.x.T @ d          # (n_in, n_out)
        self.db = d.sum(axis=0)
        return d @ self.W.T             # blame for the inputs


# ----------------------------------------------------------------------------
# Softmax and the loss
# ----------------------------------------------------------------------------
def softmax(z):
    """Turn each row of scores into chances that are positive and add up to 1."""
    z = z - z.max(axis=1, keepdims=True)        # does not change the answer, avoids huge exp()
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def loss_and_grad(scores, y):
    """Cross-entropy loss of a batch, and its gradient with respect to the scores.

    scores : (N, 12) raw outputs of the last layer
    y      : (N,) the right class index of each picture
    Returns (loss, d) where d has the shape of scores and feeds Net.backward.
    """
    N = scores.shape[0]
    p = softmax(scores)
    loss = -np.mean(np.log(p[np.arange(N), y] + 1e-12))
    d = p.copy()
    d[np.arange(N), y] -= 1.0                   # chances minus the one-hot answer
    return float(loss), d / N


# ----------------------------------------------------------------------------
# The network
# ----------------------------------------------------------------------------
class Net:
    """3 x 64 x 64 -> conv 8 -> pool -> conv 16 -> pool -> conv 32 -> pool -> 64 -> 12."""

    def __init__(self, seed=0, dtype=np.float32):
        rng = np.random.default_rng(seed)
        self.layers = [
            Conv(3, 8, rng=rng, dtype=dtype, need_dx=False), ReLU(), MaxPool(),   # -> 8 x 31 x 31
            Conv(8, 16, rng=rng, dtype=dtype), ReLU(), MaxPool(),                 # -> 16 x 14 x 14
            Conv(16, 32, rng=rng, dtype=dtype), ReLU(), MaxPool(),                # -> 32 x 6 x 6
            Flatten(),                                                            # -> 1,152
            Dense(32 * 6 * 6, 64, rng=rng, dtype=dtype), ReLU(),                  # -> 64
            Dense(64, len(CLASSES), rng=rng, dtype=dtype),                        # -> 12 scores
        ]
        # The layers that own weights, with the names used in weights.npz.
        idx = [0, 3, 6, 10, 12]
        names = ["conv1", "conv2", "conv3", "dense1", "dense2"]
        self.named = [(n, self.layers[i]) for n, i in zip(names, idx)]
        # One "velocity" array per weight array, for momentum.
        self.velocity = {(n, p): np.zeros_like(getattr(layer, p))
                         for n, layer in self.named for p in ("W", "b")}

    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x                                 # (N, 12) scores, softmax NOT applied yet

    def backward(self, d):
        for layer in reversed(self.layers):
            d = layer.backward(d)

    def step(self, lr=0.01, momentum=0.9):
        """One SGD-with-momentum update of every weight, using the stored gradients."""
        for name, layer in self.named:
            for p in ("W", "b"):
                w = getattr(layer, p)                        # the weight array itself
                v = self.velocity[(name, p)]                 # its velocity array
                v *= momentum                                # keep 90% of the old direction
                v -= lr * getattr(layer, "d" + p)            # add a step downhill
                w += v                                       # move the weights, in place

    def count_weights(self):
        return sum(layer.W.size + layer.b.size for _, layer in self.named)

    def get_weights(self):
        """A dictionary of copies of the 10 weight arrays."""
        return {f"{n}_{p}": getattr(layer, p).copy() for n, layer in self.named for p in ("W", "b")}

    def set_weights(self, arrays):
        for n, layer in self.named:
            for p in ("W", "b"):
                a = arrays[f"{n}_{p}"]
                if a.shape != getattr(layer, p).shape:
                    raise ValueError(f"{n}_{p}: file has {a.shape}, network needs {getattr(layer, p).shape}")
                setattr(layer, p, a.astype(getattr(layer, p).dtype))

    def save_weights(self, path):
        np.savez(path, **self.get_weights())

    def load_weights(self, path):
        with np.load(path) as data:
            self.set_weights({k: data[k] for k in data.files})


def predict(net, x):
    """Class index and confidence (0..1) for ONE prepared picture x of shape (1, 3, 64, 64)."""
    p = softmax(net.forward(x))[0]
    best = int(p.argmax())
    return best, float(p[best])


def top_k(net, x, k=3):
    """The k most likely classes for one picture, best first: [(class_index, chance), ...]."""
    p = softmax(net.forward(x))[0]
    order = np.argsort(p)[::-1][:k]
    return [(int(i), float(p[i])) for i in order]


if __name__ == "__main__":
    # A tiny self-test: the fast convolution must agree with the slow textbook one.
    rng = np.random.default_rng(1)
    layer = Conv(3, 8, rng=rng, dtype=np.float64)
    x = rng.standard_normal((1, 3, 16, 16))
    fast = layer.forward(x)[0]
    slow = conv_forward_slow(x[0], layer.W, layer.b)
    print("fast conv equals slow conv:", np.allclose(fast, slow))
    net = Net()
    print("weights in the network:", net.count_weights())
    print("output shape for 2 pictures:", net.forward(np.zeros((2, 3, 64, 64), np.float32)).shape)
