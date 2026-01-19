import numpy as np

class Piece:
    """
    Base class for pieces on the board. 
    
    A piece holds a reference to the board, its color and its currently located cell.
    In this class, you need to implement two methods, the "evaluate()" method and the "get_valid_cells()" method.
    """
    def __init__(self, board, white):
        """
        Constructor for a piece based on provided parameters

        :param board: Reference to the board this piece is placed on
        :type board: :ref:class:`board`
        """
        self.board = board      #reference to the board
        self.white = white      #colour of the piece (True=white, False=black)
        self.cell = None        #cell/position of the piece; tuple of row and colum



    def is_white(self):
        """
        Returns whether this piece is white

        :return: True if the piece white, False otherwise
        """
        return self.white

    def can_enter_cell(self, cell):
        """
        Shortcut method to see if a cell on the board can be entered.
        Simply calls :py:meth:`piece_can_enter_cell <board.Board.piece_can_enter_cell>` from the current board class.

        :param cell: The cell to check for. Must be a unpackable (row, col) type.
        :return: True if the provided cell can enter, False otherwise
        """
        return self.board.piece_can_enter_cell(self, cell)

    def can_hit_on_cell(self, cell):
        """
        Shortcut method to see if this piece can hit another piece on a cell.
        Simply calls :py:meth:`piece_can_hit_on_cell <board.Board.piece_can_hit_on_cell>` from the current board class.

        :param cell: The cell to check for. Must be a unpackable (row, col) type.
        :return: True if the piece can hit on the provided cell, False otherwise
        """
        return self.board.piece_can_hit_on_cell(self, cell)

    def evaluate(self, ai_mode=True):
        """
        **TODO** Implement a meaningful numerical evaluation of this piece on the board.
        This evaluation happens independent of the color as later, values for white pieces will be added and values for black pieces will be substracted. 
        
        **HINT** Making this method *independent* of the pieces color is crucial to get a *symmetric* evaluation metric in the end.
         
        - The pure existance of this piece alone is worth some points. This will create an effect where the player with more pieces on the board will, in sum, get the most points assigned. 
        - Think of other criteria that would make this piece more valuable, e.g. movability or whether this piece can hit other pieces. Value them accordingly.
        
        :return: Return numerical score between -infinity and +infinity. Greater values indicate better evaluation result (more favorable).
        """
        # each piece gets base points assigned, according to its class
        
        base_pts = 0

        if isinstance(self, Pawn):
            base_pts = 1
        elif isinstance(self, Knight) or isinstance(self, Bishop):
            base_pts = 3
        elif isinstance(self, Rook):
            base_pts = 5
        elif isinstance(self, Queen):
            base_pts = 9
        elif isinstance(self, King):
            base_pts = 999999
        elif base_pts == 0:         # controll structure;  for the case that the piece is not an object of any our known classes
            return 0
        
        score = base_pts            # these base points are the foundation of this pieces score

        if ai_mode:            # more complex evaluation for the ai
            
            # Bedrohen von pieces                   # the ability to hit oposing pieces in the next move adds value to the piece;
            offensive_base_factor = 1               # corresponding to the base points of the potentially hitted piece
            valid_cells = self.get_valid_cells()
            for cell in valid_cells:                # iterates through all valid cells of the piece
                enemy_base_pts = 0
                occupant = self.board.get_cell(cell)
                if occupant is not None:            # if an opposing piece can be hit in the next move, check the class of the piece
                    if isinstance(occupant, Pawn):
                        enemy_base_pts = 1
                    elif isinstance(occupant, Knight) or isinstance(occupant, Bishop):
                        enemy_base_pts = 3
                    elif isinstance(occupant, Rook):
                        enemy_base_pts = 5
                    elif isinstance(occupant, Queen):
                        enemy_base_pts = 9
                    elif isinstance(occupant, King):    # the equivalent to check (a check is favourable bc of the king's high base points)
                        enemy_base_pts = 12
                score += enemy_base_pts / 10        # adds a tenth of the base points of the hittable piece to the piece
                    
                    
            # position on the board/moveability

            row, col = self.cell        # unpacking of the current position of the piece in row and colum (col)
            position_factor = 1
            # checks with the row and col, how close the current position of the piece is to the center
            if not isinstance(self, King):          # for all pieces except the king
                if (row == 0 or row == 7) or (col == 0 or col == 7):
                    position_factor = 0.91
                elif (row == 1 or row == 6) or (col == 1 or col == 6):
                    position_factor = 0.94
                elif (row == 2 or row == 5) or (col == 2 or col == 5):
                    position_factor = 0.97
                elif (row == 3 or row == 4) and (col == 3 or col == 4):
                    position_factor = 1
            
            score *= position_factor    # the closer to the center; the higher the moveability, the higher the position factor

        return score          # returns the score of the evaluation of the piece

    def get_valid_cells(self):
        """
        **TODO** Return a list of **valid** cells this piece can move into. 
        
        A cell is valid if 
          a) it is **reachable**. That is what the :py:meth:`get_reachable_cells` method is for and
          b) after a move into this cell the own king is not (or no longer) in check.

        **HINT**: Use the :py:meth:`get_reachable_cells` method of this piece to receive a list of reachable cells.
        Iterate through all of them and temporarily place the piece on this cell. Then check whether your own King (same color)
        is in check. Use the :py:meth:`is_king_check_cached` method to test for checks. If there is no check after this move, add
        this cell to the list of valid cells. After every move, restore the original board configuration. 
        
        To temporarily move a piece into a new cell, first store its old position (self.cell) in a local variable. 
        The target cell might have another piece already placed on it. 
        Use :py:meth:`get_cell <board.BoardBase.get_cell>` to retrieve that piece (or None if there was none) and store it as well. 
        Then call :py:meth:`set_cell <board.BoardBase.set_cell>` to place this piece on the target cell and test for any checks given. 
        After this, restore the original configuration by placing this piece back into its old position (call :py:meth:`set_cell <board.BoardBase.set_cell>` again)
        and place the previous piece also back into its cell. 
        
        :return: Return True 
        """

        valid_cells = []                            #creation of a new list which should contain all the valid cells for a piece
        og_cell = self.cell                         # -> valid cells = possible moves that don't leave or put the own king in a check
        reachable_cells = self.get_reachable_cells()
       
        for cell in reachable_cells:                # iterates through all the reachable cells of the piece
            enemy = self.board.get_cell(cell)       # sets the new position on the board
            self.board.set_cell(cell, self)

            if not self.board.is_king_check_cached(self.white): # checks if the own king is in check in the newly set position
                valid_cells.append(cell)                        # if not, appends the cell to valid_cells

            self.board.set_cell(og_cell, self)      # reapplies the original board configurations
            self.board.set_cell(cell, enemy)

        return valid_cells                          # returns a list of the valid cells of the piece
            

