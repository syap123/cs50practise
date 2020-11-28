import sys

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
        newset = ()
        for var in self.domains:
            for word in list(self.domains[var]):
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
        revised = False
        for x_word in list(self.domains[x]):
            # find at least 1 y_word that satisfies x_word:
            y_word_satisfaction = False
            for y_word in list(self.domains[y]):
                # prevent same word
                if y_word == x_word:
                    continue
                if self.crossword.overlaps[x,y] is None:
                    continue
                xpos, ypos = self.crossword.overlaps[x,y]
                if x_word[xpos] == y_word[ypos]:
                    y_word_satisfaction = True
                    break
            if y_word_satisfaction == False:
                self.domains[x].remove(x_word)
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
        # first initiate arc queue
        arc_queue = []
        if arcs is None:
            for x_var in self.crossword.variables:
                for y_var in self.crossword.variables:
                    if x_var == y_var:
                        continue
                    if self.crossword.overlaps[x_var,y_var] is None:
                        continue
                    else:
                        arc_queue.append((x_var,y_var))
        else:
            arc_queue = arcs
        while len(arc_queue) > 0:
            x,y = arc_queue.pop(0)
            if self.revise(x,y):
                if len(self.domains[x]) == 0:
                    return False
                for z_var in self.crossword.neighbors(x):
                    if z_var == y:
                        continue
                    arc_queue.append((z_var,x))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if (var not in assignment) or (assignment[var] is None):
                return False
        return True
    

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for x_var in assignment:
            for y_var in assignment:
                if x_var == y_var:
                    continue
                if y_var in self.crossword.neighbors(x_var):
                    xpos, ypos = self.crossword.overlaps[x_var,y_var]
                    if assignment[x_var][xpos] != assignment[y_var][ypos]:
                        return False
                # prevent same word from being assigned twice
                if assignment[x_var] == assignment[y_var]:
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        ordered_domain_list = []
        for x_word in self.domains[var]:
            rule_out_count = 0
            for y_var in self.crossword.neighbors(var):
                xpos, ypos = self.crossword.overlaps[var,y_var]
                for y_word in self.domains[y_var]:
                    if x_word[xpos] != y_word[ypos]:
                        rule_out_count = rule_out_count + 1
            ordered_domain_list.append((x_word,rule_out_count))
        return sorted(ordered_domain_list, key = lambda x: x[1])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        var_list = []
        for var in self.crossword.variables:
            if var not in assignment:
                domain_count = len(self.domains[var])
                neighbor_count = len(self.crossword.neighbors(var))
                # if there is a tie, choose var with the highest neighbor
                var_list.append((var,domain_count,neighbor_count))
        var_list = sorted(var_list, key = lambda x: (x[1],-x[2]))
        return var_list[0][0]

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
        for value in self.domains[var]:
            assignment[var] = value
            if not self.consistent(assignment):
                del assignment[var]
            else:
                result = self.backtrack(assignment)
                if result != False:
                    return result
                else:
                    del assignment[var]
        return False


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
