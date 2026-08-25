import pandas as pd
import os
from pathlib import Path
from tabulate import tabulate
import shutil
from re import sub


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

def populate_ddl_ers(output_fname,df,constraints_df):
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

    
    temp_cons_df = constraints_df.loc[(constraints_df['child_database_name'] == database_name) & (constraints_df['child_table_name'] == table_name) ,['constraint_name']].copy()
    for index,cons_row in temp_cons_df.iterrows():
       #table_ddl_str = table_ddl_str + ',\n'
       table_ddl_str = table_ddl_str + ',' + '\n' + cons_row['constraint_name'] 


    table_ddl_str = '\n' + table_ddl_str + ');\n'
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

def populate_pks_ers(df):
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
         pk_sql_str = pk_sql_str + ' CONSTRAINT ' + pks['ref_grp'] + '_' + pks['child_table_name'] + '_' + pks['parent_table_name'] + ' FOREIGN KEY ' + '(' + get_primary_keys(pks_col_df['child_column_name'].to_list()) + ')' + ' REFERENCES ' +  pks['parent_database_name'] + '.' +  pks['parent_table_name'] + '(' + get_primary_keys(pks_col_df['parent_column_name'].to_list()) + ')' 
         pk_list.append({'child_database_name': pks['child_database_name'], 'child_table_name' : pks['child_table_name'], 'constraint_name':pk_sql_str})


   return pd.DataFrame(pk_list)

def snake_case(s):
    # Replace hyphens with spaces, then apply regular expression substitutions for title case conversion
    # and add an underscore between words, finally convert the result to lowercase
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
        sub('([A-Z]+)', r' \1',
        s.replace('-', ' '))).split()).lower()

def get_formatted_attribute_df(template_file):
   data_df = pd.read_excel(template_file,dtype=str, sheet_name='Attribute Mapping',header=0).fillna('')
   data_df.columns = map(str.lower, data_df.columns)
   data_df.columns = [c.replace("\n", "_") for c in data_df.columns]
   data_df['phase (1/2)'] = data_df['phase (1/2)'].astype(str)

   data_df.fillna('',inplace=True)
   #print(new_df.columns)

   """
   data_df['requested attribute']  = data_df['required attribute (business name)'] 
   data_df['source table']         = data_df['source schema.table'] 
   data_df['source column']        = data_df['source field']
   data_df['transformation logic'] = data_df['transformation logic (plain english, numbered steps)']
   """

   temp_list = []
   curr_attribute_name = ''
   curr_phase = ''
   for index, row in data_df.iterrows():
     #print(row)
     row_attribute_name = row['required attribute (business name)']
     if row_attribute_name != '':
        curr_attribute_name = row_attribute_name
        curr_phase = row['phase (1/2)']
        row['derived requested attribute'] = row_attribute_name
        row['derived phase'] = row['phase (1/2)']
     else:
       row['derived requested attribute'] = curr_attribute_name
       row['derived phase'] =  curr_phase
     temp_list.append(row)



   return pd.DataFrame(temp_list)

def populate_table_excel(merged_df,ref_file,out_file,template_file,path):
   #merged_df has all the fields in the target_db in snake_case_substitute format
   snake_df = pd.read_excel(ref_file, sheet_name='snake_case',header=0)
   
   #requested_attribute_df = pd.read_excel(out_file, sheet_name='requested attribute',header=0)
   
   #formatted_attribute_df = pd.read_excel(out_file, sheet_name='attributes_formated',header=0)
   formatted_attribute_df = get_formatted_attribute_df(template_file)
   #write_excel('C:\\app\\modelling\\staff\\test.xlsx','formatted_attribute_df_1',formatted_attribute_df)
   
   formatted_attribute_df['derived requested attribute'] = formatted_attribute_df['derived requested attribute'].str.strip().str.lower()
   #write_excel('C:\\app\\modelling\\staff\\test.xlsx','formatted_attribute_df_2',formatted_attribute_df)

   formatted_attribute_df['snake_case'] = formatted_attribute_df.apply(lambda row: snake_case(row['derived requested attribute']), axis = 1)
   #write_excel('C:\\app\\modelling\\staff\\test.xlsx','formatted_attribute_df_3',formatted_attribute_df)

   formatted_attribute_df = formatted_attribute_df.loc[formatted_attribute_df['derived phase'] == '1']
   #write_excel('C:\\app\\modelling\\staff\\test.xlsx','formatted_attribute_df_4',formatted_attribute_df)
   

   snake_case_substitute_df = pd.merge(formatted_attribute_df,snake_df,how='left',left_on='snake_case',right_on='snake_case')
   
   
   snake_case_substitute_df = snake_case_substitute_df.drop('snake_case', axis=1)
   snake_case_substitute_df['snake_case'] = snake_case_substitute_df['snake_case_substitute']
   snake_case_substitute_df['transformation logic'] = snake_case_substitute_df['transformation logic (plain english, numbered steps)']
   print(snake_case_substitute_df.columns)
   write_excel('C:\\app\\modelling\\staff\\test.xlsx','snake_case_substitute_df',snake_case_substitute_df)
   

   
   all_tables_df = merged_df.groupby(['database_name','table_name'], dropna=False).size().reset_index(name = 'count')
   
   for index,table in all_tables_df.iterrows():
      try:
         if not os.path.exists(path):
          raise FileNotFoundError(f"Template file not found: {model_template}")
         os.makedirs(path, exist_ok=True)
         destination = os.path.join(path, table['table_name'] + '.xlsx')
         shutil.copy2(template_file, destination)
         
         d1 = snake_case_substitute_df
         write_excel('C:\\app\\modelling\\staff\\test.xlsx','d1'+table['table_name'],d1)
         d2 = merged_df.loc[(merged_df['database_name'] == table['database_name']) & (merged_df['table_name'] == table['table_name'])]
         write_excel('C:\\app\\modelling\\staff\\test.xlsx','d2'+table['table_name'],d2)

         table_attributes_df = populate_table_specific_attribute_df(d1,d2)
         write_excel('C:\\app\\modelling\\staff\\test.xlsx','final_result',table_attributes_df) # test
         write_excel(destination,'Attibute Mapping for ' + table['table_name'],table_attributes_df)


      except FileNotFoundError as e:
          print(f"✗ Error: {e}")
      except PermissionError as e:
          print(f"✗ Permission denied: {e}")
      except Exception as e:
          print(f"✗ An unexpected error occurred: {e}")

