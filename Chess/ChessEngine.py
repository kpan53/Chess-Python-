"""
- Responsible for storing all the info about the current state of a chess game
- Responsible for finding the valid moves at a current state
- Responsible for keeping a move log
"""


class GameState():
    def __init__(self):
        #Each element has 2 characters
        #First character represents color of the piece
        #Second character determines the type of the piece
        # "--" represents an empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        # Keep track of kings here so that its easier to look for checks/checkmates
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        '''
        self.checkMate = False
        self.staleMate = False
        '''
        self.inCheck = False
        self.pins = []
        self.checks = []


    '''
    Takes a move as a param and execute the move (won't work with castling, pawn promotions, and en-passant)
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #Log move so it can be undone later, can assume this move is legal
        self.whiteToMove = not self.whiteToMove #Swap Players
        # Update the kings location if moves
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # Update Kings position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

    '''
    Consider a pin against a King, the opponents piece that is pinned will see many "legal" moves it
    can make, but they're all invalid because the piece itself doesn't know that it's pinned against 
    its own King.
    This is why we make the distinction between valid moves and all possible moves.
    '''
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: # There is only 1 check. Can block it or move the king
                moves = self.getAllPossibleMoves()
                # To block a check we have to move a piece into one of the squares between the enemy piece and the King
                check = self.checks[0] # Info about the check
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] # The enemy piece that is causing the check
                validSquares = [] # Any squares that piece can move to
                # If the enemy piece is a Knight, must take or move King, anything else can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8): # Produces a list of coords that result in blocking the check
                        # Can move along the direction of the attacking piece until you hit the attacking piece
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) # check[2] and check [3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: # Where we hit the attacking piece
                            break
                # Get rid of moves that don't block check or move the King
                for i in range(len(moves) -1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K': # The move doesn't move the King so it HAS to block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: # Move doesn't block check or capture the piece
                            moves.remove((moves[i]))
            else: # It's a double check and the King has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: # Not in check so any move is fine
            moves = self.getAllPossibleMoves()

        return moves

    def checkForPinsAndChecks(self):
        pins = [] # Square where the allied pinned piece is and direction pinned from
        checks = [] # Squares where the enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            allyColor = "w"
            enemyColor = "b"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            allyColor = "b"
            enemyColor = "w"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # Check outwards from King for pins and checks, keep track of the pins
        directions = ((-1, -0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () # Reset Possible Pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == (): # This means that the allied piece could possibly be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break # Second allied piece, so no pin or check possible from this direction
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1] # The type of the piece we are working with, knights done seperately
                        # 1.) Orthogonally away from king and piece is a Rook
                        # 2.) Diagonally away and piece is a Bishop
                        # 3.) 1 square away diagonally and piece is a Pawn
                        # 4.) Any direction and piece is a Queen
                        # 5.) Any direction 1 square away from and piece is a King (Kings can't walk into each other)
                        # Note: Doing these conditionals is MUCH faster than generating all possible moves
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): # This mean no piece is blocking, so in check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: # A piece is blocking the pin
                                pins.append(possiblePin)
                                break
                        else: # Enemy Piece isn't applying a check
                            break
                else:
                    break # Off the board
        # Check for Knight moves
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': # Enemy Knight attacking King
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    '''
    Determines if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    '''
    Determines if the enemy can attack the square
    '''
    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove # Switch to opp pov
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # Switch back
        for move in oppMoves:
            if move.endRow == row and move.endCol == col: # Square is under attack
                return True
        return False

    '''
    All legal moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])): # Number of cols in a given row
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves) # Will call move function based on piece types
        return moves

    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if self.board[row - 1][col] == "--": # A 1 square move
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((row, col), (row - 1, col), self.board))
                    if row == 6 and self.board[row - 2][col] == "--": # A 2 square move
                        moves.append(Move((row, col), (row - 2, col), self.board))
            # Capturing
            if col - 1 >= 0: # Capture to the left
                if self.board[row - 1][col - 1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, -1): # Can move in the direction of the pin
                        moves.append(Move((row, col), (row - 1, col - 1), self.board))
            if col + 1 <= 7: # Capture to the right
                if self.board[row - 1][col + 1] == 'b':
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((row, col), (row - 1, col + 1), self.board))
        else: # Black Pawn moves
            if self.board[row + 1][col] == "--": # 1 square move
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    if row == 1 and self.board[row + 2][col] == "--":
                        moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0: # Capture to the left
                if self.board[row + 1][col - 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7: # Capture to the right
                if self.board[row + 1][col + 1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((row, col), (row + 1, col + 1), self.board))

    '''
    Get Rook moves given starting square, append to "moves"
    '''
    def getRookMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q': # Can't remove Queen from pin on rook moves, only on Bishop moves
                    self.pins.remove(self.pins[i])
                    break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # On the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": # Empty space and is valid
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: # Enemy piece and is valid
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else: # Friendly piece and Invalid
                            break
                    else: #  It's off the board
                        break

    '''
    Get Bishop moves given start square, append to "moves"
    '''
    def getBishopMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q': # Can't remove Queen from pin on rook moves, only on Bishop moves
                    self.pins.remove(self.pins[i])
                    break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # On the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": # Empty space and is valid
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: # Enemy piece and is valid
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else: # Friendly piece and Invalid
                            break
                    else: #  It's off the board
                        break


    '''
    Get Knight moves given start square, append to "moves"
    '''
    def getKnightMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for m in knightMoves:
            endRow = row + m[0]
            endCol = row + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # On the board
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == enemyColor: # Not an ally piece (Empty or Enemy square)
                        moves.append(Move((row, col), (endRow, endCol), self.board))


    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = col + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # Not an ally piece (empty or enemy piece)
                    if allyColor == "w": # Place King on end square and check for checks
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    # Place King back at original location
                    if allyColor == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)




'''
Creating a Move class helps to create chess notation, and deal with castling, en passant, etc.'''
class Move():

    # maps keys to value
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol #Kind of like a Hash function

    '''
    Overriding the Equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
