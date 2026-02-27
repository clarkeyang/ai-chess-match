import chess
import chess.pgn
import subprocess
import time
import re
import datetime
import random

def ask_claude(prompt):
    """Claude CLI를 호출하여 응답을 받습니다."""
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error calling Claude: {e}"

def ask_gemini(prompt):
    """Gemini CLI를 호출하여 응답을 받습니다."""
    try:
        result = subprocess.run(
            ["gemini", "-p", prompt],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error calling Gemini: {e}"

def extract_move(text):
    """AI의 답변에서 UCI 형식의 수(예: e2e4, e7e8q)를 추출합니다."""
    # 첫 줄 우선 확인 (UCI는 4~5글자)
    first_line = text.strip().split('\n')[0].strip()
    match = re.search(r"([a-h][1-8][a-h][1-8][qrbn]?)", first_line)
    if match:
        return match.group(1)
    
    # 전체 텍스트에서 검색 (폴백)
    match = re.search(r"([a-h][1-8][a-h][1-8][qrbn]?)", text)
    if match:
        return match.group(1)
    return None

def main():
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["Event"] = "AI Chess Battle: Gemini vs Claude"
    game.headers["Site"] = "Local Server"
    game.headers["Date"] = datetime.date.today().strftime("%Y.%m.%d")
    game.headers["White"] = "Gemini"
    game.headers["Black"] = "Claude"
    
    node = game
    
    print("\n" + "★"*20)
    print("  AI CHESS MATCH: Gemini vs Claude")
    print("★"*20)
    
    while not board.is_game_over():
        # 유니코드 체스판 출력 (더 예쁘게!)
        print("\n" + "-"*30)
        print(board.unicode())
        print("-"*30)
        
        current_fen = board.fen()
        turn_name = "Gemini (White)" if board.turn == chess.WHITE else "Claude (Black)"
        
        move_made = False
        for attempt in range(1, 4): # 최대 3회 시도
            prompt = f"""
현재 체스판 FEN: {current_fen}
너는 {turn_name}야.

반드시 첫 줄에 UCI 표기법으로 수만 적어 (예: e2e4, 프로모션 시 e7e8q).
둘째 줄부터 왜 이 수를 뒀는지 한 문장으로 설명해.
(시도 횟수: {attempt}/3)
"""
            
            print(f"\n> {turn_name} 생각 중... (시도 {attempt}/3)")
            if board.turn == chess.WHITE:
                response = ask_gemini(prompt)
            else:
                response = ask_claude(prompt)
            
            print(f"AI 응답:\n{response}")
            move_uci = extract_move(response)
            
            if move_uci:
                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in board.legal_moves:
                        board.push(move)
                        node = node.add_main_line(move)
                        print(f"결정된 수: {move_uci}")
                        move_made = True
                        break
                    else:
                        print(f"경고: {move_uci}는 규칙에 어긋나는 수입니다.")
                except ValueError:
                    print(f"경고: 잘못된 형식 ({move_uci}).")
            else:
                print("경고: 수를 찾지 못함.")
        
        # 3회 시도 모두 실패 시 랜덤 수
        if not move_made:
            legal_moves = list(board.legal_moves)
            random_move = random.choice(legal_moves)
            board.push(random_move)
            node = node.add_main_line(random_move)
            print(f"알림: 3회 시도 실패로 인해 랜덤 수({random_move.uci()})를 둡니다.")

    # 게임 종료 및 PGN 저장
    print("\n" + "="*30)
    print("게임 종료!")
    print(f"결과: {board.result()}")
    print("="*30)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pgn_path = f"games/match_{timestamp}.pgn"
    with open(pgn_path, "w", encoding="utf-8") as f:
        f.write(str(game))
    print(f"기보가 저장되었습니다: {pgn_path}")

if __name__ == "__main__":
    main()
