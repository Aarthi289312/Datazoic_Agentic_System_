# Scalable Agentic System
# Datazoic Job Assessment


TOOLS = [
    {
        "name": "create_invoice",
        "description": "Creates a new invoice for a customer",
        "category": "invoice",
        "parameters": ["customer_id", "amount", "currency"],
        "endpoint": "/v1/invoices",
        "method": "POST",
        "keywords": ["create", "invoice", "bill"]
    },
    {
        "name": "send_invoice",
        "description": "Sends an invoice to a customer",
        "category": "invoice",
        "parameters": ["invoice_id", "recipient"],
        "endpoint": "/v1/invoices/send",
        "method": "POST",
        "keywords": ["send", "invoice", "email"]
    },
    {
        "name": "get_invoice",
        "description": "Retrieves invoice details",
        "category": "invoice",
        "parameters": ["invoice_id"],
        "endpoint": "/v1/invoices/{invoice_id}",
        "method": "GET",
        "keywords": ["get", "invoice", "details"]
    },
    {
        "name": "get_sales_report",
        "description": "Gets sales volume and sales reports",
        "category": "reports",
        "parameters": ["start_date", "end_date"],
        "endpoint": "/v1/reports/sales",
        "method": "GET",
        "keywords": ["sales", "report", "volume"]
    },
    {
        "name": "get_dispute",
        "description": "Checks whether a customer has an open dispute",
        "category": "disputes",
        "parameters": ["customer_id"],
        "endpoint": "/v1/disputes",
        "method": "GET",
        "keywords": ["dispute", "customer", "open"]
    },
    {
        "name": "refund_payment",
        "description": "Processes a payment refund",
        "category": "payments",
        "parameters": ["payment_id", "amount"],
        "endpoint": "/v1/payments/refund",
        "method": "POST",
        "keywords": ["refund", "payment", "money"]
    }
]
# Simulate a large tool registry
for i in range(1, 501):
    TOOLS.append({
        "name": f"tool_{i}",
        "description": f"Generic tool number {i}",
        "category": "general",
        "parameters": ["input"],
        "endpoint": f"/v1/tools/{i}",
        "method": "POST",
        "keywords": [f"tool{i}", "general"]
    })


# -----------------------------
# STATE MANAGEMENT
# -----------------------------

class AgentState:

    def __init__(self, user_request):
        self.user_request = user_request
        self.selected_tools = []
        self.selected_tool = None
        self.tool_result = None
        self.status = "STARTED"
        self.error = None

    def show_state(self):
        print("\nAgent State:")
        print(f"Request: {self.user_request}")
        print(f"Status: {self.status}")

        if self.selected_tool:
            print(f"Selected Tool: {self.selected_tool}")

        if self.tool_result:
            print(f"Result: {self.tool_result}")

        if self.error:
            print(f"Error: {self.error}")


# -----------------------------
# TOOL ROUTER
# -----------------------------


def calculate_relevance(user_request, tool):

    request_words = set(
        user_request.lower().split()
    )

    tool_text = (
        tool["name"]
        + " "
        + tool["description"]
        + " "
        + tool["category"]
        + " "
        + " ".join(tool["keywords"])
    ).lower()

    tool_words = set(tool_text.split())

    return len(
        request_words.intersection(tool_words)
    )


def route_tools(user_request, top_k=3):

    scored_tools = []
    print(f"Searching across {len(TOOLS)} registered tools...")

    for tool in TOOLS:

        score = calculate_relevance(
            user_request,
            tool
        )

        if score > 0:
            scored_tools.append(
                (score, tool)
            )

    scored_tools.sort(
        key=lambda item: item[0],
        reverse=True
    )
    print(f"Relevant candidate tools found: {len(scored_tools)}")

    return [
        tool
        for score, tool
        in scored_tools[:top_k]
    ]


# -----------------------------
# RAG PIPELINE
# -----------------------------

DOCUMENTATION = {

    "invoice":
        "Invoice APIs require customer information, "
        "amount, currency and invoice details.",

    "sales":
        "Sales reports provide sales volume, "
        "transaction information and reporting periods.",

    "dispute":
        "Dispute APIs can be used to check "
        "open and closed customer disputes.",

    "payment":
        "Payment APIs support payment processing "
        "and refunds."
}


def rag_search(query):

    query = query.lower()

    results = []

    for topic, documentation in DOCUMENTATION.items():

        if topic in query:

            results.append(
                f"{topic.upper()} DOCUMENTATION: "
                f"{documentation}"
            )

    if not results:
        return "No relevant documentation found."

    return "\n".join(results)


# -----------------------------
# SYSTEM SEARCH
# -----------------------------

