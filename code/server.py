# server.py
from mcp.server.mcpserver import MCPServer, Context
from pyspark.sql import SparkSession

mcp = MCPServer("iceberg-mcp")

# Build one SparkSession, reused across tool calls.
spark = SparkSession.builder.appName("iceberg-mcp").master("local[1]").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")


def _show(df) -> str:
    """Render a Spark DataFrame the way .show() does, but as a returnable string."""
    return df._jdf.showString(1000, 0, False)


@mcp.tool()
def list_schemas() -> str:
    """List all schemas (databases) available in the catalog."""
    return _show(spark.sql("SHOW SCHEMAS"))


@mcp.tool()
def list_tables(schema: str) -> str:
    """List all tables in a given schema. Example: schema='bronze'."""
    return _show(spark.sql(f"SHOW TABLES IN {schema}"))


@mcp.tool()
def describe_table(schema: str, table: str) -> str:
    """Show extended details (columns, types, properties, location) for a table.
    Example: schema='bronze', table='customer'."""
    return _show(spark.sql(f"DESCRIBE EXTENDED {schema}.{table}"))


if __name__ == "__main__":
    mcp.run()

