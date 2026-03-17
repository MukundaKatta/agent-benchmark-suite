"""FastAPI application for agent-benchmark-suite."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import logging, time, uuid

logger = logging.getLogger(__name__)
app = FastAPI(title="agent-benchmark-suite", version="0.1.0", description="agent-benchmark-suite API")

# --- Models ---
class ProcessRequest(BaseModel):
    input: str
    options: Dict[str, Any] = {}
    context: Optional[Dict[str, Any]] = None

class ProcessResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    success: bool
    result: Any
    processing_time_ms: float = 0
    metadata: Dict[str, Any] = {}

class BatchRequest(BaseModel):
    items: List[ProcessRequest]

# --- State ---
_history: List[Dict] = []

# --- Routes ---
@app.get("/health")
def health():
    return {"status": "ok", "service": "agent-benchmark-suite", "version": "0.1.0"}

@app.post("/process", response_model=ProcessResponse)
async def process(req: ProcessRequest):
    start = time.time()
    try:
        result = _core_process(req.input, req.options)
        elapsed = (time.time() - start) * 1000
        resp = ProcessResponse(success=True, result=result, processing_time_ms=round(elapsed, 2),
                              metadata={"service": "agent-benchmark-suite", "input_length": len(req.input)})
        _history.append({"id": resp.id, "input": req.input[:100], "success": True})
        return resp
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(500, str(e))

@app.post("/batch")
async def batch_process(req: BatchRequest):
    results = []
    for item in req.items:
        start = time.time()
        result = _core_process(item.input, item.options)
        elapsed = (time.time() - start) * 1000
        results.append(ProcessResponse(success=True, result=result, processing_time_ms=round(elapsed, 2)))
    return {"results": [r.model_dump() for r in results], "total": len(results)}

@app.get("/history")
def get_history(limit: int = 20):
    return _history[-limit:]

@app.get("/status")
def status():
    return {"service": "agent-benchmark-suite", "version": "0.1.0", "ready": True,
            "total_processed": len(_history)}

def _core_process(input_text: str, options: Dict[str, Any] = {}) -> Dict[str, Any]:
    """Core processing logic."""
    words = input_text.split()
    return {
        "input_length": len(input_text),
        "word_count": len(words),
        "processed": True,
        "options_applied": list(options.keys()),
    }
