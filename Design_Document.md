# Design a Scalable Agentic System

## 1. Problem Statement

We need to design a scalable agentic AI system that can work with a large number of tools and APIs, ranging from 100+ tools to thousands of tools.

When an LLM is given too many tools, its performance can decrease. It may select the wrong tool, generate incorrect parameters, or fail to complete the user's request.

The goal is to design a system that allows a user to interact with the agent using natural language while the system intelligently identifies and executes the appropriate tool or sequence of tools.

## 2. Example Scenario

Consider a PayPal API collection containing more than 50 APIs for invoices, payments, disputes, reports, and other operations.

A user should be able to ask questions such as:

- "Send an invoice for $50."
- "What was my total sales volume last month?"
- "Is there a dispute open from user_123?"

The agent should determine which API or sequence of APIs is required and provide the correct parameters.

## 3. Main Goal

The main goal is to design an architecture that can efficiently select the appropriate tools as the number of available tools grows from 100+ to thousands.
## 4. Proposed System Architecture

The system will use a central Agent Orchestrator instead of giving all available tools directly to the LLM.

The main components are:

1. User Interface
   - Accepts the user's natural language request.

2. Agent Orchestrator
   - Understands the user's request.
   - Maintains the current task state.
   - Coordinates the other components.

3. Tool Discovery / Router
   - Searches for the most relevant tools based on the user's request.
   - Reduces the large tool collection to a small set of candidate tools.
   - The LLM only receives the relevant tools instead of all available tools.

4. Tool Registry
   - Stores information about all available tools.
   - Each tool contains its name, description, parameters, category, and API information.

5. Tool Executor
   - Executes the selected API/tool.
   - Validates parameters before execution.
   - Returns the result to the agent.

6. RAG Pipeline Tool
   - Searches product documentation, API documentation, and knowledge bases.
   - Helps the agent understand how a tool or API should be used.

7. System Search Tool
   - Searches system capabilities, logs, and previous requests.
   - Can answer questions about available tools and request status.

8. Error Handler
   - Handles API failures, invalid parameters, authentication errors, and tool execution failures.
   - Allows the agent to retry or select another appropriate tool when possible.
   ## 5. Tool Selection and Routing

The system should not expose all available tools to the LLM at the same time.

Instead, a Tool Router will first identify the tools that are relevant to the user's request.

### Tool Selection Process

1. The user sends a natural language request.

2. The Agent Orchestrator analyzes the request and identifies the required task.

3. The Tool Router searches the Tool Registry for relevant tools.

4. The router selects a small number of candidate tools instead of passing hundreds or thousands of tools to the LLM.

5. The LLM receives only the relevant candidate tools.

6. The LLM selects the appropriate tool and generates the required parameters.

7. The Tool Executor validates the parameters and executes the tool.

8. The result is returned to the Agent Orchestrator.

9. The agent provides the final response to the user.

### Example

User request:

"Send an invoice for $50."

The router searches the tool registry and identifies relevant invoice tools.

For example:

- create_invoice
- send_invoice
- get_invoice

The LLM receives these relevant tools and determines that creating and sending an invoice may require a sequence of operations.

This approach prevents the LLM from having to choose directly from hundreds or thousands of unrelated tools.
## 6. Tool Registry

The Tool Registry maintains metadata about all available tools and APIs.

Instead of sending every tool definition to the LLM, the system searches the registry and retrieves only the relevant tools.

### Tool Metadata

Each tool should contain:

- Tool name
- Description
- Category
- Input parameters
- Required parameters
- API endpoint
- HTTP method
- Authentication requirements
- Related keywords

### Example Tool Registry

| Tool Name | Category | Description |
|---|---|---|
| create_invoice | Invoice | Creates a new invoice |
| send_invoice | Invoice | Sends an invoice to a customer |
| get_invoice | Invoice | Retrieves invoice details |
| get_sales_report | Reports | Retrieves sales information |
| get_dispute | Disputes | Checks dispute information |
| refund_payment | Payments | Processes a payment refund |

### Tool Search

When a user sends a request, the Tool Router searches the registry using the request's meaning and relevant keywords.

For example:

User request:

"What was my total sales volume last month?"

The router identifies the category as "Reports" and retrieves tools related to sales reports.

Only the relevant tools are then provided to the LLM.

This keeps the LLM's tool-selection context small even when the system contains thousands of tools.
## 7. RAG Pipeline Tool

The RAG (Retrieval-Augmented Generation) Pipeline Tool helps the agent retrieve relevant information from a knowledge base.

It can search:

- API documentation
- Product documentation
- User guides
- Tool usage instructions

### RAG Workflow

1. Receive the user's question.
2. Convert the question into a search query.
3. Search the knowledge base.
4. Retrieve the most relevant documents.
5. Provide the retrieved information to the agent.
6. Use the information to select or correctly use a tool.