def populate_table_specific_attribute_df(d1,d2):
    d2['row_number'] = d2.reset_index().index

    # Process d1 - fill forward the target entity and target column values
    d1_processed = d1.copy()
    #d1_processed['target entity'] = d1_processed['target entity'].fillna(method='ffill')
    #d1_processed['target column'] = d1_processed['target column'].fillna(method='ffill')

    d1_processed['target entity'] = ''
    d1_processed['target column'] = ''

    # Select only the columns we want from d1
    """
    d1_columns = ['target entity', 'target column', 'population', 'target data type', 
                'source schema.table', 'source field', 'source data type', 
                'is pbi logic? (y/n)', 'snake_case']
    """
    d1_columns = [ 'target entity', 'target column', 'population', 'target data type', 'pk? (y/n)', 'nullable? (y/n)', 'required attribute (business name)'
                 , 'description', 'phase (1/2)', 'source type', 'source schema.table', 'source field', 'source data type', 'direct or derived'
                 , 'transformation logic', 'null / duplicate / unmatched-key handling', 'code snippet', 'is pbi logic? (y/n)', 'pii / sensitivity'
                 , 'business comments', 'status', 'last updated', 'derived requested attribute', 'derived phase', 'snake_case_substitute', 'snake_case']

    # Rename derived requested attribute to column_name for joining
    d1_processed = d1_processed[d1_columns].rename(columns={
        'snake_case': 'column_name'
    })

    # Join d1 and d2 on column_name
    merged_df = pd.merge(
        d1_processed,
        d2[['database_name','table_name','column_name', 'column_type','pk','row_number']],
        on='column_name',
        how='right' ## previousely outer
    )

    write_excel('c:\\documentation\\gdocs\\test2_out.xlsx','merged_df',merged_df)


    ######################

    col_list = []
    prev_attribute = ''
    #curr_attribute = ''
    first_row = True
    for index, row in merged_df.iterrows():
    #print(row)
    
     if first_row:  #The first row in the iteration
        row['target database'] = row['database_name']
        row['target entity'] = row['table_name']
        row['target column'] = row['column_name']
        row['target data type'] = row['column_type']
        row['PK? (Y/N)'] = row['pk']
        row['Nullable? (Y/N)'] = ''
        prev_attribute = row['column_name']
        #curr_attribute = row['column_name']
        first_row = False

     elif prev_attribute != row['column_name']:
        row['target database'] = row['database_name']
        row['target entity'] = row['table_name']
        row['target column'] = row['column_name']
        row['target data type'] = row['column_type']
        row['PK? (Y/N)'] = row['pk']
        row['Nullable? (Y/N)'] = ''
        prev_attribute = row['column_name']

     col_list.append(row)


    final_df = pd.DataFrame(col_list)
    final_df = final_df.drop(['database_name', 'table_name', 'column_name','column_type','pk'], axis=1)
    final_df = final_df.fillna('')
    #final_df = final_df[['target database', 'target entity', 'target column', 'target data type','PK? (Y/N)','Nullable? (Y/N)','source schema.table','source field','source data type','is pbi logic? (y/n)']]
    final_df = final_df[[ 'target entity', 'target column', 'population', 'target data type', 'pk? (y/n)', 'nullable? (y/n)', 'required attribute (business name)'
                 , 'description', 'phase (1/2)', 'source type', 'source schema.table', 'source field', 'source data type', 'direct or derived'
                 , 'transformation logic', 'null / duplicate / unmatched-key handling', 'code snippet', 'is pbi logic? (y/n)', 'pii / sensitivity'
                 , 'business comments', 'status', 'last updated']]
    return final_df



      
      
