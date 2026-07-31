# DEPENDENCY_GRAPH — HUSSAM PLATFORM V3.0

Nodes (high-level):
- core/config (PROTECTED)
- Database (Postgres + Alembic)
- Authentication service
- Tenancy engine
- Ledger (entries & transactions)
- Payments (gateway & verification)
- Storage (object storage)
- Logistics / Shipments
- Products / Marketplace
- AI Hub & Telemetry
- Frontend (Vite + React)
- DevOps (CI/CD + infra)
- Monitoring & Observability

Graph relationships (directed edges)
- core/config -> Database, Auth, Payments, Storage, Frontend (configuration)
- Database -> Ledger, Auth, Tenants, Payments, Storage
- Auth -> Frontend, Payments, Ledger (authorization)
- Tenancy -> Ledger, Storage, Auth (isolation)
- Ledger -> Payments (ledger entries from payments)
- Payments -> Payment Verifications -> Ledger (verification writes)
- Storage -> Frontend (uploads/downloads)
- Logistics -> Shipments -> Database
- AI Hub -> Database (audit logs) and Monitoring
- DevOps -> CI/CD -> All (build & deploy pipelines)
- Monitoring -> Alerting/Oncall (operational control plane)

ASCII dependency visual:
```
                 +-----------------+
                 | core/config (*) |
                 +-----------------+
                          |
                          v
                       Database
                          |
        +-----------------+----------------+
        |                 |                |
        v                 v                v
      Auth              Tenancy           Ledger
        |                 |                |
        v                 v                v
     Frontend <-------- Payments <------ payment_verifications
         ^                  |
         |                  v
       Storage <-------- Logistics/Shipments
                          |
                          v
                        Marketplace
                          |
                          v
                        AI Hub
                          |
                          v
                    Monitoring & DevOps
```

(*) protected per README