### Example

User asks:

"How do I create an invoice with a due date?"

The RAG tool searches the API documentation and retrieves the information about the invoice API and its required parameters.

The agent can then use this information to correctly call the appropriate tool.


## 8. System Search Tool

The System Search Tool allows the agent to search information about the running system.

It can search:

- Available tools
- Tool capabilities
- System logs
- Previous request status
- Execution information

### Example 1

User asks:

"What tools are available for managing invoices?"

The System Search Tool searches the Tool Registry and returns relevant invoice-related tools.

### Example 2

User asks:

"What's the status of my last request?"

The System Search Tool searches the system records and returns the status of the previous request.

This allows the agent to answer system-related questions without exposing all system information to the LLM at once.
## 9. State Management

The agent should maintain the state of the current task throughout the interaction.

The state can contain:

- User request
- Selected tools
- Tool parameters
- Tool execution results
- Current execution step
- Errors
- Final response

This allows the agent to remember what has already been completed and continue the task without starting again.

### Example

For the request:

"Create and send an invoice for $50."

The agent may perform the following steps:

1. Identify the customer.
2. Create the invoice.
3. Verify the invoice.
4. Send the invoice.
5. Return the result to the user.

The state records the result of each step.

If one step fails, the agent can identify the failed step and handle the error instead of repeating the entire workflow.


## 10. Multi-Step Tool Execution

Some user requests require multiple tools to be executed in a specific order.

The Agent Orchestrator should create an execution plan when multiple tools are required.

### Example

User request:

"Create an invoice for $50 and send it to the customer."

Execution:

User Request
     |
     v
Tool Router
     |
     v
create_invoice
     |
     v
Invoice Created
     |
     v
send_invoice
     |
     v
Invoice Sent
     |
     v
Final Response

The state is updated after every tool execution.

This allows the system to support both single-tool requests and complex multi-tool workflows.
## 11. Error Handling

The system should handle failures safely instead of stopping the entire task.

Common errors include:

- Incorrect tool selection
- Missing parameters
- Invalid parameters
- API errors
- Authentication errors
- Tool timeout
- Tool unavailable

### Error Handling Process

1. Execute the selected tool.
2. Check the tool response.
3. If successful, continue to the next step.
4. If an error occurs, identify the type of error.
5. Correct the parameters or select another suitable tool when possible.
6. Retry the operation within a limited number of attempts.
7. If the operation still fails, return a clear error message to the user.


## 12. Retry Strategy

Retries should be limited to prevent infinite execution loops.

For example:

- Maximum retry attempts: 2
- Validate parameters before retrying.
- Do not retry permanent errors such as invalid authentication.
- Retry temporary failures such as timeouts when appropriate.

### Example

If the `send_invoice` tool fails because a required parameter is missing:

Tool Execution
     |
     v
Error Detected
     |
     v
Validate Parameters
     |
     v
Correct Parameters
     |
     v
Retry Tool
     |
     v
Success / Final Error

The system should also record errors in the execution state so that the agent knows which step failed.
## 13. Scalability

The system should remain efficient as the number of tools increases from 100+ to thousands.

The main strategy is to avoid sending the complete tool collection to the LLM.

### Scalable Tool Selection

The system uses the following approach:

1. Store all tools in the Tool Registry.
2. Organize tools using categories and metadata.
3. Use the Tool Router to search for relevant tools.
4. Retrieve only a small set of candidate tools.
5. Pass only the candidate tools to the LLM.
6. Execute the selected tool.
7. Store the execution result in the current state.

### Scaling Example

With 100 tools:

User Request
    |
    v
Tool Router
    |
    v
Relevant Tools
    |
    v
LLM
    |
    v
Tool Execution

With 1,000+ tools, the same architecture is used.

The difference is that the Tool Router searches a larger registry and still provides only the relevant candidate tools to the LLM.

### Benefits

This architecture:

- Reduces the number of tools exposed to the LLM.
- Reduces tool-selection confusion.
- Reduces unnecessary context.
- Makes the system easier to maintain.
- Allows new tools to be added without changing the main agent.
- Supports scaling from hundreds to thousands of tools.

The Tool Registry and Tool Router therefore act as an abstraction layer between the large tool collection and the LLM.
## 14. End-to-End Workflow

The complete workflow of the proposed system is:

User
  |
  v
User Request
  |
  v
Agent Orchestrator
  |
  v
Understand User Intent
  |
  +----------------------+
  |                      |
  v                      v
Tool Router          RAG Pipeline
  |                      |
  v                      v
