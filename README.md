BazaarIQ
BazaarIQ is a DBMS-based e-commerce platform that ensures secure user authentication, unique user registration, and login validation using database constraints and logic.

E-Commerce Backend with Query Performance Analyzer
B.Tech AI & Data Science Final Project Demo.

Features
User auth (register/login)
Products CRUD
Cart & Orders (normalized DB)
Dashboard: Stats, Query Logs (time/cache/CPU/mem), Index Demo
Responsive Bootstrap UI
DB Schema
users → cart, orders → order_items → products
Indexes: product.category
Run
cd d:/navpreet
python app.py
Open http://127.0.0.1:5000

Demo Admin: admin@test.com / admin

Query Analyzer: Place orders, toggle index, see logs/colors/cache hits.

CAO Sim: CPU cycles (rows*complexity), Memory (result size), LRU Cache (100 cap).

Viva Points
Normalization (3NF)
Indexing impact
Cache HIT/MISS
Query perf metrics
