"""
Reward functions for Gran Turismo (PSX)
Simplified version of : https://github.com/trackmania-rl/tmrl/blob/e3254888ae7e865c56236d72fb03311a41c10310/tmrl/custom/utils/compute_reward.py#L10
nadir.syedsammut@gmail.com
Development started in December 2022
"""


# third-party imports
import numpy as np

class RewardFunction:
    def __init__(self,
                 filename='Py/hsSpaced.csv',):
        self.cur_idx = 0
        self.maxSearch = 500
        self.data = np.genfromtxt(filename, delimiter=",")
        self.datalen = len(self.data)
        self.fudgeFactor = 2 #since the spacing of data points along the track may vary this scales the reward

    def computeReward(self, pos):
        """
        Computes the current reward given the position pos
        Args:
            pos: the current position
        Returns:
            float, bool: the reward and the terminated signal
        """
        # self.traj.append(pos)

        terminated = False
        min_dist = np.inf  # smallest distance found so far in the trajectory to the target pos
        index = self.cur_idx  # cur_idx is where we were last step in the trajectory        
        best_index = 0  # index best matching the target pos
        counter = 0

        while True:
            dist = np.linalg.norm(pos - self.data[index])  # distance of the current index to target pos
            if dist <= min_dist:  # if dist is smaller than our minimum found distance so far,
                min_dist = dist  # then we found a new best distance,
                best_index = index  # and a new best index
            index += 1  # now we will evaluate the next index in the trajectory
            counter += 1
            if index >= self.datalen or counter > self.maxSearch:  # if trajectory complete or cuts counter depleted
                # We check that we are not too far from the demo trajectory:
                #if min_dist > self.max_dist_from_traj:
                    #best_index = self.cur_idx  # if so, consider we didn't move
                break  # we found the best index and can break the while loop

        index = self.cur_idx                
        counter = 0
        while True:
            dist = np.linalg.norm(pos - self.data[index])  # distance of the current index to target pos
            if dist <= min_dist:  # if dist is smaller than our minimum found distance so far,
                min_dist = dist  # then we found a new best distance,
                best_index = index  # and a new best index
            index -= 1  # now we will evaluate the next index in the trajectory
            counter += 1
            if index <= 0 or counter > self.maxSearch:  # if trajectory complete or cuts counter depleted
                # We check that we are not too far from the demo trajectory:
                # if min_dist > self.max_dist_from_traj:
                    #best_index = self.cur_idx  # if so, consider we didn't move
                break  # we found the best index and can break the while loop

        # The reward is then proportional to the number of passed indexes (i.e., track distance):
        reward = (best_index - self.cur_idx) / self.fudgeFactor
        if reward < 0:
            reward = -1 
            
        self.cur_idx = best_index  # finally, we save our new best matching index

        return reward, terminated

    def reset(self):
        """
        Resets the reward function for a new episode.
        """
        print(self.cur_idx)
        self.cur_idx = 0