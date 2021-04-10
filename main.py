import fire
import pandas as pd

from flow import FlowConstructor
from flow_dragen import ConstructDragen
from utility.dragen_utility import custom_sort

# register flows
available_flows = {
    # "echo": ConstructFlowEcho(),
    # "head": ConstructFlowHead(),
    "dragen": ConstructDragen()
}


class HandleFlow(object):
    """
    Interface to flow objects through command line
    """

    def parse_file(self, path: str, flow: str) -> pd.DataFrame:
        """
        parse excel file(sample sheet) and return sorted pandas df
        """
        if flow == "dragen":
            data_file = pd.read_csv(path, skiprows=4)
            data_file["tumor/normal"] = data_file["tumor/normal"].fillna(0)
            data_file["sort_order"] = data_file["tumor/normal"].apply(
                lambda x: custom_sort(x)
            )
            data_file["sort_order"] = data_file["sort_order"].astype(float)
            data_file = data_file.sort_values(
                ["sort_order", "tumor/normal"]
            ).reset_index(drop=True)
            data_file = data_file.reset_index()
        else:
            data_file = pd.read_csv(path)
        return data_file

    def construct_str(self, path: str, flow: str) -> None:
        """
        create appropriate flow object from argument supplied from cli
        & invoke construct_flow method of flow object
        """
        data_file = self.parse_file(path, flow)

        for _, val in data_file.iterrows():

            if available_flows.get(flow):
                data = val.to_dict()
                chosen_flow = available_flows.get(flow)
                flow_context = FlowConstructor(chosen_flow, data=data)
                constructed_str = flow_context.construct_flow()
                if constructed_str:
                    for strings in constructed_str:
                        print(strings)
                        print("=========")

    def execute_bash(self, path: str, flow: str) -> None:
        """
        create appropriate flow object from argument supplied from cli
        & invoke execute flow method of flow object
        """
        data_file = self.parse_file(path, flow)
        for _, val in data_file.iterrows():
            flow = val["pipeline"]
            if available_flows.get(flow):
                data = val.to_dict()
                chosen_flow = available_flows.get(flow)
                flow_context = FlowConstructor(chosen_flow, data=data)
                flow_context.execute_flow()


if __name__ == "__main__":
    fire.Fire(HandleFlow)
