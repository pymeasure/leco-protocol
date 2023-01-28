(iface)=
# Interfaces

An Interface is the way Components can communicate with each other.


:::{glossary}

zmq
    [Zeromq](https://zeromq.org/) is a message passing framework that can communicate over multiple
    network communication protocols, such as TCP, UDP, and websockets. It implements several common message passing 
    patterns, such as the "Publish / Subscribe" pattern.

queue.py
    The queue.py interface utilizes the builtin Python [queue](https://docs.python.org/3/library/queue.html) system for 
    passing messages between Python threads.

object
    The object interface is interacted with inline of the codebase, in the same thread as the Component that 
    initializes it. For example, if the output of `Procedure` was only accessible in code `result = Procedure.output()`,
    the interface of `Procedure` would be labelled as an "object interface".

:::
