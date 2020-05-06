import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
import soundfile as sf
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D


input_file = "./test.wav"

data, fs = sf.read(input_file)
data = data[:,1] # only one channel for now

animation_fps = 30

start = 0
stop = 4096
frame = 4096
window = 256
hop = int(fs/animation_fps)

nframes = len(data) - frame // hop

# f, t, stft = signal.stft(data, fs, signal.get_window('blackmanharris', window), nperseg=window)
# stft = abs(stft)
# stft = 20*np.log10(stft * 2 / np.sum(signal.get_window('blackmanharris', window)))
# stft = np.clip(stft, -200, 0)
# stft[stft==-200] = np.nan

fig = plt.figure(figsize=(8,8), facecolor='black', frameon=False)
ax = fig.gca(projection='3d')

def set_plot_params(fig, ax):
    ax.set_autoscale_on(False)
    ax.view_init(azim=-70, elev=30)
    ax.set_xlim([0, fs/2])
    # ax.set_xlim([3000, 22000])
    ax.set_ylim([0.03, 0.08])

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
    global start, stop, window, hop
    ax.clear()

    f, t, stft = signal.stft(data[start:stop], fs, signal.get_window('blackmanharris', window), nperseg=window)
    stft = abs(stft)
    stft = 20*np.log10(stft * 2 / np.sum(signal.get_window('blackmanharris', window)))
    stft = np.clip(stft, -200, 0)
    stft[stft==-200] = np.nan

    # remove edges because they look ugly --> stft[1:-1]
    surf = ax.plot_surface(f[:, None], t[None, 1:-1], stft[:, 1:-1], cmap=plt.cm.inferno)#, antialiased=False)

    set_plot_params(fig, ax)

    start += hop
    stop = start + frame
    if stop > len(data):
        quit()
    
    return surf

anim = FuncAnimation(fig, update_plot, frames=nframes)
anim.save('out.mp4', fps=animation_fps, writer='ffmpeg', progress_callback=lambda i, n: print(f'Saving frame {i} of {n}'))
