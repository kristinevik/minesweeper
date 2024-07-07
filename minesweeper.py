import copy
import itertools
import random


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
        # If the number of cells left to investigate (neighbour of cells) = the count of mines,
        # the rest of the cells are mines

        if len(self.cells) == self.count:
            return self.cells
        
        # else we cannot know what cells are mines yet, so return empty set
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If the count of mines around a cell are 0 (we have identified all cells with mines),
        # the rest of the cells are safe
        if self.count == 0:
            return self.cells
        return set() # else we cannot know what cells are safe yet, so return empty set

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        # If we know it is a mine, remove it from cells/possible mines that needs investigation
        # These cells will be found in the mines set
        try: # Try to remove the cell from the set. If error, it was not there
            self.cells.remove(cell) 
            self.count -= 1 # Take away one mine from the count of mine
        except: pass

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        # If we know it is safe, remove it from moves that needs investigation
        # These cells will be found in the safes set
        try: # This cell might not be in the set of neighbours for this sentence
            self.cells.remove(cell)
        except: pass


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
        self.mines.add(cell) # Add this cell to set of mines

        # For each sentence, move this cell away from the list of cells to investigate
        # and update undiscovered mines
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell) # Add this cell to set of safe moves to take

        # For each sentence, move this cell away from the set of possible mines (cells)
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
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`

        # First find the neighbours which are the possible cells for mines around the current cell
        neighbours = []
        for i in range(cell[0] - 1, cell[0] + 2): # Check one cell to the left. Add plus two as the range function does not inlcude the last number
            for j in range(cell[1] - 1, cell[1] + 2): # Check from one above to one below

                if 0 <= i < self.height and 0 <= j < self.width: # Check only if positive value and on the board
                    # check if i, j is same as cell (we already know this does not have mine)
                    # or if it is already marked as safe
                    # then we can skip it
                    if (i, j) == cell or (i, j) in self.safes:
                        pass
                    
                    # If it is a mine, the count should be reduced for this sentence,
                    # as one mine is already found
                    elif (i, j) in self.mines: 
                        count -= 1

                    else:
                        neighbours.append((i, j))


        # Add sentence to the knowledge base
        if len(neighbours) > 0: # Only if there are cells left that needs investigation
            create_sentence = Sentence(neighbours, count)
            self.knowledge.append(create_sentence)

        # 4) mark any additional cells as safe or as mines
        # if it can be concluded based on the AI's knowledge base
        self.update_knowledge()

            
    def update_knowledge(self):
        """
        mark any additional cells as safe or as mines
        if it can be concluded based on the AI's knowledge base

        add any new sentences to the AI's knowledge base
        if they can be inferred from existing knowledge
        """

        stop = False
        # Keep looping until no new knowledge
        while stop == False:
            # Only set to false again, if we find new knowledge
            stop = True

            # Now that we have made a new move and added a new sentence, 
            # We have to go through all sentences to see if we now can identify all mines or all safe cells
            new_safes = set() # Use set to avoid duplicates
            new_mines = set()
            for sentence in self.knowledge:
                new_safes.update(sentence.known_safes())
                new_mines.update(sentence.known_mines())

            # Mark any new safe cells
            for safe_cell in new_safes:
                if safe_cell in self.safes: pass
                else:
                    self.mark_safe(safe_cell)
                    stop = False # We have to keep looping to see if this new info helped us find more info

            # Mark any new mines
            for mine_cell in new_mines:
                if mine_cell not in self.mines:
                    self.mark_mine(mine_cell)
                    stop = False # We have to keep looping to see if this new info helped us find more info

            # Create a list to store new sentences
            new_sentences = []

            copy_knowledge = copy.deepcopy(self.knowledge)

            # Compare every pair of sentences to check if they share cells, and if so, use this to create new sentences
            for s in copy_knowledge:
                copy_knowledge.remove(s)

                for s2 in copy_knowledge:
                    # Check if all of the cells of s2 are part of the sentence investigated
                    if s2.cells.issubset(s.cells):
                        # If they are, we now that the rest of the cells in the original sentence, will not have the mines
                        # that are in the subset, so we now have more information
                        new_cells = s.cells-s2.cells
                        new_count = s.count-s2.count
                        new_sentence = Sentence(new_cells, new_count)

                        # Add the new sentence if it's not already in the knowledge
                        if new_sentence in self.knowledge or new_sentence in new_sentences:
                            pass
                        else:
                            if new_sentence not in new_sentences: new_sentences.append(new_sentence)
                            stop = False

            # Add the inferred sentences to the knowledge base
            for new_knowledge in new_sentences:
                self.knowledge.append(new_knowledge)

            # Check if there are any sentences that does not have cells left to investigate
            non_empty_sentences = []
            for sentence in self.knowledge:
                if len(sentence.cells) > 0:
                    non_empty_sentences.append(sentence)
            self.knowledge = non_empty_sentences
            
            # If no new knowledge found, exit the loop
            if stop == True:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe in self.safes:
            if safe in self.moves_made:
                pass
            else:
                return safe
        return None # If there are no safe moves


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        moves = [(i, j) for i in range(self.height) for j in range(self.width)]
        
        while len(moves) != 0: # only loop if moves not empty
            move = random.choice(moves)
            if move in self.moves_made or move in self.mines:
                moves.remove(move)
            else:
                return move

        # if all moves are made or are mines, return None
        return None       
