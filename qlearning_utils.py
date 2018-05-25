class Discretizer():
    """ mins: vector with minimim values allowed for each variable
        maxs: vector with maximum values allowed for each variable
    """

    def __init__(self, discr_vector, mins, maxs):
        self.mins = mins
        self.maxs = maxs
        self.discr_vector = discr_vector

    def Discretize(self, obs):
        ratios = [(obs[i] + abs(self.mins[i])) / (self.maxs[i] - self.mins[i]) for i in range(len(obs))]
        new_obs = [int(round((self.discr_vector[i] - 1) * ratios[i])) for i in range(len(obs))]
        new_obs = [min(self.discr_vector[i] - 1, max(0, new_obs[i])) for i in range(len(obs))]
        return tuple(new_obs)