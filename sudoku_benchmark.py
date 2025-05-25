import time
import csv
import psutil
import os
from typing import List, Dict, Tuple
from sudoku_cp import depth_first_search, propagate_constraints, generate_board, dict_to_2d_list
from sudoku_backtracking import SudokuBacktracking
from sudoku_cp_backtracking import SudokuSolver

'''
Đo lường hiệu suất 3 thuật toán gồm backtracking (sudoku_backtracking.py), constraint propagation (soduku_cp.py) và 
thuật toán constraint propagation kết hợp backtracking(sudoku_cp_backtracking.py)
Kết quả được lưu vào file benchmark_results.csv

'''
class SudokuMetrics:
    def __init__(self):
        self.execution_time = 0
        self.assignments = 0
        self.backtracks = 0
        self.memory_usage = 0

class SudokuBenchmark:
    def __init__(self, enable_memory=False):
        self.bt_metrics = []  # Backtracking metrics
        self.cp_metrics = []  # Constraint Propagation metrics 
        self.opt_metrics = [] # Optimized solver metrics
        self.backtracking_solver = SudokuBacktracking()
        self.optimized_solver = SudokuSolver()
        self.enable_memory = enable_memory

    def solve_with_backtracking(self, grid: List[List[int]]) -> Tuple[List[List[int]], SudokuMetrics]:
        metrics = SudokuMetrics()
        if self.enable_memory:
            import tracemalloc
            tracemalloc.start()
        start_time = time.time()
        
        # Reset counters before solving
        self.backtracking_solver.assignments = 0
        self.backtracking_solver.backtracks = 0
        
        # Solve with backtracking
        solved = self.backtracking_solver.solve(grid)
        
        # Record metrics
        metrics.execution_time = (time.time() - start_time) * 1000
        if self.enable_memory:
            current, peak = tracemalloc.get_traced_memory()
            metrics.memory_usage = peak / 1024 / 1024
            tracemalloc.stop()
        else:
            metrics.memory_usage = 0
        metrics.assignments = self.backtracking_solver.assignments
        metrics.backtracks = self.backtracking_solver.backtracks
        
        return solved, metrics

    def solve_with_constraint_propagation(self, grid: List[List[int]]) -> Tuple[Dict[str, str], SudokuMetrics]:
        import sudoku_cp  # Ensure we can access global counters
        metrics = SudokuMetrics()
        if self.enable_memory:
            import tracemalloc
            tracemalloc.start()
        start_time = time.time()
        
        # Convert grid to puzzle format
        puzzle = {}
        for i, row in enumerate('ABCDEFGHI'):
            for j, col in enumerate('123456789'):
                puzzle[row + col] = str(grid[i][j]) if grid[i][j] != 0 else '0'
        
        # Initialize board and counters
        board = generate_board()
        # Reset counters before solving
        sudoku_cp.cp_assignments = 0
        sudoku_cp.cp_backtracks = 0
        
        # Solve with constraint propagation
        solved = None
        try:
            board = propagate_constraints(puzzle, board)
            if board:
                solved = depth_first_search(board)
                if solved:
                    solved = dict_to_2d_list(solved)
        except Exception as e:
            print(f"Error in constraint propagation: {e}")
        
        # Record metrics
        metrics.execution_time = (time.time() - start_time) * 1000
        if self.enable_memory:
            current, peak = tracemalloc.get_traced_memory()
            metrics.memory_usage = peak / 1024 / 1024
            tracemalloc.stop()
        else:
            metrics.memory_usage = 0
        metrics.assignments = getattr(sudoku_cp, 'cp_assignments', 0)
        metrics.backtracks = getattr(sudoku_cp, 'cp_backtracks', 0)
        
        return solved, metrics

    def solve_with_optimized(self, grid: List[List[int]]) -> Tuple[List[List[int]], SudokuMetrics]:
        metrics = SudokuMetrics()
        if self.enable_memory:
            import tracemalloc
            tracemalloc.start()
        start_time = time.time()
        
        # Solve with optimized solver
        solved = self.optimized_solver.solve(grid)
        
        # Record metrics
        metrics.execution_time = (time.time() - start_time) * 1000
        if self.enable_memory:
            current, peak = tracemalloc.get_traced_memory()
            metrics.memory_usage = peak / 1024 / 1024
            tracemalloc.stop()
        else:
            metrics.memory_usage = 0
        metrics.assignments = self.optimized_solver.assignments
        metrics.backtracks = self.optimized_solver.backtracks
        
        return solved, metrics

    def save_results(self, filename: str):
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Backtracking', 'Constraint Propagation', 'Optimized'])
            
            def safe_average(metrics, attr):
                values = [getattr(m, attr) for m in metrics]
                return sum(values) / len(values) if values else 0
            
            # Calculate metrics for all three methods
            avg_bt_time = safe_average(self.bt_metrics, 'execution_time')
            avg_cp_time = safe_average(self.cp_metrics, 'execution_time')
            avg_opt_time = safe_average(self.opt_metrics, 'execution_time')
            
            avg_bt_assigns = safe_average(self.bt_metrics, 'assignments')
            avg_cp_assigns = safe_average(self.cp_metrics, 'assignments')
            avg_opt_assigns = safe_average(self.opt_metrics, 'assignments')
            
            avg_bt_backtracks = safe_average(self.bt_metrics, 'backtracks')
            avg_cp_backtracks = safe_average(self.cp_metrics, 'backtracks')
            avg_opt_backtracks = safe_average(self.opt_metrics, 'backtracks')
            
            avg_bt_mem = safe_average(self.bt_metrics, 'memory_usage')
            avg_cp_mem = safe_average(self.cp_metrics, 'memory_usage')
            avg_opt_mem = safe_average(self.opt_metrics, 'memory_usage')
            
            # Write results for all three methods
            writer.writerow(['Execution Time (ms)', f'{avg_bt_time:.2f}', f'{avg_cp_time:.2f}', f'{avg_opt_time:.2f}'])
            writer.writerow(['Assignments', f'{avg_bt_assigns:.0f}', f'{avg_cp_assigns:.0f}', f'{avg_opt_assigns:.0f}'])
            writer.writerow(['Backtracks', f'{avg_bt_backtracks:.0f}', f'{avg_cp_backtracks:.0f}', f'{avg_opt_backtracks:.0f}'])
            writer.writerow(['Memory Usage (MB)', f'{avg_bt_mem:.2f}', f'{avg_cp_mem:.2f}', f'{avg_opt_mem:.2f}'])

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
                current_puzzle.append([int(x) for x in line])
        if current_puzzle:
            puzzles.append(current_puzzle)
    
    return puzzles



