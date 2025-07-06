"""
CLIインターフェース
"""
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .input_handler import InputHandler
from .config import MIDIConfig
from .converter import MIDIConverter
from .exceptions import KantanPlayMIDIError


console = Console()


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--config',
    type=click.Path(exists=True, path_type=Path),
    default='MIDI.json',
    help='MIDI設定ファイルのパス (デフォルト: MIDI.json)'
)
@click.option(
    '--validate-only',
    is_flag=True,
    help='入力ファイルの検証のみを行う'
)
@click.option(
    '--show-conversion',
    is_flag=True,
    help='変換結果を表示する'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='詳細な情報を表示'
)
def main(
    input_file: Path,
    config: Path,
    validate_only: bool,
    show_conversion: bool,
    verbose: bool
) -> None:
    """
    Kantan Play MIDI - JSON入力からMIDI演奏を実行
    
    INPUT_FILE: 演奏データのJSONファイル
    """
    try:
        if verbose:
            console.print(f"[blue]入力ファイル:[/blue] {input_file}")
            console.print(f"[blue]設定ファイル:[/blue] {config}")
            console.print()

        # 入力ファイルの読み込みと検証
        console.print("[yellow]📖 入力ファイルを読み込み中...[/yellow]")
        handler = InputHandler()
        performance = handler.load_from_file(input_file)
        
        # 詳細検証
        handler.validate_performance(performance)
        
        console.print("[green]✅ 入力ファイルの検証が完了しました[/green]")
        
        if verbose:
            _display_performance_info(performance)

        if validate_only:
            console.print("[blue]🔍 検証モードで実行されました[/blue]")
            return

        # MIDI設定の読み込み
        console.print("[yellow]🎵 MIDI設定を読み込み中...[/yellow]")
        midi_config = MIDIConfig(config)
        converter = MIDIConverter(midi_config)
        
        console.print("[green]✅ MIDI設定の読み込みが完了しました[/green]")

        if show_conversion or verbose:
            _display_conversion_results(performance, converter)

        # TODO: 実際のMIDI演奏処理は後のIssueで実装
        console.print("[yellow]🎹 MIDI演奏機能は未実装です[/yellow]")
        console.print("[blue]💡 Issue #4でMIDI出力機能が実装される予定です[/blue]")

    except KantanPlayMIDIError as e:
        console.print(f"[red]❌ エラー: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]💥 予期しないエラー: {e}[/red]")
        if verbose:
            import traceback
            console.print("[red]詳細:[/red]")
            console.print(traceback.format_exc())
        sys.exit(1)


def _display_performance_info(performance) -> None:
    """演奏情報を表示"""
    info_text = f"""スロット: {performance.slot}
テンポ: {performance.tempo} BPM
音符数: {len(performance.notes)}
推定演奏時間: {_estimate_duration(performance):.1f}分"""
    
    console.print(Panel(info_text, title="📊 演奏情報", border_style="blue"))


def _display_conversion_results(performance, converter) -> None:
    """変換結果を表示"""
    console.print("\n[yellow]🔄 MIDI変換結果:[/yellow]")
    
    # スロット変換
    slot_note = converter.convert_slot(performance.slot)
    console.print(f"[blue]スロット {performance.slot}[/blue] → MIDIノート {slot_note}")
    
    # 音符変換（最初の5つまで表示）
    console.print("\n[blue]音符変換:[/blue]")
    for i, note in enumerate(performance.notes[:5], 1):
        degree_note = converter.convert_degree(note.degree)
        console.print(f"  {i}. 音階 '{note.degree}' → MIDIノート {degree_note}")
        
        # モディファイア
        modifiers = []
        for mod_num in [1, 2, 3]:
            mod_value = getattr(note, f"modifier{mod_num}")
            if mod_value > 0:
                mod_note = converter.convert_modifier(mod_num, mod_value)
                modifiers.append(f"Mod{mod_num}({mod_value})→{mod_note}")
        
        if modifiers:
            console.print(f"     モディファイア: {', '.join(modifiers)}")
    
    if len(performance.notes) > 5:
        console.print(f"     ... 他 {len(performance.notes) - 5} 音符")


def _estimate_duration(performance) -> float:
    """演奏時間を推定"""
    total_beats = len(performance.notes) * 8  # 各音符は8回degreeボタンを押す
    return total_beats / (performance.tempo * 4)  # 4拍で1小節


if __name__ == '__main__':
    main()