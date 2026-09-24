# Python (FastAPI / Gunicorn) Kubernetes Sizing Lab

Demonstrates sizing worker processes in multi-process Python web servers to avoid Copy-On-Write memory explosion and container OOMKills.

## Key Rules
1. **Worker Formula:** Size workers according to the container's **allocated CPU cores**, NOT physical host cores.
2. **Periodic Worker Recycling:** Use `--max-requests 2000` to prevent memory fragmentation and slow leaks from native C extensions.
