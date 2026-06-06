# **Mini Project: Customer Sales Insights**



#### **Objective:**



The objective of this project is to analyze customer purchasing behavior using SQL techniques such as Subqueries, Common Table Expressions (CTEs), Joins, Aggregation Functions, and Window Functions. The analysis helps identify high-value customers, low-value customers, customer engagement patterns, and sales trends.



#### 

#### Dataset Information



##### Dataset: Superstore Sales Dataset



###### Key Tables:



* customers
* orders
* products



###### Important Fields Used:



* Customer\_ID
* Customer\_Name
* Order\_ID
* Sales







#### Answer the following using SQL:



1. Who are the top 5 customers?



**Purpose**: Identify customers contributing the highest revenue to the business.



**Query:**

with CustomerSales as (

&#x20;   select

&#x20;       c.Customer\_Name,

&#x20;       sum(o.Sales) as TotalSales

&#x20;   from orders o

&#x20;   join customers c

&#x20;       on o.Customer\_ID = c.Customer\_ID

&#x20;   group by c.Customer\_Name

)

select \*

from CustomerSales

order by TotalSales DESC

LIMIT 5;



**Output:**

Customer\_Name	TotalSales

Sean Miller	25043.07

Tamara Chand	19052.22

Raymond Buch	15117.35

Tom Ashbrook	14595.62

Adrian Barton	14473.57



###### Insight

* Sean Miller generated the highest revenue of $25,043.07.
* The top five customers contribute a significant portion of total sales.
* These customers can be targeted through loyalty and retention programs.





2\. Who are the bottom 5 customers?



**purpose**: Identify customers with the lowest contribution to sales.



**Query:**



with CustomerSales as (

&#x20;   select

&#x20;       c.Customer\_Name,

&#x20;       SUM(o.Sales) as TotalSales

&#x20;   from orders o

&#x20;   join customers c

&#x20;       ON o.Customer\_ID = c.Customer\_ID

&#x20;   group by c.Customer\_Name

)

select \* from CustomerSales

order by TotalSales ASC

LIMIT 5;



**Output:**

Customer\_Name	TotalSales

Thais Sissman	4.84

Lela Donovan	5.30

Carl Jackson	16.52

Mitch Gastineau	16.74

Roy Skaria	22.33



###### Insight

* Thais Sissman generated only $4.84 in sales.
* The bottom five customers collectively contribute very little revenue.
* Marketing campaigns may be used to improve engagement among these customers.





3\. Which customers made only one order?



**Query:**



select

&#x20;   c.Customer\_Name,

&#x20;   COUNT(DISTINCT o.Order\_ID) AS OrderCount

from orders o

join customers c

&#x20;   ON o.Customer\_ID = c.Customer\_ID

group by c.Customer\_Name

having count(DISTINCT o.Order\_ID) = 1;



**Output:**

Customer\_Name		OrderCount

Anemone Ratner		1

Anthony O'Donnell	1

Carl Jackson		1

Jenna Caffey		1

Jocasta Rupert		1

Lela Donovan		1

Mitch Gastineau		1

Patricia Hirasaki	1

Ricardo Emerson		1

Roland Murray		1

Susan MacKendrick	1

Theresa Coyne		1



###### Insight

* 12 customers placed only one order.
* Single-order customers may indicate low retention or infrequent purchasing behavior.
* Follow-up marketing campaigns could encourage repeat purchases.





4\. Which customers have above-average sales?

&#x20;

**Query:**



with CustomerSales as (

&#x20;   select

&#x20;       c.Customer\_Name,

&#x20;       SUM(o.Sales) AS TotalSales

&#x20;   from orders o

&#x20;   join customers c

&#x20;       on o.Customer\_ID = c.Customer\_ID

&#x20;   group by c.Customer\_Name

)

select \* from CustomerSales

where TotalSales > (

&#x20;   select avg(TotalSales)

&#x20;   from CustomerSales

);



**Output: only top 5 rows are displayed**

Customer\_Name	TotalSales

Brosina Hoffman	6255.34

Irene Maddox	4930.49

Pete Kriz	8646.93

Tracy Blumstein	4737.48

Matt Abelman	4299.16'



###### Insight

* 294 customers have total sales above the overall customer average.



5\. What is the highest order value per customer?



**Query:**



select

&#x20;   c.Customer\_Name,

&#x20;   MAX(o.Sales) AS HighestOrderValue

from orders o

join customers c

&#x20;   on o.Customer\_ID = c.Customer\_ID

group by c.Customer\_Name

order by HighestOrderValue DESC;



**Output:**



Customer\_Name	HighestOrderValue

Sean Miller	22638.48

Tamara Chand	17499.95

Raymond Buch	13999.96

Tom Ashbrook	11199.97

Hunter Lopez	10499.97



###### Insight

* Sean Miller placed the highest single-value order worth $22,638.48.
* High-value orders significantly impact overall revenue.
* Monitoring such customers can help identify strategic business opportunities.



#### Conclusion



This analysis used SQL Joins, CTEs, Aggregation Functions, Subqueries, and Window Functions to examine customer purchasing behavior within the Superstore dataset. The results show that a small group of customers contributes a large percentage of total sales, while several customers generate minimal revenue or make only a single purchase. Understanding these patterns enables businesses to improve customer retention strategies, target high-value customers, and optimize sales performance.

