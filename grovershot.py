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


# --- Game parameters ---
n_qubits = 5                    # 5 qubits → 32 possible cells
ship_position = 0            # hidden cell index (0–31)

# --- Build the circuit ---
qc = QuantumCircuit(n_qubits)
qc.h(range(n_qubits))           # uniform superposition over all 32 cells

# --- Oracle: mark the ship cell with a phase flip ---
binary_ship = format(ship_position, f'0{n_qubits}b')  # e.g. '10011'
for i, bit in enumerate(reversed(binary_ship)):
    if bit == '0':
        qc.x(i)                 # X to flip controls for matching 0s
qc.h(n_qubits-1)
qc.mcx(list(range(n_qubits-1)), n_qubits-1)  # multi-controlled Z
qc.h(n_qubits-1)
for i, bit in enumerate(reversed(binary_ship)):
    if bit == '0':
        qc.x(i)                 # uncompute
qc.barrier()

# --- Diffusion operator (Grover reflection) ---
qc.h(range(n_qubits))
qc.x(range(n_qubits))
qc.h(n_qubits-1)
qc.mcx(list(range(n_qubits-1)), n_qubits-1)
qc.h(n_qubits-1)
qc.x(range(n_qubits))
qc.h(range(n_qubits))
qc.barrier()

# --- Measure ---
qc.measure_all()

# --- Simulate ---
sim = AerSimulator()
result = sim.run(qc, shots=1024).result()
counts = result.get_counts()

# --- Show results ---
#print("Hidden ship at:", ship_position)
plot_histogram(counts)
plt.show()
