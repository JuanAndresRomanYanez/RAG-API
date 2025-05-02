from fastapi import APIRouter, HTTPException
from app.services.query import query_answer
from app.schemas import QueryRequest, QueryResponse

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    try:
        result = query_answer(
            question=request.question,
            history=request.history,
            summary=request.summary or ""
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))