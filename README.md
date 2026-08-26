# Digital Data Collection & Program Monitoring App

> An end-to-end information management system for collecting structured field data, validating and processing submissions, monitoring program performance, tracking data quality, and visualizing key indicators.


## Overview

The **Digital Data Collection & Program Monitoring System** is an end-to-end platform designed to support the collection, processing, validation, storage, monitoring, and visualization of structured program activity data.

Field officers collect activity records using digital forms built with **KoboToolbox/ODK**. Submitted records are retrieved through a REST API and processed by a Python-based data pipeline that performs validation, transformation, duplicate detection, and data quality checks before loading the processed data into **PostgreSQL**.

A SQL monitoring layer calculates program indicators and performance metrics. These metrics are exposed through a **FastAPI REST API** and visualized using **Power BI**.

The project demonstrates how different technologies can be combined into a complete information management workflow rather than operating as isolated tools.

---

## Problem Statement

Organizations running programs across multiple locations often need to answer questions such as:

* How many activities have been completed?
* How many beneficiaries have been reached?
* Are program targets being achieved?
* Which locations are underperforming?
* Are submitted records complete and valid?
* Which field submissions contain data quality issues?
* How does program performance change over time?

When data collection, storage, validation, and reporting are handled manually or through disconnected tools, generating reliable answers can become slow and error-prone.

This project addresses that problem by creating a structured data flow from **field data collection to monitoring and decision-making**.

---

# System Architecture

```text
                         FIELD DATA COLLECTION

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      Field Officer                          │
│                            │                                │
│                            ▼                                │
│                  KoboToolbox / ODK Form                     │
│                                                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ Form submissions
                             ▼

                    ┌────────────────────┐
                    │  KoboToolbox API   │
                    │       v2 API       │
                    └─────────┬──────────┘
                              │
                              │ JSON / REST API
                              ▼

┌─────────────────────────────────────────────────────────────┐
│                    PYTHON DATA PIPELINE                     │
│                                                             │
│   Extract → Validate → Transform → Quality Check → Load     │
│                                                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼

                    ┌────────────────────┐
                    │     PostgreSQL     │
                    │                    │
                    │  Raw Data          │
                    │  Processed Data    │
                    │  Quality Issues    │
                    │  ETL Logs          │
                    └─────────┬──────────┘
                              │
                              ▼

                    ┌────────────────────┐
                    │ SQL Monitoring     │
                    │ Layer              │
                    │                    │
                    │ Views              │
                    │ Indicators         │
                    │ Performance Metrics│
                    └─────────┬──────────┘
                              │
                  ┌───────────┴───────────┐
                  ▼                       ▼

        ┌──────────────────┐      ┌──────────────────┐
        │    FastAPI       │      │     Power BI     │
        │    REST API      │      │    Dashboard     │
        └──────────────────┘      └──────────────────┘
```

---

# Key Features

## Digital Field Data Collection

Structured program activity data is collected through KoboToolbox/ODK digital forms.

The form supports:

* Required fields
* Input validation
* Numeric constraints
* Conditional questions
* Skip logic
* Choice filtering
* GPS capture
* Standardized activity categories
* Structured geographic information

---

## Data Validation

The system performs validation at multiple stages.

### Form-Level Validation

Validation rules prevent invalid data from being submitted.

Examples include:

```text
Actual Participants ≥ 0
```

```text
Male Participants + Female Participants = Actual Participants
```

```text
Youth Participants + Adult Participants = Actual Participants
```

```text
Activity Date ≤ Current Date
```

---

## Python ETL Pipeline

Submitted records pass through a structured data pipeline.

```text
EXTRACT
   │
   ▼
VALIDATE
   │
   ├── Missing values
   ├── Invalid dates
   ├── Duplicate records
   ├── Invalid participant totals
   └── Invalid locations
   │
   ▼
TRANSFORM
   │
   ├── Standardize dates
   ├── Clean text fields
   ├── Convert data types
   ├── Map categories
   └── Prepare relational records
   │
   ▼
QUALITY CHECK
   │
   ├── Detect issues
   ├── Assign severity
   └── Log quality findings
   │
   ▼
LOAD
   │
   ▼
POSTGRESQL
```

---

# Data Quality Monitoring

Rather than silently discarding invalid records, the system records and monitors data quality issues.

Example quality checks include:

| Rule                 | Example Issue                                   |
| -------------------- | ----------------------------------------------- |
| Participant totals   | Male + Female does not equal Total Participants |
| Required fields      | Field Officer ID is missing                     |
| Activity date        | Activity date is in the future                  |
| Duplicate detection  | Submission already processed                    |
| Location validation  | GPS location missing                            |
| Data type validation | Participant count contains invalid value        |

