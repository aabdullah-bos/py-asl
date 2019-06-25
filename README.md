# py-asl
Python Object Model for Amazon State Language

This package provides an object model for creating Step Functions

## Examples

### Simple Hello World Example
```
import py_asl

def hello_world():
    state_machine = py_asl.StateMachine(Comment="A simple minimal example of the States language", StartAt="Hello World")
    state = py_asl.TaskState("Hello World", Resource="arn:aws:lambda:us-east-1:123456789012:function:HelloWorld", End=True)
    state_machine.States.append(state)
    hw = state_machine.dumps(indent=2)
    return hw

print(hello_world())
```

### Example of creating a Parallel Task

```
import py_asl

def parallel_states():
    state1 = py_asl.TaskState("Hello World", Resource="arn:aws:lambda:us-east-1:123456789012:function:HelloWorld", End=True)
    state2 = py_asl.TaskState("Goodbye World", Resource="arn:aws:lambda:us-east-1:123456789012:function:GoodbyeWorld", End=True)
    parallel_state = state_model.ParallelState("Hello Goodbye", Branches=[state1, state2], Next="Foo")
    ps = parallel_state.dumps(indent=2)
    return ps

print(parallel_states())
```
