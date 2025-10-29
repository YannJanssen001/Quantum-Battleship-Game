import numpy as np
import random
import math
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

class QuantumBattleship:
    def __init__(self, grid_size=5, num_ships=3):
        self.grid_size = grid_size
        self.num_ships = num_ships
        self.moves_made = 0
        self.ships_found = 0
        
        # Initialize the true ship positions (hidden from player)
        self.ship_positions = self._place_ships()
        
        # Initialize probability grid (all squares start in superposition)
        self.probability_grid = np.full((grid_size, grid_size), 0.5)
        
        # Track which squares have been fully collapsed
        self.collapsed_grid = np.zeros((grid_size, grid_size), dtype=bool)
        
        # Track which squares have ships (revealed through gameplay)
        self.revealed_ships = np.zeros((grid_size, grid_size), dtype=bool)
        
        # Zeno watch counters for each square
        self.zeno_counters = np.zeros((grid_size, grid_size), dtype=int)
        
        print(f"🚢 Quantum Battleship initialized!")
        print(f"Grid: {grid_size}x{grid_size}, Ships: {num_ships}")
        print(f"Find all ships using quantum-inspired moves!\n")
    
    def _place_ships(self):
        """Randomly place ships on the grid"""
        positions = []
        while len(positions) < self.num_ships:
            x, y = random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)
            if (x, y) not in positions:
                positions.append((x, y))
        return positions
    
    def display_board(self):
        """Display the current state of the board"""
        print("🎯 Current Board State:")
        print("   ", end="")
        for j in range(self.grid_size):
            print(f" {j+1} ", end="")
        print()
        
        for i in range(self.grid_size):
            print(f"{i+1}  ", end="")
            for j in range(self.grid_size):
                if self.revealed_ships[i][j]:
                    print("🚢 ", end="")  # Found ship
                elif self.collapsed_grid[i][j]:
                    print("💧 ", end="")  # Empty water (collapsed)
                else:
                    # Show probability as colored squares
                    prob = self.probability_grid[i][j]
                    if prob > 0.8:
                        print("🔴", end="")  # High probability
                    elif prob > 0.6:
                        print("🟠", end="")  # Medium-high probability
                    elif prob > 0.4:
                        print("🟡", end="")  # Medium probability
                    elif prob > 0.2:
                        print("🟢", end="")  # Low-medium probability
                    else:
                        print("🔵", end="")  # Low probability
                print(" ", end="")
            print()
        
        print(f"\n📊 Ships found: {self.ships_found}/{self.num_ships}")
        print(f"🎮 Moves made: {self.moves_made}")
        print(f"🎯 Efficiency: {self.ships_found/max(1, self.moves_made):.2f}\n")
    
    def classical_shot(self, x, y):
        """Classical shot: Instantly collapse the quantum state"""
        if self.collapsed_grid[x][y] or self.revealed_ships[x][y]:
            print("❌ Square already measured!")
            return False
        
        self.moves_made += 1
        self.collapsed_grid[x][y] = True
        
        if (x, y) in self.ship_positions:
            self.revealed_ships[x][y] = True
            self.ships_found += 1
            self.probability_grid[x][y] = 1.0
            print(f"💥 DIRECT HIT at ({x+1}, {y+1})! Ship destroyed!")
        else:
            self.probability_grid[x][y] = 0.0
            print(f"💧 Miss at ({x+1}, {y+1}). Square collapsed to empty.")
        
        return True
    
    def quantum_probe(self, x, y):
        """Quantum probe: Elitzur-Vaidman bomb tester inspired move"""
        if self.collapsed_grid[x][y] or self.revealed_ships[x][y]:
            print("❌ Square already measured!")
            return False
        
        self.moves_made += 1
        
        # Quantum probe gives partial information without full collapse
        if (x, y) in self.ship_positions:
            # With 70% probability, detect the ship without destroying it
            if random.random() < 0.7:
                self.probability_grid[x][y] = 0.9  # Very high probability
                print(f"🔍 Quantum probe detected high ship probability at ({x+1}, {y+1})!")
            else:
                # 30% chance of accidental collapse
                self.revealed_ships[x][y] = True
                self.ships_found += 1
                self.collapsed_grid[x][y] = True
                self.probability_grid[x][y] = 1.0
                print(f"💥 Quantum probe accidentally triggered ship at ({x+1}, {y+1})!")
        else:
            # No ship: reduce probability but don't fully collapse
            self.probability_grid[x][y] *= 0.3
            print(f"🔍 Quantum probe suggests low ship probability at ({x+1}, {y+1}).")
        
        return True
    
    def zeno_watch(self, x, y):
        """Zeno watch: Quantum Zeno effect - repeated gentle measurements"""
        if self.collapsed_grid[x][y] or self.revealed_ships[x][y]:
            print("❌ Square already measured!")
            return False
        
        self.moves_made += 1
        self.zeno_counters[x][y] += 1
        
        if (x, y) in self.ship_positions:
            # Each Zeno measurement increases certainty
            zeno_factor = 1 - (0.5 ** self.zeno_counters[x][y])
            self.probability_grid[x][y] = min(0.95, 0.5 + zeno_factor * 0.4)
            
            # After enough measurements, "freeze" and reveal the ship
            if self.zeno_counters[x][y] >= 3:
                self.revealed_ships[x][y] = True
                self.ships_found += 1
                self.collapsed_grid[x][y] = True
                self.probability_grid[x][y] = 1.0
                print(f"⏰ Zeno effect froze and revealed ship at ({x+1}, {y+1})!")
            else:
                print(f"⏰ Zeno watch #{self.zeno_counters[x][y]} at ({x+1}, {y+1}). Probability: {self.probability_grid[x][y]:.2f}")
        else:
            # Gradually reduce probability for empty squares
            reduction = 0.6 ** self.zeno_counters[x][y]
            self.probability_grid[x][y] = max(0.05, 0.5 * reduction)
            print(f"⏰ Zeno watch #{self.zeno_counters[x][y]} at ({x+1}, {y+1}). Probability: {self.probability_grid[x][y]:.2f}")
        
        return True
    
    def grover_shot(self, region_coords):
        """Grover shot: Amplify probabilities in a region using quantum search principles"""
        if len(region_coords) == 0:
            print("❌ No coordinates provided for Grover shot!")
            return False
        
        self.moves_made += 1
        
        # Check if any ships are in the target region
        ships_in_region = []
        total_coords = []
        
        for x, y in region_coords:
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                total_coords.append((x, y))
                if (x, y) in self.ship_positions and not self.revealed_ships[x][y]:
                    ships_in_region.append((x, y))
        
        if not total_coords:
            print("❌ Invalid coordinates for Grover shot!")
            return False
        
        # Grover's algorithm amplifies marked items
        if ships_in_region:
            # Amplify ship probabilities
            for x, y in ships_in_region:
                if not self.collapsed_grid[x][y]:
                    self.probability_grid[x][y] = min(0.95, self.probability_grid[x][y] * 1.8)
            
            # Suppress non-ship probabilities in the region
            for x, y in total_coords:
                if (x, y) not in ships_in_region and not self.collapsed_grid[x][y]:
                    self.probability_grid[x][y] *= 0.7
            
            print(f"🔍 Grover shot amplified {len(ships_in_region)} ship signature(s) in the target region!")
        else:
            # No ships in region - reduce all probabilities
            for x, y in total_coords:
                if not self.collapsed_grid[x][y]:
                    self.probability_grid[x][y] *= 0.4
            
            print(f"🔍 Grover shot found no ships in the target region. Probabilities reduced.")
        
        return True
    
    def is_game_won(self):
        """Check if all ships have been found"""
        return self.ships_found == self.num_ships
    
    def get_score(self):
        """Calculate final score based on efficiency"""
        if self.ships_found == 0:
            return 0
        efficiency = self.ships_found / self.moves_made
        bonus = max(0, (self.grid_size * self.grid_size - self.moves_made) * 10)
        return int(efficiency * 1000 + bonus)

