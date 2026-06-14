from fastapi import FastAPI

app = FastAPI(
    title="Domain-Specific Knowledge Agents API",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "agents-api",
    }