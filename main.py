import fire
import pandas as pd

from flow import FlowConstructor, simpleFlow
from flowEcho import constructFlowEcho
from flowHead import constructFlowHead

# register flows
available_flows = {"echo": constructFlowEcho(), "head": constructFlowHead()}


class dragenflow(object):
    def parse_file(self, path: str) -> None:
        data_file = pd.read_csv(path)
        return data_file

    def construct_str(self, path: str) -> None:
        data_file = self.parse_file(path)
        for _, val in data_file.iterrows():
            flow = val["pipeline"]
            if available_flows.get(flow):
                data = val.to_dict()
                chosen_flow = available_flows.get(flow)
                flow_context = FlowConstructor(chosen_flow, data=data)
                const_str = flow_context.construct_flow()
                print(const_str)
                # return const_str
                # print(const_str)

    def execute_bash(self, path: str) -> None:
        data_file = self.parse_file(path)
        for _, val in data_file.iterrows():
            flow = val["pipeline"]
            if available_flows.get(flow):
                data = val.to_dict()
                chosen_flow = available_flows.get(flow)
                flow_context = FlowConstructor(chosen_flow, data=data)
                flow_context.execute_flow()


def test():
    flow_context = FlowConstructor(
        simpleFlow(), {"command": "echo", "outpu": "test.txt"}
    )
    test = flow_context.construct_flow()
    print(test)


if __name__ == "__main__":
    fire.Fire(dragenflow)
