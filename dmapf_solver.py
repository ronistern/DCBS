from mapf import MapfProblem
from dmapf_solver_agent import DMapfSolverAgent
from messages import Message

class DMapfSolver:
    ''' This runs the solver agents on the given MAPF problem '''
    def __init__(self):
        self.mapf_problem = None # The MAPF problem we want to solve
        self.solver_agents = None # The agents designed to solve the MAPF problem

    def _send_messages(self, messages):
        ''' Distribute the messages by all the agents to all the agents (simulating real communication) '''
        for message in messages:
            self.solver_agents[message.to_agent].recieve_message(message)

    def solve(self, mapf_problem: MapfProblem, solver_agents: list):
        self.mapf_problem = mapf_problem
        self.solver_agents = solver_agents

        # Setup the initial solution
        all_outgoing_messages = []
        for agent in self.solver_agents:
            outgoing_messages = agent.setup(self.mapf_problem)
            all_outgoing_messages.extend(outgoing_messages)
        self._send_messages(all_outgoing_messages)
        # Main loop
        is_done = False
        while not is_done:
            is_done = True
            all_outgoing_messages.clear()

            # This loop simulates distributed execution of all the agents
            for agent in self.solver_agents:
                # Check if we have finished
                if agent.is_done() == False:
                    is_done=False

                outgoing_messages = agent.act()
                all_outgoing_messages.extend(outgoing_messages)

            self._send_messages(all_outgoing_messages)

        assert(is_done)

        # Extract solution. All agents should have the same solution, so doesn't matter which one
        return self.solver_agents[0].incumbent_solution
