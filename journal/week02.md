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
Dashboard
```sh
minikube dashboard
```

## kubectl
Create new deployment object:
```sh
kubectl create deployment <name> --image=<image>
```
- <name> - name to give deployment object
- <image> - name, including repo, for image since pods will pull image

Can then check deployment object via:
```sh
kubectl get deployments
kubectl get pods
```

