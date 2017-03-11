#!/usr/bin/env python
import os
import sys
import gym
import time

if len(sys.argv) < 2:
    env_id = 'MontezumaRevenge'
else:
    env_id = sys.argv[1]

env = gym.make('{}NoFrameskip-v3'.format(env_id))
if not hasattr(env.action_space, 'n'):
    raise NotImplementedError('Keyboard agent only supports discrete action spaces')
ACTION_LIST = env.unwrapped.get_action_meanings()
print('action list:', ACTION_LIST)
ACTION_MAP = {action: i for i, action in enumerate(ACTION_LIST)}

DIRECTION_MAP = {
    'LEFT': 0xff51,
    'UP': 0xff52,
    'RIGHT': 0xff53,
    'DOWN': 0xff54,
}

CONTROL_MAP = {
    'LEFT': ord('a'),
    'UP': ord('w'),
    'RIGHT': ord('d'),
    'DOWN': ord('s'),
    'UPLEFTFIRE': ord('q'),
    'UPRIGHTFIRE': ord('e'),
    'DOWNLEFTFIRE': ord('z'),
    'DOWNRIGHTFIRE': ord('c'),
    'FIRE': ord(' '),
    'RESTART': ord('r'),
    'PAUSE': ord('p')
}

def invert_dict(D):
    return {v: k for k, v in D.items()}


INV_CONTROL_MAP = invert_dict(CONTROL_MAP)
INV_CONTROL_MAP.update(invert_dict(DIRECTION_MAP))

def name2key(name):
    if name in CONTROL_MAP:
        return CONTROL_MAP[name]
    else:
        return ord(name)


def key2name(key):
    if key in INV_CONTROL_MAP:
        return INV_CONTROL_MAP[key]
    else:
        return chr(key)


def key2action(key):
    """
    Returns:
      an int index of the selected action
      action 0 is always NOOP
    """
    name = key2name(key)
    return ACTION_MAP.get(name, 0)
    

ACTIONS = env.action_space.n
ROLLOUT_TIME = 1000
# Use previous control decision SKIP_CONTROL times. Set to 0 for NoFrameskip envs
SKIP_CONTROL = 0    

human_action = 0
human_restart = False
human_pause = False

def key_press(key, mod):
    global human_action, human_restart, human_pause
#     print(key2name(key), mod)
    if key == name2key('RESTART'): 
        human_restart = True
    if key == name2key('PAUSE'): 
        human_pause = not human_pause
    human_action = key2action(key)


def key_release(key, mod):
    global human_action
    action = key2action(key)
    if human_action == action:
        human_action = 0


env.render()
env.unwrapped.viewer.window.on_key_press = key_press
env.unwrapped.viewer.window.on_key_release = key_release
env = gym.wrappers.Monitor(env, 
                           directory='.',
                           video_callable=lambda i : True,
                           force=True,
                           uid='_')

def start(env):
    global human_action, human_restart, human_pause
    human_restart = False
    obs = env.reset()
    skip = 0
    while True:
        if not skip:
            #print("taking action {}".format(human_action))
            a = human_action
            skip = SKIP_CONTROL
        else:
            skip -= 1

        obs, r, done, info = env.step(a)
        env.render()
        if done: break
        if human_restart: break
        while human_pause:
            env.render()
            time.sleep(0.2)

episode = 0
while 1:
    start(env)
    old_name = 'openaigym.video.0._.video{:0>6}.mp4'.format(episode)
    new_name = '{}.{:0>2}.mp4'.format(env_id, episode)
    print('Rename {} to {}'.format(old_name, new_name))
    os.system('mv {} {}'.format(old_name, new_name))
    reply = input('Episode finished. Continue? (y/n): ')
    if reply.strip().lower() == 'n':
        break
    episode += 1