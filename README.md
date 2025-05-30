# Approach to the Sudoku puzzle

Upon reading the requirements, I started reading about Sudoku on the Internet.
The first article I read was about the BackTracking method on Wikipedia
(http://en.wikipedia.org/wiki/Sudoku_solving_algorithms). The rules of the game
were explained as follows:

The objective of Sudoku is to fill each square in a 9x9 grid with a value from 1
to 9 while observing the following constraints:

1. Each number 1 to 9 may only appear in each row .
2. Each number 1 to 9 may only appear in each column once.
3. Each number 1 to 9 may only appear in each box (a smaller 3x3 grid) once.

I decided to attempt solving the problem using the BackTracking algorithm as it
seemed like a very simple approach.

My work in the past has primarily been on SQL databases and I am not well versed
with any of the languages listed in the Sudoku coding challenge. I chose Python
because it is easy to learn and it has good data structures.

After attempting to solve the puzzle using the BackTracking algorithm, I
realized that while it was a simple approach, it was not a very efficient one.
So I decided to implement the solution using the Constraint Propagation
algorithm by Peter Norwig.
[Solving Every Sudoku Puzzle](http://norvig.com/sudoku.html).




# Summary

You can view the final code in [sudoku.py](sudoku.py). Use the following commands
to run to solve the example puzzles:

```bash


python sudoku.py -i test_hard_and_unsolvable_puzzles.txt -o original_solver_output.txt

sudoku_cp_backtracking.py -i test_hard_and_unsolvable_puzzles.txt -o optimized_solver_output.txt

python sudoku_benchmark.py
```


# References

- [Sudoku Wikipedia article](http://en.wikipedia.org/wiki/Sudoku_solving_algorithm)
- [Sudoku as a Constraint Problem](http://4c.ucc.ie/~hsimonis/sudoku.pdf)
- [Constraint satisfaction](http://en.wikipedia.org/wiki/Constraint_satisfaction)
- [Backtracking](http://en.wikipedia.org/wiki/Backtracking)
- [Solving Every Sudoku Puzzle](http://norvig.com/sudoku.html)
- [Google Python Style Guide](https://google-styleguide.googlecode.com/svn/trunk/pyguide.html)
