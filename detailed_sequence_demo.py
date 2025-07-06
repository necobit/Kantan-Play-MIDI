#!/usr/bin/env python3
"""
詳細なシーケンス生成デモ - 全イベントを表示
"""
from pathlib import Path
from kantan_play_midi import (
    InputHandler, MIDIConfig, PerformanceProcessor
)


def show_all_events():
    print("=== 全MIDIイベント詳細表示 ===\n")
    
    # 1. データ読み込み
    handler = InputHandler()
    performance = handler.load_from_file(Path("example_input.json"))
    
    config = MIDIConfig(Path("MIDI.json"))
    processor = PerformanceProcessor(config)
    sequence = processor.process_performance(performance)
    
    print(f"📊 概要:")
    print(f"   スロット: {sequence.slot}")
    print(f"   テンポ: {sequence.tempo} BPM")
    print(f"   総イベント数: {len(sequence.events)}")
    print(f"   総演奏時間: {sequence.total_duration:.2f}秒")
    print()
    
    # 2. 全イベントの詳細表示
    print("🎵 全MIDIイベント:")
    print("=" * 80)
    print(f"{'No.':<4} {'時刻(秒)':<8} {'イベント種別':<12} {'ノート':<6} {'説明'}")
    print("-" * 80)
    
    for i, event in enumerate(sequence.events, 1):
        print(f"{i:<4} {event.timestamp:<8.3f} {event.event_type.value:<12} "
              f"{event.note:<6} {event.description}")
    
    print("-" * 80)
    print(f"合計: {len(sequence.events)} イベント")
    print()
    
    # 3. イベント種別の統計
    print("📈 イベント統計:")
    event_stats = {}
    for event in sequence.events:
        event_type = event.event_type.value
        event_stats[event_type] = event_stats.get(event_type, 0) + 1
    
    for event_type, count in sorted(event_stats.items()):
        print(f"   {event_type}: {count}回")
    print()
    
    # 4. 時刻別の詳細分析
    print("⏰ 主要タイミング分析:")
    
    # スロット選択
    slot_events = [e for e in sequence.events if e.event_type.value == "slot_press"]
    if slot_events:
        print(f"   スロット選択: {slot_events[0].timestamp:.3f}秒")
    
    # 各音符の開始時刻
    note_starts = {}
    for event in sequence.events:
        if "Note " in event.description and "press 1/8" in event.description:
            note_num = event.description.split("Note ")[1].split(":")[0]
            note_starts[note_num] = event.timestamp
    
    print("   音符開始時刻:")
    for note_num in sorted(note_starts.keys(), key=int):
        print(f"     音符{note_num}: {note_starts[note_num]:.3f}秒")
    print()
    
    # 5. 音符別の詳細
    print("🎼 音符別詳細:")
    current_note = None
    note_events = []
    
    for event in sequence.events:
        if "Note " in event.description:
            note_num = event.description.split("Note ")[1].split(":")[0]
            if current_note != note_num:
                if note_events:
                    _show_note_details(current_note, note_events)
                current_note = note_num
                note_events = []
            note_events.append(event)
    
    # 最後の音符
    if note_events:
        _show_note_details(current_note, note_events)


def _show_note_details(note_num, events):
    print(f"\n   📝 音符{note_num}の詳細:")
    
    # 音符の基本情報を抽出
    degree = None
    modifiers = []
    degree_presses = 0
    
    for event in events:
        if "Degree" in event.description:
            if degree is None:
                degree_part = event.description.split("Degree '")[1].split("'")[0]
                degree = degree_part
            if "press" in event.description:
                degree_presses += 1
        elif "Modifier" in event.description and "press" in event.description:
            mod_info = event.description.split("Modifier")[1].split(" ")[0]
            if mod_info not in modifiers:
                modifiers.append(mod_info)
    
    print(f"     音階: {degree}")
    if modifiers:
        print(f"     モディファイア: {', '.join(modifiers)}")
    else:
        print(f"     モディファイア: なし")
    print(f"     degree押下回数: {degree_presses}回")
    
    # タイミング詳細
    start_time = min(e.timestamp for e in events)
    end_time = max(e.timestamp for e in events)
    print(f"     演奏時間: {start_time:.3f}秒 ～ {end_time:.3f}秒 ({end_time-start_time:.3f}秒間)")


if __name__ == "__main__":
    try:
        show_all_events()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()