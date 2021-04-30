import argparse
import logging
from typing import List

# import fire

from flow import FlowConstructor
from flow_dragen import ConstructDragen
from utility.dragen_utility import basic_reader, file_parse

# register flows
available_flows = {
    # "echo": ConstructFlowEcho(),
    # "head": ConstructFlowHead(),
    "dragen": ConstructDragen()
}

logging.basicConfig(filename="app.log", filemode="w", level=logging.DEBUG)
logging.info("started new logging session")


class HandleFlow(object):
    """
    Interface to flow objects through command line
    """

    def parse_file(self, path: str, flow: str) -> list:
        """
        parse excel file(sample sheet) and return sorted pandas df
        """
        if flow == "dragen":
            data_file = file_parse(path)
            return data_file
        else:
            data_file = basic_reader(path)
            return data_file

    def construct_str(self, path: str, flow: str = "dragen") -> List[str]:
        """
        create appropriate flow object from argument supplied from cli
        & invoke construct_flow method of flow object
        """
        logging.info("executing construct str")
        data_file = self.parse_file(path, flow)
        commands = []

        for val in data_file:
            if available_flows.get(flow):
                data = val
                chosen_flow = available_flows.get(flow)
                flow_context = FlowConstructor(chosen_flow, data=data)
                constructed_str = flow_context.construct_flow()
                if constructed_str:
                    for strings in constructed_str:
                        commands.append(strings)
                        print(strings)
                        print("=========")
        return commands

    def execute_bash(
        self, path: str, flow: str = "dragen", bash_cmd: str = "echo"
    ) -> list:
        """
        create appropriate flow object from argument supplied from cli
        & invoke execute flow method of flow object
        """
        logging.info("executing bash")
        execution_status = []
        data_file = self.parse_file(path, flow)
        for val in data_file:
            if available_flows.get(flow):
                data = val
                chosen_flow = available_flows.get(flow)
                flow_context = FlowConstructor(chosen_flow, data=data)
                outputs = flow_context.execute_flow(base_cmd=bash_cmd)
                execution_status.append(outputs)
        return execution_status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="dragenflow", description="Process some integers."
    )
    parser.add_argument("--execute", type=str, required=False, nargs=1)
    parser.add_argument("--flow", type=str, action="store", required=False, nargs=1)
    parser.add_argument("--dryrun", type=str, required=False, nargs=1)
    args = parser.parse_args()
    if args.execute is not None:
        handle = HandleFlow()
        handle.execute_bash(path=args.execute[0])
        print(args.execute)
    elif args.dryrun is not None:
        print(args.dryrun)
        handle = HandleFlow()
        handle.construct_str(path=args.dryrun[0])
    else:
        print("unknown command")
