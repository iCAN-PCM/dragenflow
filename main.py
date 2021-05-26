import argparse
import logging
from typing import List

from src.utility.flow import FlowConstructor
from src.dragen_pipeline import ConstructDragenPipeline
from src.utility.dragen_utility import basic_reader, create_fastq_dir, file_parse

# register flows/pipeline
available_pipeline = {"dragen": ConstructDragenPipeline()}

logging.basicConfig(filename="app.log", filemode="w", level=logging.DEBUG)
logging.info("started new logging session")


class HandleFlow(object):
    """
    Interface to flow(pipeline) objects through command line
    """

    def parse_file(self, path: str, flow: str) -> List[dict]:
        """Read excel file(sample sheet)

        if flow/pipeline is is dragen sort based on col tumor/normal
        else just read the csv file. Mehtod returns list of dictionary
        with column name as key and value as row.
        """
        if flow == "dragen":
            data_file = file_parse(path)
            return data_file
        else:
            data_file = basic_reader(path)
            return data_file

    def execute_bash(
        self,
        path: str,
        pipeline: str = "dragen",
        bash_cmd: str = "echo",
        dry_run: bool = False,
    ) -> list:
        """
        Construct bash command as string and execute if dry_run is False

        This creates appropriate flow object from argument supplied from cli
        & invoke construct_flow method of flow object
        """
        logging.info("executing bash")
        outputs = []
        data_file = self.parse_file(path, pipeline)
        logging.info("creating fastq directory")
        data_file = create_fastq_dir(data_file, dry_run=dry_run)

        for val in data_file:
            if available_pipeline.get(pipeline):
                data = val
                # skip if pipeline is not dragen
                if data["pipeline"].lower() != "dragen":
                    continue
                chosen_pipeline = available_pipeline.get(pipeline)
                flow_context = FlowConstructor(chosen_pipeline, data=data)
                if dry_run is True:
                    constructed_str = flow_context.construct_flow()
                    if constructed_str:
                        for strings in constructed_str:
                            outputs.append(strings)
                            print(strings)
                            print("=========")
                else:
                    output = flow_context.execute_flow(base_cmd=bash_cmd)
                    outputs.append(output)
        return outputs


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="dragenflow",
        description="Process given samplesheet and turn into dragen commands.",
    )
    parser.add_argument(
        "-p", "--path", type=str, action="store", required=True, nargs=1
    )
    parser.add_argument("-d", "--dryrun", default=False, action="store_true")
    parser.add_argument("-q", "--queue", default=False, action="store_true")
    args = parser.parse_args()
    handle = HandleFlow()
    bash_str = "echo"
    if args.queue:
        bash_str = "queue"
    handle.execute_bash(path=args.path[0], bash_cmd=bash_str, dry_run=args.dryrun)
