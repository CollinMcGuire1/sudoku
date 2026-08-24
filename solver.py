


"""
r is row, like 'A' or 'I'
c is column, like '1' or '9'
s is a square, like 'A1' or 'I9'
d is a digit, like '9'
u is a unit, such as a row or column or box, like ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1']
grid is the grid of 81 squares, and is listed in a string of 81 digits or dots: '..13..4.5.7...8    ...'
values is a dict of possible values givin a square, i.e. {'A1': '13478', 'A2': '23'}
"""

def cross(A, B):
    "Cross product of elements in A and elements in B"
    return [a + b for a in A for b in B]

digits = '123456789'
rows = 'ABCDEFGHI'
columns = digits
squares = cross(rows, columns)
unitlist = ([cross(rows, c) for c in columns] +
            [cross(r, columns) for r in rows] +
            [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')])
units = dict((s, [u for u in unitlist if s in u]) for s in squares) # this line assigns each square to the three units that it belongs to, its row, column, and box. for s in squares is the looping through each square on the grid, [u for u in unitlist if s in u] filters each given square into its 3 units. dict(...) is the storing into key-value pairs; 'SQUARE': [[**ROW**], [**COLUMN**], [**BOX**]]
peers = dict((s, set(sum(units[s],[])) - set([s])) for s in squares) # this line combines the 3 units that each square belongs to, and identifies the 20 peers for each. sum(units[s], []) combines the 3 unit lists into one list. set(...) converts the single list into a set, which removes duplicate entries. - set([s]) removes the individual square from the set, as a square cannot be its own peer.

        ### GRID PARSING ###

def parse_grid(grid):
    # Convert the grid into a dict of possible values, {square: digits}, or return False if a contradiction is detected

    values = dict((s, digits) for s in squares)
    for s, d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False # fails if a digit cannot be assigned to a square
    return values

def grid_values(grid):
    # Convert the grid into a dict of {square: char} with '0' or '.' for empty squares
    chars = [c for c in grid if c in digits or c in '0. '] # this line loops through all of the charactes listed in grid, and if c appears in digits, or if c is a '0', '.', or ' ', then c is kept. otherwise, it is not put into the chars list, thus removing gridlines and such from the next steps.
    if len(chars) != 81: print(grid, chars, len(chars))
    assert len(chars) == 81
    return dict(zip(squares, chars)) # pairs each square with the digit (or blank '.' / ' ') that is associated with that square

        ### CONSTRAINT PROPOGATING ###

def assign(values, s, d):
    # eliminate all digits other than d to a square, s. Returns all Values except False when a contradiction is found.
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False

def eliminate(values, s, d):
    # eleminate d from values[s], propagate when values or places <= 2. Returns values except False when a contradiction is found.
    if d not in values[s]:
        return values # already eliminated
    values[s] = values[s].replace(d, '')
    # (1) if a square is reduced to one value d2, then eliminate d2 from the rest of the square's peers
    if len(values[s]) == 0:
        return False # contradiction found, the last value has been removed
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    # (2) if a unit u is reduced to only one place for a value d, put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False # contradiction: this digit has no place that it can go in this square's units.
        elif len(dplaces) == 1:
            # then d can only be put into one square, assign it there;
            if not assign(values, dplaces[0], d):
                return False # contradiction if digit cannot be placed in the only square that it belongs in.
    return values

        ### DISPLAY AS A 2-D GRID ###

def display(values):
    "Display these values as a 2-D grid."
    if values is False:
        print("No solution found.")
        return
    width = 1 + max(len(values[s]) for s in squares)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in columns))
        if r in 'CF': 
            print(line)


def solve(grid): return search(parse_grid(grid))

def search(values):
    # using depth-first search and propagation, try all possible values
    if values is False:
        return False # already failed earlier somwhere else
    if all(len(values[s]) == 1 for s in squares): # checking if all squares have exactly one possible digit
           return values # success, solved!
    # since it is not solved at this point, choose the square with the fewest possible digits and start making guesses. backtrack when a guess turns out to be impossible/wrong
    n, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1) # check for all unsolved squares (len(values) > 1). (len(values[s]), s) Assigns pairs of (number of options, square name). min(...) picks the square with the least number of options available
    for d in values[s]: # loops through the values
        result = search(assign(values.copy(), s, d)) # makes a COPY of the boardstate, so that it can backtrack if wrong. assign() tentatively places the digit in that square. search() recursively calls the search function on the NEW board to see if that guess digit would work for the rest of the board.
        if result: return result # if all works out after a guess, return the resulting correct, solved board.