def system_search(query):

    query = query.lower()

    if "invoice" in query:

        return (
            "Available invoice tools: "
            "create_invoice, send_invoice, get_invoice"
        )

    if "sales" in query or "report" in query:

        return (
            "Available reporting tool: "
            "get_sales_report"
        )

    if "dispute" in query:

        return (
            "Available dispute tool: "
            "get_dispute"
        )

    if "payment" in query or "refund" in query:

        return (
            "Available payment tool: "
            "refund_payment"
        )

    return "No matching system capability found."


# -----------------------------
# TOOL EXECUTOR
# -----------------------------
def validate_parameters(tool_name, user_request):

    request = user_request.lower()

    if tool_name == "create_invoice":
        return "invoice" in request and "$" in request

    if tool_name == "send_invoice":
        return "invoice" in request

    if tool_name == "get_invoice":
        return "invoice" in request

    if tool_name == "get_sales_report":
        return "sales" in request or "report" in request

    if tool_name == "get_dispute":
        return "dispute" in request

    if tool_name == "refund_payment":
        return "payment" in request or "refund" in request

    return True


# -----------------------------
# MULTI-STEP TOOL EXECUTION
# -----------------------------

def execute_tool_sequence(state):

    request = state.user_request.lower()

    if "send" in request and "invoice" in request:

        steps = [
            "create_invoice",
            "send_invoice"
        ]

        results = []

        for tool_name in steps:

            print(f"\nExecuting: {tool_name}")

            max_retries = 2
            result = None

            for attempt in range(max_retries + 1):

                if not validate_parameters(
                    tool_name,
                    state.user_request
                ):
                    state.status = "FAILED"
                    state.error = (
                        f"Missing or invalid parameters "
                        f"for {tool_name}."
                    )
                    return results

                result = execute_tool(
                    tool_name,
                    state.user_request
                )

                if result is not None:
                    break

                print(f"Attempt {attempt + 1} failed.")

                if attempt < max_retries:
                    print("Retrying...")

            if result is None:
                state.status = "FAILED"
                state.error = (
                    f"Execution failed for {tool_name} "
                    f"after {max_retries} retries."
                )
                return results

            results.append(
                f"{tool_name}: {result}"
            )

        state.selected_tool = "create_invoice → send_invoice"
        state.tool_result = results
        state.status = "COMPLETED"

        return results

    state.selected_tool = (
        state.selected_tools[0]["name"]
    )

    result = execute_tool(
        state.selected_tool,
        state.user_request
    )

    if result is None:
        state.status = "FAILED"
        state.error = "Tool execution failed."
    else:
        state.tool_result = result
        state.status = "COMPLETED"

    return result


def execute_tool(tool_name, user_request):

    if tool_name == "create_invoice":
     import re

     match = re.search(r"\$(\d+(?:\.\d+)?)", user_request)

     if match:
        amount = match.group(1)
     else:
        amount = "0"

     return f"Invoice created successfully for ${amount}."
    elif tool_name == "send_invoice":

        return "Invoice sent successfully to the customer."

    elif tool_name == "get_invoice":

        return "Invoice details retrieved successfully."

    elif tool_name == "get_sales_report":

        return "Total sales volume for last month: $25,430."

    elif tool_name == "get_dispute":

        return "Dispute found for user_123."

    elif tool_name == "refund_payment":

        return "Payment refund processed successfully."

    return None
    


# -----------------------------
# MAIN AGENT
# -----------------------------

def main():

    print("===================================")
    print("     Scalable Agentic System")
    print("===================================")
    print(f"Total tools registered: {len(TOOLS)}")

    user_request = input("\nUser: ")

    state = AgentState(user_request)

    # System Search
    if "what tools are available" in user_request.lower():

        state.status = "SYSTEM_SEARCH"

        result = system_search(user_request)

        print("\nSystem Search:")
        print(result)

        state.tool_result = result
        state.status = "COMPLETED"
        state.show_state()

        return

    # RAG Search
    if "documentation" in user_request.lower():

        state.status = "RAG_SEARCH"

        result = rag_search(user_request)

        print("\nRAG Pipeline Result:")
        print(result)

        state.tool_result = result
        state.status = "COMPLETED"

        state.show_state()

        return

    # Tool Routing
    state.status = "ROUTING"

    state.selected_tools = route_tools(
        user_request
    )

    print("\nTool Router Result:")

    if not state.selected_tools:

        state.status = "FAILED"
        state.error = "No relevant tools found."

        print(state.error)

        state.show_state()

        return

    for tool in state.selected_tools:

        print(
            f"- {tool['name']} "
            f"[{tool['category']}]"
        )

    # Select tool
    state.selected_tool = (
        state.selected_tools[0]["name"]
    )

    print("\nSelected Tool:")
    print(state.selected_tool)

    # Execute tool sequence
    state.status = "EXECUTING"

    result = execute_tool_sequence(state)

    print("\nTool Execution Result:")
    print(result)

    state.show_state()

if __name__ == "__main__":
    main()