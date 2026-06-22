# 🚀 M-Pesa Safaricom Data Pipeline

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Apache Airflow](https://img.shields.io/badge/Airflow-Orchestration-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![License](https://img.shields.io/badge/License-MIT-green)

An end-to-end Data Engineering project that ingests, processes, stores, and analyzes **Safaricom M-Pesa transaction data** using modern data engineering practices. This pipeline demonstrates scalable ETL workflows, workflow orchestration, data quality validation, and analytics-ready storage. M-Pesa integrations commonly involve Daraja APIs and asynchronous callback processing. :contentReference[oaicite:0]{index=0}

---

## 📌 Overview

This project showcases a production-style data pipeline designed to:

- Extract M-Pesa transaction data
- Process and validate records
- Transform raw data into analytics-ready datasets
- Store structured data in a relational database
- Automate workflows and scheduling
- Monitor pipeline health and execution
- Generate business insights from transaction activity

---

## 🏗️ Architecture

```text
┌──────────────┐
│ M-Pesa API   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Data Ingest  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ ETL Process  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PostgreSQL   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Analytics    │
└──────────────┘
🛠️ Tech Stack
Data Engineering
Python
Pandas
SQL
Apache Airflow
Data Storage
PostgreSQL
CSV / JSON
Infrastructure
Docker
Docker Compose
Linux
Development
Git
GitHub
VS Code
Monitoring
Logging
Data Quality Checks
Pipeline Validation

mpesa_safaricom-pipeline/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── curated/
│
├── dags/
│   └── mpesa_pipeline.py
│
├── scripts/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
├── sql/
│   ├── schema.sql
│   └── queries.sql
│
├── logs/
│
├── docker/
│
├── tests/
│
├── requirements.txt
│
├── docker-compose.yml
│
└── README.md

⚙️ Features

✅ Automated ETL Pipeline

✅ Transaction Data Validation

✅ Data Quality Checks

✅ Workflow Orchestration

✅ Error Handling & Logging

✅ Scalable Architecture

✅ Analytics-Ready Data Models

✅ Containerized Deployment
🚀 Getting Started
Clone Repository
git clone https://github.com/Victor-Kipruto-Rop/mpesa_safaricom-pipeline.git

cd mpesa_safaricom-pipeline
Create Virtual Environment
python -m venv venv

source venv/bin/activate
Install Dependencies
pip install -r requirements.txt
Run Pipeline
python scripts/extract.py

python scripts/transform.py

python scripts/load.py
🐳 Docker Setup

Build containers:

docker-compose up --build

Run in detached mode:

docker-compose up -d
📊 Example Use Cases
Transaction Monitoring
Financial Analytics
Revenue Reporting
Fraud Detection Preparation
Customer Behavior Analysis
Data Warehousing
Real-Time Data Processing
🔒 Data Quality Checks

The pipeline includes:

Duplicate Detection
Null Value Validation
Schema Validation
Data Consistency Checks
Transaction Integrity Validation
📈 Future Enhancements
Kafka Streaming
Spark Processing
AWS Data Lake Integration
dbt Transformations
Grafana Monitoring
Real-Time Dashboards
Machine Learning Fraud Detection
🤝 Contributing

Contributions are welcome.

Fork the repository
Create a feature branch
git checkout -b feature/new-feature
Commit changes
git commit -m "Add new feature"
Push branch
git push origin feature/new-feature
Open a Pull Request
👨‍💻 Author
Victor Kipruto Rop

Data Engineer | Cloud & Analytics Enthusiast

GitHub: Victor Kipruto Rop GitHub
LinkedIn: Add your LinkedIn profile
⭐ Support

If you find this project useful:

⭐ Star the repository

🍴 Fork the project

📢 Share with others
