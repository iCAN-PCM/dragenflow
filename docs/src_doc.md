# Pipeline constructor class
Main logic of the dragenflow resides in `dragen_pipeline.py` and `dragen_commands.py` and is called by [main.py](usage).

[dragen_pipeline.py](section_two) takes care of running pipeline in particular order and save the artifact from the run like bam files, file prefixes etc, that are used by subsequent run. And `dragen_commands.py` handles only the creation of the dragen command. Its done it step first base command handles the basic dragen commands and the more pipeline specific command are added on top
of base commands.

File inside directory utility `flow.py` is an abstract class and its concrete class is `dragen_pipeline.py` similarly `command.py` is abstract class whose concrete class is  `dragen_commands.py`.

As we can see in {py:class}`src.dragen_pipeline`.

(section_two)=
## Class dragen_pipeline

```{eval-rst}
.. automodule:: src.dragen_pipeline
	:members:

```

(section_three)=
## Class dragen_commands

```{eval-rst}
.. automodule:: src.dragen_commands
	:members:

```
