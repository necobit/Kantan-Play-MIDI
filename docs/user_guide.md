# ユーザーガイド

このガイドでは、Kantan Play MIDIの基本的な使用方法から応用的な活用法まで詳しく説明します。

## 基本概念

### 「かんぷれ」ガジェットについて

「かんぷれ」は、音楽演奏用のMIDIコントローラーガジェットです。以下の要素から構成されています：

- **スロット**: 8つの演奏チャンネル（1-8）
- **Degreeボタン**: 音階を指定するボタン（1, 2b, 2, 3b, 3, 4, 5b, 5, 6b, 6, 7b, 7）
- **モディファイアボタン**: 演奏を修飾するボタン（1-8の値）

### MIDIシミュレーション

このソフトウェアは、物理的なボタン操作をMIDI信号で再現します：

1. **ボタン押下**: MIDI Note On
2. **ボタン離脱**: MIDI Note Off
3. **タイミング制御**: BPMベースの正確な制御

## クイックスタート

### 1. 最初の演奏

シンプルな4音符の演奏を試してみましょう：

```bash
# テスト演奏ファイルで基本動作を確認
kantan-play-midi test_performance.json --play -v
```

### 2. MIDIポートの設定

```bash
# 利用可能なポートを確認
kantan-play-midi test_performance.json --list-ports

# 特定のポートを指定
kantan-play-midi test_performance.json --play --midi-port "M2"
```

### 3. 演奏データの検証

新しい演奏データを作成したら、まず検証しましょう：

```bash
kantan-play-midi your_song.json --validate-only
```

## 演奏データの作成

### JSON形式の基本構造

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
    }
  ]
}
```

### パラメータ詳細

#### slot（スロット）
- **型**: 整数
- **範囲**: 1-8
- **説明**: 使用する演奏チャンネル
- **例**: `"slot": 3`

#### tempo（テンポ）
- **型**: 整数
- **範囲**: 1-300（実用的には60-200）
- **単位**: BPM (Beats Per Minute)
- **例**: `"tempo": 120`（中程度のテンポ）

#### degree（音階）
- **型**: 文字列
- **選択肢**: `"1"`, `"2b"`, `"2"`, `"3b"`, `"3"`, `"4"`, `"5b"`, `"5"`, `"6b"`, `"6"`, `"7b"`, `"7"`
- **説明**: 演奏する音階を指定
- **例**: `"degree": "5"` (ソの音)

#### modifier1-3（モディファイア）
- **型**: 整数
- **範囲**: 0-8
- **説明**: 0は無効、1-8は対応するモディファイアボタン
- **例**: `"modifier1": 2` (2番目のモディファイア1ボタン)

### 実践的な例

#### 基本的なスケール演奏

```json
{
  "slot": 1,
  "tempo": 120,
  "notes": [
    {"degree": "1", "modifier1": 0, "modifier2": 0, "modifier3": 0},
    {"degree": "2", "modifier1": 0, "modifier2": 0, "modifier3": 0},
    {"degree": "3", "modifier1": 0, "modifier2": 0, "modifier3": 0},
    {"degree": "4", "modifier1": 0, "modifier2": 0, "modifier3": 0},
    {"degree": "5", "modifier1": 0, "modifier2": 0, "modifier3": 0},
    {"degree": "6", "modifier1": 0, "modifier2": 0, "modifier3": 0},
    {"degree": "7", "modifier1": 0, "modifier2": 0, "modifier3": 0},
    {"degree": "1", "modifier1": 0, "modifier2": 0, "modifier3": 0}
  ]
}
```

#### モディファイアを使用した演奏

```json
{
  "slot": 2,
  "tempo": 100,
  "notes": [
    {"degree": "1", "modifier1": 1, "modifier2": 0, "modifier3": 0},
    {"degree": "3", "modifier1": 0, "modifier2": 2, "modifier3": 0},
    {"degree": "5", "modifier1": 1, "modifier2": 2, "modifier3": 3}
  ]
}
```

#### 半音を含む演奏

```json
{
  "slot": 1,
  "tempo": 140,
  "notes": [
    {"degree": "1", "modifier1": 0, "modifier2": 0, "modifier3": 0},
    {"degree": "2b", "modifier1": 0, "modifier2": 0, "modifier3": 0},
    {"degree": "2", "modifier1": 0, "modifier2": 0, "modifier3": 0},
    {"degree": "3b", "modifier1": 0, "modifier2": 0, "modifier3": 0},
    {"degree": "3", "modifier1": 0, "modifier2": 0, "modifier3": 0}
  ]
}
```

## タイミングと演奏制御

### BPMとタイミング計算

演奏のタイミングは以下の計算で決定されます：

1. **1拍の長さ**: 60秒 ÷ BPM
2. **degreeボタン1回の長さ**: (60秒 ÷ BPM) × 4 ÷ 8 = 30秒 ÷ BPM
3. **音符の演奏時間**: degreeボタン8回分 = 4拍

#### 例：BPM 120の場合
- 1拍 = 60 ÷ 120 = 0.5秒
- degreeボタン1回 = 0.5 × 4 ÷ 8 = 0.25秒
- 1音符の演奏時間 = 0.25 × 8 = 2秒

### 演奏シーケンス

各音符の演奏は以下の順序で実行されます：

1. **モディファイア押下**: 該当するmodifier（1-3）のボタンを同時押し
2. **degree演奏**: 指定されたdegreeボタンを8回押下・離脱
3. **モディファイア離脱**: 押下していたmodifierボタンを離脱

## コマンドラインの詳細使用法

### 基本コマンド

```bash
kantan-play-midi [OPTIONS] INPUT_FILE
```

### オプション詳細

#### --config PATH
MIDI設定ファイルを指定します。

```bash
kantan-play-midi song.json --config custom_midi.json
```

#### --validate-only
演奏を実行せず、入力ファイルの検証のみを行います。

```bash
kantan-play-midi song.json --validate-only
```

#### --show-conversion
MIDI変換の詳細を表示します。

```bash
kantan-play-midi song.json --show-conversion
```

#### --play
実際にMIDI信号を送信して演奏を実行します。

```bash
kantan-play-midi song.json --play
```

#### --midi-port TEXT
使用するMIDIポートを明示的に指定します。

```bash
kantan-play-midi song.json --play --midi-port "IAC Driver Bus 1"
```

#### --list-ports
利用可能なMIDIポートを一覧表示します。

```bash
kantan-play-midi song.json --list-ports
```

#### -v, --verbose
詳細な実行情報を表示します。

```bash
kantan-play-midi song.json --play -v
```

### 組み合わせ例

```bash
# 詳細表示付きで演奏
kantan-play-midi my_song.json --play --midi-port "USB MIDI" -v

