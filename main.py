from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, date_format
from pyspark.sql.types import *

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("KafkaStreamingExample") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1") \
    .config("spark.driver.extraClassPath", "C:/practice/spark/jars/sqljdbc42.jar") \
    .config("spark.executor.extraClassPath", "C:/practice/spark/jars/sqljdbc42.jar") \
    .getOrCreate()

# Define schema for the incoming Kafka messages using StructField
schema = StructType([
    StructField("sensor_id", StringType(), nullable=False),
    StructField("timestamp", TimestampType(), nullable=False),
    StructField("temperature", FloatType(), nullable=False),
    StructField("humidity", FloatType(), nullable=False)
])

# Read data from Kafka as a streaming DataFrame
kafka_stream_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "stream") \
    .load()

# Parse the value column (containing JSON data) and apply schema
parsed_stream_df = kafka_stream_df \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema).alias("data")) \
    .select("data.*")

# Apply transformations or processing on the streaming DataFrame
# For example, filter out data, perform aggregations, etc.
#Function to write the transformed data to MS SQL Server
def write_to_sql_server(df, epoch_id):
    df.write \
        .format("jdbc") \
        .option("url", "jdbc:sqlserver://localhost:1433;databaseName=stream") \
        .option("dbtable", "iot") \
        .option("user", "ganapati") \
        .option("password", "Ganapati@09") \
        .mode("append") \
        .save()

# Start the streaming query
query = parsed_stream_df \
    .writeStream \
    .foreachBatch(write_to_sql_server) \
    .start()
# query = parsed_stream_df \
#     .writeStream \
#    .outputMode("append") \
#     .format("console") \
#     .start()
# Wait for the termination of the query
query.awaitTermination()
