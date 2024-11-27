import chess
import numpy as np

from IPython.display import SVG, display


squares_index={
    "a":0,
    "b":1,
    "c":2,
    "d":3,
    "e":4,
    "f":5,
    "g":6,
    "h":7
}
def square_to_index(square):
    letter = chess.square_name(square)
    return 8 - int(letter[1]), squares_index[letter[0]]

def split_dims(fen):
    # this is the 3d matrix
    board3d = np.zeros((14, 8, 8), dtype=np.int8)

    board = chess.Board(fen=fen)

    # here we add the pieces's view on the matrix
    for piece in chess.PIECE_TYPES:
        for square in board.pieces(piece, chess.WHITE):
            idx = np.unravel_index(square, (8, 8))
            board3d[piece - 1][7 - idx[0]][idx[1]] = 1
        for square in board.pieces(piece, chess.BLACK):
            idx = np.unravel_index(square, (8, 8))
            board3d[piece + 5][7 - idx[0]][idx[1]] = 1
 # so the network knows what is being attacked
    aux = board.turn
    board.turn = chess.WHITE
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[12][i][j] = 1
    board.turn = chess.BLACK
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[13][i][j] = 1
    board.turn = aux

    return board3d

def evaluate_board(model, position):
    input_vector = split_dims(position)
    return float(model.predict(np.expand_dims(input_vector, axis=0), verbose=0)[0][0])

def alpha_beta_deep(model, position, depth, alpha=float('-inf'), beta=float('inf')):
    fen=position.fen()
    if depth == 0 :
        return evaluate_board(model, fen)
    else:
        if position.turn == chess.BLACK:
            for move in position.legal_moves:
                position.push(move)
                value = alpha_beta_deep(model, position, depth - 1, -beta, -alpha)
                position.pop()  # Undo the move
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return alpha
        if position.turn == chess.WHITE:
            for move in position.legal_moves:
                position.push(move)
                value = alpha_beta_deep(model, position, depth - 1, -beta, -alpha)
                position.pop()  # Undo the move
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return beta


def play_nn(model, fen, depth):
    board = chess.Board(fen=fen)
    best_move_score=float("-inf")
    for move in board.legal_moves:
        candidate_board=board.copy()
        candidate_board.push(move)
        
        candidate_move_score = alpha_beta_deep(model, position=candidate_board, depth=depth)
        if candidate_move_score > best_move_score:
            best_move=move
            best_move_score=candidate_move_score
    print(f'{best_move}: {best_move_score}')
    return str(best_move)


def play_game(model, ai_function, depth):
    board = chess.Board()
    while board.outcome() is None:
        # We print out the board as an SVG
        display(SVG(board._repr_svg_()))

        # If it's white's turn, we have the user play
        if board.turn == chess.WHITE:
            user_move = input('Your move: ')
            if user_move == 'quit':
                break
            # The move a user puts in isn't a valid move, we keep prompting them for a valid move
            while user_move not in [str(move) for move in board.legal_moves]:
                print('That wasn\'t a valid move. Please enter a move in Standard Algebraic Notation')
                user_move = input('Your move: ')
            board.push_san(user_move)

        # If it's black's turn, we have the AI play
        elif board.turn == chess.BLACK:
            
            ai_move = ai_function(model, board.fen(), depth)
            print(f'AI move: {ai_move}')
            board.push_san(ai_move)
            # print(board.fen())                
            
            
            # break
    print(board.outcome())

