"""bill.py - prices and the itemised bill, with money kept in whole paise.

Why paise: computers store decimal rupees like 8.78 only approximately, so
adding many of them can give 15.079999999999998 instead of 15.08. Whole
numbers of paise are exact, so every sum is exact. Rupees appear only when
the bill is printed.

>>> price_paise(412, 35)          # 412 g of tomato at Rs 35/kg
1442
>>> rupees(1442)
'Rs 14.42'
>>> price_paise(1033, 25)         # 2,582.5 paise rounds half up to 2,583
2583
>>> b = Bill()
>>> _ = b.add("Tomato", 412, 35)
>>> _ = b.add("Onion", 1032.6, 25)
>>> b.total_paise, rupees(b.total_paise)
(4025, 'Rs 40.25')
"""
import csv
from pathlib import Path


def load_prices(path):
    """Read prices.csv into a dictionary {"Tomato": 35, ...} of whole rupees per kg."""
    prices = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            prices[row["item"].strip()] = int(row["rupees_per_kg"])
    return prices


def check_prices(prices, class_names):
    """Stop at start-up if any class the network knows has no price."""
    missing = [name for name in class_names if name not in prices]
    if missing:
        raise ValueError(f"prices.csv has no price for: {', '.join(missing)}")


def price_paise(grams, rupees_per_kg):
    """Price of `grams` (rounded to whole grams) at `rupees_per_kg`, in whole paise.

    paise = grams x rupees_per_kg x 100 / 1000, rounded half up. All whole numbers.
    """
    g = int(round(grams))                     # the bill shows and charges whole grams
    return (g * rupees_per_kg * 100 + 500) // 1000


def money(paise):
    """1442 -> '14.42', using whole-number maths only."""
    return f"{paise // 100}.{paise % 100:02d}"


def rupees(paise):
    """1442 -> 'Rs 14.42'. Paise become rupees only when they are shown."""
    return "Rs " + money(paise)


class Bill:
    """The customer's bill: a list of lines and a total, all in paise."""

    def __init__(self):
        self.lines = []                       # each line: (name, grams, rupees_per_kg, paise)

    def add(self, name, grams, rupees_per_kg):
        line = (name, int(round(grams)), rupees_per_kg, price_paise(grams, rupees_per_kg))
        self.lines.append(line)
        return line

    def remove_last(self):
        if self.lines:
            self.lines.pop()

    def clear(self):
        self.lines = []

    @property
    def total_paise(self):
        return sum(line[3] for line in self.lines)

    def text(self):
        """The bill as lines of text, the same layout the screen shows."""
        rows = [f"{'Item':<14}{'Grams':>7}{'Rs/kg':>7}{'Rs':>9}"]
        for name, g, rpk, p in self.lines:
            rows.append(f"{name:<14}{g:>7}{rpk:>7}{money(p):>9}")
        rows.append("-" * 37)
        rows.append(f"{'Total':<28}{money(self.total_paise):>9}")
        return "\n".join(rows)


if __name__ == "__main__":
    import doctest
    print("doctest failures:", doctest.testmod().failed)
    prices = load_prices(Path(__file__).resolve().parent / "prices.csv")
    bill = Bill()
    for name, grams in [("Tomato", 412), ("Onion", 1032.6), ("Apple", 618), ("Lemon", 97)]:
        bill.add(name, grams, prices[name])
    print(bill.text())
    print("total:", rupees(bill.total_paise))
