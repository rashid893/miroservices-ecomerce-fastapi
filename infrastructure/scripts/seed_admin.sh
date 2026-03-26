#!/bin/bash
# Create an admin user via the auth-service REST API
# Usage: ./infrastructure/scripts/seed_admin.sh

curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "Admin1234!",
    "full_name": "Admin User"
  }' | python3 -m json.tool

echo ""
echo "Note: manually set role=admin in the database:"
echo "  docker compose exec auth-db psql -U auth_user -d auth_db -c \"UPDATE users SET role='admin' WHERE email='admin@example.com';""
