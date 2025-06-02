#  Citi Bike Analytics Project

This project leverages Citi Bike’s open API data to drive insights to spport business decisions for station placement and service planning.

This project answers following questions:
- Identify stations frequently full or empty, highlighting redistribution needs.
- Improve bike availability through smarter resource allocation.
- Determine which stations have the highest and lowest usage.


---

## Architecture

This pipeline follows a **Bronze → Silver → Gold** data architecture pattern:

### Bronze Layer
- Extracts and loads raw Citi Bike data from the API.
- Stores raw JSON files in Google Cloud Storage (GCS).
- Performs JSON schema validation.

### Silver Layer
- Transforms and enriches the data.
- Adds new columns and creates a master table in BigQuery.

### Gold Layer
- Aggregates and curates data for reporting and dashboarding.
- Provides analytical insights into fleet optimization and location performance.

---

## Technologies Used

| Tool             | Purpose                                |
|------------------|----------------------------------------|
| Python           | Data extraction, validation, transformation |
| Google Cloud Storage | Stores raw and intermediate data       |
| BigQuery         | Data warehousing and analytics          |
| Airflow/Composer | Orchestrates the data pipeline          |
| Terraform        | Infrastructure as Code (IaC)            |
| GitHub Actions   | CI/CD for deployment workflows          |

---

## Folder Structure

```bash
.
├── dags/                     # Airflow DAGs
├── plugins            # Python scripts for ETL
├── schemas/                  # schema filess for biqquery tables
├── terraform/                # Infrastructure configuration
├── data/            # SQL transformation logic
├── README.md                 # Project documentation
