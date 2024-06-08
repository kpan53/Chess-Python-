"""
- The Driver File
- Handles User Input
- Display Current Game State object
"""

import pygame as p
from Chess import ChessEngine

p.init()
WIDTH = HEIGHT = 512 # or 400 are good resolutions
DIMENSION = 8 # 8x8 Board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #For animations
IMAGES = {}

'''
Only want to render images once
Will initialze a global dictionary of images
Will be called exactly once within main
'''

def loadImages():
    pieces = ['wP', 'wR', 'wB', 'wN', 'wK', 'wQ', 'bP', 'bR', 'bB', 'bN', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # We can access an image by --> IMAGES['wP']


'''
The main driver
- Will handle User Input
_ Will handle updating graphics
'''


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gameState = ChessEngine.GameState()
    validMoves = gameState.getValidMoves()
    moveMade = False #Flag Variable for when a VALID move is made
    loadImages() #Done only once since before loop

    running = True
    sqSelected = () # No square initially selected, keeps track of the last click of the user (tuple: (row, col))
    playerClicks = [] #Keeps track of player clicks (two tuples: [(6,4), (4,4)])
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x,y) location of mouse
                row = location[1] // SQ_SIZE
                col = location[0]//SQ_SIZE
                '''
                if gameState.board[row, col] == "--" and len(playerClicks) == 0:
                    continue
                '''
                if sqSelected == (row,col): #the user clicked the same square again
                    sqSelected = () #Deselects
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) #Append for both first and second clicks
                if len(playerClicks) == 2: #After the second click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gameState.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        gameState.makeMove(move)
                        moveMade = True
                        sqSelected = () #Rest user clicks
                        playerClicks = []
                    else:
                        playerClicks = [sqSelected]

            #Key Handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #Undo when 'z' is pressed
                    gameState.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gameState.getValidMoves()
            moveMade = False
        drawGameState(screen, gameState)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Responsible for graphics within a current gameState
'''
def drawGameState(screen, gameState):
    drawBoard(screen) #Draws squares on the board
    drawPieces(screen, gameState.board) #Draw pieces on top of board

'''
Draw the squares on the baord
'''
def drawBoard(screen):
    colors = [p.Color("light gray"), p.Color("dark green")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row+col) % 2)]
            p.draw.rect(screen, color, p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the pieces on the board using the GameState.board
'''
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--": #Not an empty square
                #Used to draw an image over an image
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
