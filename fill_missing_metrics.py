import time
import csv
from sudoku_backtracking import SudokuBacktracking
from sudoku_cp_backtracking import SudokuSolver 

# Solver instances
backtracking_solver = SudokuBacktracking()
cp_bt_solver = SudokuSolver()  # Used for both CP and CP+BT

def convert_grid(puzzle):
    """Convert string puzzle to list of lists of integers."""
    return [[int(cell) for cell in row] for row in puzzle]

# File paths for categorized puzzles
PUZZLE_FILES = {
    "Dễ": "classified_puzzles/easy_puzzles.txt",
    "Trung bình": "classified_puzzles/medium_puzzles.txt",
    "Khó": "classified_puzzles/hard_puzzles.txt",
    "Siêu khó": "classified_puzzles/extreme_puzzles.txt",
}

# Output CSV file
OUTPUT_FILE = "benchmark_results_missing_metrics.csv"

def read_puzzles(file_path):
    """Read puzzles from a file."""
    puzzles = []
    with open(file_path, "r") as f:
        puzzle = []
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if len(line) == 9:
                puzzle.append(line)
                if len(puzzle) == 9:
                    puzzles.append(puzzle)
                    puzzle = []
    return puzzles

def benchmark_solver(solver, puzzles):
    """Benchmark a solver on a list of puzzles."""
    total_time = 0
    for puzzle in puzzles:
        grid = convert_grid(puzzle)
        start_time = time.time()
        solver.solve(grid)
        total_time += (time.time() - start_time)
    return total_time / len(puzzles) if puzzles else 0

def calculate_improvement(bt_time, cp_time, cp_bt_time):
    """Calculate percentage improvement."""
    if bt_time == 0:
        return 0
    return ((bt_time - cp_bt_time) / bt_time) * 100

def main():
    results = []    
    for difficulty, file_path in PUZZLE_FILES.items():
        puzzles = read_puzzles(file_path)
        
        # Measure times for each algorithm
        bt_time = benchmark_solver(backtracking_solver, puzzles) * 1000  # Convert to ms
        # Use the same solver with different flag for CP vs CP+BT
        cp_bt_solver.use_backtracking = False
        cp_time = benchmark_solver(cp_bt_solver, puzzles) * 1000  # Convert to ms
        cp_bt_solver.use_backtracking = True
        cp_bt_time = benchmark_solver(cp_bt_solver, puzzles) * 1000  # Convert to ms

        improvement = calculate_improvement(bt_time, cp_time, cp_bt_time)

        results.append([difficulty, bt_time, cp_time, cp_bt_time, improvement])

    # Write results to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Độ khó", "Backtracking (ms)", "CP (ms)", "CP+BT (ms)", "% Cải thiện"])
        writer.writerows(results)

if __name__ == "__main__":
    main()
