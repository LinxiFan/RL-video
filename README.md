# Human play

Run script `./human_play.py <atari_game>` to play the game interactively and record a video. 

The recorded video file will be named as `<game>.<episode_id>.mp4`.

Key controls:

- `A, D, W, S`: left, right, up, down. You can also use the normal direction keys.
- `<space>`: fire or jump.
- `Q, E, Z, C`: fire/jump towards upleft, upright, downleft, downright. 
- `P`: pause the game.
- `R`: restart the game.

# Pretrained agent videos

The [video gallery](https://goo.gl/oX6Jn6) has 46 atari games, each of which has 50 video demonstrations by pretrained A3C agents. 

All videos are named as `<game>.<episode_id>.mp4`.

The `manifest.json` meta file records the episode length, final reward, and file name of each gameplay. 