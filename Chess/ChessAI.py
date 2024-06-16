import random

# global nextMove

# King score doesn't matter, because you can't technically capture the King
pieceScores = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}

knightScores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

bishopScores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 1],
    [3, 4, 3, 2, 2, 3, 4, 1],
    [4, 3, 2, 1, 1, 2, 3, 1]
]

queenScores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1]
]

rookScores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4]
]

whitePawnScores = [
    [9, 9, 9, 9, 9, 9, 9, 9],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

blackPawnScores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [9, 9, 9, 9, 9, 9, 9, 9]
]

piecePositionScores = {"N": knightScores, "B": bishopScores, "Q": queenScores,
                      "R": rookScores, "bP": blackPawnScores, "wP": whitePawnScores}

CHECKMATE = 1000 # Worth the most since it wins the game
STALEMATE = 0 # Always better than a losing position
DEPTH = 4

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMoveMinMaxNoRecursion(gameState, validMoves):
    turnMultiplier = 1 if gameState.whiteToMove else -1
    opponentsMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves) # Prevents AI from picking the same move to make
    for playerMove in validMoves:
        gameState.makeMove(playerMove)
        opponentsMoves = gameState.getValidMoves() # Inefficient, but gameState won't change until we call this
        if gameState.stalemate:
            opponentsMaxScore = STALEMATE
        elif gameState.checkmate:
            opponentsMaxScore = -CHECKMATE
        else:
            opponentsMaxScore = -CHECKMATE
            for opponentsMove in opponentsMoves:
                gameState.makeMove(opponentsMove)
                gameState.getValidMoves()
                if gameState.checkmate:
                    score = CHECKMATE
                elif gameState.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gameState.board) # Will be really good for black if negative
                if score > opponentsMaxScore:
                    opponentsMaxScore = score
                gameState.undoMove()
        if opponentsMaxScore < opponentsMinMaxScore:
            opponentsMinMaxScore = opponentsMaxScore
            bestPlayerMove = playerMove
        gameState.undoMove()
    return bestPlayerMove

'''
Will call the initial recursive call to this value and then return
'''
def findBestMove(gameState, validMoves):
    global nextMove, counter
    nextMove = None # Pick Random move
    random.shuffle(validMoves)
    counter = 0
    # findMoveMinMax(gameState, validMoves, DEPTH, gameState.whiteToMove)
    # findMoveNegaMax(gameState, validMoves, DEPTH, 1 if gameState.whiteToMove else -1)
    findMoveNegaMaxAlphaBeta(gameState, validMoves, DEPTH, -CHECKMATE, CHECKMATE,  1 if gameState.whiteToMove else -1)
    print(counter)
    return nextMove


def findMoveMinMax(gameState, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gameState.board)\

    if whiteToMove: # Maximize
        maxScore = -CHECKMATE
        for move in validMoves:
            gameState.makeMove(move)
            nextMoves = gameState.getValidMoves()
            score = findMoveMinMax(gameState, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH: # Worked back up the tree and are at max depth
                    nextMove = move
            gameState.undoMove()
        return maxScore
    else: # Minimize
        minScore = CHECKMATE
        for move in validMoves:
            gameState.makeMove(move)
            nextMoves = gameState.getValidMoves()
            score = findMoveMinMax(gameState, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gameState.undoMove()
        return minScore


'''
Cleaner way to implement MinMax alg.
'''
def findMoveNegaMax(gameState, validMoves, depth, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gameState)

    maxScore = -CHECKMATE
    for move in validMoves:
        gameState.makeMove(move)
        nextMoves = gameState.getValidMoves()
        score = -findMoveNegaMax(gameState, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gameState.undoMove()
    return maxScore

'''
Alpha-Beta pruned
'''
def findMoveNegaMaxAlphaBeta(gameState, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gameState)

    # Move Ordering - Implement Later
    maxScore = -CHECKMATE
    for move in validMoves:
        gameState.makeMove(move)
        nextMoves = gameState.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gameState, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gameState.undoMove()
        if maxScore > alpha: # Prune
            alpha = maxScore
        if alpha >= beta: # Already found a better move so don't explore
            break
    return maxScore


'''
A positive score = good for White
A negative score = good for Black
'''
def scoreBoard(gameState):
    if gameState.checkmate:
        if gameState.whiteToMove:
            return -CHECKMATE # Black Wins
        else:
            return CHECKMATE # White Wins
    elif gameState.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gameState.board)):
        for col in range(len(gameState.board[row])):
            square = gameState.board[row][col] # The piece
            if square != "--":
                # Positional Scoring
                piecePositionScore = 0
                if square[1] != "K": # Can do this because no position table for King
                    if square[1] == "P": # For Pawns
                        piecePositionScore = piecePositionScores[square][row][col]
                    else: # Any other piece
                        piecePositionScore = piecePositionScores[square[1]][row][col]

                if square[0] == 'w':
                    score += pieceScores[square[1]] + piecePositionScore * .1

                elif square[0] == 'b':
                    score -= pieceScores[square[1]] + piecePositionScore * .1

    return score


'''
Score board based on material
'''


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScores[square[1]]
            elif square[0] == 'b':
                score -= pieceScores[square[1]]

    return score

