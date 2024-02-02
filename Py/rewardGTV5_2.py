"""
Reward functions for Gran Turismo (PSX)
Simplified version of : 
https://github.com/trackmania-rl/tmrl/blob/e3254888ae7e865c56236d72fb03311a41c10310/tmrl/custom/utils/compute_reward.py#L10
nadir.syedsammut@gmail.com
Development started in December 2022
"""


# third-party imports
import numpy as np
import logging
import csv
import datetime

DEBUG = False


class RewardFunction:
    def __init__(self,
                 filename='Py/hsSpaced.csv', start=0):
        print(filename)
        self.start = start
        self.cur_idx = 0
        self.maxSearch = 300
        self.data = np.genfromtxt(filename, delimiter=",")
        self.datalen = len(self.data)
        # since the spacing of data points along the track may vary this scales the reward
        self.fudgeFactor = 20
        self.totalReward = 0
        self.episodeNumber = 0
        self.steps = 0
        self.badDirectionSteps = 0
        self.maxBadDirectionSteps = 100
        self.firstLoop = True

    # I think the reward needs to include speed

    def complexReward(self, pos, vColl, vSpeed, vDir, wheelOff):
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

        if self.firstLoop:
            # if things just started, maybe the car did not launch at the start line, so we should check more positions
            maxSearch = self.maxSearch * 10
        else:
            maxSearch = self.maxSearch

        while True:
            # distance of the current index to target pos
            dist = np.linalg.norm(pos - self.data[index])
            if dist <= min_dist:  # if dist is smaller than our minimum found distance so far,
                min_dist = dist  # then we found a new best distance,
                best_index = index  # and a new best index
            index += 1  # now we will evaluate the next index in the trajectory
            counter += 1
            if index >= self.datalen or counter > maxSearch:  # if trajectory complete or cuts counter depleted
                # We check that we are not too far from the demo trajectory:
                # if min_dist > self.max_dist_from_traj:
                # best_index = self.cur_idx  # if so, consider we didn't move
                break  # we found the best index and can break the while loop

        index = self.cur_idx
        counter = 0
        while True:
            # distance of the current index to target pos
            dist = np.linalg.norm(pos - self.data[index])
            if dist <= min_dist:  # if dist is smaller than our minimum found distance so far,
                min_dist = dist  # then we found a new best distance,
                best_index = index  # and a new best index
            index -= 1  # now we will evaluate the next index in the trajectory
            counter += 1
            if index <= 0 or counter > maxSearch:  # if trajectory complete or cuts counter depleted
                # We check that we are not too far from the demo trajectory:
                # if min_dist > self.max_dist_from_traj:
                # best_index = self.cur_idx  # if so, consider we didn't move
                break  # we found the best index and can break the while loop

        # The reward is then proportional to the number of passed indexes (i.e., track distance):
        self.reward = (best_index - self.cur_idx) / self.fudgeFactor
        if vDir == 1:  # going back is bad
            self.badDirectionSteps = self.badDirectionSteps + 1
            self.reward = self.reward - 0.02
        elif vSpeed < 15:  # going slow is a bit bad
            self.badDirectionSteps = self.badDirectionSteps + 0.5  # new for v3
            # self.reward = self.reward - 0.02
        elif vColl > 0:
            self.reward = 0.25 * self.reward
        if wheelOff > 0:
            self.reward = 0.25 * self.reward
            # print(vColl, self.reward)
        #else:
        #    self.reward = (best_index - self.cur_idx) / self.fudgeFactor
            

        self.cur_idx = best_index

        if self.firstLoop:  # hack just in case the car is not starting at index 0
            self.reward = 0.0
            self.firstLoop = False

        if self.badDirectionSteps > self.maxBadDirectionSteps:
            terminated = True
        self.reward = self.reward / 1.00
        span = 100
        x1, y1 = self.data[self.cur_idx+span][0], self.data[self.cur_idx+span][1]
        x2, y2 = self.data[self.cur_idx +span*2][0], self.data[self.cur_idx+span*2][1]
        future1 = [x1, y1]
        future2 = [x2, y2]
        #print(pos, future1, future2)
        return self.reward, terminated, future1, future2
    
    def computeReward(self, pos=None, vColl=None, vDir=None, vSpeed=None, wheelOff=None, mode="complex"):
        reward, terminated, future1, future2, = self.complexReward(
            pos, vColl, vSpeed, vDir, wheelOff)
        self.steps = self.steps + 1
        self.totalReward = self.totalReward + reward
        # print(reward)
        return reward, terminated, future1, future2

    def reset(self):
        """
        Resets the reward function for a new episode.
        """
        print("Last Total Reward was: ", self.totalReward)
        self.episodeNumber = self.episodeNumber + 1
        self.totalReward = 0.0
        self.cur_idx = self.start
        self.steps = 0
        self.badDirectionSteps = 0
        self.firstLoop = True
