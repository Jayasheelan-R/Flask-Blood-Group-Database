# Flask Blood Group Database

A lightweight Flask application to store and query names and blood groups.

This repository contains a small web app that demonstrates basic CRUD-style
operations against a MySQL database using `flask-mysqldb`. The app is intended
for learning and small internal tools; it is **not** production-ready without
further hardening (authentication, input rate-limits, backups).

## Features

- Add a record (name + blood group)
- List all records
- Delete a record by name
- Filter records by blood group

## Prerequisites

- Python 3.8+
- MySQL server (local or remote)
- `pip` for installing Python packages

## Install

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The app reads database configuration from `db.yaml` by default. Example `db.yaml`:

```yaml
mysql_host: localhost
mysql_user: your_mysql_user
mysql_password: your_password
mysql_db: blood_db
```

You can also provide configuration via environment variables: `MYSQL_HOST`,
`MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`. To provide a secret key for Flask set
`FLASK_SECRET_KEY`.

## Database schema

Create a minimal `blood` table in your MySQL database before running the app:

```sql
CREATE TABLE IF NOT EXISTS blood (
	name VARCHAR(255) PRIMARY KEY,
	blood_group VARCHAR(3) NOT NULL
);
```

Adjust column types and constraints as needed for your use-case.

## Run the app

Start the app with:

```bash
python proj.py
```

By default the app runs in debug mode if `FLASK_DEBUG` is `1` (or not set). For a
production deployment use a proper WSGI server (Gunicorn, uWSGI) and disable
debug mode.

## Tests / Validation

This repository doesn't include automated tests. After setup try the web UI at
`http://127.0.0.1:5000/` and exercise the forms.
