import pandas as pd
import os
from pathlib import Path
from tabulate import tabulate

def write_excel (output_fname,sheet_name,df):
 if os.path.exists(output_fname):
   with pd.ExcelWriter(output_fname, engine='openpyxl', mode='a',if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name=sheet_name, index=False)

 else:
   with pd.ExcelWriter(output_fname, engine='openpyxl', mode='w') as writer:
    df.to_excel(writer, sheet_name=sheet_name, index=False)

def get_primary_keys(pk_list):
    return ','.join(pk_list)

def populate_ddl(output_fname,df):
 ddl_list = []
 #We need to check if the df is a pandas dataframe
 #We need to validate the columns of the dataframe to check if the database_name,table_name,column_name,column_type and pk exists
 tables_df = df.groupby(['database_name','table_name']).size().reset_index(name = 'count')
 #print(tables_df)

 for index,db_table_row in tables_df.iterrows():
    #print(db_table_row)
    table_name = str(db_table_row['table_name'])
    database_name = db_table_row['database_name']
    #table_ddl_str = "CREATE TABLE " + '"' + database_name + '.' + table_name + '"' + " (\n"
    table_ddl_str = "CREATE TABLE " + database_name + '.' + table_name +  " (\n"

    first_col_ind = True
    #column_df = all_col_df[all_col_df['Source_TableName_AWS'] == table_name]
    #column_df = column_df.drop_duplicates()
    column_df = df.loc[(df['table_name'] == table_name) & (df['database_name'] == database_name),['column_name','column_type','pk']].copy()
    column_df['column_name'] = column_df['column_name'].str.lower()
    column_df['column_type'] = column_df['column_type'].str.lower()
    column_df['pk'] = column_df['pk'].str.lower()
    
    #print(column_df)
    column_df = column_df.groupby(['column_name','column_type','pk'], dropna=False).size().reset_index(name = 'count')

    #print(column_df)
    for index,column_row in column_df.iterrows():
        if first_col_ind:
           table_ddl_str = table_ddl_str + str(column_row['column_name']).lower().strip() + ' ' + str(column_row['column_type']).lower().strip()
           first_col_ind = False
        else:
            table_ddl_str = table_ddl_str + ',\n'
            table_ddl_str = table_ddl_str + str(column_row['column_name']).lower().strip() + ' ' + str(column_row['column_type']).lower().strip()

    #table_columns = all_data.loc[(all_data['enriched_table_name']== table['Table_Name']) & (all_data['source_sheet'] == table['Tab Name'])]
    pk_df = df[(df['table_name'] == table_name) & (df['pk'] == 'not null')]
    if pk_df.empty:        
      table_ddl_str = table_ddl_str + '\n'
    else:
        table_ddl_str = table_ddl_str + ',\n'
        table_ddl_str = table_ddl_str + 'PRIMARY KEY (' + get_primary_keys(pk_df['column_name'].to_list()) + ')\n'

    table_ddl_str = table_ddl_str + ');\n'
    table_ddl_str = table_ddl_str + '\n' 
    ddl_list.append(table_ddl_str)


 with open(output_fname, 'w') as fp:
    for table_ddl in ddl_list:
        fp.write("%s\n" % table_ddl)
 return ddl_list


def populate_pks(output_fname,df):
   pk_list = []
   pks_df = df.groupby(['child_database_name','child_table_name','parent_database_name','parent_table_name','ref_grp'], dropna=False).size().reset_index(name = 'count')
   #print(pks_df.to_markdown())
   for index,pks in pks_df.iterrows():
      #print(pks)
      pk_sql_str=''
      pks_col_df = df.loc[(df['child_database_name'] == pks['child_database_name']) & (df['child_table_name'] == pks['child_table_name']) & (df['parent_table_name'] == pks['parent_table_name']) & (df['parent_database_name'] == pks['parent_database_name']) & (df['ref_grp'] == pks['ref_grp']),['child_column_name','parent_column_name']].copy()
      #print(pks_col_df)
      if not pks_col_df.empty:
      
         pk_sql_str = pk_sql_str + '\n'
         pk_sql_str = pk_sql_str + 'ALTER TABLE ' + pks['child_database_name'] + '.' +  pks['child_table_name'] + ' ADD CONSTRAINT ' + pks['ref_grp'] + '_' + pks['child_table_name'] + '_' + pks['parent_table_name'] + ' FOREIGN KEY ' + '(' + get_primary_keys(pks_col_df['child_column_name'].to_list()) + ')' + ' REFERENCES ' +  pks['parent_database_name'] + '.' +  pks['parent_table_name'] + '(' + get_primary_keys(pks_col_df['parent_column_name'].to_list()) + ')' + ';'
         pk_list.append(pk_sql_str)

   with open(output_fname, 'a') as fp:
       for table_ddl in pk_list:
           fp.write("%s\n" % table_ddl)
   #return pk_list


