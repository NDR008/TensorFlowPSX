    # Mandatory
    def get_observation(self):
        self.__lock_obs.acquire()
        o_pos_x = self.__obs_pos_x
        o_pos_y = self.__obs_pos_y
        self.__lock_obs.release()
        return o_pos_x, o_pos_y