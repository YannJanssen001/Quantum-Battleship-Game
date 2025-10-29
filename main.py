# main.py
import tkinter as tk
from game_controller import GameController
from visual_ui import QuantumBattleshipUI


def main():
    """Main entry point for Quantum Battleship game."""
    # Game configuration
    grid_size = 8  # 8x8 grid (64 cells, requires 6 qubits)
    num_ships = 8  # Number of ships to place randomly
    
    # Initialize the game
    root = tk.Tk()
    controller = GameController(grid_size, num_ships)
    ui = QuantumBattleshipUI(root, controller, grid_size)
    
    # Start the game loop
    root.mainloop()


if __name__ == "__main__":
    main()
