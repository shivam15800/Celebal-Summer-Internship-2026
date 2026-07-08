# Delta Lake Assignment: Incremental Data Processing

## Overview

This project demonstrates incremental data processing using **Delta Lake** on the **Databricks** platform. The workflow covers loading data into a Delta table, performing data cleaning, processing incremental data using the `MERGE` operation, and validating the final results.

## Objectives

- Load a CSV dataset into a Delta table.
- Perform basic data cleaning by removing null values and duplicate records.
- Load a second CSV file containing incremental data.
- Apply the Delta Lake `MERGE` operation to:
  - Update existing records.
  - Insert new records.
- Validate the results by checking the row count and duplicate records.
- Display the final dataset and Delta transaction history.

## Technologies Used

- Databricks
- Apache Spark (PySpark)
- Delta Lake
- Python

## Project Structure

```
.
├── DeltaLakeAssignment.ipynb
├── dataset_50_records.csv
├── incremental_data.csv
└── README.md
```

## Workflow

### 1. Load Dataset

The primary dataset is loaded from a CSV file into a Spark DataFrame.

### 2. Data Cleaning

The dataset is cleaned by:
- Removing records containing null values.
- Removing duplicate records.

### 3. Create Delta Table

The cleaned dataset is stored as a Delta table using:

```python
df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("customer_master")
```

### 4. Load Incremental Dataset

A second CSV file containing updated and new records is loaded into another DataFrame.

### 5. Incremental Processing

Delta Lake's `MERGE` operation is used to:
- Update existing customer records.
- Insert new customer records.

This implementation follows the **Slowly Changing Dimension (SCD) Type 1** approach, where existing records are overwritten with the latest values.

### 6. Validation

The results are validated by:
- Counting the total number of records.
- Checking for duplicate IDs.
- Displaying the final Delta table.
- Viewing the Delta transaction history.

## Expected Output

After executing the notebook:

- The Delta table contains cleaned data.
- Existing records are updated.
- New records are inserted.
- Duplicate records are removed.
- Delta transaction history shows the completed operations.

## Learning Outcomes

This project demonstrates:

- Reading CSV files using PySpark.
- Performing basic data cleaning.
- Creating and managing Delta tables.
- Implementing incremental data processing.
- Using Delta Lake's `MERGE` operation.
- Validating processed data.
- Understanding SCD Type 1 implementation.

## Author

**Shivam**