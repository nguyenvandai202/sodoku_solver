#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sudoku solver using optimized constraint propagation and depth-first search"""

import argparse
import csv
import time
import psutil
import os
from typing import List, Dict, Any, Set, Tuple

class SudokuSolver:
    def __init__(self):
        self.ALLOWED_NUMBERS = '123456789'
        self.ROWS = 'ABCDEFGHI'
        self.COLS = self.ALLOWED_NUMBERS
        
        # Generate core data structures once
        self.squares = self._generate_squares()
        self.units = self._generate_units()
        self.peers = self._generate_peers()
        
        # Metrics
        self.assignments = 0
        self.backtracks = 0
        
    def _generate_squares(self) -> List[str]:
        return [r + c for r in self.ROWS for c in self.COLS]
        
    def _generate_units(self) -> Dict[str, List[List[str]]]:
        # Generate unit patterns
        row_units = [[r + c for c in self.COLS] for r in self.ROWS]
        col_units = [[r + c for r in self.ROWS] for c in self.COLS]
        box_units = [[r + c for r in rs for c in cs]
                    for rs in ('ABC','DEF','GHI')
                    for cs in ('123','456','789')]
        
        unit_list = row_units + col_units + box_units
        return {s: [u for u in unit_list if s in u] for s in self.squares}
        
    def _generate_peers(self) -> Dict[str, Set[str]]:
        return {s: set(sum(self.units[s], [])) - {s} for s in self.squares}
        
    def generate_board(self) -> Dict[str, Any]:
        return {s: self.ALLOWED_NUMBERS for s in self.squares}
        
    def assign_value(self, board: Dict[str, Any], square: str, value: str) -> Dict[str, Any]:
        """Assign a value to a square and propagate constraints."""
        self.assignments += 1
        other_values = board[square].replace(value, '')
        return all(self.remove_value(board, square, val) for val in other_values) and board

    def remove_value(self, board: Dict[str, Any], square: str, value: str) -> bool:
        """Remove a value from a square and propagate constraints."""
        if value not in board[square]:
            return True
            
        board[square] = board[square].replace(value, '')
        
        # If no values left, contradiction found
        if len(board[square]) == 0:
            self.backtracks += 1
            return False
            
        # If only one value left, propagate to peers
        if len(board[square]) == 1:
            final_value = board[square]
            if not all(self.remove_value(board, peer, final_value) 
                      for peer in self.peers[square]):
                return False
                
        # Look for single possibilities in units
        for unit in self.units[square]:
            places = [s for s in unit if value in board[s]]
            if not places:
                self.backtracks += 1
                return False
            if len(places) == 1 and len(board[places[0]]) > 1:
                if not self.assign_value(board, places[0], value):
                    return False
        return True

    def propagate_constraints(self, puzzle: Dict[str, Any], board: Dict[str, Any]) -> Dict[str, Any]:
        """Initial constraint propagation for the puzzle."""
        for square, value in puzzle.items():
            if value in self.ALLOWED_NUMBERS and not self.assign_value(board, square, value):
                return False
        return board
        
    def solve(self, grid: List[List[int]]) -> List[List[int]]:
        """Solve the Sudoku puzzle using constraint propagation and search."""
        self.assignments = 0
        self.backtracks = 0
        
        # Convert grid to puzzle format
        puzzle = {}
        for i, row in enumerate(grid):
            for j, val in enumerate(row):
                square = self.ROWS[i] + self.COLS[j]
                puzzle[square] = str(val) if val != 0 else '0'
                
        # Initialize and solve
        board = self.generate_board()
        board = self.propagate_constraints(puzzle, board)
        solution = self._search(board)
        
        # Convert solution back to grid format
        if solution:
            return [[int(solution[self.ROWS[i] + self.COLS[j]]) 
                    for j in range(9)] for i in range(9)]
        return None

    def _search(self, board: Dict[str, Any]) -> Dict[str, Any]:
        """Use depth-first search and propagation to try all possible values."""
        if board is False:
            return False
        if all(len(board[s]) == 1 for s in self.squares):
            return board
            
        # Choose square with fewest possibilities
        n, square = min((len(board[s]), s) for s in self.squares if len(board[s]) > 1)
        
        # Try each value
        for value in board[square]:
            new_board = {k: v for k, v in board.items()}
            if self.assign_value(new_board, square, value):
                result = self._search(new_board)
                if result:
                    return result
        return False

    def solve_with_cp_and_backtracking(self, grid: List[str]) -> List[List[int]]:
        """Solve the Sudoku puzzle using CP and Backtracking."""
        self.assignments = 0
        self.backtracks = 0

        # Convert grid to puzzle format
        puzzle = {}
        for i, row in enumerate(grid):
            for j, val in enumerate(row):
                square = self.ROWS[i] + self.COLS[j]
                puzzle[square] = val if val != '0' else '0'

        # Initialize and solve
        board = self.generate_board()
        board = self.propagate_constraints(puzzle, board)
        if not board:
            return None  # CP failed

        # Use Backtracking if CP alone cannot solve
        solution = self._search(board)

        # Convert solution back to grid format
        if solution:
            return [[int(solution[self.ROWS[i] + self.COLS[j]])
                     for j in range(9)] for i in range(9)]
        return None

