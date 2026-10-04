from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")

docs = {
  
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures",
    "outlook.pdf": "This document presents the projected future performance of the system",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment"
}


@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string."
)
def read_document(
    doc_id: str = Field(description="Id of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    
    return docs[doc_id]

@mcp.tool(
    name = 'edit_document',
    description = 'edit a document by replacing a string in the document content with a new string'
    )
def edit_document(
    doc_id : str = Field(description='id of the document that will be edited'),
    old_str : str = Field(description = 'The text to replace.Must match exacrly , including whitespaces'),
    new_str : str = Field(description= 'The new text to insert to place of the old text')
) :
    if doc_id not in docs:
        raise ValueError(f'doc with id{doc_id} not found')
    docs[doc_id] = docs[doc_id].replace(old_str,new_str)    

async def list_tools(self) -> list[types.Tool]:
    result = await self.session().list_tools()
    return result.tools

async def call_tool(
    self, tool_name: str, tool_input: dict
) -> types.CallToolResult | None:
    return await self.session().call_tool(tool_name, tool_input)

if __name__ == "__main__":
    mcp.run(transport="stdio")