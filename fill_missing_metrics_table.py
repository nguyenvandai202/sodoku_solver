import csv
import os
from sudoku_benchmark import SudokuBenchmark
from typing import List

def convert_str_to_grid(puzzle: List[str]) -> List[List[int]]:
    """Convert string puzzle to grid format."""
    return [[int(cell) for cell in row] for row in puzzle]

def benchmark_algorithms(file_path: str):
    """Run benchmarks for all algorithms on puzzles in the file."""
    benchmark = SudokuBenchmark()
    
    # Read and parse puzzles
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
                    puzzles.append(convert_str_to_grid(puzzle))
                    puzzle = []
    
    if not puzzles:
        return 0, 0, 0
    
    # Run benchmarks
    total_bt = 0
    total_cp = 0
    total_cp_bt = 0
    
    for grid in puzzles:
        # Backtracking
        solved, metrics = benchmark.solve_with_backtracking(grid)
        total_bt += metrics.execution_time
        
        # CP without backtracking
        benchmark.optimized_solver.use_backtracking = False
        solved, metrics = benchmark.solve_with_optimized(grid)
        total_cp += metrics.execution_time
        
        # CP with backtracking
        benchmark.optimized_solver.use_backtracking = True
        solved, metrics = benchmark.solve_with_optimized(grid)
        total_cp_bt += metrics.execution_time
    
    n = len(puzzles)
    return total_bt/n, total_cp/n, total_cp_bt/n

def fill_missing_metrics():
    # Define the difficulty levels
    difficulties = ["Dễ", "Trung bình", "Khó", "Siêu khó"]

    # Define the file paths for categorized puzzles
    puzzle_files = {
        "Dễ": "classified_puzzles/easy_puzzles.txt",
        "Trung bình": "classified_puzzles/medium_puzzles.txt",
        "Khó": "classified_puzzles/hard_puzzles.txt",
        "Siêu khó": "classified_puzzles/extreme_puzzles.txt",
    }

    # Initialize the results table
    results = []

    for difficulty in difficulties:
        file_path = puzzle_files[difficulty]

        if not os.path.exists(file_path):
            print(f"Puzzle file for {difficulty} not found: {file_path}")
            continue

        # Benchmark the algorithms for the current difficulty level
        backtracking_time, cp_time, cp_bt_time = benchmark_algorithms(file_path)

        # Calculate percentage improvement
        if backtracking_time > 0:
            improvement = ((backtracking_time - cp_bt_time) / backtracking_time) * 100
        else:
            improvement = 0

        # Append the results
        results.append({
            "Độ khó": difficulty,
            "Backtracking (ms)": backtracking_time,
            "CP (ms)": cp_time,
            "CP+BT (ms)": cp_bt_time,
            "% Cải thiện": improvement,
        })

    # Write the results to a CSV file
    output_file = "benchmark_results_tables.csv"
    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Độ khó", "Backtracking (ms)", "CP (ms)", "CP+BT (ms)", "% Cải thiện"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print(f"Benchmark results saved to {output_file}")

if __name__ == "__main__":
    fill_missing_metrics()
