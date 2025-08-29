# List of control protocol methods

List of methods defined by LECO.
You MAY implement the optional methods of this list and you MUST implement the methods obligatory for your type of Component.
All methods implemented in a Component MUST adhere to this list or MUST have a name different to any method in this list.

## Component

Any Component, i.e. any participant in the LECO protocol, MUST offer the [OpenRPC Service Discovery Method](https://spec.open-rpc.org/#service-discovery-method) and the following methods.

:::{data-viewer}
:expand:
:file: schemas/component.json
:::

Any Component MAY offer ANY of the following methods.
Components SHOULD offer ``shut_down``.

:::{data-viewer}
:expand:
:file: schemas/component_optional.json
:::

## Coordinator

Control protocol Coordinators are also {ref}`Components <methods.md#Component>`.
Furthermore, Coordinators MUST offer the following methods.

:::{leco-json-viewer}
:expand:
:file: schemas/coordinator.json
:::

## Actor

An Actor is a {ref}`methods.md#Component`.
Additionally, it MUST offer the following methods.

:::{leco-json-viewer}
:expand:
:file: schemas/actor.json
:::

## Polling Actor

An {ref}`methods.md#Actor`, which supports regular polling of values, MUST implement these methods.

:::{data-viewer}
:expand:
:file: schemas/polling_actor.json
:::

## Locking Actor

An {ref}`methods.md#Actor` which support locking resources MUST offer the following methods.

:::{data-viewer}
:expand:
:file: schemas/locking_actor.json
:::

Accessing a locked resource (the whole Component or parts of it) or trying to unlock one, locked by another Component, will raise appropriate {ref}`control_protocol.md#errors`.
