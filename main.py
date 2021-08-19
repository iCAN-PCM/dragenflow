"""
main.py
=====================================
Public interface of dragenflow project
"""

import argparse
import logging
from typing import List

from src.dragen_pipeline import ConstructDragenPipeline
from src.utility.flow import FlowConstructor
from src.utility.dragen_utility import (
    basic_reader,
    create_fastq_dir,
    file_parse,
    run_type,
    sort_list,
)

# register flows/pipeline
available_pipeline = {"dragen": ConstructDragenPipeline()}

logging.basicConfig(filename="app.log", filemode="w", level=logging.DEBUG)
logging.info("started new logging session")


class HandleFlow(object):
    """
    Interface to flow(pipeline) objects through command line
    """

    def parse_file(self, path: str, flow: str) -> List[dict]:
        """Read excel file(sample sheet) in csv

        if flow/pipeline is dragen sort based on column 'tumor/normal'
        else just read the csv file. Mehtod returns list of dictionary
        with column name as key and value as row.

        Args:
            path: excel file (sample sheet)
            flow: flow to use (at the moment no other implementation than dragen)
        Returns:
            rows in excels file as list of dictionaries

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
        """Construct bash command as string and execute if dry_run is False

        This creates appropriate flow object from argument supplied from cli
        & invoke construct_flow method of flow object

        Args:
            path: path to the samplesheet
            pipeline: name of the pipeline to use
            bash_cmd: name of the bash command to use
            dry_run: enable/disable dry run
        Returns:
            List of bash cmd if dry run is enabled else return code of command & stdout

        """
        logging.info(f"dry run mode: {dry_run}")
        outputs = []
        command_list = []
        data_file = self.parse_file(path, pipeline)
        logging.info("creating fastq directory")
        data_file = create_fastq_dir(data_file, dry_run=dry_run)
        logging.info("assigning runtype")
        data_file1 = run_type(data_file)
        data_file = sort_list(data_file1)
        chosen_pipeline = available_pipeline.get(pipeline)
        flow_context = FlowConstructor(chosen_pipeline)
        for data in data_file:
            if available_pipeline.get(pipeline):
                # skip if pipeline is not dragen
                if data["pipeline"].lower() != "dragen":
                    continue
                logging.info("Creating dragen commands")
                constructed_str = flow_context.construct_flow(data=data)
                # collect all executable command in a list
                logging.info(f"Input dict:{data}")
                for c in constructed_str:
                    logging.info(f"command:{c}")
                    command_list.append([str(data["fastq_dir"]), c])
        if dry_run:
            for path, str_command in command_list:
                print("chdir " + path)
                outputs.append(str_command)
                print(str_command)
                print("===========")
        else:
            logging.info("Executing commands:")
            for path, str_command in command_list:
                output, arglist = FlowConstructor.execute_flow(
                    command=str_command, base_cmd=bash_cmd, wd_path=path
                )
                logging.info(f"Executed command: {arglist}")
                logging.info(f"Return code: {output.returncode}")
                outputs.append([(output.returncode, output.stdout)])
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
    parser.add_argument("-c", "--cmd", default=None)
    args = parser.parse_args()
    handle = HandleFlow()
    handle.execute_bash(path=args.path[0], bash_cmd=args.cmd, dry_run=args.dryrun)
