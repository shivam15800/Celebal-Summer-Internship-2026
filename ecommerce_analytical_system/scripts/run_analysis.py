import sqlite3
import csv
from pathlib import Path

def create_database():
    """Create SQLite database and load cleaned CSV files"""
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    print("Creating tables...")
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT,
            region_code TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            subcategory TEXT,
            cost_price REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            item_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER,
            unit_price REAL,
            discount_percent REAL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            customer_name TEXT,
            email TEXT,
            registration_date TEXT,
            customer_type TEXT
        )
    ''')
    
    # Load data from cleaned CSVs
    print("Loading orders...")
    with open('orders_cleaned.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT INTO orders VALUES (?, ?, ?, ?, ?)
            ''', (row['order_id'], row['customer_id'], row['order_date'], 
                  row['status'], row['region_code']))
    
    print("Loading products...")
    with open('products_cleaned.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT INTO products VALUES (?, ?, ?, ?, ?)
            ''', (row['product_id'], row['product_name'], row['category'], 
                  row['subcategory'], row['cost_price']))
    
    print("Loading order items...")
    with open('order_items_cleaned.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['item_id'], row['order_id'], row['product_id'], 
                  row['quantity'], row['unit_price'], row['discount_percent']))
    
    print("Loading customers...")
    with open('customers.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cursor.execute('''
                    INSERT INTO customers VALUES (?, ?, ?, ?, ?)
                ''', (row['customer_id'], row['customer_name'], row['email'], 
                      row['registration_date'], row['customer_type']))
            except sqlite3.IntegrityError:
                pass  # Skip duplicate customer
    
    conn.commit()
    print("✓ Database loaded successfully\n")
    return conn

def execute_query(cursor, query_num, query):
    """Execute a single query and return results"""
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return True, column_names, results
    except Exception as e:
        return False, None, str(e)

def save_results(query_num, column_names, results):
    """Save query results to a text file"""
    filename = f"query_{query_num:02d}_results.txt"
    with open(filename, 'w') as f:
        # Write header
        f.write(f"QUERY {query_num} RESULTS\n")
        f.write("="*80 + "\n\n")
        
        # Write column names
        if column_names:
            f.write(" | ".join(column_names) + "\n")
            f.write("-"*80 + "\n")
            
            # Write data
            for row in results:
                f.write(" | ".join(str(cell) if cell is not None else "NULL" for cell in row) + "\n")
        
        f.write(f"\n[Total rows: {len(results)}]\n")
    
    return filename

def main():
    # Create and load database
    conn = create_database()
    cursor = conn.cursor()
    
    # Define all queries
    queries = {
        1: """
            SELECT 
                p.category,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as total_revenue,
                COUNT(DISTINCT oi.item_id) as total_items,
                COUNT(DISTINCT oi.order_id) as total_orders
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.quantity > 0
            GROUP BY p.category
            ORDER BY total_revenue DESC
        """,
        2: """
            SELECT 
                c.customer_id,
                c.customer_name,
                c.customer_type,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as total_spent,
                COUNT(DISTINCT oi.order_id) as order_count
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.quantity > 0
            GROUP BY c.customer_id
            ORDER BY total_spent DESC
            LIMIT 10
        """,
        3: """
            SELECT 
                strftime('%Y-%m', o.order_date) as month,
                COUNT(DISTINCT o.order_id) as order_count,
                COUNT(DISTINCT o.customer_id) as unique_customers,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as monthly_revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.quantity > 0
            GROUP BY strftime('%Y-%m', o.order_date)
            ORDER BY month DESC
            LIMIT 12
        """,
        4: """
            SELECT 
                c.customer_id,
                c.customer_name,
                COUNT(DISTINCT o.order_id) as order_count,
                COUNT(DISTINCT CASE WHEN o.status = 'DELIVERED' THEN o.order_id END) as delivered_orders
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id
            HAVING delivered_orders = 0 AND order_count > 0
            ORDER BY order_count DESC
        """,
        5: """
            SELECT 
                p.product_id,
                p.product_name,
                p.category,
                SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) as purchases,
                SUM(CASE WHEN oi.quantity < 0 THEN ABS(oi.quantity) ELSE 0 END) as returns
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_id
            HAVING returns > purchases
            ORDER BY returns DESC
        """,
        6: """
            SELECT 
                p.category,
                COUNT(DISTINCT CASE WHEN oi.quantity < 0 THEN oi.item_id END) as returned_items,
                COUNT(DISTINCT oi.item_id) as total_items,
                ROUND(100.0 * COUNT(DISTINCT CASE WHEN oi.quantity < 0 THEN oi.item_id END) / 
                      COUNT(DISTINCT oi.item_id), 2) as return_rate_percent
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.category
            ORDER BY return_rate_percent DESC
        """,
        7: """
            SELECT 
                o.region_code,
                DATE(o.order_date) as order_date,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as daily_revenue,
                ROUND(SUM(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0))) 
                    OVER (PARTITION BY o.region_code ORDER BY DATE(o.order_date)), 2) as running_total
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.quantity > 0
            GROUP BY o.region_code, DATE(o.order_date)
            ORDER BY o.region_code, order_date
            LIMIT 50
        """,
        8: """
            SELECT 
                p.category,
                p.product_id,
                p.product_name,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as total_revenue,
                DENSE_RANK() OVER (PARTITION BY p.category ORDER BY 
                    SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) DESC) as rank_in_category
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            WHERE oi.quantity > 0
            GROUP BY p.product_id
            ORDER BY p.category, rank_in_category
            LIMIT 30
        """,
        9: """
            SELECT 
                customer_id,
                order_id,
                order_date,
                prev_order_date,
                CAST((julianday(order_date) - julianday(prev_order_date)) AS INTEGER) as days_gap
            FROM (
                SELECT 
                    o.customer_id,
                    o.order_id,
                    DATE(o.order_date) as order_date,
                    LAG(DATE(o.order_date)) OVER (PARTITION BY o.customer_id ORDER BY o.order_date) as prev_order_date
                FROM orders o
            )
            WHERE prev_order_date IS NOT NULL
            ORDER BY customer_id, order_date
            LIMIT 50
        """,
        10: """
            WITH monthly_revenue AS (
                SELECT 
                    o.customer_id,
                    strftime('%Y-%m', o.order_date) as month,
                    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as revenue
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                WHERE oi.quantity > 0
                GROUP BY o.customer_id, strftime('%Y-%m', o.order_date)
            ),
            customer_segments AS (
                SELECT 
                    customer_id,
                    month,
                    revenue,
                    CASE 
                        WHEN revenue > 10000 THEN 'High'
                        WHEN revenue >= 5000 THEN 'Medium'
                        ELSE 'Low'
                    END as segment
                FROM monthly_revenue
            )
            SELECT 
                month,
                segment,
                COUNT(DISTINCT customer_id) as customer_count,
                ROUND(SUM(revenue), 2) as total_revenue
            FROM customer_segments
            GROUP BY month, segment
            ORDER BY month DESC, customer_count DESC
        """,
        11: """
            SELECT 
                c.customer_id,
                c.customer_name,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as total_value,
                NTILE(4) OVER (ORDER BY SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) DESC) as quartile,
                CASE 
                    WHEN NTILE(4) OVER (ORDER BY SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) DESC) = 1 THEN 'Platinum'
                    WHEN NTILE(4) OVER (ORDER BY SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) DESC) = 2 THEN 'Gold'
                    WHEN NTILE(4) OVER (ORDER BY SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) DESC) = 3 THEN 'Silver'
                    ELSE 'Bronze'
                END as quartile_label
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.quantity > 0
            GROUP BY c.customer_id
            ORDER BY total_value DESC
        """,
        12: """
            SELECT 
                strftime('%Y', o.order_date) as year,
                strftime('%m', o.order_date) as month,
                ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as revenue,
                ROUND(LAG(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0))) 
                    OVER (PARTITION BY strftime('%m', o.order_date) ORDER BY strftime('%Y', o.order_date)), 2) as prev_year_revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.quantity > 0
            GROUP BY strftime('%Y', o.order_date), strftime('%m', o.order_date)
            ORDER BY year DESC, month
        """,
        13: """
            WITH customer_categories AS (
                SELECT 
                    o.customer_id,
                    FIRST_VALUE(p.category) OVER (PARTITION BY o.customer_id ORDER BY DATE(o.order_date)) as first_category,
                    LAST_VALUE(p.category) OVER (PARTITION BY o.customer_id ORDER BY DATE(o.order_date) 
                        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_category
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.quantity > 0
            )
            SELECT DISTINCT
                customer_id,
                first_category,
                last_category,
                CASE WHEN first_category != last_category THEN 'Yes' ELSE 'No' END as category_shift
            FROM customer_categories
            ORDER BY customer_id
        """,
        14: """
            WITH customer_revenue AS (
                SELECT 
                    o.customer_id,
                    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) as revenue
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                WHERE oi.quantity > 0
                GROUP BY o.customer_id
            )
            SELECT 
                customer_id,
                revenue,
                ROUND(SUM(revenue) OVER (ORDER BY revenue DESC), 2) as cumulative_revenue,
                ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC) / 
                    SUM(revenue) OVER (), 2) as cumulative_percent
            FROM customer_revenue
            ORDER BY revenue DESC
            LIMIT 30
        """,
        15: """
            WITH cohort_data AS (
                SELECT 
                    c.customer_id,
                    strftime('%Y-%m', c.registration_date) as cohort_month,
                    strftime('%Y-%m', o.order_date) as order_month,
                    CAST((julianday(strftime('%Y-%m-01', o.order_date)) - 
                         julianday(strftime('%Y-%m-01', c.registration_date))) / 30.0 AS INTEGER) as months_since_registration
                FROM customers c
                LEFT JOIN orders o ON c.customer_id = o.customer_id
            )
            SELECT 
                cohort_month,
                COUNT(DISTINCT CASE WHEN months_since_registration = 0 THEN customer_id END) as month_0,
                COUNT(DISTINCT CASE WHEN months_since_registration >= 1 AND months_since_registration < 2 THEN customer_id END) as month_1,
                COUNT(DISTINCT CASE WHEN months_since_registration >= 2 AND months_since_registration < 3 THEN customer_id END) as month_2,
                COUNT(DISTINCT CASE WHEN months_since_registration >= 3 AND months_since_registration < 4 THEN customer_id END) as month_3
            FROM cohort_data
            GROUP BY cohort_month
            ORDER BY cohort_month DESC
        """,
        16: """
            SELECT 
                oi1.product_id as product_a,
                p1.product_name as product_a_name,
                oi2.product_id as product_b,
                p2.product_name as product_b_name,
                COUNT(DISTINCT oi1.order_id) as times_bought_together
            FROM order_items oi1
            JOIN order_items oi2 ON oi1.order_id = oi2.order_id
                AND oi1.product_id < oi2.product_id
            JOIN products p1 ON oi1.product_id = p1.product_id
            JOIN products p2 ON oi2.product_id = p2.product_id
            GROUP BY oi1.product_id, oi2.product_id
            HAVING COUNT(DISTINCT oi1.order_id) >= 2
            ORDER BY times_bought_together DESC
            LIMIT 20
        """
    }
    
    print("="*80)
    print("EXECUTING ALL 16 QUERIES")
    print("="*80 + "\n")
    
    # Execute each query
    for query_num, query in queries.items():
        print(f"Query {query_num}...", end=" ")
        success, columns, results = execute_query(cursor, query_num, query)
        
        if success:
            filename = save_results(query_num, columns, results)
            print(f"✓ {len(results)} rows -> {filename}")
        else:
            print(f"✗ ERROR: {results}")
    
    print("\n" + "="*80)
    print("✓ All queries executed. Results saved to query_XX_results.txt files")
    print("="*80)
    
    conn.close()

if __name__ == "__main__":
    main()
