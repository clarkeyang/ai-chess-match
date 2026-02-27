
import chess
import subprocess
import time
import re

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
    """AI의 답변에서 첫 줄에 있는 UCI 형식의 수만 추출합니다."""
    # 클코 제안대로 첫 줄을 먼저 확인
    first_line = text.strip().split('
')[0].strip()
    match = re.search(r"([a-h][1-8][a-h][1-8])", first_line)
    if match:
        return match.group(1)
    
    # 만약 첫 줄에 없으면 전체 텍스트에서 검색 (폴백)
    match = re.search(r"([a-h][1-8][a-h][1-8])", text)
    if match:
        return match.group(1)
    return None

def main():
    board = chess.Board()
    print("=== AI CHESS MATCH: Gemini vs Claude ===")
    
    while not board.is_game_over():
        print("
" + "="*30)
        print(board)
        print("="*30)
        
        current_fen = board.fen()
        turn_name = "Gemini (White)" if board.turn == chess.WHITE else "Claude (Black)"
        
        # 클코의 제안을 반영한 새로운 프롬프트 구조
        prompt = f"""
현재 체스판 FEN: {current_fen}
너는 {turn_name}야.

반드시 첫 줄에 UCI 표기법으로 수만 적어 (예: e2e4).
둘째 줄부터 왜 이 수를 뒀는지 한 문장으로 설명해.

규칙에 어긋나는 수를 두면 기권으로 간주한다.
"""
        
        if board.turn == chess.WHITE:
            print(f"
> {turn_name} 생각 중...")
            response = ask_gemini(prompt)
        else:
            print(f"
> {turn_name} 생각 중...")
            response = ask_claude(prompt)
        
        print(f"AI 응답:
{response}")
        move_uci = extract_move(response)
        
        if move_uci:
            try:
                move = chess.Move.from_uci(move_uci)
                if move in board.legal_moves:
                    board.push(move)
                    print(f"결정된 수: {move_uci}")
                else:
                    print(f"경고: {move_uci}는 규칙에 어긋나는 수입니다.")
                    break # 정식 대국에서는 바로 패배 처리 가능
            except ValueError:
                print(f"경고: 잘못된 형식.")
                break
        else:
            print("경고: 수를 찾지 못함.")
            break
            
        time.sleep(1)

    print("
" + "="*30)
    print("게임 종료!")
    print(f"결과: {board.result()}")
    print("="*30)

if __name__ == "__main__":
    main()
