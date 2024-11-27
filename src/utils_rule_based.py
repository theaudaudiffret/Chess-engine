import chess

from IPython.display import SVG, display


# Quelques mouvements classiques de l'ouverture prédéfinis
réponses_prédéfinies={}
r={"rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "e7e5",#e2e4 -- e7e5
                      "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2":"b8c6",#Cf3 -- Cc6
                      "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3":"f8c5", #Fc4 -- Fc5
                      "rnbqkbnr/pppp1ppp/8/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR b KQkq - 1 2":"g8f6", # Cf3-- Cf6
                      "rnbqkbnr/pppp1ppp/8/4p3/4P3/2N5/PPPP1PPP/R1BQKBNR b KQkq - 1 2":"g8f6", # Cc3 -- CF6
                      "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R b KQkq - 3 3":"b8c6", # 4 cavaliers
                      "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R b KQkq - 3 3":"g8f6", # 4 cav
                      "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R b KQkq - 5 4":"f8c5" #4 cav + fous
                      }


# Définition du centre de l'échiquier
CENTER = {chess.D5, chess.D4, chess.E4, chess.D5}

#attribue des bonus et malus en fonctions de règles
def evaluate_board_rule(board):
    evaluation = 0
    
    evaluation += evaluation_pieces(board)

    evaluation += controle_centre(board)

    #evaluation += activite_pieces(board)

    evaluation+= roque(board)

    evaluation +=attaques_et_defenses(board)
    
    return evaluation


def evaluation_pieces(board):
    evaluation=0
    # Développement des pièces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        value = 100 if piece.color == chess.BLACK else -100
        if piece.piece_type == chess.PAWN:
            evaluation += value * 1 
        elif piece.piece_type == chess.KNIGHT:
            evaluation += value * 3 
        elif piece.piece_type == chess.BISHOP:
            evaluation += value * 3 
        elif piece.piece_type == chess.ROOK:
            evaluation += value * 5 
        elif piece.piece_type == chess.QUEEN:
            evaluation += value * 9 
        elif piece.piece_type == chess.KING:
            evaluation += value * 100
    return evaluation

def controle_centre(board):
     # Contrôle du centre
    center_control_score = (sum(1 if square in CENTER else 0 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.BLACK) - sum(1 if square in CENTER else 0 for square in chess.SQUARES if board.piece_at(square) and board.piece_at(square).color == chess.WHITE))*50

    return(center_control_score)

def roque(board):
    # Bonus pour roquer
    roque_score = 0
    if board.fullmove_number < 10:
        if board.has_kingside_castling_rights(chess.WHITE) and board.king(chess.WHITE)==chess.G1:
            roque_score -= 100
        elif board.has_kingside_castling_rights(chess.WHITE) and not(board.king(chess.WHITE)==chess.G1):
            roque_score += 50
        if board.has_kingside_castling_rights(chess.BLACK) and board.king(chess.BLACK)==chess.G8:
            roque_score += 100
        elif board.has_kingside_castling_rights(chess.BLACK) and not(board.king(chess.BLACK)==chess.G8):
            roque_score -= 50
    return roque_score

def attaques_et_defenses(board):
    # Bonus accordé si une pièce est bien défendue
    bonus_defense = 5 
    malus_defense = -10
    eval = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        # Calcul du nombre d'attaques sur la pièce
        attacks = len(board.attackers(not piece.color, square))

        defenses = len(board.attackers(piece.color, square))

        # Bonus si une pièce est bien défendue, malus sinon
        if piece.color == chess.BLACK:
            eval += (defenses - attacks) * bonus_defense if defenses >= attacks else (defenses - attacks) * malus_defense
        elif piece.color == chess.WHITE:
            eval += (defenses - attacks) * (-bonus_defense) if defenses >= attacks else (defenses - attacks) * (-malus_defense)

    return eval



def alpha_beta_rule(position, depth, alpha=float('-inf'), beta=float('inf')):
    if depth == 0 :
        return evaluate_board_rule(position)
    else:
        if position.turn == chess.BLACK:
            for move in position.legal_moves:
                position.push(move)
                value = alpha_beta_rule(position, depth - 1, -beta, -alpha)
                position.pop()  # Undo the move
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return alpha
        if position.turn == chess.WHITE:
            for move in position.legal_moves:
                position.push(move)
                value = alpha_beta_rule(position, depth - 1, -beta, -alpha)
                position.pop()  # Undo the move
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return beta
        
def play_nn(fen, depth):
    board = chess.Board(fen=fen)
    best_move_score=float("-inf")
    for move in board.legal_moves:
        candidate_board=board.copy()
        candidate_board.push(move)
        candidate_move_score = alpha_beta_rule(position=candidate_board, depth=depth)
        if candidate_move_score > best_move_score:
            best_move=move
            best_move_score=candidate_move_score
    print(f'{best_move}: {best_move_score}')
    return str(best_move)
def play_game(ai_function, depth):
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
            if board.fen() in réponses_prédéfinies.keys():
                ai_move = réponses_prédéfinies[str(board.fen())]
                print(f'AI move: {ai_move}')
                board.push_san(ai_move)
            else:
                ai_move = ai_function(board.fen(), depth)
                print(f'AI move: {ai_move}')
                board.push_san(ai_move)
                # print(board.fen())
                # break
    print(board.outcome())