from mcp.server.fastmcp import FastMCP

server = FastMCP("My calculator Server")

@server.tool(name="evaluate_expression", description="Evaluates a mathematical expression and returns the result")
def evaluate_expression(expression:str) -> float:
    """ Evaluates a mathematical expression and returns the result."""
    try:
        result = eval(expression, {"__builtins__": {}}, {"sum": sum})
        return result 
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}")

if __name__ == "__main__" :
    server.run()
    