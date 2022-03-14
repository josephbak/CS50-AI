import itertools
import random
import copy


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
        # mine_cells = set() # I need to implement this part.
        if self.count == len(self.cells):
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
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
        # 1
        self.moves_made.add(cell)
        # 2
        self.mark_safe(cell)
        # 3
        cells_around = set()
        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # check if cell in bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    cells_around.add((i, j))
        # check if neighbot cell's state is already determined
        copied_cells_around = copy.deepcopy(cells_around)
        for neighbor_cell in copied_cells_around:
            if neighbor_cell in self.mines:
                cells_around.remove(neighbor_cell)
                count -= 1
            elif neighbor_cell in self.safes:
                cells_around.remove(neighbor_cell)
            else:
                pass

        new_sentence = Sentence(cells_around, count)

        if count == 0:
            for cell in cells_around:
                self.mark_safe(cell)


        if self.no_sentence_dupl_check(new_sentence):
            self.mark_safes_and_mines(new_sentence)
            # new inferences
            new_knowledge = []
            copied_knowledge = copy.deepcopy(self.knowledge)
            for sentence in copied_knowledge:
                if sentence.cells.issubset(new_sentence.cells): 
                    count_differece = new_sentence.count - sentence.count
                    set_difference = new_sentence.cells.difference(sentence.cells)
                    if count_differece != 0 and len(set_difference) != count_differece:
                        new_knowledge.append(Sentence(set_difference, count_differece))
                if new_sentence.cells.issubset(sentence.cells):
                    count_differece = sentence.count - new_sentence.count
                    set_difference = sentence.cells.difference(new_sentence.cells)
                    if count_differece != 0 and len(set_difference) != count_differece: 
                        new_knowledge.append(Sentence(set_difference,count_differece))
            self.knowledge.append(new_sentence)
            for sentence in new_knowledge:
                self.add_inference

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_moves_unmade = set()
        for cell in self.safes:
            if cell not in self.moves_made:
                safe_moves_unmade.add(cell)
        if safe_moves_unmade: # not empty
            # print(safe_moves_unmade)
            return random.choice(tuple(safe_moves_unmade))
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_possible_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                all_possible_moves.add((i, j))
        all_possible_moves = all_possible_moves.difference(self.moves_made)
        all_possible_moves = all_possible_moves.difference(self.mines)
        if all_possible_moves:
            return random.choice(tuple(all_possible_moves))
        else:
            return None
    

    def mark_safes_and_mines(self, new_sentence):
        if self.no_sentence_dupl_check(new_sentence): # this ensures there is no same sentence
            copied_knowledge = copy.deepcopy(self.knowledge)
            for sentence in copied_knowledge:
                if sentence.cells.issubset(new_sentence.cells):
                    count_differece = new_sentence.count - sentence.count
                    set_difference = new_sentence.cells.difference(sentence.cells)
                    if count_differece == 0: # all safe cells
                        for cell in set_difference:
                            self.mark_safe(cell)
                    elif len(set_difference) == count_differece: # all mines
                        for cell in set_difference:
                            self.mark_mine(cell)
                    else:
                        pass
                if new_sentence.cells.issubset(sentence.cells):
                    count_differece = sentence.count - new_sentence.count
                    set_difference = sentence.cells.difference(new_sentence.cells)
                    if count_differece == 0: # all safe cells
                        for cell in set_difference:
                            self.mark_safe(cell)
                    elif len(set_difference) == count_differece: # all mines
                        for cell in set_difference:
                            self.mark_mine(cell)
                    else:
                        pass


    def no_sentence_dupl_check(self, new_sentence): # true if there is no duplication
        checker = True
        for sentence in self.knowledge:
            if new_sentence == sentence:
                checker = False
                break
        return checker
    

    def add_inference(self, new_sentence):
        self.mark_safes_and_mines(new_sentence)
        copied_knowledge = copy.deepcopy(self.knowledge)
        self.knowledge.append(new_sentence)
        for sentence in copied_knowledge:
            if sentence.cells.issubset(new_sentence.cells): 
                count_differece = new_sentence.count - sentence.count
                set_difference = new_sentence.cells.difference(sentence.cells)
                if count_differece != 0 and len(set_difference) != count_differece:
                    self.knowledge.append(Sentence(set_difference, count_differece))
            
            if new_sentence.cells.issubset(sentence.cells):
                count_differece = sentence.count - new_sentence.count
                set_difference = sentence.cells.difference(new_sentence.cells)
                if count_differece != 0 and len(set_difference) != count_differece: 
                    self.knowledge.append(Sentence(set_difference,count_differece))


# def add_inferences_to_knowledge(knowledge, new_sentence): # recursion....
#     copied_knowledge = copy.copy(knowledge) # before adding the sentence
#     knowledge.append(new_sentence)

#     for sentence in copied_knowledge:
#         if sentence.cells.issubset(new_sentence.cells):
#             count_differece = new_sentence.count - sentence.count
#             set_difference = new_sentence.cells.difference(sentence.cells)
#             created_sentence = Sentence(set_difference, count_differece)
#             if no_sentence_dupl_check(knowledge, created_sentence):
#                 add_inferences_to_knowledge(knowledge, created_sentence)
#                 # knowledge.append(created_sentence) # add new inference
#             else:
#                 return
#         elif new_sentence.cells.issubset(sentence.cells):
#             count_differece = sentence.count - new_sentence.count
#             set_difference = sentence.cells.difference(new_sentence.cells)
#             created_sentence = Sentence(set_difference, count_differece)
#             if no_sentence_dupl_check(knowledge, created_sentence):
#                 add_inferences_to_knowledge(knowledge, created_sentence)
#                 # knowledge.append(created_sentence) # add new inference
#             else:
#                 return
#         else:
#             pass

# def clean_knowledge(knowledge):
#     safe_sets = set()
#     mine_sets = set()
#     for sentence in knowledge:
#         if sentence.count == 0:
#             for element in sentence.cells:
#                 safe_sets.add(element)
#         elif sentence.count == len(sentence.cells):
#             for element in sentence.cells:
#                 mine_sets.add(element)
#         else:
#             pass
#     return safe_sets, mine_sets