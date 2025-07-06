"""
MIDI演奏機能のテスト
"""
import time
import pytest
from unittest.mock import Mock, patch

from kantan_play_midi.player import MIDIPlayer, PlaybackState
from kantan_play_midi.sequence import PlaybackSequence, MIDIEvent, MIDIEventType
from kantan_play_midi.exceptions import MIDIDeviceError


class TestMIDIPlayer:
    """MIDIPlayerクラスのテスト"""

    @pytest.fixture
    def player(self):
        """MIDIPlayerのインスタンス"""
        return MIDIPlayer()

    @pytest.fixture
    def simple_sequence(self):
        """シンプルなテストシーケンス"""
        events = [
            MIDIEvent(0.0, MIDIEventType.NOTE_ON, 60),
            MIDIEvent(0.1, MIDIEventType.NOTE_OFF, 60),
            MIDIEvent(0.5, MIDIEventType.NOTE_ON, 64),
            MIDIEvent(0.6, MIDIEventType.NOTE_OFF, 64),
        ]
        return PlaybackSequence(
            events=events,
            total_duration=1.0,
            slot=1,
            tempo=120
        )

    @patch('rtmidi.MidiOut')
    def test_get_available_ports(self, mock_midi_out, player):
        """利用可能ポートの取得"""
        mock_instance = Mock()
        mock_instance.get_ports.return_value = ["Port1", "Port2"]
        mock_midi_out.return_value = mock_instance

        ports = player.get_available_ports()
        assert ports == ["Port1", "Port2"]
        mock_instance.delete.assert_called_once()

    @patch('rtmidi.MidiOut')
    def test_connect_success(self, mock_midi_out, player):
        """MIDI接続成功"""
        mock_instance = Mock()
        mock_instance.get_ports.return_value = ["TestPort"]
        mock_instance.is_port_open.return_value = True
        mock_midi_out.return_value = mock_instance

        player.connect("TestPort")
        
        assert player.midi_port == "TestPort"
        assert player.is_connected()
        mock_instance.open_port.assert_called_once_with(0)

    @patch('rtmidi.MidiOut')
    def test_connect_no_ports(self, mock_midi_out, player):
        """利用可能ポートがない場合"""
        mock_instance = Mock()
        mock_instance.get_ports.return_value = []
        mock_midi_out.return_value = mock_instance

        with pytest.raises(MIDIDeviceError, match="No MIDI output ports available"):
            player.connect()

    @patch('rtmidi.MidiOut')
    def test_connect_port_not_found(self, mock_midi_out, player):
        """指定ポートが見つからない場合"""
        mock_instance = Mock()
        mock_instance.get_ports.return_value = ["Port1", "Port2"]
        mock_midi_out.return_value = mock_instance

        with pytest.raises(MIDIDeviceError, match="MIDI port 'InvalidPort' not found"):
            player.connect("InvalidPort")

    def test_send_note_without_connection(self, player):
        """接続なしでのMIDI送信エラー"""
        with pytest.raises(MIDIDeviceError, match="MIDI device not connected"):
            player.send_note_on(60)

        with pytest.raises(MIDIDeviceError, match="MIDI device not connected"):
            player.send_note_off(60)

    @patch('rtmidi.MidiOut')
    def test_send_midi_messages(self, mock_midi_out, player):
        """MIDIメッセージ送信"""
        mock_instance = Mock()
        mock_instance.get_ports.return_value = ["TestPort"]
        mock_instance.is_port_open.return_value = True
        mock_midi_out.return_value = mock_instance

        player.connect()

        # ノートオン
        player.send_note_on(60, 100)
        mock_instance.send_message.assert_called_with([0x90, 60, 100])

        # ノートオフ
        player.send_note_off(60)
        mock_instance.send_message.assert_called_with([0x80, 60, 0])

    def test_initial_state(self, player):
        """初期状態のテスト"""
        assert player.get_state() == PlaybackState.STOPPED
        assert player.get_current_time() == 0.0

    @patch('rtmidi.MidiOut')
    def test_playback_state_without_connection(self, mock_midi_out, player, simple_sequence):
        """接続なしでの演奏開始エラー"""
        with pytest.raises(MIDIDeviceError, match="MIDI device not connected"):
            player.play_sequence(simple_sequence)

    @patch('rtmidi.MidiOut')
    def test_playback_basic_functionality(self, mock_midi_out, player, simple_sequence):
        """基本的な演奏機能"""
        mock_instance = Mock()
        mock_instance.get_ports.return_value = ["TestPort"]
        mock_instance.is_port_open.return_value = True
        mock_midi_out.return_value = mock_instance

        player.connect()
        
        # 演奏開始
        player.play_sequence(simple_sequence)
        assert player.get_state() == PlaybackState.PLAYING

        # 少し待機
        time.sleep(0.2)

        # 停止
        player.stop()
        assert player.get_state() == PlaybackState.STOPPED

    @patch('rtmidi.MidiOut')
    def test_pause_resume_functionality(self, mock_midi_out, player, simple_sequence):
        """一時停止・再開機能"""
        mock_instance = Mock()
        mock_instance.get_ports.return_value = ["TestPort"]
        mock_instance.is_port_open.return_value = True
        mock_midi_out.return_value = mock_instance

        player.connect()
        player.play_sequence(simple_sequence)

        # 一時停止
        player.pause()
        assert player.get_state() == PlaybackState.PAUSED

        # 再開
        player.resume()
        assert player.get_state() == PlaybackState.PLAYING

        player.stop()

    @patch('rtmidi.MidiOut')
    def test_already_playing_error(self, mock_midi_out, player, simple_sequence):
        """既に演奏中の場合のエラー"""
        mock_instance = Mock()
        mock_instance.get_ports.return_value = ["TestPort"]
        mock_instance.is_port_open.return_value = True
        mock_midi_out.return_value = mock_instance

        player.connect()
        player.play_sequence(simple_sequence)

        # 既に演奏中の状態で再度演奏開始を試行
        with pytest.raises(MIDIDeviceError, match="Already playing"):
            player.play_sequence(simple_sequence)

        player.stop()

    @patch('rtmidi.MidiOut')
    def test_disconnect_during_playback(self, mock_midi_out, player, simple_sequence):
        """演奏中の切断"""
        mock_instance = Mock()
        mock_instance.get_ports.return_value = ["TestPort"]
        mock_instance.is_port_open.return_value = True
        mock_midi_out.return_value = mock_instance

        player.connect()
        player.play_sequence(simple_sequence)

        # 切断（演奏も停止される）
        player.disconnect()
        assert player.get_state() == PlaybackState.STOPPED
        assert not player.is_connected()

    def test_button_press_simulation(self, player):
        """ボタン押下シミュレーション（モック使用）"""
        # send_note_on/offをモック
        player.send_note_on = Mock()
        player.send_note_off = Mock()

        with patch('time.sleep') as mock_sleep:
            player.press_button(60, 100)

            player.send_note_on.assert_called_once_with(60)
            player.send_note_off.assert_called_once_with(60)
            mock_sleep.assert_called_once_with(0.1)  # 100ms = 0.1s

    @patch('rtmidi.MidiOut')
    def test_all_notes_off_on_stop(self, mock_midi_out, player):
        """停止時の全ノートオフ"""
        mock_instance = Mock()
        mock_instance.get_ports.return_value = ["TestPort"]
        mock_instance.is_port_open.return_value = True
        mock_midi_out.return_value = mock_instance

        player.connect()
        player.stop()

        # 全ノートオフが送信されることを確認
        # (実際には128回呼ばれるが、呼ばれていることを確認)
        assert mock_instance.send_message.call_count > 0

    def test_destructor_cleanup(self, player):
        """デストラクタでのクリーンアップ"""
        player.disconnect = Mock()
        
        # デストラクタ呼び出し
        player.__del__()
        
        player.disconnect.assert_called_once()