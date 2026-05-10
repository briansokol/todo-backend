from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["tags"])

NOT_IMPLEMENTED = JSONResponse(
    status_code=501,
    content={"detail": "Tags feature not yet implemented. See specs/add-tags/ in todo-meta."},
)


@router.get("/tags")
def list_tags():
    """List all tags. NOT YET IMPLEMENTED."""
    return NOT_IMPLEMENTED


@router.post("/tags")
def create_tag():
    """Create a tag. NOT YET IMPLEMENTED."""
    return NOT_IMPLEMENTED


@router.post("/todos/{todo_id}/tags/{tag_id}")
def add_tag_to_todo(todo_id: int, tag_id: int):
    """Add a tag to a todo. NOT YET IMPLEMENTED."""
    return NOT_IMPLEMENTED


@router.delete("/todos/{todo_id}/tags/{tag_id}")
def remove_tag_from_todo(todo_id: int, tag_id: int):
    """Remove a tag from a todo. NOT YET IMPLEMENTED."""
    return NOT_IMPLEMENTED
