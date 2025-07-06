# サンプルファイル

このディレクトリには、Kantan Play MIDIの使用例となるJSONファイルが含まれています。

## ファイル一覧

### 基本的な例

#### `basic_scale.json`
- **内容**: 基本的なスケール（ドレミファソラシド）
- **スロット**: 1
- **テンポ**: 120 BPM
- **特徴**: モディファイアなしのシンプルな演奏
- **使用例**:
```bash
kantan-play-midi examples/basic_scale.json --play -v
```

#### `chromatic_scale.json`
- **内容**: 半音階スケール（全12音）
- **スロット**: 1
- **テンポ**: 100 BPM
- **特徴**: フラット記号（b）を含む全音階
- **使用例**:
```bash
kantan-play-midi examples/chromatic_scale.json --show-conversion
```

#### `with_modifiers.json`
- **内容**: モディファイアを活用した演奏例
- **スロット**: 2
- **テンポ**: 90 BPM
- **特徴**: modifier1, 2, 3の組み合わせ使用
- **使用例**:
```bash
kantan-play-midi examples/with_modifiers.json --play --midi-port "M2"
```

## チュートリアル（tutorial/）

段階的に学習できるチュートリアルファイルです。

### `01_first_note.json`
- **レベル**: 初心者
- **内容**: 単一音符の演奏
- **学習内容**: 基本的なJSON構造とslot/tempo/degree

### `02_three_notes.json`
- **レベル**: 初心者
- **内容**: 3音符の連続演奏
- **学習内容**: notes配列の使用方法

### `03_with_modifier.json`
- **レベル**: 中級者
- **内容**: モディファイア付きの演奏
- **学習内容**: modifier1, 2, 3の使い分け

## 使用方法

### 1. 基本的な検証
```bash
# 全サンプルファイルの検証
find examples/ -name "*.json" -exec kantan-play-midi {} --validate-only \;
```

### 2. 変換結果の確認
```bash
# 変換結果を詳細表示
kantan-play-midi examples/basic_scale.json --show-conversion -v
```

### 3. 実際の演奏
```bash
# MIDIポートを確認
kantan-play-midi examples/basic_scale.json --list-ports

# 演奏実行
kantan-play-midi examples/basic_scale.json --play --midi-port "Your MIDI Port"
```

### 4. チュートリアルの進行
```bash
# ステップ1: 最初の音符
kantan-play-midi examples/tutorial/01_first_note.json --play -v

# ステップ2: 3つの音符
kantan-play-midi examples/tutorial/02_three_notes.json --play -v

# ステップ3: モディファイア使用
kantan-play-midi examples/tutorial/03_with_modifier.json --play -v
```

## カスタマイズ例

### テンポの変更
```json
{
  "slot": 1,
  "tempo": 60,  // ← テンポを60 BPMに変更
  "notes": [
    // ...
  ]
}
```

### スロットの変更
```json
{
  "slot": 3,  // ← スロット3を使用
  "tempo": 120,
  "notes": [
    // ...
  ]
}
```

### モディファイアの追加
```json
{
  "degree": "1",
  "modifier1": 2,  // ← モディファイア1の2番を使用
  "modifier2": 0,
  "modifier3": 0
}
```

## トラブルシューティング

### ファイルが見つからない
```bash
# 現在のディレクトリを確認
pwd

# ファイルの存在確認
ls examples/
```

### JSON形式エラー
```bash
# 構文チェック
python -m json.tool examples/basic_scale.json
```

### MIDI演奏エラー
```bash
# 詳細ログで問題を特定
kantan-play-midi examples/basic_scale.json --play -v
```

## 次のステップ

1. **オリジナル作成**: サンプルを参考に独自の演奏データを作成
2. **高度な使用法**: [ユーザーガイド](../docs/user_guide.md)を参照
3. **API使用**: [API仕様書](../docs/api_reference.md)でプログラミング方法を学習

## 貢献

新しいサンプルファイルや改善案は、GitHubのIssueまたはPull Requestでお知らせください：

- [GitHub Issues](https://github.com/necobit/Kantan-Play-MIDI/issues)
- [Pull Requests](https://github.com/necobit/Kantan-Play-MIDI/pulls)