excel_dir = 'C:\\app\\modelling\\staff\\excel\\'
ref_file = 'C:\\app\\modelling\\staff\\advisor_refs.xlsx'
format_outfile = 'C:\\app\\modelling\\staff\\Adviser_out.xlsx' # This should replace model_out_file

model_template = 'C:\\app\\modelling\\staff\\Copy of TDC_Mapping_Workbook_Template Adviser V12.xlsx'
#model_in_file = 'C:\\app\\modelling\\staff\\Adviser_model.xlsx'
#model_out_file = 'C:\\app\\modelling\\staff\\Adviser_model_out.xlsx'
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
#This block is not necessary as in the out file the matched variable type will exist
#attribute_required_df = pd.read_excel(model_in_file, sheet_name='advisor_model',header=0)
#attribute_types_df = pd.read_excel(model_out_file, sheet_name='model',header=0)
#write_excel(model_out_file,'merged model',attribute_required_df.merge(attribute_types_df,how='left',on='requested attribute'))
#write_excel(model_out_file,'silver_ref',pd.read_excel(model_in_file, sheet_name='silver_ref',header=0))
#write_excel(model_out_file,'gold_ref'  ,pd.read_excel(model_in_file, sheet_name='gold_ref',header=0))

#main_model_df = pd.read_excel(model_out_file, sheet_name='merged model',header=0) # This should be changed to ref.advisor_model
main_model_df = pd.read_excel(ref_file, sheet_name='advisor_model',header=0) # This should be changed to ref.advisor_model
main_model_df = main_model_df.loc[(main_model_df['phase (1/2)'] == 1) & (main_model_df['modelled'] == 'y')]
main_model_df = main_model_df[['column_name','silver','gold','mv','pk','source data type','modelled']]

main_silver_df = main_model_df[['column_name','silver','source data type','pk','modelled']]
main_silver_df['table_name'] = main_silver_df['silver']
main_silver_df['column_type'] = main_silver_df['source data type']

main_gold_df = main_model_df[['column_name','gold','source data type','pk']]
main_gold_df['table_name'] = main_gold_df['gold']
main_gold_df['column_type'] = main_gold_df['source data type']

main_mv_df = main_model_df[['column_name','mv','source data type','pk']]
main_mv_df['table_name'] = main_mv_df['mv']
main_mv_df['column_type'] = main_mv_df['source data type']

#silver_model_df = pd.read_excel(model_in_file, sheet_name='aux_silver',header=0) # This should be changed to ref.aux_silver
silver_model_df = pd.read_excel(ref_file, sheet_name='aux_silver',header=0) # This should be changed to ref.aux_silver
silver_model_df = silver_model_df[['column_name','column_type','table_name','pk','modelled']]
silver_model_df = pd.concat([silver_model_df,main_silver_df],ignore_index=True)
silver_model_df['database_name'] = 'pre_prod_20_silver.silver' ##This has the merged df

silver_model_df = silver_model_df.loc[(silver_model_df['modelled'] == 'y') ].copy()
write_excel(merged_out_file,'silver',silver_model_df)

#silver_ddl = populate_ddl(silver_sql_file,silver_model_df) # Now I am using the er studio format
#silver_pk_df = pd.read_excel(model_out_file, sheet_name='silver_ref',header=0) # This should be changed to ref.silver_ref
silver_pk_df = pd.read_excel(ref_file, sheet_name='silver_ref',header=0) # This should be changed to ref.silver_ref
silver_pk_df['child_database_name'] = 'pre_prod_20_silver.silver'
silver_pk_df['parent_database_name'] = 'pre_prod_20_silver.silver'
populate_pks(silver_sql_file,silver_pk_df)
cons_df = populate_pks_ers(silver_pk_df)
silver_ddl = populate_ddl_ers(silver_sql_file,silver_model_df,cons_df)

populate_table_excel(silver_model_df,ref_file,format_outfile,model_template,excel_dir+'silver\\')

#gold_model_df = pd.read_excel(model_in_file, sheet_name='aux_gold',header=0) # This should be changed to ref.aux_gold
gold_model_df = pd.read_excel(ref_file, sheet_name='aux_gold',header=0) # This should be changed to ref.aux_gold
gold_model_df = gold_model_df[['column_name','column_type','table_name','pk','modelled']]
gold_model_df = pd.concat([gold_model_df,main_gold_df],ignore_index=True)
gold_model_df['database_name'] = 'pre_prod_20_gold.gold' ##This has the merged df for gold join with formatted attributes

gold_model_df = gold_model_df.loc[(gold_model_df['modelled'] == 'y') ].copy()
write_excel(merged_out_file,'gold',gold_model_df)
gold_ddl = populate_ddl(gold_sql_file,gold_model_df)
#gold_pk_df = pd.read_excel(model_out_file, sheet_name='gold_ref',header=0)
gold_pk_df = pd.read_excel(ref_file, sheet_name='gold_ref',header=0)
gold_pk_df['child_database_name'] = 'pre_prod_20_gold.gold'
gold_pk_df['parent_database_name'] = 'pre_prod_20_gold.gold'
populate_pks(gold_sql_file,gold_pk_df)
