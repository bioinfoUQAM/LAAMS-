"""
HEADER 
CMS_data_analysis.py 
    File created to load the cms data and perform a few basic analyses on it. 
 
Created on Thur Apr  2 16:07:40 2020
@author: Amanda Boatswain Jacques
"""

import pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Create a list of all the files we will work with
input_path = "./input/cms_Extracts_07Apr2020/"
file_paths = os.listdir(input_path)
datasets = dict()

# Load each dataset in the folder and save to a pandas dataframe (df) 
for i, file in enumerate(os.listdir(input_path)): 
    if file.endswith(".cpickle"):
        # load the dataframe 
        df = pickle.load(open(input_path + file, "rb"))
        # convert all column names to lower case  
        df = df.rename(str.lower, axis='columns')
        
        # Store all the final dataframes in a dictionary 
        datasets[file.split(".")[0]] = df
        
        # Print an overview of the dataset in the terminal 
        print("Loaded Dataset {}: {}".format(i, file))
        print(datasets[file.split(".")[0]].head())
        print(" ")

# Next, start working on the combined dataset using the included files
        
# Rename some of the columns for clarity and to be able to merge later
datasets["cms_Animals"].rename(columns={"id": "cca_id", "crtn_date": "animals_crtn_date"}, inplace=True)  
datasets["cms_Herds"].rename(columns={"id": "cch_id", "crtn_date": "herds_crtn_date"}, inplace=True)  
datasets["cms_Start_Lactations"].rename(columns={"start_date": "lactation_start_date"}, inplace=True)  
datasets["cms_End_Lactations"].rename(columns={"end_date": "lactation_end_date"}, inplace=True)  

""" Notes de René
Le mieux est de commencer par ccc_cms_herds, en triant sur hrd_prv_cd, hrd_id, 
id (primary key) et export_date.  Regarde comment se comportent les export_start_date, 
export_end_date et crtn_date. Ne te préoccupe pas des duplicatas pour l’instant. 
Le but est de te familiariser avec le processus d’acquisition et stockage.

Ensuite ccc_cms_animals. Fais le lien avec ccc_cms_herds via cch_id (foreign key), 
et fais un tri sur par exemple, cch.hrd_prv_cd, cch.hrd_id, anm_ident, visible_id_no_6, 
birth_date, cch.crtn_date, cca.crtn_date. Encore une fois, ne te préoccupe 
pas trop des duplicatas pour l’instant.

Ensuite tu pourras attaquer ccc_cms_milkings, et la tu devras te préoccuper des duplicatas!

"""
# Drop the columns we don't need 
datasets["cms_Animals"].drop(["last_modfd_by", "last_modfd_date"], inplace=True, axis = 1)       
datasets["cms_Breeding_Dates"].drop(["last_modfd_by", "last_modfd_date", "crtn_date"], inplace=True, axis = 1)
datasets["cms_End_Lactations"].drop(["last_modfd_by", "last_modfd_date", "crtn_date"], inplace=True, axis = 1)
datasets["cms_Start_Lactations"].drop(["last_modfd_by", "last_modfd_date", "crtn_date"], inplace=True, axis = 1)
datasets["cms_Herds"].drop(["last_modfd_by", "last_modfd_date", "cms_software_code", 
                    "cms_software_version", "installation_code", "interface_code", "manufacturer_code"], inplace=True, axis = 1) 
datasets["cms_Milkings"].drop(["milkng_code", "lr_scc", "lf_scc", "rf_scc", 
              "rr_scc", "lactose", "urea", "last_modfd_by", "last_modfd_date"], inplace=True, axis =1)       

# Start with cms_Herds
# Rearrange the columns and sort the values
datasets["cms_Herds"] = datasets["cms_Herds"][["cch_id", "hrd_prv_cd", "hrd_id", "export_start_date", "exported_date", "export_end_date", "herds_crtn_date"]]

datasets["cms_Herds"].sort_values(by=['hrd_prv_cd', 'hrd_id', 'exported_date'])

# Next join animals and herds 
datasets["cms_Animals"] = datasets["cms_Animals"][["cca_id", "cch_id", "anm_ident", "visible_id_no_6", "birth_date", "animals_crtn_date"]]
result = pd.merge(datasets["cms_Animals"], datasets["cms_Herds"][["cch_id", "hrd_id", "hrd_prv_cd", "export_start_date", "exported_date", "export_end_date", "herds_crtn_date"]], on="cch_id", how="outer")

# remove the keys since we no longer need them
#result.drop(["cca_id", "cch_id"], axis=1, inplace=True)

# Sort all the final values
result.sort_values(by=["anm_ident", "visible_id_no_6", "birth_date","hrd_prv_cd", "hrd_id", "animals_crtn_date", "herds_crtn_date"])
result = result[["cca_id", "anm_ident", "visible_id_no_6", "birth_date","hrd_prv_cd", "hrd_id", "export_start_date", "exported_date", "export_end_date", "animals_crtn_date", "herds_crtn_date"]]


result = pd.merge(result, datasets["cms_Milkings"][["cca_id", "milkng_date", "milk_wgt", "milkng_temp", "milk_flow_avg", "milk_flow_max", "fat_pcnt", "prot_pcnt", "scc", "crtn_date" ]], 
                  on="cca_id", how="outer")
result.sort_values(by=["anm_ident", "visible_id_no_6", "birth_date","hrd_prv_cd", "hrd_id","milkng_date", "animals_crtn_date", "herds_crtn_date"])

"""
# Merge the datasets to create a final one
result = pd.merge(datasets["cms_Animals"], datasets["cms_Breeding_Dates"][["cca_id", "service_date"]], 
                  on="cca_id", how="outer")

#result = pd.merge(result, datasets["cms_Start_Lactations"][["cca_id", "lact_no", "lactation_start_date"]], 
                  #on="cca_id", how="outer")


#result = pd.merge(result, datasets["cms_End_Lactations"][["cca_id", "lactation_end_date"]], 
                  #on="cca_id", how="outer")

result = pd.merge(result, datasets["cms_Herds"][["cch_id", "hrd_id", "hrd_prv_cd"]], 
                  on="cch_id", how="outer")

result = pd.merge(result, datasets["cms_Milkings"][["cca_id", "milk_wgt", "milkng_temp", "milk_flow_avg", "milk_flow_max", "fat_pcnt", "prot_pcnt", "scc" ]], 
                  on="cca_id", how="left")

print(result.head())
"""