def populate_table_excel(merged_df,ref_file,out_file,template_file,path):
   #merged_df has all the fields in the target_db in snake_case_substitute format
   snake_df = pd.read_excel(ref_file, sheet_name='snake_case',header=0)
   requested_attribute_df = pd.read_excel(out_file, sheet_name='requested attribute',header=0)
   formatted_attribute_df = pd.read_excel(out_file, sheet_name='attributes_formated',header=0)
   formatted_attribute_df['derived requested attribute'] = formatted_attribute_df['derived requested attribute'].str.strip().str.lower()
   formatted_attribute_df = formatted_attribute_df.loc[formatted_attribute_df['derived phase'] == '1.0']

   snake_case_substitute_df = pd.merge(requested_attribute_df,snake_df,how='left',left_on='snake_case',right_on='snake_case')

      
      


model_template = 'C:\\app\\modelling\\staff\\TDC_Mapping_Workbook_Template Adviser V7.xlsx'
model_in_file = 'C:\\app\\modelling\\staff\\Adviser_model.xlsx'
model_out_file = 'C:\\app\\modelling\\staff\\Adviser_model_out.xlsx'
merged_out_file = 'C:\\app\\modelling\\staff\\Adviser_model_merged.xlsx'

silver_sql_file = 'C:\\app\\modelling\\staff\\advisor_silver.sql'
gold_sql_file = 'C:\\app\\modelling\\staff\\advisor_gold.sql'

#######################Grouping the attributes and assigning the types###################
## Change the format_mapping_sheet.py to get the data types assigned
#attribute_formatted_df = pd.read_excel(model_in_file, sheet_name='attributes_formated',header=0)
#attribute_formatted_df = attribute_formatted_df[['derived requested attribute','derived phase','source data type']]
#attribute_formatted_df = attribute_formatted_df.loc[attribute_formatted_df['derived phase'] == 1]
#write_excel(model_out_file,'phase',attribute_formatted_df)
#attribute_formatted_df = attribute_formatted_df.groupby(['derived requested attribute']).agg(min)[['derived phase', 'source data type']].reset_index()
#write_excel(model_out_file,'model',attribute_formatted_df)

#######################Merging the data types with attributes and bringing the references to one excel###################
#attribute_required_df = pd.read_excel(model_in_file, sheet_name='advisor_model',header=0)
#attribute_types_df = pd.read_excel(model_out_file, sheet_name='model',header=0)
#write_excel(model_out_file,'merged model',attribute_required_df.merge(attribute_types_df,how='left',on='requested attribute'))
#write_excel(model_out_file,'silver_ref',pd.read_excel(model_in_file, sheet_name='silver_ref',header=0))
#write_excel(model_out_file,'gold_ref'  ,pd.read_excel(model_in_file, sheet_name='gold_ref',header=0))

main_model_df = pd.read_excel(model_out_file, sheet_name='merged model',header=0)
main_model_df = main_model_df.loc[(main_model_df['phase (1/2)'] == 1) & (main_model_df['modelled'] == 'y')]
main_model_df = main_model_df[['column_name','silver','gold','mv','pk','source data type']]

main_silver_df = main_model_df[['column_name','silver','source data type','pk']]
main_silver_df['table_name'] = main_silver_df['silver']
main_silver_df['column_type'] = main_silver_df['source data type']

main_gold_df = main_model_df[['column_name','gold','source data type','pk']]
main_gold_df['table_name'] = main_gold_df['gold']
main_gold_df['column_type'] = main_gold_df['source data type']

main_mv_df = main_model_df[['column_name','mv','source data type','pk']]
main_mv_df['table_name'] = main_mv_df['mv']
main_mv_df['column_type'] = main_mv_df['source data type']

silver_model_df = pd.read_excel(model_in_file, sheet_name='aux_silver',header=0)
silver_model_df = silver_model_df[['column_name','column_type','table_name','pk']]
silver_model_df = pd.concat([silver_model_df,main_silver_df],ignore_index=True)
silver_model_df['database_name'] = 'pre_prod_20_silver.silver' ##This has the merged df
write_excel(merged_out_file,'silver',silver_model_df)

silver_ddl = populate_ddl(silver_sql_file,silver_model_df)
silver_pk_df = pd.read_excel(model_out_file, sheet_name='silver_ref',header=0)
silver_pk_df['child_database_name'] = 'pre_prod_20_silver.silver'
silver_pk_df['parent_database_name'] = 'pre_prod_20_silver.silver'
populate_pks(silver_sql_file,silver_pk_df)

gold_model_df = pd.read_excel(model_in_file, sheet_name='aux_gold',header=0)
gold_model_df = gold_model_df[['column_name','column_type','table_name','pk']]
gold_model_df = pd.concat([gold_model_df,main_gold_df],ignore_index=True)
gold_model_df['database_name'] = 'pre_prod_20_gold.gold' ##This has the merged df for gold join with formatted attributes
write_excel(merged_out_file,'gold',gold_model_df)
gold_ddl = populate_ddl(gold_sql_file,gold_model_df)
gold_pk_df = pd.read_excel(model_out_file, sheet_name='gold_ref',header=0)
gold_pk_df['child_database_name'] = 'pre_prod_20_gold.gold'
gold_pk_df['parent_database_name'] = 'pre_prod_20_gold.gold'
populate_pks(gold_sql_file,gold_pk_df)
