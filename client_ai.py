from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import anthropic
import asyncio

# Define server parameters to run the calculator server
server_params = StdioServerParameters(
    command="python",              # The executable to run
    args=["calculator_server.py"], # The server script (you’ll need to create this)
    env=None                       # Optional: environment variables (None uses defaults)
)

async def run():
    # Start the server as a subprocess and get stdio read/write functions
    async with stdio_client(server_params) as (read, write):
        # Create a client session to communicate with the server
        async with ClientSession(read, write) as session:
            # Initialize the connection to the server
            await session.initialize()

            # List available tools to confirm what’s there
            tools = await session.list_tools()
            print("\n=== Available Tools ===")
            for tool in tools:
                print(f"- {tool}")
            print("========================\n")

            # Assume tools have name, description, input_schema attributes
            tools_for_claude = [
            {
                "name": "evaluate_expression",
                "description": "Evaluates a mathematical expression and returns the result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate."
                }
            },
            "required": ["expression"]
        }
    }
]
            
            # Get a question from the user
            user_query = input("Ask me a question (e.g., 'What’s 5 times 7?'): ")
            
            # Set up Anthropic client (replace with your API key)
            anthropic_client = anthropic.Anthropic(api_key="api")
            
            # Send initial message to Claude with the user’s query and tools
            response = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": user_query}],
                tools=tools_for_claude,
            )
            
            # Check if Claude wants to use a tool
            if response.stop_reason == "tool_use":
                print("Claude wants to use a tool.")
                tool_call = next((block for block in response.content if block.type == "tool_use"), None)
                if tool_call:
                    tool_name = tool_call.name
                    tool_input = tool_call.input
                    # Call the tool via MCP
                    try:
                        result = await session.call_tool(tool_name, arguments=tool_input)
                        # Create tool result message for Claude
                        tool_result_message = {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_call.id,
                                    "content": str(result),
                                }
                            ],
                        }
                        # Send follow-up message to Claude with the tool result
                        follow_up_response = anthropic_client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=1000,
                            messages=[
                                {"role": "user", "content": user_query},
                                {"role": "assistant", "content": response.content},
                                tool_result_message,
                            ],
                        )
                        final_answer = follow_up_response.content[0].text
                    except Exception as e:
                        final_answer = f"Error calling tool: {e}"
                else:
                    final_answer = "Claude tried to use a tool, but no tool_use block was found."
            else:
                final_answer = response.content[0].text
            
            # Print the assistant’s response
            print("\n=== Assistant’s Response ===")
            print(final_answer)
            print("============================\n")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(run())
