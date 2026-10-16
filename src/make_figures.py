"""make_figures.py -- render paper figures from results/ into assets/."""
import csv, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RES = sys.argv[1] if len(sys.argv) > 1 else "results"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 10, "figure.dpi": 150})


def rows(name):
    return list(csv.DictReader(open(os.path.join(RES, name))))


def fig_per_read():
    r = rows("per_read.csv")
    N = [int(x["N"]) for x in r]
    qrom = [float(x["qrom_T_per_read"]) for x in r]
    qdma = [float(x["qdma_T_per_read"]) for x in r]
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.plot(N, qrom, "o-", label="QROM (random access)")
    ax.plot(N, qdma, "s-", label="QDMA (contiguous burst)")
    ax.set_xscale("log", base=2); ax.set_yscale("log", base=2)
    ax.set_xlabel("memory size $N$ (string length)")
    ax.set_ylabel("T-count per character read")
    ax.set_title("Per-read cost: QDMA amortizes address decode")
    ax.legend(); ax.grid(alpha=0.3, which="both")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_per_read.pdf"))
    print("wrote fig_per_read.pdf")


def fig_oracle():
    r = rows("oracle_cost.csv")
    N = [int(x["N"]) for x in r]
    ra = [int(x["random_access_T"]) for x in r]
    qd = [int(x["qdma_burst_T"]) for x in r]
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.plot(N, ra, "o-", label="random-access oracle ($N$ decodes)")
    ax.plot(N, qd, "s-", label="QDMA burst oracle (1 decode)")
    ax.set_xscale("log", base=2); ax.set_yscale("log", base=2)
    ax.set_xlabel("memory size $N$")
    ax.set_ylabel("total T-count per LMSR cost evaluation")
    ax.set_title("LMSR cost oracle: the hidden QRAM cost")
    ax.legend(); ax.grid(alpha=0.3, which="both")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_oracle.pdf"))
    print("wrote fig_oracle.pdf")


def fig_constructions():
    r = rows("constructions.csv")
    methods = {}
    for x in r:
        m = x["method"].split("(")[0]
        methods.setdefault(m, ([], []))
        methods[m][0].append(int(x["N"]))
        methods[m][1].append(int(x["T"]))
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    marks = {"QROM": "o-", "QROAM": "s-", "bucket-brigade": "^-"}
    for m, (N, T) in methods.items():
        ax.plot(N, T, marks.get(m, "x-"), label=m)
    ax.set_xscale("log", base=2); ax.set_yscale("log", base=2)
    ax.set_xlabel("memory size $N$")
    ax.set_ylabel("T-count per single read")
    ax.set_title("Read-oracle construction survey")
    ax.legend(); ax.grid(alpha=0.3, which="both")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_constructions.pdf"))
    print("wrote fig_constructions.pdf")


if __name__ == "__main__":
    fig_per_read(); fig_oracle(); fig_constructions()
