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

no_values = []
limited_values = []
many_values = []

for col in df.columns:
    n_unique = df[col].nunique()
    if n_unique == 0:
        #print(f"\n{col} ({n_unique} distinct values): No values")
        no_values.append({'attribute':col,'distinct_values':n_unique})
    
    elif 0 < n_unique < 100:
        distinct_vals = df[col].dropna().unique().tolist()
        limited_values.append({'attribute':col,'distinct_values':n_unique,'distinct_values_list':distinct_vals})
        #print(f"\n{col} ({n_unique} distinct values): {distinct_vals}")
    
    else:
        #print(f"\n{col} ({n_unique} distinct values): Too many to display")
        many_values.append({'attribute':col,'distinct_values':n_unique})

print("\n=== No Value Columns (columns with 0 unique values) ===")
for val in no_values:
    print(f"\n{val['attribute']} ({val['distinct_values']} distinct values): No values")

print("\n=== Limited Value Columns (columns with fewer than 100 unique values) ===")
for val in limited_values:
    print(f"\n{val['attribute']} ({val['distinct_values']} distinct values):{val['distinct_values_list']}")

print("\n=== Many Value Columns (columns with more than 100 unique values) ===")
for val in many_values:
    print(f"\n{val['attribute']} ({val['distinct_values']} distinct values): Too many to display")
