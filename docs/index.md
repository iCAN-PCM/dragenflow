# Welcome to Dragenflow's documentation!

# Usage

Tool to convert sample sheet into dragen command and execute the command

The main interface too the application is through `main.py`.

```{note}
To see the dragen command and the order of execution enable dry run. (No code will be execute in process)
```

## For Dry Run
```
python3 main.py  --path samplesheet.csv --dryrun True
```
## To execute the command
```
python3 main.py  --path samplesheet.csv
```

## Code documentation
When you are executing the command through command line you are essentially interfacing with main.py

```{toctree}
:maxdepth: 2
:caption: "Contents:"

usage
src_doc
```



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
