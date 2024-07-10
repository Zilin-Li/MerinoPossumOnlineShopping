from config import get_cursor  
from datetime import datetime  # Import datetime module for date and time handling

def get_popular_products_report(start_date=None, end_date=None):
    # Get the database cursor
    cursor = get_cursor()
    
    # If start_date is not provided, set it to a very old date to include all records
    if not start_date:
        start_date = '1900-01-01 00:00:00'
    # If end_date is not provided, set it to the current date and time
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # SQL query to fetch the popular products report based on the given date range
    query = """
    SELECT 
        p.product_name,  # Select product name
        SUM(od.price * od.quantity) AS total_sales_revenue,  # Calculate total sales revenue for each product
        SUM(od.quantity) AS total_quantity_sold,  # Calculate total quantity sold for each product
        COUNT(DISTINCT od.order_id) AS total_orders,  # Count the total number of unique orders for each product
        ROUND(AVG(o.total_excl_gst), 2) AS average_order_value  # Calculate the average order value
    FROM 
        order_details od  # From order details table
        JOIN orders o ON od.order_id = o.id  # Join with orders table on order ID
        JOIN products p ON od.product_id = p.id  # Join with products table on product ID
    WHERE 
        o.order_date BETWEEN %s AND %s  # Filter records between the start_date and end_date
    GROUP BY 
        p.product_name  # Group by product name
    ORDER BY 
        total_sales_revenue DESC, total_quantity_sold DESC  # Order the results by total sales revenue and total quantity sold in descending order
    """

    # Execute the query with the specified start_date and end_date
    cursor.execute(query, (start_date, end_date))
    # Fetch all the results from the query execution
    report_data = cursor.fetchall()
    
    # Close the cursor after the query execution
    cursor.close()
    
    # Return the fetched report data
    return report_data




















