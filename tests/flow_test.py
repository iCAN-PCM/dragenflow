import pytest

from src.utility.flow import Flow, FlowConstructor


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
    flow_context = FlowConstructor(SimpleFlow())
    return flow_context


@pytest.fixture
def flow_context_echo():
    flow_context_echo = FlowConstructor(ConstructFlowEcho())
    return flow_context_echo


def test_simple_flow(flow_context):
    context = flow_context
    command = context.construct_flow({"command": "echo", "output": "test.txt"})
    assert command == "command echo output test.txt"


# @pytest.mark.skip(
#     reason="need some time to think on how flow execute method should work"
# )
def test_echo_flow(flow_context_echo):
    context = flow_context_echo
    str_command = context.construct_flow({"l": "./tests"})
    output, command = context.execute_flow(command=str_command[0])
    assert output.returncode == 0
    assert command == ["ls", "-l", "./tests"]
    assert str_command == ["ls -l ./tests"]