class Pawn(Piece):  # Bauer
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        **TODO** Implement the movability mechanik for `pawns <https://de.wikipedia.org/wiki/Bauer_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Pawns can move only forward (towards the opposing army). Depening of whether this piece is black of white, this means pawn
        can move only to higher or lower rows. Normally a pawn can only move one cell forward as long as the target cell is not occupied by any other piece. 
        If the pawn is still on its starting row, it can also dash forward and move two pieces at once (as long as the path to that cell is not blocked).
        Pawns can only hit diagonally, meaning they can hit other pieces only the are one cell forward left or one cell forward right from them. 

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the pawn movability mechanics. 

        **NOTE**: For all you deep chess experts: Hitting `en passant <https://de.wikipedia.org/wiki/En_passant>`_ does not need to be implemented.
        
        :return: A list of reachable cells this pawn could move into.
        """
        reachable_cells = []        # creation of a list that should contain all the cells the pawn can reach in its next move;
        row, col = self.cell        # following the rules and in consideration of the current board configuration

        if self.white == True:      # white pawns
            if self.board.cell_is_valid_and_empty((row+1, col)):                # can always move one cell 'up' the board;
                reachable_cells.append((row+1, col))                            # if this cell is valid and empty
                if row == 1 and self.board.cell_is_valid_and_empty((3, col)):   # can move two cells 'up' the board on its first move;
                    reachable_cells.append((3, col))                            # if both of these cells are valid and empty
            if self.can_hit_on_cell((row+1, col+1)):                       
                reachable_cells.append((row+1, col+1))       # can hit one cell diagonally 'up' the board 
            if self.can_hit_on_cell((row+1, col-1)):         # if this cell has a piece of the opposing colour (black) on it
                reachable_cells.append((row+1, col-1))

        if self.white == False:     # black pawns
            if self.board.cell_is_valid_and_empty((row-1, col)):                # can always move one cell 'down' the board;
                reachable_cells.append((row-1, col))                            # if this cell is valid and empty
                if row == 6 and self.board.cell_is_valid_and_empty((4, col)):   # can move two cells 'down' the board on its first move;
                    reachable_cells.append((4, col))                            # if both of these cells are valid and empty
            if self.can_hit_on_cell((row-1, col+1)):
                reachable_cells.append((row-1, col+1))      # can hit one cell diagonally 'down' the board
            if self.can_hit_on_cell((row-1, col-1)):        # if this cell has a piece of the opposing colour (white) on it
                reachable_cells.append((row-1, col-1))

        return reachable_cells      # returns the list of reachable cells


class Rook(Piece):  # Turm
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        **TODO** Implement the movability mechanic for `rooks <https://de.wikipedia.org/wiki/Turm_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Rooks can move only horizontally or vertically. They can move an arbitrary amount of cells until blocked by an own piece
        or an opposing piece (which they could hit and then being stopped).

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the rook movability mechanics. 

        :return: A list of reachable cells this rook could move into.
        """
        reachable_cells = []        # creation of a list that should contain all the cells the rook can reach in its next move
        row, col = self.cell        # unpacking of the current position of the rook in row and colum (col)

        # the rook moves vertically or horizontally

       #vertikale Bewegung

        for r in range(row+1, 8):           # iteration vertically 'up' the board
        
            if self.board.cell_is_valid_and_empty((r, col)):    # check if the cell is valid and empty
                reachable_cells.append((r, col))                # if v and e; append cell and continue iteration
            elif self.can_hit_on_cell((r, col)):                # if not v and e; check if the rook can hit on this cell an opponent
                reachable_cells.append((r, col))
                break                                           # if rook can hit; append the cell and break
            else:                                               # if not v and e + rook can't hit; break
                break
                
        for r in reversed(range(0, row)):   # iteration vertically 'down' the board
        
            if self.board.cell_is_valid_and_empty((r, col)):
                reachable_cells.append((r, col))
            elif self.can_hit_on_cell((r, col)):
                reachable_cells.append((r, col))
                break
            else:
                break

        #horizontale Bewegung

        for c in reversed(range(0, col)):   # iteration horizontally to the 'left' on the board
        
            if self.board.cell_is_valid_and_empty((row, c)):
                reachable_cells.append((row, c))
            elif self.can_hit_on_cell((row, c)):
                reachable_cells.append((row, c))
                break
            else:
                break
        
        for c in range(col+1, 8):           # iteration horizontally to the 'right' on the board
        
            if self.board.cell_is_valid_and_empty((row, c)):
                reachable_cells.append((row, c))
            elif self.can_hit_on_cell((row, c)):
                reachable_cells.append((row, c))
                break
            else:
                break
                
        return reachable_cells              # returns the list of reachable cells


