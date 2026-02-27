import chess
import chess.pgn
import subprocess
import re
import datetime
import random
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
GAMES_DIR = os.path.join(PROJECT_DIR, "games")

# 유니코드 체스 기물 매핑
PIECE_SYMBOLS = {
    "R": "♜", "N": "♞", "B": "♝", "Q": "♛", "K": "♚", "P": "♟",
    "r": "♖", "n": "♘", "b": "♗", "q": "♕", "k": "♔", "p": "♙",
}


def ask_claude(prompt):
    """Claude CLI 비대화형 모드로 호출 (Max 구독)"""
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=120
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: Claude 응답 시간 초과"
    except Exception as e:
        return f"Error calling Claude: {e}"


def ask_gemini(prompt):
    """Gemini API 호출 (google-generativeai SDK)"""
    try:
        import google.generativeai as genai
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except ImportError:
        # SDK 없으면 gemini CLI 폴백 시도
        try:
            result = subprocess.run(
                ["gemini", "-p", prompt],
                capture_output=True, text=True, timeout=120
            )
            return result.stdout.strip()
        except Exception:
            return "Error: google-generativeai SDK가 설치되지 않았습니다. pip install google-generativeai"
    except Exception as e:
        return f"Error calling Gemini: {e}"


def extract_move(text):
    """AI 응답에서 UCI 형식의 수(예: e2e4, e7e8q)를 추출"""
    # 첫 줄 우선 확인
    first_line = text.strip().split("\n")[0].strip()
    match = re.search(r"\b([a-h][1-8][a-h][1-8][qrbn]?)\b", first_line)
    if match:
        return match.group(1)

    # 전체 텍스트에서 검색 (폴백)
    match = re.search(r"\b([a-h][1-8][a-h][1-8][qrbn]?)\b", text)
    if match:
        return match.group(1)
    return None


def print_board(board):
    """유니코드 체스판을 터미널에 예쁘게 출력"""
    print()
    print("  ┌───┬───┬───┬───┬───┬───┬───┬───┐")
    for rank in range(7, -1, -1):
        row = f"{rank + 1} │"
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            if piece:
                symbol = PIECE_SYMBOLS.get(piece.symbol(), piece.symbol())
            else:
                symbol = " "
            row += f" {symbol} │"
        print(row)
        if rank > 0:
            print("  ├───┼───┼───┼───┼───┼───┼───┼───┤")
    print("  └───┴───┴───┴───┴───┴───┴───┴───┘")
    print("    a   b   c   d   e   f   g   h")
    print()


def build_prompt(fen, turn_name, attempt, move_history):
    """대국용 프롬프트 생성"""
    return f"""You are playing chess as {turn_name}.

Current board (FEN): {fen}
Move history so far: {move_history if move_history else "(opening)"}

IMPORTANT: Your FIRST LINE must contain ONLY a UCI move (e.g. e2e4, e7e8q for promotion). Nothing else on the first line.
From the second line, briefly explain why you chose this move (1-2 sentences in Korean).

This is attempt {attempt}/3. An illegal move will cost you an attempt."""


def main():
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["Event"] = "AI Chess Battle: Gemini vs Claude (Game 1)"
    game.headers["Site"] = "Mac Mini HomeServer"
    game.headers["Date"] = datetime.date.today().strftime("%Y.%m.%d")
    game.headers["Round"] = "1"
    game.headers["White"] = "Gemini"
    game.headers["Black"] = "Claude (Opus)"

    node = game
    move_list = []

    print("\n" + "=" * 40)
    print("   AI CHESS MATCH: Gemini vs Claude")
    print("   Game 1 - " + datetime.date.today().strftime("%Y.%m.%d"))
    print("=" * 40)

    move_number = 0

    while not board.is_game_over():
        print_board(board)

        current_fen = board.fen()
        is_white = board.turn == chess.WHITE
        turn_name = "Gemini (White)" if is_white else "Claude (Black)"
        move_history = " ".join(move_list)

        move_made = False
        for attempt in range(1, 4):
            prompt = build_prompt(current_fen, turn_name, attempt, move_history)

            print(f"> {turn_name} 생각 중... (시도 {attempt}/3)")
            if is_white:
                response = ask_gemini(prompt)
            else:
                response = ask_claude(prompt)

            # 응답 중 첫 줄만 간략 출력, 코멘트는 들여쓰기
            lines = response.strip().split("\n")
            print(f"  수: {lines[0]}")
            if len(lines) > 1:
                comment = " ".join(lines[1:]).strip()
                print(f"  이유: {comment[:100]}{'...' if len(comment) > 100 else ''}")

            move_uci = extract_move(response)

            if move_uci:
                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in board.legal_moves:
                        board.push(move)
                        node = node.add_variation(move)
                        move_list.append(move_uci)
                        move_number += 1
                        print(f"  >> {move_number}. {move_uci} (합법)")
                        move_made = True
                        break
                    else:
                        print(f"  !! {move_uci} 불법 수")
                except ValueError:
                    print(f"  !! {move_uci} 잘못된 형식")
            else:
                print("  !! 수를 파싱하지 못함")

        # 3회 실패 시 랜덤 합법 수
        if not move_made:
            legal_moves = list(board.legal_moves)
            random_move = random.choice(legal_moves)
            board.push(random_move)
            node = node.add_variation(random_move)
            move_list.append(random_move.uci())
            move_number += 1
            print(f"  >> {move_number}. {random_move.uci()} (랜덤 - 3회 실패)")

    # 게임 종료
    result = board.result()
    game.headers["Result"] = result

    print_board(board)
    print("=" * 40)
    print("  GAME OVER")
    print(f"  결과: {result}")
    if board.is_checkmate():
        winner = "Claude (Black)" if board.turn == chess.WHITE else "Gemini (White)"
        print(f"  승자: {winner} (체크메이트)")
    elif board.is_stalemate():
        print("  스테일메이트 (무승부)")
    elif board.is_insufficient_material():
        print("  기물 부족 (무승부)")
    elif board.is_fifty_moves():
        print("  50수 규칙 (무승부)")
    print(f"  총 {move_number}수")
    print("=" * 40)

    # PGN 저장
    os.makedirs(GAMES_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pgn_path = os.path.join(GAMES_DIR, f"game1_{timestamp}.pgn")
    with open(pgn_path, "w", encoding="utf-8") as f:
        f.write(str(game))
    print(f"\n  기보 저장: {pgn_path}")


if __name__ == "__main__":
    main()
