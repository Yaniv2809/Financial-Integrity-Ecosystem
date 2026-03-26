CREATE TABLE IF NOT EXISTS expenses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    expense_name VARCHAR(255),
    amount DOUBLE CHECK (amount >= 0),
    date VARCHAR(50),
    category VARCHAR(100)
);
