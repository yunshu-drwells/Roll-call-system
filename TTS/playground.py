import wave

import numpy as np
import pyaudio

from TTS.TTService import TTService

# 定义一个`config_combo`列表，这是一个包含多个元组的列表，每个元组表示一个配置文件和一个预训练模型的路径。
# 这些配置文件和模型是针对不同的角色或风格的语音合成的
config_combo = [
        # ("TTS/models/CyberYunfei3k.json", "TTS/models/yunfei3k_69k.pth"),
        # ("TTS/models/paimon6k.json", "TTS/models/paimon6k_390k.pth"),
        # ("TTS/models/ayaka.json", "TTS/models/ayaka_167k.pth"),
        # ("TTS/models/ningguang.json", "TTS/models/ningguang_179k.pth"),
        # ("TTS/models/nahida.json", "TTS/models/nahida_129k.pth"),
        # ("TTS/models_unused/miko.json", "TTS/models_unused/miko_139k.pth"),
        # ("TTS/models_unused/yoimiya.json", "TTS/models_unused/yoimiya_102k.pth"),
        # ("TTS/models/noelle.json", "TTS/models/noelle_337k.pth"),
        # ("TTS/models_unused/yunfeimix.json", "TTS/models_unused/yunfeimix_122k.pth"),
        # ("TTS/models_unused/yunfeineo.json", "TTS/models_unused/yunfeineo_25k.pth"),
        # ("TTS/models/yunfeimix2.json", "TTS/models/yunfeimix2_47k.pth")
        ("TTS/models_unused/zhongli.json", "TTS/models_unused/zhongli_44k.pth"),
    ]
#  使用`for`循环遍历`config_combo`列表中的每个元组，分别创建一个`TTService`实例，传入配置文件，模型，角色名称和语音速度作为参数
for cfg, model in config_combo:
    a = TTService(cfg, model, 'test', 1)  # 这里的角色名称是`test`，语音速度是`1`
    p = pyaudio.PyAudio()  # 使用`pyaudio.PyAudio`方法创建一个`pyaudio`对象，这是一个用于处理音频输入输出的对象
    audio = a.read('旅行者，今天是星期四，能否威我五十')  # 调用`TTService`实例的`read`方法，传入一个文本作为参数，得到一个语音的波形数据
    # 使用`pyaudio`对象的`open`方法创建一个`stream`对象，这是一个用于播放音频的对象。设置音频的格式，通道数，采样率和输出模式
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=a.hps.data.sampling_rate,
                    output=True
                    )
    data = audio.astype(np.float32).tostring()  # 将波形数据转换为`numpy`数组，并转换为字符串格式，赋值给`data`变量
    stream.write(data)  #  使用`stream`对象的`write`方法，将`data`变量中的字符串写入音频流中，实现语音的播放
    # Set the output file name
    output_file = "output.wav"  # 设置一个输出文件的名称

    # Set the audio properties
    num_channels = 1
    sample_width = 2  # Assuming 16-bit audio
    frame_rate = a.hps.data.sampling_rate

    # Convert audio data to 16-bit integers
    audio_int16 = (audio * np.iinfo(np.int16).max).astype(np.int16)  # 设置一些音频的属性，如通道数，采样宽度，采样率等。这里假设音频是16位的，所以采样宽度是2字节

    # Open the output file in write mode
    with wave.open(output_file, 'wb') as wav_file:  # 使用`wave.open`方法打开输出文件，以写入模式。
        # Set the audio properties 设置音频的属性
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(frame_rate)

        # Write audio data to the file
        wav_file.writeframes(audio_int16.tobytes())  # 使用`wav_file`对象的`writeframes`方法，将`audio_int16`变量中的字节数据写入文件中，实现语音的保存