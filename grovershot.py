import numpy as np

import matplotlib.pyplot as plt
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer import AerSimulator

from qiskit.circuit import Parameter

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector

from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit.visualization import plot_distribution


from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# grover_engine.py
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import math

# -------------------------------------------------------------------
# 🧠 Build an Oracle that marks one "ship" state with a phase flip
# -------------------------------------------------------------------
def build_oracle(n_qubits: int, target_index: int) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits)
    binary_target = format(target_index, f'0{n_qubits}b')

    # Flip qubits for bits that are 0 so that the mcx hits only |target>
    for i, bit in enumerate(reversed(binary_target)):
        if bit == '0':
            qc.x(i)

    # Multi-controlled Z (as H–MCX–H on last qubit)
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)

    # Uncompute the X gates
    for i, bit in enumerate(reversed(binary_target)):
        if bit == '0':
            qc.x(i)

    return qc


# -------------------------------------------------------------------
# 💫 Build the Diffuser (inversion about the mean)
# -------------------------------------------------------------------
def build_diffuser(n_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc

#########
#HEATMAP
#########
def plot_grover_heatmap(counts, n_qubits):
    """
    Convert Grover counts to a 2D heatmap.
    Works best when 2^n_qubits is a perfect square (e.g. 4, 16, 64, 256...).
    """
    N = 2 ** n_qubits
    grid_size = int(np.sqrt(N))

    # Convert bitstrings → integer indices
    values = np.zeros((grid_size, grid_size))
    for bitstring, freq in counts.items():
        idx = int(bitstring, 2)
        x, y = divmod(idx, grid_size)
        values[x, y] = freq

    # Normalize for color intensity
    norm = values / np.max(values)

    plt.figure(figsize=(6, 5))
    plt.imshow(norm, cmap="plasma", origin="lower")
    plt.colorbar(label="Relative frequency")
    plt.title(f"Grover heatmap — {grid_size}×{grid_size} grid ({n_qubits} qubits)")
    plt.xlabel("Column")
    plt.ylabel("Row")
    plt.tight_layout()
    plt.show()

# -------------------------------------------------------------------
# 🚀 Run Grover's algorithm
# -------------------------------------------------------------------
def run_grover(n_qubits: int, target_index: int, shots: int = 1024, plot: bool = True):
    """
    Runs Grover's algorithm on n_qubits for a target_index (0–2^n - 1)
    Returns the measured counts dictionary.
    """

    oracle = build_oracle(n_qubits, target_index)
    diffuser = build_diffuser(n_qubits)

    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))  # start in uniform superposition

    # Optimal number of iterations: ~pi/4 * sqrt(N)
    n_iterations = 1 #max(1, int(math.floor((math.pi / 4) * math.sqrt(2 ** n_qubits) / 2)))

    for _ in range(n_iterations):
        qc.compose(oracle, inplace=True)
        qc.compose(diffuser, inplace=True)

    qc.measure_all()

    sim = AerSimulator()
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()

    if plot:
        plot_grover_heatmap(counts, n_qubits)


    print(f"🔎 Most likely ship cell: {max(counts, key=counts.get)} (target was {target_index})")
    return counts


# -------------------------------------------------------------------
# 🧩 Example test
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Example: 5 qubits (32 possible cells), hidden ship at cell index 13
    run_grover(n_qubits=8, target_index=33, shots=128)
