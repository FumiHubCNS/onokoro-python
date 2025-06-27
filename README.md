# onokoro-python

ONOKOROプロジェクトで作成した Python コードを管理するリポジトリです。  
パッケージ管理には [uv](https://github.com/astral-sh/uv) を使用しています。

## セットアップ手順

```bash
# uv をインストール（まだの場合）
curl -Ls https://astral.sh/uv/install.sh | sh
```

## スクリプト

STRASSEのLogをplotlyを使って描画するコマンド。

```bash
uv run check_strasse_log
```

引数として`input`(ログファイルのパス)と`experiment_number`(実験課題番号)を指定でき、デフォルトは`./data/onokoro57/logs/*.txt`と`57`である。

指摘する際は以下のようにする。

```bash
uv run check_strasse_log experiment_number=57 input="./data/onokoro57/logs/*.txt"
```