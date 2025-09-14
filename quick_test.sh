#!/bin/bash
# MIDI演奏の簡単テストスクリプト

echo "=== かんぷれMIDI演奏テスト ==="

# MIDIポート確認
echo "1. MIDIポート確認..."
python -c "
import rtmidi
midi_out = rtmidi.MidiOut()
ports = midi_out.get_ports()
if ports:
    print(f'利用可能: {ports[0]}')
    port = ports[0]
else:
    print('MIDIポートなし')
    exit(1)
midi_out.delete()
" || exit 1

# ポート名を取得
PORT=$(python -c "
import rtmidi
midi_out = rtmidi.MidiOut()
ports = midi_out.get_ports()
if ports: print(ports[0])
midi_out.delete()
")

echo "2. 演奏開始..."
kantan-play-midi test_performance.json --play --midi-port "$PORT" -v

echo "3. テスト完了！"