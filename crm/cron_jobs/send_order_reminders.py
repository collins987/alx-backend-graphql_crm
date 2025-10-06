import sys
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/order_reminders_log.txt"
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=False)
client = Client(transport=transport, fetch_schema_from_transport=True)

query = gql("""
query GetRecentOrders {
  orders(last7days: true) {
    id
    customer {
      email
    }
  }
}
""")

try:
    result = client.execute(query)
    with open(LOG_FILE, "a") as f:
        for order in result.get("orders", []):
            f.write(f"{TIMESTAMP} - Reminder for Order {order['id']} to {order['customer']['email']}\n")
    print("Order reminders processed!")
except Exception as e:
    sys.stderr.write(f"Error: {e}\n")
