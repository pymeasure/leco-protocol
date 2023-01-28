# Architecture: Pymeasure v0.11 

This is a description of the Pymeasure architecture at version 0.11

## Components

### Manager

- Type: [Director](comp:director), [Coordinator](comp:coordinator)
- Interface: {term}`Queue.py`
- Input: procedure, status
- Output: status
- Description:
  - The pymeasure Manager is an optional component that is used only with the pymeasure graphic user interface. It 
    manages a queue of experiment runs for a given Procedure.

### Procedure

- Type: [Procedure](comp:procedure), [Actor](comp:actor)
- Interface: {term}`object`
- Input: N/A
- Output: N/A
- Description:
  - A pymeasure Procedure defines the control sequence for an experiment. As an `object`, it is instantiated and 
    controlled in code by the Worker component. It uses pymeasure Drivers to connect and communicate with different 
    instruments.

### Recorder

- Type: [Observer](comp:observer)
- Interface: {term}`queue.py`
- Input: result
- Output: N/A
- Description:
  - The pymeasure Recorder records ongoing datapoints from an experiment to an output file. It utilizes the builtin 
    python `logging` library for recording output to a file handle.

### Results
- Type: [Observer](comp:observer)
- Interface: {term}`object`
- Input: status
- Output: N/A
- Description:
  - The pymeasure Results creates the output file for an experiment run, although it doesn't write data 
    points to it, see Recorder. It is typically instantiated and controlled by the Manager to periodically read the 
    output file data points to graph datapoints in the GUI.

### Worker

- Type: [Director](comp:director), [Coordinator](comp:coordinator)
- Interface: {term}`queue.py`, {term}`zmq`
- Input: procedure, status
- Output: result, status
- Description:
  - A pymeasure Worker is the main component that executes an experiment run, directing other components such as 
    Procedure and Recorder. The `zmq` interface is not utilized by default.

## Diagrams
GUI Implementation

```{mermaid}
graph TD
  Manager-->Results
  Results-->Worker
  Worker-->Recorder
  Worker-->Procedure
  Worker-->Manager
  Procedure-->Worker
```

Script Implementation

```{mermaid}
graph TD
  Results-->Worker
  Worker-->Recorder
  Worker-->Procedure
  Procedure-->Worker
```