Issues are stored for monitoring and analysis.

```text
data_quality_issues
│
├── id
├── submission_id
├── rule_name
├── issue_description
├── severity
├── status
└── detected_at
```

This allows the system to calculate a **Data Quality Score**:

```text
Valid Records
───────────── × 100
Total Records
```

---

# Program Monitoring

The system calculates program indicators from processed activity data.

## Example Indicators

### Activities Completed

```sql
COUNT(activities WHERE status = 'Completed')
```

### Target Achievement Rate

```text
Actual Participants
─────────────────── × 100
Target Participants
```

### Activity Completion Rate

```text
Completed Activities
──────────────────── × 100
Planned Activities
```

### Gender Distribution

```text
Female Participants
─────────────────── × 100
Total Participants
```

### Data Quality Score

```text
Valid Submissions
───────────────── × 100
Total Submissions
```

---

# Technology Stack

| Layer                 | Technology            |
| --------------------- | --------------------- |
| Field Data Collection | KoboToolbox / ODK     |
| Data Integration      | REST API / JSON       |
| Data Processing       | Python                |
| API Framework         | FastAPI               |
| Validation            | Pydantic              |
| Database              | PostgreSQL            |
| Data Access           | SQLAlchemy            |
| Data Transformation   | Python                |
| Monitoring Layer      | SQL Views and Queries |
| Data Visualization    | Power BI              |
| Containerization      | Docker                |
| Orchestration         | Docker Compose        |
| Testing               | Pytest                |
| CI                    | GitHub Actions        |

---

# Data Model

The system uses a relational database instead of storing all incoming submissions in a single table.

## Core Entities

```text
programs
locations
field_officers
activities
activity_participants
indicator_definitions
program_targets
raw_submissions
data_quality_issues
etl_runs
```

### Entity Relationship Overview

```text
PROGRAM
   │
   │ 1
   │
   └──────────────< ACTIVITIES >──────────── FIELD OFFICERS
                         │
                         │
                         ▼
                     LOCATIONS
                         │
                         │
                         ▼
                ACTIVITY PARTICIPANTS
```

The ingestion architecture follows a layered approach:

```text
Kobo Submission
       │
       ▼
Raw Submission Storage
       │
       ▼
Validation & Transformation
       │
       ▼
Normalized PostgreSQL Tables
       │
       ▼
Monitoring Views & Indicators
```

This separation preserves the original source data while providing clean, structured records for reporting and analysis.

---

# Project Structure

```text
digital-data-monitoring-system/
│
├── README.md
│
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   ├── api-documentation.md
│   ├── data-quality-rules.md
│   └── collection-workflow.md
│
├── kobo-form/
│   └── program_activity_monitoring.xlsx
│
├── backend/
│   ├── app/
│   │   │
│   │   ├── api/
│   │   │   ├── activities.py
│   │   │   ├── indicators.py
│   │   │   ├── performance.py
│   │   │   └── quality.py
│   │   │
│   │   ├── config/
│   │   │
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── models.py
│   │   │
│   │   ├── kobo/
│   │   │   └── client.py
│   │   │
│   │   ├── pipeline/
│   │   │   ├── extract.py
│   │   │   ├── validate.py
│   │   │   ├── transform.py
│   │   │   └── load.py
│   │   │
│   │   ├── services/
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── database/
│   ├── migrations/
│   ├── schema.sql
│   ├── views.sql
│   └── seed.sql
│
├── powerbi/
│   ├── dashboard.pbix
│   └── screenshots/
│
├── sample-data/
│
├── docker-compose.yml
│
└── .github/
    └── workflows/
        └── ci.yml
```

---

# Data Collection Workflow

The field data collection process follows this flow:

```text
Field Officer
      │
      ▼
Open Digital Form
      │
      ▼
Enter Activity Information
      │
      ▼
Capture Location
      │
      ▼
Enter Participant Information
      │
      ▼
Form-Level Validation
      │
      ▼
Submit Record
      │
      ▼
KoboToolbox Storage
      │
      ▼
Python Data Pipeline
      │
      ▼
PostgreSQL
```

---

# Example Activity Record

A simplified activity record may contain:

```json
{
  "program": "Community Development",
  "activity_type": "Training",
  "activity_title": "Digital Skills Training",
  "activity_date": "2026-08-20",
  "state": "Rivers",
  "lga": "Port Harcourt",
  "community": "Example Community",
  "target_participants": 100,
  "actual_participants": 92,
  "male_participants": 40,
  "female_participants": 52,
  "youth_participants": 70,
  "adult_participants": 22,
  "activity_status": "Completed"
}
```

