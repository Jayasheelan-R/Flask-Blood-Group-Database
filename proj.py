"""Flask app for a simple blood-group database.

This module contains a small Flask application that stores and queries
donors (name and blood group) using MySQL. The code was refactored for
readability, input validation, and to avoid SQL injection.

Configuration is read from `db.yaml` (see README) or environment variables.
"""

from typing import Optional
import logging
import os

from flask import Flask, render_template, request, flash
from flask_mysqldb import MySQL
import yaml


# Allowed blood groups (normalized uppercase)
BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_db_config(config_path: str = "db.yaml") -> dict:
    """Load DB configuration from YAML file.

    Falls back to environment variables if file is missing.
    """
    if os.path.exists(config_path):
        with open(config_path, "r") as fh:
            data = yaml.safe_load(fh)
            if not isinstance(data, dict):
                raise RuntimeError("db.yaml must contain a mapping of mysql_* keys")
            return data

    # Fallback to environment variables
    logger.warning("%s not found. Falling back to environment variables.", config_path)
    return {
        "mysql_host": os.getenv("MYSQL_HOST", "localhost"),
        "mysql_user": os.getenv("MYSQL_USER", "root"),
        "mysql_password": os.getenv("MYSQL_PASSWORD", ""),
        "mysql_db": os.getenv("MYSQL_DB", "blood_db"),
    }


def create_app(config_path: str = "db.yaml") -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    db_conf = load_db_config(config_path)
    app.config["MYSQL_HOST"] = db_conf.get("mysql_host")
    app.config["MYSQL_USER"] = db_conf.get("mysql_user")
    app.config["MYSQL_PASSWORD"] = db_conf.get("mysql_password")
    app.config["MYSQL_DB"] = db_conf.get("mysql_db")
    app.config["MYSQL_CURSORCLASS"] = "DictCursor"

    # Use environment-provided secret if present; otherwise generate one.
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY") or os.urandom(24)

    mysql = MySQL(app)


    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")


    @app.route("/form", methods=["GET", "POST"])
    def form():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            blood_group = request.form.get("blood_group", "").upper().strip()

            if not name:
                flash("Name is required", "error")
                return render_template("form.html")

            if blood_group not in BLOOD_GROUPS:
                flash("Invalid blood group", "error")
                return render_template("form.html")

            # Normalize name (title case) and insert safely
            normalized_name = name.upper()
            try:
                cur = mysql.connection.cursor()
                cur.execute(
                    "INSERT INTO blood (name, blood_group) VALUES (%s, %s)",
                    (normalized_name, blood_group),
                )
                mysql.connection.commit()
                flash("Record added successfully", "success")
            except Exception as e:
                logger.exception("Failed to insert record")
                flash("An error occurred while saving the record", "error")

        return render_template("form.html")


    @app.route("/info", methods=["GET"])
    def info():
        try:
            cur = mysql.connection.cursor()
            count = cur.execute("SELECT name, blood_group FROM blood ORDER BY name")
            if count > 0:
                info_rows = cur.fetchall()
                return render_template("info.html", info=info_rows, x=len(info_rows))
            return render_template("empty.html")
        except Exception:
            logger.exception("Failed to fetch records")
            flash("Could not fetch records", "error")
            return render_template("empty.html")


    @app.route("/delete", methods=["GET", "POST"])
    def delete():
        if request.method == "POST":
            name = request.form.get("wow", "").strip()
            if not name:
                flash("Name is required to delete", "error")
                return render_template("delete.html")
            try:
                cur = mysql.connection.cursor()
                cur.execute("DELETE FROM blood WHERE name = %s", (name.upper(),))
                mysql.connection.commit()
                flash("Record deleted (if existed)", "success")
            except Exception:
                logger.exception("Failed to delete record")
                flash("An error occurred while deleting the record", "error")

        return render_template("delete.html")


    @app.route("/select", methods=["GET", "POST"])
    def select():
        if request.method == "POST":
            bg = request.form.get("hii", "").upper().strip()
            if bg not in BLOOD_GROUPS:
                flash("Invalid blood group selected", "error")
                return render_template("select.html")

            try:
                cur = mysql.connection.cursor()
                count = cur.execute("SELECT name, blood_group FROM blood WHERE blood_group = %s", (bg,))
                if count > 0:
                    info_rows = cur.fetchall()
                    return render_template("info.html", info=info_rows, x=len(info_rows))
                return render_template("empty.html")
            except Exception:
                logger.exception("Failed to query by blood group")
                flash("An error occurred while querying records", "error")

        return render_template("select.html")


    return app


if __name__ == "__main__":
    # When running locally keep debug controlled by environment
    debug_mode = os.getenv("FLASK_DEBUG", "1") in ("1", "true", "True")
    app = create_app()
    app.run(debug=debug_mode)
