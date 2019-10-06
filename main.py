from multiprocessing import Pool
from stat import ST_CTIME
import random
import gpxpy
import matplotlib.pyplot as plt
import os
import sys
import numpy as np
import imageio 


dirname = sys.argv[1]


def parse_gpx(filename):
    g = gpxpy.parse(open(filename, 'r'))

    track = []
    for t in g.tracks:
        for seg in t.segments:
            lat = []
            lon = []
            last_tp = None
            for p in seg.points:
                if (last_tp is not None and
                        abs((p.time - last_tp).seconds) > 300):
                    track.append((lat, lon))
                    lat, lon = [], []
                lat.append(p.latitude)
                lon.append(p.longitude)
                last_tp = p.time
            track.append((lat, lon))
    print('Parsed {}, segs {}'.format(filename, len(track)))
    return track


def main():
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor('black')
    plt.axis('off')

    th_pool = Pool()

    files = []
    lens = []
    for idx, dirname in enumerate(sys.argv[1:]):
        files += [os.path.join(dirname, f) for f in os.listdir(dirname)]
        lens.append(len(files))
    coors = th_pool.map(parse_gpx, files)
    
    lines = []
    colorscheme = ['magenta', 'gold']
    for idx, dirname in enumerate(sys.argv[1:]):
        lines.append([])
        color = None if len(sys.argv) < 3 else colorscheme[idx]
        print('Series {}, color {}'.format(dirname, color))
        for _ in os.listdir(dirname):
            for (lat, lon) in coors.pop(0):
                lines[idx] += plt.plot(lon, lat, linewidth=1, color=color, 
                        alpha=.6, linestyle='none')

    gca = plt.gca()
    gca.set_aspect('equal', adjustable='box')

    for idx, dirname in enumerate(sys.argv[1:]):
        for l in lines[idx]:
            l.set_linestyle('solid')
        plt.savefig('{}.png'.format(idx), facecolor='black')
        for l in lines[idx]:
            l.set_linestyle('none')
        print('{}.png saved'.format(idx))


def overlay():
    ims = []
    for idx, dirname in enumerate(sys.argv[1:]):
        ims.append(imageio.imread('{}.png'.format(idx),
            pilmode='RGB').astype(float))
    bg = np.ones_like(ims[0]) * 255
    masks = [bg * 1e-10 + np.array([(im.sum(axis=-1) > 0)]* 3,
                dtype=float).transpose(1, 2, 0) for im in ims]
    c_im = sum(ims) / sum(masks)
    imageio.imwrite('combined.png', c_im)

if __name__ == '__main__':
    main()
    overlay()
