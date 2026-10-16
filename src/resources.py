"""
resources.py -- measured resource counts for QRAM read-oracle constructions,
specialized to the LMSR cost oracle, plus analytic models where a construction
is too wide to synthesize.

Why these numbers are honest:
  * T-count, qubit count, and depth are read off a transpiled circuit for the
    constructions we can build (QROM, QDMA block read, SELECT-SWAP/QROAM at small
    N). T is THE fault-tolerant cost driver (each T needs a distilled magic
    state), so T-count is the number that actually matters.
  * For bucket-brigade we report the ANALYTIC model from the literature
    (O(log N) active 2-qubit ops but O(N) coherent qubits and O(N) T in a
    fault-tolerant circuit), clearly labelled as a model, not a synthesis.

The transpiler basis is Clifford+T; we count T and Tdg as "T".
"""
from __future__ import annotations
import math
from qiskit import transpile, QuantumCircuit, QuantumRegister
from qiskit.circuit.library import MCXGate

from qrom import build_qrom, qdma_block_read

TBASIS = ["x", "cx", "h", "s", "sdg", "t", "tdg", "rz"]


def counts(qc: QuantumCircuit) -> dict:
    """Transpile to Clifford+T and tally T-count, qubits, depth, 2q-gates."""
    tq = transpile(qc, basis_gates=TBASIS, optimization_level=1)
    ops = tq.count_ops()
    tcount = ops.get("t", 0) + ops.get("tdg", 0)
    twoq = ops.get("cx", 0)
    return {"qubits": tq.num_qubits, "T": tcount, "2q": twoq, "depth": tq.depth()}


# -------------------------------------------------------------------------
# Construction A: QROM (unary / multiplexed). One read oracle.
# -------------------------------------------------------------------------
def qrom_read(data, n_addr, n_word):
    a = QuantumRegister(n_addr, "a")
    d = QuantumRegister(n_word, "d")
    qc = QuantumCircuit(a, d)
    qc.compose(build_qrom(data, n_addr, n_word), inplace=True)
    return qc


# -------------------------------------------------------------------------
# Construction B: SELECT-SWAP / QROAM. Trade qubits for T: split the N-row table
# into N/lam groups of lam rows; a QROM over N/lam selects a group into lam*word
# output registers, then a lam-way controlled SWAP routes the wanted row. Optimal
# lam ~ sqrt(N) gives ~O(sqrt(N)) T. We build it explicitly at small N.
# -------------------------------------------------------------------------
def qroam_read(data, n_addr, n_word, lam):
    N = len(data)
    # lam must be a power of two so the address splits cleanly into
    # (group high bits | selector low bits); caller passes a power of two.
    n_sel = max(0, round(math.log2(lam)))
    n_grp = max(0, n_addr - n_sel)
    groups = 1 << n_grp
    a = QuantumRegister(n_addr, "a")                 # full address
    out = QuantumRegister(lam * n_word, "o")         # lam words loaded at once
    tgt = QuantumRegister(n_word, "d")               # final selected word
    qc = QuantumCircuit(a, out, tgt)
    # high bits of address = group index, low bits = within-group selector
    # QROM over groups: for each group g, write its lam words into `out`
    for g in range(groups):
        gbits = [(g >> b) & 1 for b in range(n_grp)]
        hi = [a[n_sel + b] for b in range(n_grp)]
        zeros = [hi[b] for b in range(n_grp) if gbits[b] == 0]
        for q in zeros:
            qc.x(q)
        ctrl = hi if hi else []
        for r in range(lam):
            idx = g * lam + r
            if idx >= N:
                continue
            val = int(data[idx])
            for wbit in range(n_word):
                if (val >> wbit) & 1:
                    if ctrl:
                        qc.mcx(ctrl, out[r * n_word + wbit])
                    else:
                        qc.x(out[r * n_word + wbit])
        for q in zeros:
            qc.x(q)
    # controlled-SWAP the selected row (low bits) from `out` into `tgt`
    for r in range(lam):
        rbits = [(r >> b) & 1 for b in range(n_sel)]
        lo = [a[b] for b in range(n_sel)]
        zeros = [lo[b] for b in range(n_sel) if rbits[b] == 0]
        for q in zeros:
            qc.x(q)
        for wbit in range(n_word):
            # controlled copy out[r,wbit] -> tgt[wbit], controlled on selector==r
            # (CNOT fan-in from the selected group's slot into the final word)
            qc.mcx(lo + [out[r * n_word + wbit]], tgt[wbit])
        for q in zeros:
            qc.x(q)
    return qc


# -------------------------------------------------------------------------
# Construction C: QDMA block read -- the contribution. One descriptor
# (start,length) streams a contiguous rotation window into `length` word slots,
# decoding the base address pattern once per slot (vs a fresh full MCX decode on
# an independent superposed address for each of the N random reads a generic
# oracle would do for a cost evaluation).
# -------------------------------------------------------------------------
def qdma_read(data, n_addr, n_word, start, length):
    qc, _ = qdma_block_read(data, n_addr, n_word, start, length)
    return qc


# -------------------------------------------------------------------------
# Analytic bucket-brigade model (NOT synthesized -- labelled as model).
# -------------------------------------------------------------------------
def bucket_brigade_model(N, n_word):
    n = max(1, math.ceil(math.log2(N)))
    return {
        "qubits": 2 * N - 1 + n + n_word,   # binary tree of routers + addr + word
        "T": 7 * (2 * N - 2),               # ~2N Toffoli routers, 7 T each (FT)
        "2q": None,
        "depth": None,
        "active_2q_per_query": 2 * n,       # the O(log N) activation claim
        "model": True,
    }


if __name__ == "__main__":
    data = [1, 3, 2, 1, 2, 3, 3, 1]  # N=8, alphabet {1,2,3}
    n_addr, n_word = 3, 2
    print("QROM single read:   ", counts(qrom_read(data, n_addr, n_word)))
    lam = 1 << round(math.log2(max(1, round(math.sqrt(len(data))))))  # power of 2 near sqrt(N)
    print(f"QROAM (lam={lam}) read:", counts(qroam_read(data, n_addr, n_word, lam)))
    print("QDMA block read (len=4):", counts(qdma_read(data, n_addr, n_word, 2, 4)))
    print("Bucket-brigade (model):", bucket_brigade_model(len(data), n_word))
