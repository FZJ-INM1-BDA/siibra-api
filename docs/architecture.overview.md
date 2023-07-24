Unlike python scripts, or jupyter notebook sessions, decades of advancement in web technology and internet speed have conditioned all of us to expect sub-second response time for web resources.

To achieve this in siibra-api, there exist several challenges:

> python is (by default) blocking/sychronous

Whilst modern python web frameworks (including fastapi) tries to mitigate python's shortfalls (e.g. spawning multiple workers to allow parallel requests to be processsed, usage of asynchronous APIs, such as asyncio), these cannot fully mitigate...

> siibra-python is (at the current state, on cold start) not very fast

Whilst some recent improvement been made (using ThreadPool for network requests, etc), siibra-python is still quite slow on cold starts. This is further exacerbated by ...

> a typical client (e.g. siibra-explorer) will often make tens of API calls on startup ...

... and more as the user navigates/interacts with the atlas. The API calls often can be categorized into Critical/Not, Computationally Expensive/Not. A naive design of siibra-api would often result in most/all workers hung up on Computationally Expensive, but not critical API calls, result in worsened end user experience. 

> Observability

As siibra-api will run centrally on a server (compared to siibra-python, which is dependent on the quality of user's computer and internet), metrics must be made available, to allow potential issues to be discovered and resolved sooner.


## Language of choice

> python is not a very fast language

It is not the fastest, but by most account, python is _fast enough_. When/if the response time of an average request is consistently <200ms, then we can revisit this point.
