import sqlite3
import sys
from datetime import datetime, timedelta

def connect_db():
    """Connect to existing SQLite database"""
    try:
        conn = sqlite3.connect('ecommerce.db')
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def get_date_range(period):
    """Get start and end dates based on period"""
    end_date = datetime.now()
    
    if period == 'daily':
        start_date = end_date - timedelta(days=1)
    elif period == 'weekly':
        start_date = end_date - timedelta(days=7)
    elif period == 'monthly':
        start_date = end_date - timedelta(days=30)
    else:
        print("Invalid period. Use 'daily', 'weekly', or 'monthly'")
        sys.exit(1)
    
    return start_date, end_date

def generate_summary_report(conn, start_date, end_date, period):
    """Generate a summary report for the given date range"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print(f"SUMMARY REPORT: {period.upper()}")
    print(f"Period: {start_date.date()} to {end_date.date()}")
    print("="*80 + "\n")
    
    # Total orders, revenue, unique customers
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT o.order_id) as total_orders,
            COUNT(DISTINCT o.customer_id) as unique_customers,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as total_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE oi.quantity > 0 
            AND DATE(o.order_date) >= ? 
            AND DATE(o.order_date) <= ?
    """, (start_date.date(), end_date.date()))
    
    total_orders, unique_customers, total_revenue = cursor.fetchone()
    print(f"Total Orders: {total_orders}")
    print(f"Unique Customers: {unique_customers}")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    
    # Top 3 products
    print(f"\nTop 3 Products:")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            p.product_id,
            p.product_name,
            COUNT(DISTINCT oi.item_id) as items_sold,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as product_revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE oi.quantity > 0 
            AND DATE(o.order_date) >= ? 
            AND DATE(o.order_date) <= ?
        GROUP BY p.product_id
        ORDER BY product_revenue DESC
        LIMIT 3
    """, (start_date.date(), end_date.date()))
    
    for idx, (product_id, product_name, items_sold, revenue) in enumerate(cursor.fetchall(), 1):
        print(f"{idx}. {product_name} ({product_id}): {items_sold} items, ${revenue:,.2f}")
    
    # Previous period comparison
    print(f"\nComparison with Previous {period.title()}:")
    print("-" * 80)
    
    if period == 'daily':
        prev_start = start_date - timedelta(days=1)
        prev_end = end_date - timedelta(days=1)
    elif period == 'weekly':
        prev_start = start_date - timedelta(days=7)
        prev_end = end_date - timedelta(days=7)
    else:  # monthly
        prev_start = start_date - timedelta(days=30)
        prev_end = end_date - timedelta(days=30)
    
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT o.order_id) as total_orders,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as total_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE oi.quantity > 0 
            AND DATE(o.order_date) >= ? 
            AND DATE(o.order_date) <= ?
    """, (prev_start.date(), prev_end.date()))
    
    prev_orders, prev_revenue = cursor.fetchone()
    
    if prev_revenue and prev_revenue > 0:
        revenue_change = ((total_revenue - prev_revenue) / prev_revenue) * 100
        order_change = ((total_orders - prev_orders) / prev_orders) * 100 if prev_orders > 0 else 0
        
        print(f"Previous {period.title()} Revenue: ${prev_revenue:,.2f}")
        print(f"Current Revenue: ${total_revenue:,.2f}")
        print(f"Revenue Change: {revenue_change:+.2f}%")
        print(f"Previous {period.title()} Orders: {prev_orders}")
        print(f"Current Orders: {total_orders}")
        print(f"Order Change: {order_change:+.2f}%")
    else:
        print("No data available for previous period")
    
    print("\n" + "="*80 + "\n")

def main():
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python report_generator.py <period>")
        print("  period: daily, weekly, or monthly")
        print("\nExample: python report_generator.py monthly")
        sys.exit(1)
    
    period = sys.argv[1].lower()
    
    if period not in ['daily', 'weekly', 'monthly']:
        print("Invalid period. Use 'daily', 'weekly', or 'monthly'")
        sys.exit(1)
    
    # Connect to database
    conn = connect_db()
    
    # Get date range
    start_date, end_date = get_date_range(period)
    
    # Generate report
    generate_summary_report(conn, start_date, end_date, period)
    
    conn.close()

if __name__ == "__main__":
    main()
