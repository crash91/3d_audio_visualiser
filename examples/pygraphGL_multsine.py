import sys
import time

import numpy as np
import matplotlib.pyplot as plt
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import soundfile as sf
from pyqtgraph.Qt import QtCore, QtGui
from scipy import signal


class Visualizer(object):
    def __init__(self, data, fs):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 40
        self.w.setWindowTitle('test')
        self.w.setGeometry(0, 30, 1280, 720)
        self.w.setCameraPosition(distance=30, elevation=12)
        self.w.show()

        self.data = data
        self.fs = fs

        self.start = 0
        self.stop = 2048

        self.hop_length = int(fs/1000) # samples / 10 ms
        self.window_size = 2048
        
        self.f, self.t, self.Sxx = signal.spectrogram(self.data[self.start:self.stop], self.fs, signal.get_window('blackmanharris', 64), mode='magnitude')
        self.Sxx = self.Sxx.transpose()

        self.colors = np.random.rand(*self.Sxx.shape)

        self.offset = self.hop_length
       
        self.surface = gl.GLSurfacePlotItem(self.t, self.f, self.Sxx, computeNormals=False)
        self.w.addItem(self.surface)

    def run(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def update(self):
        stime = time.time()

        self.start = self.offset
        self.stop = self.start + self.window_size

        if self.stop > len(self.data):
            quit()

        self.f, t, Sxx = signal.spectrogram(self.data[self.start:self.stop], self.fs, signal.get_window('blackmanharris', 64), mode='magnitude')

        self.t = np.concatenate((self.t, t))
        self.Sxx = np.concatenate((self.Sxx, Sxx.transpose()))

        self.surface.setData(self.t, self.f, self.Sxx)

        self.offset += self.hop_length


    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(10)
        self.run()


# Start event loop.
if __name__ == '__main__':

    input_file = "D:/git/Misc/07 Mind's Mirrors.wav"
    input_file = "D:/git/Misc/07 Break Those Bones Whose Sinews Gave It Motion.wav"

    data, fs = sf.read(input_file)
    data = data[:, 1]

    v = Visualizer(data, fs)
    v.animation()
