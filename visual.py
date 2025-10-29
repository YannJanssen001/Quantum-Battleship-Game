# visual.py
import tkinter as tk
from tkinter import messagebox
import math
from grovershot import grover_shot

class QuantumBattleshipGUI:
    def __init__(self, root, grid_size=5, region_size=2, ships=None):
        self.root = root
        self.grid_size = grid_size
        self.region_size = region_size
        self.ships = ships or []
        self.found_ships = set()  # ✅ keeps track of discovered ships
        
        self.root.title("🌌 Quantum Battleship")
        self.cell_size = 80
        self.canvas = tk.Canvas(root, width=self.grid_size*self.cell_size, height=self.grid_size*self.cell_size)
        self.canvas.pack()

        self.start_cell = None
        self.region_rect = None
        self.selected_region = []

        self.cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.draw_grid()

        # Fire button
        self.shoot_btn = tk.Button(root, text="🚀 Fire Grover Shot", command=self.fire_grover_shot)
        self.shoot_btn.pack(pady=10)

        # Mouse click binding
        self.canvas.bind("<Button-1>", self.on_click)

    # --- Helper conversion functions ---
    def coords_to_index(self, x, y):
        return x * self.grid_size + y

    def index_to_coords(self, index):
        """Convert a linear index back to (row, col)."""
        return divmod(index, self.grid_size)

    def coords_to_indices(self, coords):
        return [self.coords_to_index(x, y) for x, y in coords if 0 <= x < self.grid_size and 0 <= y < self.grid_size]

    # --- Draw grid ---
    def draw_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x0, y0 = j * self.cell_size, i * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                rect = self.canvas.create_rectangle(x0, y0, x1, y1, outline="gray", width=2, fill="white")
                self.cells[i][j] = rect

    # --- Handle region selection ---
    def on_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if row >= self.grid_size or col >= self.grid_size:
            return
        self.highlight_region(row, col)

    def highlight_region(self, row, col):
        # Reset previous highlight (but keep found ships red)
        if self.region_rect:
            for r in self.region_rect:
                self.canvas.itemconfig(r, fill="white")
        for (x, y) in self.found_ships:
            self.canvas.itemconfig(self.cells[x][y], fill="#ff3333")

        self.region_rect = []
        self.selected_region = []
        for dx in range(self.region_size):
            for dy in range(self.region_size):
                rr, cc = row + dx, col + dy
                if 0 <= rr < self.grid_size and 0 <= cc < self.grid_size:
                    self.canvas.itemconfig(self.cells[rr][cc], fill="#99ccff")
                    self.region_rect.append(self.cells[rr][cc])
                    self.selected_region.append((rr, cc))

    def fire_grover_shot(self):
        if not self.selected_region:
            messagebox.showwarning("⚠️ Warning", "Please select a region first!")
            return

        region_indices = self.coords_to_indices(self.selected_region)
        ship_indices = self.coords_to_indices(self.ships)
        ships_in_region = [s for s in ship_indices if s in region_indices]

        n_qubits = math.ceil(math.log2(self.grid_size * self.grid_size))

        if ships_in_region:
            result = grover_shot(n_qubits, ships_in_region)
        else:
            # No ships — skip Grover, fake a miss result
            result = {
                "hit": False,
                "measured_index": None,
                "measured_state": None,
                "iterations": 0,
                "counts": {},
            }

        hit = result["hit"]
        measured = result["measured_index"]

        if hit and measured is not None:
            msg = f"💥 Hit! Ship detected at cell index {measured}!"
            color = "#ff3333"
            coords = self.index_to_coords(measured)
            self.found_ships.add(coords)  # ✅ remember found ship
        else:
            msg = f"💧 Miss! No ship detected in this region."
            color = "#dddddd"

        for (r, c) in self.selected_region:
            if (r, c) not in self.found_ships:
                self.canvas.itemconfig(self.cells[r][c], fill=color)

        messagebox.showinfo("Grover Result", msg)

        # ✅ Check for win condition
        if self.all_ships_found():
            messagebox.showinfo("🏁 Victory!", "You’ve found all enemy ships!")
            self.shoot_btn.config(state="disabled")

    def all_ships_found(self):
        """Check if all ships have been discovered."""
        return set(self.ships) == self.found_ships
