import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import math
import random
import time

# Import the Grover's algorithm functions from your existing file
def build_oracle(n_qubits: int, target_index: int) -> QuantumCircuit:
    """Build an Oracle that marks one target state with a phase flip"""
    qc = QuantumCircuit(n_qubits)
    binary_target = format(target_index, f'0{n_qubits}b')

    # Flip qubits for bits that are 0 so that the mcx hits only |target>
    for i, bit in enumerate(reversed(binary_target)):
        if bit == '0':
            qc.x(i)

    # Multi-controlled Z (as H–MCX–H on last qubit)
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)

    # Uncompute the X gates
    for i, bit in enumerate(reversed(binary_target)):
        if bit == '0':
            qc.x(i)

    return qc


def build_diffuser(n_qubits: int) -> QuantumCircuit:
    """Build the Diffuser (inversion about the mean)"""
    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc


def build_multi_target_oracle(n_qubits: int, target_indices: list) -> QuantumCircuit:
    """Build an Oracle that marks multiple target states with a phase flip"""
    qc = QuantumCircuit(n_qubits)
    
    for target_index in target_indices:
        binary_target = format(target_index, f'0{n_qubits}b')

        # Flip qubits for bits that are 0 so that the mcx hits only |target>
        for i, bit in enumerate(reversed(binary_target)):
            if bit == '0':
                qc.x(i)

        # Multi-controlled Z (as H–MCX–H on last qubit)
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)

        # Uncompute the X gates
        for i, bit in enumerate(reversed(binary_target)):
            if bit == '0':
                qc.x(i)

    return qc


def run_grover_search(n_qubits: int, target_index: int, shots: int = 512):
    """Run Grover's algorithm to search for a single target"""
    oracle = build_oracle(n_qubits, target_index)
    diffuser = build_diffuser(n_qubits)

    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))  # start in uniform superposition

    # Optimal number of iterations
    n_iterations = max(1, int(math.floor((math.pi / 4) * math.sqrt(2 ** n_qubits) / 2)))

    for _ in range(n_iterations):
        qc.compose(oracle, inplace=True)
        qc.compose(diffuser, inplace=True)

    qc.measure_all()

    sim = AerSimulator()
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()
    
    return counts


def run_grover_multi_search(n_qubits: int, target_indices: list, shots: int = 512):
    """Run Grover's algorithm to search for multiple targets"""
    if not target_indices:
        return {}
        
    oracle = build_multi_target_oracle(n_qubits, target_indices)
    diffuser = build_diffuser(n_qubits)

    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))  # start in uniform superposition

    # Optimal number of iterations for multiple targets
    # Formula: pi/4 * sqrt(N/M) where N=total states, M=number of targets
    N = 2 ** n_qubits
    M = len(target_indices)
    n_iterations = max(1, int(math.floor((math.pi / 4) * math.sqrt(N / M))))

    for _ in range(n_iterations):
        qc.compose(oracle, inplace=True)
        qc.compose(diffuser, inplace=True)

    qc.measure_all()

    sim = AerSimulator()
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()
    
    return counts


