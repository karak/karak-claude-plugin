CREATE TABLE orders (id uuid PRIMARY KEY, status text NOT NULL DEFAULT 'pending', amount int NOT NULL);
CREATE TABLE charges (id serial PRIMARY KEY, order_id uuid REFERENCES orders(id), gateway_ref text NOT NULL);
