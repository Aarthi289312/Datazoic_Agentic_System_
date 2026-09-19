# Datazoic Agentic System

## Overview

This project implements a scalable agentic system designed to work with a large number of tools and APIs.

The system addresses the problem of tool-selection degradation when an LLM has access to hundreds or thousands of tools.

Instead of exposing the complete tool collection directly to the agent, the system uses a Tool Registry and Tool Router to identify a small set of relevant candidate tools.

## Architecture

```text
User
  ↓
Agent Orchestrator
  ↓
Tool Router
  ↓
Tool Registry
  ↓
Relevant Candidate Tools
  ↓
Tool Selection
  ↓
Parameter Validation
  ↓
Tool Executor
  ↓
API / Tool
  ↓
Result
  ↓
Agent State
  ↓
Final Response
```

The system also provides separate RAG and System Search tools.

## Key Features

* Scalable tool registry
* Tool discovery and routing
* 500+ registered tools
* Multi-step tool execution
* PayPal Sandbox API integration
* Invoice creation and sending
* RAG Pipeline Tool
* System Search Tool
* Agent state management
* Parameter validation
* Error handling and retry logic

## Tool Routing

The system does not require the agent to directly select from every registered tool.

For a large tool registry, the Tool Router first searches for relevant tools and returns a small candidate set.

For example:

```text
506 registered tools
        ↓
Tool Router
        ↓
Relevant invoice tools
        ↓
create_invoice
send_invoice
get_invoice
        ↓
Execution
```

This reduces unnecessary tool-selection context and allows the architecture to scale to hundreds or thousands of tools.

## PayPal Integration

The project includes a PayPal Sandbox integration for invoice operations.

The invoice workflow is:

```text
User Request
     ↓
create_invoice
     ↓
PayPal Sandbox
     ↓
Invoice ID
     ↓
send_invoice
     ↓
PayPal Sandbox
     ↓
Completed
```

Example request:

```text
Create and send an invoice for $10 to customer@example.com
```

Example successful result:

```text
Total tools registered: 506

Executing: create_invoice
PayPal Invoice ID: INV2-QC8E-WC9V-JCCY-2L6T

Executing: send_invoice

Tool Execution Result:
create_invoice: Invoice created successfully.
send_invoice: Invoice ... sent successfully.

Agent State:
Status: COMPLETED
Selected Tool: create_invoice → send_invoice
```

## RAG Pipeline Tool

The RAG tool is provided as a separate system capability.

It can retrieve relevant information from documentation and knowledge sources to help the agent answer questions or understand how a tool should be used.

## System Search Tool

The System Search tool allows the agent to query system capabilities and execution information.

Example:

```text
What tools are available for managing invoices?
```

The system can search the available tool registry and return relevant invoice-related capabilities.

## Scalability

The prototype demonstrates scalability using 506 registered tools.

The registry contains functional PayPal-style tools together with simulated tools used to demonstrate a large tool ecosystem.

The architecture can be extended from:

```text
100 tools
   ↓
500 tools
   ↓
1000+ tools
```

The Tool Router continues to retrieve only relevant candidate tools instead of exposing the complete tool collection to the agent.

## Error Handling

The system handles:

* Missing parameters
* Invalid parameters
* API errors
* Authentication errors
* Tool execution failures
* Temporary failures

Retries are limited to avoid infinite execution loops.

## Technology

### Prototype

* Python
* Custom Tool Registry
* Custom Tool Router
* PayPal Sandbox API
* Rule-based parameter extraction
* RAG tool
* System Search tool
* Custom agent state management

### Production Extensions

The architecture can be extended with:

* LangGraph for workflow orchestration
* Vector databases for semantic tool discovery
* FastAPI for API deployment
* Pydantic for structured validation
* LangSmith or OpenTelemetry for observability

## Framework Choice

The prototype uses a custom Python architecture so that the core concepts of tool discovery, routing, state management, execution, and error handling remain explicit and easy to evaluate.

For a production-scale implementation, frameworks such as LangGraph can be introduced for workflow orchestration.

The trade-off is that a custom implementation provides greater control and transparency but requires more functionality to be implemented manually.

## Project Structure

```text
Datazoic_Agentic_System/
│
├── agent_system/
│   ├── main.py
│   └── main_backup.py
│
├── Design_Document.md
├── README.md
├── .env
└── .gitignore
```

The `.env` file contains local credentials and must not be committed to GitHub.

## Running the Project

Install the required Python packages:

```bash
py -m pip install requests python-dotenv
```

Configure the PayPal Sandbox credentials in `.env`.

Then run:

```bash
py agent_system/main.py
```

Example input:

```text
Create and send an invoice for $10 to customer@example.com
```

A successful execution should end with:

```text
Status: COMPLETED
```

## Documentation

Detailed architecture, design decisions, scalability considerations, error handling, testing, and framework trade-offs are documented in:

`Design_Document.md`
