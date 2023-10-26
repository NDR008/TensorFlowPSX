"""
Reward functions for Gran Turismo (PSX)
Simplified version of : https://github.com/trackmania-rl/tmrl/blob/e3254888ae7e865c56236d72fb03311a41c10310/tmrl/custom/utils/compute_reward.py#L10
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
                 filename='Py/hsSpaced.csv'):
        print(filename)
        self.cur_idx = 0
        self.maxSearch = 300
        self.data = np.genfromtxt(filename, delimiter=",")
        self.datalen = len(self.data)
        self.fudgeFactor = 20 #since the spacing of data points along the track may vary this scales the reward
        self.totalReward = 0
        self.episodeNumber = 0
        self.steps = 0
        self.badDirectionSteps = 0
        self.maxBadDirectionSteps = 100
        self.firstLoop = True
        x = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        with open('logging.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([x])


    # I think the reward needs to include speed        
    def complexReward(self, pos, vColl, vSpeed, vDir):
              
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
            maxSearch = self.maxSearch * 10 # if things just started, maybe the car did not launch at the start line, so we should check more positions
        else:
            maxSearch = self.maxSearch
            
        while True:
            dist = np.linalg.norm(pos - self.data[index])  # distance of the current index to target pos
            if dist <= min_dist:  # if dist is smaller than our minimum found distance so far,
                min_dist = dist  # then we found a new best distance,
                best_index = index  # and a new best index
            index += 1  # now we will evaluate the next index in the trajectory
            counter += 1
            if index >= self.datalen or counter > maxSearch:  # if trajectory complete or cuts counter depleted
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
            if index <= 0 or counter > maxSearch:  # if trajectory complete or cuts counter depleted
                # We check that we are not too far from the demo trajectory:
                # if min_dist > self.max_dist_from_traj:
                    #best_index = self.cur_idx  # if so, consider we didn't move
                break  # we found the best index and can break the while loop

        # The reward is then proportional to the number of passed indexes (i.e., track distance):
        self.reward = (best_index - self.cur_idx) / self.fudgeFactor    
        if vColl > 0: # hit
            self.reward = self.reward - 0.02
        if vSpeed < 5 and vDir == 1: # going slow
            self.reward = self.reward - 0.05
        else: # going back
            self.reward = self.reward -0.1
          
        self.cur_idx = best_index
        
        if self.firstLoop: # hack just in case the car is not starting at index 0
            self.reward = 0
            self.firstLoop = False
                
        #if self.badDirectionSteps > self.maxBadDirectionSteps:
            #terminated = True


        return self.reward, terminated

    def simplexReward(self, vSpeed, vDir):
        terminated = False       
        penalty = 0.5
        if vDir == 1:
            penalty = -2
            self.badDirectionSteps = self.badDirectionSteps + 1
        reward = (vSpeed)*penalty / 4
        
        if self.badDirectionSteps > self.maxBadDirectionSteps:
            terminated = True

        return reward, terminated

    def computeReward(self, pos=None, vColl=None, vDir=None, vSpeed = None, mode="complex"):
        if mode == "complex":
            reward, terminated = self.complexReward(pos, vColl, vSpeed, vDir)
        else:
            reward, terminated = self.simplexReward(vSpeed, vDir)
        self.steps = self.steps + 1    
        self.totalReward = self.totalReward + reward
            
        if DEBUG:
            print(self.reward, self.cur_idx)
                
        return reward, terminated

    def reset(self):
        """
        Resets the reward function for a new episode.
        """
        with open('logging.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.episodeNumber, int(self.steps), int(self.totalReward)])
        self.episodeNumber =self.episodeNumber + 1
        self.totalReward = 0
        self.cur_idx = 0
        self.steps = 0
        self.badDirectionSteps = 0
        self.firstLoop = True
        