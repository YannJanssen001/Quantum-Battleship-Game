from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, SparsePauliOp, Statevector
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit import QuantumCircuit as QC
import numpy as np
import math

def change_grid(grid):
    
    x = int(input("Please choose a coordinate to place a ship\n" "x = "))
    y = int(input("y = "))

    grid[x-1][y-1] = 1

    return grid

def choose_row_col(grid):

    print(grid)

    choice = str(input("Choose either to pick a row or column: "))
    
    if choice == "row":
        y = int(input("Pick a row:"))
        row = grid[y-1,:]
        print(row)
        return row

    elif choice == "column":
        x = int(input("Pick a column:"))
        col = grid[:,x-1]
        print(col)
        return col
    
    else:
        print("Not an option bro")

n = 5
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


def main():
    
    grid = np.zeros([5,5])
    change_grid(grid)
    choose_row_col(grid)
    
main()