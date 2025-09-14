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
from .processor import PerformanceProcessor
from .player import MIDIPlayer, PlaybackState
from .exceptions import KantanPlayMIDIError, MIDIDeviceError


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
    '--play',
    is_flag=True,
    help='実際にMIDI演奏を実行する'
)
@click.option(
    '--speed', '-s',
    type=float,
    default=1.0,
    show_default=True,
    help='再生スピード倍率（1.0=等速, 2.0=2倍速）'
)
@click.option(
    '--double-speed',
    is_flag=True,
    help='2倍速のショートカット（--speed 2.0 と同じ）'
)
@click.option(
    '--midi-port',
    type=str,
    help='使用するMIDIポート名'
)
@click.option(
    '--list-ports',
    is_flag=True,
    help='利用可能なMIDIポートを一覧表示'
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
    play: bool,
    midi_port: Optional[str],
    list_ports: bool,
    verbose: bool,
    speed: float,
    double_speed: bool
) -> None:
    """
    Kantan Play MIDI - JSON入力からMIDI演奏を実行
    
    INPUT_FILE: 演奏データのJSONファイル
    """
    try:
        # MIDIポート一覧表示
        if list_ports:
            _list_midi_ports()
            return

        if verbose:
            console.print(f"[blue]入力ファイル:[/blue] {input_file}")
            console.print(f"[blue]設定ファイル:[/blue] {config}")
            if midi_port:
                console.print(f"[blue]MIDIポート:[/blue] {midi_port}")
            console.print()

        # 入力ファイルの読み込みと検証
        console.print("[yellow]📖 入力ファイルを読み込み中...[/yellow]")
        handler = InputHandler()
        performance = handler.load_from_file(input_file)

        # 再生スピード設定
        if double_speed:
            speed = 2.0
        if speed <= 0:
            speed = 1.0
        effective_tempo = max(20, min(600, int(round(performance.tempo * speed))))
        
        # 詳細検証
        handler.validate_performance(performance)
        
        console.print("[green]✅ 入力ファイルの検証が完了しました[/green]")
        
        if verbose:
            _display_performance_info(performance)
            if speed != 1.0:
                console.print(f"[blue]再生テンポ:[/blue] {effective_tempo} BPM (x{speed:.2f})")

        if validate_only:
            console.print("[blue]🔍 検証モードで実行されました[/blue]")
            return

        # MIDI設定の読み込み
        console.print("[yellow]🎵 MIDI設定を読み込み中...[/yellow]")
        midi_config = MIDIConfig(config)
        processor = PerformanceProcessor(midi_config)
        
        console.print("[green]✅ MIDI設定の読み込みが完了しました[/green]")

        # シーケンス生成
        sequence = processor.process_performance(performance, tempo_scale=speed)

        if show_conversion or verbose:
            _display_conversion_results(performance, processor.converter)
            _display_sequence_info(sequence)

        # MIDI演奏の実行
        if play:
            _execute_midi_playback(sequence, midi_port)
        else:
            console.print("[blue]💡 実際の演奏を行うには --play オプションを追加してください[/blue]")

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


def _list_midi_ports() -> None:
    """利用可能なMIDIポートを一覧表示"""
    try:
        player = MIDIPlayer()
        ports = player.get_available_ports()
        
        if ports:
            console.print("[green]🎹 利用可能なMIDIポート:[/green]")
            for i, port in enumerate(ports):
                console.print(f"  [{i}] {port}")
        else:
            console.print("[yellow]⚠️  利用可能なMIDIポートが見つかりません[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ MIDIポート取得エラー: {e}[/red]")


def _display_sequence_info(sequence) -> None:
    """シーケンス情報を表示"""
    console.print(f"\n[yellow]🎼 演奏シーケンス情報:[/yellow]")
    console.print(f"  総イベント数: {len(sequence.events)}")
    console.print(f"  演奏時間: {sequence.total_duration:.2f}秒")


def _execute_midi_playback(sequence, midi_port: Optional[str]) -> None:
    """MIDI演奏を実行"""
    player = MIDIPlayer()
    
    try:
        # MIDI接続
        console.print("[yellow]🔌 MIDIデバイスに接続中...[/yellow]")
        player.connect(midi_port)
        console.print(f"[green]✅ MIDIポート '{player.midi_port}' に接続しました[/green]")
        
        # 演奏開始
        console.print(f"[green]🎵 演奏を開始します... (時間: {sequence.total_duration:.1f}秒)[/green]")
        console.print("[dim]Ctrl+C で演奏を停止できます[/dim]")
        
        player.play_sequence(sequence)
        
        # 演奏完了まで待機
        import time
        try:
            while player.get_state() == PlaybackState.PLAYING:
                current_time = player.get_current_time()
                progress = (current_time / sequence.total_duration) * 100
                console.print(f"\r[blue]進行: {current_time:.1f}s / {sequence.total_duration:.1f}s ({progress:.1f}%)[/blue]", end="")
                time.sleep(0.1)
        except KeyboardInterrupt:
            console.print(f"\n[yellow]⏸️  ユーザーによって演奏が停止されました[/yellow]")
            player.stop()
            
        console.print(f"\n[green]🎉 演奏が完了しました！[/green]")
        
    except MIDIDeviceError as e:
        console.print(f"[red]🎹 MIDIエラー: {e}[/red]")
        console.print("[blue]💡 利用可能なMIDIポートを確認するには: --list-ports[/blue]")
    except Exception as e:
        console.print(f"[red]💥 演奏エラー: {e}[/red]")
    finally:
        player.disconnect()


if __name__ == '__main__':
    main()
