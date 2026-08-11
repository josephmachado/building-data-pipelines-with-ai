from pyspark.sql import DataFrame, SparkSession

TABLE_NAME = "fully_qualified.table_name"


def extract(
    spark: SparkSession,
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict[str, DataFrame]:
    """Function to extract data from source tables.

    Args:
        spark: SparkSession to access the source tables
        start_time: Optional start time (string timestamp) for incremental pulls
        end_time: Optional end time (string timestamp) for incremental pulls

    Returns: A dict with table_name -> Spark dataframe of that table
    """
    pass


def transform(spark: SparkSession, input_dfs: dict[str, DataFrame]) -> DataFrame:
    """Function to transform input spark dataframes into output.
    This function represents the crux of transformation

    Args:
        spark: SparkSession to transform data, used when converting df to temp views/tables for SQL transformation
        input_dfs: The dict of table_name -> Spark dataframe from extract function

    Returns: The transformed dataframe ready to be quality checked

    """
    pass


def validate(transformed_df: DataFrame) -> bool:
    """Function that validates that the transformed_df passed data quality checks.
    Data quality checks written as SQL that returns >1 rows if failed.

    Args:
        transformed_df: The data frame to be quality checked

    Returns: True or false depending on if the dataframe passed DQ checks or not

    """
    pass


def load(transformed_validated_df: DataFrame, spark: SparkSession) -> None:
    """Function that creates or loads data into the destination table

    It generally follows the pattern below for incremental tables. Note that the
    partitioning is decided per table

    ```
        if not spark.catalog.tableExists(TABLE_NAME):
        (
            output_df.writeTo(TABLE_NAME)
            .partitionedBy(F.partitioning.days("o_orderdate"))
            .createOrReplace()
        )
    else:
        output_df.writeTo(TABLE_NAME).overwritePartitions()
    ````

    For full snapshot tables, the following pattern is used.

    ```
    output_df.writeTo(TABLE_NAME).createOrReplace()
    ```

    Args:
        transformed_validated_df: The dataframe that has been DQ checked and to be loaded into the destination
        spark: Spark session to check if table already exists
    """
    pass


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
