import argparse
import glob
import json
import os
import random

from dotenv import load_dotenv
import chess
from stockfish import Stockfish



load_dotenv(dotenv_path="src/config/.env")  # Charge les variables d'environnement depuis le fichier .env
path_stockfish = os.getenv("PATH_STOCKFISH")

def configure_stockfish(path, elo, depth, threads, min_time):
    return Stockfish(
        path=path,
        parameters={
            "Threads": threads,
            "Minimum Thinking Time": min_time
        }
    ), elo, depth

def checkEndCondition(board):
    return (board.is_checkmate() or board.is_stalemate() or 
            board.is_insufficient_material() or board.can_claim_threefold_repetition() or 
            board.can_claim_fifty_moves() or board.can_claim_draw())

def findNextIdx():
    files = glob.glob(r"data/*.json")
    if len(files) == 0:
        return 1  # if no files, return 1
    highestIdx = max(int(f.split("MovesAndPositions")[-1].split(".json")[0]) for f in files)
    return highestIdx + 1

def saveData(moves, positions, evaluations):
    MovesAndPositions = [{"move": move, "evaluation": evaluation, "position": position} for move, evaluation ,position in zip(moves, evaluations, positions)]
    nextIdx = findNextIdx()
    with open(f"data/MovesAndPositions{nextIdx}.json", "w") as json_file:
        json.dump(MovesAndPositions, json_file)
    print(f"Game {nextIdx} saved successfully.")

def getRandomMove(board):
    legal_moves = list(board.legal_moves)
    return random.choice(legal_moves).uci()

def evaluate_position(stockfish, fen):
    stockfish.set_fen_position(fen)
    return stockfish.get_evaluation()["value"]





def mineGames(numGames: int, maxMoves: int, stockfish, stockfish_evaluator):
    for i in range(numGames):
        currentGameMoves = []
        currentGamePositions = []
        evaluations = []
        board = chess.Board()
        stockfish.set_position([])
        
        for _ in range(maxMoves):
            if board.turn == chess.WHITE:  # White's turn
                move = stockfish.get_best_move()
            elif board.turn == chess.BLACK:  # Black's turn
                move = stockfish.get_best_move()
                
            currentGamePositions.append(board.fen())
            board.push_uci(move)
            currentGameMoves.append(move)
            stockfish.set_position(currentGameMoves)
            evaluation = - evaluate_position(stockfish_evaluator, board.fen())
            evaluations.append(evaluation)
            
            if checkEndCondition(board):
                print("Game is over")
                break
        
        saveData(currentGameMoves, currentGamePositions, evaluations)

# Parse arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mine chess games and save data.")
    
    # Game configuration
    parser.add_argument("--numGames", type=int, default=20, help="Number of games to mine.")
    parser.add_argument("--maxMoves", type=int, default=500, help="Maximum moves per game.")
    
    # Stockfish configuration
    parser.add_argument("--elo", type=int, default=2000, help="ELO rating of Stockfish player.")
    parser.add_argument("--evaluatorElo", type=int, default=4500, help="ELO rating of evaluation Stockfish.")
    parser.add_argument("--depth", type=int, default=1, help="Search depth of Stockfish.")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads for Stockfish.")
    parser.add_argument("--minTime", type=int, default=30, help="Minimum thinking time for Stockfish (ms).")
    
    args = parser.parse_args()

    # Initialize Stockfish engines
    stockfish, elo, depth = configure_stockfish(path_stockfish, args.elo, args.depth, args.threads, args.minTime)
    stockfish.set_elo_rating(elo)
    stockfish.set_depth(depth)

    stockfish_evaluator, evaluator_elo, _ = configure_stockfish(path_stockfish, args.evaluatorElo, args.depth, args.threads, args.minTime)
    stockfish_evaluator.set_elo_rating(evaluator_elo)
    stockfish_evaluator.set_depth(depth)

    # Mine games with provided arguments
    mineGames(args.numGames, args.maxMoves, stockfish, stockfish_evaluator)
