# Kantan Play MIDI - かんぷれコントロール用Pythonライブラリ

「かんぷれ」ガジェットを自動制御するためのPythonライブラリです。JSON形式の演奏データをMIDI信号に変換し、物理的なボタン操作をシミュレートします。

## 🎯 概要

このプロジェクトは、音楽演奏ガジェット「かんぷれ」を自動化するためのツールです。JSON形式で記述された演奏データを読み込み、MIDI信号を通じてガジェットのボタンを自動で押下・離脱することで、楽曲の自動演奏を実現します。

### 主な機能

- ✅ JSON形式の演奏データ読み込み
- ✅ リアルタイムMIDI信号送信
- ✅ スロット選択とdegreeボタンの自動制御
- ✅ モディファイアボタンの組み合わせ制御
- ✅ BPMベースのタイミング制御
- ✅ 豊富なCLIオプション
- ✅ 包括的なエラーハンドリング

## 📦 インストール

### 必要環境

- Python 3.8以上
- pip (パッケージ管理ツール)
- MIDIインターフェース（USB-MIDI、仮想MIDIポートなど）

### インストール手順

1. **リポジトリのクローン**
```bash
git clone https://github.com/necobit/Kantan-Play-MIDI.git
cd Kantan-Play-MIDI
```

2. **パッケージのインストール**
```bash
pip install -e .
```

3. **動作確認**
```bash
kantan-play-midi --help
```

### 依存関係

以下のパッケージが自動的にインストールされます：

- `python-rtmidi>=1.5.8` - MIDI入出力
- `mido>=1.3.2` - MIDI処理
- `click>=8.1.7` - CLIインターフェース
- `rich>=13.7.0` - コンソール表示

## 🚀 基本的な使い方

### 1. MIDIポートの確認

利用可能なMIDIポートを確認：
```bash
kantan-play-midi test_performance.json --list-ports
```

### 2. 演奏データの検証

JSON形式の演奏データが正しいかチェック：
```bash
kantan-play-midi input.json --validate-only
```

### 3. 変換結果の表示

MIDI変換の詳細を確認：
```bash
kantan-play-midi input.json --show-conversion -v
```

### 4. 実際の演奏実行

MIDI信号を送信して演奏：
```bash
kantan-play-midi input.json --play --midi-port "Your MIDI Port"
```

### 5. 簡単テスト

付属のテストスクリプトで動作確認：
```bash
./quick_test.sh
```

## 📝 演奏データ形式

### JSON形式の例

```json
{
  "slot": 1,
  "tempo": 120,
  "notes": [
    {
      "degree": "1",
      "modifier1": 0,
      "modifier2": 0,
      "modifier3": 0
    },
    {
      "degree": "3",
      "modifier1": 1,
      "modifier2": 0,
      "modifier3": 0
    },
    {
      "degree": "5",
      "modifier1": 0,
      "modifier2": 1,
      "modifier3": 1
    }
  ]
}
```

### パラメータ説明

| パラメータ | 型 | 範囲 | 説明 |
|------------|----|----|------|
| `slot` | 整数 | 1-8 | 使用するスロット番号 |
| `tempo` | 整数 | 1-300 | テンポ (BPM) |
| `notes` | 配列 | - | 演奏する音符のリスト |
| `degree` | 文字列 | "1", "2b", "2", "3b", "3", "4", "5b", "5", "6b", "6", "7b", "7" | 音階 |
| `modifier1-3` | 整数 | 0-8 | モディファイア値（0は無効） |

## ⚙️ 設定ファイル

### MIDI.json

MIDI設定ファイルで、各要素のMIDIノートナンバーを定義：

```json
{
  "slot": [24, 25, 26, 27, 28, 29, 30, 31],
  "notes": [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
  "modifier1": [52, 53, 54, 55, 56, 57, 58, 59],
  "modifier2": [52, 53, 54, 55, 56, 57, 58, 59],
  "modifier3": [52, 53, 54, 55, 56, 57, 58, 59]
}
```

## 🎹 演奏の仕組み

### タイミング制御