def load_puzzles(filename: str) -> List[Dict[str, str]]:
    """Load multiple puzzles from a text file."""
    puzzles = []
    current_grid = []
    
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if line.startswith('Grid'):
                if current_grid:
                    solver = SudokuSolver()
                    puzzles.append(dict(zip(solver.squares, ''.join(current_grid))))
                current_grid = []
            else:
                current_grid.append(line)
        if current_grid:
            solver = SudokuSolver()
            puzzles.append(dict(zip(solver.squares, ''.join(current_grid))))
    
    return puzzles

def save_solutions(solutions: List[Dict[str, str]], filename: str, 
                  times: List[float], memories: List[float]):
    """Save solutions with performance metrics."""
    with open(filename, 'w') as file:
        total_time = sum(times)
        avg_time = total_time / len(times)
        avg_memory = sum(memories) / len(memories)
        
        file.write(f"Performance Metrics:\n")
        file.write(f"Total Time: {total_time:.4f} seconds\n")
        file.write(f"Average Time per puzzle: {avg_time:.4f} seconds\n")
        file.write(f"Average Memory per puzzle: {avg_memory:.2f} MB\n\n")
        
        solver = SudokuSolver()
        for i, solution in enumerate(solutions, 1):
            file.write(f"Grid {i:02d}\n")
            file.write(f"Time: {times[i-1]:.4f} seconds\n")
            file.write(f"Memory: {memories[i-1]:.2f} MB\n")
            
            # Convert to grid format
            for r in solver.ROWS:
                row = [solution[r + c] for c in solver.COLS]
                file.write(''.join(row) + '\n')
            file.write('\n')

def main():
    parser = argparse.ArgumentParser(description='Optimized Sudoku Solver')
    parser.add_argument("-i", "--input", required=True, help="input file (.txt)")
    parser.add_argument("-o", "--output", required=True, help="output file (.txt)")
    args = parser.parse_args()

    # Load puzzles
    puzzles = load_puzzles(args.input)
    solver = SudokuSolver()
    solutions = []

    # Solve each puzzle using CP + Backtracking
    for i, puzzle in enumerate(puzzles, 1):
        print(f"Solving Grid {i}...")
        try:
            grid = [puzzle.get(s, '0') for s in solver.squares]  # Sử dụng get để tránh KeyError
            formatted_grid = [grid[i:i+9] for i in range(0, len(grid), 9)]
            solution = solver.solve_with_cp_and_backtracking(formatted_grid)

            if solution:
                solutions.append(solution)
                print(f"Solved Grid {i}")
            else:
                print(f"Failed to solve Grid {i}")
        except Exception as e:
            print(f"Error solving Grid {i}: {e}")

    # Save results
    total_puzzles = len(puzzles)  # Đếm chính xác số lượng bài toán
    if solutions:
        with open(args.output, 'w') as file:
            for i, solution in enumerate(solutions, 1):
                file.write(f"Grid {i:02d}\n")
                for row in solution:
                    file.write(''.join(map(str, row)) + '\n')
                file.write('\n')
        print(f"Successfully solved {len(solutions)} out of {total_puzzles} puzzles")

if __name__ == "__main__":
    main()
