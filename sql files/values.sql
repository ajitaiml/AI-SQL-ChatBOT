
INSERT INTO customers (name, email, phone, city)
SELECT
    'Customer_' || i AS name,
    'customer' || i || '@example.com' AS email,
    '+91' || (1000000000 + floor(random() * 9000000000)::bigint) AS phone,
    CASE (floor(random() * 5)::int)
        WHEN 0 THEN 'Mumbai'
        WHEN 1 THEN 'Delhi'
        WHEN 2 THEN 'Bangalore'
        WHEN 3 THEN 'Chennai'
        WHEN 4 THEN 'Kolkata'
    END AS city
FROM generate_series(1, 1000) AS s(i);



SELECT * FROM customers

INSERT INTO products (name, category, price, stock)
SELECT
    'Product_' || i AS name,
    CASE (floor(random() * 5)::int)
        WHEN 0 THEN 'Electronics'
        WHEN 1 THEN 'Clothing'
        WHEN 2 THEN 'Books'
        WHEN 3 THEN 'Home'
        WHEN 4 THEN 'Sports'
    END AS category,
    round((random() * 1000 + 50)::numeric, 2) AS price,   -- price between 50 and 1050
    floor(random() * 100 + 1) AS stock                      -- stock between 1 and 100
FROM generate_series(1, 1000) AS s(i);




INSERT INTO orders (customer_id, order_date, total_amount)
SELECT
    floor(random() * 1000 + 1)::int AS customer_id,   -- assuming 1000 customers
    CURRENT_DATE - (floor(random() * 365))::int AS order_date,  -- past 1 year
    0 AS total_amount   -- will update after order_items
FROM generate_series(1, 2000) AS s(i);




INSERT INTO employees (name, role, hire_date, salary)
SELECT
    'Employee_' || i AS name,
    CASE (floor(random() * 4)::int)
        WHEN 0 THEN 'Manager'
        WHEN 1 THEN 'Sales'
        WHEN 2 THEN 'Support'
        WHEN 3 THEN 'Developer'
    END AS role,
    CURRENT_DATE - (floor(random() * 2000))::int AS hire_date,
    round((random() * 90000 + 30000)::numeric, 2)
FROM generate_series(1, 50) AS s(i);


