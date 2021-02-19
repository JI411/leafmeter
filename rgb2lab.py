import numpy as np
from skimage import io, color
import matplotlib.pyplot as plt

rgb = plt.imread('7.jpg')
lab = color.rgb2lab(rgb).astype(np.int8)
np.savez_compressed('7.npz', lab)