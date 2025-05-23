import csv
from typing import List, Dict, Tuple
from sudoku_cp_backtracking import SudokuSolver
import time

def count_clues(puzzle: List[List[int]]) -> int:
    """Count the number of initial clues in a puzzle."""
    return sum(1 for row in puzzle for cell in row if cell != 0)

def categorize_by_clues(puzzle: List[List[int]]) -> str:
    """Categorize puzzle based on number of clues."""
    num_clues = count_clues(puzzle)
    if 17 <= num_clues <= 25:
        return "17-25"
    elif 26 <= num_clues <= 35:
        return "26-35"
    else:
        return ">35"

def convert_grid(puzzle):
    """Convert string puzzle to list of lists of integers."""
    return [[int(cell) for cell in row] for row in puzzle]

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

def analyze_clues_and_performance():
    # Initialize solver
    solver = SudokuSolver()
    
    # Initialize results structure for each clue category
    results = {
        "17-25": {"count": 0, "total_time": 0, "total_backtracks": 0},
        "26-35": {"count": 0, "total_time": 0, "total_backtracks": 0},
        ">35": {"count": 0, "total_time": 0, "total_backtracks": 0}
    }
    
    # Read puzzles from all difficulty levels
    puzzle_files = [
        "classified_puzzles/easy_puzzles.txt",
        "classified_puzzles/extreme_puzzles.txt"
    ]
    
    for file_path in puzzle_files:
        puzzles = read_puzzles(file_path)
        
        for puzzle in puzzles:
            grid = convert_grid(puzzle)
            category = categorize_by_clues(grid)
            
            # Solve with CP+BT
            solver.backtracks = 0
            start_time = time.time()
            solver.solve(grid)
            solve_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Update results for this category
            results[category]["count"] += 1
            results[category]["total_time"] += solve_time
            results[category]["total_backtracks"] += solver.backtracks

    # Calculate averages and write results
    output_file = "clues_analysis.csv"
    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Số lượng manh mối", "Số lượng câu đố", "Thời gian CP+BT (ms)", "Số lần cần Backtracking"])
        
        for category in ["17-25", "26-35", ">35"]:
            count = results[category]["count"]
            if count > 0:
                avg_time = results[category]["total_time"] / count
                avg_backtracks = results[category]["total_backtracks"] / count
                writer.writerow([category, count, f"{avg_time:.2f}", f"{avg_backtracks:.1f}"])
            else:
                writer.writerow([category, 0, "N/A", "N/A"])

    print(f"Analysis saved to {output_file}")

if __name__ == "__main__":
    analyze_clues_and_performance()
