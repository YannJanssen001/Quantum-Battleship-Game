# visual_ui.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os


class QuantumBattleshipUI:
    """
    Pure UI component for Quantum Battleship.
    Handles only visual rendering, user input, and display.
    """
    
    def __init__(self, root, game_controller, grid_size=8):
        self.root = root
        self.game_controller = game_controller
        self.grid_size = grid_size
        self.selection_mode = "square"
        self.region_size = 2
        
        self.root.title("Quantum Battleship")
        self.cell_size = 80
        canvas_size = self.grid_size * self.cell_size
        
        # Initialize UI state
        self.selected_region = []
        self.cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.cell_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        self.setup_ui(canvas_size)
        self.load_assets()
        self.draw_grid()
        
    def setup_ui(self, canvas_size):
        """Setup the main UI components."""
        # Main container
        self.frame = tk.Frame(self.root, bg="#003366")
        self.frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(
            self.frame,
            text="QUANTUM BATTLESHIP",
            font=("Helvetica", 22, "bold"),
            bg="#003366",
            fg="white"
        )
        title_label.pack(pady=(10, 0))
        
        # Instructions
        instr_label = tk.Label(
            self.frame,
            text="Choose your targeting mode and select region to scan for enemy ships.",
            font=("Helvetica", 12),
            bg="#003366",
            fg="lightblue"
        )
        instr_label.pack(pady=(5, 15))
        
        # Canvas
        self.canvas = tk.Canvas(
            self.frame,
            width=canvas_size,
            height=canvas_size,
            highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)
        self.canvas.bind("<Button-1>", self.on_click)
        
        # Selection mode controls
        self.setup_targeting_controls()
        
        # Fire button
        self.setup_fire_button()
    
    def setup_targeting_controls(self):
        """Setup the targeting mode selection controls."""
        mode_container = tk.Frame(self.frame, bg="#003366")
        mode_container.pack(pady=15)
        
        # Title with better visibility
        mode_title = tk.Label(
            mode_container,
            text="QUANTUM TARGETING SYSTEM",
            font=("Helvetica", 16, "bold"),
            bg="#003366",
            fg="#ffffff"
        )
        mode_title.pack(pady=(0, 15))
        
        # Much more prominent frame for radio buttons
        mode_frame = tk.Frame(
            mode_container, 
            bg="#ffffff",  # White background for maximum contrast
            relief="solid", 
            bd=3,
            padx=20,
            pady=15
        )
        mode_frame.pack(padx=30, pady=10)
        
        self.mode_var = tk.StringVar(value="square")
        modes = [
            ("2x2 Square", "square", "Precision targeting"),
            ("Full Row", "row", "Horizontal sweep"),
            ("Full Column", "column", "Vertical sweep")
        ]
        
        for i, (text, mode, description) in enumerate(modes):
            # Container for each radio button with clear separation
            radio_container = tk.Frame(mode_frame, bg="#ffffff", relief="ridge", bd=2)
            radio_container.pack(side=tk.LEFT, padx=8, pady=5, fill="both", expand=True)
            
            # Use Button instead of Radiobutton for better visual feedback
            def make_button_command(mode_val):
                def command():
                    self.mode_var.set(mode_val)
                    self.change_selection_mode()
                    self.update_button_styles()
                return command
            
            button = tk.Button(
                radio_container,
                text=text,
                command=make_button_command(mode),
                font=("Helvetica", 12, "bold"),
                relief="raised",
                bd=3,
                padx=15,
                pady=10,
                cursor="hand2"
            )
            button.pack(fill="x", pady=(5, 2))
            
            # Store button reference for styling updates
            if not hasattr(self, 'mode_buttons'):
                self.mode_buttons = {}
            self.mode_buttons[mode] = button
            
            # Description label
            desc_label = tk.Label(
                radio_container,
                text=description,
                font=("Helvetica", 9, "italic"),
                bg="#ffffff",
                fg="#666666"
            )
            desc_label.pack(pady=(0, 5))
        
        # Initialize button styles
        self.update_button_styles()
    
    def setup_fire_button(self):
        """Setup the fire button and status display."""
        button_container = tk.Frame(self.frame, bg="#003366")
        button_container.pack(pady=25)
        
        # Fire button with enhanced styling
        self.shoot_btn = tk.Button(
            button_container,
            text="FIRE GROVER SHOT",
            font=("Helvetica", 18, "bold"),
            bg="#ff3333",
            fg="white",
            activebackground="#ff5555",
            activeforeground="white",
            relief="raised",
            bd=5,
            padx=40,
            pady=20,
            command=self.fire_shot,
            cursor="hand2"
        )
        self.shoot_btn.pack()
        
        # Enhanced hover effects
        def on_enter(e):
            self.shoot_btn.config(bg="#ff5555", relief="raised", bd=7)
        
        def on_leave(e):
            self.shoot_btn.config(bg="#ff3333", relief="raised", bd=5)
        
        self.shoot_btn.bind("<Enter>", on_enter)
        self.shoot_btn.bind("<Leave>", on_leave)
        
        # Status label with better visibility
        self.status_label = tk.Label(
            button_container,
            text="Select a region on the grid to begin quantum scan",
            font=("Helvetica", 12, "italic"),
            bg="#ffffff",
            fg="#000000",
            relief="solid",
            bd=1,
            padx=20,
            pady=10
        )
        self.status_label.pack(pady=(15, 0))
    
    def update_button_styles(self):
        """Update the visual style of mode selection buttons."""
        if not hasattr(self, 'mode_buttons'):
            return
            
        current_mode = self.mode_var.get()
        
        for mode, button in self.mode_buttons.items():
            if mode == current_mode:
                # Selected button - bright green with white text
                button.config(
                    bg="#00cc00",
                    fg="white", 
                    relief="sunken",
                    bd=4,
                    activebackground="#00aa00",
                    activeforeground="white"
                )
            else:
                # Unselected button - light gray with dark text
                button.config(
                    bg="#f0f0f0",
                    fg="#000000",
                    relief="raised", 
                    bd=2,
                    activebackground="#e0e0e0",
                    activeforeground="#000000"
                )
    
    def load_assets(self):
        """Load image assets for the game."""
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
                    print(f"Could not load image {path}: {e}")
                    return None
            else:
                print(f"Missing asset: {path}")
                return None
        
        self.bg_img = safe_load("water.png")
        self.ship_img = safe_load("ship.png")
        self.splash_img = safe_load("splash.png")
    
    def draw_grid(self):
        """Draw the game grid."""
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
    
    def on_click(self, event):
        """Handle mouse clicks on the grid."""
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if row >= self.grid_size or col >= self.grid_size:
            return
        self.highlight_region(row, col)
    
    def highlight_region(self, row, col):
        """Highlight the selected region based on current mode."""
        # Reset previous highlights
        found_ships = self.game_controller.get_found_ships()
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) not in found_ships:
                    self.canvas.itemconfig(self.cells[i][j], outline="#99ccff", width=2, fill="")
        
        # Get region coordinates from game controller
        self.selected_region = self.game_controller.get_region_coords(
            row, col, self.selection_mode, self.region_size
        )
        
        # Highlight selected region with both outline and semi-transparent fill
        for rr, cc in self.selected_region:
            if 0 <= rr < self.grid_size and 0 <= cc < self.grid_size:
                self.canvas.itemconfig(
                    self.cells[rr][cc], 
                    outline="#ffff00", 
                    width=5,
                    fill="#ffffaa"  # Light yellow fill
                )
        
        # Update status with high contrast
        region_size = len(self.selected_region)
        self.status_label.config(
            text=f"Ready! {region_size} cells selected. Fire when ready!",
            bg="#00ff00",  # Bright green background when ready
            fg="#000000"
        )
    
    def change_selection_mode(self):
        """Handle selection mode changes."""
        self.selection_mode = self.mode_var.get()
        
        # Update button styles to show selection
        self.update_button_styles()
        
        # Clear current selection
        found_ships = self.game_controller.get_found_ships()
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) not in found_ships:
                    self.canvas.itemconfig(self.cells[i][j], outline="#99ccff", width=2, fill="")
        self.selected_region = []
        
        # Update status with high contrast
        mode_descriptions = {
            "square": "Click any cell to select a 2x2 quantum targeting square",
            "row": "Click any cell to select an entire row for scanning",
            "column": "Click any cell to select an entire column for scanning"
        }
        self.status_label.config(
            text=mode_descriptions.get(self.selection_mode, "Select a region to scan"),
            bg="#ffffff",
            fg="#000000"
        )
    
    def fire_shot(self):
        """Handle fire button click."""
        if not self.selected_region:
            messagebox.showwarning("Warning", "Please select a region first!")
            return
        
        # Execute shot through game controller
        result = self.game_controller.fire_shot(self.selected_region)
        
        # Handle result
        if "error" in result:
            messagebox.showinfo("Info", result["error"])
            return
        
        # Update visual based on result
        if result["type"] == "hit":
            self.place_marker(result["coords"], hit=True)
        elif result["type"] == "miss" and result["coords"]:
            self.place_marker(result["coords"], hit=False)
        
        # Show result message
        messagebox.showinfo("Grover Result", result["message"])
        
        # Check for win condition
        if self.game_controller.is_game_won():
            messagebox.showinfo("VICTORY!", "You've found all enemy ships!")
            self.shoot_btn.config(state="disabled")
    
    def place_marker(self, coords, hit=False):
        """Place a visual marker (ship or splash) at the given coordinates."""
        x, y = coords
        cx = y * self.cell_size + self.cell_size // 2
        cy = x * self.cell_size + self.cell_size // 2
        
        # Remove existing overlay
        if self.cell_overlays[x][y]:
            self.canvas.delete(self.cell_overlays[x][y])
        
        # Place appropriate marker
        if hit and self.ship_img:
            self.cell_overlays[x][y] = self.canvas.create_image(cx, cy, image=self.ship_img)
        elif not hit and self.splash_img:
            self.cell_overlays[x][y] = self.canvas.create_image(cx, cy, image=self.splash_img)
        else:
            color = "#ff3333" if hit else "#99ccff"
            self.canvas.itemconfig(self.cells[x][y], fill=color)