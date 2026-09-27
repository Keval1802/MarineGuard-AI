from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.auth import require_user
from app.mcp.server import MarineIntelligenceMCPServer

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol (MCP)"])
mcp_server = MarineIntelligenceMCPServer()

class MCPToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}
    allowed_scopes: Optional[List[str]] = None

@router.get("/tools")
def list_mcp_tools(current_user: Dict[str, Any] = Depends(require_user)):
    """GET /api/v1/mcp/tools (AUTHENTICATED) - List all registered MCP tools & capability scopes."""
    return {
        "status": "success",
        "total_tools": len(mcp_server.tools),
        "tools": mcp_server.list_tools()
    }

@router.post("/call")
async def call_mcp_tool(
    request: MCPToolCallRequest = Body(...),
    current_user: Dict[str, Any] = Depends(require_user)
):
    """POST /api/v1/mcp/call (AUTHENTICATED) - Execute controlled MCP tool by name."""
    res = await mcp_server.call_tool(
        name=request.tool_name,
        kwargs=request.arguments,
        allowed_scopes=request.allowed_scopes
    )
    return res
