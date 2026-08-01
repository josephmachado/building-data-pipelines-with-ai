import argparse
import logging
from pathlib import Path

from pyspark.sql import SparkSession

logging.basicConfig(
    level=logging.WARN, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def run_ddl(data_path, spark, recreate=False):
    spark.sparkContext.setLogLevel("ERROR")
    if not recreate:
        return

    logger.info("Dropping any existing TPCH tables")
    spark.sql("CREATE SCHEMA IF NOT EXISTS prod")
    # Drop existing tables if they exist
    spark.sql("DROP TABLE IF EXISTS prod.customer")
    spark.sql("DROP TABLE IF EXISTS prod.lineitem")
    spark.sql("DROP TABLE IF EXISTS prod.nation")
    spark.sql("DROP TABLE IF EXISTS prod.orders")
    spark.sql("DROP TABLE IF EXISTS prod.part")
    spark.sql("DROP TABLE IF EXISTS prod.partsupp")
    spark.sql("DROP TABLE IF EXISTS prod.region")
    spark.sql("DROP TABLE IF EXISTS prod.supplier")
    spark.sql("DROP TABLE IF EXISTS prod.dim_date")

    logger.info("Creating TPCH Iceberg tables")
    # Create tables using Iceberg format
    spark.sql("""
    CREATE TABLE IF NOT EXISTS prod.customer (
      c_custkey    BIGINT,
      c_name       STRING,
      c_address    STRING,
      c_nationkey  BIGINT,
      c_phone      STRING,
      c_acctbal    DECIMAL(15,2),
      c_mktsegment STRING,
      c_comment    STRING
    ) USING iceberg
    TBLPROPERTIES (
      'format-version' = '2'
    )
    """)

    spark.sql("""
    CREATE TABLE IF NOT EXISTS prod.lineitem (
      l_orderkey      BIGINT,
      l_partkey       BIGINT,
      l_suppkey       BIGINT,
      l_linenumber    INT,
      l_quantity      DECIMAL(15,2),
      l_extendedprice DECIMAL(15,2),
      l_discount      DECIMAL(15,2),
      l_tax           DECIMAL(15,2),
      l_returnflag    STRING,
      l_linestatus    STRING,
      l_shipdate      DATE,
      l_commitdate    DATE,
      l_receiptdate   DATE,
      l_shipinstruct  STRING,
      l_shipmode      STRING,
      l_comment       STRING
    ) USING iceberg
    TBLPROPERTIES (
      'format-version' = '2'
    )
    """)

    spark.sql("""
    CREATE TABLE IF NOT EXISTS prod.nation (
      n_nationkey INT,
      n_name      STRING,
      n_regionkey INT,
      n_comment   STRING
    ) USING iceberg
    TBLPROPERTIES (
      'format-version' = '2'
    )
    """)

    spark.sql("""
    CREATE TABLE IF NOT EXISTS prod.orders (
      o_orderkey      BIGINT,
      o_custkey       BIGINT,
      o_orderstatus   STRING,
      o_totalprice    DECIMAL(15,2),
      o_orderdate     DATE,
      o_orderpriority STRING,
      o_clerk         STRING,
      o_shippriority  INT,
      o_comment       STRING
    ) USING iceberg
    TBLPROPERTIES (
      'format-version' = '2'
    )
    """)

    spark.sql("""
    CREATE TABLE IF NOT EXISTS prod.part (
      p_partkey     BIGINT,
      p_name        STRING,
      p_mfgr        STRING,
      p_brand       STRING,
      p_type        STRING,
      p_size        INT,
      p_container   STRING,
      p_retailprice DECIMAL(15,2),
      p_comment     STRING
    ) USING iceberg
    TBLPROPERTIES (
      'format-version' = '2'
    )
    """)

    spark.sql("""
    CREATE TABLE IF NOT EXISTS prod.partsupp (
      ps_partkey    BIGINT,
      ps_suppkey    BIGINT,
      ps_availqty   INT,
      ps_supplycost DECIMAL(15,2),
      ps_comment    STRING
    ) USING iceberg
    TBLPROPERTIES (
      'format-version' = '2'
    )
    """)

    spark.sql("""
    CREATE TABLE IF NOT EXISTS prod.region (
      r_regionkey INT,
      r_name      STRING,
      r_comment   STRING
    ) USING iceberg
    TBLPROPERTIES (
      'format-version' = '2'
    )
    """)

    spark.sql("""
    CREATE TABLE IF NOT EXISTS prod.supplier (
      s_suppkey   BIGINT,
      s_name      STRING,
      s_address   STRING,
      s_nationkey BIGINT,
      s_phone     STRING,
      s_acctbal   DECIMAL(15,2),
      s_comment   STRING
    ) USING iceberg
    TBLPROPERTIES (
      'format-version' = '2'
    )
    """)

    spark.sql("""
    CREATE TABLE IF NOT EXISTS prod.dim_date (
      date_key          BIGINT,
      full_date         DATE,
      year              INT,
      quarter           INT,
      quarter_name      STRING,
      month             INT,
      month_name        STRING,
      month_short       STRING,
      day_of_month      INT,
      day_of_year       INT,
      day_of_week       INT,
      day_name          STRING,
      day_short         STRING,
      week_of_year      INT,
      iso_week          INT,
      iso_year          INT,
      is_weekend        BOOLEAN,
      is_weekday        BOOLEAN,
      is_holiday        BOOLEAN,
      holiday_name      STRING,
      is_leap_year      BOOLEAN,
      first_day_of_month DATE
    ) USING iceberg
    PARTITIONED BY (year)
    TBLPROPERTIES (
      'format-version' = '2'
    )
    """)

    ##################### DATA FOR EXAMPLES ####################################

    spark.sql("drop table if exists prod.dim_mktsegment")
    spark.sql("""
        CREATE TABLE IF NOT EXISTS prod.dim_mktsegment (
          c_mktsegment        STRING,
          segment_description STRING,
          priority_tier       STRING
        ) USING iceberg
        TBLPROPERTIES (
          'format-version' = '2'
        )
        """)
    spark.sql("""
        INSERT INTO prod.dim_mktsegment VALUES
          ('MACHINERY',  'Industrial machinery and equipment buyers', 'High'),
          ('AUTOMOBILE', 'Automotive and vehicle-related customers',   'High'),
          ('BUILDING',   'Construction and building materials sector', 'Medium'),
          ('HOUSEHOLD',  'Household goods and consumer products',      'Medium')
        """)

    spark.sql("drop table if exists prod.customer_details")
    spark.sql("""
        CREATE TABLE IF NOT EXISTS prod.customer_details (
          customer_id  STRING,
          name         STRING,
          email        STRING,
          created_at   DATE,
          updated_at   DATE
        ) USING iceberg
        TBLPROPERTIES (
          'format-version' = '2'
        )
        """)

    spark.sql("""
        INSERT INTO prod.customer_details VALUES
          ('c1', 'customer_1_name', 'customer_1_email',    DATE '2026-01-01', DATE '2026-01-01'),
          ('c2', 'customer_2_name', 'customer_2_email',    DATE '2026-01-02', DATE '2026-01-02'),
          ('c3', 'customer_3_name', 'customer_3_email',    DATE '2026-01-02', DATE '2026-01-02'),
          ('c4', 'customer_4_name', 'customer_4_email',    DATE '2026-01-03', DATE '2026-01-03'),
          ('c1', 'customer_1_name', 'customer_1_email_v2', DATE '2026-01-01', DATE '2026-01-03')
        """)

    spark.sql("drop table if exists prod.customer_address")
    spark.sql("""
        CREATE TABLE IF NOT EXISTS prod.customer_address (
          customer_id  STRING,
          address      STRING,
          created_at   DATE,
          updated_at   DATE
        ) USING iceberg
        TBLPROPERTIES (
          'format-version' = '2'
        )
        """)

    spark.sql("""
        INSERT INTO prod.customer_address VALUES
          ('c1', 'customer_1_address', DATE '2026-01-01', DATE '2026-01-01'),
          ('c2', 'customer_2_address', DATE '2026-01-02', DATE '2026-01-02'),
          ('c3', 'customer_3_address', DATE '2026-01-02', DATE '2026-01-02'),
          ('c4', 'customer_4_address', DATE '2026-01-03', DATE '2026-01-03')
        """)

    ######################################################################################################

    def upsert_data(data_name, data_path=data_path):
        csv_path = data_path / f"{data_name}.csv"
        if data_name == "dim_date":
            csv_path = f"{data_name}.csv"
        logger.info(f"Reading {data_name} data from {str(csv_path)}")
        df = (
            spark.read.format("csv")
            .option("header", "true")
            .option("delimiter", ",")
            .option("inferSchema", "true")
            .load(str(csv_path))
        )
        df.writeTo(f"prod.{data_name}").createOrReplace()

    logger.info("Loading data into TPCH Iceberg tables")
    upsert_data("customer")
    upsert_data("lineitem")
    upsert_data("nation")
    upsert_data("orders")
    upsert_data("part")
    upsert_data("partsupp")
    upsert_data("region")
    upsert_data("supplier")
    upsert_data("dim_date")

    # customer
    spark.sql(
        "ALTER TABLE prod.customer ALTER COLUMN c_custkey COMMENT 'Customer primary key'"
    )
    spark.sql("ALTER TABLE prod.customer ALTER COLUMN c_name COMMENT 'Customer name'")
    spark.sql(
        "ALTER TABLE prod.customer ALTER COLUMN c_address COMMENT 'Customer street address'"
    )
    spark.sql(
        "ALTER TABLE prod.customer ALTER COLUMN c_nationkey COMMENT 'Foreign key to nation.n_nationkey'"
    )
    spark.sql(
        "ALTER TABLE prod.customer ALTER COLUMN c_phone COMMENT 'Customer phone number'"
    )
    spark.sql(
        "ALTER TABLE prod.customer ALTER COLUMN c_acctbal COMMENT 'Customer account balance'"
    )
    spark.sql(
        "ALTER TABLE prod.customer ALTER COLUMN c_mktsegment COMMENT 'Market segment the customer belongs to'"
    )
    spark.sql(
        "ALTER TABLE prod.customer ALTER COLUMN c_comment COMMENT 'General-purpose comment'"
    )

    # lineitem
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_orderkey COMMENT 'Foreign key to orders.o_orderkey'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_partkey COMMENT 'Foreign key to part.p_partkey'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_suppkey COMMENT 'Foreign key to supplier.s_suppkey'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_linenumber COMMENT 'Line number within the order'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_quantity COMMENT 'Quantity ordered'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_extendedprice COMMENT 'Extended price (quantity * part retail price)'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_discount COMMENT 'Discount rate applied to the line item'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_tax COMMENT 'Tax rate applied to the line item'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_returnflag COMMENT 'Return status flag'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_linestatus COMMENT 'Line item status'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_shipdate COMMENT 'Date the line item shipped'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_commitdate COMMENT 'Committed delivery date'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_receiptdate COMMENT 'Date the line item was received'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_shipinstruct COMMENT 'Shipping instructions'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_shipmode COMMENT 'Shipping mode'"
    )
    spark.sql(
        "ALTER TABLE prod.lineitem ALTER COLUMN l_comment COMMENT 'General-purpose comment'"
    )

    # nation
    spark.sql(
        "ALTER TABLE prod.nation ALTER COLUMN n_nationkey COMMENT 'Nation primary key'"
    )
    spark.sql("ALTER TABLE prod.nation ALTER COLUMN n_name COMMENT 'Nation name'")
    spark.sql(
        "ALTER TABLE prod.nation ALTER COLUMN n_regionkey COMMENT 'Foreign key to region.r_regionkey'"
    )
    spark.sql(
        "ALTER TABLE prod.nation ALTER COLUMN n_comment COMMENT 'General-purpose comment'"
    )

    # orders
    spark.sql(
        "ALTER TABLE prod.orders ALTER COLUMN o_orderkey COMMENT 'Order primary key'"
    )
    spark.sql(
        "ALTER TABLE prod.orders ALTER COLUMN o_custkey COMMENT 'Foreign key to customer.c_custkey'"
    )
    spark.sql(
        "ALTER TABLE prod.orders ALTER COLUMN o_orderstatus COMMENT 'Order status flag'"
    )
    spark.sql(
        "ALTER TABLE prod.orders ALTER COLUMN o_totalprice COMMENT 'Total price of the order'"
    )
    spark.sql(
        "ALTER TABLE prod.orders ALTER COLUMN o_orderdate COMMENT 'Date the order was placed'"
    )
    spark.sql(
        "ALTER TABLE prod.orders ALTER COLUMN o_orderpriority COMMENT 'Order priority level'"
    )
    spark.sql(
        "ALTER TABLE prod.orders ALTER COLUMN o_clerk COMMENT 'Clerk who handled the order'"
    )
    spark.sql(
        "ALTER TABLE prod.orders ALTER COLUMN o_shippriority COMMENT 'Shipping priority'"
    )
    spark.sql(
        "ALTER TABLE prod.orders ALTER COLUMN o_comment COMMENT 'General-purpose comment'"
    )

    # part
    spark.sql("ALTER TABLE prod.part ALTER COLUMN p_partkey COMMENT 'Part primary key'")
    spark.sql("ALTER TABLE prod.part ALTER COLUMN p_name COMMENT 'Part name'")
    spark.sql("ALTER TABLE prod.part ALTER COLUMN p_mfgr COMMENT 'Manufacturer'")
    spark.sql("ALTER TABLE prod.part ALTER COLUMN p_brand COMMENT 'Brand'")
    spark.sql("ALTER TABLE prod.part ALTER COLUMN p_type COMMENT 'Part type'")
    spark.sql("ALTER TABLE prod.part ALTER COLUMN p_size COMMENT 'Part size'")
    spark.sql("ALTER TABLE prod.part ALTER COLUMN p_container COMMENT 'Container type'")
    spark.sql("ALTER TABLE prod.part ALTER COLUMN p_retailprice COMMENT 'Retail price'")
    spark.sql(
        "ALTER TABLE prod.part ALTER COLUMN p_comment COMMENT 'General-purpose comment'"
    )

    # partsupp
    spark.sql(
        "ALTER TABLE prod.partsupp ALTER COLUMN ps_partkey COMMENT 'Foreign key to part.p_partkey'"
    )
    spark.sql(
        "ALTER TABLE prod.partsupp ALTER COLUMN ps_suppkey COMMENT 'Foreign key to supplier.s_suppkey'"
    )
    spark.sql(
        "ALTER TABLE prod.partsupp ALTER COLUMN ps_availqty COMMENT 'Available quantity from this supplier'"
    )
    spark.sql(
        "ALTER TABLE prod.partsupp ALTER COLUMN ps_supplycost COMMENT 'Cost to supply the part'"
    )
    spark.sql(
        "ALTER TABLE prod.partsupp ALTER COLUMN ps_comment COMMENT 'General-purpose comment'"
    )

    # region
    spark.sql(
        "ALTER TABLE prod.region ALTER COLUMN r_regionkey COMMENT 'Region primary key'"
    )
    spark.sql("ALTER TABLE prod.region ALTER COLUMN r_name COMMENT 'Region name'")
    spark.sql(
        "ALTER TABLE prod.region ALTER COLUMN r_comment COMMENT 'General-purpose comment'"
    )

    # supplier
    spark.sql(
        "ALTER TABLE prod.supplier ALTER COLUMN s_suppkey COMMENT 'Supplier primary key'"
    )
    spark.sql("ALTER TABLE prod.supplier ALTER COLUMN s_name COMMENT 'Supplier name'")
    spark.sql(
        "ALTER TABLE prod.supplier ALTER COLUMN s_address COMMENT 'Supplier street address'"
    )
    spark.sql(
        "ALTER TABLE prod.supplier ALTER COLUMN s_nationkey COMMENT 'Foreign key to nation.n_nationkey'"
    )
    spark.sql(
        "ALTER TABLE prod.supplier ALTER COLUMN s_phone COMMENT 'Supplier phone number'"
    )
    spark.sql(
        "ALTER TABLE prod.supplier ALTER COLUMN s_acctbal COMMENT 'Supplier account balance'"
    )
    spark.sql(
        "ALTER TABLE prod.supplier ALTER COLUMN s_comment COMMENT 'General-purpose comment'"
    )


if __name__ == "__main__":
    spark = SparkSession.builder.appName("run-ddl").master("local[*]").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    run_ddl(Path("./data"), spark, True)
