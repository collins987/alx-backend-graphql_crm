from datetime import datetime
import requests
from celery import shared_task

@shared_task
def generate_crm_report():
    """
    Celery task to fetch CRM data from GraphQL and log a weekly report.
    """
    LOG_FILE = "/tmp/crm_report_log.txt"
    TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = """
    query {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query},
            timeout=10
        )
        data = response.json().get("data", {})
        customers = data.get("totalCustomers", 0)
        orders = data.get("totalOrders", 0)
        revenue = data.get("totalRevenue", 0)

        with open(LOG_FILE, "a") as f:
            f.write(f"{TIMESTAMP} - Report: {customers} customers, {orders} orders, {revenue} revenue\n")

    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{TIMESTAMP} - Error generating report: {e}\n")
