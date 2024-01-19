# docu-nator

A multi level engine for documenting python code with AI (LLMs) with guard rails via static analysis



## Preq

- run the sphinx quicstart to generate the boiler plate

## how to use

```bash
# A single file
python -m src.main --file /python.file --temp-dir /temp 

# A full directory and sub directories
python -m src.main --file /python.file --temp /temp --patch ./patch

```

## apply the patches

- note its a git patch, so your code must be commited...

```bash
make patch
```

## VScode docstrings now show the definitions

[vscode]!(./assets/vs_code.png)
