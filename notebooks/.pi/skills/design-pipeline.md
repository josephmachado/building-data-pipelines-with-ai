---
name: design-pipeline
description: Use when the user wants to design or build a warehouse data pipeline from an existing dataset — i.e. they describe a dataset or output table they want and need help selecting source tables and generating an ETL/ETVL pipeline script. Guides an interactive, 
approval-gated flow: identify source tables and columns via the iceberg-mcp server, confirm the selection with the user, then generate a fact or dimension pipeline script from the base template and iterate with the user until approved.
---

# Warehouse Data Pipeline Design

**Input:** The user explains the dataset they want to build.

This skill runs as a two-stage, approval-gated process. Do not skip an approval gate — end your turn and wait for the user's response before moving on.

## 1. Identify inputs

- Use the user's description to determine which tables should serve as the source.
- Use the `iceberg-mcp` server to get the list of tables, their descriptions, and column descriptions. Use this metadata to decide which tables and columns are relevant to the request.
- Use the `iceberg-mcp` to get information about data size to estimate appropriate size per partition. This is to avoid too many small files or one large filer per partition. Use this information to determine if the data should be partitioned by hour, day, month, year.
- Present the selected tables back to the user for approval. In this summary, clearly indicate:
  - which table is the **main** table, and
  - which tables are **enrichment** tables or tables to be **inner joined**.
- **Wait for approval before moving to the next step.**

## 2. Create the ETVL script for the outputs

- Determine whether the table to be created is a **fact** or a **dimension** table.
- Use the code template at `/home/app/notebooks/base_table.py`.
- Follow the design patterns below to construct the pipeline script.
- Show the pipeline script to the user and **wait for approval**.
- Make changes as requested by the user. If a request conflicts with the design patterns below, inform the user of the conflict rather than silently applying it.

## Design Patterns: Fact & Dimension Tables

Reference for the extract, transform, quality-check, load, and optimization stages. Choose the row that matches the table type determined above.

### Fact tables

- **Extract:** Incremental extract, filtering with `inserted_at >= start_time AND inserted_at < end_time`. The start and end time are supplied by the scheduler (Airflow/Dagster).
- **Transform:**
  - *Standard enrichment:* `COALESCE(mapping_data, 'UNKNOWN')` combined with `LEFT JOIN` onto mapping tables.
  - *Advanced:* window functions, self joins, union, and except — used for (1) deduplication, (2) sessionization/attribution, and (3) multi-source fact data.
- **Quality check — Reconciliation:** `COUNT(*)` in the output vs `COUNT(*)` in the input.
- **Load:** Insert overwrite partition.
- **Optimization — Storage:** Partition by `day(created_at)`.
- **Optimization — Code:** Broadcast-join the mapping tables. Window functions and self joins reduce data shuffle when combined with SPJ (Storage-Partitioned Join) and partition pruning.

### Dimension tables

- **Extract:** Full table extract — `select * from source_tables`.
- **Transform:**
  - *Unknown incomplete data:* driver table + `INNER JOIN` the other tables.
  - *Known incomplete data:* driver table + `LEFT JOIN` the other tables.
  - *Slow complete data:* wait for all input tables to be complete.
- **Quality check:**
  - *Reconciliation:* `COUNT(*)` in the output vs `COUNT(*)` in the input.
  - *Table constraint checks:* uniqueness and completeness of the business natural key (for SCD2, use the natural key + `is_current`).
- **Load:** Overwrite the full table. For SCD2, use `MERGE INTO`.
- **Optimization — Storage:** Not needed (data < 10 mil).
- **Optimization — Code:** Not needed (data < 10 mil).

**Glossary:** SPJ = Storage-Partitioned Join. SCD2 = Slowly Changing Dimension Type 2. Scheduler = Airflow/Dagster.
