#!/bin/bash
#
# Kantan Play MIDI - 動作確認スクリプト
# すべての動作確認を順番に実行します
#

set -e  # エラーが発生したら停止

echo "======================================"
echo " Kantan Play MIDI 動作確認スクリプト"
echo "======================================"
echo ""

# 1. 仮想環境の確認と作成
echo "1. Python仮想環境のセットアップ"
echo "   ------------------------------------"
if [ ! -d "venv" ]; then
    echo "   仮想環境を作成しています..."
    python3 -m venv venv
else
    echo "   ✓ 仮想環境は既に存在します"
fi

# 仮想環境のアクティベート
source venv/bin/activate
echo "   ✓ 仮想環境をアクティベートしました"
echo ""

# 2. 依存関係のインストール
echo "2. 依存関係のインストール"
echo "   ------------------------------------"
echo "   開発用パッケージをインストールしています..."
pip install -q --upgrade pip
pip install -q -e ".[dev]"
echo "   ✓ 依存関係のインストールが完了しました"
echo ""

# 3. インストール確認
echo "3. パッケージのインストール確認"
echo "   ------------------------------------"
python -c "import kantan_play_midi; print(f'   ✓ kantan_play_midi v{kantan_play_midi.__version__} がインストールされています')"
echo ""

# 4. 基本機能テスト
echo "4. 基本機能の動作確認"
echo "   ------------------------------------"
if [ -f "test_basic.py" ]; then
    python test_basic.py
else
    echo "   ⚠️  test_basic.py が見つかりません"
fi
echo ""

# 5. コード品質チェック
echo "5. コード品質チェック"
echo "   ------------------------------------"

# Black (フォーマット)
echo "   [Black] コードフォーマットチェック..."
if black --check src/ tests/ 2>/dev/null; then
    echo "   ✓ コードフォーマットは正しいです"
else
    echo "   ⚠️  コードフォーマットの修正が必要です (black src/ tests/ で修正)"
fi

# Flake8 (リンター)
echo "   [Flake8] コードスタイルチェック..."
if flake8 src/ tests/ --max-line-length=88 2>/dev/null; then
    echo "   ✓ コードスタイルは問題ありません"
else
    echo "   ⚠️  コードスタイルの問題があります"
fi

# MyPy (型チェック)
echo "   [MyPy] 型チェック..."
if mypy src/ --ignore-missing-imports 2>/dev/null; then
    echo "   ✓ 型チェックは問題ありません"
else
    echo "   ⚠️  型チェックの問題があります"
fi
echo ""

# 6. テスト実行
echo "6. テストスイートの実行"
echo "   ------------------------------------"
if [ -d "tests" ] && [ -n "$(find tests -name 'test_*.py' -print -quit)" ]; then
    pytest tests/ -v --tb=short
else
    echo "   ⚠️  テストファイルが見つかりません"
fi
echo ""

# 7. MIDIインターフェースの確認
echo "7. MIDIインターフェースの確認"
echo "   ------------------------------------"
python -c "
import rtmidi
midi_out = rtmidi.MidiOut()
ports = midi_out.get_ports()
if ports:
    print('   利用可能なMIDIポート:')
    for i, port in enumerate(ports):
        print(f'     [{i}] {port}')
else:
    print('   ⚠️  MIDIポートが見つかりません')
"
echo ""

# 8. プロジェクト構造の確認
echo "8. プロジェクト構造の確認"
echo "   ------------------------------------"
echo "   プロジェクトのファイル構成:"
tree -I 'venv|__pycache__|*.egg-info|.git' -L 3 2>/dev/null || {
    # treeコマンドがない場合はfindを使用
    find . -path ./venv -prune -o -path './__pycache__' -prune -o -path './*.egg-info' -prune -o -path './.git' -prune -o -type f -print | grep -E '\.(py|json|md|txt|toml)$' | sort | sed 's/^/   /'
}
echo ""

# 9. サマリー
echo "======================================"
echo " 動作確認完了"
echo "======================================"
echo ""
echo "次のステップ:"
echo "  1. Issue #2: JSON入力処理機能の実装"
echo "  2. Issue #3: MIDI変換処理の実装"
echo "  3. Issue #4: MIDI出力機能の実装"
echo ""
echo "開発を開始するには:"
echo "  source venv/bin/activate"
echo "  ipython  # インタラクティブな開発"
echo ""