Search Tool          Search Documentation
Registry                  |
  |                       |
  +-----------+-----------+
              |
              v
      Relevant Tools
              |
              v
             LLM
              |
              v
     Select Tool + Parameters
              |
              v
       Parameter Validation
              |
              v
       Tool Executor
              |
        +-----+-----+
        |           |
     Success       Error
        |           |
        v           v
 Update State    Error Handler
        |           |
        |       Retry / Correct
        |           |
        +-----+-----+
              |
              v
       Final Response
              |
              v
             User


### Example: Invoice Request

User:

"Send an invoice for $50."

Workflow:

1. The Agent Orchestrator receives the request.
2. The Tool Router identifies invoice-related tools.
3. The relevant tools are retrieved from the Tool Registry.
4. The LLM determines the required tool and parameters.
5. The Tool Executor validates the parameters.
6. The invoice API is executed.
7. The result is stored in the state.
8. If another API is required, the next step is executed.
9. The final result is returned to the user.

This workflow allows the same architecture to support simple requests as well as multi-step tasks.
## 15. Technology Stack

### Prototype
- Python – core implementation
- Custom tool registry and routing logic
- Rule-based parameter validation and extraction
- In-memory documentation store for RAG
- Python-based system search
- Custom state management
- Simulated tool execution

### Production Extension
- LangGraph – workflow and state orchestration
- Vector Database – scalable semantic search for tools and documentation
- FastAPI – API layer for integrating the agent with external applications
- LLM – natural-language understanding and intelligent tool selection
- Pydantic – structured parameter validation

### Framework Trade-offs

The prototype was implemented from scratch using Python to keep the architecture simple, transparent, and easy to demonstrate. This avoids unnecessary framework complexity during the assessment.

For a production system with hundreds or thousands of tools, LangGraph can be introduced for workflow orchestration, a vector database can support semantic tool discovery, and FastAPI can expose the agent as a scalable API service.
## 16. Observability

Observability is important for monitoring an agentic system, especially when the number of tools becomes large.

In a production implementation, an observability platform such as LangSmith or OpenTelemetry can be integrated to monitor:

- User requests
- Tool discovery and routing decisions
- Selected tools
- Tool execution latency
- API failures
- Retry attempts
- Agent state transitions
- Final responses

These traces can help developers identify incorrect tool selection, slow API calls, repeated failures, and other issues.

The current prototype does not require a separate observability platform, but the architecture allows observability to be added during production deployment.
## 17. Prototype Implementation

A Python prototype was implemented to demonstrate the Tool Registry and Tool Router.

The prototype stores tool metadata including:

- Tool name
- Description
- Category

The Tool Router calculates a relevance score between the user's request and each registered tool.

Only the top relevant tools are returned to the agent.

### Prototype Test

Input:

"Send an invoice for $50"

Output:

- create_invoice [invoice]
- send_invoice [invoice]
- get_invoice [invoice]

The prototype demonstrates that the agent does not need to receive the complete tool collection. Instead, the router retrieves a small set of relevant candidate tools.

This approach can be extended to a much larger tool registry containing hundreds or thousands of APIs.
## 18. Tool Execution

The prototype includes a Tool Executor that simulates the execution of selected tools.

After the Tool Router identifies relevant tools, the highest-ranked candidate is selected for execution.

### Example

User request:

"Send an invoice for $50"

Tool Router:

- create_invoice
- send_invoice
- get_invoice

Selected tool:

create_invoice

Execution result:

"Invoice created successfully for $50."

This demonstrates the complete flow from natural-language input to tool selection and execution.

In a production system, the simulated executor would be replaced by actual API calls.
## 19. Prototype Test Results

The prototype was tested using natural-language requests based on the assessment scenarios.

| User Request | Tool Selected | Result |
|---|---|---|
| Send an invoice for $100 | create_invoice → send_invoice | Completed successfully |
| What was my total sales volume last month? | get_sales_report | Completed successfully |
| Is there a dispute open from user_123? | get_dispute | Completed successfully |
| How do I use the invoice documentation? | RAG Pipeline | Documentation retrieved successfully |
| What tools are available for managing invoices? | System Search | Invoice tools identified successfully |
| Send an invoice for $100 with 106 tools registered | create_invoice → send_invoice | Correct tools selected and executed | Send an invoice for $100 with 506 tools registered | create_invoice → send_invoice | Completed successfully |
### Scalability Test

The prototype was tested with 506 registered tools, consisting of 6 functional PayPal-style tools and 500 simulated tools. A natural-language request to send an invoice for $100 was correctly routed to the relevant invoice workflow, `create_invoice → send_invoice`, without requiring all tools to be individually exposed to the execution step.

This demonstrates the prototype's ability to maintain relevant tool selection as the tool registry grows beyond 500 tools.

The tests demonstrate tool discovery, routing, multi-step execution, parameter extraction, state management, RAG-based documentation retrieval, system capability search, and scalability with a large tool registry.