# 変換結果を確認してから演奏
kantan-play-midi my_song.json --show-conversion
kantan-play-midi my_song.json --play --midi-port "USB MIDI"

# カスタム設定での演奏
kantan-play-midi my_song.json --config my_midi.json --play -v
```

## MIDI設定のカスタマイズ

### MIDI.jsonの編集

デフォルトのMIDI設定を変更する場合：

```json
{
  "slot": [24, 25, 26, 27, 28, 29, 30, 31],
  "notes": [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
  "modifier1": [52, 53, 54, 55, 56, 57, 58, 59],
  "modifier2": [44, 45, 46, 47, 48, 49, 50, 51],
  "modifier3": [36, 37, 38, 39, 40, 41, 42, 43]
}
```

### MIDIノートナンバー対応表

| 要素 | デフォルト範囲 | 説明 |
|------|----------------|------|
| slot | 24-31 | C1-G1 |
| notes | 60-71 | C4-B4 |
| modifier1 | 52-59 | E3-B3 |
| modifier2 | 52-59 | E3-B3 |
| modifier3 | 52-59 | E3-B3 |

## トラブルシューティング

### 演奏が開始されない

1. **MIDIポートの確認**
```bash
kantan-play-midi song.json --list-ports
```

2. **演奏データの検証**
```bash
kantan-play-midi song.json --validate-only
```

3. **詳細ログの確認**
```bash
kantan-play-midi song.json --play -v
```

### タイミングがずれる

- **低いBPM**: 60-80で試してください
- **システム負荷**: 他のアプリケーションを終了
- **バッファサイズ**: MIDIドライバーの設定を確認

### MIDI信号が送信されない

- **デバイス接続**: 物理的な接続を確認
- **ドライバー**: 最新のMIDIドライバーをインストール
- **競合**: 他のMIDIアプリケーションを終了

## 応用的な使用法

### バッチ処理

複数のファイルを連続演奏：

```bash
#!/bin/bash
for file in songs/*.json; do
    echo "演奏中: $file"
    kantan-play-midi "$file" --play --midi-port "USB MIDI"
    sleep 2
done
```

### パフォーマンス監視

演奏の詳細なログを記録：

```bash
kantan-play-midi song.json --play -v 2>&1 | tee performance.log
```

### 自動テスト

演奏データの自動検証：

```bash
find . -name "*.json" -exec kantan-play-midi {} --validate-only \;
```

## 次のステップ

より詳細な情報については、以下を参照してください：

- [API仕様書](api_reference.md) - プログラミング向けの詳細
- [使用例](examples.md) - 実践的な演奏例
- [GitHub Issues](https://github.com/necobit/Kantan-Play-MIDI/issues) - 質問・問題報告