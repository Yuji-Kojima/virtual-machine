# sound.py : sema の音源(矩形波を1チャンネルだけ鳴らす)
#
# 流れ:
#   スピーカーは「次の音のデータをください」と何度も呼んでくる。
#   その呼び出しに応えて、四角い波の数字の列を作って渡す。
#   これが callback() の仕事。
#
# VM からは  sound.freq = 440.0  のように書き換えるだけでいい(0なら無音)。

#Claudeが制作

import numpy as np
import sounddevice as sd

SR = 22050          # 1秒あたりのサンプル数(音の細かさ)
VOLUME = 0.2        # 音量 0.0 ~ 1.0

freq = 0.0          # 今鳴らす周波数[Hz]。0 なら無音
phase = 0.0         # 波の位置 0.0 ~ 1.0 (前回の終わりを覚えておく)


def callback(outdata, frames, time, status):
    """スピーカーに頼まれるたびに呼ばれる。frames 個ぶんの数字を outdata に入れる。"""
    global phase
    if freq == 0:
        outdata[:] = 0          # 無音
        return
    # 1サンプル進むごとに波の位置は freq/SR だけ進む
    ph = phase + freq / SR * np.arange(1, frames + 1)
    phase = ph[-1] % 1.0        # 次回の続きのために位置を覚える(つなぎ目のプチッを防ぐ)
    # 位置の小数部が 0.5 未満な.nら +、以上なら - → 四角い波
    outdata[:, 0] = np.where(ph % 1.0 < 0.5, VOLUME, -VOLUME)


stream = sd.OutputStream(samplerate=SR, channels=1, dtype="float32",
                         blocksize=256, callback=callback)
stream.start()
