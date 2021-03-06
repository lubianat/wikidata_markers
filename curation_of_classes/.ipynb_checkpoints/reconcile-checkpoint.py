import os 
import pandas as pd
from dicts import *
import re
import pickle

os.system('wget -O cell_classes.xlsx https://docs.google.com/spreadsheets/d/e/2PACX-1vTanLtzxD6OXpu3Ze4aNITlIMZEqfK3qrrcNiwFE6kA-YVnuzULp3dG3oYIe5gYAVj28QWZnGwzN_H6/pub\?output\=xlsx')

cells = pd.read_excel("cell_classes.xlsx", sheet_name="cell classes")

print(cells.head())


with open('celltypes_dict.pickle', 'rb') as handle:
    subclass_dict = pickle.load(handle)
    
print(subclass_dict)

subclass_dict["B cell"] =  'Q188930'


from wikidataintegrator import wdi_login
import getpass

pwd = getpass.getpass()
login_instance = wdi_login.WDLogin(user='TiagoLubiana', pwd=pwd)


from wikidataintegrator import wdi_core
import time

for index, row in cells.iterrows():

    data_for_item = []     
    stated_in_full_reference = wdi_core.WDItemID(value=row["stated in"], prop_nr="P248", is_reference=True)
    references = [[stated_in_full_reference]]
    

    label = row["label"]
    print(f"Running code for {label} ")

    if "human" in label:
      description = "cell type in Homo sapiens"
      taxon = "Q15978631"
        
      data_for_item.append( 
        wdi_core.WDItemID(value=taxon,
                        prop_nr="P703",
                         references=references)
    )  
      
    elif "mouse" in label:
      description = "cell type in Mus musculus"
      data_for_item.append( 
        wdi_core.WDItemID(value=taxon,
                        prop_nr="P703",
                         references=references)
    )  

    elif "zebrafish" in label:
      description = "cell type in Danio rerio"
      taxon = "Q169444"
      data_for_item.append( 
        wdi_core.WDItemID(value=taxon,
                        prop_nr="P703",
                         references=references)
    )  
    else:
      description = "cell type"

    try:
        if  re.findall("Q[0-9]*", row["subclass of"]):
            subclass = row["subclass of"]
        else:
            subclass = subclass_dict[row["subclass of"]]            
        
        data_for_item.append( 
        wdi_core.WDItemID(value=subclass,
                        prop_nr="P279")
    )  

        if str(row["anatomical location"]) != "nan":
            if  re.findall("Q[0-9]*", row["anatomical location"]):
                part_of = row["anatomical location"]
            else:
                part_of = part_of_dict[row["anatomical location"]]

            data_for_item.append( 
            wdi_core.WDItemID(value=part_of,
                            prop_nr="P927",
                             references=references)
        )          

        if str(row["described by source"]) != "nan":
            data_for_item.append( 
            wdi_core.WDItemID(value=row["described by source"],
                            prop_nr="P1343")
                        )
     
    except:
        print("")
        print("failed: ")
        print(row)
        break
    
    if str(row["aliases"]) != "nan":
        aliases = row["aliases"].split("|")
    else:
        aliases = []

    if str(row["instance of"]) != "nan":
      instance = instance_dict[row["instance of"]]
    else: 
      instance = instance_dict["cell type"]
    print(instance)
    data_for_item.append( 
    wdi_core.WDItemID(value=instance,
                    prop_nr="P31",
                    references=references)
    )
    wd_item = wdi_core.WDItemEngine(data=data_for_item)
    wd_item.set_label(label=label, lang="en")
    wd_item.set_aliases(aliases, lang="en")
    wd_item.set_description(description, lang="en")
    try:
        wd_item.write(login_instance)
        subclass_dict[label] = wd_item.wd_item_id
    except:
        print("Something went wrong")
    
    time.sleep(1)

        

with open('celltypes_dict.pickle', 'wb') as handle:
    pickle.dump(subclass_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)