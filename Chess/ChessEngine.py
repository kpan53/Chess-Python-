"""
- Responsible for storing all the info about the current state of a chess game
- Responsible for finding the valid moves at a current state
- Responsible for keeping a move log
"""


class GameState():
    def __init__(self):
        # Each element has 2 characters
        # First character represents color of the piece
        # Second character determines the type of the piece
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
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enPassantPossible = () # Coordinates for the square where an en passant capture is possible
        # Not if it's possible, just have you broken the rules fro castling before checking
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.whiteKingSide, self.currentCastlingRights.blackKingSide,
                                                   self.currentCastlingRights.whiteQueenSide, self.currentCastlingRights.blackQueenSide)]


    '''
    Takes a move as a param and execute the move (won't work with castling, pawn promotions, and en-passant)
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # Log move so it can be undone later, can assume this move is legal
        self.whiteToMove = not self.whiteToMove # Swap Players
        # Update the kings location if moves
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn promotion
        if move.isPawnPromotion:
            promotedPiece = input("Promote to Q, R, B, or N: ")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

        # En Passant Move
        if move.isEnPassantMove:
            # Need to remove the square behind the pawn
            self.board[move.startRow][move.endCol] = "--" # Capturing the pawn

        # Update EnPassantPossible variable
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2: # Only on 2 square pawn moves
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol) # Some nice math
        else:
            self.enPassantPossible = ()

        # Castle Moves
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # A King side castle
                # Copies Rook into new square
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                # Remove from old square
                self.board[move.endRow][move.endCol + 1] = '--'
            else: # Queen Side
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        # Update Castling Rights -> Whenever a King or Rook moves
        self.updateCastleRights(move)
        self.castleRightsLog.append(
            CastleRights(self.currentCastlingRights.whiteKingSide, self.currentCastlingRights.blackKingSide,
                         self.currentCastlingRights.whiteQueenSide, self.currentCastlingRights.blackQueenSide))


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
            # Undo En Passant move
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = '--' # Leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                # If En Passant move is undone, without having this, wouldn't be able to redo the En Passant move
                self.enPassantPossible = (move.endRow, move.endCol)
            # Undo a 2 square Pawn advance
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()
            # Undo Castling Rights
            self.castleRightsLog.pop() # Get's rid of new castle rights from move being undone
            # Set current castle rights to the last one in the list (last state)
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRights = CastleRights(newRights.whiteKingSide, newRights.blackKingSide,
                                                      newRights.whiteQueenSide, newRights.blackQueenSide)
            # Undo Castle Move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # King Side
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else: # Queen Side
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

    '''
    Update castle rights given a move
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.whiteQueenSide = False
            self.currentCastlingRights.whiteKingSide = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.blackKingSide = False
            self.currentCastlingRights.blackQueenSide = False
        elif move.pieceMoved == 'wR':
            # Have to know which rook was moved
            if move.startRow == 7:
                if move.startCol == 0: # Left Rook
                    self.currentCastlingRights.whiteQueenSide = False
                if move.startCol == 7: # Right Rook
                    self.currentCastlingRights.whiteKingSide = False
        elif move.pieceMoved == 'bR':
            # Have to know which rook was moved
            if move.startRow == 0:
                if move.startCol == 0: # Left Rook
                    self.currentCastlingRights.blackQueenSide = False
                if move.startCol == 7: # Right Rook
                    self.currentCastlingRights.blackKingSide = False
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.whiteQueenSide = False
                elif move.endCol == 7:
                    self.currentCastlingRights.whiteKingSide = False
            elif move.pieceCaptured == 'bR':
                if move.endRow == 0:
                    if move.endCol == 0:
                        self.currentCastlingRights.blackQueenSide = False
                    elif move.endCol == 7:
                        self.currentCastlingRights.blackKingSide = False




    '''
    Consider a pin against a King, the opponents piece that is pinned will see many "legal" moves it
    can make, but they're all invalid because the piece itself doesn't know that it's pinned against 
    its own King.
    This is why we make the distinction between valid moves and all possible moves.
    '''
    def getValidMoves(self):
        for log in self.castleRightsLog:
            print(log.whiteKingSide, log.whiteQueenSide, log.blackKingSide, log.blackQueenSide, end=", ")
        print()
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
                # If no moves in "moves" and in check, then are in checkmate
                if len(moves) == 0:
                    self.checkmate = True
            else: # It's a double check and the King has to move
                self.getKingMoves(kingRow, kingCol, moves)
                # If no moves in "moves" and in check, then are in checkmate
                if len(moves) == 0:
                    self.checkmate = True
        else: # Not in check so any move is fine
            moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves, "w")
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves, "b")
        # If not in check, but can't make any moves, it's stalemate
        if not self.inCheck and len(moves) == 0:
            self.stalemate = True
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
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
        pawnPromotion = False

        if self.board[row + moveAmount][col] == "--": # 1 Square Move
            if not piecePinned or pinDirection == (moveAmount, 0):
                if row + moveAmount == backRow: # If piece get to bank rank then it's a pawn promotion
                    pawnPromotion = True
                moves.append(Move((row, col), (row + moveAmount, col), self.board, pawnPromotion=pawnPromotion))
                if row == startRow and self.board[row + (2 * moveAmount)][col] == "--":
                    moves.append(Move((row, col), (row + (2 * moveAmount), col), self.board))
        if col - 1 >= 0: # Capture to the left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][col - 1][0] == enemyColor:
                    if row + moveAmount == backRow: # Pawn Promotion
                        pawnPromotion = True
                    moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, pawnPromotion=pawnPromotion))
                if (row + moveAmount, col - 1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, enPassant=True))
        if col + 1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[row + moveAmount][col + 1][0] == enemyColor:
                    if row + moveAmount == backRow: # Pawn Promotion
                        pawnPromotion = True
                    moves.append(Move((row, col), (row + moveAmount, col + 1), self.board, pawnPromotion=pawnPromotion))
                if (row + moveAmount, col + 1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row + moveAmount, col + 1), self.board, enPassant=True))

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
                    else: # It's off the board
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
                    else: # It's off the board
                        break


    '''
    Get Knight moves given start square, append to "moves"
    '''
    def getKnightMoves(self, row, col, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = row + m[0]
            endCol = col + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # On the board
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: # Not an ally piece (Empty or Enemy square)
                        moves.append(Move((row, col), (endRow, endCol), self.board))


    '''
    Get Queen moves given start square, append to "moves"
    '''
    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    '''
    Get King moves given start square, append to "moves"
    '''
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
    Generates all valid castle moves for king at (row, col), and add to list of moves'''
    def getCastleMoves(self, row, col, moves, allyColor):
        if self.squareUnderAttack(row, col):
            return # Can't castle while in check
        if ((self.whiteToMove and self.currentCastlingRights.whiteKingSide) or
                (not self.whiteToMove and self.currentCastlingRights.blackKingSide)):
            self.getKingSideCastleMoves(row, col, moves, allyColor)
        if ((self.whiteToMove and self.currentCastlingRights.whiteQueenSide) or
                (not self.whiteToMove and self.currentCastlingRights.blackQueenSide)):
            self.getQueenSideCastleMoves(row, col, moves, allyColor)

    def getKingSideCastleMoves(self, row, col, moves, allyColor):
        # Don't need to check if moves are offboard because otherwise castlingRights wouldn't be True
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, row, col, moves, allyColor):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))





class CastleRights:
    def __init__(self, whiteKingSide, blackKingSide, whiteQueenSide, blackQueenSide):
        self.whiteKingSide = whiteKingSide
        self.blackKingSide = blackKingSide
        self.whiteQueenSide = whiteQueenSide
        self.blackQueenSide = blackQueenSide


'''
Creating a Move class helps to create chess notation, and deal with castling, en passant, etc.'''
class Move():

    # maps keys to value
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant = False, pawnPromotion=False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Pawn Promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7):
            # Pawn made it to the end
            self.isPawnPromotion = True
        # En Passant
        self.isEnPassantMove = enPassant
        if self.isEnPassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'
        # Castle Moves
        self.isCastleMove = isCastleMove

        '''
        self.isEnPassantMove = False
        if self.pieceMoved[1] == 'P' and (self.endRow, self.endCol) == enPassantPossible:
            self.isEnPassantMove = True
        '''

        # Kind of like a Hash Function
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

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


