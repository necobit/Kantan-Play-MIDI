"""
カスタム例外クラス
"""


class KantanPlayMIDIError(Exception):
    """基底例外クラス"""
    pass


class InvalidInputError(KantanPlayMIDIError):
    """入力データが不正な場合の例外"""
    pass


class MIDIDeviceError(KantanPlayMIDIError):
    """MIDIデバイス関連のエラー"""
    pass


class ConfigurationError(KantanPlayMIDIError):
    """設定ファイル関連のエラー"""
    pass