-- create roles table
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL
);

-- create order_statuses table
CREATE TABLE IF NOT EXISTS order_status_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status_type VARCHAR(50) NOT NULL,
    description VARCHAR(255)
);
-- create payment_types table
CREATE TABLE IF NOT EXISTS payment_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL,
    description VARCHAR(255)
);
-- create colors table
CREATE TABLE IF NOT EXISTS product_colors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    color_name VARCHAR(50) NOT NULL UNIQUE
);

-- create sizes table
CREATE TABLE IF NOT EXISTS sizes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    size_name VARCHAR(50) NOT NULL UNIQUE
);

-- create brands table
CREATE TABLE IF NOT EXISTS brands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL UNIQUE,
    description VARCHAR(255)
);
-- create image_types table
CREATE TABLE IF NOT EXISTS image_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);


-- create message_type table
CREATE TABLE IF NOT EXISTS message_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_type_name VARCHAR(50) NOT NULL,
    description VARCHAR(255)
);



-- create gift_cards_types table
CREATE TABLE IF NOT EXISTS gift_cards_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL,
    value DECIMAL(10, 2) NOT NULL,
    description VARCHAR(255),
    redeem_points int NOT NULL,
    is_active Tinyint
);

-- create promotions table
CREATE TABLE IF NOT EXISTS promotions (
    is_active BOOLEAN DEFAULT TRUE,
    id INT AUTO_INCREMENT PRIMARY KEY,
    promotion_name VARCHAR(100) NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    discount_rate DECIMAL(4, 3) NOT NULL,
    description TEXT
);


-- create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(100) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    post_code VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    role_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_logged_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);


-- create categories table
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_category_id INT,
    category_name VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    FOREIGN KEY (parent_category_id) REFERENCES categories(id)
);


-- create products tables
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL UNIQUE,
    category_id INT NOT NULL,
    brand_id INT NOT NULL,
    description TEXT,
    base_price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (brand_id) REFERENCES brands(id)
);

-- create product_images table
CREATE TABLE IF NOT EXISTS product_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    image_type_id INT NOT NULL,
    color_id INT,
    description VARCHAR(255),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (image_type_id) REFERENCES image_types(id),
    FOREIGN KEY (color_id) REFERENCES product_colors(id)
);

-- create variants table
CREATE TABLE IF NOT EXISTS product_variants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    color_id INT NOT NULL,
    size_id INT NOT NULL,
    stock_quantity INT DEFAULT 0,
    additonal_price DECIMAL(10, 2) DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (color_id) REFERENCES product_colors(id),
    FOREIGN KEY (size_id) REFERENCES sizes(id)
);


-- create orders table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date DATETIME NOT NULL,
    total_excl_gst DECIMAL(10, 2) DEFAULT 0,
    total_points DECIMAL(10, 2) DEFAULT 0,
    shipping_fee DECIMAL(10,2) DEFAULT 0,
    status_id INT NOT NULL,
    recipient_name VARCHAR(50) NOT NULL,
    recipient_mobile VARCHAR(20) NOT NULL,
    delivery_street VARCHAR(500) NOT NULL,
    delivery_city VARCHAR(100) NOT NULL,
    delivery_state VARCHAR(100) NOT NULL,
    delivery_post_code VARCHAR(20) NOT NULL,
    delivery_country VARCHAR(100) NOT NULL,
    order_note VARCHAR(255),
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (status_id) REFERENCES order_status_types(id)
);

-- create invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_id INT NOT NULL,
    total_incl_gst DECIMAL(10, 2) NOT NULL,
    shipping_fee DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    is_paid BOOLEAN NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    invoice_id INT NOT NULL,
    payment_date DATETIME NOT NULL,
    payment_type_id INT NOT NULL,
    FOREIGN KEY (invoice_id ) REFERENCES invoices(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (payment_type_id) REFERENCES payment_types(id)
);
-- create messages table
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    send_id INT NOT NULL,
    receive_id INT NOT NULL,
    message_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    message_type_id INT NOT NULL,
    FOREIGN KEY (send_id) REFERENCES users(id),
    FOREIGN KEY (receive_id) REFERENCES users(id),
    FOREIGN KEY (message_type_id) REFERENCES message_type(id)
);

-- create customers table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    point INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- create corporate_clients table
CREATE TABLE IF NOT EXISTS corporate_clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    discount_level INT NOT NULL,
    credit_limit DECIMAL(10, 2) NOT NULL,
    available_credit DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- create credit_limit_increase_requests table
CREATE TABLE IF NOT EXISTS credit_limit_increase_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    requested_limit DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved BOOLEAN DEFAULT FALSE,
    approved_date TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- create employees table
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    hire_date DATE NOT NULL,
    job_title VARCHAR(50) NOT NULL,
    is_admin BOOLEAN NOT NULL,
    is_manager BOOLEAN NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- create monthly_settlements table
CREATE TABLE IF NOT EXISTS monthly_settlements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    settlement_amount DECIMAL(10, 2) DEFAULT 0,
    settlement_date DATETIME NOT NULL,
    is_paid BOOLEAN NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- create carts table
CREATE TABLE IF NOT EXISTS carts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
-- create cart_items tables
CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES carts(id),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
-- create reward_transactions table
CREATE TABLE IF NOT EXISTS reward_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    point_change INT NOT NULL,
    transaction_date DATETIME NOT NULL,
    user_id INT NOT NULL,
    order_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
-- create gift_cards table
CREATE TABLE IF NOT EXISTS gift_cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type_id INT NOT NULL,
    card_number VARCHAR(50) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL,
    purchase_time DATETIME NOT NULL,
    FOREIGN KEY (type_id) REFERENCES gift_cards_types(id)
);

-- create gift_card_transactions table
CREATE TABLE IF NOT EXISTS gift_card_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_id INT NOT NULL,
    order_id INT NOT NULL,
    balance_change DECIMAL(10,2) NOT NULL,
    transaction_date DATETIME NOT NULL,
    FOREIGN KEY (card_id) REFERENCES gift_cards(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
-- create order_details table
CREATE TABLE IF NOT EXISTS order_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) DEFAULT 0,
    points INT DEFAULT 0,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id)
);

-- create reward_products table
CREATE TABLE IF NOT EXISTS reward_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    required_points INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- create promotion_products table
CREATE TABLE IF NOT EXISTS promotion_products (
    id INT AUTO_INCREMENT PRIMARY KEY,   
    promotion_id INT NOT NULL,
    product_id INT,
    category_id INT,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (promotion_id) REFERENCES promotions(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- create news table
CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    news_content TEXT NOT NULL,
    selected BOOLEAN DEFAULT FALSE    
);