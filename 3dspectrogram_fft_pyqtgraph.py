import sys
import time
import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import scipy.signal as signal
import soundfile as sf
from pyqtgraph.Qt import QtCore, QtGui


class Visualizer(object):
    def __init__(self, data, fs):

        # setup window and camera
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        # self.w.opts['distance'] = 40
        self.w.setWindowTitle('test')
        self.w.setGeometry(0, 30, 1280, 720)

        self.w.pan(10, 500, 100)
        self.w.setCameraPosition(distance=20000, elevation=30, azimuth=-135)
        self.w.show()

        self.data = data
        self.fs = fs

        # set window relative to fps so we grab the appropriate number of samples
        self.animation_fps = 60
        self.window = fs // self.animation_fps

        # make frame big so we can see some history
        self.frame = 256*self.window
        self.chunks = self.frame*2 // self.window
        self.nframes = len(self.data)//self.window  # wrong?

        self.fft = -50*np.ones((self.window//2 + 1, self.chunks))
        self.f = np.linspace(0, self.fs//2, self.window//2+1)
        self.t = np.linspace(0, self.fs/self.frame, self.chunks)

        self.start = 0
        self.stop = self.window

        self.cmap = plt.get_cmap('inferno')
        # zvalues - min / (max - min)
        self.colors = self.cmap((self.fft+50)/(0+50))

        self.surface = gl.GLSurfacePlotItem(
            self.f, self.t, self.fft, colors=self.colors, computeNormals=False)
        # scale so we have a square
        self.surface.scale(1, np.max(self.f)/np.max(self.t), 100)

        self.w.addItem(self.surface)

    def run(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def update(self):
        # stime = time.time()

        # get fft of new chunk
        tmp = np.fft.rfft(self.data[self.start:self.stop]
                          * signal.get_window('blackmanharris', self.window))
        tmp = 20*np.log10(np.abs(tmp)*2 /
                          np.sum(signal.get_window('blackmanharris', self.window)))

        # roll array
        self.fft = np.roll(self.fft, 1)
        self.fft[:, 1] = tmp

        self.start += self.window  # // 2
        self.stop += self.window  # // 2

        if self.stop > len(self.data):
            quit()

        self.colors = self.cmap((self.fft+50)/(0+50))
        self.surface.setData(self.f, self.t, self.fft, colors=self.colors)

        # print(self.w.cameraPosition())

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(1000/self.animation_fps)
        self.run()


# Start event loop.
if __name__ == '__main__':

    input_file = "D:/git/Misc/07 Mind's Mirrors.wav"
    # input_file = "D:/git/Misc/07 Break Those Bones Whose Sinews Gave It Motion.wav"
    # input_file = "./test.wav"
    # input_file = "./01 6_00.wav"

    data_stereo, fs = sf.read(input_file)
    # only one channel for now, downmix @TODO
    data = np.array(data_stereo[:, 1])

    pg.setConfigOptions(useOpenGL=True, antialias=True)  # turn of aa if laggy
    v = Visualizer(data, fs)

    # data_stereo = np.concatenate((np.zeros((v.window, 2)), data_stereo)) # shitty delay compensation
    data_stereo *= 32767 / np.max(np.abs(data_stereo))
    data_stereo = data_stereo.astype(np.int16)

    sd.play(data_stereo, fs)
    v.animation()
