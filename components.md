# Components

This page provides details on the main component/entity types that make up a deployment of the ECP.

## Director
A Director manages a part of or the entire setup, orchestrating the actors and observers according to the needs of the experiment.
It can, among other things, 
* issue commands to actors
* request data from individual actors
* read data from an observer

Potentially a GUI could be attached here too.

## Actor
The Actor is a component which (typically) instantiates one or more Driver class and/or does some kind of processing.
Actions which the actor can take could be anything from measuring on a regular basis ("acting" as a sensor), commanding hardware devices through the use of the driver to do X or Y, processing some data and re-emitting results (e.g. a PID controller).

The actor is part of the communication network, that means it is listening for messages and maybe sending messages by itself.

Potentially a GUI could be attached here too.

## Driver
A Driver is a component that interfaces with some hardware in a manner we don't specify, and that has a specific API on the ECP side.
This might contain or wrap a `pymeasure.Instrument` instance or something from another instrument library.
This is the place where all instrument libraries (including pymeasure) wire their hardware interface classes into ECP.

Concerning the ECP, we draw the abstraction boundary at the Driver -- the details on how this communicates with hardware (SCPI, dll, ...) should not be relevant for the protocol details.
What we define is how the other ECP components interact with the Driver, how it determines and announces its capabilities, etc.

## Procedures
Sequences of commands that make up experiment runs, e.g. PyMeasure procedures.

Procedures as they are now should maybe not rely on actors, but could, and again, need to look into it further). Once a user is familiar with this bigger framework, they can then add new actors, to grow their system one by one.

```{note} This is a placeholder, we have not defined the concept yet
```

### Actor Driver separation
We want to keep Actor and Driver separated, to leave the entry threshold as low as possible, the learning curve flat, and the usability of ECP modular.
If someone wants to just connect with a Driver instance, directly, that should be possible, and when looking at the class, easily understood (and implemented).

Once a user is familiar with that, and a slightly bigger system is envisaged by them, one or two Driver classes (which might already exist for this specific instrument in pymeasure, or have easy templates) might get packaged into Actors, and a director attached to them (via broker/proxy/whatever), so both can be controlled together (e.g. in a sequence-like fashion.

For quick tests, some simple measurements (and the first steps), one can still just open a python interpreter, connect to the hardware with `Instrument`, and measure a small sequence of things, ideally with out-of-pymeasure's-box classes for devices, and the only thing one needs to understand for it, is `Instrument` (and maybe not even that really). No need for servers, proxies, brokers, GUI, databases, etc. 

This would give users a broad freedom, while at the same time they can be guided in a small-step by small-step fashion to master bigger challenges and journeys.

```{note} There was a paragraph here on the that I (BB) integrated into the actor and driver texts, it did not seem current anymore.
Also, please review the text on Driver and Actor, which I tried to make more consistent.
```

## Coordinator
A component primarily concerned with routing/coordinating the message flow between other components.
It represent the intermediate zmq brokers, proxies or somesuch.
Multiple coordinator instances may be necessary for large deployments, but a single coordinator instance should be sufficient for operation.

The presence of a coordinator should avoid the complexity/scaling of a purely point-to-point approach. 
Currently, this corresponds to the zmq majordomo broker, and/or a zmq proxy.

## Observer
A component that receives data from other components, e.g. for logging, storage, or plotting, either directly in a streaming fashion, batched, or delayed.
It only consumes message streams, but does not command `actors`.

```{note} Depending on setup, some commanding might be necessary, e.g. to subscribe/register.
```
