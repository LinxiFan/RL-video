#!/usr/bin/env python
"""

"""
import os
import os.path as p
import json

DRY_RUN = False
MANIFEST = 'manifest.json'

db = {}

def load(root, fname):
    if root:
        fname = p.join(root, fname)
    with open(fname) as fp:
        return json.load(fp)

for root, dirs, files in os.walk('/Users/jimfan/Documents/Video'):
    if not files:
        continue
    game = p.basename(root)
    entry = {}
    stat = load(root, 'openaigym.episode_batch.0._.stats.json')
    entry['lengths'] = stat['episode_lengths']
    entry['rewards'] = stat['episode_rewards']
    entry['files'] = []
    for ep in range(50):
        old_name = 'openaigym.video.0._.video{:0>6}.mp4'.format(ep)
        new_name = '{}.{:0>2}.mp4'.format(game, ep)
        entry['files'].append(new_name)
        cmd = 'mv {0}/{1} {0}/{2}'.format(root, old_name, new_name)
        if DRY_RUN:
            print(cmd)
        else:
            os.system(cmd)

    db[game] = entry
    
with open(MANIFEST, 'w') as fp:
    json.dump(db, fp, indent=4)