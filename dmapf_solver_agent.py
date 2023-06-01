from mapf import *
from messages import Message


class ConstraintTreeNode:
    ''' A node in the constraint tree '''
    def __init__(self, solution: MapfSolution, constraints:list):
        self.solution = solution
        self.constraints = constraints

class Conflict:
    ''' A conflict between agents '''
    def __init__(self, location, time_step, agent1, agent2):
        self.location = location
        self.time_step = time_step
        self.agent1 = agent1
        self.agent2 = agent2

class Constraint:
    ''' A constraint on a single agent '''
    def __init__(self, location, time_step, agent_id):
        self.location = location
        self.time_step = time_step
        self.agent_id = agent_id

class PathForAgentMessage(Message):
    ''' A message sent in the initial state to notify other agents of the initial path'''
    def __init__(self,from_agent:int, to_agent:int, path_for_agent: Path):
        super().__init__(from_agent=from_agent, to_agent=to_agent)
        self.path_for_agent = path_for_agent

class DeclareEmptyOpenMessage(Message):
    ''' This means the best solution seens so far might be optimal  '''
    def __init__(self,from_agent:int, to_agent:int, incumbent: MapfSolution):
        super().__init__(from_agent=from_agent, to_agent=to_agent)
        self.incumbent = incumbent

class DeclareSolutionMessage(Message):
    ''' This means the best solution seens so far might be optimal  '''
    def __init__(self,from_agent:int, to_agent:int, incumbent: MapfSolution):
        super().__init__(from_agent=from_agent, to_agent=to_agent)
        self.incumbent = incumbent


class DeclareConflictMessage(Message):
    ''' This means the best solution seens so far might be optimal  '''
    def __init__(self,from_agent:int, to_agent:int, ct_node: ConstraintTreeNode, conflict:Conflict):
        super().__init__(from_agent=from_agent, to_agent=to_agent)
        self.ct_node = ct_node
        self.conflict = conflict



class DMapfSolverAgent:
    # Agent states
    INIT_STATE = 0
    IN_PROGRESS_STATE = 1
    DONE_STATE = 2

    def __init__(self, agent_id: int):
        self.agent_id = agent_id  # ID of this agent

        self.mapf_problem = None # The MAPF problem we want to solve
        self.message_queue = []  # message queue
        self.incumbet_solution = None  # Best solution found so far
        self.state = None

        self._root_solution = None
        self._open_list = None # Open list for the CBS high level search (on the constraint tree)

    def recieve_message(self, message: Message):
        self.message_queue.append(message)

    def setup(self, mapf_problem: MapfProblem):
        self.mapf_problem = mapf_problem
        self.message_queue.clear()  # message queue
        self.incumbet_solution = None  # Best solution found so far
        self.state = DMapfSolverAgent.INIT_STATE
        self._root_solution = MapfSolution()
        self._open_list = list() # TODO: Shoudl be priority list based on the cost of the solution in each node

        # Find initial path for this agent and send it to all other agents
        my_root_path = self._find_shortest_path(constraints=[])
        self._root_solution[self.agent_id]=my_root_path
        outgoing_messages = []
        for agent in mapf_problem.agents:
            if agent!=self.agent_id:
                outgoing_messages.append(PathForAgentMessage(from_agent=self.agent_id,
                                                             to_agent=agent,
                                                             path_for_agent=my_root_path))
        return outgoing_messages

    def _handle_initial_state(self):
        backlog_messages =[] # Message we want to handle later (all the non-init related messages)
        while len(self.message_queue) > 0:
            message = self.message_queue.pop()
            if message(type) == PathForAgentMessage:
                self._root_solution[message.from_agent] = message.path_for_agent
            else:
                backlog_messages.append(message)
        self.message_queue.extend(backlog_messages) # Return the backloged messages

        # If recieved paths for all agents, construct the root CT node
        if len(self._root_solution.keys()) == len(self.mapf_problem.agents):
            self.state = DMapfSolverAgent.IN_PROGRESS_STATE
            root_ct_node = ConstraintTreeNode(self._root_solution, constraints=[])
            self._open_list.append(root_ct_node)

    def _handle_message(self, message: Message):
        assert(type(message)!=PathForAgentMessage) # This messages should only be used in the initial state
        
        # TODO Handle the different messages

    def _declare_incumbent(self):
        ''' Create set of messages that declare a new incumbent solution'''
        messages = []
        for agent in self.mapf_problem.agents:
            if agent != self.agent_id:
                messages.append(DeclareSolutionMessage(self.agent_id, agent, self.incumbet_solution))
        return messages

    def act(self):
        # *** Handle messages ***

        # If we're still in the initial state, only process the PathForAgent messages to construct the root node of the constraint tree
        if self.state==DMapfSolverAgent.INIT_STATE:
            self._handle_initial_state()
            if len(self._root_solution)<len(self.mapf_problem.agents):
                return  # Do not start to act before we constructed the initial solution

        while len(self.message_queue) > 0:
            msg = self.message_queue.pop()
            self._handle_message(msg)

        # *** Act: expand agent's own OPEN

        # If OPEN is empty, we might be done. Declare our current best solution (==incumbent)
        if len(self._open_list)==0:
            if self.incumbet_solution is not None:
                return self._declare_incumbent()
            else:
                return []

        # Else, choose a conflict with this agent to resolve. If non exists, do nothing
        new_node = self._open_list.pop()
        if new_node.solution.is_valid():
            if self.incumbet_solution is None or self.incumbet_solution.cost()>new_node.solution.cost():
                self.incumbet_solution = new_node.solution
                return self._declare_incumbent()

        conflicts = self._find_conflicts_with_agent(new_node)
        if len(conflicts)==0:
            return []
        else:
            conflict = self._choose_conflict(conflicts)
            # TODO Implement: create a CT node with a constraint for this agent (self.agent_id). Add that node to this open list

            new_ct_node = self._generate_ct_node(new_node, conflict)
            self._open_list.append(new_ct_node)

            # TODO Implement: send a message to the other agent in this conflict, that will generate CT node that constrain and replan that agent
            # The resulting CT agent will be added to the open list of that agent when it handles the message
            message = DeclareConflictMessage(from_agent=self.agent_id,
                                         to_agent=conflict.agent2,
                                         ct_node=new_node,
                                         conflict = conflict)
            return [message]

    def _find_conflicts_with_agent(self, ct_node: ConstraintTreeNode):
        ''' Return conflicts with this (=self.agent_id) agent  '''
        # TODO Implement me. IMPORTANT: Ensure in the created conflicts conflict.agent1 is always self.agent_id

        return []

    def _generate_ct_node(self, ct_node:ConstraintTreeNode, conflict:Conflict):
        ''' Create a single CT node by adding a constraint to our agent  and replanning for it '''
        return None # TODO Implement me

    def _choose_conflict(self, conflicts:list):
        # TODO Any way to choose is Ok for now
        return conflicts[0]

    def is_done(self):
        ''' Returns true if the agent has an incumbent solution and no potentially better solutions to examine '''
        return self.state==DMapfSolverAgent.DONE_STATE

    def _find_shortest_path(self, constraints):
        # Find the shortest poth for self.agent_id from its start to its goals subject to the given set of constraints
        # (= standard low-level search in CBS)
        return None  # Should be a path for agent i


    def _find_shortest_path(self, constraints):
        # Find the shortest poth for self.agent_id from its start to its goals subject to the given set of constraints
        # (= standard low-level search in CBS)
        return None # Should be a path for agent i

