# coding=utf8
import os
import re
import wave
import numpy as np
import pyaudio
import matplotlib.pylab as pl

class voice():
    def loaddata(self, filepath):
        '''

        :param filepath: 文件路径，为wav文件
        :return: 如果无异常则返回True，如果有异常退出并返回False
        self.wave_data内储存着多通道的音频数据，其中self.wave_data[0]代表第一通道
        具体有几通道，看self.nchannels
        '''
        if type(filepath) != str:
            print('the type of filepath must be string')
            return False
        p1 = re.compile('\.wav')
        if p1.findall(filepath) is None:
            print ('the suffix of file must be .wav')
            return False
        try:
            f = wave.open(filepath, 'rb')
            params = f.getparams()
            #声道数, 量化位数（byte单位）, 采样频率,采样点数
            #2 2 48000 975872
            self.nchannels, self.sampwidth, self.framerate, self.nframes = params[:4]
            str_data = f.readframes(self.nframes)

            #格式化
            self.wave_data = np.fromstring(str_data, dtype=np.short)
            #-1表示自动处理  只有一个维度可以是-1
            print(self.wave_data.shape)
            #（1 2）（3 4）（5 6）（7 8）
            self.wave_data.shape = -1, self.sampwidth
            print(self.wave_data.shape)
            #转换维度 与线代中的转置相同
            # （1 3 5 7）（2 4 6 8）
            self.wave_data = self.wave_data.T
            print( self.nchannels, self.sampwidth, self.framerate, self.nframes)
            print(self.wave_data.shape)
            f.close()
            time = np.arange(0, self.nframes) * (1.0 / self.framerate)

            # 绘制波形
            pl.subplot(211)
            pl.plot(time, self.wave_data[0])
            pl.subplot(212)
            pl.plot(time, self.wave_data[1], c="g")
            pl.xlabel("time (seconds)")

            pl.savefig(filepath[:-4]+".jpg")

            self.name = os.path.basename(filepath)  # 记录下文件名
            return True
        except:
            print
            'File Error!'

    def fft(self, frames=40):
        '''
        :param frames: frames是指定每秒钟分块数
        :return:
        '''
        block = []
        fft_blocks = []
        self.high_point = []
        blocks_size = int(self.framerate / frames)  # block_size为每一块的frame数量
        blocks_num = self.nframes / blocks_size  # 将音频分块的数量
        for i in range(0, len(self.wave_data[0]) - int(blocks_size), int(blocks_size)):
            block.append(self.wave_data[0][i:i + blocks_size])
            #快速傅里叶变换
            fft_blocks.append(np.abs(np.fft.fft(self.wave_data[0][i:i + blocks_size])))
            if i==0 :
                print(len(fft_blocks[-1]))
            self.high_point.append((np.argmax(fft_blocks[-1][:40]),
                                    np.argmax(fft_blocks[-1][40:80]) + 40,
                                    np.argmax(fft_blocks[-1][80:120]) + 80,
                                    np.argmax(fft_blocks[-1][120:180]) + 120,
                                    np.argmax(fft_blocks[-1][180:300]) + 180,
                                    ))  # 提取指纹的关键步骤，没有取最后一个，但是保留了这一项，可以想想为什么去掉了？

    def play(self, filepath):
        '''
        用来做音频播放的方法
        :param filepath:文件路径
        :return:
        '''
        chunk = 1024
        filepath="C:\\Users\\37301\\Desktop\\music\\songs\\"+filepath
        wf = wave.open(filepath, 'rb')
        p = pyaudio.PyAudio()
        # 打开声音输出流
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        # 写声音输出流进行播放
        while True:
            data = wf.readframes(chunk)
            if data == "":
                break
            stream.write(data)

        stream.close()
        p.terminate()