---

# REST API

The processed monitoring data is exposed through a REST API.

## Activities

```http
GET /api/v1/activities
```

Retrieve activity records.

```http
GET /api/v1/activities/{id}
```

Retrieve a specific activity.

---

## Programs

```http
GET /api/v1/programs
```

Retrieve available programs.

---

## Indicators

```http
GET /api/v1/indicators
```

Retrieve calculated program indicators.

Example response:

```json
{
  "activities_completed": 84,
  "activities_planned": 100,
  "completion_rate": 84.0,
  "target_participants": 5000,
  "actual_participants": 4320,
  "target_achievement_rate": 86.4
}
```

---

## Performance

```http
GET /api/v1/performance
```

The endpoint supports filtering by program, location, activity type, and date range.

Example:

```text
GET /api/v1/performance?program=community-development&year=2026
```

---

## Data Quality

```http
GET /api/v1/data-quality
```

Returns data quality metrics and detected validation issues.

Example response:

```json
{
  "total_submissions": 1000,
  "valid_submissions": 945,
  "invalid_submissions": 55,
  "data_quality_score": 94.5
}
```

---

# Power BI Dashboard

The Power BI dashboard is designed around three main areas.

## 1. Executive Overview

Key metrics include:

* Total Activities
* Completed Activities
* Total Participants
* Target Achievement Rate
* Activity Completion Rate
* Data Quality Score

Example visualizations:

```text
Activities by Month
Activities by Location
Participants by Gender
Target vs Actual Performance
Program Performance Summary
```

---

## 2. Program Performance

The performance dashboard supports analysis using filters such as:

* Program
* Location
* Activity Type
* Date Range

Example visualizations:

```text
Target vs Actual Participants

Completion Rate by Program

Activities by Location

Monthly Performance Trends
```

---

## 3. Data Quality Dashboard

The data quality dashboard provides visibility into the reliability of collected data.

Metrics include:

```text
Total Submissions

Valid Records

Invalid Records

Data Quality Score

Issues by Validation Rule

Issues by Location

Issues Over Time
```

---

# Data Quality Rules

The pipeline validates records against defined business and quality rules.

Examples:

| Rule ID | Rule                                          | Severity |
| ------- | --------------------------------------------- | -------- |
| DQ001   | Actual participants cannot be negative        | High     |
| DQ002   | Male + Female must equal Actual Participants  | High     |
| DQ003   | Youth + Adults must equal Actual Participants | High     |
| DQ004   | Activity date cannot be in the future         | Medium   |
| DQ005   | GPS location is required                      | Medium   |
| DQ006   | Required fields cannot be empty               | High     |
| DQ007   | Duplicate submissions must be detected        | High     |

Quality issues are logged rather than silently ignored, allowing users to investigate recurring data problems.

---

# Local Development

## Prerequisites

Install the following:

* Python
* Docker
* Docker Compose
* PostgreSQL, if running without Docker
* Git

---

## Clone the Repository

```bash
git clone <your-repository-url>
cd digital-data-monitoring-system
```

---

## Configure Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/program_monitoring

KOBO_BASE_URL=your_kobo_instance_url
KOBO_API_TOKEN=your_kobo_api_token
KOBO_ASSET_UID=your_form_asset_uid

APP_ENV=development
LOG_LEVEL=INFO
```

> Never commit your `.env` file or API credentials to version control.

---

## Start the Application with Docker

```bash
docker compose up --build
```

This starts the required services, including:

```text
PostgreSQL
FastAPI Application
```

---

# Testing

The project includes automated testing for major system components.

```text
tests/
│
├── unit/
│   ├── test_validation.py
│   ├── test_transformation.py
│   └── test_indicators.py
│
├── integration/
│   ├── test_kobo_ingestion.py
│   ├── test_database_pipeline.py
│   └── test_api.py
│
└── fixtures/
```

Run the tests with:

```bash
pytest
```

Example areas covered by tests:

* Data validation rules
* Transformation logic
* Duplicate detection
* Database operations
* API responses
* Indicator calculations
* Data quality calculations

---

# CI/CD

GitHub Actions is used to automatically validate changes pushed to the repository.

The CI pipeline can perform:

```text
Code Checkout
      │
      ▼
Install Dependencies
      │
      ▼
Run Automated Tests
      │
      ▼
Run Code Quality Checks
      │
      ▼
Build Docker Images
      │
      ▼
