#!/bin/bash
# Script to delete inactive customers with no orders since 1 year ago

LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Run Django shell command to delete inactive customers
DELETED=$(python manage.py shell -c "
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=365)
qs = Customer.objects.filter(last_order_date__lt=cutoff)
count = qs.count()
qs.delete()
print(count)
")

# Log result
echo "$TIMESTAMP - Deleted $DELETED inactive customers" >> $LOG_FILE
