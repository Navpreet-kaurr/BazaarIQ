# BazaarIQ - E-Commerce Backend with Query Performance Analyzer

B.Tech AI & Data Science Final Project Demo.

## Features
- User auth (register/login)
- Products CRUD
- Cart & Orders (normalized DB)
- Dashboard: Stats, Query Logs (time/cache/CPU/mem), Index Demo
- Responsive Bootstrap UI
 
## Database Schema
The system utilizes a normalized relational structure:
- `Users` → `Cart`
- `Orders` → `Order Items` → `Products`
- **Indexes**: `product.category`
  
## Installation
   **Clone the repository**:
   ```bash
   git clone https://github.com/Navpreet-kaurr/BazaarIQ.git
   cd BazaarIQ
   ```
   Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   Run the application:
   ```
   python app.py
   ```
   Access the platform:
   Open http://127.0.0.1:5000
  
### Demo Credentials
Admin: admin@test.com / admin

### Query Analyzer
Place Orders: Perform user activities to generate database logs.
Toggle Index: Use the dashboard to enable/disable indexing on product categories.
Analyze: Monitor the dashboard logs to observe the impact of cache hits vs. misses.

### Computational Simulation
CPU Cycles: Calculated via rows * complexity.
Memory: Calculated via result size.
LRU Cache: 100-capacity caching mechanism implemented for performance testing.



