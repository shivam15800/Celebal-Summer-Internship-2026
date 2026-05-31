-- Q1: Display all rows and columns from customers table
SELECT * FROM customers;

-- Q2: Retrieve first_name, last_name and city
SELECT first_name, last_name, city
FROM customers;

-- Q3: List all unique categories available in the products table.
SELECT DISTINCT category
FROM products;

-- Q5: Constraints on email Column and duplicate email entry
-- duplicate email entry
INSERT INTO customers
VALUES (
109,
'Test',
'User',
'aarav.s@email.com',
'Mumbai',
'Maharashtra',
'2024-09-01',
TRUE
);

-- Q- 6 Try inserting a product with unit_price = -50. What happens and which constraint prevents it? Write both the INSERT statement and explain the error.
-- Query:
INSERT INTO products
VALUES (
209,
'Fake Product',
'Electronics',
'TestBrand',
-50,
100
);


--  Q7. Retrieve all orders with status = 'Delivered'.
SELECT *
FROM orders
WHERE status = 'Delivered';

-- Q8. Find all products in the 'Electronics' category with a unit_price greater than ₹2000.
SELECT *
FROM products
WHERE category = 'Electronics'
AND unit_price > 2000;

-- Q9. List all customers who joined in the year 2024 and belong to the state 'Maharashtra'.
SELECT *
FROM customers
WHERE join_date >= '2024-01-01'
AND join_date < '2025-01-01'
AND state = 'Maharashtra';

-- Q10. Find all orders placed between '2024-08-10' and '2024-08-25' (inclusive) that are NOT cancelled.
SELECT *
FROM orders
WHERE order_date BETWEEN '2024-08-10' AND '2024-08-25'
AND status != 'Cancelled';

-- Q11. Explain what the index idx_orders_date does. How would it improve the performance of a query that filters orders by order_date? Write a sample query that would benefit from this index.
SELECT *
FROM orders
WHERE order_date BETWEEN '2024-08-01' AND '2024-08-31';

-- Q12. If you run: SELECT * FROM customers WHERE YEAR(join_date) = 2024; — would the index on join_date be used? Explain why or why not, and rewrite the query to be index-friendly (SARGable).
-- new updated query
SELECT *
FROM customers
WHERE join_date >= '2024-01-01'
AND join_date < '2025-01-01';

-- Q13. Count the total number of orders in the orders table.
SELECT COUNT(*) AS total_orders
FROM orders;

-- Q14. Find the total revenue (SUM of total_amount) from all 'Delivered' orders.
SELECT SUM(total_amount) AS total_revenue
FROM orders
WHERE status = 'Delivered';

-- Q15. Calculate the average unit_price of products in each category.
select category, avg(unit_price) as avg_pr
from products
group by category;

-- Q16. For each order status, find the count of orders and the total revenue. Sort the result by total revenue in descending order.
select status,
count(*),
sum(total_amount) as total_revenue
from orders
group by status
order by total_revenue desc;

-- Q17. Find the most expensive (MAX) and cheapest (MIN) product in each category.
select category,
min(unit_price) as Min_price,
max(unit_price) as Max_price
from products
group by category;

-- Q18. List all product categories where the average unit_price is greater than ₹2000. (Hint: Use HAVING clause)
select category,
avg(unit_price) as avg_price
from products
group  by category
having avg_price > 2000;

-- Q19. Write an INNER JOIN query to display each order along with the customer's first_name and last_name. Show: order_id, order_date, first_name, last_name, total_amount.
select o.order_id,
o.order_date,
c.first_name,
c.last_name,
o.total_amount
from orders o
inner join customers c
on o.customer_id = c.customer_id;

-- Q20. Using a LEFT JOIN, list ALL customers and their orders (if any). Customers with no orders should still appear with NULL values for order columns.
select c.customer_id,
c.first_name,
c.last_name,
o.order_id,
o.order_date,
o.total_amount
from customers c
left join orders o
on c.customer_id = o.customer_id;

-- Q21. Write a query using JOINs across three tables (orders → order_items → products) to show: order_id, product_name, quantity, unit_price, and discount_pct for each order item.
select o.order_id,
p.product_name,
oi.quantity,
oi.unit_price,
oi.discount_pct
from orders o
inner join  order_items oi
on o.order_id = oi.order_id
inner join products p
on oi.product_id = p.product_id;

-- Q22. Explain the difference between LEFT JOIN and RIGHT JOIN with an example from this schema. When would you use a FULL OUTER JOIN?
-- left join 
SELECT *
FROM customers c
LEFT JOIN orders o
ON c.customer_id = o.customer_id;

-- right join 
SELECT *
FROM customers c
RIGHT JOIN orders o
ON c.customer_id = o.customer_id;

-- Q23. Identify all Foreign Key relationships in the schema. Explain what would happen if you tried to insert an order with customer_id = 999 (which doesn't exist in customers). 
insert into orders
values(1011, 999, "2024-09-01", "Pending", 2000);

/*Q24. Write a query using CASE to classify products into price tiers:
  • 'Budget'    → unit_price < 1000
  • 'Mid-Range' → unit_price BETWEEN 1000 AND 3000
  • 'Premium'   → unit_price > 3000
Display: product_name, unit_price, price_tier.
*/
select product_name,
unit_price,
case
when unit_price < 1000 then 'Budget'
when unit_price > 1000 and unit_price < 3000 then 'Mid-Range'
when unit_price > 3000 then 'Premium'
end as price_tiers
from products;

-- Q25. Using a CASE statement inside an aggregate function, count how many orders are 'Delivered' vs 'Not Delivered' (all other statuses). Display the result in a single row.
select
sum(case
when status = 'Delivered' then 1
else 0
end) as delivered_orders,
sum(case
when status != 'Delivered' then 1
else 0
end) as not_delivered_orders
from orders;

/*Q27. Write a SQL transaction that does the following atomically:
  1. Insert a new order (order_id=1011, customer_id=102, today's date, 'Pending', 1598.00)
  2. Insert two order items for that order
  3. Update the stock_qty of the purchased products
  4. If any step fails, ROLLBACK the entire transaction. Otherwise, COMMIT.
Write the complete BEGIN...COMMIT/ROLLBACK block.
*/
-- Start transaction
START TRANSACTION;

-- Insert new order
INSERT INTO orders (
    order_id,
    customer_id,
    order_date,
    status,
    total_amount
)
VALUES (
    1011,
    102,
    CURDATE(),
    'Pending',
    1598.00
);

-- Insert first order item
INSERT INTO order_items (
    item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_pct
)
VALUES (
    5016,
    1011,
    202,
    1,
    799.00,
    0
);

-- Insert second order item
INSERT INTO order_items (
    item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_pct
)
VALUES (
    5017,
    1011,
    208,
    1,
    599.00,
    0
);

-- Update stock for first product
UPDATE products
SET stock_qty = stock_qty - 1
WHERE product_id = 202;

-- Update stock for second product
UPDATE products
SET stock_qty = stock_qty - 1
WHERE product_id = 208;

-- If all queries execute successfully
COMMIT;

-- If any query fails, undo all changes
ROLLBACK;
