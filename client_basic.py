from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

# Define server parameters to run the calculator server 

server_params = StdioServerParameters(
    command = "python"  # The executabe to run the server 
    args = ["calculator_server.py"] # the server script
)

async def run():
    # Start the server as a subprocess and get stdio read/write functions 
    async with stdio_client(server_params) as (read, write):
        # Create a client session to communicvate with the server
        async with ClientSession(read, write) as session:
            # intialize the connection to the server 
            await session.initialize()

            # list available tools 
            tools = await session.list_tools()
            print("\n====Available tools ====")
            for tool in tools:
                print(f" {tool}")
            print("=================\n")

            expression = input("Enter a math expression (e.g., '5 * 7'):")

            result = await session.call_tool(
                "evaluate_expression",
                arguments={"expression": expression}
            )
            print("\n=== Calculation Result ===")
            print(f"Expression: {expression}")
            print(f"Result: {result}")
            print("==========================\n")

if __name__ == "__main__":
    asyncio.run(run())

            


