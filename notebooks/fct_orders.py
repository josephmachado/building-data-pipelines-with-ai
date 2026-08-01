import argparse

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

TABLE_NAME = "local.silver.fct_orders"

def extract(
    spark: SparkSession,
    start_time: str,
    end_time: str,
) -> dict[str, DataFrame]:
    orders_df = spark.sql(f"""
    SELECT * 
    FROM prod.db.orders
    WHERE o_orderdate >= '{start_time}'
    AND o_orderdate < '{end_time}'
    """)

    dim_date_df = spark.sql(f"""
    SELECT * 
    FROM prod.db.dim_date
    """)

    return {"orders": orders_df, "dim_date": dim_date_df}


def transform(spark, input_dfs: dict[str, DataFrame]) -> DataFrame:
    input_dfs['orders'].createOrReplaceTempView('orders')
    input_dfs['dim_date'].createOrReplaceTempView('dim_date')
    return spark.sql("""
        SELECT
          o.o_orderkey,
          o.o_custkey,
          o.o_orderstatus,
          o.o_totalprice,
          o.o_orderdate,
          o.o_orderpriority,
          o.o_clerk,
          o.o_shippriority,
          o.o_comment,
          d.date_key,
          d.year,
          d.quarter,
          d.quarter_name,
          d.month,
          d.month_name,
          d.day_of_month,
          d.day_name,
          d.week_of_year,
          d.iso_week,
          d.is_weekend,
          d.is_holiday,
          d.holiday_name
        FROM orders o
        LEFT JOIN dim_date d
          ON o.o_orderdate = d.full_date
    """)


def load(output_df: DataFrame, spark: SparkSession) -> None:

    if not spark.catalog.tableExists(TABLE_NAME):
        (
            output_df.writeTo(TABLE_NAME)
            .partitionedBy(F.partitioning.days("o_orderdate"))
            .createOrReplace()
        )
    else:
        output_df.writeTo(TABLE_NAME).overwritePartitions()


def run(spark: SparkSession, start_time: str, end_time: str) -> None:
    load(transform(spark, extract(spark, start_time, end_time)), spark)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"{TABLE_NAME} ETL")
    parser.add_argument(
        "--start-time",
        required=True,
        help="Start time (inclusive), format: YYYY-MM-DD HH:MM:SS",
    )
    parser.add_argument(
        "--end-time",
        required=True,
        help="End time (exclusive), format: YYYY-MM-DD HH:MM:SS",
    )
    args = parser.parse_args()

    spark = SparkSession.builder.appName(TABLE_NAME).master("local[*]").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    run(spark, args.start_time, args.end_time)