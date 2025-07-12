#!/usr/bin/env python3
"""
Order reminder script that queries GraphQL endpoint for recent orders
and logs reminders for processing.
"""

import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def main():
    """Main function to process order reminders"""
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)
    seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Setup GraphQL client
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # GraphQL query to get orders from the last 7 days
    query = gql("""
        query GetRecentOrders($orderDateGte: DateTime!) {
            filteredOrders(filter: { orderDateGte: $orderDateGte }) {
                id
                orderDate
                customer {
                    email
                }
            }
        }
    """)
    
    try:
        # Execute the query
        variables = {"orderDateGte": seven_days_ago_str}
        result = client.execute(query, variable_values=variables)
        
        # Get current timestamp for logging
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Process orders and log reminders
        orders = result.get('filteredOrders', [])
        
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            if orders:
                for order in orders:
                    order_id = order['id']
                    customer_email = order['customer']['email']
                    log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}\n"
                    log_file.write(log_entry)
            else:
                log_entry = f"[{timestamp}] No recent orders found for reminders\n"
                log_file.write(log_entry)
        
        print("Order reminders processed!")
        
    except Exception as e:
        # Log errors
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] ERROR: {str(e)}\n")
        print(f"Error processing order reminders: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()