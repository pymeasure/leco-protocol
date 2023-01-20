# Components

This page provides details on the main component/entity types that make up a deployment of the ECP.

## Director
A Director manages a part of or the entire setup, orchestrating the actors and observers according to the needs of the experiment.
It can, among other things, 
* issue commands to actors
* request data from individual actors
* read data from an observer

Potentially a GUI could be attached here too.

## Action
An Action represents a method or function of the device represented by a Driver.
It can be called with zero or more arguments.

## Actor
The actor participates in the network listening for commands and acts on them. 
It may act regularly of its own accord.
Typically an actor controls one or several devices via Drivers and/or does some kind of processing.
Actions which the actor can take could be anything from measuring on a regular basis ("acting" as a sensor), commanding hardware devices through the use of the driver to do X or Y, processing some data and re-emitting results (e.g. a PID controller).

Potentially a GUI could be attached here too.

The Actor would send commands to a Driver, instructing it to `set`/`get`/`call` a given Parameter/Action by name, with a value if appropriate, and receive replies.

This could look for example like this:
:::{mermaid}
sequenceDiagram
    par
        Actor1->>Driver42: GET temp_K
        Driver42-->>HW-on-COM1: "*TEMP?\n"
        HW-on-COM1-->>Driver42: "275.14\n"
        Driver42->>Actor1: 275.14
    and
        Actor1->>Driver11: GET temperature
        Note over Driver11: Fetched a fresh value 23ms ago, using cached value
        Driver11->>Actor1: 300.1
    end
    Note over Actor1: computes average temperature, converts to degC
    Note over Actor1: stores/caches value maybe
    Actor1->>Observer1: "Average oven temperature" 14.47 degC
:::

:::{admonition} TODO
We could achieve more complete separation and make the Actor purely about processing _inputs_, doing some _operation_ and generating _outputs_.
This could be either stateless (temperature conversion) or stateful (PID control).
Maybe a better name would be "Processor" then.
This means that _all_ device-related stuff stays compartmentalized in the Driver, and an Actor would address that Driver over the network (to fetch the Parameter values it is interested in).

Thoughts?
:::

## Driver
A Driver is a component that interfaces with a (hardware) Device in a manner we don't specify, and that has a specific API on the ECP side.
A driver must contain some object dealing with hardware communication.
This may be a `pymeasure.Instrument` instance or something from another instrument library.
This is the place where all instrument libraries (including pymeasure) wire their hardware interface classes into ECP.

Concerning the ECP, we draw the abstraction boundary at the Driver -- the details on how this communicates with a Device (SCPI, dll, ...) should not be relevant for the protocol details.
What we define is how the other ECP components interact with the Driver, how it determines and announces its capabilities, etc.

A driver must contain/manage
* An object that communicates with the connected Device, including managing its lifecycle (init, operations, shutdown)
* The name of the connected instrument
* A list of available Parameters (properties/attributes to get/set) and Actions(methods to call)
* `set`/`get`/`get_all`/`call` interfaces (for incoming commands to use to act on Parameters and Actions)

A driver may contain/manage
* A list of Parameters to poll/publish regularly (and the interval for that)
* A cache of parameter values (to avoid unnecessary communication). 
    - If caching is included, the `get*` interfaces must include a configurable cache timeout and a way to force fetching a fresh value. 
* Concurrent access management/locking
* Logging configuration

:::{admonition} TODO
We might want to add the notion of "Channels", especially for the multi-Director stuff
:::

## Parameter
A Parameter is a property (in the English, not the Pythonic sense) of the device represented by a Driver
It has a name and can be read(`get`) or `set`.

:::{note}
Recent values may be cached in the Driver.
:::

It may correspond closely to _attributes_ or Python (or PyMeasure) _properties_ of the instrument interface classes.
It may have unit information, that is used when sending data over the network.

## Procedures
Sequences of steps that make up experiment runs, e.g. PyMeasure procedures.
These instructions could be consumed by a Director and trigger a sequence of commands (ramps, loops, conditionals,...).

:::{admonition} TODO
This is a placeholder, we have not fleshed out the concept yet
:::

## Coordinator
A component primarily concerned with routing/coordinating the message flow between other components.
It represents the intermediate zmq brokers, proxies or somesuch.
Multiple coordinator instances may be necessary for large deployments, but a single coordinator instance should be sufficient for operation.

The presence of a coordinator should avoid the complexity/scaling of a purely point-to-point approach. 
Currently, this corresponds to the something like a zmq majordomo broker, and/or a zmq proxy.

## Observer
A component that receives data from other components, e.g. for logging, storage, or plotting, either directly in a streaming fashion, batched, or delayed.
It only consumes message streams, but does not command `actors`.

:::{note} Depending on setup, some commanding might be necessary, e.g. to subscribe/register.
:::

## Notes 
### Actor Driver separation
We want to keep Actor and Driver separated, to leave the entry threshold as low as possible, the learning curve flat, and the usability of ECP modular.
If someone wants to just connect with a Driver instance, directly, that should be possible, and when looking at the class, easily understood (and implemented).

Once a user is familiar with that, and a slightly bigger system is envisaged by them, one or two Driver classes (which might already exist for these specific instruments in pymeasure, or have easy templates) might get packaged into Actors, and a director attached to them (via broker/proxy/whatever), so both can be controlled together (e.g. in a sequence-like fashion.
Once a user is familiar with this bigger framework, they can then add new actors, to grow their system one by one.

For quick tests, some simple measurements (and the first steps), one can still just open a python interpreter, connect to the hardware with `Instrument`, and measure a small sequence of things, ideally with out-of-pymeasure's-box classes for devices, and the only thing one needs to understand for it, is `Instrument` (and maybe not even that really). No need for servers, proxies, brokers, GUI, databases, etc. 

This would give users a broad freedom, while at the same time they can be guided in a small-step by small-step fashion to master bigger challenges and journeys.

:::{admonition} TODO
There was a paragraph here on the that I (BB) integrated into the actor and driver texts, it did not seem current anymore.
Also, please review the text on Driver and Actor, which I tried to make more consistent.
:::
