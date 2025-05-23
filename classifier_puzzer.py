#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phân loại độ khó Sudoku theo tiêu chí Lewis (2007)
"""

import time
import os
from typing import Dict, List, Tuple, Any

class SudokuClassifier:
    def __init__(self):
        self.ALLOWED_NUMBERS = '123456789'
        self.ROWS = 'ABCDEFGHI'
        self.COLS = self.ALLOWED_NUMBERS
        
        # Generate core data structures
        self.squares = self._generate_squares()
        self.units = self._generate_units()
        self.peers = self._generate_peers()
        
        # Metrics for classification
        self.reset_metrics()
        
    def reset_metrics(self):
        """Reset metrics for new puzzle"""
        self.cp_assignments = 0
        self.backtrack_count = 0
        self.total_assignments = 0
        self.cells_solved_by_cp = 0
        self.total_empty_cells = 0
        
    def _generate_squares(self) -> List[str]:
        return [r + c for r in self.ROWS for c in self.COLS]
        
    def _generate_units(self) -> Dict[str, List[List[str]]]:
        row_units = [[r + c for c in self.COLS] for r in self.ROWS]
        col_units = [[r + c for r in self.ROWS] for c in self.COLS]
        box_units = [[r + c for r in rs for c in cs]
                    for rs in ('ABC','DEF','GHI')
                    for cs in ('123','456','789')]
        
        unit_list = row_units + col_units + box_units
        return {s: [u for u in unit_list if s in u] for s in self.squares}
        
    def _generate_peers(self) -> Dict[str, set]:
        return {s: set(sum(self.units[s], [])) - {s} for s in self.squares}
        
    def generate_board(self) -> Dict[str, str]:
        return {s: self.ALLOWED_NUMBERS for s in self.squares}
        
    def assign_value(self, board: Dict[str, str], square: str, value: str) -> bool:
        """Assign a value and propagate constraints"""
        self.total_assignments += 1
        other_values = board[square].replace(value, '')
        return all(self.remove_value(board, square, val) for val in other_values)

    def remove_value(self, board: Dict[str, str], square: str, value: str) -> bool:
        """Remove a value and propagate constraints"""
        if value not in board[square]:
            return True
            
        board[square] = board[square].replace(value, '')
        
        if len(board[square]) == 0:
            return False
            
        # Naked Singles
        if len(board[square]) == 1:
            final_value = board[square]
            if not all(self.remove_value(board, peer, final_value) 
                      for peer in self.peers[square]):
                return False
                
        # Hidden Singles
        for unit in self.units[square]:
            places = [s for s in unit if value in board[s]]
            if not places:
                return False
            if len(places) == 1:
                if not self.assign_value(board, places[0], value):
                    return False
        return True

    def propagate_constraints(self, puzzle: Dict[str, str], board: Dict[str, str]) -> Dict[str, str]:
        """Initial constraint propagation"""
        initial_empty = sum(1 for v in puzzle.values() if v == '0')
        self.total_empty_cells = initial_empty
        
        for square, value in puzzle.items():
            if value in self.ALLOWED_NUMBERS:
                self.cp_assignments += 1
                if not self.assign_value(board, square, value):
                    return False
                    
        # Count cells solved by CP only
        cells_after_cp = sum(1 for s in self.squares if len(board[s]) == 1)
        initial_filled = 81 - initial_empty
        self.cells_solved_by_cp = cells_after_cp - initial_filled
        
        return board
        
    def solve_with_search(self, board: Dict[str, str]) -> Dict[str, str]:
        """Depth-first search with backtracking"""
        if board is False:
            return False
        if all(len(board[s]) == 1 for s in self.squares):
            return board
            
        # Choose square with fewest possibilities (MRV)
        n, square = min((len(board[s]), s) for s in self.squares if len(board[s]) > 1)
        
        for value in board[square]:
            # Count backtracking attempts
            self.backtrack_count += 1
            
            # Make a copy and try
            new_board = {k: v for k, v in board.items()}
            if self.assign_value(new_board, square, value):
                result = self.solve_with_search(new_board)
                if result:
                    return result
        
        return False
        
    def solve_puzzle(self, puzzle_dict: Dict[str, str]) -> Tuple[bool, Dict[str, Any]]:
        """Solve puzzle and return success status and metrics"""
        self.reset_metrics()
        
        start_time = time.time()
        
        # Initial constraint propagation
        board = self.generate_board()
        board = self.propagate_constraints(puzzle_dict, board)
        
        if board is False:
            return False, {}
            
        # Check if solved by CP alone
        if all(len(board[s]) == 1 for s in self.squares):
            solve_time = time.time() - start_time
            cp_percentage = (self.cells_solved_by_cp / self.total_empty_cells * 100) if self.total_empty_cells > 0 else 100
            
            return True, {
                'time': solve_time,
                'backtrack_count': 0,
                'cp_percentage': cp_percentage,
                'total_assignments': self.total_assignments,
                'solved_by_cp_only': True
            }
        
        # Need backtracking
        solution = self.solve_with_search(board)
        solve_time = time.time() - start_time
        
        if solution:
            cp_percentage = (self.cells_solved_by_cp / self.total_empty_cells * 100) if self.total_empty_cells > 0 else 0
            
            return True, {
                'time': solve_time,
                'backtrack_count': self.backtrack_count,
                'cp_percentage': cp_percentage,
                'total_assignments': self.total_assignments,
                'solved_by_cp_only': False
            }
        
        return False, {}
        
    def classify_difficulty_lewis(self, metrics: Dict[str, Any]) -> str:
        """Classify difficulty according to Lewis (2007) criteria"""
        backtrack_count = metrics.get('backtrack_count', 0)
        cp_percentage = metrics.get('cp_percentage', 0)
        
        if backtrack_count == 0 and cp_percentage > 95:
            return "Easy"
        elif backtrack_count <= 3 and cp_percentage > 85:
            return "Medium"  
        elif backtrack_count <= 15 and cp_percentage > 70:
            return "Hard"
        else:
            return "Extreme"

def load_puzzles_from_file(filename: str) -> List[Tuple[str, Dict[str, str]]]:
    """Load puzzles from text file"""
    puzzles = []
    current_grid = []
    grid_name = ""
    
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if line.startswith('Grid'):
                if current_grid and grid_name:
                    solver = SudokuClassifier()
                    puzzle_dict = dict(zip(solver.squares, ''.join(current_grid)))
                    puzzles.append((grid_name, puzzle_dict))
                
                grid_name = line
                current_grid = []
            else:
                current_grid.append(line)
        
        # Add last puzzle
        if current_grid and grid_name:
            solver = SudokuClassifier()
            puzzle_dict = dict(zip(solver.squares, ''.join(current_grid)))
            puzzles.append((grid_name, puzzle_dict))
    
    return puzzles

def save_puzzles_by_difficulty(puzzles_with_difficulty: Dict[str, List], output_dir: str = "classified_puzzles"):
    """Save puzzles grouped by difficulty to separate files"""
    os.makedirs(output_dir, exist_ok=True)
    
    for difficulty, puzzle_list in puzzles_with_difficulty.items():
        filename = os.path.join(output_dir, f"{difficulty.lower()}_puzzles.txt")
        
        with open(filename, 'w') as file:
            file.write(f"# {difficulty} Sudoku Puzzles (Lewis 2007 Classification)\n")
            file.write(f"# Total puzzles: {len(puzzle_list)}\n\n")
            
            for grid_name, puzzle_dict, metrics in puzzle_list:
                file.write(f"{grid_name}\n")
                file.write(f"# Backtrack count: {metrics['backtrack_count']}\n")
                file.write(f"# CP percentage: {metrics['cp_percentage']:.1f}%\n")
                file.write(f"# Solve time: {metrics['time']:.4f}s\n")
                
                # Convert puzzle dict back to 9x9 format
                solver = SudokuClassifier()
                for i, row in enumerate(['ABCDEFGHI'[i:i+1] for i in range(9)]):
                    row_values = ''.join(puzzle_dict[row + col] for col in solver.COLS)
                    file.write(f"{row_values}\n")
                file.write("\n")

def main():
    # Initialize classifier
    classifier = SudokuClassifier()
    
    # Load puzzles
    input_file = "p096_sudoku.txt"  # Change this to your input file
    puzzles = load_puzzles_from_file(input_file)
    
    # Classify puzzles
    classified_puzzles = {
        "Easy": [],
        "Medium": [],
        "Hard": [],
        "Extreme": []
    }
    
    classification_summary = []
    
    print("Classifying Sudoku puzzles according to Lewis (2007) criteria...")
    print("=" * 70)
    
    for grid_name, puzzle_dict in puzzles:
        print(f"Processing {grid_name}...", end=" ")
        
        success, metrics = classifier.solve_puzzle(puzzle_dict)
        
        if success:
            difficulty = classifier.classify_difficulty_lewis(metrics)
            classified_puzzles[difficulty].append((grid_name, puzzle_dict, metrics))
            
            classification_summary.append({
                'grid': grid_name,
                'difficulty': difficulty,
                'time': metrics['time'],
                'backtrack_count': metrics['backtrack_count'],
                'cp_percentage': metrics['cp_percentage']
            })
            
            print(f"✓ {difficulty} (BT: {metrics['backtrack_count']}, CP: {metrics['cp_percentage']:.1f}%)")
        else:
            print("✗ Failed to solve")
    
    # Save classified puzzles
    save_puzzles_by_difficulty(classified_puzzles)
    
    # Print summary
    print("\n" + "=" * 70)
    print("CLASSIFICATION SUMMARY (Lewis 2007)")
    print("=" * 70)
    
    for difficulty in ["Easy", "Medium", "Hard", "Extreme"]:
        count = len(classified_puzzles[difficulty])
        percentage = (count / len(puzzles)) * 100 if puzzles else 0
        print(f"{difficulty:8}: {count:2} puzzles ({percentage:5.1f}%)")
    
    print(f"\nTotal processed: {len(classification_summary)} puzzles")
    print(f"Files saved in 'classified_puzzles' directory")
    
    # Detailed statistics
    print("\n" + "=" * 70)
    print("DETAILED STATISTICS")
    print("=" * 70)
    
    for difficulty in ["Easy", "Medium", "Hard", "Extreme"]:
        puzzles_in_cat = [p for p in classification_summary if p['difficulty'] == difficulty]
        if puzzles_in_cat:
            avg_time = sum(p['time'] for p in puzzles_in_cat) / len(puzzles_in_cat)
            avg_bt = sum(p['backtrack_count'] for p in puzzles_in_cat) / len(puzzles_in_cat)
            avg_cp = sum(p['cp_percentage'] for p in puzzles_in_cat) / len(puzzles_in_cat)
            
            print(f"\n{difficulty}:")
            print(f"  Average time: {avg_time:.4f}s")
            print(f"  Average backtracking: {avg_bt:.1f}")
            print(f"  Average CP percentage: {avg_cp:.1f}%")

if __name__ == "__main__":
    main()