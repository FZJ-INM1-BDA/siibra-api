{WIP PLACEHOLDER}

## Current architectural designs

{WIP PLACEHOLDER}

### all-in-one

In an all in one 

#### module dependency graph

```mermaid
flowchart TD
	server
	models
	serialization
	common.data_handlers

	siibra

	server --> |response models| models
	server --> |direct call| common.data_handlers

	common.data_handlers --> |get siibra instances| siibra
	common.data_handlers --> |serialize siibra instances| serialization

	serialization --> |build| models
```

#### architectural diagram

```mermaid
flowchart TD

    Internet
    RespCache[Cache database]
    OpenshiftServer[Server Pod]

    Internet --> |queries| OpenshiftServer
    OpenshiftServer --> |caches| RespCache
    RespCache --> |provides cache| OpenshiftServer

    OpenshiftServer --> |responds| Internet
```


#### How to activate

```bash
export SIIBRA_API_ROLE=all
uvicorn api.server.api
```

#### Pro & Con

Pro:

Easy to setup, easy to debug. Fewer moving parts, less likely to "break".

Con:

Does not scale easily. On production, available workers can easily be overwhelmed, resulting in 

### server-worker

On the contrary, the design that offers some flexibility is the server-worker design.

#### Module dependency graph

```mermaid
flowchart TD
	server
	models
	serialization
	common.data_handlers.server[common.data_handlers]
	common.data_handlers.worker[common.data_handlers]
	worker

	siibra

	server --> |response models| models
	server --> |schedule task| common.data_handlers.server

	worker --> |awaits task| common.data_handlers.worker

	common.data_handlers.worker --> |get siibra instances| siibra
	common.data_handlers.worker --> |serialize siibra instances| serialization

	serialization --> |build| models
```

#### architectural diagram

```mermaid
flowchart TD

    Internet
    RespCache[Cache database]
    OpenshiftServer[Server Pod]
    OpenshiftWorker1[Worker Pod1]
    OpenshiftWorker2[Worker Pod2]
    OpenshiftWorker3[Worker Pod3]
    OpenshiftWorker4[Worker Pod4]

    QueueMessageBroker[Queue Broker]
    QueueResultBackend[Result Broker]

    Internet --> |queries| OpenshiftServer
    OpenshiftServer --> |caches| RespCache
    RespCache --> |provides cache| OpenshiftServer
    OpenshiftServer --> |sends task|QueueMessageBroker
    
    QueueMessageBroker --> OpenshiftWorker1
    QueueMessageBroker --> OpenshiftWorker2
    QueueMessageBroker --> OpenshiftWorker3
    QueueMessageBroker --> OpenshiftWorker4

    OpenshiftWorker1 -->  QueueResultBackend
    OpenshiftWorker2 -->  QueueResultBackend
    OpenshiftWorker3 -->  QueueResultBackend
    OpenshiftWorker4 -->  QueueResultBackend

    QueueResultBackend --> |send result| OpenshiftServer
    OpenshiftServer --> |responds| Internet
```
