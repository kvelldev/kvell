## アノテーションコメント

TODO: 

## コマンド

### 起動
Docker
`cd ~/ws/kvell docker-compose up -d`

FastAPI
`cd ~/ws/kvell/apps/api && PYTHONPATH=src uv run uvicorn app.main:app --port 8000 --reload`


### Dev

PBIを取得
```shell
gh issue view 12 --json title,body,url
```

diffを取得
```shell
git diff ${対象ディレクトリ} > diff.txt
```

変更されたファイルの中身をすべて取得
```shell
git diff --cached --name-only --diff-filter=d ${対象ディレクトリ} | xargs -I{} cat "{}" > diff.txt
```

対象ディレクトリの実装ファイルをすべて取得
```shell
find ${対象ディレクトリ} -type f \( -name "*.ts" -o -name "*.js" -o -name "*.json" -o -name "*.py" \) | xargs -I{} cat "{}" > files.txt
```

コードレビュー
```md
添付インセプションデッキのPJをやってます。Agentic AIにコーディングさせて、diff.txtの結果を得ました。
添付のアーキテクチャ指示書等を参考にコードレビューをお願いします。
```


## TODO

