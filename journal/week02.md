# Week 2
## Minikube
Installed minikube on Windows for local testing.
Commands to run:
```sh
minikube start --driver=docker
minikube start --driver=wsl2
```
Check if running with:
```sh
minikube status
```
Dashboard:
```sh
minikube dashboard
```
To get address to view application:
```sh
minikube service <name>
```

## kubectl
Create new deployment object:
```sh
kubectl create deployment <name> --image=<image>
```
- <name> - name to give deployment object
- <image> - name, including repo, for image since pods will pull image

Check deployment object:
```sh
kubectl get deployments
kubectl get pods
```
Create service from pod:
```sh
kubectl expose deployment <name> --type=<ClusterIP|NodePort|LoadBalancer> --port=<port>
```
Check services:
```sh
kubectl get services
```
Scale:
```sh
kubectl scale deployment/<name> --replicas=<number>
```
Update:
```sh
kubectl set image deployment/<name> <old image name>=<new image>
kubectl set image deployment/<name> <old image name>=<new image>:<tag>
```
Delete:
```sh
kubectl delete <name>
kubectl delete deployment <deployment name>
kubectl delete service <service name>

kubectl delete <type> -l <label>=<label value>
kubectl delete deployments,services -l group=example
```
Status check:
```sh
kubectl rollout status deployment/<name>
```
History:
```sh
kubectl rollout history deployment/<name>
kubectl rollout history deployment/<name> --revision=<number>
```
Rollback:
```sh
kubectl rollout undo deployment/<name>
kubectl rollout undo deployment/<name> --to-revision=<number>
```
Declarative approach:
```sh
kubectl apply -f=<filename>
kubectl apply -f=deployment.yaml
kubectl apply -f=<filename> -f=<filename> ...
kubectl apply -f=deployment.yaml -f=service.yaml

kubectl delete -f=<filename>
kubectl delete -f=<filename> -f=<filename> ...
kubectl delete -f=deployment.yaml -f=service.yaml
```
### deployment.yaml example (any deployment file)
https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <deployment name>
spec:
  replicas: <number>
  selector:
    matchLabels:
      <label>: <label value> # should match the labels below
    # matchExpressions:
    #   - {key: <label>, operator: <In|NotIn|...>, values: [<label value 1>, <label value 2>]}
  template:
    metadata:
      labels:
        <label>: <label value>
    spec:
      containers:
        - name: <name>
          image: <image>
          livenessProbe:
            httpGet:
              path: <path> # ex) /healthCheck
              port: <port>
            periodSeconds: <number>
            initialDelaySeconds: <number>
```
### service.yaml example (any service file)
https://kubernetes.io/docs/concepts/services-networking/service/
```yaml
apiVersion: v1
kind: Service
metadata:
  name: <name>
spec:
  selector:
    <label>: <label value> # should match those in deployment file
  ports:
    - protocol: TCP
      port: 80
      targetPort: <exposed port>
  type: <ClusterIP|NodePort|LoadBalancer>
```
### combined.yaml example (deployment and service file merged)
To merge the files, just seperate with "---":
```yaml
apiVersion: v1
kind: Service
metadata:
  name: <name>
spec:
  selector:
    <label>: <label value> # should match those in deployment file
  ports:
    - protocol: TCP
      port: 80
      targetPort: <exposed port>
  type: <ClusterIP|NodePort|LoadBalancer>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <deployment name>
spec:
  replicas: <number>
  selector:
    matchLabels:
      <label>: <label value> # should match the labels below
  template:
    metadata:
      labels:
        <label>: <label value>
    spec:
      containers:
        - name: <name>
          image: <image>
```