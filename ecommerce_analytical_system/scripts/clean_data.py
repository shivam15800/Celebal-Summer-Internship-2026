import csv
import re
from datetime import datetime

class DataCleaner:
    def __init__(self):
        self.issues_report = {
            'null_customer_ids': [],
            'invalid_emails': [],
            'date_format_errors': [],
            'referential_integrity_errors': [],
            'product_name_issues': []
        }
    
    def clean_orders(self):
        """
        Clean orders.csv:
        - Fix date formats (handle DD-MM-YYYY -> YYYY-MM-DD)
        - Remove rows with NULL customer_ids
        - Validate data types
        """
        print("Cleaning orders...")
        cleaned_orders = []
        
        with open('orders.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                order_id = row['order_id'].strip()
                customer_id = row['customer_id'].strip()
                order_date = row['order_date'].strip()
                status = row['status'].strip()
                region_code = row['region_code'].strip()
                
                # Skip rows with NULL customer_id
                if not customer_id:
                    self.issues_report['null_customer_ids'].append(order_id)
                    continue
                
                # Fix date format
                try:
                    # Try parsing as YYYY-MM-DD HH:MM:SS (correct format)
                    parsed_date = datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        # Try parsing as DD-MM-YYYY HH:MM:SS (wrong format)
                        parsed_date = datetime.strptime(order_date, "%d-%m-%Y %H:%M:%S")
                        self.issues_report['date_format_errors'].append({
                            'order_id': order_id,
                            'original': order_date,
                            'corrected': parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                        })
                    except ValueError:
                        # Skip invalid dates entirely
                        self.issues_report['date_format_errors'].append({
                            'order_id': order_id,
                            'original': order_date,
                            'status': 'SKIPPED - unparseable'
                        })
                        continue
                
                # Standardize date format
                order_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                
                # Validate status
                valid_statuses = ['PLACED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED']
                if status not in valid_statuses:
                    status = 'PLACED'  # Default to PLACED if invalid
                
                cleaned_orders.append({
                    'order_id': order_id,
                    'customer_id': customer_id,
                    'order_date': order_date,
                    'status': status,
                    'region_code': region_code
                })
        
        # Write cleaned orders
        with open('orders_cleaned.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['order_id', 'customer_id', 'order_date', 'status', 'region_code'])
            writer.writeheader()
            writer.writerows(cleaned_orders)
        
        print(f"✓ Cleaned {len(cleaned_orders)} orders (removed {len(self.issues_report['null_customer_ids'])} with NULL customer_id)")
        return cleaned_orders
    
    def clean_products(self):
        """
        Clean products.csv:
        - Normalize product names (trim spaces, title case)
        - Fix mixed case and extra spaces
        """
        print("Cleaning products...")
        cleaned_products = []
        
        with open('products.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                product_id = row['product_id'].strip()
                product_name = row['product_name'].strip()
                category = row['category'].strip()
                subcategory = row['subcategory'].strip()
                cost_price = row['cost_price'].strip()
                
                # Normalize product name
                original_name = product_name
                product_name = ' '.join(product_name.split())  # Remove extra spaces
                product_name = product_name.title()  # Title case
                
                if original_name != product_name:
                    self.issues_report['product_name_issues'].append({
                        'product_id': product_id,
                        'original': original_name,
                        'cleaned': product_name
                    })
                
                cleaned_products.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'category': category,
                    'subcategory': subcategory,
                    'cost_price': cost_price
                })
        
        # Write cleaned products
        with open('products_cleaned.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['product_id', 'product_name', 'category', 'subcategory', 'cost_price'])
            writer.writeheader()
            writer.writerows(cleaned_products)
        
        print(f"✓ Cleaned {len(cleaned_products)} products (fixed {len(self.issues_report['product_name_issues'])} name issues)")
        return cleaned_products
    
    def validate_emails(self):
        """
        Validate customers.csv:
        - Check for valid email format (must have @ and domain)
        - Return list of customer_ids with invalid emails
        """
        print("Validating emails...")
        invalid_customers = []
        
        with open('customers.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer_id = row['customer_id'].strip()
                email = row['email'].strip()
                
                # Check if email has @ and a domain
                if '@' not in email or '.' not in email.split('@')[-1]:
                    invalid_customers.append({
                        'customer_id': customer_id,
                        'email': email,
                        'issue': 'Missing @ or domain'
                    })
                    self.issues_report['invalid_emails'].append(customer_id)
        
        print(f"✓ Found {len(invalid_customers)} customers with invalid emails")
        return invalid_customers
    
    def check_referential_integrity(self):
        """
        Check order_items referential integrity:
        - Ensure every order_id in order_items exists in orders
        - Find orphaned order_item records
        """
        print("Checking referential integrity...")
        
        # Load all valid order IDs from cleaned orders
        valid_order_ids = set()
        with open('orders_cleaned.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                valid_order_ids.add(row['order_id'].strip())
        
        # Check order_items
        orphaned_items = []
        with open('order_items.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                order_id = row['order_id'].strip()
                if order_id not in valid_order_ids:
                    orphaned_items.append({
                        'item_id': row['item_id'].strip(),
                        'order_id': order_id,
                        'status': 'Order not in cleaned orders'
                    })
                    self.issues_report['referential_integrity_errors'].append(order_id)
        
        # Also clean order_items (remove negative quantities and orphaned records)
        cleaned_items = []
        with open('order_items.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                item_id = row['item_id'].strip()
                order_id = row['order_id'].strip()
                product_id = row['product_id'].strip()
                quantity = int(row['quantity'].strip())
                unit_price = float(row['unit_price'].strip())
                discount_percent = float(row['discount_percent'].strip())
                
                # Skip if order_id doesn't exist in cleaned orders
                if order_id not in valid_order_ids:
                    continue
                
                # Keep negative quantities (they're legitimate returns)
                # But validate discount_percent
                if discount_percent < 0 or discount_percent > 100:
                    discount_percent = max(0, min(100, discount_percent))
                
                cleaned_items.append({
                    'item_id': item_id,
                    'order_id': order_id,
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'discount_percent': discount_percent
                })
        
        # Write cleaned order_items
        with open('order_items_cleaned.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['item_id', 'order_id', 'product_id', 'quantity', 'unit_price', 'discount_percent'])
            writer.writeheader()
            writer.writerows(cleaned_items)
        
        print(f"✓ Found {len(orphaned_items)} orphaned order items")
        print(f"✓ Cleaned {len(cleaned_items)} order items")
        
        return orphaned_items
    
    def generate_report(self):
        """Generate a summary report of all issues found"""
        print("\n" + "="*60)
        print("DATA QUALITY REPORT")
        print("="*60)
        
        print(f"\n1. NULL Customer IDs: {len(self.issues_report['null_customer_ids'])} orders removed")
        if self.issues_report['null_customer_ids'][:5]:
            print(f"   Examples: {', '.join(self.issues_report['null_customer_ids'][:5])}")
        
        print(f"\n2. Date Format Errors: {len(self.issues_report['date_format_errors'])} fixed")
        if self.issues_report['date_format_errors'][:3]:
            for item in self.issues_report['date_format_errors'][:3]:
                print(f"   {item['order_id']}: {item.get('original')} -> {item.get('corrected', 'SKIPPED')}")
        
        print(f"\n3. Invalid Emails: {len(self.issues_report['invalid_emails'])} customers")
        if self.issues_report['invalid_emails'][:5]:
            print(f"   Examples: {', '.join(self.issues_report['invalid_emails'][:5])}")
        
        print(f"\n4. Referential Integrity Errors: {len(self.issues_report['referential_integrity_errors'])} orphaned items")
        
        print(f"\n5. Product Name Issues: {len(self.issues_report['product_name_issues'])} fixed")
        if self.issues_report['product_name_issues'][:3]:
            for item in self.issues_report['product_name_issues'][:3]:
                print(f"   {item['product_id']}: '{item['original']}' -> '{item['cleaned']}'")
        
        print("\n" + "="*60)
        print("CLEANED FILES GENERATED:")
        print("  - orders_cleaned.csv")
        print("  - products_cleaned.csv")
        print("  - order_items_cleaned.csv")
        print("="*60 + "\n")
        
        # Write report to file
        with open('data_quality_report.txt', 'w') as f:
            f.write("DATA QUALITY REPORT\n")
            f.write("="*60 + "\n\n")
            f.write(f"NULL Customer IDs: {len(self.issues_report['null_customer_ids'])} orders\n")
            f.write(f"Date Format Errors: {len(self.issues_report['date_format_errors'])} fixed\n")
            f.write(f"Invalid Emails: {len(self.issues_report['invalid_emails'])} customers\n")
            f.write(f"Referential Integrity Errors: {len(self.issues_report['referential_integrity_errors'])} items\n")
            f.write(f"Product Name Issues: {len(self.issues_report['product_name_issues'])} fixed\n")

def main():
    cleaner = DataCleaner()
    
    # Run all cleaning functions
    cleaner.clean_orders()
    cleaner.clean_products()
    invalid_emails = cleaner.validate_emails()
    orphaned_items = cleaner.check_referential_integrity()
    
    # Generate report
    cleaner.generate_report()

if __name__ == "__main__":
    main()
