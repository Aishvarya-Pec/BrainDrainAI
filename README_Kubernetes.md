# BrainDrainAI on Kubernetes

This guide makes the Streamlit app ready for Kubernetes. It covers building a container image, creating configuration and secrets, and deploying with a `Deployment` + `Service` (and optional `Ingress`).

## 1) Build and push the image

Choose a registry (Docker Hub or GitHub Container Registry).

### Docker Hub
- Login: `docker login`
- Build: `docker build -t <dockerhub-username>/braindrainai:latest .`
- Push: `docker push <dockerhub-username>/braindrainai:latest`

### GitHub Container Registry (GHCR)
- Login: `echo $GHCR_TOKEN | docker login ghcr.io -u <github-username> --password-stdin`
- Build: `docker build -t ghcr.io/<github-username>/braindrainai:latest .`
- Push: `docker push ghcr.io/<github-username>/braindrainai:latest`

## 2) Update the deployment image

Open `k8s/deployment.yaml` and set the `image:` field to the tag you pushed, e.g.:

```
image: ghcr.io/<github-username>/braindrainai:latest
```

## 3) Provide config and secrets

Create the ConfigMap and Secret (replace values as needed):

```
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.example.yaml
```

Recommended: copy `k8s/secret.example.yaml` to `k8s/secret.yaml` and set your real values, then apply `secret.yaml` instead.

## 4) Deploy the app

```
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Check status:

```
kubectl get pods,svc
kubectl logs deploy/braindrainai -f
```

## 5) Access the app

- Port-forward locally: `kubectl port-forward svc/braindrainai 8080:80` then open `http://localhost:8080/`.
- Or create an Ingress (with NGINX) and set your domain in `k8s/ingress.example.yaml`, then apply it: `kubectl apply -f k8s/ingress.example.yaml`.

## Notes

- The container listens on port `8501`; the Service maps it to port `80` for convenience.
- Liveness/readiness probes query `/`. Streamlit returns `200` on the root path once the app is ready.
- Env vars used:
  - `FIREWORKS_API_KEY` (Secret)
  - `FIREWORKS_BASE_URL` (ConfigMap; default is `https://api.fireworks.ai/inference/v1`)
- Adjust resource requests/limits in `k8s/deployment.yaml` to match your cluster.