import itertools
import random
#import pickle

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count
     

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()
        

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        self.cells.remove(cell)
        self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        self.cells.remove(cell)
        


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def adjacent_cells(self, cell):
        neighbors = set()

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # Ignore if it is a move made
                if (i, j) in self.moves_made:
                    continue
                # Add cell as possible neighbor if within bounds of the board:
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbors.add((i,j))
        return neighbors               

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark cell as moved
        self.moves_made.add(cell)
        # 2) mark cell as safe:
        self.safes.add(cell)
        # 3) add a new sentence to the AI's knowledge base
        new_sentence = Sentence(self.adjacent_cells(cell),count)
        print('new_sentence_cells and count:')
        print(new_sentence.cells)
        print(new_sentence.count)
        # for cell in self.safes:
        #     if cell in new_sentence.cells:
        #         new_sentence.mark_safe(cell)
        # for cell in self.mines:
        #     if cell in new_sentence.cells:
        #         new_sentence.mark_mine(cell)            
        self.knowledge.append(new_sentence)
        
        # now loop through knowledge base to do #4 and #5
        nth_sentence = 0

        while nth_sentence < len(self.knowledge):
            set1 = self.knowledge[nth_sentence]
            nth_sentence = nth_sentence + 1
            if len(set1.cells) == 0:
                continue   
            # 4) mark any additional cells as safe or as mines
            if len(set1.known_mines()) > 0:
                for mine in set1.known_mines():
                    self.mines.add(mine)
            if len(set1.known_safes()) > 0:
                for safe in set1.known_safes():
                    self.safes.add(safe)                           
            
            # first update the existing sentences with new information:
            safe_in_set1 = set1.cells.intersection(self.safes)
            for safe in safe_in_set1:
                set1.mark_safe(safe)
            mines_in_set1 = set1.cells.intersection(self.mines)
            for mine in mines_in_set1:
                set1.mark_mine(mine)  

            if len(set1.cells) == 0:
                continue                          
            # 5) add any new sentences to the AI's knowledge base
            # we compare every sentence against every other sentence, check if any of them are subsets of each other
            for set2 in self.knowledge:
                if len(set2.cells) == 0:
                    continue
                if set1 == set2:
                    continue
                if set1.cells.issubset(set2.cells):
                    s3cells = set2.cells.difference(set1.cells)
                    set3 = Sentence(s3cells,set2.count - set1.count)
                    # now check if the sentence already exists in knowledge base to prevent infinite loops
                    has_sentence = False
                    for existing_sentence in self.knowledge:
                        if set3 == existing_sentence:
                            has_sentence = True
                    if has_sentence == False:
                        self.knowledge.append(set3)
                        # now that sentence has been added, we need to start from the top and check every sentence again
                        print('new sentence inferred: ')
                        print('set 1: ' + str(set1.cells))
                        print('set 2: ' + str(set2.cells))
                        print('outcome: ' + str(set3.cells))
                        nth_sentence = 0
            
        #with open('knowledge_' + str(len(self.moves_made)), 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            #pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

        print('add knowledge done, below are the safe cells: ')
        print(self.safes)

        print('add knowledge done, below are the cells with mines: ')
        print(self.mines)        

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                print(cell)
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Initialize an empty field with no mines
        for i in range(self.height):
            for j in range(self.width):
                if (i,j) not in self.moves_made and (i,j) not in self.mines:
                    print(i,j)
                    return (i,j)
        return None
        
