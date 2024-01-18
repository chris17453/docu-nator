# docu-nator

A multi level engine for documenting python code with AI (LLMs) with guard rails via static analysis


## how to use


## Preq

- run the sphinx quicstart to generate the boiler plate

```bash
# A single file
python -m src.main --file /python.file --temp-dir /temp 

# A full directory and sub directories
python -m src.main --file /python.file --temp /temp --patch ./patch

```

