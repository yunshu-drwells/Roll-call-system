import sys
import time

sys.path.append('./TTS/vits')

import soundfile
import os
os.environ["PYTORCH_JIT"] = "0"
import torch

# print("TTService", sys.path)

import TTS.vits.commons as commons
import TTS.vits.utils as utils

from TTS.vits.models import SynthesizerTrn
from TTS.vits.text.symbols import symbols
from TTS.vits.text import text_to_sequence

import logging
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

# 将文本转换为序列，用于输入VITS模型
def get_text(text, hps):
    text_norm = text_to_sequence(text, hps.data.text_cleaners)  # 该函数根据`hps.data.text_cleaners`参数对文本进行清洗和规范化
    if hps.data.add_blank:  # 如果`hps.data.add_blank`为真，那么在文本序列中插入空白符
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm)  # 将文本序列转换为`torch.LongTensor`类型
    return text_norm  # 返回


class TTService():
    # 创建一个TTS服务的实例
    # 从配置文件中获取超参数，加载预训练模型，并创建一个`SynthesizerTrn`对象，该对象是VITS模型的实现
    def __init__(self, cfg, model, char, speed, hardware):  # `cfg`是配置文件的路径，`model`是预训练模型的路径，`char`是要合成的角色的名称，`speed`是语音的速度
        logging.info('Initializing TTS Service for %s...' % char)
        self.hps = utils.get_hparams_from_file(cfg)
        self.speed = speed
        self.hardware = hardware
        if self.hardware == 'cuda':
            self.net_g = SynthesizerTrn(
                len(symbols),
                self.hps.data.filter_length // 2 + 1,
                self.hps.train.segment_size // self.hps.data.hop_length,
                **self.hps.model).cuda()
        else:
            self.net_g = SynthesizerTrn(
                len(symbols),
                self.hps.data.filter_length // 2 + 1,
                self.hps.train.segment_size // self.hps.data.hop_length,
                **self.hps.model).cpu()
        _ = self.net_g.eval()
        _ = utils.load_checkpoint(model, self.net_g, None)

    # 用于根据给定的文本合成语音。
    def read(self, text):
        text = text.replace('~', '！')  # 将文本中的`~`符号替换为`！`符号
        stn_tst = get_text(text, self.hps)  # 调用`get_text`函数将文本转换为序列
        with torch.no_grad():
            if self.hardware == 'cuda':
                x_tst = stn_tst.cuda().unsqueeze(0)
                x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cuda()
            else:
                x_tst = stn_tst.cpu().unsqueeze(0)
                x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cpu()
            audio = self.net_g.infer(x_tst, x_tst_lengths, noise_scale=.667, noise_scale_w=0.2, length_scale=self.speed)[0][
                0, 0].data.cpu().float().numpy()  # 使用`self.net_g.infer`方法对序列进行推理，得到语音的波形数据。再将波形数据转换为`numpy`数组并返回
        return audio  # numpy数组

    # 用于根据给定的文本合成语音，并将语音保存为文件
    def read_save(self, text, filename, sr):  # `text`是要合成的文本，`filename`是要保存的文件名，`sr`是语音的采样率
        stime = time.time()
        au = self.read(text)  # 调用`read`方法得到语音的波形数据
        soundfile.write(filename, au, sr)  # 使用`soundfile.write`函数将波形数据写入文件
        logging.info('VITS Synth Done, time used %.2f' % (time.time() - stime))  # 使用`logging.info`函数记录合成语音所用的时间




