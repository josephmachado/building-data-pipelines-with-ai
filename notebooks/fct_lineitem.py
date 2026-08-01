from pyspark.sql import DataFrame, SparkSession
import pyspark.sql.functions as F
import argparse

TABLE_NAME = "silver.fct_lineitem"


def extract(
    spark: SparkSession,
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict[str, DataFrame]:
    lineitem_df = spark.sql(f"""
        SELECT * FROM prod.lineitem
        WHERE l_shipdate >= '{start_time}' AND l_shipdate < '{end_time}'
    """)

    dim_date_df = spark.table("prod.dim_date")

    return {
        "lineitem": lineitem_df,
        "dim_date": dim_date_df,
    }


def transform(spark: SparkSession, input_dfs: dict[str, DataFrame]) -> DataFrame:
    input_dfs["lineitem"].createOrReplaceTempView("lineitem")
    input_dfs["dim_date"].createOrReplaceTempView("dim_date")

    transformed_df = spark.sql("""
        SELECT
            l.l_orderkey,
            l.l_partkey,
            l.l_suppkey,
            l.l_linenumber,
            l.l_quantity,
            l.l_extendedprice,
            l.l_discount,
            l.l_tax,
            l.l_returnflag,
            l.l_linestatus,
            l.l_shipdate,
            l.l_commitdate,
            l.l_receiptdate,
            l.l_shipinstruct,
            l.l_shipmode,
            l.l_comment,

            l.l_extendedprice * (1 - l.l_discount) AS extended_price_with_discount,
            l.l_extendedprice * (1 - l.l_discount) * (1 + l.l_tax) AS extended_price_with_discount_and_tax,

            COALESCE(d.date_key, 0) AS d_date_key,
            COALESCE(d.year, 0) AS d_year,
            COALESCE(d.quarter, 0) AS d_quarter,
            COALESCE(d.month, 0) AS d_month,
            COALESCE(d.month_name, 'UNKNOWN') AS d_month_name,
            COALESCE(d.day_of_month, 0) AS d_day_of_month,
            COALESCE(d.day_of_week, 0) AS d_day_of_week,
            COALESCE(d.day_name, 'UNKNOWN') AS d_day_name,
            COALESCE(d.week_of_year, 0) AS d_week_of_year,
            COALESCE(d.is_weekend, FALSE) AS d_is_weekend,
            COALESCE(d.is_holiday, FALSE) AS d_is_holiday,
            COALESCE(d.holiday_name, 'UNKNOWN') AS d_holiday_name

        FROM lineitem l
        LEFT JOIN dim_date d ON l.l_shipdate = d.full_date
    """)

    transformed_df.createOrReplaceTempView("transformed")
    return transformed_df


def validate(transformed_df: DataFrame) -> bool:
    spark = transformed_df.sparkSession

    input_count = spark.table("lineitem").count()
    output_count = transformed_df.count()
    if input_count != output_count:
        print(f"Reconciliation failed: input={input_count}, output={output_count}")
        return False

    nulls = spark.sql("""
        SELECT 1 FROM transformed
        WHERE extended_price_with_discount IS NULL
           OR extended_price_with_discount_and_tax IS NULL
        LIMIT 1
    """)
    if nulls.count() > 0:
        print("Null check failed on computed columns")
        return False

    return True


def load(transformed_validated_df: DataFrame, spark: SparkSession) -> None:
    if not spark.catalog.tableExists(TABLE_NAME):
        (
            transformed_validated_df.writeTo(TABLE_NAME)
            .partitionedBy(F.partitioning.years("l_shipdate"))
            .createOrReplace()
        )
    else:
        transformed_validated_df.writeTo(TABLE_NAME).overwritePartitions()


def run(spark: SparkSession, start_time: str, end_time: str) -> None:
    transformed_df = transform(spark, extract(spark, start_time, end_time))
    if not validate(transformed_df):
        raise ValueError("DQ checks failed")
    load(transformed_df, spark)


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
