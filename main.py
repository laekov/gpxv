from multiprocessing import Pool
from stat import ST_CTIME
import random
import gpxpy
import matplotlib.pyplot as plt
import matplotlib
import os
import sys
import numpy as np
import imageio 
import pickle


dirname = sys.argv[1]


def parse_gpx(filename):

    cachename = '.cache/{}'.format(filename.split('/')[-1])
    if os.path.exists(cachename):
        print('Found {} in cache'.format(filename))
        with open(cachename, 'rb') as f:
            return pickle.load(f)
    try:
        g = gpxpy.parse(open(filename, 'r'))
    except:
        print('{} cannot be parsed'.format(filename))
        return None

    track = []
    first_tp = None
    for t in g.tracks:
        for seg in t.segments:
            lat = []
            lon = []
            last_tp = None
            for p in seg.points:
                if (last_tp is not None and
                        abs((p.time - last_tp).seconds) > 300):
                    track.append((lat, lon, last_tp))
                    lat, lon = [], []
                if first_tp is None:
                    first_tp = p.time
                lat.append(p.latitude)
                lon.append(p.longitude)
                if filename == 'trails/cdaoao/puhong_ride.gpx':
                    lon[-1] -= 0.2
                    lat[-1] -= 0.5
                elif filename == 'trails/cdaoao/3382804135.gpx':
                    lat[-1] -= 0.5

                last_tp = p.time
            track.append((lat, lon, last_tp))
    print('Parsed {}, segs {}'.format(filename, len(track)))
    if first_tp is None:
        return None
    with open(cachename, 'wb') as f:
        pickle.dump((track, first_tp), f)
    return track, first_tp


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

    cmap = matplotlib.cm.get_cmap('plasma')

    num_lines = 0
    for coor_i in coors:
        if coor_i is not None:
            num_lines += len(coor_i)
    i_lines = 0

    base_idx = 0
    for idx, dirname in enumerate(sys.argv[1:]):
        lines.append([])
        if len(sys.argv) < 3:
            color = None
        else:
            color = colorscheme[idx]
        print('Series {}, color {}'.format(dirname, color))
        coor_i = coors[base_idx:base_idx + lens[idx]]
        base_idx += lens[idx]
        coor_i = [x for x in sorted([c for c in coor_i if c is not None], key=lambda x: x[1])]
        tmin = min([c[1] for c in coor_i])
        tmax = max([c[1] for c in coor_i])
        for c, t in coor_i:
            for (lat, lon, _) in c:
                if len(sys.argv) < 3:
                    color = cmap((t - tmin) / (tmax - tmin) * .5 + .5)
                    i_lines += 1
                lines[idx] += plt.plot(lon, lat, linewidth=1, color=color, 
                        alpha=.6, linestyle='none')

    gca = plt.gca()
    gca.set_aspect('equal', adjustable='box')

    tot_lines = sum([len(l) for l in lines])
    print('Num lines = {}'.format(tot_lines))

    for idx, dirname in enumerate(sys.argv[1:]):
        for i, l in enumerate(lines[idx]):
            l.set_linestyle('solid')
            if 'PRINT_PROCESS' in os.environ:
                plt.savefig('process/{}_{}.png'.format(idx, i), facecolor='black')
                if i % 16 == 15:
                    print('{} / {}'.format(i, tot_lines))
        plt.savefig('{}.png'.format(idx), facecolor='black')
        for l in lines[idx]:
            l.set_linestyle('none')
        print('{}.png saved with {} lines'.format(idx, len(lines[idx])))


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
