![example workflow](https://github.com/iCAN-PCM/dragenflow/actions/workflows/tests.yml/badge.svg)
## Uses
- dry run to print dragen command in screen
`python3 main.py --path ./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet_updated.csv --dryrun`
- submit dragen command to queue
`python3 main.py --path ./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet_updated.csv`
- enable pre and post scripts
`python3 main.py --path ./path/210317_A00464_0300_BHW7FTDMXX/test_samplesheet_updated.csv --script`

## To run the test in local development environment
install nox `python3 -m pip install nox`
- inside the dragenflow directory to run all test `nox`
- to test just linting `nox -rs lint`
- to test just typing `nox -rs typing`
- to run the actual test file `nox -rs tests`
