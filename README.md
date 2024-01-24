# scrapper_zameen

The scrapper_zameen is a Python-based web scraping and database interaction application that automates the collection of data from `zameen.com` and stores it in a PostgreSQL database.

## Table of Contents

1. [Modules](#modules)
   - [cronjob.py](#cronjobpy)
   - [scrap.py](#scrappy)
   - [init_db.py](#init_dbpy)
2. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
3. [Usage](#usage)
   - [Running with Docker](#running-with-docker)
4. [Contributing](#contributing)
5. [License](#license)

## Modules

### cronjob.py

The `cronjob.py` module is responsible for scheduling a cron job to run at a specific time daily. This job triggers the execution of another script called `scrap.py`.

### scrap.py

The `scrap.py` module is designed to scrape a specific website. It calls methods from the `init_db` module to store the scraped data into a PostgreSQL database.

### init_db.py

The `init_db.py` module handles all operations related to the database. It includes methods for initializing the database, storing data, and any other database-related tasks.

## Getting Started

### Prerequisites

- Python (version 3.10)
- Docker
- Docker Compose

### Installation

1. Clone the repository.
2. ~~Install the required Python dependencies: `pip install -r requirements.txt`~~
3. ~~Install Playwright: `pip install playwright && playwright install`~~
4. ~~Install Playwright dependencies (if required): `playwright install-deps`~~
5. Create `.env` file using example from `.env.example` in root folder.
6. ~~Setup Postgres Database~~

## Usage

### Running with Docker

To run the entire application using Docker, execute the following command in the project root directory:

```bash
sudo docker-compose up -d
```
