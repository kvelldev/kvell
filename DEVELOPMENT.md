## アノテーションコメント

TODO: 

## コマンド

### 起動
Docker
`cd ~/ws/kvell && docker-compose up -d`

FastAPI
`cd ~/ws/kvell/apps/api && PYTHONPATH=src uv run uvicorn app.main:app --port 8000 --reload`


### Dev

PBIを取得
```shell
gh issue view 8 --json title,body,url > PBI.json
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

- /timeline: リロード時にsparkが0件になるバグ。B/Eにバグはなさそう。F/E側で想定してるデータの形式が違う?
    - F/EにてUTCとして解釈サれなかったためにおこってた。
- 続けて。今は開発用にsparkのdecaytimeは1分に設定されてます。E2Eもそれ準拠にしましょう。
gherkinを書き換えたので参考にして。


## React

勉強用。

### 原理原則

**UI=f(State)**。

- stateを作るのがuseState()。f()はtsxのこと。Stateが更新されるとf()が実行される。これを**再描画**と呼ぶ。
- 副作用とは、UI描画以外のすべての処理（通信、DOM変更、タイマー、State更新など）のこと。
- useEffect()は、f()による描画が終わった後に実行される「副作用の予約」。どのタイミングで実行するかは、第二引数で決まる。

```tsx
const Component = () => {
  const [data, setData] = useState(null); // State

  // 副作用の予約（描画が終わったら通信して、Stateを更新しろ）
  useEffect(() => {
    fetch('/api').then(res => setData(res)); 
  }, []);

  return <div>{data}</div>; // UI = f(State)
};
```

### useEffect

```ts
useEffect(callback(), [監視対象])
```

- 監視対象の変更を検知すると、callback()を実行する。
- 監視対象が空の場合はコンポーネントの生成時に一度だけ実行する。

### useState

```ts
const [sparks, setSparks] = useState<型>(初期値);

setSparks(1) // にするとsparks=1になる
setSparks(callback( return 1 ) ) // とすると同じくspark=1になる
setSparks(callback((arg) => {})) // とするとargには最新のsparkが渡る(Reactが暗黙的に渡す)。

```
- setXX()はuseStateで作成したState(今回はsparks)を更新するための関数。
- setXX(値)とすることもできるし、setXX(() => {return})とすることもできる。
