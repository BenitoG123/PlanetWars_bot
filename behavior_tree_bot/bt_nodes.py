from copy import deepcopy
import logging
import random


def log_execution(fn):
    def logged_fn(self, state):
        logging.debug('Executing:' + str(self))
        result = fn(self, state)
        logging.debug('Result: ' + str(self) + ' -> ' + ('Success' if result else 'Failure'))
        return result
    return logged_fn


############################### Base Classes ##################################
class Node:
    def __init__(self):
        raise NotImplementedError

    def execute(self, state):
        raise NotImplementedError

    def copy(self):
        return deepcopy(self)


class Composite(Node):
    def __init__(self, child_nodes=[], name=None):
        self.child_nodes = child_nodes
        self.name = name

    def execute(self, state):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.name if self.name else ''

    def tree_to_string(self, indent=0):
        string = '| ' * indent + str(self) + '\n'
        for child in self.child_nodes:
            if hasattr(child, 'tree_to_string'):
                string += child.tree_to_string(indent + 1)
            else:
                string += '| ' * (indent + 1) + str(child) + '\n'
        return string


############################### Composite Nodes ##################################
class Selector(Composite):
    @log_execution
    def execute(self, state):
        for child_node in self.child_nodes:
            success = child_node.execute(state)
            if success:
                return True
        else:  # for loop completed without success; return failure
            return False


class Sequence(Composite):
    @log_execution
    def execute(self, state):
        for child_node in self.child_nodes:
            continue_execution = child_node.execute(state)
            if not continue_execution:
                return False
        else:  # for loop completed without failure; return success
            return True
        
class RandomSelector(Composite):
    @log_execution
    def execute(self, state):
        child_nodes_copy = self.child_nodes #copy of child nodes so don't interfere with real list
        for _ in range(len(self.child_nodes)):
            child_node = random.choice(child_nodes_copy) #randomly chooses next child
            child_nodes_copy.remove(child_node) #removes child from list so no repeats
            success = child_node.execute(state)
            if success:
                return True
        else:  # for loop completed without success; return failure
            return False
        
class RandomSequence(Composite):
    @log_execution
    def execute(self, state):
        child_nodes_copy = self.child_nodes #copy of child nodes so don't interfere with real list
        for _ in range(len(self.child_nodes)):
            child_node = random.choice(child_nodes_copy) #randomly chooses next child
            child_nodes_copy.remove(child_node) #removes child from list so no repeats
            continue_execution = child_node.execute(state)
            if not continue_execution:
                return False
        else:  # for loop completed without failure; return success
            return True


############################### Leaf Nodes ##################################
class Check(Node):
    def __init__(self, check_function):
        self.check_function = check_function

    @log_execution
    def execute(self, state):
        return self.check_function(state)

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.check_function.__name__


class Action(Node):
    def __init__(self, action_function):
        self.action_function = action_function

    @log_execution
    def execute(self, state):
        return self.action_function(state)

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.action_function.__name__

############################### Decorator Nodes ##################################

class Inverter(Composite):
    @log_execution
    def execute(self, state):
        child_node = self.child_nodes[0] #should only be one node
        success = child_node.execute(state)
        if success:
            return False #return opposite
        else:  
            return True #return opposite

class AlwaysSucceed(Composite):
    @log_execution
    def execute(self, state):
        child_node = self.child_nodes[0] #should only be one node
        child_node.execute(state)
        
        return True #return True always

class AlwaysFailure(Composite):
    @log_execution
    def execute(self, state):
        child_node = self.child_nodes[0] #should only be one node
        child_node.execute(state)
        
        return False #return False always

class LoopUntilFailed(Composite):
    @log_execution
    def execute(self, state):
        child_node = self.child_nodes[0] #should only be one node
        success = True
        while success:
            success = child_node.execute(state)
        
        return False #return False always
    
class LoopUntilSucceed(Composite):
    @log_execution
    def execute(self, state):
        child_node = self.child_nodes[0] #should only be one node
        failure = True
        while failure:
            failure = child_node.execute(state)
        
        return True #return True always