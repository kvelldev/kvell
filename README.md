# kvell
A BBS for silent majority.

- プロト: https://bolt.new/~/sb1-f2qwfqq1

## コマンド

Docker
`cd ~/ws/kvell docker-compose up -d`

FastAPI
`cd ~/ws/kvell/apps/api && PYTHONPATH=src uv run uvicorn app.main:app --port 8000 --reload`

## TODO

2. Repository層の堅牢化 (例外ハンドリング)
MongoHealthRepository 等のGateway実装において、DBドライバ（Motor）のエラーをそのまま垂れ流しています。これは危険です。 必ず try-except で捕捉し、ドメイン層で定義した例外（あるいは適切なカスタム例外）にラップして送出するか、適切にハンドリングしてください。

B. PydanticモデルのConfig
HealthMessage や DTO ですが、Pydantic V2 を使用している場合、model_config で frozen=True (イミュータブル化) などを設定しておくと、予期せぬ書き換えを防ぎ、堅牢になります。

C. 環境変数の型安全性
database.py や main.py で os.getenv を多用していますが、pydantic-settings を使って Settings クラスにまとめると、起動時に「DB URL設定忘れ」などに気づけるため安全です。

あとテスト。
