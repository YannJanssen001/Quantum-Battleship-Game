import math
import numpy as np
import numba 
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, SparsePauliOp, Statevector
from qiskit.visualization import plot_histogram, plot_bloch_multivector
#from qiskit_aer import AerSimulator
from qiskit.circuit import Parameter, ParameterVector
import qiskit.qasm3
#from qiskit_ibm_runtime.fake_provider import FakeVigoV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
#from qiskit_ibm_runtime import SamplerV2 as Sampler, EstimatorV2 as Estimator, QiskitRuntimeService

n = 4
N = 2**n
R = math.floor(math.sqrt(N) * (math.pi/4))

qc = QuantumCircuit(n)

# Superposition
qc.h(range(n))

# Oracle for |1000>
def oracle(qc):
    qc.x([0,1,2])
    qc.h(n-1)
    qc.mcx([0,1,2], n-1)
    qc.h(n-1)
    qc.x([0,1,2])
    return qc

# Diffuser
def diffuser(qc):
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n-1)
    qc.mcx([0,1,2], n-1)
    qc.h(n-1)
    qc.x(range(n))
    qc.h(range(n))
    return qc

# Grover iterations
for _ in range(R):
    oracle(qc)
    diffuser(qc)
"""
qc.measure_all()
display(qc.draw("mpl"))

# Transpile and simulate
backend = FakeVigoV2()
pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
qc_isa = pm.run(qc)

sampler = Sampler(backend)
job = sampler.run([qc_isa], shots=100)
result = job.result()

counts = result[0].data["meas"].get_counts()
print(counts)
plot_histogram(counts)
"""