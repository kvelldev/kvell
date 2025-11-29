# kvell
A BBS for silent majority.

- プロト: https://bolt.new/~/sb1-f2qwfqq1

## コマンド

Docker
`cd ~/ws/kvell docker-compose up -d`

FastAPI
`cd ~/ws/kvell/apps/api && PYTHONPATH=src uv run uvicorn app.main:app --port 8000 --reload`

## TODO

fetch_latestのTZがUTCになってそう。(saveの方はJTCっぽい。)
