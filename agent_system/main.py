
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv(r"C:\Users\hp\Desktop\Datazoic_Agentic_System\.env")

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
# -----------------------------
# PAYPAL API
# -----------------------------

def get_paypal_access_token():

    client_id = os.getenv("PAYPAL_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
    base_url = os.getenv("PAYPAL_BASE_URL")

    response = requests.post(
        f"{base_url}/v1/oauth2/token",
        auth=(client_id, client_secret),
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US"
        },
        data={
            "grant_type": "client_credentials"
        }
    )

    response.raise_for_status()

    token_data = response.json()


    return token_data["access_token"]

def create_paypal_invoice(amount, currency="USD", recipient_email="customer@example.com"):

    access_token = get_paypal_access_token()
    base_url = os.getenv("PAYPAL_BASE_URL")

    invoice_data = {
        "detail": {
            "currency_code": currency,
            "note": "Invoice created by Datazoic Agentic System",
            "payment_term": {
                "term_type": "DUE_ON_RECEIPT"
            }
        },
        "invoicer": {
            "name": {
                "given_name": "Datazoic",
                "surname": "System"
            },
            "email_address": os.getenv("PAYPAL_INVOICER_EMAIL")
        },
        "primary_recipients": [
            {
                "billing_info": {
                    "email_address": recipient_email
                }
            }
        ],
        "items": [
            {
                "name": "Agentic System Service",
                "quantity": "1",
                "unit_amount": {
                    "currency_code": currency,
                    "value": amount
                }
            }
        ]
    }

    response = requests.post(
        f"{base_url}/v2/invoicing/invoices",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        },
        json=invoice_data
)
    if not response.ok:
        print("PayPal Error Status:", response.status_code)
        print("PayPal Error Response:", response.text)


    response.raise_for_status()
    return response.json()
def send_paypal_invoice(invoice_id):

    access_token = get_paypal_access_token()
    base_url = os.getenv("PAYPAL_BASE_URL")

    response = requests.post(
        f"{base_url}/v2/invoicing/invoices/{invoice_id}/send",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        },
        json={
            "send_to_recipient": True,
            "send_to_invoicer": False
        }
    )

    response.raise_for_status()

    return True

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

        print("\nExecuting: create_invoice")

        if not validate_parameters(
            "create_invoice",
            state.user_request
        ):
            state.status = "FAILED"
            state.error = "Missing invoice amount."
            return None

        # Step 1: Create invoice using PayPal
        invoice = execute_tool(
            "create_invoice",
            state.user_request
        )

        if invoice is None:
            state.status = "FAILED"
            state.error = "PayPal invoice creation failed."
            return None

        invoice_id = invoice.get("id")

        if not invoice_id:
            invoice_url = invoice.get("href", "")

            if "/invoices/" in invoice_url:
               invoice_id = invoice_url.split("/invoices/")[-1]

        if not invoice_id:
            state.status = "FAILED"
            state.error = "PayPal did not return an invoice ID."
            return None

        print(f"PayPal Invoice ID: {invoice_id}")

        # Step 2: Send invoice using PayPal
        print("\nExecuting: send_invoice")

        try:
            send_paypal_invoice(invoice_id)

            send_result = (
                f"Invoice {invoice_id} sent successfully."
            )

        except requests.exceptions.RequestException as error:

            state.status = "FAILED"
            state.error = (
                f"PayPal invoice sending failed: {error}"
            )
            return None

        state.selected_tool = (
            "create_invoice → send_invoice"
        )

        state.tool_result = [
            f"create_invoice: Invoice created successfully. "
            f"Invoice ID: {invoice_id}",
            f"send_invoice: {send_result}"
        ]

        state.status = "COMPLETED"

        return state.tool_result

    # Normal single-tool execution
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

        match = re.search(r"\$(\d+(?:\.\d+)?)", user_request)

        if not match:
            return None

        amount = match.group(1)

        email_match = re.search(
            r"[\w\.-]+@[\w\.-]+\.\w+",
            user_request
        )

        if email_match:
            recipient_email = email_match.group()
        else:
            recipient_email = "customer@example.com"

        invoice = create_paypal_invoice(
            amount=amount,
            recipient_email=recipient_email
        )

        return invoice

    elif tool_name == "send_invoice":

        return None

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