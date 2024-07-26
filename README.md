# NYU DevOps Project - Shopcarts

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build Status](https://github.com/CSCI-GA-2820-SU24-001/shopcarts/actions/workflows/tdd-tests.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU24-001/shopcarts/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU24-001/shopcarts/graph/badge.svg?token=ML2KBQH422)](https://codecov.io/gh/CSCI-GA-2820-SU24-001/shopcarts)

## Overview

This project implements the shopcarts service, which allows customers to make a collection of products they want to purchase. The service includes a REST API that provides CRUD operations for managing shopcarts and the items within them.

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.gitattributes      - File to gix Windows CRLF issues

.devcontainers/     - Folder with support for VSCode Remote Containers
.tekton/            - Tekton CI/CD pipeline files
k8s/                - Kubernetes deployment files
Dockerfile          - Docker configuration file

dot-env-example     - copy to .env to use environment variables
.flaskenv           - Environment variables to configure Flask
pyproject.toml      - Poetry list of Python libraries required
wsgi.py             - WSGI entry point for the application

thunder/            - Thunder Client collection for testing APIs

features/                  - BDD features package
├── steps                  - step definitions for BDD
│   ├── shopcart_steps.py  - BDD steps for shopcarts
│   ├── web_steps.py       - BDD steps for web interactions
├── environment.py         - BDD environment setup
└── shopcart.feature       - BDD feature file

service/                        - service python package
├── __init__.py                 - package initializer
├── config.py                   - configuration parameters
├── routes.py                   - module with service routes
├── common                      - common code package
│   ├── cli_commands.py         - Flask command to recreate all tables
│   ├── error_handlers.py       - HTTP error handling code
│   ├── log_handlers.py         - logging setup code
│   └── status.py               - HTTP status constants
│── models                      - models package
│   ├── __init__.py             - package initializer
│   ├── persistent_base.py      - base class for persistence
│   ├── shopcart_item.py        - model for shopcart items
│   └── shopcart.py             - model for shopcarts
└── static                      - static files package
    ├── css                     - CSS files
    ├── images                  - Image files
    ├── js                      - JavaScript files
    │   ├── bootstrap.min.js    - Bootstrap library for responsive design
    │   ├── jquery-3.6.0.min.js - jQuery library for simplified JavaScript operations
    │   └── rest_api.js         - JavaScript file for interacting with the REST API
    └── index.html              - Main HTML file for the web interface

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_shopcart.py       - test suite for shopcart model
├── test_shopcart_item.py  - test suite for shopcart item model
└── test_routes.py         - test suite for service routes
```

## API Endpoints

The shopcarts service provides the following API endpoints:

| Operation                         | Method | URL                                          |
|-----------------------------------|--------|----------------------------------------------|
| **Create a new shopcart**         | POST   | `/shopcarts`                                 |
| **Get a shopcart**                | GET    | `/shopcarts/{shopcart_id}`                   |
| **List all shopcarts**            | GET    | `/shopcarts`                                 |
| **Update a shopcart**             | PUT    | `/shopcarts/{shopcart_id}`                   |
| **Delete a shopcart**             | DELETE | `/shopcarts/{shopcart_id}`                   |
| **Add an item to a shopcart**     | POST   | `/shopcarts/{shopcart_id}/items`             |
| **Get an item from a shopcart**   | GET    | `/shopcarts/{shopcart_id}/items/{item_id}`   |
| **List all items in a shopcart**  | GET    | `/shopcarts/{shopcart_id}/items`             |
| **Update a shopcart item**        | PUT    | `/shopcarts/{shopcart_id}/items/{item_id}`   |
| **Delete a shopcart item**        | DELETE | `/shopcarts/{shopcart_id}/items/{item_id}`   |
| **Delete all items in a shopcart**| DELETE | `/shopcarts/{shopcart_id}/items`             |
| **Query shopcarts**               | GET    | `/shopcarts?product_id={product_id}&name={name}` |
| **Query item**                    | GET    | `/shopcarts/{shopcart_id}/items?product_id={product_id}&name={name}` |
| **Checkout a shopcart**           | GET    | `/checkout`                                  |

## Running the Tests

To run the tests for this project, you can use the following command:

```bash
make test
```

This command will run the test suite using `pytest` and ensure that all the tests pass.

## Running the Service Locally

To run the shopcarts service locally, you can use the following command:

```bash
honcho start
```

The service will start and be accessible at `http://localhost:8080`.

## Deploy on Kubernetes Locally

To deploy the shopcarts service on Kubernetes locally, follow these steps:

* Create a Kubernetes cluster:

```bash
make cluster
```

* Build the Docker image:

```bash
docker build -t shopcarts:latest .
```

* Tag the Docker image:

```bash
docker tag shopcarts:latest cluster-registry:5000/shopcarts:latest
```

* Push the Docker image to the cluster registry:

```bash
docker push cluster-registry:5000/shopcarts:latest
```

* Apply the Kubernetes configurations:

```bash
kc apply -f k8s/
```

The service will start and be accessible at `http://localhost:8080`.

## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.