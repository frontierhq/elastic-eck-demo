# elastic-eck-demo

## Overview

## FAQs

### How do I get the elastic user password?

`kubectl get secret <cluster>-es-elastic-user -n <namespace> -o=jsonpath='{.data.elastic}' | base64 --decode; echo`

[LINK]

### How do I get the current license stats?

`kubectl -n elastic-system get configmap elastic-licensing -o json | jq .data`

[LINK]
