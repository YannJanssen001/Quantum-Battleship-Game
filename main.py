# main.py
import tkinter as tk
from visual import QuantumBattleshipGUI

def main():
    grid_size = 5
    region_size = 2
    ships = [(0,0), (1,2), (3,4)]  # Example ship positions

    root = tk.Tk()
    game = QuantumBattleshipGUI(root, grid_size=grid_size, region_size=region_size, ships=ships)
    root.mainloop()

if __name__ == "__main__":
    main()
