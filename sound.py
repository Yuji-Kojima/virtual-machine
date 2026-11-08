# sound.py : sema の音源(矩形波を1チャンネルだけ鳴らす)
#
# 流れ:
#   スピーカーは「次の音のデータをください」と何度も呼んでくる。
#   その呼び出しに応えて、四角い波の数字の列を作って渡す。
#   これが callback() の仕事。
#
# VM からは  sound.freq = 440.0  のように書き換えるだけでいい(0なら無音)。

#Claudeをかなり使用して制作

import numpy as np
import sounddevice as sd

SR = 22050          # 1秒あたりのサンプル数(音の細かさ)
VOLUME = 0.2        # 音量 0.0 ~ 1.0
kind = [0, 0, 1, 2]          # 0=矩形波, 1=波形メモリ, 2=ノイズ
wavetable = [0] * 32         # 波形メモリの表(0〜15 を32個)
freq = [0.0,0.0,0.0,0.0]          # 今鳴らす周波数[Hz]。0 なら無音
phase = [0.0,0.0,0.0,0.0]         # 波の位置 0.0 ~ 1.0 (前回の終わりを覚えておく)
duty = [0.5,0.5,0.5,0.5]
vol = [1.0,1.0,1.0,1.0]
noise_val = 1.0              # ノイズの「いまの値」を覚えておく

# GB仕様: LFSRノイズ用のレジスタ状態記憶
lfsr_reg = 0x7FFF     # 15bitシフトレジスタ初期値
lfsr_short = False   # Trueにすると金属的な短周期ノイズ(7bit)
lfsr_val = 1.0       # 現在の出力レベル

def callback(outdata, frames, time, status):
    """スピーカーに頼まれるたびに呼ばれる。frames 個ぶんの数字を outdata に入れる。""" 
    global noise_val
    mix = np.zeros(frames, dtype=np.float32)
    
    for ch in range(4):
        if freq[ch] == 0:
            continue
    # 1サンプル進むごとに波の位置は freq/SR だけ進む
        ph = phase[ch] + freq[ch] / SR * np.arange(1, frames + 1)
        phase[ch] = ph[-1] % 1.0        # 次回の続きのために位置を覚える(つなぎ目のプチッを防ぐ)
        if kind[ch] == 0:                                   # 矩形波
            wave = np.where(ph % 1.0 < duty[ch], 1.0, -1.0)
        elif kind[ch] == 1:                                 # 波形メモリ
            table = np.array(wavetable, dtype=np.float32) / 7.5 - 1.0   # 0〜15 を -1〜+1 に
            wave = table[(ph % 1.0 * 32).astype(int) % 32]
        else:                                               # ノイズ
            steps = np.floor(ph).astype(int)                # 何回ぶん「乱数を変える時刻」が来たか
            vals = np.concatenate(([noise_val], np.random.choice([-1.0, 1.0], steps[-1])))
            wave = vals[steps]
            noise_val = vals[-1]
        mix += wave * VOLUME * vol[ch] 
    # 位置の小数部が 0.5 未満なら +、以上なら - → 四角い波
    outdata[:, 0] = mix

stream = sd.OutputStream(samplerate=SR, channels=1, dtype="float32",
                         blocksize=256, callback=callback)
stream.start()
