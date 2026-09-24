import os
import resource
from fastapi import FastAPI

app = FastAPI(title="Python Rightsizing Demo")

@app.get("/healthz")
def healthz():
    # Read Resident Set Size (RSS) in KB
    rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {
        "status": "healthy",
        "pid": os.getpid(),
        "cpu_count_visible": os.cpu_count(),
        "rss_mb": round(rss_kb / 1024, 2)
    }
