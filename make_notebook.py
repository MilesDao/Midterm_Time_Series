"""Convert group5_analysis.py ('# %% <id>' cells) into an executed notebook."""
import re
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

src = open("group5_analysis.py", encoding="utf8").read()
nb = nbformat.v4.new_notebook()
for cid, body in re.findall(r"^# %% (\S+)\n(.*?)(?=^# %% |\Z)", src, flags=re.S | re.M):
    body = body.strip("\n")
    if cid == "md":
        nb.cells.append(nbformat.v4.new_markdown_cell(body))
    else:
        cell = nbformat.v4.new_code_cell(body)
        cell.metadata["tags"] = [cid]
        nb.cells.append(cell)

ExecutePreprocessor(timeout=1800, kernel_name="python3").preprocess(nb, {"metadata": {"path": "."}})
nbformat.write(nb, "Group5_TimeSeries.ipynb")
print("ok", len(nb.cells), "cells")
