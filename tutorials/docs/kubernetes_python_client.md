# Manage a Kubernetes cluster with Python client

The Kubernetes Python client allows to automate some tasks on your Kubernetes cluster.

The whole sources are available on the project github: https://github.com/kubernetes-client/python

Documentation is available at: https://github.com/kubernetes-client/python/blob/master/kubernetes/README.md

You can find on this last page all API endpoints. This page is your best ally, as you can easily find your needed enpoint, and all its related parameters.

## Usage

The client can be used 2 ways:

1. Outside of the cluster, by running on a system that owns a kubeconfig file.
2. Inside the cluster, by running in a pod, using in-config.

Most of the time, first way is to deploy things and monitor the cluster, while second way is to automate some tasks internaly of the cluster by having a daemon running directly "inside the place".

Both methods uses the same syntax, only the way of connection to the cluster changes.

## Install the client

Create first a local Python virtual environment, to prevent packages issues with the operating system:

```
python3 -m venv venv_kube_client
source venv_kube_client/bin/activate
```

Now install the client via pip3 command:

```
pip3 install kubernetes
```

## Connect to a cluster

### Using a local kubeconfig

If you wish to connect to the cluster using a local kubeconfig (aka you are able to use kubectl commands localy to manage your cluster), simply import the kubernetes module, and use dedicated function:

```python
from kubernetes import config

# From a machine with a defined kubeconfig file
config.load_kube_config()
```

This will use the default cluster set on the current system.

Or if you have multiple clusters, you can specify the kubeconfig to be uses:

```python
from kubernetes import config

# From a specific json file
with open('my_kubeconfig.json') as f:
  kubeconfig = json.load(f)
  config.load_kube_config_from_dictionary(kubeconfig)
```

### Using in pod config

If you are running your Python application from inside a pod in the cluster, you can directly use the auto-mounted configuration:

```python
from kubernetes import config

# From a inside a pod of the cluster
config.load_incluster_config()
```

## Get version of the target cluster

As a first attempt to communicate with the cluster, lets grab its version:

```python
from kubernetes import config, client

config.load_kube_config()

print(client.VersionApi().get_code())
```

And execute this code:

```
python3 mycode.py
```

You should get an output with some details about version of the remote cluster running.
This is equivalent to the `kubectl version` command.

## Life of a resource

Lets cover the life cycle of a basic resource: a configmap.
We will work in the `default` namespace.

### Create a resource

