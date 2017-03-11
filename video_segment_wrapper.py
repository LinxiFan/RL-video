"""
Wrapper for augmented reward
"""
import gym
import numpy as np

norm = np.linalg.norm

def _cosine_distance(f1, f2):
    return 0.5 *(1 - np.dot(f1, f2) / (norm(f1) * norm(f2)))

    
def _l1_distance(f1, f2):
    return norm(f1 - f2, 1) / (norm(f1, 1) * norm(f2, 1))

    
def _l2_distance(f1, f2):
    return norm(f1 - f2) / (norm(f1) * norm(f2))

    
VIDEO_DISTANCE_METRIC = {
    'cosine': _cosine_distance,
    'l1': _l1_distance,
    'l2': _l2_distance,
}


class ClippedRewardsWrapper(gym.Wrapper):
    def _step(self, action):
        obs, reward, done, info = self.env.step(action)
        return obs, np.sign(reward), done, info


class VideoSegmentWrapper(gym.Wrapper):
    def __init__(self, env, 
                 goals, 
                 featurizer, 
                 distance_metric, 
                 goal_epsilon,
                 augmented_reward_weight=1.0):
        """
        
        """
        super(VideoSegmentWrapper, self).__init__(env)
        self.goals = goals
        self.goal_i = 0 # current video segment
        self.featurizer = featurizer
        if isinstance(distance_metric, str):
            self.distance_metric = VIDEO_DISTANCE_METRIC[distance_metric.lower()]
        else:
            self.distance_metric = distance_metric
        self.goal_epsilon = goal_epsilon
        self.augmented_reward_weight = augmented_reward_weight
        

    def _step(self, action):
        obs, reward, done, info = self.env.step(action)
        if self.goal_i < len(self.goals):
            cur_goal = self.goals[self.goal_i]
            cur_distance = self.distance_metric(self.featurizer(obs), cur_goal)
            if abs(cur_distance) < self.goal_epsilon:
                # goal achieved, move to the next goal
                self.goal_i += 1
            reward -= cur_distance * self.augmented_reward_weight
        return (obs, self.get_goal_vector()), reward, done, info


    def _reset(self):
        obs = self.env.reset()
        self.goal_i = 0
        return (obs, self.get_goal_vector())
    
    
    def get_goal_vector(self):
        """
        Mark completed stages as 1 and the rest as 0
        """
        vec = np.zeros(len(self.goals))
        vec[:self.goal_i] = 1.0
        return vec


if __name__ == '__main__':
    import sys
    import matplotlib.pyplot as plt
    if len(sys.argv) < 2:
        env_id = 'SpaceInvaders'
    else:
        env_id = sys.argv[1]
    env = gym.make('{}NoFrameskip-v3'.format(env_id))
    A = np.array
    goals = [(1,1), (0,1), (-1,0), (0,-1), (1, 0)]
    goals = list(map(np.array, goals))
    step = 0
    def featurizer(obs):
        global step
        theta = step / 1500.0 * 2*np.pi
        return np.array([np.cos(theta), np.sin(theta)])
    env = ClippedRewardsWrapper(env)
    env = VideoSegmentWrapper(env, goals, featurizer, 'cosine', 1e-5)
    env.reset()
    reward_history = []
    goal_vec_history = []
    while True:
        obs, r, done, info = env.step(env.action_space.sample())
        step += 1
        reward_history.append(r)
        goal_vec_history.append(np.count_nonzero(obs[1]))
        if done:
            break
    print('total steps', step)
    goal_vec_history = np.array(goal_vec_history, np.float32) / len(obs[1])
    plt.plot(reward_history)
    plt.plot(goal_vec_history)
    plt.axis([0, 1900, -1, 1])
    plt.show()