class QuantumBattleship:
    def __init__(self, grid_size=4):
        """Initialize quantum battleship game"""
        self.grid_size = grid_size
        self.n_qubits = int(math.log2(grid_size * grid_size))
        self.total_cells = 2 ** self.n_qubits
        
        # Game state
        self.ships = self.place_ships()
        self.player_shots = set()
        self.ai_shots = set()
        self.player_hits = set()
        self.ai_hits = set()
        
        # Game settings
        self.max_quantum_shots = 3  # Limit AI quantum shots for fairness
        self.quantum_shots_used = 0
        self.player_quantum_shots = 2  # Player gets quantum shots too!
        self.player_quantum_used = 0
        
        print(f"🚢 Quantum Battleship - {grid_size}x{grid_size} Grid ({self.n_qubits} qubits)")
        print(f"Ships: {len(self.ships)} | Your Quantum Shots: {self.player_quantum_shots} | AI Quantum Shots: {self.max_quantum_shots}")
        print("=" * 70)

    def place_ships(self):
        """Place ships randomly on the grid"""
        num_ships = min(3, self.total_cells // 4)  # Reasonable number of ships
        ships = set()
        while len(ships) < num_ships:
            ships.add(random.randint(0, self.total_cells - 1))
        return ships

    def index_to_coords(self, index):
        """Convert linear index to (row, col) coordinates"""
        return divmod(index, self.grid_size)

    def coords_to_index(self, row, col):
        """Convert (row, col) coordinates to linear index"""
        return row * self.grid_size + col

    def get_row_indices(self, row):
        """Get all cell indices in a specific row"""
        return [self.coords_to_index(row, col) for col in range(self.grid_size)]

    def get_column_indices(self, col):
        """Get all cell indices in a specific column"""
        return [self.coords_to_index(row, col) for row in range(self.grid_size)]

    def get_2x2_area_indices(self, start_row, start_col):
        """Get all cell indices in a 2x2 area starting from (start_row, start_col)"""
        indices = []
        for r in range(start_row, min(start_row + 2, self.grid_size)):
            for c in range(start_col, min(start_col + 2, self.grid_size)):
                indices.append(self.coords_to_index(r, c))
        return indices

    def display_grid(self):
        """Display the current game state"""
        print("\n📊 GAME BOARD:")
        print("   ", end="")
        for col in range(self.grid_size):
            print(f" {col} ", end="")
        print()

        for row in range(self.grid_size):
            print(f" {row} ", end="")
            for col in range(self.grid_size):
                index = self.coords_to_index(row, col)
                
                if index in self.player_hits:
                    print(" 🎯", end="")  # Player hit
                elif index in self.ai_hits:
                    print(" 🤖", end="")  # AI hit
                elif index in self.player_shots:
                    print(" 💧", end="")  # Player miss
                elif index in self.ai_shots:
                    print(" ❌", end="")  # AI miss
                else:
                    print(" ⬜", end="")  # Unknown
            print()

    def player_turn(self):
        """Handle player's turn"""
        print(f"\n🎮 YOUR TURN (Ships remaining: {len(self.ships) - len(self.player_hits)})")
        print(f"🔮 Quantum shots available: {self.player_quantum_shots - self.player_quantum_used}")
        
        # Ask player for shot type
        if self.player_quantum_used < self.player_quantum_shots:
            print("\nChoose your shot type:")
            print("1. 🎯 Classical shot (row, col)")
            print("2. 🔮 Quantum row search")
            print("3. 🔮 Quantum column search")
            if self.grid_size >= 4:
                print("4. 🔮 Quantum 2x2 area search")
            
            while True:
                try:
                    choice = input("Enter choice (1-4): ").strip()
                    if choice == '1':
                        return self.classical_shot()
                    elif choice == '2':
                        return self.quantum_row_search()
                    elif choice == '3':
                        return self.quantum_column_search()
                    elif choice == '4' and self.grid_size >= 4:
                        return self.quantum_2x2_search()
                    else:
                        print("❗ Invalid choice! Try again.")
                except ValueError:
                    print("❗ Please enter a valid number!")
        else:
            print("(No quantum shots remaining - using classical shot)")
            return self.classical_shot()

    def classical_shot(self):
        """Handle classical shooting"""
        while True:
            try:
                row = int(input(f"Enter row (0-{self.grid_size-1}): "))
                col = int(input(f"Enter col (0-{self.grid_size-1}): "))
                
                if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                    index = self.coords_to_index(row, col)
                    
                    if index in self.player_shots or index in self.player_hits:
                        print("❗ Already shot there! Try again.")
                        continue
                        
                    self.player_shots.add(index)
                    
                    if index in self.ships:
                        print("🎯 HIT! You found a ship!")
                        self.player_hits.add(index)
                        return True
                    else:
                        print("💧 MISS!")
                        return False
                else:
                    print(f"❗ Invalid coordinates! Use 0-{self.grid_size-1}")
            except ValueError:
                print("❗ Please enter valid numbers!")

    def quantum_row_search(self):
        """Use quantum search on a specific row"""
        while True:
            try:
                row = int(input(f"Enter row to quantum search (0-{self.grid_size-1}): "))
                if 0 <= row < self.grid_size:
                    break
                else:
                    print(f"❗ Invalid row! Use 0-{self.grid_size-1}")
            except ValueError:
                print("❗ Please enter a valid number!")
        
        row_indices = self.get_row_indices(row)
        unshot_indices = [idx for idx in row_indices if idx not in self.player_shots and idx not in self.player_hits]
        
        if not unshot_indices:
            print("❗ All cells in this row already shot! Try a different row.")
            return self.quantum_row_search()
        
        print(f"🔮 Quantum searching row {row}...")
        time.sleep(1)
        
        # Check if there are ships in this row
        ships_in_row = [idx for idx in unshot_indices if idx in self.ships]
        
        if ships_in_row:
            # Use Grover's algorithm targeting ships in this row
            counts = run_grover_multi_search(self.n_qubits, ships_in_row, shots=256)
            
            # Filter results to only row indices and find best unshot cell
            valid_results = {k: v for k, v in counts.items() if int(k, 2) in unshot_indices}
            if valid_results:
                best_result = max(valid_results, key=valid_results.get)
                target_index = int(best_result, 2)
                confidence = valid_results[best_result] / sum(counts.values()) * 100
            else:
                target_index = random.choice(unshot_indices)
                confidence = 25.0
        else:
            # No ships in row, but still show quantum "analysis"
            target_index = random.choice(unshot_indices)
            confidence = 15.0
        
        self.player_quantum_used += 1
        print(f"🧮 Quantum analysis complete! Confidence: {confidence:.1f}%")
        
        return self.execute_shot(target_index, "🔮 Quantum row")

    def quantum_column_search(self):
        """Use quantum search on a specific column"""
        while True:
            try:
                col = int(input(f"Enter column to quantum search (0-{self.grid_size-1}): "))
                if 0 <= col < self.grid_size:
                    break
                else:
                    print(f"❗ Invalid column! Use 0-{self.grid_size-1}")
            except ValueError:
                print("❗ Please enter a valid number!")
        
        col_indices = self.get_column_indices(col)
        unshot_indices = [idx for idx in col_indices if idx not in self.player_shots and idx not in self.player_hits]
        
        if not unshot_indices:
            print("❗ All cells in this column already shot! Try a different column.")
            return self.quantum_column_search()
        
        print(f"🔮 Quantum searching column {col}...")
        time.sleep(1)
        
        # Check if there are ships in this column
        ships_in_col = [idx for idx in unshot_indices if idx in self.ships]
        
        if ships_in_col:
            # Use Grover's algorithm targeting ships in this column
            counts = run_grover_multi_search(self.n_qubits, ships_in_col, shots=256)
            
            # Filter results to only column indices and find best unshot cell
            valid_results = {k: v for k, v in counts.items() if int(k, 2) in unshot_indices}
            if valid_results:
                best_result = max(valid_results, key=valid_results.get)
                target_index = int(best_result, 2)
                confidence = valid_results[best_result] / sum(counts.values()) * 100
            else:
                target_index = random.choice(unshot_indices)
                confidence = 25.0
        else:
            # No ships in column, but still show quantum "analysis"
            target_index = random.choice(unshot_indices)
            confidence = 15.0
        
        self.player_quantum_used += 1
        print(f"🧮 Quantum analysis complete! Confidence: {confidence:.1f}%")
        
        return self.execute_shot(target_index, "🔮 Quantum column")

    def quantum_2x2_search(self):
        """Use quantum search on a 2x2 area"""
        while True:
            try:
                start_row = int(input(f"Enter top-left row of 2x2 area (0-{self.grid_size-2}): "))
                start_col = int(input(f"Enter top-left col of 2x2 area (0-{self.grid_size-2}): "))
                
                if 0 <= start_row <= self.grid_size-2 and 0 <= start_col <= self.grid_size-2:
                    break
                else:
                    print(f"❗ Invalid coordinates! Use 0-{self.grid_size-2} to fit 2x2 area.")
            except ValueError:
                print("❗ Please enter valid numbers!")
        
        area_indices = self.get_2x2_area_indices(start_row, start_col)
        unshot_indices = [idx for idx in area_indices if idx not in self.player_shots and idx not in self.player_hits]
        
        if not unshot_indices:
            print("❗ All cells in this 2x2 area already shot! Try a different area.")
            return self.quantum_2x2_search()
        
        print(f"🔮 Quantum searching 2x2 area at ({start_row},{start_col})...")
        time.sleep(1)
        
        # Check if there are ships in this area
        ships_in_area = [idx for idx in unshot_indices if idx in self.ships]
        
        if ships_in_area:
            # Use Grover's algorithm targeting ships in this area
            counts = run_grover_multi_search(self.n_qubits, ships_in_area, shots=256)
            
            # Filter results to only area indices and find best unshot cell
            valid_results = {k: v for k, v in counts.items() if int(k, 2) in unshot_indices}
            if valid_results:
                best_result = max(valid_results, key=valid_results.get)
                target_index = int(best_result, 2)
                confidence = valid_results[best_result] / sum(counts.values()) * 100
            else:
                target_index = random.choice(unshot_indices)
                confidence = 25.0
        else:
            # No ships in area, but still show quantum "analysis"
            target_index = random.choice(unshot_indices)
            confidence = 15.0
        
        self.player_quantum_used += 1
        print(f"🧮 Quantum analysis complete! Confidence: {confidence:.1f}%")
        
        return self.execute_shot(target_index, "🔮 Quantum 2x2")

    def execute_shot(self, index, shot_type):
        """Execute a shot and return hit/miss"""
        self.player_shots.add(index)
        row, col = self.index_to_coords(index)
        
        if index in self.ships:
            print(f"🎯 {shot_type} HIT at ({row},{col})! You found a ship!")
            self.player_hits.add(index)
            return True
        else:
            print(f"💧 {shot_type} MISS at ({row},{col})")
            return False

    def quantum_ai_turn(self):
        """Handle quantum AI's turn"""
        remaining_ships = self.ships - self.ai_hits
        
        if not remaining_ships:
            return False
            
        print(f"\n🤖 QUANTUM AI'S TURN (Quantum shots left: {self.max_quantum_shots - self.quantum_shots_used})")
        
        # AI decides on strategy
        if self.quantum_shots_used < self.max_quantum_shots:
            # AI picks the best quantum strategy
            strategy = self.ai_choose_quantum_strategy()
            if strategy:
                return strategy
        
        return self.random_search()

    def ai_choose_quantum_strategy(self):
        """AI intelligently chooses the best quantum strategy"""
        remaining_ships = self.ships - self.ai_hits
        available_shots = set(range(self.total_cells)) - self.ai_shots - self.ai_hits
        
        if not remaining_ships or not available_shots:
            return None
        
        # Analyze ship density in rows, columns, and 2x2 areas
        best_strategy = None
        best_score = 0
        
        # Check rows
        for row in range(self.grid_size):
            row_indices = self.get_row_indices(row)
            available_in_row = [idx for idx in row_indices if idx in available_shots]
            ships_in_row = [idx for idx in available_in_row if idx in remaining_ships]
            
            if ships_in_row and len(available_in_row) > 0:
                score = len(ships_in_row) / len(available_in_row)
                if score > best_score:
                    best_score = score
                    best_strategy = ('row', row, ships_in_row, available_in_row)
        
        # Check columns
        for col in range(self.grid_size):
            col_indices = self.get_column_indices(col)
            available_in_col = [idx for idx in col_indices if idx in available_shots]
            ships_in_col = [idx for idx in available_in_col if idx in remaining_ships]
            
            if ships_in_col and len(available_in_col) > 0:
                score = len(ships_in_col) / len(available_in_col)
                if score > best_score:
                    best_score = score
                    best_strategy = ('col', col, ships_in_col, available_in_col)
        
        # Check 2x2 areas
        if self.grid_size >= 4:
            for start_row in range(self.grid_size - 1):
                for start_col in range(self.grid_size - 1):
                    area_indices = self.get_2x2_area_indices(start_row, start_col)
                    available_in_area = [idx for idx in area_indices if idx in available_shots]
                    ships_in_area = [idx for idx in available_in_area if idx in remaining_ships]
                    
                    if ships_in_area and len(available_in_area) > 0:
                        score = len(ships_in_area) / len(available_in_area)
                        if score > best_score:
                            best_score = score
                            best_strategy = ('2x2', (start_row, start_col), ships_in_area, available_in_area)
        
        # Execute best strategy if found
        if best_strategy and best_score > 0.3:  # Only use quantum if decent chance
            return self.ai_execute_quantum_strategy(best_strategy)
        
        # Fall back to single-target quantum search
        return self.quantum_search()

    def ai_execute_quantum_strategy(self, strategy):
        """Execute AI's chosen quantum strategy"""
        strategy_type, target, ships_in_target, available_in_target = strategy
        
        if strategy_type == 'row':
            print(f"🤖 AI using quantum row search on row {target}")
        elif strategy_type == 'col':
            print(f"🤖 AI using quantum column search on column {target}")
        elif strategy_type == '2x2':
            print(f"🤖 AI using quantum 2x2 search at area {target}")
        
        time.sleep(1)
        
        # Use Grover's algorithm on the target area
        if ships_in_target:
            counts = run_grover_multi_search(self.n_qubits, ships_in_target, shots=256)
            
            # Filter to available shots in target area
            valid_results = {k: v for k, v in counts.items() if int(k, 2) in available_in_target}
            if valid_results:
                best_result = max(valid_results, key=valid_results.get)
                guess_index = int(best_result, 2)
                confidence = valid_results[best_result] / sum(counts.values()) * 100
            else:
                guess_index = random.choice(available_in_target)
                confidence = 25.0
        else:
            guess_index = random.choice(available_in_target)
            confidence = 15.0
        
        print(f"🧮 Quantum analysis complete! Confidence: {confidence:.1f}%")
        
        self.quantum_shots_used += 1
        return self.ai_shoot(guess_index, is_quantum=True)

    def quantum_search(self):
        """Use Grover's algorithm to find a ship"""
        remaining_ships = list(self.ships - self.ai_hits)
        
        if not remaining_ships:
            return False
            
        # Pick a random ship to search for (simulating unknown target)
        target_ship = random.choice(remaining_ships)
        
        print("🔮 Initiating quantum search...")
        time.sleep(1)  # Dramatic pause
        
        # Run Grover's algorithm
        counts = run_grover_search(self.n_qubits, target_ship, shots=256)
        
        # Get the most likely result
        quantum_result = max(counts, key=counts.get)
        guess_index = int(quantum_result, 2)
        
        # Show quantum "probability analysis"
        success_rate = counts.get(quantum_result, 0) / sum(counts.values()) * 100
        print(f"🧮 Quantum analysis complete! Confidence: {success_rate:.1f}%")
        
        self.quantum_shots_used += 1
        
        return self.ai_shoot(guess_index, is_quantum=True)

    def random_search(self):
        """AI makes a random shot"""
        available_shots = set(range(self.total_cells)) - self.ai_shots - self.ai_hits
        
        if not available_shots:
            return False
            
        guess_index = random.choice(list(available_shots))
        print("🎲 AI making random shot...")
        time.sleep(0.5)
        
        return self.ai_shoot(guess_index, is_quantum=False)

    def ai_shoot(self, index, is_quantum=False):
        """Execute AI shot at given index"""
        if index in self.ai_shots or index in self.ai_hits:
            # If already shot here, pick a random available spot
            available = set(range(self.total_cells)) - self.ai_shots - self.ai_hits
            if available:
                index = random.choice(list(available))
            else:
                return False
        
        self.ai_shots.add(index)
        row, col = self.index_to_coords(index)
        shot_type = "🔮 Quantum" if is_quantum else "🎲 Random"
        
        if index in self.ships:
            print(f"🤖 {shot_type} HIT at ({row},{col})! AI found a ship!")
            self.ai_hits.add(index)
            return True
        else:
            print(f"🤖 {shot_type} MISS at ({row},{col})")
            return False

    def check_game_over(self):
        """Check if game is over and return winner"""
        if len(self.player_hits) == len(self.ships):
            return "player"
        elif len(self.ai_hits) == len(self.ships):
            return "ai"
        return None

    def show_game_stats(self):
        """Show final game statistics"""
        print("\n📈 GAME STATISTICS:")
        print("Player - Shots: {}, Hits: {}, Quantum shots used: {}/{}".format(
            len(self.player_shots), len(self.player_hits), 
            self.player_quantum_used, self.player_quantum_shots))
        print("AI - Shots: {}, Hits: {}, Quantum shots used: {}/{}".format(
            len(self.ai_shots), len(self.ai_hits), 
            self.quantum_shots_used, self.max_quantum_shots))
        
        if len(self.player_shots) > 0:
            player_accuracy = len(self.player_hits) / len(self.player_shots) * 100
            print(f"Player Accuracy: {player_accuracy:.1f}%")
        
        if len(self.ai_shots) > 0:
            ai_accuracy = len(self.ai_hits) / len(self.ai_shots) * 100
            print(f"AI Accuracy: {ai_accuracy:.1f}%")

    def play(self):
        """Main game loop"""
        print("🎯 Use classical shots or quantum searches to find all ships before the AI!")
        print("🔮 Quantum searches: Row, Column, or 2x2 area searches using Grover's algorithm")
        print("Legend: 🎯=Your hits, 🤖=AI hits, 💧=Your misses, ❌=AI misses, ⬜=Unknown")
        
        while True:
            self.display_grid()
            
            # Player turn
            self.player_turn()
            
            winner = self.check_game_over()
            if winner:
                break
                
            # AI turn
            self.quantum_ai_turn()
            
            winner = self.check_game_over()
            if winner:
                break
        
        # Game over
        self.display_grid()
        
        if winner == "player":
            print("\n🏆 CONGRATULATIONS! You won!")
            print("You found all ships before the Quantum AI!")
        else:
            print("\n🤖 QUANTUM AI WINS!")
            print("The AI found all ships first using quantum algorithms!")
        
        self.show_game_stats()
        
        # Reveal ship locations
        print(f"\n🗺️  Ship locations were: {sorted(list(self.ships))}")
        for ship in self.ships:
            row, col = self.index_to_coords(ship)
            print(f"   Ship at ({row},{col}) = index {ship}")
def main():
    """Main function to start the game"""
    print("🌟 Welcome to Quantum Battleship! 🌟")
    print("A game where you compete against a Quantum AI using Grover's algorithm!")
    print()
    
    while True:
        try:
            choice = input("Choose grid size - (1) 4x4 Easy, (2) 4x4 Hard, (3) 8x8 Expert, (q) Quit: ").lower()
            
            if choice == 'q':
                print("Thanks for playing! 👋")
                break
            elif choice == '1':
                game = QuantumBattleship(grid_size=4)
                game.max_quantum_shots = 5  # More quantum shots for easy mode
                game.player_quantum_shots = 3
            elif choice == '2':
                game = QuantumBattleship(grid_size=4)
                game.max_quantum_shots = 2  # Fewer quantum shots for hard mode
                game.player_quantum_shots = 2
            elif choice == '3':
                print("⚠️  8x8 grid requires 6 qubits - this is computationally intensive!")
                confirm = input("Continue? (y/n): ").lower()
                if confirm == 'y':
                    game = QuantumBattleship(grid_size=8)
                    game.max_quantum_shots = 3
                    game.player_quantum_shots = 2
                else:
                    continue
            else:
                print("Invalid choice! Please try again.")
                continue
                
            game.play()
            
            if input("\nPlay again? (y/n): ").lower() != 'y':
                break
                
        except KeyboardInterrupt:
            print("\n\nGame interrupted. Thanks for playing! 👋")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Returning to main menu...")


if __name__ == "__main__":
    main()