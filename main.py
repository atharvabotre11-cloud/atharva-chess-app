from fastapi import FastAPI
from pydantic import BaseModel
import chess.pgn
from stockfish import Stockfish
import io

app = FastAPI(title="Atharva.com Chess Analysis API")

stockfish = Stockfish(path="/usr/bin/stockfish")

class PGNInput(BaseModel):
    pgn: str

@app.post("/analyze_pgn")
def analyze_pgn(data: PGNInput):
    pgn = io.StringIO(data.pgn)
    game = chess.pgn.read_game(pgn)
    board = game.board()

    analysis = []
    move_no = 1

    for move in game.mainline_moves():
        stockfish.set_fen_position(board.fen())
        best_move = stockfish.get_best_move()
        eval_before = stockfish.get_evaluation()

        board.push(move)
        stockfish.set_fen_position(board.fen())
        eval_after = stockfish.get_evaluation()

        move_type = "Good"
        if eval_before["type"] == "cp" and eval_after["type"] == "cp":
            diff = eval_after["value"] - eval_before["value"]
            if diff < -300:
                move_type = "Blunder"
            elif diff < -100:
                move_type = "Mistake"

        analysis.append({
            "move_no": move_no,
            "move": board.san(move),
            "best_move": best_move,
            "evaluation": eval_after,
            "type": move_type
        })

        move_no += 1

    return {"status": "success", "analysis": analysis}
