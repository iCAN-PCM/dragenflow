import fire
import pandas as pd
import logging

from flow import FlowConstructor, simpleFlow
from flowEcho import constructFlowEcho
from flowHead import constructFlowHead
from flowDragen import constructDragen

# register flows
available_flows = {
    "echo": constructFlowEcho(),
    "head": constructFlowHead(),
    "dragen": constructDragen(),
}


def custom_sort(val):

    if len(str(val)) > 1:
        if val[0] == "N":
            return val[-1]
        if val[0] == "T":
            return val[-1]
    else:
        return 0


class dragenflow(object):
    def parse_file(self, path: str, flow: str) -> None:
        if flow == "dragen":
            data_file = pd.read_csv(path, skiprows=4)
            data_file["tumor/normal"] = data_file["tumor/normal"].fillna(0)
            # data_file['tumor/normal'] = pd.Categorical(data_file['tumor/normal'],['N1','T1','T','N'])
            data_file["sort_order"] = data_file["tumor/normal"].apply(
                lambda x: custom_sort(x)
            )
            data_file["sort_order"] = data_file["sort_order"].astype(float)
            data_file = data_file.sort_values(
                ["sort_order", "tumor/normal"]
            ).reset_index(drop=True)
            # data_file = data_file.sort_values('tumor/normal').reset_index(drop=True)
            data_file = data_file.reset_index()
        else:
            data_file = pd.read_csv(path)
        return data_file

    def construct_str(self, path: str, flow: str) -> None:
        data_file = self.parse_file(path, flow)

        for _, val in data_file.iterrows():

            if available_flows.get(flow):
                data = val.to_dict()
                chosen_flow = available_flows.get(flow)
                flow_context = FlowConstructor(chosen_flow, data=data)
                constructed_str = flow_context.construct_flow()
                # print(const_str)
                if constructed_str:
                    for strings in constructed_str:
                        print(strings)
                        print("=========")
                # return const_str
                # print(const_str)

    def execute_bash(self, path: str, flow: str) -> None:
        data_file = self.parse_file(path, flow)
        for _, val in data_file.iterrows():
            flow = val["pipeline"]
            if available_flows.get(flow):
                data = val.to_dict()
                chosen_flow = available_flows.get(flow)
                flow_context = FlowConstructor(chosen_flow, data=data)
                flow_context.execute_flow()


def test():
    flow_context = FlowConstructor(
        simpleFlow(), {"command": "echo", "output": "test.txt"}
    )
    test = flow_context.construct_flow()
    print(test)


if __name__ == "__main__":
    fire.Fire(dragenflow)