def get_coordinates():
    """Helper function to get coordinates from user"""
    try:
        x = int(input("Enter row (1-5): ")) - 1
        y = int(input("Enter column (1-5): ")) - 1
        return x, y
    except ValueError:
        print("❌ Invalid input! Please enter numbers.")
        return None, None

def get_grover_region():
    """Helper function to get multiple coordinates for Grover shot"""
    coords = []
    print("Enter coordinates for Grover shot region (press Enter when done):")
    print("📝 Format examples: 2,3 or (2,3) or 2 3")
    while True:
        try:
            coord_input = input(f"Coordinate {len(coords)+1} (row,col) or Enter to finish: ")
            if not coord_input.strip():
                break
            
            # Clean up input - remove parentheses and extra spaces
            cleaned_input = coord_input.strip().replace('(', '').replace(')', '').replace(' ', ',')
            
            # Split by comma or space
            parts = [p.strip() for p in cleaned_input.split(',') if p.strip()]
            
            if len(parts) == 2:
                x = int(parts[0]) - 1
                y = int(parts[1]) - 1
                
                # Validate coordinates are within grid
                if 0 <= x < 5 and 0 <= y < 5:
                    coords.append((x, y))
                    print(f"✅ Added ({x+1}, {y+1})")
                else:
                    print(f"❌ Coordinates ({int(parts[0])}, {int(parts[1])}) are outside the 5x5 grid! Use 1-5.")
            else:
                print("❌ Format: row,col (e.g., 2,3 or (2,3))")
        except ValueError:
            print("❌ Invalid format! Use numbers only (e.g., 2,3)")
    
    return coords

