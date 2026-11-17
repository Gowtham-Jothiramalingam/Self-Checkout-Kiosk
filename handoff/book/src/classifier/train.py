"""train.py - train the NumPy CNN, keep the best epoch, test once, save everything.

Real run (laptop, after prepare_dataset.py):
    python train.py
Proof that the code learns, with no fruit photos at all:
    python train.py --synthetic
    (12 classes of coloured shapes drawn with OpenCV; results go to classifier/synthetic_run/
     so they can never be mistaken for the real weights)

Writes into the output folder:
  weights.npz            the weights of the best validation epoch
  metrics.json           every epoch's accuracy and loss, the test result, the confusion matrix
  training_curve.png     and confusion_matrix.png (if matplotlib is installed)
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np

from cnn_numpy import CLASSES, Net, loss_and_grad, prepare_image, softmax

HERE = Path(__file__).resolve().parent


# ----------------------------------------------------------------------------- data
def load_dataset(path):
    d = np.load(path)
    return [(d[f"x_{p}"], d[f"y_{p}"]) for p in ("train", "val", "test")]


def make_synthetic(per_class=(60, 15, 15), seed=0):
    """12 classes of coloured shapes on a blue tray, prepared exactly like real crops.

    Each class is a (shape, colour) pair; size, position, colour shade and
    brightness vary randomly, so the network has to learn shape AND colour.
    """
    import cv2
    rng = np.random.default_rng(seed)
    shapes = ["circle", "square", "triangle", "ellipse"]
    colours = [(40, 40, 200), (60, 200, 230), (60, 170, 60)]          # BGR: red, yellow, green
    kinds = [(s, c) for s in shapes for c in colours]                  # 4 x 3 = 12 classes
    piles = []
    for n in per_class:
        xs, ys = [], []
        for k, (shape, colour) in enumerate(kinds):
            for _ in range(n):
                h, w = rng.integers(90, 140), rng.integers(90, 140)
                img = np.zeros((h, w, 3), np.uint8)
                img[:] = (200, 120, 40)                                 # tray blue
                c = [int(np.clip(v + rng.integers(-30, 31), 0, 255)) for v in colour]
                cx, cy = w // 2 + rng.integers(-8, 9), h // 2 + rng.integers(-8, 9)
                r = int(min(h, w) * rng.uniform(0.25, 0.38))
                if shape == "circle":
                    cv2.circle(img, (int(cx), int(cy)), r, c, -1)
                elif shape == "square":
                    cv2.rectangle(img, (int(cx - r), int(cy - r)), (int(cx + r), int(cy + r)), c, -1)
                elif shape == "triangle":
                    pts = np.array([[cx, cy - r], [cx - r, cy + r], [cx + r, cy + r]], np.int32)
                    cv2.fillPoly(img, [pts], c)
                else:
                    cv2.ellipse(img, (int(cx), int(cy)), (r, r // 2), int(rng.integers(0, 180)), 0, 360, c, -1)
                img = np.clip(img * rng.uniform(0.85, 1.15), 0, 255).astype(np.uint8)
                xs.append(np.round(prepare_image(img)[0] * 255).astype(np.uint8))
                ys.append(k)
        piles.append((np.stack(xs), np.array(ys, np.int64)))
    names = [f"{s} {['red', 'yellow', 'green'][i % 3]}" for s in shapes for i in range(3)]
    return piles, names


def to_float(x_uint8):
    return x_uint8.astype(np.float32) / 255.0


def augment(x, rng):
    """Random flip, shift up to 4 pixels and brightness 0.85..1.15, for TRAINING batches only."""
    x = x.copy()
    n = len(x)
    flip = rng.random(n) < 0.5
    x[flip] = x[flip][..., ::-1]                                       # mirror left-right
    padded = np.pad(x, ((0, 0), (0, 0), (4, 4), (4, 4)), mode="edge")  # repeat the border pixels
    dy, dx = rng.integers(0, 9, n), rng.integers(0, 9, n)              # shift of -4..+4
    for i in range(n):
        x[i] = padded[i, :, dy[i]:dy[i] + 64, dx[i]:dx[i] + 64]
    x *= rng.uniform(0.85, 1.15, (n, 1, 1, 1)).astype(np.float32)
    return np.clip(x, 0.0, 1.0)


# ----------------------------------------------------------------------------- measuring
def evaluate(net, x_uint8, y, batch=128):
    """Accuracy, average loss and the predicted class of every picture."""
    preds, losses = [], []
    for i in range(0, len(y), batch):
        scores = net.forward(to_float(x_uint8[i:i + batch]))
        loss, _ = loss_and_grad(scores, y[i:i + batch])
        losses.append(loss * len(scores))
        preds.append(scores.argmax(axis=1))
    preds = np.concatenate(preds)
    return float((preds == y).mean()), float(sum(losses) / len(y)), preds


def confusion_matrix(y, preds, k):
    m = np.zeros((k, k), np.int64)
    np.add.at(m, (y, preds), 1)                                        # rows true, columns predicted
    return m


def save_plots(out, history, cm, names):
    try:
        import matplotlib
        matplotlib.use("Agg")                                          # draw to files, no window
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed: skipping the pictures")
        return
    ep = [h["epoch"] for h in history]
    plt.figure(figsize=(7, 4))
    plt.plot(ep, [100 * h["train_acc"] for h in history], label="training")
    plt.plot(ep, [100 * h["val_acc"] for h in history], label="validation")
    plt.xlabel("epoch"); plt.ylabel("accuracy (%)"); plt.legend(); plt.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig(out / "training_curve.png", dpi=120); plt.close()
    plt.figure(figsize=(7, 6))
    plt.imshow(cm, cmap="Blues")
    for i in range(len(cm)):
        for j in range(len(cm)):
            if cm[i, j]:
                plt.text(j, i, cm[i, j], ha="center", va="center", fontsize=8)
    plt.xticks(range(len(names)), names, rotation=60, ha="right", fontsize=8)
    plt.yticks(range(len(names)), names, fontsize=8)
    plt.xlabel("predicted"); plt.ylabel("true"); plt.tight_layout()
    plt.savefig(out / "confusion_matrix.png", dpi=120); plt.close()


# ----------------------------------------------------------------------------- training
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(HERE / "data" / "dataset_64.npz"))
    ap.add_argument("--synthetic", action="store_true", help="train on drawn shapes to prove the code learns")
    ap.add_argument("--epochs", type=int, default=None, help="default 40 (real) or 8 (synthetic)")
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=0.01)
    ap.add_argument("--momentum", type=float, default=0.9)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--no-augment", action="store_true", help="the first, overfitting attempt")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.synthetic:
        (train, val, test), names = make_synthetic(seed=args.seed)
        out = Path(args.out or HERE / "synthetic_run")
        epochs = args.epochs or 8
    else:
        train, val, test = load_dataset(args.data)
        names = CLASSES
        out = Path(args.out or HERE)
        epochs = args.epochs or 40
    out.mkdir(parents=True, exist_ok=True)
    (x_tr, y_tr), (x_va, y_va), (x_te, y_te) = train, val, test
    print(f"crops: train {len(y_tr)}, validation {len(y_va)}, test {len(y_te)}; "
          f"chance level {100 / len(names):.1f}%")

    rng = np.random.default_rng(args.seed)
    net = Net(seed=args.seed)
    history, best = [], {"val_acc": -1.0}
    start = time.time()
    for epoch in range(1, epochs + 1):
        t0 = time.time()
        order = rng.permutation(len(y_tr))                               # shuffle every epoch
        losses = []
        for i in range(0, len(order), args.batch):
            idx = order[i:i + args.batch]
            xb = to_float(x_tr[idx])
            if not args.no_augment:
                xb = augment(xb, rng)
            loss, d = loss_and_grad(net.forward(xb), y_tr[idx])          # forward + loss
            net.backward(d)                                              # blame for every weight
            net.step(args.lr, args.momentum)                             # one step downhill
            losses.append(loss)
        train_acc, _, _ = evaluate(net, x_tr, y_tr)
        val_acc, val_loss, _ = evaluate(net, x_va, y_va)
        history.append({"epoch": epoch, "train_loss": float(np.mean(losses)), "train_acc": train_acc,
                        "val_loss": val_loss, "val_acc": val_acc, "seconds": round(time.time() - t0, 1)})
        mark = ""
        if val_acc > best["val_acc"]:                                    # keep the best epoch's weights
            best = {"val_acc": val_acc, "epoch": epoch, "train_acc": train_acc, "weights": net.get_weights()}
            mark = "  <- best so far"
        print(f"epoch {epoch:2d}  loss {np.mean(losses):.3f}  train {100 * train_acc:5.1f}%  "
              f"val {100 * val_acc:5.1f}%  ({time.time() - t0:.0f} s){mark}")

    # Test ONCE, with the best weights.
    net.set_weights(best["weights"])
    test_acc, test_loss, preds = evaluate(net, x_te, y_te)
    cm = confusion_matrix(y_te, preds, len(names))
    per_class = {names[k]: (round(100 * cm[k, k] / cm[k].sum(), 1) if cm[k].sum() else None)
                 for k in range(len(names))}
    chances = np.concatenate([softmax(net.forward(to_float(x_te[i:i + 128]))).max(axis=1)
                              for i in range(0, len(y_te), 128)])
    sure = chances >= 0.60
    net.save_weights(out / "weights.npz")
    metrics = {
        "synthetic": args.synthetic, "classes": list(names), "epochs": epochs, "batch": args.batch,
        "lr": args.lr, "momentum": args.momentum, "augment": not args.no_augment,
        "crops": {"train": int(len(y_tr)), "val": int(len(y_va)), "test": int(len(y_te))},
        "best_epoch": best["epoch"], "best_train_acc": best["train_acc"], "best_val_acc": best["val_acc"],
        "test_acc": test_acc, "test_correct": int(cm.trace()), "test_total": int(len(y_te)),
        "test_loss": test_loss, "per_class_test_acc": per_class, "confusion_matrix": cm.tolist(),
        "confidence_0.60": {"sure": int(sure.sum()), "sure_correct": int((preds == y_te)[sure].sum()),
                            "unsure": int((~sure).sum()), "unsure_correct": int((preds == y_te)[~sure].sum())},
        "training_minutes": round((time.time() - start) / 60, 1), "history": history,
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1))
    save_plots(out, history, cm, names)
    print(f"best epoch {best['epoch']}: train {100 * best['train_acc']:.1f}%, "
          f"validation {100 * best['val_acc']:.1f}%")
    print(f"test accuracy {100 * test_acc:.1f}% ({cm.trace()} of {len(y_te)})")
    print("wrote", out / "weights.npz", "and", out / "metrics.json")


if __name__ == "__main__":
    main()
