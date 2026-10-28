"""Stateless API. Do not expose publicly without rate limits and resource controls."""
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
from .engine import analyze

app = FastAPI(title='VeriText API', version='1.0.0')
origins = [item.strip() for item in os.getenv('ALLOWED_ORIGINS', 'http://localhost:5500,http://127.0.0.1:5500').split(',') if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['POST', 'GET'], allow_headers=['Content-Type'])

@app.middleware('http')
async def limit_body(request: Request, call_next):
    # Bound streamed bodies too, rather than relying on Content-Length.
    from starlette.responses import JSONResponse
    size = 0
    chunks = []
    async for chunk in request.stream():
        size += len(chunk)
        if size > 1_000_000:
            return JSONResponse({'detail': 'Request exceeds 1 MB.'}, status_code=413)
        chunks.append(chunk)
    request._body = b''.join(chunks)
    return await call_next(request)

class Reference(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    text: str = Field(min_length=1, max_length=50000)

class AnalysisRequest(BaseModel):
    document: str = Field(min_length=1, max_length=50000)
    references: list[Reference] = Field(min_length=1, max_length=10)
    threshold: float = Field(default=.45, ge=.2, le=.9)

    @model_validator(mode='after')
    def validate_text(self):
        if not self.document.strip() or any(not r.text.strip() or not r.name.strip() for r in self.references):
            raise ValueError('Document, names, and references must contain non-whitespace text.')
        if sum(len(r.text) for r in self.references) > 150000:
            raise ValueError('Total reference text must be at most 150,000 characters.')
        return self

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/api/analyze')
def analyze_route(body: AnalysisRequest):
    try:
        return analyze(body.document, [r.model_dump() for r in body.references], body.threshold)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