First step is to create a basic configmap, in namespace default.
To do so, we are going to use the create_namespaced_config_map from the CoreV1Api (https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#create_namespaced_config_map)

```python
from kubernetes import config, client

config.load_kube_config()

# Create the configmap object first

my_configmap = client.V1ConfigMap(
    metadata=client.V1ObjectMeta(
        name="my-test-configmap",
        labels={}
    ),
    data={
        "name": "Laguna",
        "age": "35"
    }
)

# Now spawn the configmap in namsepace default

client.CoreV1Api().create_namespaced_config_map("default", my_configmap)
```

Execute this code, and check that the config map exist:

```
kubectl describe configmap my-test-configmap -n default 
```

Output should be:

```
root@7fa3d9f804da:~/# kubectl describe configmap my-test-configmap -n default 

Name:         my-test-configmap
Namespace:    default
Labels:       <none>
Annotations:  <none>

Data
====
age:
----
35
name:
----
Laguna

BinaryData
====

Events:  <none>
root@7fa3d9f804da:~/# 
```

### Get status of a resource

We now need to access data inside the configmap.

We will use the read_namespaced_config_map function (https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#read_namespaced_config_map).

```python
from kubernetes import config, client

config.load_kube_config()

my_data = client.CoreV1Api().read_namespaced_config_map("my-test-configmap", "default").data

print(my_data)
```

Output should be:

```
root@7fa3d9f804da:~/# python3 read_cm.py 
{'age': '35', 'name': 'Laguna'}
root@7fa3d9f804da:~/#
```

### Replace a resource

We now want to update our configmap. Note that "cold" resources can be updated on the fly, but some "active" resources, like a pod, cannot be updated directly. You need for example to rely on a deployment, and update the deployment itself to be able to rollup related pods.

Since a configmap is a cold resource, we can update it on the fly. We will use the replace_namespaced_config_map function.

```python
from kubernetes import config, client

config.load_kube_config()

my_configmap = client.V1ConfigMap(
    metadata=client.V1ObjectMeta(
        name="my-test-configmap",
        labels={}
    ),
    data={
        "name": "Kiros Seagill",
        "age": "38"
    }
)

client.CoreV1Api().replace_namespaced_config_map("my-test-configmap", "default", my_configmap)
```

Checking the configmap confirms it was updated:

```
root@7fa3d9f804da:~/# kubectl describe configmap my-test-configmap -n default 
Name:         my-test-configmap
Namespace:    default
Labels:       <none>
Annotations:  <none>

Data
====
age:
----
38
name:
----
Kiros Seagill

BinaryData
====

Events:  <none>
root@7fa3d9f804da:~/# 
```

### Delete a resource

We can finaly simply delete the config map using delete_namespaced_config_map function:

```python
from kubernetes import config, client

config.load_kube_config()

client.CoreV1Api().delete_namespaced_config_map("my-test-configmap", "default")
```

After this, configmap should be deleted:

```
root@7fa3d9f804da:~/# kubectl describe configmap my-test-configmap -n default 
Error from server (NotFound): configmaps "my-test-configmap" not found
root@7fa3d9f804da:~/# 
```

## Secure the code

It may happen that for any reasons the negotiations with remote cluster fail, due to an API error.

To prevent your code to crash, you can rely on the ApiException to capture these errors and print them in logs:

```python
from kubernetes import config, client
from kubernetes.client.rest import ApiException

config.load_kube_config()

try:
    resp = client.AppsV1Api().read_namespaced_deployment(name="my-deployment", namespace="default")
except ApiException as e:
  print("Exception when calling read_namespaced_deployment: %s\n" % e)
```

In case of error, which will happen because this deployment do not exist on the cluster, you should get:

```
Exception when calling read_namespaced_deployment: (404)
Reason: Not Found
HTTP response headers: HTTPHeaderDict({'Audit-Id': 'XXXXXXXXXXXX', 'Cache-Control': 'no-cache, private', 'Content-Type': 'application/json', 'X-Kubernetes-Pf-Flowschema-Uid': 'XXXXXXXXXXXXXXX', 'X-Kubernetes-Pf-Prioritylevel-Uid': 'XXXXXXXXXXXXXXXXX', 'Date': 'XXXXXXXXXX', 'Content-Length': '228'})
HTTP response body: {"kind":"Status","apiVersion":"v1","metadata":{},"status":"Failure","message":"deployments.apps \"my-deployment\" not found","reason":"NotFound","details":{"name":"my-deployment","group":"apps","kind":"deployments"},"code":404}
```

## Full example

Lets create a daemon that is in charge of spawning 2 http servers, their related services, and an ingress to reach them.
That daemon will also be in charge of making sure these resources exist, whatever happen.

Note that this is an example, not something to be used in production.

Note also that we rely on the assumption here that a 404 error when getting the status of a resource means it does not exist. This could not be 100% true, but that is a good asumption.

```python
from kubernetes import config, client
from kubernetes.client.rest import ApiException
import time

config.load_kube_config()

# Generic function to create a pod
def create_http_server(fruit):

  http_server_pod = client.V1Pod(
    metadata=client.V1ObjectMeta(
      name=str(fruit) + "-pod",
      labels={
        "app": str(fruit)
      }
    ),
    spec=client.V1PodSpec(
      containers=[
        client.V1Container(
          name="http-server",
          image="hashicorp/http-echo",
          args=[
            "-text=" + str(fruit)
          ]
        )
      ]
    )
  )
  client.CoreV1Api().create_namespaced_pod(
    "default",
    http_server_pod
  )

# Generic function to create a service
def create_http_server_service(fruit):

  http_server_service = client.V1Service(
    metadata=client.V1ObjectMeta(
      name=str(fruit) + "-svc",
    ),
    spec=client.V1ServiceSpec(
      selector={
        "app": str(fruit)
      },
      ports=[
        client.V1ServicePort(
          port=5678
        )
      ]
    )
  )
  client.CoreV1Api().create_namespaced_service(
    "default",
    http_server_service
  )

# Function to create the ingress
def create_main_ingress():

  my_ingress = client.V1Ingress(
    metadata=client.V1ObjectMeta(
      name="fruits-ingress",
      annotations={
        "nginx.ingress.kubernetes.io/rewrite-target": '/$1'
      }
    ),
    spec=client.V1IngressSpec(
      rules=[
        client.V1IngressRule(
          host="fruits.example",
          http=client.V1HTTPIngressRuleValue(
            paths=[
              client.V1HTTPIngressPath(
                path='/apple',
                path_type="Prefix",
                backend=client.V1IngressBackend(
                  service=client.V1IngressServiceBackend(
                    name="apple-service",
                    port=client.V1ServiceBackendPort(
                      number=5678
                    )
                  )
                )
              ),
              client.V1HTTPIngressPath(
                path='/banana',
                path_type="Prefix",
                backend=client.V1IngressBackend(
                  service=client.V1IngressServiceBackend(
                    name="banana-service",
                    port=client.V1ServiceBackendPort(
                      number=5678
                    )
                  )
                )
              ),
            ]
          )
        )
      ]
    )
  )

  client.NetworkingV1Api().create_namespaced_ingress(
      "default",
      my_ingress
  )

if __name__ == '__main__':

  # Enter an infinite loop. Kill it via Ctrl + C
  while True:

    # We try to grab a resource via API
    # If it does not exist, then ApiException is raised
    try:
        client.CoreV1Api().read_namespaced_pod(name="apple-pod", namespace="default")
    except ApiException as e:
      if e.status == 404:
        print("Apple pod does not exist, creating the resource.")
        create_http_server("apple")

    try:
        client.CoreV1Api().read_namespaced_pod(name="banana-pod", namespace="default")
    except ApiException as e:
      if e.status == 404:
        print("Banana pod does not exist, creating the resource.")
        create_http_server("banana")

    try:
        client.CoreV1Api().read_namespaced_service(name="apple-svc", namespace="default")
    except ApiException as e:
      if e.status == 404:
        print("Apple service does not exist, creating the resource.")
        create_http_server_service("apple")

    try:
        client.CoreV1Api().read_namespaced_service(name="banana-svc", namespace="default")
    except ApiException as e:
      if e.status == 404:
        print("Banana service does not exist, creating the resource.")
        create_http_server_service("banana")

    try:
        client.NetworkingV1Api().read_namespaced_ingress(name="fruits-ingress", namespace="default")
    except ApiException as e:
      if e.status == 404:
        print("Fruits ingress does not exist, creating the resource.")
        create_main_ingress()

    time.sleep(5)
```

Launch this small daemon, and try to reach the resources.
The way to reach the resources can depend on the way your kubernetes cluster is running, we assume here a minikube running localy:

```
oxedions@prima:~/$ curl --resolve "fruits.example:80:$( minikube ip )" -i http://fruits.example/apple
HTTP/1.1 200 OK
Date: Mon, 20 May 2024 18:50:15 GMT
Content-Type: text/plain; charset=utf-8
Content-Length: 6
Connection: keep-alive
X-App-Name: http-echo
X-App-Version: 1.0.0

apple
oxedions@prima:~/$ curl --resolve "fruits.example:80:$( minikube ip )" -i http://fruits.example/banana
HTTP/1.1 200 OK
Date: Mon, 20 May 2024 18:50:23 GMT
Content-Type: text/plain; charset=utf-8
Content-Length: 7
Connection: keep-alive
X-App-Name: http-echo
X-App-Version: 1.0.0

banana
oxedions@prima:~/$ 
```

## Conclusion

This is a small introduction to Python Kubernetes client package. Feel free to update this small code to adapt to your cluster and your needs.

All documentation is available online, and tons of examples are provided on usual development websites.

Small tips to continue:

1. When using in-cluster daemons, be careful of service account attached to the pod. When running the python code from an external system (via a kubeconfig file), you are usualy "god of the place", with all admin rights. But when running inside a pod, you do not have rights to go out of the current namespace. If you need to extend the pod's rights, be careful to not give it cluster-admin role!
2. Nearly all Python objects are 100% identical to YAML resources definitions. When dealing with a complex resource, it is usually best to first define it as a YAML, ensure it works on a cluster, and then convert it to Python object as the YAML format is easier most of the time at first.
