# 関西の投稿の予定表（11/13〜）

- `schedule/D.json`：DB drafts の date==D の文書を、そのまま並べた配列。会議（21:40）が書き、06:23 の回が直す。
- 書いたら機械（.github/workflows/book.yml）が門（tools/book/gate.py）に通し、`state/gate/D.json` に枠ごとの ○×・理由を書く。
- 予約するのは `state/gate/D.json` で ok:true の枠だけ。× の枠は直して schedule/D.json を書き直す（門がもう一度見る）。
- 枠の表は tools/book/config.json（DB rules/content ■3 と同じにする）。
