# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp

# 1. Init Spark
spark = SparkSession.builder \
    .appName("Ecommerce_ODS_to_DWD_ETL") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print("Spark Session started successfully!")

# 2. HDFS Paths (向下兼容老版本 Python)
HDFS_NN = "hdfs://namenode:9000"
ODS_USERS = HDFS_NN + "/user/root/ods/users/part-m-*"
ODS_ORDERS = HDFS_NN + "/user/root/ods/orders/part-m-*"

DWD_USERS = HDFS_NN + "/user/root/dwd/users"
DWD_ORDERS = HDFS_NN + "/user/root/dwd/orders"

# 3. Read ODS Data
print("Reading ODS data...")
users_df = spark.read.csv(ODS_USERS, inferSchema=True)
users_df = users_df.toDF("user_id", "name", "city", "reg_date")

orders_df = spark.read.csv(ODS_ORDERS, inferSchema=True)
orders_df = orders_df.toDF("order_id", "user_id", "product_category", "amount", "order_time")

# 4. Transform Data
print("Transforming data...")
users_cleaned = users_df.withColumn("reg_date", to_timestamp(col("reg_date")))
orders_cleaned = orders_df.withColumn("order_time", to_timestamp(col("order_time"))) \
                          .withColumn("amount", col("amount").cast("double"))

users_cleaned = users_cleaned.dropDuplicates(["user_id"])
orders_cleaned = orders_cleaned.dropDuplicates(["order_id"])

# 5. Write to DWD
print("Writing to DWD as Parquet...")
users_cleaned.write.mode("overwrite").parquet(DWD_USERS)
orders_cleaned.write.mode("overwrite").parquet(DWD_ORDERS)

print("ETL Job completed successfully!")
spark.stop()