"""gradient_check.py - proof that the hand-written backward pass is correct.

Idea: the gradient of a weight says how much the loss changes when that weight
changes a tiny bit. That can also be MEASURED: nudge the weight up by eps, then
down by eps, and see how the loss moves (the "central difference"). If my
backward pass is right, the two numbers agree to many digits.

Run:  python gradient_check.py
It uses float64 so that rounding does not hide a real mistake.
"""
import numpy as np
from cnn_numpy import Net, loss_and_grad

EPS = 1e-5            # size of the nudge
PER_LAYER = 20        # random weights tested in every weight array


def loss_of(net, x, y):
    loss, _ = loss_and_grad(net.forward(x), y)
    return loss


def relative_difference(net, x, y, weights, pos, analytic, eps):
    """Nudge one weight up and down by eps and compare the measured slope with mine."""
    old = weights[pos]
    weights[pos] = old + eps
    up = loss_of(net, x, y)
    weights[pos] = old - eps
    down = loss_of(net, x, y)
    weights[pos] = old                                   # put it back
    numeric = (up - down) / (2 * eps)                    # central difference
    return abs(numeric - analytic) / max(1e-12, abs(numeric) + abs(analytic))


def main(seed=0):
    rng = np.random.default_rng(seed)
    net = Net(seed=seed, dtype=np.float64)
    x = rng.random((4, 3, 64, 64))               # 4 random "pictures" in 0..1
    y = rng.integers(0, 12, size=4)              # 4 random "right answers"

    # Gradients from my backward pass.
    loss, d = loss_and_grad(net.forward(x), y)
    net.backward(d)
    print(f"loss on random data: {loss:.4f}")

    worst, retried = 0.0, 0
    for name, layer in net.named:
        for p in ("W", "b"):
            weights = getattr(layer, p)
            analytic = getattr(layer, "d" + p)
            layer_worst = 0.0
            for _ in range(PER_LAYER):
                pos = tuple(rng.integers(0, s) for s in weights.shape)   # one random weight
                rel = relative_difference(net, x, y, weights, pos, analytic[pos], EPS)
                if rel > 1e-5:
                    # ReLU and max pooling have "kinks". If the nudge pushes one unit
                    # across its kink, the measured slope is slightly off even though
                    # my gradient is right. A 10 times smaller nudge avoids the kink.
                    # A real bug stays wrong for every nudge size.
                    retried += 1
                    rel = relative_difference(net, x, y, weights, pos, analytic[pos], EPS / 10)
                layer_worst = max(layer_worst, rel)
            print(f"  {name + '_' + p:9s} shape {str(weights.shape):16s} worst relative difference {layer_worst:.1e}")
            worst = max(worst, layer_worst)

    print(f"weights re-measured with a smaller nudge (kinks): {retried} of {PER_LAYER * 10}")
    print(f"biggest relative difference: {worst:.1e}")
    print("PASS" if worst < 1e-5 else "FAIL: the backward pass has a mistake")
    return worst


if __name__ == "__main__":
    main()
