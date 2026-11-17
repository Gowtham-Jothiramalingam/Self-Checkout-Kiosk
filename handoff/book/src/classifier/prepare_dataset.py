"""prepare_dataset.py - turn the version 1 photos and YOLO boxes into 64 x 64 crops.

Input (from version 1):
  dataset/images/<photo>.jpg     top-view photos of the tray
  dataset/labels/<photo>.txt     one line per box: class cx cy w h (fractions of the photo size)
Output:
  classifier/data/dataset_64.npz  x_train, y_train, x_val, y_val, x_test, y_test (uint8 crops, int labels)
  classifier/data/split.csv       which photo went to which pile

Steps:
  1. Read every label file. Map the 14 version 1 class numbers to my 12 classes BY NAME.
     Capsicum and Chilly are dropped (15 and 17 photos: too few to learn or to test).
  2. Split the PHOTOS (not the crops) into train / validation / test, 70 / 15 / 15
     within each class, with a fixed seed, so near-identical crops of one photo
     can never be on both sides of the split.
  3. Cut every box out with a 10% margin and prepare it with the SAME function the
     kiosk uses (pad to square, RGB, 64 x 64). Store as whole numbers 0..255.

Run:  python prepare_dataset.py --images ../dataset/images --labels ../dataset/labels
"""
import argparse
import csv
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

from cnn_numpy import CLASSES, crop_with_margin, prepare_image

# The class order of version 1's YOLO training (14 classes, index 0..13).
V1_CLASSES = ["Apple", "Beetroot", "Brinjal", "Brinjal White", "Capsicum", "Chilly", "Coconut",
              "Guava", "Lemon", "Mosambi", "Onion", "Pomegranate", "Potato", "Tomato"]
DROPPED = {"Capsicum", "Chilly"}
SPLIT_SEED = 42
VAL_SHARE, TEST_SHARE = 0.15, 0.15
HERE = Path(__file__).resolve().parent


def read_boxes(label_path, photo_w, photo_h):
    """YOLO lines -> list of (class_name, (x, y, w, h) in pixels)."""
    boxes = []
    for line in label_path.read_text().split("\n"):
        parts = line.split()
        if len(parts) != 5:
            continue                                         # empty or broken line
        k, cx, cy, w, h = int(parts[0]), *map(float, parts[1:])
        bw, bh = w * photo_w, h * photo_h
        x, y = (cx * photo_w) - bw / 2, (cy * photo_h) - bh / 2   # centre -> top left corner
        boxes.append((V1_CLASSES[k], (int(round(x)), int(round(y)), int(round(bw)), int(round(bh)))))
    return boxes


def split_photos(photos_by_class, seed=SPLIT_SEED):
    """{class: [photo, ...]} -> {photo: "train" | "val" | "test"}, 70/15/15 inside every class."""
    rng = np.random.default_rng(seed)
    pile = {}
    for name in CLASSES:                                      # fixed order, so the result never changes
        photos = sorted(photos_by_class.get(name, []))
        rng.shuffle(photos)
        n_val, n_test = round(len(photos) * VAL_SHARE), round(len(photos) * TEST_SHARE)
        for i, p in enumerate(photos):
            pile[p] = "val" if i < n_val else "test" if i < n_val + n_test else "train"
    return pile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", default=str(HERE.parent / "dataset" / "images"))
    ap.add_argument("--labels", default=str(HERE.parent / "dataset" / "labels"))
    ap.add_argument("--out", default=str(HERE / "data"))
    args = ap.parse_args()
    images, labels, out = Path(args.images), Path(args.labels), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # 1. Read all boxes; give each photo the class most of its boxes belong to.
    photo_boxes, photos_by_class, dropped = {}, {}, Counter()
    for img_path in sorted(images.glob("*.jpg")):
        label_path = labels / (img_path.stem + ".txt")
        if not label_path.exists():
            print("no label file for", img_path.name)
            continue
        h, w = cv2.imread(str(img_path)).shape[:2]
        boxes = read_boxes(label_path, w, h)
        dropped.update(name for name, _ in boxes if name in DROPPED)
        boxes = [(n, b) for n, b in boxes if n not in DROPPED]
        if not boxes:
            continue                                          # a Capsicum or Chilly photo
        photo_boxes[img_path] = boxes
        main_class = Counter(n for n, _ in boxes).most_common(1)[0][0]
        photos_by_class.setdefault(main_class, []).append(img_path)
    print(f"photos kept: {len(photo_boxes)}   boxes dropped: {dict(dropped)}")

    # 2. Split by photo.
    pile = split_photos(photos_by_class)

    # 3. Cut, prepare and collect the crops.
    data = {p: ([], []) for p in ("train", "val", "test")}
    with open(out / "split.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["photo", "pile", "crops"])
        for img_path, boxes in photo_boxes.items():
            bgr = cv2.imread(str(img_path))
            for name, box in boxes:
                crop = crop_with_margin(bgr, box)
                if crop.size == 0:
                    continue                                  # a box outside the photo
                x = prepare_image(crop)[0]                    # (3, 64, 64), values 0..1
                data[pile[img_path]][0].append(np.round(x * 255).astype(np.uint8))
                data[pile[img_path]][1].append(CLASSES.index(name))
            writer.writerow([img_path.name, pile[img_path], len(boxes)])

    arrays = {}
    for p, (xs, ys) in data.items():
        arrays[f"x_{p}"] = np.stack(xs) if xs else np.zeros((0, 3, 64, 64), np.uint8)
        arrays[f"y_{p}"] = np.array(ys, np.int64)
    np.savez_compressed(out / "dataset_64.npz", **arrays)

    # A table of crops per class and pile, to check against the book.
    print(f"{'class':14s} {'train':>6s} {'val':>5s} {'test':>5s} {'total':>6s}")
    for k, name in enumerate(CLASSES):
        n = [int((arrays[f'y_{p}'] == k).sum()) for p in ("train", "val", "test")]
        print(f"{name:14s} {n[0]:6d} {n[1]:5d} {n[2]:5d} {sum(n):6d}")
    n = [len(arrays[f"y_{p}"]) for p in ("train", "val", "test")]
    print(f"{'total':14s} {n[0]:6d} {n[1]:5d} {n[2]:5d} {sum(n):6d}")
    print("wrote", out / "dataset_64.npz", "and", out / "split.csv")


if __name__ == "__main__":
    main()
