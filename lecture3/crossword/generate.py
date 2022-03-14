from multiprocessing.reduction import duplicate
import sys
import copy

from sqlalchemy import distinct

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domain_copy = copy.deepcopy(self.domains)
        for var in domain_copy:
            for word in domain_copy[var]:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if self.crossword.overlaps[x, y] is None:
            return False
        else:
            revised = False
            x_index, y_index = self.crossword.overlaps[x, y]
            possible_char = {word[y_index] for word in self.domains[y]}
            x_domain_copy = copy.deepcopy(self.domains[x])
            for word in x_domain_copy:
                if word[x_index] not in possible_char:
                    self.domains[x].remove(word)
                    revised = True
            return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            # all possible arcs
            arcs = [(x, y) for x in self.crossword.variables for y in self.crossword.variables if x != y and self.crossword.overlaps[x,y] is not None]
        while arcs:
            # deque
            (x, y) = arcs[0]
            arcs = arcs[1:]
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                neighbors_of_x = self.crossword.neighbors(x).remove(y)
                if neighbors_of_x is not None:
                    for neighbor in neighbors_of_x:
                        arcs.append((neighbor, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in set(assignment.keys()):
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check distinctness
        if len(list(assignment.values())) != len(set(assignment.values())):
            return False
        # check unary condition
        for var in assignment:
            if var.length != len(assignment[var]):
                return False
        # check binary condition
        for var in assignment:
            neighbors= self.crossword.neighbors(var).intersection(set(assignment.keys()))
            for neighbor in neighbors:
                # if neighbor in assignment_variables: 
                var_index, neighbor_index = self.crossword.overlaps[var, neighbor]
                if assignment[var][var_index] != assignment[neighbor][neighbor_index]:
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        assigned_variables = set(assignment.keys())
        not_assigned_variables = self.crossword.variables.difference(assigned_variables)

        def order_helper(value):
            n = 0
            for neighbor in self.crossword.neighbors(var).intersection(not_assigned_variables):
                var_index, neighbor_index = self.crossword.overlaps[var, neighbor]
                for neighbor_value in self.domains[neighbor]:
                    if value[var_index] != neighbor_value[neighbor_index]:
                        n += 1
            return n

        return sorted(self.domains[var], key=order_helper)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        assigned_variables = set(assignment.keys())
        not_assigned_variables = self.crossword.variables.difference(assigned_variables)
        return sorted(not_assigned_variables, key=lambda x: (len(self.domains[x]), len(self.crossword.variables)-len(self.crossword.neighbors(x))))[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment): 
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            temp_assignment = copy.deepcopy(assignment)
            temp_assignment[var] = value
            if self.consistent(temp_assignment):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                else:
                    del assignment[var]
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()