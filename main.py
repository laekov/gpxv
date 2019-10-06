from multiprocessing import Pool
from stat import ST_CTIME
import random
import gpxpy
import matplotlib.pyplot as plt
import os
import sys
import numpy as np


dirname = sys.argv[1]


def parse_gpx(filename):
    g = gpxpy.parse(open(filename, 'r'))

    lat = []
    lon = []
    last_tp = None

    track = []
    for t in g.tracks:
        for seg in t.segments:
            for p in seg.points:
                if last_tp is not None and abs(p.time - last_tp).seconds > 300:
                    track.append((lat, lon))
                    lat, lon = [], []
                lat.append(p.latitude)
                lon.append(p.longitude)
    print('Parsed {}'.format(filename))
    return track


if __name__ == '__main__':
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor('black')
    plt.axis('off')

    th_pool = Pool()

    for idx, dirname in enumerate(sys.argv[1:]):
        files = [os.path.join(dirname, f) for f in os.listdir(dirname)]
        # files = sorted(files, key=lambda x: os.stat(x)[ST_CTIME])
        random.shuffle(files)
        coors = th_pool.map(parse_gpx, files)
        n = len(coors)
        # colors = plt.cm.autumn(np.linspace(.5, 0, n))
        # colors = plt.cm.hsv(np.linspace(0, 1, n))

        for i, track in enumerate(coors):
            for lat, lon in track:
                plt.plot(r_lon, r_lat, linewidth=1)

    plt.gca().set_aspect('equal', adjustable='box')

    plt.savefig('1.eps')
