=================
Deploy Kubernetes
=================

BlueBanquise and Kubernetes works pretty well together.

While BlueBanquise is in charge of provisioning bare metal / on premise infrastructure, 
Kubespray can deploy a production ready Kubernetes cluster over this infrastructure.

This result in 2 layers on the hardware, both autonomous but working together.

Deploy BlueBanquise CORE cluster
================================

>>>>>>>>>>>>> SCHEMA

Deploy Kubernetes cluster
=========================

Grab kubespray
--------------

Configure kubespray
-------------------

Deploy K8S
----------

Check cluster works
-------------------

Now that cluster is deployed, we need to dialog with it.
For that, we are going to install kubectl:

.. code-block:: text

  sudo apt-get update && sudo apt-get install -y apt-transport-https
  curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
  echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
  sudo apt-get update
  sudo apt-get install -y kubectl

Then, ssh on master1 and grab the content of credentials file:

.. code-block:: text

  ssh m1 cat /etc/kubernetes/admin.conf

And copy this content on ~/.kube/config:

.. code-block:: text

  mkdir -p ~/.kube
  vim ~/.kube/config

And check the cluster is running as expected:

.. code-block:: text

  kubectl cluster-info
  kubectl get nodes

Configure Kubernetes cluster
============================

Now that the K8S cluster is running, we need to adjust few parameters to be 
able to use it on a bare metal hardware.

Configure nginx-ingress together with MetalLB
---------------------------------------------

We want our ingress resources to be reachable over a virtual ip, spawned by MetalLB, and 
connected to our proxy servers.

>>>>>>>>>>>>>>>>>> scehma

Create file nginx-ingress-metallb.yml with the following content:

.. code-block:: yaml

    # Source: https://github.com/kubernetes/ingress-nginx/blob/main/charts/ingress-nginx/templates/controller-service-webhook.yaml
    apiVersion: v1
    kind: Service
    metadata:
    labels:
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/instance: ingress-nginx
        app.kubernetes.io/component: controller
    name: ingress-nginx-controller-admission
    namespace: ingress-nginx
    spec:
    type: ClusterIP
    ports:
        - name: https-webhook
        port: 443
        targetPort: webhook
    selector:
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/part-of: ingress-nginx
    ---
    # Source: https://github.com/kubernetes/ingress-nginx/blob/main/charts/ingress-nginx/templates/controller-service.yaml
    apiVersion: v1
    kind: Service
    metadata:
    labels:
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/instance: ingress-nginx
        app.kubernetes.io/component: controller
    name: ingress-nginx-controller
    namespace: ingress-nginx
    spec:
    type: LoadBalancer
    externalTrafficPolicy: Cluster
    ports:
        - name: http
        port: 80
        protocol: TCP
        targetPort: http
        - name: https
        port: 443
        protocol: TCP
        targetPort: https
    selector:
        app.kubernetes.io/name: ingress-nginx
        app.kubernetes.io/part-of: ingress-nginx

And apply it:

.. code-block:: text

  kubectl apply -f nginx-ingress-metallb.yml

You should now be able to see the address given by MetalLB to reach ingress resources:

.. code-block:: text

    bluebanquise@ansible:~$ kubectl get services -n ingress-nginx
    NAME                                 TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
    ingress-nginx-controller             LoadBalancer   10.233.6.175    10.10.7.7     80:32694/TCP,443:32099/TCP   16h
    ingress-nginx-controller-admission   ClusterIP      10.233.45.203   <none>        443/TCP                      16h
    bluebanquise@ansible:~$

Here: 10.10.7.7

Create test resources
---------------------

Lets create 2 http server basic resources, and connect them to dedicated services, and then to an ingress.

>>>>>>>>>>>>>>>>>>

Create file banana.yml with the following content:

.. code-block:: yaml

    kind: Pod
    apiVersion: v1
    metadata:
    name: banana-app
    labels:
        app: banana
    spec:
    containers:
        - name: banana-app
        image: hashicorp/http-echo
        args:
            - "-text=banana"

    ---

    kind: Service
    apiVersion: v1
    metadata:
    name: banana-service
    spec:
    selector:
        app: banana
    ports:
        - port: 5678 # Default port for image

Then create apple.yml with the following content:

.. code-block:: yaml

    kind: Pod
    apiVersion: v1
    metadata:
    name: apple-app
    labels:
        app: apple
    spec:
    containers:
        - name: apple-app
        image: hashicorp/http-echo
        args:
            - "-text=apple"

    ---

    kind: Service
    apiVersion: v1
    metadata:
    name: apple-service
    spec:
    selector:
        app: apple
    ports:
        - port: 5678 # Default port for image

Both will 



# Kubernetes over BlueBanquise

## Deploy BlueBanquise CORE cluster

## Tune few cluster parameters

ipv4 forwarding stuff
iptables -t nat -A POSTROUTING -s 10.10.0.0/16 -o enp0s3 -j MASQUERADE

no firewall


oxedion@m1:~$ sudo cat /etc/kubernetes/admin.conf

oxedion@management1:~$ vi .kube/config
oxedion@management1:~$ kubectl version
Client Version: version.Info{Major:"1", Minor:"23", GitVersion:"v1.23.4", GitCommit:"e6c093d87ea4cbb530a7b2ae91e54c0842d8308a", GitTreeState:"clean", BuildDate:"2022-02-16T12:38:05Z", GoVersion:"go1.17.7", Compiler:"gc", Platform:"linux/amd64"}
Server Version: version.Info{Major:"1", Minor:"22", GitVersion:"v1.22.5", GitCommit:"5c99e2ac2ff9a3c549d9ca665e7bc05a3e18f07e", GitTreeState:"clean", BuildDate:"2021-12-16T08:32:32Z", GoVersion:"go1.16.12", Compiler:"gc", Platform:"linux/amd64"}
oxedion@management1:~$ kubectl get nodes
NAME   STATUS   ROLES                  AGE     VERSION
m1     Ready    control-plane,master   6m24s   v1.22.5
m2     Ready    control-plane,master   6m4s    v1.22.5
m3     Ready    control-plane,master   5m52s   v1.22.5
w1     Ready    <none>                 4m49s   v1.22.5
w2     Ready    <none>                 4m48s   v1.22.5
oxedion@management1:~$

