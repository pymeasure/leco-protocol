# Glossary
An alphabetical list of terms with a short description.
To help distinguish between the plain English meaning of these terms, and our more specific use, we Capitalize terms from this glossary when we refer to the ECP-specific meaning.

:::{glossary}

Actor
    A component which instantiates one or more Driver classes or does some kind of processing, see {ref}`components.md#actor`.

Component
    A type of entity, a set of which make up the ECP communication Network, see {ref}`components.md#components`.

Coordinator
    A component primarily concerned with routing/coordinating the message flow, see {ref}`components.md#coordinator`.

Device
    Some piece of hardware controlled via ECP.

Director
    A component which takes part in orchestrating a (i.e. ECP-controlled) measurement setup, see {ref}`components.md#director`.

Driver
    A driver offers a standardized interface to communicate with some Device (possibly via some intermediate object), see {ref}`components.md#driver`. 

ECP
    The **E**xperiment **C**ontrol **P**rotocol framework.

Network
    The web of Components communicating with each other in an ECP deployment.

Observer
    A component that receives data from other components, e.g. for logging, storage, or plotting, see {ref}`components.md#observer`.
:::
