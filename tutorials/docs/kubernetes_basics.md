# Deploy basic resources inside K8S

## Create basic test resources

Lets create 2 http server basic resources, and 
connect them to dedicated services, and then to an ingress.

Create file banana.yml with the following content:

```yaml
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
```

Then create apple.yml with the following content:

```yaml
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
```

Both will create a small test http server, that will answer 'banana' 
or 'apple' depending on the one reached.

Apply these 2 files:

```
kubectl apply -f banana.yml
kubectl apply -f apple.yml
```

And check pods and services were created:

```
bluebanquise@ansible:~$ kubectl get pods
NAME         READY   STATUS    RESTARTS   AGE
apple-app    1/1     Running   0          20h
banana-app   1/1     Running   0          20h
bluebanquise@ansible:~$ kubectl get services
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
apple-service    ClusterIP   10.233.12.216   <none>        5678/TCP   20h
banana-service   ClusterIP   10.233.9.162    <none>        5678/TCP   20h
kubernetes       ClusterIP   10.233.0.1      <none>        443/TCP    20h
bluebanquise@ansible:~$
```

We can check that http server works. Ssh on a master, and try to curl these ip 
(these are internal ip, only reachable from inside the cluster).

```
bluebanquise@ansible:~$ ssh m1
bluebanquise@m1:~$ curl http://10.233.12.216:5678
apple
bluebanquise@m1:~$ curl http://10.233.9.162:5678
banana
bluebanquise@m1:~$
```

![k8s_resources_step1](images/deploy_kubernetes/k8s_resources_step2.png)

Lets now create an ingress, so these 2 web servers can be reached from the MetalLB ip.

Create file fruits.yml with the following content:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fruits
  annotations:
      ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - http:
      paths:
        - path: /apple
          pathType: Prefix
          backend:
            service:
            name: apple-service
            port:
              number: 5678
        - path: /banana
          pathType: Prefix
          backend:
            service:
            name: banana-service
            port:
              number: 5678
```

Basicaly, this ingress will bind to both apple and banana services.
If a request reach /apple url path, it will be redirected to apple 
service and so pod, and same for banana.

Apply this ingress to the K8S cluster:

```
kubectl apply -f fruits.yml
```

Check ingress has been created:

```
bluebanquise@ansible:~$ kubectl get ingress
NAME     CLASS    HOSTS   ADDRESS   PORTS   AGE
fruits   <none>   *                 80      3s
bluebanquise@ansible:~$
```

And try to reach pods on the MetalLB ip:

```
bluebanquise@ansible:~$ curl http://10.10.7.7/banana
banana
bluebanquise@ansible:~$ curl http://10.10.7.7/apple
apple
bluebanquise@ansible:~$
```

![k8s_resources_step1](images/deploy_kubernetes/k8s_resources_step3.png)

.. image:: images/scenario_kubernetes/k8s_resources_step3.svg

It is also interesting to check resources graph into Octant:

![k8s_resources_step1](images/deploy_kubernetes/octant_fruits.png)

Logout, and try to reach fruits web servers from the outside world, i.e. on 
the keepalived virtualip:

```
curl http://192.168.1.202/banana
```

If you get 'banana' as an answer, you won!

K8S cluster is now ready to accept your resources.

I suggest that your next step is to replace pods by a deployment: a pod is a single isloated resources, which is not reliable and not easily updatable without service interuption.
Using a deployment (multiple clone pods) allows to load balance their usage, increases crash resistance (if one fail, others handle), and allows rolling update them.