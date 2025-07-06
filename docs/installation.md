# インストールガイド

このドキュメントでは、Kantan Play MIDIの詳細なインストール手順を説明します。

## システム要件

### オペレーティングシステム
- **Windows**: 10以上（64bit推奨）
- **macOS**: 10.15 Catalina以上
- **Linux**: Ubuntu 18.04以上、または同等のディストリビューション

### Python環境
- **Python**: 3.8以上（3.10推奨）
- **pip**: 21.0以上

### ハードウェア要件
- **MIDI接続**: USB-MIDIインターフェース、または仮想MIDIポート
- **メモリ**: 最低512MB（1GB推奨）
- **ストレージ**: 100MB以上の空き容量

## 事前準備

### 1. Pythonのインストール確認

```bash
python --version
pip --version
```

Python 3.8以上がインストールされていることを確認してください。

### 2. MIDIドライバーのインストール

#### Windows
- **ASIO4ALL**: 一般的なASIOドライバー
- **LoopMIDI**: 仮想MIDIポートソフトウェア

#### macOS
- **Audio MIDI Setup**: macOS標準のMIDI設定ツール
- **IAC Driver**: 仮想MIDIバス（macOS標準）

#### Linux
```bash
# ALSA MIDI サポート
sudo apt-get install alsa-utils

# PulseAudio MIDI
sudo apt-get install pulseaudio-module-jack
```

## インストール手順

### 方法1: 開発版インストール（推奨）

1. **リポジトリのクローン**
```bash
git clone https://github.com/necobit/Kantan-Play-MIDI.git
cd Kantan-Play-MIDI
```

2. **仮想環境の作成（推奨）**
```bash
# Windowsの場合
python -m venv venv
venv\Scripts\activate

# macOS/Linuxの場合
python3 -m venv venv
source venv/bin/activate
```

3. **パッケージのインストール**
```bash
pip install -e .
```

### 方法2: PyPI（将来対応予定）

```bash
pip install kantan-play-midi
```

## インストール後の確認

### 1. コマンドライン確認

```bash
kantan-play-midi --help
```

正常にインストールされていれば、ヘルプメッセージが表示されます。

### 2. MIDIポート確認

```bash
kantan-play-midi test_performance.json --list-ports
```

利用可能なMIDIポートが表示されることを確認してください。

### 3. テスト実行

```bash
pytest tests/ -v
```

全テストが通ることを確認してください。

## トラブルシューティング

### よくある問題と解決方法

#### 1. python-rtmidiのインストールエラー

**症状**: `python-rtmidi`のコンパイルでエラーが発生

**解決方法**:

**Windows**:
```bash
# Visual Studio Build Toolsのインストールが必要
# または事前コンパイル済みを使用
pip install --only-binary=all python-rtmidi
```

**macOS**:
```bash
# Xcode Command Line Toolsのインストール
xcode-select --install
```

**Linux**:
```bash
# 開発パッケージのインストール
sudo apt-get install python3-dev libasound2-dev libjack-dev
```

#### 2. MIDIポートが検出されない

**症状**: `--list-ports`で何も表示されない

**解決方法**:
1. MIDIドライバーが正しくインストールされているか確認
2. 他のMIDIアプリケーションでポートが使用されていないか確認
3. システムを再起動

#### 3. 権限エラー（Linux）

**症状**: MIDIデバイスへのアクセスが拒否される

**解決方法**:
```bash
# ユーザーをaudioグループに追加
sudo usermod -a -G audio $USER

# 再ログインまたは再起動が必要
```

#### 4. 仮想環境の問題

**症状**: パッケージが見つからない

**解決方法**:
```bash
# 仮想環境がアクティブか確認
which python

# 再インストール
pip uninstall kantan-play-midi
pip install -e .
```

## 開発環境のセットアップ

### 追加依存関係のインストール

```bash
# 開発ツール（テスト、リント、フォーマッターなど）
pip install -e ".[dev]"

# または個別インストール
pip install pytest pytest-cov black isort mypy
```

### エディタ設定

#### VS Code
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black"
}
```

#### PyCharm
1. File → Settings → Project → Python Interpreter
2. 仮想環境のPythonを選択
3. Code Style → Python → Black formatterを有効化

## アンインストール

### パッケージの削除

```bash
pip uninstall kantan-play-midi
```

### 仮想環境の削除

```bash
# 仮想環境のディレクトリを削除
rm -rf venv/
```

### リポジトリの削除

```bash
# プロジェクトディレクトリを削除
cd ..
rm -rf Kantan-Play-MIDI/
```

## 次のステップ

インストールが完了したら、以下のドキュメントを参照してください：

- [ユーザーガイド](user_guide.md) - 基本的な使用方法
- [API仕様書](api_reference.md) - プログラミングインターフェース
- [使用例](examples.md) - 実践的な使用例

## サポート

インストールに関する問題は、以下で報告してください：

- [GitHub Issues](https://github.com/necobit/Kantan-Play-MIDI/issues)
- [ディスカッション](https://github.com/necobit/Kantan-Play-MIDI/discussions)