def main():
    # Đổi enable_memory thành False để tắt đo memory, True để bật đo memory
    benchmark = SudokuBenchmark(enable_memory=False)
    puzzles = load_puzzles('test_hard_and_unsolvable_puzzles.txt')
    
    print("Running benchmarks...")
    print(f"Total puzzles: {len(puzzles)}")
    
    for i, puzzle in enumerate(puzzles, 1):
        print(f"\nSolving puzzle {i}...")
        
        # Solve with backtracking
        print("Using Backtracking...")
        solution_bt, metrics_bt = benchmark.solve_with_backtracking(puzzle)
        if solution_bt is not None:
            benchmark.bt_metrics.append(metrics_bt)
            print(f"Time: {metrics_bt.execution_time:.2f}ms, "
                  f"Assignments: {metrics_bt.assignments}, "
                  f"Backtracks: {metrics_bt.backtracks}")
        
        # Solve with constraint propagation
        print("Using Constraint Propagation...")
        solution_cp, metrics_cp = benchmark.solve_with_constraint_propagation(puzzle)
        if solution_cp is not False:
            benchmark.cp_metrics.append(metrics_cp)
            print(f"Time: {metrics_cp.execution_time:.2f}ms, "
                  f"Assignments: {metrics_cp.assignments}, "
                  f"Backtracks: {metrics_cp.backtracks}")
            
        # Solve with optimized solver
        print("Using Optimized Solver...")
        solution_opt, metrics_opt = benchmark.solve_with_optimized(puzzle)
        if solution_opt is not None:
            benchmark.opt_metrics.append(metrics_opt)
            print(f"Time: {metrics_opt.execution_time:.2f}ms, "
                  f"Assignments: {metrics_opt.assignments}, "
                  f"Backtracks: {metrics_opt.backtracks}")
    
    # Save results
    benchmark.save_results('results_test_hard_and_unsolvable_puzzles.csv')
    print("\nResults saved to test_hard_and_unsolvable_puzzles.csv")

if __name__ == '__main__':
    main()
    # easy = [
    #     [5,3,0,0,7,0,0,0,0],
    #     [6,0,0,1,9,5,0,0,0],
    #     [0,9,8,0,0,0,0,6,0],
    #     [8,0,0,0,6,0,0,0,3],
    #     [4,0,0,8,0,3,0,0,1],
    #     [7,0,0,0,2,0,0,0,6],
    #     [0,6,0,0,0,0,2,8,0],
    #     [0,0,0,4,1,9,0,0,5],
    #     [0,0,0,0,8,0,0,7,9]
    # ]
    # print('\n--- TEST CASE ---')
    # benchmark = SudokuBenchmark()
    # # Backtracking
    # _, m_bt = benchmark.solve_with_backtracking([row[:] for row in easy])
    # print(f'Backtracking: Assignments={m_bt.assignments}, Backtracks={m_bt.backtracks}')
    # # Constraint Propagation
    # _, m_cp = benchmark.solve_with_constraint_propagation([row[:] for row in easy])
    # print(f'Constraint Propagation: Assignments={m_cp.assignments}, Backtracks={m_cp.backtracks}')
    # # Optimized
    # _, m_opt = benchmark.solve_with_optimized([row[:] for row in easy])
    # print(f'Optimized: Assignments={m_opt.assignments}, Backtracks={m_opt.backtracks}')