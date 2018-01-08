
from utils import *
import itertools
import re

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# increment both diagonals to the unitlist to account for the diagonal sudoku policy
diagonal_ltor = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9']]
diagonal_rtol = [['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']]
# add the diagonal constraint along with existing constraints to unitlist
unitlist = row_units + column_units + square_units + diagonal_ltor + diagonal_rtol

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).
    """
    # get all keys that have a pair of possible values
    candidates = [x for x in boxes if len(values[x]) == 2]
    # comparing the cells in candidates against each other
    for box1, box2 in itertools.combinations_with_replacement(candidates, 2):
        # check to find potential naked twin
        if values[box1] == values[box2]:
            # confirm the validity of the naked twin by checking if one of the boxes is in the set of peers of the other
            if box1 in peers[box2]:
                for cells in peers[box1].intersection(peers[box2]):   ## intersection of the peers for the two twin boxes (this is also the set of cells that require modification)
                    pattern = '[' + values[box1] + ']'
                    # values[cells] = re.sub(pattern, '', values[cells])  ##replace the values of the naked twins with empty string in the intersection of peers
                    values = assign_value(values, cells, re.sub(pattern, '', values[cells]))
    return values


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    # gets the boxes with only one possible digit
    vals = [i for i in values.keys() if len(values[i]) == 1]
    for k in vals:
        # gets the value of the selected box
        unit = values[k]
        # goes over all possible peers corresponding to the selected box
        for peer in peers[k]:
            # updates the values of all corresponding keys in our sudoku to not have the value of the selected box
            # values[peer] = values[peer].replace(unit,'')
            values = assign_value(values, peer, values[peer].replace(unit,''))
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    # unit is each row list, column list or square list element
    for unit in unitlist:
        """
        digit_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        A1, A2, A3, B1, B2 ... etc.
        for indices in unit:
            if len(values[indices]) == 1:
                digit_list.remove(values[indices])
        """
        # check the only choice constraint for each possible value in the selected unit
        for digit in '123456789':
            # adds the box in the selected unit if the selected digit is part of the box's values
            dplaces = [box for box in unit if digit in values[box]]
            # if the length of the list above is one, it means only that box can hold the value
            if len(dplaces) == 1:
                # perform assignment of the digit in the sudoku dictionary
                # values[dplaces[0]] = digit
                values = assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value before applying constraint strategies
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Apply the Eliminate Strategy
        values = eliminate(values)
        # Apply the Only Choice Strategy
        values = only_choice(values)
        # Apply the Naked Twins Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value after applying the constraint strategies
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, exit the loop sequence
        stalled = solved_values_before == solved_values_after
        # Return False if the puzzle is unsolvable
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.
    Using depth-first search and propagation, create a search tree and solve the sudoku.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    selected = ''
    for box in boxes:
        if len(values[box]) > 1:
            selected = box ## randomly assign selected to be a box w/t uncertain value
            break
    # assigns selected to be the one with minimum number of values (>=2)
    for i in boxes:
        if len(values[selected]) == 2:
            break
        elif len(values[i]) < len(values[selected]) and len(values[i]) == 2:
            selected = i
            break
        elif len(values[i]) < len(values[selected]) and len(values[i]) >= 2:
            selected = i
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for option in values[selected]:
        sudoku_copy = values.copy()
        sudoku_copy[selected] = option
        assign_value(sudoku_copy, selected, option)
        recurse = search(sudoku_copy)
        if recurse:
            return recurse


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.

        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    result = search(values)
    if result is None or result is False:
        return False
    return result


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    # diag_sudoku_grid = '8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..'
    # diag_sudoku_grid =  '...............9..97.3......1..6.5....47.8..2.....2..6.31..4......8..167.87......'
    # diag_sudoku_grid = '.......41......89...7....3........8.....47..2.......6.7.2........1.....4..6.9.3..'

    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
