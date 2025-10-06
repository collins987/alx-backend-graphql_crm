import datetime
import requests

def log_crm_heartbeat():
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Optional: ping GraphQL hello field
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        status = "alive" if response.ok else "unreachable"
    except Exception:
        status = "unreachable"

    with open(log_file, "a") as f:
        f.write(f"{timestamp} CRM is {status}\n")

def update_low_stock():
    import datetime
    from gql import gql, Client
    from gql.transport.requests import RequestsHTTPTransport

    log_file = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=False)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    mutation = gql("""
    mutation {
      updateLowStockProducts {
        success
        updatedProducts
      }
    }
    """)

    try:
        result = client.execute(mutation)
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - {result['updateLowStockProducts']}\n")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Error: {e}\n")
