
# Supply Chain Digital Twin – Database Setup

## Prerequisites

- Python 3.13
- PostgreSQL 17
- Git

## 1. Clone the Repository

```powershell
git clone <REPOSITORY_URL>
cd "MLOPS Project"
```

Replace `<REPOSITORY_URL>` with the actual GitHub repository URL.

## 2. Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Configure PostgreSQL

Open PostgreSQL using psql as the postgres administrator.

Create the database and application user:

```sql
CREATE USER supply_chain_user WITH PASSWORD 'YOUR_PASSWORD';
CREATE DATABASE supply_chain_db OWNER supply_chain_user;
```

Connect to the new database:

```sql
\c supply_chain_db
```

Grant schema permissions:

```sql
GRANT USAGE, CREATE ON SCHEMA public TO supply_chain_user;
```

Use a strong password and keep it private.

## 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Update `.env` with your local PostgreSQL password:

```env
DATABASE_URL=postgresql+psycopg2://supply_chain_user:YOUR_PASSWORD@127.0.0.1:5432/supply_chain_db
```

If your password contains special URL characters, URL-encode them.

Never commit `.env` to GitHub.

## 5. Create Database Tables

```powershell
python -m src.data.create_tables
```

This creates all eight tables automatically.

## 6. Insert Sample Data

```powershell
python -m src.data.seed_data
```

This populates the database with synthetic supply chain data.

## 7. Verify Database Records

```powershell
python -m src.data.verify_data
```

Expected output:

```text
suppliers: 3 records
warehouses: 3 records
retailers: 3 records
products: 3 records
inventory: 18 records
orders: 3 records
shipments: 3 records
demand_history: 810 records
```

## Notes

- All sample records are synthetic.
- Running the seed script again should not duplicate the supplied sample records.
- Each developer uses their own local PostgreSQL database.
- Database scripts are shared through GitHub, not live database contents.
- Schema changes after initial setup will require migrations.
```
