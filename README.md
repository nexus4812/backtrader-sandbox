# backtrader-sandbox

[backtrader](https://www.backtrader.com/)による、株取引の趣味レーション

## CLI によるパラメーター調整

実行方法

1. `strategies`配下に`strategies/base_strategy.py`を継承した、戦略クラスを作成する
1. `backtest.py`に銘柄、期間、戦略をねじ込む
1. 下記のコマンドで実行、SQN 順に結果が表示される

```bash
docker-compose run backtrader python backtest.py
```
