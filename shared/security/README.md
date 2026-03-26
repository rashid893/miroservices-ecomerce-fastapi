# Shared Security

JWT secret must be shared between services so each service can independently
validate access tokens without calling auth-service on every request.

In production, use a secret manager (AWS Secrets Manager, Vault, etc.)
and inject the same JWT_SECRET_KEY into all services via environment variables.

Never hard-code the secret. Never commit it to version control.