def main():
    """Main game loop"""
    print("🌌 Welcome to Quantum Battleship! 🌌")
    print("=" * 50)
    
    game = QuantumBattleship()
    
    while not game.is_game_won():
        game.display_board()
        
        print("🎮 Choose your quantum move:")
        print("1. 🎯 Classical Shot (instant collapse)")
        print("2. 🔍 Quantum Probe (partial information)")
        print("3. ⏰ Zeno Watch (gradual measurement)")
        print("4. 🚀 Grover Shot (region amplification)")
        print("5. 🏳️  Surrender")
        
        try:
            choice = int(input("Enter your choice (1-5): "))
            
            if choice == 1:
                x, y = get_coordinates()
                if x is not None and y is not None:
                    game.classical_shot(x, y)
            
            elif choice == 2:
                x, y = get_coordinates()
                if x is not None and y is not None:
                    game.quantum_probe(x, y)
            
            elif choice == 3:
                x, y = get_coordinates()
                if x is not None and y is not None:
                    game.zeno_watch(x, y)
            
            elif choice == 4:
                coords = get_grover_region()
                game.grover_shot(coords)
            
            elif choice == 5:
                print("🏳️ Game surrendered!")
                break
            
            else:
                print("❌ Invalid choice! Please select 1-5.")
                continue
        
        except ValueError:
            print("❌ Invalid input! Please enter a number.")
            continue
        
        print("\n" + "-" * 50 + "\n")
    
    if game.is_game_won():
        print("🎉 CONGRATULATIONS! 🎉")
        print(f"You found all {game.num_ships} ships!")
        print(f"Final Score: {game.get_score()}")
        print(f"Moves Used: {game.moves_made}")
        print(f"Efficiency: {game.ships_found/game.moves_made:.2f}")
        
        # Show final board with all ships revealed
        print("\n🗺️ Final board (all ships revealed):")
        for i, (x, y) in enumerate(game.ship_positions):
            game.revealed_ships[x][y] = True
        game.display_board()

if __name__ == "__main__":
    main()