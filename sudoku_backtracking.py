#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sudoku solver using simple backtracking algorithm"""

import time
import psutil
import os
from typing import List, Optional, Tuple

class SudokuBacktracking:
    def __init__(self):
        self.grid_size = 9
        self.box_size = 3
        self.assignments = 0
        self.backtracks = 0

    def is_valid(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        # Check row
        for x in range(self.grid_size):
            if grid[row][x] == num:
                return False
                
        # Check column
        for y in range(self.grid_size):
            if grid[y][col] == num:
                return False
        
        # Check box
        start_row = row - row % self.box_size
        start_col = col - col % self.box_size
        for i in range(self.box_size):
            for j in range(self.box_size):
                if grid[i + start_row][j + start_col] == num:
                    return False
        return True
    
    def find_empty_location(self, grid: List[List[int]]) -> Optional[Tuple[int, int]]:
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if grid[i][j] == 0:
                    return (i, j)
        return None
    
    def solve(self, grid: List[List[int]]) -> bool:
        empty = self.find_empty_location(grid)
        if not empty:
            return True
        
        row, col = empty
        
        for num in range(1, 10):
            if self.is_valid(grid, row, col, num):
                grid[row][col] = num
                self.assignments += 1  # Đếm phép gán
                
                if self.solve(grid):
                    return True
                    
                grid[row][col] = 0
                self.backtracks += 1  # Đếm backtrack
                
        return False

def load_puzzles(filename: str) -> List[List[List[int]]]:
    """Load multiple puzzles from a text file"""
    puzzles = []
    current_puzzle = []
    
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if line.startswith('Grid'):
                if current_puzzle:
                    puzzles.append(current_puzzle)
                current_puzzle = []
            else:
                current_puzzle.append([int(num) for num in line])
        if current_puzzle:
            puzzles.append(current_puzzle)
    
    return puzzles

def save_solutions(solutions: List[List[List[int]]], filename: str, times: List[float], memories: List[float]):
    """Save solutions with performance metrics"""
    with open(filename, 'w') as file:
        total_time = sum(times)
        avg_time = total_time / len(times)
        avg_memory = sum(memories) / len(memories)
        
        file.write(f"Performance Metrics:\n")
        file.write(f"Total Time: {total_time:.4f} seconds\n")
        file.write(f"Average Time per puzzle: {avg_time:.4f} seconds\n")
        file.write(f"Average Memory per puzzle: {avg_memory:.2f} MB\n\n")
        
        for i, solution in enumerate(solutions, 1):
            file.write(f"Grid {i:02d}\n")
            file.write(f"Time: {times[i-1]:.4f} seconds\n")
            file.write(f"Memory: {memories[i-1]:.2f} MB\n")
            for row in solution:
                file.write(''.join(map(str, row)) + '\n')
            file.write('\n')

def main():
    input_file = "p096_sudoku.txt"
    output_file = "solutions/sudoku_backtracking_solutions.txt"
    
    # Load all puzzles
    puzzles = load_puzzles(input_file)
    solver = SudokuBacktracking()
    solutions = []
    solve_times = []
    memory_usages = []
    
    for i, puzzle in enumerate(puzzles, 1):
        # Create a copy of the puzzle to solve
        grid = [row[:] for row in puzzle]
        
        # Measure time and memory
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
        start_time = time.time()
        
        # Solve puzzle
        if solver.solve(grid):
            solutions.append(grid)
            solve_time = time.time() - start_time
            end_memory = process.memory_info().rss / 1024 / 1024
            memory_used = end_memory - start_memory
            
            solve_times.append(solve_time)
            memory_usages.append(memory_used)
            print(f"Solved Grid {i} in {solve_time:.4f} seconds using {memory_used:.2f} MB")
        else:
            print(f"Failed to solve Grid {i}")
    
    # Save solutions with performance metrics
    save_solutions(solutions, output_file, solve_times, memory_usages)
    print(f"\nSolved {len(solutions)} out of {len(puzzles)} puzzles")
    print(f"Total time: {sum(solve_times):.4f} seconds")
    print(f"Average time per puzzle: {sum(solve_times)/len(solve_times):.4f} seconds")
    print(f"Average memory per puzzle: {sum(memory_usages)/len(memory_usages):.2f} MB")

if __name__ == "__main__":
    main()
