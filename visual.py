import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import math
import os
from grovershot import grover_shot


class QuantumBattleshipGUI:
    def __init__(self, root, grid_size=5, region_size=2, ships=None):
        self.root = root
        self.grid_size = grid_size
        self.region_size = region_size
        self.ships = ships or []
        self.found_ships = set()  # ✅ discovered ships (locked squares)

        self.root.title("🌊 Quantum Battleship")
        self.cell_size = 80
        canvas_size = self.grid_size * self.cell_size

        # --- UI container ---
        self.frame = tk.Frame(root, bg="#003366")
        self.frame.pack(fill="both", expand=True)

        # --- Canvas setup ---
        self.canvas = tk.Canvas(
            self.frame,
            width=canvas_size,
            height=canvas_size,
            highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)

        # --- Asset loading ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "assets")

        def safe_load(filename):
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    img = img.resize((self.cell_size, self.cell_size), Image.LANCZOS)
                    return ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"⚠️ Could not load image {path}: {e}")
                    return None
            else:
                print(f"⚠️ Missing asset: {path}")
                return None

        self.bg_img = safe_load("water.png")
        self.ship_img = safe_load("ship.png")
        self.splash_img = safe_load("splash.png")

        # --- Labels ---
        title_label = tk.Label(
            self.frame,
            text="⚓ Quantum Battleship ⚓",
            font=("Helvetica", 22, "bold"),
            bg="#003366",
            fg="white"
        )
        title_label.pack(pady=(10, 0))

        instr_label = tk.Label(
            self.frame,
            text="Select a 2×2 region to scan for enemy ships, then press 'Fire Grover Shot'.",
            font=("Helvetica", 12),
            bg="#003366",
            fg="lightblue"
        )
        instr_label.pack(pady=(5, 10))

        # --- Grid setup ---
        self.cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.cell_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.region_rect = None
        self.selected_region = []
        self.draw_grid()

        # Selection mode controls
        mode_frame = tk.Frame(root)
        mode_frame.pack(pady=5)
        
        tk.Label(mode_frame, text="Selection Mode:").pack(side=tk.LEFT, padx=5)
        
        self.mode_var = tk.StringVar(value="square")
        modes = [("2x2 Square", "square"), ("Row", "row"), ("Column", "column")]
        
        for text, mode in modes:
            tk.Radiobutton(
                mode_frame, 
                text=text, 
                variable=self.mode_var, 
                value=mode,
                command=self.change_selection_mode
            ).pack(side=tk.LEFT, padx=5)

        # Fire button
        self.shoot_btn = tk.Button(root, text="🚀 Fire Grover Shot", command=self.fire_grover_shot)
        self.shoot_btn.pack(pady=10)
        # --- Fire button ---
        self.shoot_btn = tk.Button(
            self.frame,
            text="🚀 Fire Grover Shot",
            font=("Helvetica", 14, "bold"),
            bg="#0066cc",
            fg="white",
            activebackground="#004c99",
            command=self.fire_grover_shot
        )
        self.shoot_btn.pack(pady=15)

        # --- Mouse binding ---
        self.canvas.bind("<Button-1>", self.on_click)

    def change_selection_mode(self):
        """Update selection mode and clear current selection."""
        self.selection_mode = self.mode_var.get()
        # Clear current selection when mode changes
        if self.region_rect:
            for r in self.region_rect:
                self.canvas.itemconfig(r, fill="white")
        # Restore found ships color
        for (x, y) in self.found_ships:
            self.canvas.itemconfig(self.cells[x][y], fill="#ff3333")
        self.region_rect = []
        self.selected_region = []

    # --- Helper conversion functions ---
    # --- Helpers ---
    def coords_to_index(self, x, y):
        return x * self.grid_size + y

    def index_to_coords(self, index):
        return divmod(index, self.grid_size)

    def coords_to_indices(self, coords):
        return [
            self.coords_to_index(x, y)
            for x, y in coords
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size
        ]

    # --- Draw grid background ---
    def draw_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x0, y0 = j * self.cell_size, i * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                if self.bg_img:
                    self.canvas.create_image(
                        x0 + self.cell_size // 2,
                        y0 + self.cell_size // 2,
                        image=self.bg_img
                    )
                rect = self.canvas.create_rectangle(
                    x0, y0, x1, y1,
                    outline="#99ccff", width=2, fill=""
                )
                self.cells[i][j] = rect

    # --- Region selection ---
    def on_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if row >= self.grid_size or col >= self.grid_size:
            return
        self.highlight_region(row, col)

    def highlight_region(self, row, col):
        # Reset previous highlights (keep ships red)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) not in self.found_ships:
                    self.canvas.itemconfig(self.cells[i][j], outline="#99ccff", width=2)

        self.selected_region = []
        
        if self.selection_mode == "square":
            # Original 2x2 square selection
            for dx in range(self.region_size):
                for dy in range(self.region_size):
                    rr, cc = row + dx, col + dy
                    if 0 <= rr < self.grid_size and 0 <= cc < self.grid_size:
                        self.canvas.itemconfig(self.cells[rr][cc], fill="#99ccff")
                        self.region_rect.append(self.cells[rr][cc])
                        self.selected_region.append((rr, cc))
        
        elif self.selection_mode == "row":
            # Select entire row
            for cc in range(self.grid_size):
                self.canvas.itemconfig(self.cells[row][cc], fill="#99ccff")
                self.region_rect.append(self.cells[row][cc])
                self.selected_region.append((row, cc))
        
        elif self.selection_mode == "column":
            # Select entire column
            for rr in range(self.grid_size):
                self.canvas.itemconfig(self.cells[rr][col], fill="#99ccff")
                self.region_rect.append(self.cells[rr][col])
                self.selected_region.append((rr, col))
        for dx in range(self.region_size):
            for dy in range(self.region_size):
                rr, cc = row + dx, col + dy
                if 0 <= rr < self.grid_size and 0 <= cc < self.grid_size:
                    self.canvas.itemconfig(self.cells[rr][cc], outline="yellow", width=3)
                    self.selected_region.append((rr, cc))

    # --- Fire Grover shot ---
    def fire_grover_shot(self):
        if not self.selected_region:
            messagebox.showwarning("⚠️ Warning", "Please select a region first!")
            return

        # If the region only includes already-found ships, skip search
        if all(cell in self.found_ships for cell in self.selected_region):
            messagebox.showinfo("🪙 Info", "This region already contains discovered ships.")
            return

        # Convert to indices
        region_indices = self.coords_to_indices(self.selected_region)
        remaining_ships = [s for s in self.ships if s not in self.found_ships]
        ship_indices = self.coords_to_indices(remaining_ships)
        ships_in_region = [s for s in ship_indices if s in region_indices]

        # If region includes found ships, remove them from search
        region_indices = [
            idx for idx in region_indices
            if self.index_to_coords(idx) not in self.found_ships
        ]

        if not region_indices:
            messagebox.showinfo("🪙 Info", "You already scanned this area — try another region.")
            return

        n_qubits = math.ceil(math.log2(self.grid_size * self.grid_size))

        if ships_in_region:
            result = grover_shot(n_qubits, ships_in_region)
        else:
            result = {"hit": False, "measured_index": None}

        hit = result["hit"]
        measured = result["measured_index"]

        if hit and measured is not None:
            coords = self.index_to_coords(measured)
            if coords not in self.found_ships:  # ✅ only mark once
                self.found_ships.add(coords)
                msg = f"💥 Hit! Ship detected at cell index {measured}!"
                self.place_marker(coords, hit=True)
            else:
                msg = f"🪙 Ship at index {measured} was already found."
        else:
            msg = f"💧 Miss! No ship detected in this region."
            # Avoid overwriting any ship cells
            for cell in self.selected_region:
                if cell not in self.found_ships:
                    self.place_marker(cell, hit=False)

        messagebox.showinfo("Grover Result", msg)

        # ✅ Win condition
        if self.all_ships_found():
            messagebox.showinfo("🏁 Victory!", "You’ve found all enemy ships!")
            self.shoot_btn.config(state="disabled")

    def place_marker(self, coords, hit=False):
        """Overlay ship or splash image."""
        x, y = coords
        cx = y * self.cell_size + self.cell_size // 2
        cy = x * self.cell_size + self.cell_size // 2

        # Prevent overwriting already-found ships
        if (x, y) in self.found_ships and not hit:
            return

        if self.cell_overlays[x][y]:
            self.canvas.delete(self.cell_overlays[x][y])

        if hit and self.ship_img:
            self.cell_overlays[x][y] = self.canvas.create_image(cx, cy, image=self.ship_img)
        elif not hit and self.splash_img:
            self.cell_overlays[x][y] = self.canvas.create_image(cx, cy, image=self.splash_img)
        else:
            color = "#ff3333" if hit else "#99ccff"
            self.canvas.itemconfig(self.cells[x][y], fill=color)

    def all_ships_found(self):
        """Check if all ships are found."""
        return set(self.ships) == self.found_ships
