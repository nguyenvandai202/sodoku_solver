#!/usr/bin/env python
"""Compare performance between constraint propagation and simple backtracking algorithms"""

import subprocess
import time

def main():
    print("Comparing Sudoku solving algorithms...\n")
    
    # Run constraint propagation algorithm
    print("Running Constraint Propagation with DFS algorithm...")
    start = time.time()
    subprocess.run(["python", "sudoku.py", "-i", "p096_sudoku.txt", "-o", "solutions/sudoku_constraint_solutions.txt"])
    constraint_time = time.time() - start
    
    print("\n" + "="*50 + "\n")
    
    # Run simple backtracking algorithm
    print("Running Simple Backtracking algorithm...")
    start = time.time()
    subprocess.run(["python", "sudoku_backtracking.py"])
    backtracking_time = time.time() - start
    
    print("\nOverall Execution Time Comparison:")
    print(f"Constraint Propagation: {constraint_time:.4f} seconds")
    print(f"Simple Backtracking: {backtracking_time:.4f} seconds")
    print(f"Difference: {abs(constraint_time - backtracking_time):.4f} seconds")
    print(f"Speedup: {backtracking_time/constraint_time:.2f}x")

if __name__ == "__main__":
    main()