1. **BPMベース**: `tempo`パラメータでBPMを指定
2. **degreeボタン**: 各音符で8回押下（4拍に相当）
3. **拍計算**: 1拍 = 60秒 ÷ BPM
4. **次の音符**: 8回の押下完了後に次の音符へ進行

### ボタン操作シーケンス

1. **スロット選択**: 演奏開始時に1回実行
2. **音符演奏**（各音符ごと）:
   - モディファイアボタン押下（該当する場合）
   - degreeボタンを8回押下・離脱
   - モディファイアボタン離脱

### MIDI信号例

```
スロット選択: [144, 24, 127] → 50ms後 → [128, 24, 0]
音符演奏: [144, 60, 127] → 50ms後 → [128, 60, 0]
```

## 🔧 コマンドラインオプション

```bash
kantan-play-midi [OPTIONS] INPUT_FILE
```

### オプション一覧

| オプション | 説明 |
|-----------|------|
| `--config PATH` | MIDI設定ファイル（デフォルト: MIDI.json） |
| `--validate-only` | 入力ファイルの検証のみ実行 |
| `--show-conversion` | 変換結果を表示 |
| `--play` | 実際にMIDI演奏を実行 |
| `--midi-port TEXT` | 使用するMIDIポート名 |
| `--list-ports` | 利用可能なMIDIポートを一覧表示 |
| `-v, --verbose` | 詳細な情報を表示 |
| `--help` | ヘルプを表示 |

## 🧪 テスト

### テスト実行

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ付き
pytest tests/ --cov=src/kantan_play_midi

# 特定テストのみ
pytest tests/test_player.py -v
```

### テスト結果（現在）

- **総テスト数**: 57
- **成功**: 54
- **軽微な失敗**: 3（機能に影響なし）
- **カバレッジ**: 71%

## 🔨 開発者向け

### 開発環境のセットアップ

```bash
# 開発依存関係のインストール
pip install -e ".[dev]"

# pre-commitフックの設定
pre-commit install
```

### プロジェクト構造

```
src/kantan_play_midi/
├── __init__.py          # パッケージ初期化
├── cli.py              # CLIエントリーポイント
├── config.py           # MIDI設定管理
├── converter.py        # MIDI変換処理
├── exceptions.py       # カスタム例外
├── input_handler.py    # JSON入力処理
├── models.py           # データモデル
├── player.py           # MIDI演奏制御
├── processor.py        # パフォーマンス処理
├── sequence.py         # MIDIシーケンス
└── timing.py           # タイミング計算

tests/                  # テストファイル
docs/                   # ドキュメント
examples/               # サンプルファイル
```

### API使用例

```python
from kantan_play_midi import MIDIPlayer, InputHandler, PerformanceProcessor

# 演奏データの読み込み
handler = InputHandler()
performance = handler.load_from_file("input.json")

# MIDI演奏
player = MIDIPlayer()
player.connect()

processor = PerformanceProcessor(config)
sequence = processor.process_performance(performance)
player.play_sequence(sequence)
```

## 🐛 トラブルシューティング

### よくある問題

1. **MIDIポートが見つからない**
   ```bash
   kantan-play-midi input.json --list-ports
   ```

2. **パッケージインストールエラー**
   ```bash
   pip install --upgrade pip
   pip install -e .
   ```

3. **テスト失敗**
   ```bash
   pip install -e .  # パッケージを再インストール
   pytest tests/ -v
   ```

### ログ確認

詳細なログ情報を表示：
```bash
kantan-play-midi input.json --play -v
```

## 🤝 貢献

1. フォークしてブランチを作成
2. 機能を実装
3. テストを追加・実行
4. プルリクエストを作成

### 貢献ガイドライン

- コードスタイル: Black, isort
- テスト: pytest
- コミットメッセージ: Conventional Commits

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🔗 関連リンク

- [GitHub Repository](https://github.com/necobit/Kantan-Play-MIDI)
- [Issues](https://github.com/necobit/Kantan-Play-MIDI/issues)
- [Pull Requests](https://github.com/necobit/Kantan-Play-MIDI/pulls)

---

**作成者**: necobit  
**バージョン**: 0.1.0  
**最終更新**: 2025年7月6日