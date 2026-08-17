# Dummy Data Generator

A modular, lightweight Python-based utility to generate synthetic, relational supply chain and transactional data. This generator is designed to create mock data specifically for **supply chain analytics**, **supply chain data engineering use cases**, and **supply chain visualization dashboards**. It automatically simulates realistic supply chain workflows, generating consistent relational data for materials, purchase orders (PO), order confirmations, inbound deliveries, and invoices based on constraints provided in configuration CSV files.

---

## Table of Contents
1. [Purpose & Overview](#purpose--overview)
2. [Data Pipeline Architecture](#data-pipeline-architecture)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [How to Run](#how-to-run)
6. [Detailed Module Documentation](#detailed-module-documentation)
    - [Material Generator (`material.py`)](#1-material-generator-materialpy)
    - [Purchase Order Schedule (`purchase_order_schedule.py`)](#2-purchase-order-schedule-purchase_order_schedulepy)
    - [PO Confirmation (`purchase_order_confirmation.py`)](#3-po-confirmation-purchase_order_confirmationpy)
    - [Inbound Delivery (`inbound_delivery.py`)](#4-inbound-delivery-inbound_deliverypy)
    - [Invoice Generator (`invoice.py`)](#5-invoice-generator-invoicepy)
7. [Inputs and Outputs Reference](#inputs-and-outputs-reference)

---

## Purpose & Overview

The primary goal of this tool is to generate realistic, relational dummy data designed to support critical supply chain workflows, testing, and training environments. This generator is engineered to **mimic standard SAP supply chain data structures**, ensuring high compatibility for testing real-world ERP scenarios. Specifically, the generated datasets can be utilized for:

*   **Supply Chain Analytics**: Build and test analytic models tracking vendor performance (OTIF - On Time In Full), lead times, order fulfillment rates, average monthly usage (AMU), price fluctuations, and safety stock optimizations.
*   **Supply Chain Data Engineering**: Design robust data pipelines, orchestrate ETL/ELT flows, practice relational database modeling, and create streaming or batch data ingestion pipelines using realistic transactional hierarchies.
*   **Supply Chain Visualization**: Populate business intelligence (BI) tools (e.g., Tableau, PowerBI) and web visualization dashboards with lifelike tracking numbers, Gantt charts for delivery timelines, and multi-stage process flows (Order ➔ Confirmation ➔ Inbound Delivery ➔ Invoice).
*   **GCS Integration**: Automatically upload generated datasets to Google Cloud Storage for downstream consumption in cloud-based data warehouses or analysis pipelines.

By starting with high-level constraints (e.g., how many lines are shared or how many invoices are expected per vendor), the generators cascade this configuration down to simulate complex timing relationships, randomized batch sizes, standard supply chain calculations, and transactional tracking numbers.

---

## Data Pipeline Architecture

The generators run sequentially, feeding downstream scripts with previously generated outputs to preserve relational integrity (e.g., an inbound delivery or invoice must reference an active, valid PO line and respect realistic date offsets):

```
+---------------------------------------------------------------------------------+
|                                 Data Pipeline                                   |
+---------------------------------------------------------------------------------+
                                  
 [ material_data.csv ] --------> ( material.py ) --------> [ plant_material.csv ]
 
 [ po_schedule_data.csv ] -----> ( purchase_order_schedule.py ) 
                                            |
                                            v
                                   [ po_schedule.csv ] <-------+
                                            |                  |
   [ po_confirmation_data.csv ]             |                  |
               |                            v                  |
               +--------------> ( purchase_order_confirmation.py )   |
                                            |                  |
                                            v                  |
                                  [ po_confirmation.csv ]      |
                                            |                  |
   [ inbound_delivery_data.csv ]            |                  |
               |                            v                  |
               +--------------> ( inbound_delivery.py )        |
                                            |                  |
                                            v                  |
                                  [ inbound_delivery.csv ]     |
                                                               |
   [ invoice_data.csv ] ---------------------------------------+
               |                                               |
               +---------------------> ( invoice.py ) <--------+
                                            |
                                            v
                                     [ invoice.csv ]
```

---

## Project Structure

```
supply-chain-dummy-data-generator/
├── main.py                          # Orchestrates and runs the transactional pipeline sequentially
├── material.py                      # Standalone generator for plant-material master data
├── purchase_order_schedule.py       # Simulates purchase orders (POs) and scheduling
├── purchase_order_confirmation.py   # Simulates vendor confirmation data (ORDRSP)
├── inbound_delivery.py              # Simulates inbound delivery/advance shipping notices (DESADV)
├── invoice.py                       # Simulates vendor billing and invoices
├── requirements/                    # Input CSV files specifying the targets and boundaries
│   ├── material_data.csv
│   ├── po_schedule_data.csv
│   ├── po_confirmation_data.csv
│   ├── inbound_delivery_data.csv
│   └── invoice_data.csv
└── output/                          # Target directory for the generated relational CSVs
    ├── plant_material.csv
    ├── po_schedule.csv
    ├── po_confirmation.csv
    ├── inbound_delivery.csv
    └── invoice.csv
```

---

## Prerequisites

*   **Python 3.6** or higher.
*   No external dependencies are required. The project relies strictly on Python standard libraries (`csv`, `random`, `datetime`, `collections`).

---

## How to Run

### 1. Run the Transactional Pipeline
To generate the transactional flow (`po_schedule` ➔ `po_confirmation` ➔ `inbound_delivery` ➔ `invoice`) in sequence and upload the results to the configured GCS bucket, execute:

```bash
python3 main.py
```

### 2. Run the Material Master Generator
Since material master data operates independently of transactional flow, run the material generator as a separate process:

```bash
python3 material.py
```

All generated output files will be saved directly in the `output/` directory.

---

## Detailed Module Documentation

### 1. Material Generator (`material.py`)
Generates master materials per ERP and manufacturing plant based on the specified quantity constraints.

*   **Logic**:
    *   Groups requirements by `ERP`.
    *   Generates a total number of materials matching `NBR MATERIALS` per plant.
    *   Material code format: `A` followed by an 11-digit zero-padded number (e.g., `A00000234121`).
    *   Assigns a randomized standard batch sizing factor (`5`, `10`, `20`, `50`, or `100`).
    *   Calculates realistic operational parameters:
        *   **MOQ (Minimum Order Quantity)**: `random(10, 400) * factor`
        *   **SPQ (Standard Packing Quantity)**: `MOQ // factor`
        *   **Lead Time**: Random integer between `7` and `365` days.
        *   **Safety Stock**: `MOQ * random(1, 10)`
        *   **Unit Price**: Random pricing scale (divided by 1000 and rounded to 6 decimal places).
        *   **AMU (Average Monthly Usage)**: `MOQ * random(1, 10)`

### 2. Purchase Order Schedule (`purchase_order_schedule.py`)
Generates purchase orders starting from a vendor's initial start date.

*   **Logic**:
    *   Reads `po_schedule_data.csv` to fetch target lines per ERP/Plant/Vendor group.
    *   Generates PO numbers starting with `5` (e.g., `500001234`).
    *   Splits total lines into individual POs containing a random number of line items (up to 99 items per PO).
    *   Calculates two different dates per line item:
        *   **Contractual Delivery Date**: `Creation Date (Orders date) + random(7 to 365) days`.
        *   **Requested Delivery Date**: Simulates order delivery variation. Either matches the Contractual Delivery Date directly, or shifts it forward/backward by an offset of `10` to `30` days.

### 3. PO Confirmation (`purchase_order_confirmation.py`)
Simulates vendor acknowledgment (ORDRSP) for a subset of the generated PO lines.

*   **Logic**:
    *   Reads the active PO schedule from `output/po_schedule.csv`.
    *   Selects a random sample of lines matching `PO LINES ACKED` per ERP and Vendor combination.
    *   Calculates the dates:
        *   **PO Confirmation Date**: `Requested Delivery Date` shifted forward or backward by a random offset of `5` to `10` days.
        *   **Confirmation Enter Date**: `ORDRSP` date (from requirements) shifted forward by a random offset of `1` to `20` days.

### 4. Inbound Delivery (`inbound_delivery.py`)
Simulates physical shipping notices (DESADV) and inbound tracking information for confirmed POs.

*   **Logic**:
    *   Reads the confirmed PO schedule from `output/po_confirmation.csv`.
    *   Selects a random sample of lines matching `ASN CREATED` per ERP and Vendor combination.
    *   Generates a unique inbound tracking code format: `D` followed by a 12-digit code (`random 4-digit prefix` + `last 4 digits of PO number` + `PO Item` zero-padded).
    *   Calculates delivery timelines:
        *   **Inbound Delivery Date**: `PO Confirmation Date` shifted forward or backward by `5` to `10` days.
        *   **Inbound Creation Date**: `DESADV` date (from requirements) shifted forward by a random offset of `1` to `20` days.

### 5. Invoice Generator (`invoice.py`)
Generates billing invoices mapping to existing purchase orders.

*   **Logic**:
    *   Fetches the required `INVOICE CREATED` count per ERP and Vendor.
    *   Generates the specified number of unique invoice tracking numbers formatted as `INV<5-digit-random-number><counter>`.
    *   Applies a random distribution pattern to map these invoice numbers to all PO lines corresponding to that ERP and Vendor group.

---

## Inputs and Outputs Reference

### Directory: `requirements/` (Configuration & Inputs)

| File Name | Primary Headers | Description |
| :--- | :--- | :--- |
| `material_data.csv` | `ERP`, `PLANT`, `NBR MATERIALS` | Dictates number of materials to produce per plant. |
| `po_schedule_data.csv` | `ERP`, `PLANT`, `VENDOR`, `ORDERS`, `PO LINES SHARED` | Base schedule config + initial order start dates. |
| `po_confirmation_data.csv`| `ERP`, `VENDOR`, `ORDRSP`, `PO LINES ACKED` | Target lines to confirm and base acknowledgment dates. |
| `inbound_delivery_data.csv`| `ERP`, `VENDOR`, `DESADV`, `ASN CREATED` | Target delivery numbers and initial advice dates. |
| `invoice_data.csv` | `ERP`, `VENDOR`, `INVOIC`, `INVOICE CREATED` | Number of invoice sheets to generate and post dates. |

### Directory: `output/` (Generated Results)

| File Name | Key Output Fields | Generated By |
| :--- | :--- | :--- |
| `plant_material.csv` | `ERP`, `PLANT`, `MATERIAL CODE`, `MOQ`, `SPQ`, `LEAD TIME`, `SAFETY STOCK`, `UNIT PRICE USD`, `AMU` | `material.py` |
| `po_schedule.csv` | `ERP`, `PLANT`, `VENDOR`, `PO NUMBER`, `PO ITEM`, `CREATION DATE`, `CONTRACTUAL DELIVERY DATE`, `REQUESTED DELIVERY DATE` | `purchase_order_schedule.py`|
| `po_confirmation.csv` | `ERP`, `VENDOR`, `PO NUMBER`, `PO ITEM`, `PO CONFIRMATION DATE`, `CONFIRMATION ENTER DATE` | `purchase_order_confirmation.py`|
| `inbound_delivery.csv` | `ERP`, `VENDOR`, `PO NUMBER`, `PO ITEM`, `INBOUND DELIVERY NUMBER`, `INBOUND DELIVERY DATE`, `INBOUND CREATION DATE` | `inbound_delivery.py` |
| `invoice.csv` | `ERP`, `VENDOR`, `INVOICE NUMBER`, `PO NUMBER`, `PO ITEM`, `INVOICE DATE` | `invoice.py` |
