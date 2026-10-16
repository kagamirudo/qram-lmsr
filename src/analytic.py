"""
analytic.py -- literature-standard analytic resource models for the read-oracle
constructions. These are the headline costs; the Qiskit circuits (qrom.py) are
used to VERIFY correctness and to cross-check the small-N regime, not to produce
T-counts via generic multi-controlled-X synthesis (which a real implementation
would never use -- it uses the structured constructions costed here).

Costs are the fault-tolerant T-count per read oracle, word size b bits.

QROM via unary iteration (Babbush et al., PRX 2018): a sequence of N-1 Toffolis
walking a unary register; T-count 4(N-1) (each Toffoli = 4 T in the measurement-
and-fixup form used there; some references state 7 T per Toffoli without the
catalysis -- we expose the per-Toffoli constant so the paper can state its model).

QROAM / SELECT-SWAP (Low-Kliuchnikov-Schaeffer; Berry et al.): split the table
into N/lambda groups of lambda rows. SELECT over groups costs ~4(N/lambda) T; a
SWAP network over lambda rows of b bits costs ~4*lambda*b T. Minimizing over
lambda gives lambda* ~ sqrt(N/b) and total T ~ O(sqrt(N b)).

Bucket-brigade (Giovannetti-Lloyd-Maccone PRA 2008; Di Matteo et al. 2020): a
binary routing tree of 2N-1 nodes. Only O(log N) nodes are *activated* per query
(the headline resilience claim), but a FAULT-TOLERANT realization must still
error-correct ~2N router qubits and spend ~T_tof per router that participates in
the coherent query -> O(N) T in the circuit model. We report both the activation
count and the fault-tolerant T.

QDMA (this work): one descriptor (base, length L) drives a contiguous burst. The
address is decoded ONCE for the base; each of the L word slots is then a fixed
classical offset, costing only the data-write (no re-decode). Model:
  T_qdma(L) = T_decode(N) + L * b * c_write
where T_decode(N) = 4(N-1) is paid once (we reuse the QROM SELECT to land the
base), and each slot costs b data writes at c_write T each. Per-read T is thus
T_decode(N)/L + b*c_write, which -> b*c_write (a constant) as L grows: the
amortization. For a worst-case LMSR cost evaluation L up to N.
"""
from __future__ import annotations
import math

T_TOF = 4          # T gates per Toffoli (measurement-based form; stated in paper)
C_WRITE = 4        # T per controlled word-bit write in a burst slot


def qrom_T(N, b=2):
    return T_TOF * max(0, N - 1)


def qrom_qubits(N, b=2):
    n = max(1, math.ceil(math.log2(N)))
    return n + b + max(0, n - 1)   # address + word + unary ancilla


def qroam_T(N, b=2, lam=None):
    if lam is None:
        lam = max(1, round(math.sqrt(N / max(1, b))))
    groups = math.ceil(N / lam)
    select = T_TOF * max(0, groups - 1)
    swap = T_TOF * lam * b
    return select + swap, lam


def qroam_qubits(N, b=2, lam=None):
    if lam is None:
        lam = max(1, round(math.sqrt(N / max(1, b))))
    n = max(1, math.ceil(math.log2(N)))
    return n + lam * b + b          # addr + lam loaded words + target


def bucket_brigade(N, b=2):
    n = max(1, math.ceil(math.log2(N)))
    return {
        "qubits": 2 * N - 1 + n + b,
        "T_fault_tolerant": T_TOF * (2 * N - 2),
        "active_2q_per_query": 2 * n,     # O(log N) activation
    }


def qdma_T(N, L, b=2):
    """Total T for a length-L contiguous burst."""
    return qrom_T(N, b) + L * b * C_WRITE


def qdma_T_per_read(N, L, b=2):
    return qdma_T(N, L, b) / L


if __name__ == "__main__":
    print(f"{'N':>5} {'QROM/read':>10} {'QDMA/read(L=N)':>15} {'ratio':>7} "
          f"{'QROAM_T':>9} {'BB_T(FT)':>9} {'BB_active':>10}")
    for N in [4, 8, 16, 32, 64, 128, 256, 1024]:
        qr = qrom_T(N)
        qd = qdma_T_per_read(N, N)
        qm, lam = qroam_T(N)
        bb = bucket_brigade(N)
        print(f"{N:>5} {qr:>10} {qd:>15.2f} {qr/qd:>7.2f} "
              f"{qm:>9} {bb['T_fault_tolerant']:>9} {bb['active_2q_per_query']:>10}")
