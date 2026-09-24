# Node.js Kubernetes Sizing Lab

Demonstrates sizing Node.js V8 heap versus native memory buffers and avoiding single-threaded Event Loop throttling.

## Pitfall (`deployment-bad.yaml`)
* Omits `--max-old-space-size`, causing V8 to size itself based on node memory.
* Sets a low CPU limit (`cpu: 200m`) that freezes the single-threaded Event Loop.

## Best Practice (`deployment-optimal.yaml`)
* Sets `--max-old-space-size=768` inside a `1024Mi` container.
* Omits CPU limits or provides generous headroom to protect Event Loop responsiveness.
