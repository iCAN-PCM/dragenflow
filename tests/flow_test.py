import pytest

from flow import Flow, FlowConstructor


class SimpleFlow(Flow):
    """
    Simple test implimentation for abstract Flow
    """

    def constructor(self, data: dict) -> str:
        arg_string = " ".join(f"{key} {val}" for (key, val) in data.items())
        return arg_string


class ConstructFlowEcho(Flow):
    """
    This will construct bash script to run Echo command
    """

    def constructor(self, data: dict) -> list:
        arg_string = " ".join(f"-{key} {val}" for (key, val) in data.items())
        # arg_string = "".join(arg_string)
        final_string = [f"ls {arg_string}"]
        return final_string


@pytest.fixture
def flow_context():
    flow_context = FlowConstructor(
        SimpleFlow(), {"command": "echo", "output": "test.txt"}
    )
    return flow_context


@pytest.fixture
def flow_context_echo():
    flow_context_echo = FlowConstructor(ConstructFlowEcho(), {"l": "./tests"})
    return flow_context_echo


def test_simple_flow(flow_context):
    context = flow_context
    command = context.construct_flow()
    assert command == "command echo output test.txt"


def test_echo_flow(flow_context_echo):
    context = flow_context_echo
    str_command = context.construct_flow()
    command = context.execute_flow()
    print(command)
    stdout = command[0][1]
    assert str_command == ["ls -l ./tests"]
    assert len(stdout) > 20
    assert "conftest.py" in stdout
