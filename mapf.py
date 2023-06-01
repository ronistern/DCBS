

class MapfProblem:
    def __init__(self, sources:dict, targets:dict,terrain, agents:list):
        self.sources = sources
        self.targets = targets
        self.agents = agents
        self.terrain = terrain


class Path(list):
    ''' This is a path for a single agent.
    Should be a sequence of steps of something like that'''
    def __init__(self):
        # TODO Implement me
        print("Implement me")

class MapfSolution(dict):
    ''' This is a MAPF solution, maybe with conflicts.
    Should be a mapping between agent id to a path '''
    def __init__(self):
        # TODO Implement me
        print("Implement me")

    def is_valid(self):
        # TODO: Implement me: return true iff the paths do not conflict
        return True

    def cost(self):
        # TODO: Implement sum of costs
        return 0