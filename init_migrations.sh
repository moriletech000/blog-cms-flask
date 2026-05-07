#!/bin/bash

# Initialize Flask-Migrate and create initial migration
# Run this script once to set up database migrations

echo "Initializing Flask-Migrate..."

# Initialize migrations directory
flask db init

# Create initial migration
flask db migrate -m "Initial migration: users, posts, categories, tags, comments, likes"

# Apply migration
flask db upgrade

echo "Migrations initialized successfully!"
echo "Database tables created."
echo ""
echo "Next steps:"
echo "1. Run 'flask seed-db' to populate with sample data"
echo "2. Or run 'flask create-admin --email admin@example.com --password yourpassword'"