# AI Chess Match: Claude vs Gemini

AI 대 AI 체스 대결 프로젝트. Claude Code(Opus)와 Gemini가 Python 스크립트를 통해 자동으로 체스를 둔다.

## 구조

```
ai-chess-match/
├── README.md
├── COMMUNICATION.md       ← AI 간 소통 채널 (이슈/PR 대신 여기서)
├── scripts/
│   └── chess_match.py     ← 메인 대국 스크립트
├── games/                 ← 기보 저장 (PGN 형식)
├── prompts/
│   ├── claude.md          ← Claude용 프롬프트 템플릿
│   └── gemini.md          ← Gemini용 프롬프트 템플릿
└── viewer/                ← 관전 시각화
```

## 규칙

- LLM 자체 지능으로만 수를 둔다 (Stockfish 등 체스 엔진 사용 금지)
- 각 수마다 왜 그 수를 뒀는지 코멘트를 남긴다
- 불법 수를 두면 3회까지 재시도, 그래도 실패하면 랜덤 합법 수로 대체
- 기보는 PGN 형식으로 games/ 에 저장

## 기술

- `python-chess`: 규칙 검증, 판 상태 관리
- `claude -p`: Claude Code CLI 비대화형 모드 (Max 구독)
- Gemini API 또는 CLI: Gemini 호출
- 관전 시각화: 터미널 유니코드 체스판 + 웹 뷰어(추후)

## 참여자

- **White**: Gemini (제미나이)
- **Black**: Claude Opus (클코)
- **심판/인프라**: Clarke (인간)
