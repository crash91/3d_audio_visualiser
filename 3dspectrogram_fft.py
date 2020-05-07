import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import scipy.signal as signal
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

input_file = "./test.wav"

data, fs = sf.read(input_file)
data = data[:,1] # only one channel for now

animation_fps = 60
window = fs // animation_fps

frame = 32*window
chunks = frame*2 // window
nframes = len(data)//window

fft = -200*np.ones((window//2 + 1, chunks))
f = np.linspace(0, fs//2, window//2+1)
t = np.linspace(0, fs/frame, chunks)

start = 0
stop = window


fig = plt.figure(figsize=(8,8), facecolor='black', frameon=False)
ax = fig.gca(projection='3d')

def set_plot_params(fig, ax):
    ax.set_autoscale_on(False)
    ax.view_init(azim=-70, elev=30)
    ax.set_xlim([0, fs/2])
    # ax.set_xlim([3000, 22000])
    # ax.set_ylim([0.03, 0.08])

    plt.margins(0)
    ax.set_facecolor('black')
    ax.w_xaxis.set_pane_color((0,0,0,0))
    ax.w_yaxis.set_pane_color((0,0,0,0))
    ax.w_zaxis.set_pane_color((0,0,0,0))

    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
    ax.grid(False)
    ax.axis('off')
    ax.set_frame_on(False)
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()

def update_plot(i):
    global start, stop, window, data, fft
    ax.clear()

    fft = np.roll(fft, -1)
    tmp = np.fft.rfft(data[start:stop]*signal.get_window('blackmanharris', window))
    tmp = 20*np.log10(np.abs(tmp)*2 / np.sum(signal.get_window('blackmanharris', window)))
    # tmp = np.clip(tmp, -200, 0)
    fft[:, -1] = tmp

    start += window // 2
    stop += window // 2
    if stop>len(data):
        quit()

    # remove edges because they look ugly --> stft[1:-1]
    surf = ax.plot_surface(f[:, None], t[None, :], fft, cmap=plt.cm.inferno, vmin=-200, vmax=0)#, antialiased=False)

    set_plot_params(fig, ax)

    return surf

anim = FuncAnimation(fig, update_plot, frames=nframes)
anim.save('out.mp4', fps=animation_fps, writer='ffmpeg', progress_callback=lambda i, n: print(f'Saved frame {i} of {n}'))
