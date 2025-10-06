import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    """
    Fetch weekly CRM stats from the GraphQL API and log results.
    """
    LOG_FILE = "/tmp/crm_report_log.txt"
    TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # GraphQL transport
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=False)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    query {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """)

    try:
        result = client.execute(query)
        customers = result.get("totalCustomers", 0)
        orders = result.get("totalOrders", 0)
        revenue = result.get("totalRevenue", 0)

        with open(LOG_FILE, "a") as f:
            f.write(f"{TIMESTAMP} - Report: {customers} customers, {orders} orders, {revenue} revenue\n")

    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{TIMESTAMP} - Error generating report: {e}\n")
