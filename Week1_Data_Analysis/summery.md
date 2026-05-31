Assignment Summary

In this assignment, I used Pandas to load and work with the dataset from a CSV file. First, I explored the dataset using functions like head(), shape, columns, dtypes, and info() to understand the structure of the data.

After that, I checked for missing values using isnull().sum() and handled them by filling appropriate values such as 0, "No review", "Unknown Seller", "No Video", and "Not Available" depending on the column type and meaning.

I also checked the dataset for duplicate rows using duplicated().sum() and performed basic filtering operations to display products with ratings greater then 4. Column selection operations were also performed on the dataset.

The final_price column originally contained string values with currency symbols and commas, so I cleaned the column using regular expresions and converted it into numeric format using pd.to_numeric().

A new derived column named total_amount was created using initial_price and ratings_count to perform basic column transformation operations in Pandas. Since the dataset did not contain quantity data, ratings count was used insted for the calculation.

Finally, the cleaned dataset was saved as a new CSV file named cleaned_combined_dataset.csv.