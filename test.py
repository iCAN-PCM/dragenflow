#%%
import subprocess

st = subprocess.run(["echo", "hello"])
st

# %%
st1 = subprocess.run(["head", "-n", "10", "./app.py"])
st1

# %%
test1 = "tesing how to write"
with open ('run.sh', 'w') as rsh:
    rsh.write(f'''\
#! /bin/bash
echo {test1} >> ./test.txt
''')

# %%
test = subprocess.run("./run.sh", capture_output=True)
test.stdout
# %%
