# 機能実装の流れ

1. PBIを起票する
2. [30_BDD.md](30_BDD.md)を用い、PBIからGherkinを起票する(Vive coding)。
3. PBI + Gherkin + 00~99.mdをinputに、[100_instruction.md](100_instruction.md)をプロンプトとしてAIに実装指示を行う(Agentic Coding)。

## コマンド

- ファイル編集権限をAIに与えるので、ブランチ切ってから作業させる。
- claudeの思考量はプロンプトで制御できる。think < think hard < think harder < ultrathink。


diffを取得
```shell
git diff apps/web/src > diff.txt
```

変更されたファイルの中身をすべて取得
```shell
git diff --name-only apps/web/src | xargs -I{} cat "{}" > diff.txt
```

```md
添付インセプションデッキのPJをやってます。Agentic AIにコーディングさせて、diff.txtの結果を得ました。
```


(deprecated)
```shell
gh issue view 12 --json title,body,url | gemini "このPBIを実施して。不明点があれば質問して、疑問をすべて解消してから実装に入ってください。" -m gemini-2.5-pro -y
```