Report Build Status
```

This helps ensure that changes are tested before being merged or deployed.

---

# Development Roadmap

## Phase 1 — Architecture and Foundation

* [x] Define project use case
* [x] Define high-level architecture
* [x] Define technology stack
* [x] Initialize repository
* [x] Configure Python environment
* [x] Configure Docker
* [x] Configure PostgreSQL

## Phase 2 — Digital Data Collection

* [x] Design XLSForm
* [x] Implement validation rules
* [x] Implement skip logic
* [x] Implement choice filtering
* [x] Add GPS capture
* [x] Deploy form
* [x] Submit test records

## Phase 3 — Database Design

* [x] Create ERD
* [x] Create PostgreSQL schema
* [x] Create raw submission table
* [x] Create normalized tables
* [x] Add constraints
* [x] Add indexes

## Phase 4 — Kobo API Integration

* [x] Configure API authentication
* [x] Retrieve submissions
* [x] Handle pagination
* [x] Store raw submissions
* [x] Add ingestion logging

## Phase 5 — ETL Pipeline

* [x] Build extraction layer
* [x] Build validation layer
* [x] Build transformation layer
* [x] Build loading layer
* [x] Implement error handling
* [x] Implement ETL logging

## Phase 6 — Data Quality Framework

* [x] Define validation rules
* [x] Detect duplicate records
* [x] Detect missing values
* [x] Log quality issues
* [x] Calculate quality metrics

## Phase 7 — SQL Monitoring Layer

* [ ] Create reporting views
* [ ] Create performance queries
* [ ] Calculate monitoring indicators
* [ ] Create summary tables

## Phase 8 — REST API

* [ ] Build FastAPI application
* [ ] Implement endpoints
* [ ] Add filtering
* [ ] Add request validation
* [ ] Add API tests
* [ ] Generate API documentation

## Phase 9 — Power BI Dashboard

* [ ] Build data model
* [ ] Create DAX measures
* [ ] Build executive dashboard
* [ ] Build program performance dashboard
* [ ] Build data quality dashboard

## Phase 10 — Testing and Documentation

* [ ] Unit testing
* [ ] Integration testing
* [ ] API testing
* [ ] Pipeline testing
* [ ] Architecture documentation
* [ ] Database documentation
* [ ] API documentation

## Phase 11 — Portfolio Polish

* [ ] Dockerize the application
* [ ] Add GitHub Actions CI
* [ ] Add sample data
* [ ] Add dashboard screenshots
* [ ] Improve documentation
* [ ] Prepare project demonstration

---

# Skills Demonstrated

This project demonstrates practical experience with:

### Information Management

* Structured data collection
* Data workflows
* Data validation
* Data quality monitoring
* Information system design

### Data Engineering

* REST API data extraction
* ETL pipelines
* Data transformation
* Raw-to-processed data architecture
* Database loading

### Database Development

* PostgreSQL
* Relational data modeling
* SQL queries
* Constraints
* Indexing
* Reporting views

### Backend Development

* Python
* FastAPI
* REST API design
* Request validation
* API documentation

### Data Analysis and Monitoring

* Performance indicators
* Target tracking
* Data quality metrics
* SQL monitoring views
* Power BI dashboards

### Software Engineering

* Docker
* Docker Compose
* Automated testing
* GitHub Actions
* Environment configuration
* Documentation

---

# Future Improvements

Potential future enhancements include:

* User authentication and role-based access control
* Scheduled ETL execution
* Background task processing
* Incremental synchronization
* Automated email notifications for data quality failures
* Geographic mapping and spatial analysis
* Program target management interface
* Web-based administration dashboard
* Audit logging
* Data export functionality
* API rate limiting
* Monitoring and observability

---

# Why This Project Matters

This project is designed as a realistic example of an end-to-end information management workflow.

Instead of treating data collection, databases, APIs, data processing, and dashboards as separate projects, it demonstrates how they work together:

```text
Collect Data
     │
     ▼
Validate Data
     │
     ▼
Store Raw Records
     │
     ▼
Transform and Clean
     │
     ▼
Detect Data Quality Issues
     │
     ▼
Store Structured Data
     │
     ▼
Calculate Indicators
     │
     ▼
Expose Data Through API
     │
     ▼
Visualize Performance
     │
     ▼
Support Better Decisions
```

The result is a complete data and information management system designed to demonstrate practical skills in **digital data collection, ETL processing, PostgreSQL, REST APIs, data quality management, monitoring, visualization, testing, and deployment**.

---

## Project Status

🚧 **Active Development**

The project is being developed incrementally, with each phase focusing on a production-oriented component of the overall information management pipeline.

---

## License

This project is intended for educational, learning, and portfolio purposes.