class Knight(Piece):  # Springer
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        **TODO** Implement the movability mechanic for `knights <https://de.wikipedia.org/wiki/Springer_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Knights can move in a special pattern. They can move two rows up or down and then one column left or right. Alternatively, they can
        move one row up or down and then two columns left or right. They are not blocked by pieces in between. 

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the rook movability mechanics. 

        :return: A list of reachable cells this knight could move into.
        """
        reachable_cells = []                # creation of a list that should contain all the cells the knight can reach in its next move
        row, col = self.cell                # unpacking of the current position of the knight in row and colum (col)

        # Movement pattern of the knight is an "L"-Shape (two cells vertically/horizontally and one cell horizontally/vertically)

        # 'bw' Bewegung
        if self.can_enter_cell((row-2, col+1)):         # checks if the knight can enter the cell 'down' the board to the 'right' 
            reachable_cells.append((row-2, col+1))      # can enter cell = valid cell, which is empty or contains an opposing piece

        if self.can_enter_cell((row-2, col-1)):         # checks if the knight can enter the cell 'down' the board to the 'left'
            reachable_cells.append((row-2, col-1))

        # 'fw' Bewegung                                 # checks if the knight can enter the cells 'up' the board, to the 'right' or 'left'
        if self.can_enter_cell((row+2, col+1)):
            reachable_cells.append((row+2, col+1))

        if self.can_enter_cell((row+2, col-1)):
            reachable_cells.append((row+2, col-1))

        # 'li' Bewegung                                 # checks if the knight can enter the cells to the 'left', 'up' or 'down' the board
        if self.can_enter_cell((row+1, col-2)):
            reachable_cells.append((row+1, col-2))

        if self.can_enter_cell((row-1, col-2)):
            reachable_cells.append((row-1, col-2))

        # 'rt' Bewegung                                 # checks if the knight can enter the cells to the 'right', 'up' or 'down' the board
        if self.can_enter_cell((row+1, col+2)):
            reachable_cells.append((row+1, col+2))

        if self.can_enter_cell((row-1, col+2)):
            reachable_cells.append((row-1, col+2))

        return reachable_cells              # returns the list of reachable cells


class Bishop(Piece):  # Läufer
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        **TODO** Implement the movability mechanic for `bishop <https://de.wikipedia.org/wiki/L%C3%A4ufer_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Bishops can move diagonally an arbitrary amount of cells until blocked.

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the rook movability mechanics. 

        :return: A list of reachable cells this bishop could move into.
        """
        reachable_cells = []            # creation of a list that should contain all the cells the bishop can reach in its next move
        row, col = self.cell            # unpacking of the current position of the bishop in row and colum (col)

        # the bishop can move diagonally

        # 'fw-rt' Bewegung                                              # movement diagonally 'up' the board and to the 'right'
        cols = col
        for diagonal_r in range(row+1, 8):                              # iteration 'up' the board (row+1)
            cols = cols + 1                                             # each iteration step also one cell to the 'right' (cols+1)
            if self.board.cell_is_valid_and_empty((diagonal_r, cols)):  # check if the cell is valid and empty
                reachable_cells.append((diagonal_r, cols))              # if v and e; append cell and continue iteration
            elif self.can_hit_on_cell((diagonal_r, cols)):              # if not v and e; check if the bishop can hit on this cell an opponent
                reachable_cells.append((diagonal_r, cols))
                break                                                   # if bishop can hit; append the cell and break
            else:                                                       # if not v and e + bishop can't hit; break
                break

        # 'bw-rt' Bewegung                                              # movement diagonally 'down' the board and to the 'right'
        cols = col
        for diagonal_r in reversed(range(0, row)):                      # iteration 'down' the board (row-1)
            cols = cols + 1                                             # each iteration step also one cell to the 'right' (cols+1)
            if self.board.cell_is_valid_and_empty((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
            elif self.can_hit_on_cell((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
                break
            else:
                break

        # 'fw-li' Bewegung                                              # movement diagonally 'up' the board and to the 'left'
        cols = col
        for diagonal_r in range(row+1, 8):                              # iteration 'up' the board (row+1)
            cols = cols - 1                                             # each iteration step also one cell to the 'left' (cols-1)
            if self.board.cell_is_valid_and_empty((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
            elif self.can_hit_on_cell((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
                break
            else:
                break

        # 'bw-li' Bewegung                                              # movement diagonally 'down' the board and to the 'left'
        cols = col
        for diagonal_r in reversed(range(0, row)):                      # iteration 'down' the board (row-1)
            cols = cols - 1                                             # each iteration step also one cell to the 'left' (cols-1)
            if self.board.cell_is_valid_and_empty((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
            elif self.can_hit_on_cell((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
                break
            else:
                break
                
        return reachable_cells              # returns the list of reachable cells


class Queen(Piece):  # Königin
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        **TODO** Implement the movability mechanic for the `queen <https://de.wikipedia.org/wiki/Dame_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Queens can move horizontally, vertically and diagonally an arbitrary amount of cells until blocked. They combine the movability
        of rooks and bishops. 

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the rook movability mechanics. 

        :return: A list of reachable cells this queen could move into.
        """
        reachable_cells = []            # creation of a list that should contain all the cells the queen can reach in its next move
        row, col = self.cell            # unpacking of the current position of the queen in row and colum (col)

        # the queen can move horizontally, vertically or diagonally

        #vertikale Bewegung

        for r in range(row+1, 8):           # iteration vertically 'up' the board
        
            if self.board.cell_is_valid_and_empty((r, col)):
                reachable_cells.append((r, col))
            elif self.can_hit_on_cell((r, col)):
                reachable_cells.append((r, col))
                break
            else:
                break
                
        for r in reversed(range(0, row)):   # iteration vertically 'down' the board
        
            if self.board.cell_is_valid_and_empty((r, col)):
                reachable_cells.append((r, col))
            elif self.can_hit_on_cell((r, col)):
                reachable_cells.append((r, col))
                break
            else:
                break

        #horizontale Bewegung

        for c in reversed(range(0, col)):   # iteration horizontally to the 'left'
        
            if self.board.cell_is_valid_and_empty((row, c)):
                reachable_cells.append((row, c))
            elif self.can_hit_on_cell((row, c)):
                reachable_cells.append((row, c))
                break
            else:
                break
        
        for c in range(col+1, 8):           # iteration horizontally to the 'right'
        
            if self.board.cell_is_valid_and_empty((row, c)):
                reachable_cells.append((row, c))
            elif self.can_hit_on_cell((row, c)):
                reachable_cells.append((row, c))
                break
            else:
                break
                
        # 'fw-rt' Bewegung                  # movement diagonally 'up' the board and to the 'right'
        cols = col
        for diagonal_r in range(row+1, 8):
            cols = cols + 1
            if self.board.cell_is_valid_and_empty((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
            elif self.can_hit_on_cell((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
                break
            else:
                break

        # 'bw-rt' Bewegung                  # movement diagonally 'down' the board and to the 'right'
        cols = col
        for diagonal_r in reversed(range(0, row)):
            cols = cols + 1
            if self.board.cell_is_valid_and_empty((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
            elif self.can_hit_on_cell((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
                break
            else:
                break

        # 'fw-li' Bewegung                  # movement diagonally 'up' the board and to the 'left'
        cols = col
        for diagonal_r in range(row+1, 8):
            cols = cols - 1
            if self.board.cell_is_valid_and_empty((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
            elif self.can_hit_on_cell((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
                break
            else:
                break

        # 'bw-li' Bewegung                  # movement diagonally 'down' the board and to the 'left'
        cols = col
        for diagonal_r in reversed(range(0, row)):
            cols = cols - 1
            if self.board.cell_is_valid_and_empty((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
            elif self.can_hit_on_cell((diagonal_r, cols)):
                reachable_cells.append((diagonal_r, cols))
                break
            else:
                break

        return reachable_cells          # returns the list of reachable cells


class King(Piece):  # König
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        **TODO** Implement the movability mechanic for the `king <https://de.wikipedia.org/wiki/K%C3%B6nig_(Schach)>`_. 

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Kings can move horizontally, vertically and diagonally but only one piece at a time.

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`, 
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>` 
        to check for necessary conditions to implement the rook movability mechanics. 

        :return: A list of reachable cells this king could move into.
        """
        reachable_cells = []            # creation of a list that should contain all the cells the king can reach in its next move
        row, col = self.cell            # unpacking of the current position of the king in row and colum (col)

        # the king can move one cell in any direction (horizontally, vertically, diagonally)

        for i_r in range(-1,2):                                 # iteration over [-1, 0, 1] = summand to the row
            for i_c in range(-1,2):                             # iteration over [-1, 0, 1] = summand to the colum
                if i_r == 0 and i_c == 0:                       # if both summands are 0 -> continue iteration; (bc (row+0, col+0) == current position)
                    continue
                if self.can_enter_cell((row+i_r, col+i_c)):     # checks if the king can enter the cell
                    reachable_cells.append((row+i_r, col+i_c))  # can enter cell = valid cell, which is empty or contains an opposing piece

        return reachable_cells          # returns the list of reachable cells
