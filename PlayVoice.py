# 使用跨平台的sounddevice库播放音频
# 跨平台+支持选择播放设备
# python-sounddevice+PortAudio
# pyaudio+PortAudio
import os
import re
import time
import wave
import numpy as np
import soundfile as sf
import sounddevice as sd
from TTS import TTService
from playsound import playsound

class PlayVoice():
    def __init__(self, hardware):  # 音频合成设备
        # self.devices = sd.query_devices()
        self.devices = sd.query_devices(kind='output')  # 只搜索音频输出设备
        self.models()  # 搜索所有可用的tts模型
        self.hardware = hardware  # 音频合成设备

    def initTTS(self, character):  # 指定演员，并创建tts对象用于合成音频
        self.character = character
        self.tts = TTService.TTService(*self.char_name[self.character],
                                       self.hardware)  # cfg, model, char, speed:  # `cfg`是配置文件的路径，`model`是预训练模型的路径，`char`是要合成的角色的名称，`speed`是语音的速度

    # def change_speed(self, character, speed):
    #     self.char_name[character][3] = float(speed)
    #     self.tts = TTService.TTService(*self.char_name[self.character],
    #                                    self.hardware)  # cfg, model, char, speed:  # `cfg`是配置文件的路径，`model`是预训练模型的路径，`char`是要合成的角色的名称，`speed`是语音的速度

    def get_characters(self):  # 获取所有的演员列表
        return list(self.char_name.keys())

    def models(self):  # 搜索所有可用的tts模型
        self.char_name = {}
        # 搜索TTS/models
        char_name = []
        for entry in os.scandir('TTS/models'):
            if entry.is_dir():
                char_name.append(entry.name)
        cfgs = []
        models = []
        for char in char_name:
            for entry in os.listdir('TTS/models'+'/'+char):
                pattern1 = r'.*.json'
                pattern2 = r'.*.pth'
                res1 = re.search(pattern1, entry)
                res2 = re.search(pattern2, entry)
                if res1 is not None:
                    print()
                    cfgs.append('TTS/models'+'/'+char+'/'+res1.group(0))
                if res2 is not None:
                    models.append('TTS/models'+'/'+char+'/'+res2.group(0))
        for i in range(len(char_name)):
            self.char_name[char_name[i]] = [cfgs[i], models[i], 'character_'+char_name[i], 1]
        # print("self.char_name", self.char_name)


    def set_hardware(self, hardware):  # 设置音频合成设备
        self.hardware = hardware
        self.tts = TTService.TTService(*self.char_name[self.character],
                                       self.hardware)

    def generate_voice_file(self, resp_text):  # 通过字符生成音频文件（deprecated）
        tmp_proc_file = 'tmp/server_processed.wav'
        self.tts.read_save(resp_text, tmp_proc_file,
                      self.tts.hps.data.sampling_rate)  # 调用 `self.tts.read_save()` 方法，将文本转换为语音，并保存到 `tmp_proc_file` 中
        return tmp_proc_file

    def play_voice_file(self, resp_text, device_index):  # 调用generate_voice并通过指定设备播放音频（deprecated）
        file_path = self.generate_voice_file(resp_text)
        # 设置默认的输出设备
        sd.default.device = device_index
        # 从wav文件中读取音频数据和采样率
        data, fs = sf.read(file_path, dtype='float32')
        # 播放音频
        sd.play(data, fs)
        # 等待播放完成
        status = sd.wait()

    def generate_voice(self, resp_text):  # 通过字符生成音频文件
        audio = self.tts.read(resp_text)
        return audio

    def play_voice(self, resp_text, device_index):  # 调用generate_voice并通过指定设备播放音频
        audio = self.generate_voice(resp_text)  # 获得音频波形数据
        # 设置默认的输出设备
        sd.default.device = device_index
        # 从numpy数组中读取音频数据和采样率
        # fs, data = scipy.io.wavfile.read(audio)  # 读取采样率和音频数据
        # 播放音频
        sd.play(audio, self.tts.hps.data.sampling_rate)
        # 等待播放完成
        status = sd.wait()

    def get_devices(self):
        # print("self.devices: ", self.devices)
        # print("enumerate(self.devices): ", enumerate(self.devices))
        # res = ["{}".format(device['name']) for i, device in enumerate(self.devices)]
        devices_list = []
        indexs = []
        if type(self.devices['name']) == str:
            devices_list = [self.devices['name']]
            indexs = [self.devices['index']]
        else:
            devices_list = self.devices['name']
            devices_list = self.devices['index']
        res = ["{} {}".format(index, dev) for dev in devices_list for index in indexs]
        # print(res)
        return res

    def play_voice_(self, path):
        playsound(path)

    def play_voice_audio_file(self, audio_file, device_index):
        # Load the audio file
        with wave.open(audio_file, 'rb') as wf:
            audio_data = wf.readframes(-1)
            sample_width = wf.getsampwidth()
            channels = wf.getnchannels()
            sample_rate = wf.getframerate()
            # Convert the audio data to a NumPy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # 设置默认的输出设备
        sd.default.device = device_index
        # Play the audio
        sd.play(audio_array, sample_rate)
        sd.wait()

    # 点名（列表）
    def roll_call_list(self, stu_names, device_index, pause):
        for i in stu_names:
            time.sleep(pause)
            self.play_voice(i, device_index)

    # 点一个名字
    def roll_call(self, stu_name, device_index, pause):
        time.sleep(pause)
        self.play_voice(stu_name, device_index)


del PlayVoice.generate_voice_file
del PlayVoice.play_voice_file


if __name__ == '__main__':
    pv = PlayVoice('cuda')
    dvs = pv.get_devices()
    # print(dvs)
    pv.initTTS('paimon')
    resp_text = "张三 李四 王五"
    # pv.play_voice_file(resp_text, 3)
    # pv.play_voice(resp_text, 3)
    # pv.change_speed('paimon', 1)
    # pv.play_voice(resp_text, 3)
    pv.play_voice_audio_file('./sources/ohhhh.wav', 3)


'''
self.devices {'name': '扬声器 (Realtek High Definition Au', 'index': 3, 'hostapi': 0, 'max_input_channels': 0, 'max_output_channels': 2, 'default_low_input_latency': 0.09, 'default_low_output_latency': 0.09, 'default_high_input_latency': 0.18, 'default_high_output_latency': 0.18, 'default_samplerate': 44100.0}
'''

'''
# 查询可用的音频设备
devices = sd.query_devices()
# 打印设备列表
for i, device in enumerate(devices):
    print(i, device['name'])
# 让用户输入设备索引
index = int(input('请输入您想要使用的设备索引：'))
# 设置默认的输出设备
sd.default.device = index

# 从wav文件中读取音频数据和采样率
filename = 'myfile.wav'
data, fs = sf.read(filename, dtype='float32')
# 播放音频
sd.play(data, fs)
# 等待播放完成
status = sd.wait()
'''