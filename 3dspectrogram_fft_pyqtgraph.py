import sys
import time
import simpleaudio as sa
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import scipy.signal as signal
import soundfile as sf
from pyqtgraph.Qt import QtCore, QtGui


class Visualizer(object):
    def __init__(self, data, fs):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 40
        self.w.setWindowTitle('test')
        self.w.setGeometry(0, 30, 1280, 720)
        self.w.pan(10, 500, 100)
        self.w.setCameraPosition(distance=20000, elevation=30, azimuth=-135)
        self.w.show()

        self.data = data
        self.fs = fs

        self.animation_fps = 60
        self.window = fs // self.animation_fps

        self.frame = 128*self.window
        self.chunks = self.frame*2 // self.window
        self.nframes = len(self.data)//self.window

        self.fft = -200*np.ones((self.window//2 + 1, self.chunks))
        self.f = np.linspace(0, self.fs//2, self.window//2+1)
        self.t = np.linspace(0, self.fs/self.frame, self.chunks)

        self.start = 0
        self.stop = self.window

        self.cmap = plt.get_cmap('inferno')
        self.colors = self.cmap((self.fft+200)/(0+200))

        # self.colors = pg.ColorMap(np.arange(-200, 0), color=pg.ColorMap.getLookupTable(-200, 0, mode='float'))

        self.surface = gl.GLSurfacePlotItem(self.f, self.t, self.fft, colors=self.colors, computeNormals=False)
        self.surface.scale(1, np.max(self.f)/np.max(self.t), 100)
        # self.surface.plot.setLogMode(x=True)
        self.w.addItem(self.surface)

    def run(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def update(self):
        # stime = time.time()

        tmp = np.fft.rfft(self.data[self.start:self.stop]*signal.get_window('blackmanharris', self.window))
        tmp = 20*np.log10(np.abs(tmp)*2 / np.sum(signal.get_window('blackmanharris', self.window)))
        
        self.fft = np.roll(self.fft, -1)
        self.fft[:, -1] = tmp
        self.colors = self.cmap((self.fft+200)/(0+200))

        self.start += self.window #// 2
        self.stop += self.window #// 2

        if self.stop>len(self.data):
            quit()

        self.surface.setData(self.f, self.t, self.fft, colors=self.colors)

        print(self.w.cameraPosition())


    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(1000/self.animation_fps)
        self.run()


# Start event loop.
if __name__ == '__main__':

    input_file = "D:/git/Misc/07 Mind's Mirrors.wav"
    input_file = "D:/git/Misc/07 Break Those Bones Whose Sinews Gave It Motion.wav"
    # input_file = "./test.wav"

    data_stereo, fs = sf.read(input_file)
    data = np.array(data_stereo[:,1]) # only one channel for now

    data_stereo *= 32767 / np.max(np.abs(data_stereo))
    data_stereo = data_stereo.astype(np.int16)

    pg.setConfigOptions(useOpenGL=True, antialias=True)
    v = Visualizer(data, fs)
    sa.play_buffer(data_stereo, 2, 2, fs)
    v.animation()

    