import os
import shutil
import numpy as np
import pandas as pd 
from os import listdir 
import paths

def printCompleteDf(df):
    pd.set_option("max_rows", None)
    pd.set_option("max_columns", None)
    print(df)

def make_message_case_folder(path,test_message):
    test_case_path = path.rsplit("\\",1)[1]
    test_case_path = test_case_path.replace("base_", "")
    name = test_case_path.replace(".xml", "")

    test_folder = paths.xmls_cases_folder_path + "\\" + name
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)
    
    test_case_path = test_folder + "\\" + "base.xml"
    shutil.copyfile(path, test_case_path)
    return test_folder

def create_messages(df,case_folder_path):
    df.columns = df.iloc[0]
    df = df[1:]
    #the idea
    #it recives a data frame where each column is a field of a message and each row is a message
    # mi intent is to first go across each row and see if it has an array [val1, val2] in it
    # if it has an array make a x copy of the row and place the value of the array in the corresponding field where x is the number of elements in the array
    # then continue to the next field and so on until the end   
    made_new_row = True
    while(made_new_row):
        made_new_row = False
        for row in df.iterrows():
            row = row[1]
            row_index = list(df.index).index(row.name)
            #iterate across the columns and print the values
            for col in df.columns:
                if "[" in row[col]:
                    array = row[col].replace("[", "").replace("]", "").split(",")
                    for element in array:
                        copy_of_row = row.copy()        
                        # modify the copy
                        copy_of_row[col]= element 
                        copy_of_row.name = copy_of_row.name + "_" + str(array.index(element))
                        # insert the copy into the data frame at index row_index
                        df = df.append(copy_of_row, sort=True)
                        made_new_row = True
                    # remove the original row
                    df = df.drop(df.index[row_index])
                    print("df after drop")
                    printCompleteDf(df.T)
                    break
        

    
    

def generate_xml_cases(message_details_folder_path):
    folder = listdir(message_details_folder_path)
    for excel in folder:
        
        path = message_details_folder_path + "\\" + excel
        name = excel.rsplit("_",1)[1].replace(".xlsx", "")
        base_path = paths.xmls_folder_path +"\\base\\base_" + name + ".xml"
        case_folder_path = make_message_case_folder(base_path,name)
        pd.set_option('display.max_rows', None)
        df = pd.read_excel(path)
        df.style.hide_index()
        
        #find the values file row 
        values_file_row = df.iloc[:,0].tolist().index("values file")
        value_file_df = df.iloc[[values_file_row]]
        
        #remove the json specific part of the code 
        df_col1_list = df.iloc[:,0].tolist()
        first_nan_index = df_col1_list.index(np.nan)
        last_row = len(df_col1_list)
        df.drop(df.loc[first_nan_index:last_row].index, inplace=True)
        df = pd.concat([df,value_file_df])
        #transpose the grid to use the paths as columns and each message is now a row
        df = df.T
        create_messages(df,case_folder_path)
        
        