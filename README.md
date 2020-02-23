# py-asl
Python Object Model for Amazon State Language

This package provides an object model for creating Step Functions

## Examples

### Simple Hello World Example

```python
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

```python
import py_asl

def parallel_states():
    state1 = py_asl.TaskState("Hello World", Resource="arn:aws:lambda:us-east-1:123456789012:function:HelloWorld", End=True)
    state2 = py_asl.TaskState("Goodbye World", Resource="arn:aws:lambda:us-east-1:123456789012:function:GoodbyeWorld", End=True)
    parallel_state = state_model.ParallelState("Hello Goodbye", Branches=[state1, state2], Next="Foo")
    ps = parallel_state.dumps(indent=2)
    return ps

print(parallel_states())
```

### Arrays and Generated Templates

Template variables that were place holders for arrays were tricky, so I implemented
a workaround which is probably not suitable for all cases...Let's say that
you have to deploy a Step Function that has a task that invokes an ECS/Fargate
task and you need to specify the VPC configuration. In this case you will need
to supply parameters that include a list of subnets and a list of Security Groups.

Your code might look like this:

```python
import py_asl

Parameters = {"Cluster": "${cluster_arn}",
              "TaskDefinition": "${task_definition_arn}",
              "LaunchType": "FARGATE",
              "NetworkConfiguration": {"AwsvpcConfiguration": {
                                                               "SecurityGroups": "[${security_groups}]",
                                                               "Subnets": "[${subnets}]"
                                                              }
                                       }
              }

task = py_asl.TaskState("Run Fargate",
                        Resource="arn:aws:states:::ecs:runTask.sync",
                        End=True,
                        Parameters=Parameters)

state_machine = py_asl.StateMachine(Comment="Step Function to Test Invoking ECS/Fargate Task",
                                    StartAt="Run Fargate",
                                    States=[task])

if __name__ == '__main__':
    print(state_machine.dumps(indent=2))
```

**NOTE:** The arrays for the security groups will be transformed into:
```JSON
{
  "Comment": "Step Function to Test Invoking ECS/Fargate Task",
  "StartAt": "Run Fargate",
  "States": {
    "Run Fargate": {
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "End": true,
      "Parameters": {
        "Cluster": "${cluster_arn}",
        "TaskDefinition": "${task_definition_arn}",
        "LaunchType": "FARGATE",
        "NetworkConfiguration": {
          "AwsvpcConfiguration": {
            "SecurityGroups": ${security_groups},
            "Subnets": ${subnets}
          }
        }
      },
      "Type": "Task"
    }
  }
}
```

It is expected that your Terraform code supplies and array. For example,

```
variable "security_groups" {
    type = "list"
    default = ["ab-12345", "bc-56788"]
}

variable "subnets" {
    type = "list"
    default = ["itsy", "bitsy"]
}
```

When replacing values in the template you can use:

```
data "template_file" "step_function" {
    template = "${file("${path.module}/step-function.json.tpl")}"
    vars = {
        ...
        security_groups = "${jsonencode(var.cluster_security_groups)}"
        subnets = "${jsonencode(var.cluster_subnets)}"
    }
}
```
