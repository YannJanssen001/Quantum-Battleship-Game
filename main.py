# main.py
import tkinter as tk
import random
import math
from visual import QuantumBattleshipGUI

def generate_random_ships(grid_size, num_ships):
    """Generate random ship positions ensuring no duplicates."""
    ships = set()
    max_attempts = grid_size * grid_size * 2  # Prevent infinite loops
    attempts = 0
    
    while len(ships) < num_ships and attempts < max_attempts:
        row = random.randint(0, grid_size - 1)
        col = random.randint(0, grid_size - 1)
        ships.add((row, col))
        attempts += 1
    
    if len(ships) < num_ships:
        print(f"Warning: Could only place {len(ships)} ships out of {num_ships} requested")
    
    return list(ships)

def main():
    grid_size = 8  # Increased from 5 to 8 (64 cells total, requires 6 qubits)
    region_size = 2
    num_ships = 8  # Increased ships proportionally
    
    # Generate random ship positions
    ships = generate_random_ships(grid_size, num_ships)
    print(f"🚢 Ships placed at: {ships}")  # Show ship positions for debugging
    print(f"🔬 Grid size: {grid_size}x{grid_size} = {grid_size*grid_size} cells")
    print(f"🌌 Qubits needed: {math.ceil(math.log2(grid_size * grid_size))}")

    root = tk.Tk()
    game = QuantumBattleshipGUI(root, grid_size=grid_size, region_size=region_size, ships=ships)
    root.mainloop()

if __name__ == "__main__":
    main()
