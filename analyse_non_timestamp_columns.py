from pyspark.sql.types import TimestampType
import pyspark.sql.functions as F

spark_df = spark.table("pre_prod_10_bronze.swift.dbo_s_agents")

# Drop all timestamp columns
ts_cols = [f.name for f in spark_df.schema.fields if isinstance(f.dataType, TimestampType)]
spark_df = spark_df.drop(*ts_cols)

df = spark_df.toPandas()

# Descriptive statistics for non-timestamp columns
print("=== Descriptive Statistics ===")
display(df.describe(include='all').astype(str))

# Distinct values for columns with fewer than 100 unique values
print("\n=== Distinct Values (columns with < 100 unique values) ===")
for col in df.columns:
    n_unique = df[col].nunique()
    if n_unique < 100:
        distinct_vals = df[col].dropna().unique().tolist()
        print(f"\n{col} ({n_unique} distinct values): {distinct_vals}")
