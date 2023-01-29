# Components

This page provides details on the main component/entity types that make up a deployment of the ECP.

## Director
A Director manages a part of or the entire setup, orchestrating the Components according to the needs of the experiment.
It can, among other things, 
* issue commands to Actors
* request data from individual Actors
* read data from an Observer

Potentially a GUI could be attached here too.

## Actor
An Actor is a component that interfaces with a (hardware) Device and that has a specific API on the ECP side.
An Actor must contain a separate Driver object which communicates with the Device.

We define how the other ECP components interact with the Actor, how it determines and announces its capabilities, etc.
An Actor implements the mapping between ECP messages and Driver calls/attribute access.

An Actor must contain/manage/provide
* An Driver that communicates with the connected Device, including managing its lifecycle (init, operations, shutdown)
* The name of the connected instrument
* A list of available Parameters (properties/attributes to get/set) and Actions (methods to call)
* `set`/`get`/`get_all`/`call` interfaces (for incoming commands to use to act on Parameters and Actions)

An Actor may contain/manage
* A list of Parameters to poll/publish regularly (and the interval for that)
* A cache of parameter values (to avoid unnecessary communication). 
    - If caching is included, the `get*` interfaces must include a configurable cache timeout and a way to force fetching a fresh value. 
* Concurrent access management/locking
* Logging configuration

### Driver
The Driver object takes care of communicating with the Device, and is always contained in an Actor.
This object is external to ECP, for example a `pymeasure.Instrument` instance or something from another instrument library.
This is the place where all instrument libraries (including pymeasure) wire their hardware interface classes into ECP.

Interfacing with the Driver is the task of instrument-library-specific Actors.

Concerning the ECP, we draw the abstraction boundary at the Driver -- the details on how this communicates with a Device (SCPI, dll, ...) should not be relevant for the protocol details.

:::{admonition} TODO
We might want to add the notion of "Channels", especially for the multi-Director stuff
:::

## Action
An Action represents a method or function of the Driver represented by an Actor.
It can be called with zero or more arguments.

## Parameter
A Parameter represents a property (in the English, not the Pythonic sense) of the Driver represented by a Actor.
It has a name and can be read(`get`) or `set`.

:::{note}
Recent values may be cached in the Actor.
:::

It may correspond closely to _attributes_ or Python (or PyMeasure) _properties_ of the Driver.
It may have unit information that is used when sending data over the Network.

## Procedures
Sequences of steps that make up experiment runs, e.g. PyMeasure procedures.
These instructions could be consumed by a Director and trigger a sequence of commands (ramps, loops, conditionals,...).

:::{admonition} TODO
This is a placeholder, we have not fleshed out the concept yet
:::

## Processor
The processor runs some kind of processing operation on one or more inputs and produces one or more outputs.  
It can be stateless (e.g. temperature conversion) or stateful (like a PID controller).
It may act regularly of its own accord.

The Processor would send commands to an Actor, instructing it to `set`/`get`/`call` a given Parameter/Action by name, with a value if appropriate, and receive replies.

This could look for example like this:
:::{mermaid}
sequenceDiagram
    par
        Processor1->>Actor42: GET temp_K
        Note over Actor42: Driver involvement not shown
        Actor42-->>HW-on-COM1: "*TEMP?\n"
        HW-on-COM1-->>Actor42: "275.14\n"
        Actor42->>Processor1: 275.14
    and
        Processor1->>Actor11: GET temperature
        Note over Actor11: Fetched a fresh value 23ms ago, using cached value
        Actor11->>Processor1: 300.1
    end
    Note over Processor1: computes average temperature, converts to degC
    Note over Processor1: stores/caches value maybe
    Processor1->>Observer1: "Average oven temperature" 14.47 degC
:::

## Coordinator
A component primarily tasked with routing/coordinating the message flow between other Components.
It represents the intermediate zmq brokers, proxies or somesuch.

Every network needs at least one Coordinator, as all Components within a Node directly exchange messages only with the Coordinator.

Every Node must have exactly one Coordinator.

Multiple coordinator instances may be necessary for large deployments, but a single coordinator instance should be sufficient for operation.

The use of a coordinator should avoid the complexity/scaling of a purely point-to-point messaging approach. 

## Observer
A Component that receives data from other Components, e.g. for logging, storage, or plotting, either directly in a streaming fashion, batched, or delayed.
It only consumes message streams, but does not command `Actors`.

:::{note} Depending on setup, some commanding might be necessary, e.g. to subscribe/register.
:::

## Notes 
### Complexity scaling
We want to leave the entry threshold as low as possible, the learning curve flat, and the usability of ECP modular.
If someone wants to just connect with an Actor instance, that should be possible, and easily understood, as the Actors have a consistent API.
This assumes that a library-specific Actor has already been written by the library maintainers.

Once a user is familiar with that, and a slightly bigger system is envisaged by them, multiple Actor classes might be used, maybe with a Processor doing some useful transformations, and a Director attached to them (via Coordinators), so all can be controlled together.
Possibly Procedures are added for sequencing, too.
Once a user is familiar with this bigger framework, they can then add new Components as needed, to grow their system one by one.

For quick tests, some simple measurements (and the first steps), one can still just open a python interpreter, connect to the hardware with an Actor (containing e.g. a `pymeasure.Instrument` Driver), and measure some things using, ideally with out-of-pymeasure's-box classes for devices, and the only thing one needs to understand for it, is the Actor interface, no need for servers, proxies, brokers, GUI, databases, etc. 

This would give users a broad freedom, while at the same time they can be guided step by small step to master bigger challenges and journeys.
