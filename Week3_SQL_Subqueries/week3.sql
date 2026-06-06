-- creating database superstore_raw.
create database superstore_raw;
use superstore_raw;

-- 1. Import the Superstore dataset into a table named superstore_raw.  
LOAD DATA LOCAL INFILE 'D:/Downloads_D/Sample - Superstore.csv'
INTO TABLE superstore_raw
CHARACTER SET latin1
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;


-- 2a. creating Customers table and inserting data using distinct
create table customers as
select distinct
Customer_ID,
Customer_Name,
Segment
from superstore_raw;

-- 2b. creating orders table and inserting data using distinct
-- Relax the SQL mode for the current session(to avoid zero date error)
set session sql_mode = REPLACE(REPLACE(@@sql_mode, 'NO_ZERO_DATE', ''), 'NO_ZERO_IN_DATE', '');

create table orders as
select distinct
Order_ID,
Order_Date,
Ship_Date,
Customer_ID,
Product_ID,
Sales,
Quantity,
Discount,
Profit
from superstore_raw;

-- 2c. creating products table and inserting data using distinct
create table products as
select distinct
Product_ID,
Product_Name,
Category,
Sub_Category
from superstore_raw;


-- Step 2: Performing Required Queries

-- 1. Find all orders where sales are greater than the average sales. (Subquery)
  
select *
from orders
where Sales >
(
select avg(Sales)
from orders
);

-- 2. Find the highest sales order for each customer. (Subquery)  

select *
from orders o
where Sales = (
select
max(o2.Sales)
from orders o2
where o2.Customer_ID = o.Customer_ID);

-- 3. Calculate total sales for each customer. (CTE)  

with customerSales as (
select Customer_ID,
sum(sales) as TotalSales
from orders
group by Customer_ID)
select * from customerSales;

-- 4. Find customers whose total sales are above average. (CTE + Subquery)  

with CustomerSales as (
select Customer_ID,
sum(sales) as TotalSales
from orders
group by Customer_ID)
select * from CustomerSales
where TotalSales > (
select Avg(TotalSales)
from CustomerSales);

-- 5. Rank all customers based on total sales. (Window Function)  

with CustomerSales as (
select Customer_ID,
sum(sales) as TotalSales
from orders
group by Customer_ID)
select Customer_ID,
TotalSales,
RANK() over (order by TotalSales desc) as CustomerRank
from CustomerSales;

-- 6. Assign row numbers to each order within a customer. (Window Function + PARTITION BY)

select customer_id,
order_id,
sales,
row_number() over(
partition by customer_id
order by sales desc
) as RowNum
from orders;

-- 7.  Display top 3 customers based on total sales. (Window Function)  

with CustomerSales as
(
    select
        Customer_ID,
        sum(Sales) as TotalSales
    from orders
    group by Customer_ID
),
RankedCustomers as
(
    select
        Customer_ID,
        TotalSales,
        RANK() over (order by TotalSales desc) as CustomerRank
    from CustomerSales
)
select *
from RankedCustomers
where CustomerRank <= 3;   


/*
Step 3: Final Combined Query 
Write one final query that shows: 
•	Customer Name  
•	Total Sales  
•	Rank  
(Use JOIN + CTE + Window Function together) 
*/

WITH CustomerSales AS
(
    SELECT
        Customer_ID,
        SUM(Sales) AS TotalSales
    FROM orders
    GROUP BY Customer_ID
)

SELECT
    c.Customer_Name,
    cs.TotalSales,
    RANK() OVER (ORDER BY cs.TotalSales DESC) AS CustomerRank
FROM CustomerSales cs
JOIN customers c
ON cs.Customer_ID = c.Customer_ID
ORDER BY CustomerRank;

