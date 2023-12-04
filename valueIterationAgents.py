# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for i in range(self.iterations):
            valCopy = self.values.copy()
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    self.values[state] = 0.0
                else:
                    maxVal = -float("inf")
                    for action in self.mdp.getPossibleActions(state):
                        value = 0.0
                        for state_prob in self.mdp.getTransitionStatesAndProbs(state, action):
                            value+=state_prob[1]*(self.mdp.getReward(state, action, state_prob[0])+self.discount*valCopy[state_prob[0]])
                        maxVal = max(value, maxVal)
                    self.values[state] = maxVal



    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        Q = 0
        for state_prob in self.mdp.getTransitionStatesAndProbs(state, action):
            Q += state_prob[1]*(self.mdp.getReward(state, action, state_prob[0])+self.discount*self.getValue(state_prob[0]))
        return Q

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state):
            return None
        
        Qvals_and_Actions = []

        for action in self.mdp.getPossibleActions(state):
            Qvals_and_Actions.append((self.getQValue(state,action), action))
        
        Qvals_and_Actions = sorted(Qvals_and_Actions, key=lambda x: x[0], reverse=True)
        return Qvals_and_Actions[0][1]



    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        states = self.mdp.getStates()
        for i in range(self.iterations):
            valCopy = self.values.copy()
            state = states[i%len(states)]
            if self.mdp.isTerminal(state):
                self.values[state] = 0.0
            else:
                maxVal = -float("inf")
                for action in self.mdp.getPossibleActions(state):
                    value = 0
                    for state_prob in self.mdp.getTransitionStatesAndProbs(state, action):
                        value+=state_prob[1]*(self.mdp.getReward(state, action, state_prob[0])+self.discount*valCopy[state_prob[0]])
                    maxVal = max(value, maxVal)
                self.values[state] = maxVal

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "start by finding the predecessors"
        predecessors = {}
        for state in self.mdp.getStates():
            for action in self.mdp.getPossibleActions(state):
                for state_prob in self.mdp.getTransitionStatesAndProbs(state, action):
                    if state_prob[0] not in predecessors:
                        predecessors[state_prob[0]] = {state}
                    else:
                        predecessors[state_prob[0]].add(state)
        
        "Do the queue things"
        pqueue = util.PriorityQueue()
        for state in self.mdp.getStates():
            if not self.mdp.isTerminal(state):
                maxval = -float("inf")
                for action in self.mdp.getPossibleActions(state):
                    qval = self.computeQValueFromValues(state, action)
                    maxval = max(qval, maxval)
                currval = self.values[state]
                pqueue.push(state, -abs(maxval-currval))
        for i in range(self.iterations):
            if pqueue.isEmpty():
                break
            s = pqueue.pop()
            if not self.mdp.isTerminal(s):
                maxval = -float("inf")
                for action in self.mdp.getPossibleActions(s):
                    qval = self.computeQValueFromValues(s, action)
                    maxval = max(qval, maxval)
                self.values[s] = maxval
            for p in predecessors[s]:
                if not self.mdp.isTerminal(p):
                    maxval = -float("inf")
                    for action in self.mdp.getPossibleActions(p):
                        qval = self.computeQValueFromValues(p, action)
                        maxval = max(qval, maxval)
                    currval = self.values[p]
                    diff = abs(maxval-currval)
                    if diff>self.theta:
                        pqueue.update(p, -diff)
