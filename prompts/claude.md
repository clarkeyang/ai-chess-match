# Claude Chess Prompt Template

You are playing chess as {{turn_name}}.

Current board (FEN): {{current_fen}}
Move history so far: {{move_history}}

IMPORTANT: Your FIRST LINE must contain ONLY a UCI move (e.g. e2e4, e7e8q for promotion). Nothing else on the first line.
From the second line, briefly explain why you chose this move (1-2 sentences in Korean).

This is attempt {{attempt}}/3. An illegal move will cost you an attempt.
