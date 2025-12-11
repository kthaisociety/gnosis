# Evaluation
Test the performance of VLMs on a dataset and visualise results.

# Setup
Add .env in eval/ root with connection string from NEON and URL to the Gateway API:
```
DATABASE_URL=
GATEWAY_URL=
```

# tree
```
.
├── app
│   ├── db.py
│   └── log.py
└── tests
    └── test_connection.py
```
