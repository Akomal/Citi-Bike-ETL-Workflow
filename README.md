#  Citi Bike Analytics Project

This project leverages Citi Bike’s open API data to drive insights to support business decisions for station placement and service planning.

This project answers following questions:
- Identify stations frequently full or empty, highlighting redistribution needs.
- Improve bike availability through smarter resource allocation.
- Determine which stations have the highest and lowest usage.


---

## Architecture

![Architecture Diagram](Untitled-Page-2.png)

This pipeline follows a **Bronze → Silver → Gold** data architecture pattern:

### Bronze Layer
- Extracts and loads raw Citi Bike data from the API.
- Stores raw JSON files in Google Cloud Storage (GCS).
- Performs JSON schema validation.

### Silver Layer
- Cleans and flattens raw JSON data using Pandas, handling timestamp formats, missing values, and data type conversions.
- Writes cleaned data to a GCS Silver bucket and loads it into a BigQuery staging table with additional derived columns like is_station_empty and is_station_full.
- Uses a MERGE operation to update the master BigQuery table with only new or changed records from the staging table.

### Gold Layer
- Aggregates and curates data for reporting and dashboarding.

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
├── plugins                   # Python scripts for ETL
├── schemas/                  # Schema definition files for BigQuery tables
├── terraform/                # Infrastructure configuration
├── data/                     # SQL for Silver (staging) and Gold (aggregation) layers
├── README.md                 # Project documentation

```

## Setup Instructions
1. Clone the repository
2. Add your GCP Service Account JSON key as a secret in your GitHub repository ( GCP_SA_KEY)
3. Install dependencies using Poetry
    ```
    poetry install
    ```
4. Modify variable values in the terraform files to match your GCP project, region, and desired bucket names
5. Pass bucket names and other runtime parameters to the DAGs 
6. Push the code to github and it will trigger a CI/CD workflow on master branch

