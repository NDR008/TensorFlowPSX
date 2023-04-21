class RewardFunction:
    """
    Computes a reward from GT on Redux
    RewardFunction(nb_zero_rew_before_failure=10, min_nb_steps_before_failure=int(3.5 * 20))
    nb_zer_rew_before_failure: number of non-progress to count as a failure.
    min_nb_steps_before_failure: number of observatitons without a reward.
    """
    def __init__(self, nb_zero_rew_before_failure=10, min_nb_steps_before_failure=int(3.5 * 20)):
        self.curTrackIdx = 0
        self.nb_zero_rew_before_failure = nb_zero_rew_before_failure
        self.min_nb_steps_before_failure = min_nb_steps_before_failure
        self.step_counter = 0
        self.failure_counter = 0
        
    def compute_reward(self, latestIndex):
        terminated = False
        reward = (latestIndex - self.curTrackIdx) / 100.0
        
        if latestIndex == self.curTrackIdx:  # if the best index didn't change, we rewind (more Markovian reward)
            self.failure_counter += 1
            if self.failure_counter > self.nb_zero_rew_before_failure:
                terminated = True
        else:
            self.failure_counter = 0
        self.curTrackIdx = latestIndex
        return reward, terminated
    
    def reset(self):
        self.curTrackIdx = 0
        self.step_counter = 0
        self.failure_counter = 0