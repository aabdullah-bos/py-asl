import json
import re

"""
Object Model for Amazon States Language

NOTES:
- [Amazon States Language](https://states-language.net/spec.html#states-fields)
- [awslabs/statelint - Ruby States Language Validator](https://github.com/awslabs/statelint)
- [Amazon States Language](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html)
"""


def filter_arrays(template_string):
    array_pattern = r'\"\[(?P<temp_var>\$\{[a-zA-Z_-]*\})]"'
    var_pattern = r'\"\[\$\{[a-zA-Z_-]*\}]"'
    arrays = re.findall(array_pattern, template_string)
    to_replace = re.findall(var_pattern, template_string)
    mappings = zip(to_replace, arrays)
    for k, v in mappings:
        template_string = template_string.replace(k, v)
    return template_string


class Dumpable(object):
    def to_dict(self):
        """
        Return a dictionary of an objects CloudFormation
        configuration schema
        """
        attrs = vars(self).copy()
        if self._exclude_fields:
            for field in self._exclude_fields:
                attrs.pop(field)
        return attrs

    def dumps(self, indent=None):
        """
        Return a JSON string of an objects CloudFormation
        configuraiton schema
        """
        config = self.to_dict()
        template_string = json.dumps(config, indent=indent)
        filtered = filter_arrays(template_string)
        return filtered


class Attrable(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class StateMachine(Attrable, Dumpable):
    """
    Represents an AWS State Machine object. The
    required fields are:

    StartAt: Task to start with
    States: Dictionary of states in the state machine
    """

    def __init__(self, **kwargs):
        super(StateMachine, self).__init__(**kwargs)
        self._exclude_fields = ['_exclude_fields', 'States']
        if not hasattr(self, 'States'):
            self.States = list()

    def to_dict(self):
        attrs = super(StateMachine, self).to_dict()
        states = dict((state.Name, state.to_dict()) for state in self.States)
        attrs['States'] = states

        return attrs


class State(Attrable):
    """
    Represnts a generic State in the Amazon States Language
    """

    def __init__(self, Name, Type, **kwargs):
        super(State, self).__init__(**kwargs)
        self.Name = Name
        self.Type = Type


class TaskState(State, Dumpable):
    """
    Represents a Task State. The required fields are:

    One of:
    - Next: The next task in state machine
    - End: Boolean value (True) to indicate that this is the last task.
    """

    def __init__(self, Name, **kwargs):
        super(TaskState, self).__init__(Name, 'Task', **kwargs)
        self._exclude_fields = ['Name', '_exclude_fields']


class ChoiceState(State, Dumpable):
    def __init__(self, Name, **kwargs):
        super(ChoiceState, self).__init__(Name, 'Choice', **kwargs)
        self._exclude_fields = ['Name', '_exclude_fields']


class WaitState(State, Dumpable):
    def __init__(self, Name, **kwargs):
        super(WaitState, self).__init__(Name, 'Wait', **kwargs)
        self._exclude_fields = ['Name', '_exclude_fields']


class SucceedState(State, Dumpable):
    def __init__(self, Name, **kwargs):
        super(SucceedState, self).__init__(Name, 'Succeed', **kwargs)
        self._exclude_fields = ['Name', '_exclude_fields']


class FailState(State, Dumpable):
    def __init__(self, Name, **kwargs):
        super(FailState, self).__init__(Name, 'Fail', **kwargs)
        self._exclude_fields = ['Name', '_exclude_fields']


class ParallelState(State, Dumpable):
    def __init__(self, Name, **kwargs):
        super(ParallelState, self).__init__(Name, 'Parallel', **kwargs)
        self._exclude_fields = ['Name', '_exclude_fields', 'Branches']
        self.Branches = kwargs.get("Branches", list())

    def to_dict(self):
        attrs = super(ParallelState, self).to_dict()
        branches = [StateMachine(StartAt=task.Name, States=[task]) for task in self.Branches]
        attrs['Banches'] = [branch.to_dict() for branch in branches]
        return attrs


class PassState(State, Dumpable):
    def __init__(self, Name, **kwargs):
        super(PassState, self).__init__(Name, 'Pass', **kwargs)
        self._exclude_fields = ['Name', '_exclude_fields']

# In previous implementations of similar Object Models I've attempted to
# use the `dataclass` decorator, but I can't remember why I chose not to
# use it. I've also considered using Ruby or some other lanugage. It may
# be that I choose to migrate to another language in the future, but for
# now I am just choosing this approach as it was the first thing that came
# to mind and it works.
