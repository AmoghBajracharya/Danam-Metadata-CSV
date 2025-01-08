from datetime import datetime
from scripts.write_csv import list_from_txt


def manual_fixes(df, filename):
    file = open(filename, 'r', encoding='UTF-8')
    for line in file.readlines():

        parts = line.split(";")
        row = int(parts[0])
        col = parts[1]
        val = parts[2].replace("\n","")
        df.at[row, col] = val
    return df

'''
Review metadata extracted from DANAM before uploading and replace faulty metadata using a CSV file

    df = Pandas DataFrame containing metadata of select images from DANAM
    fixes = string,
            a CSV file containing fixes for the metadata. This CSV file has the format 
            row_number,column_name,correct_value
    checked = boolean,
              if False, takes select columns to prepare metadata for review using variable viewer. 
              if True, metadata is fixed using prepared CSV defined in fixes
    label = string, optional, if given, the status of the metadata df will be printed out with this given label.
'''
def check_metadata(df, fixes, checked, label):
    cols = [
        'danam_caption', 'caption', 'date', 'date3', 'agent', 'role', 'agent2', 'role2', 'class_code', 'classification','source', 'notes', 'agent3', 'date_scan',
        ]
    manual_fixes(df, fixes)
    if not checked:
        df = df[cols]
        print(f"{label}: PLEASE CHECK USING VARIABLE VIEW")
    else: 
        print(f"{label}: READY TO UPLOAD")
    return df


def reset(reset_files=False):
    if reset_files:
        open("fixes\\all.fix", "w")
        open("fixes\\historical.fix", "w")
        open("fixes\\images.fix", "w")
        open("fixes\\maps.fix", "w")
        open("fixes\\recent.fix", "w")
    return (False,False,False,False,False)


def prepare_metadata(danam_df, mon, fix, check, label="" ,query=None):
    mon_list = list_from_txt(mon)

    df = danam_df.loc[danam_df['mon_id'].isin(mon_list)]
    df = df.loc[df['validCaption']]
    if query is not None:
        df = df.loc[eval(query)]

    ## manual fixes##
    df = check_metadata(df,fix,check, label)

    return df

def get_recent_changes(danam_df, year,month,date):

    recent = danam_df.loc[danam_df['lastModified'] >= datetime(year, month, date)]
    #print("Number of recently updated monuments: {}".format(recent.shape[0]))
    recent_mon_ids = set(list(set(recent['mon_id'])))

    uploaded = list_from_txt('mon\\sds.mon')
    upload_all = list_from_txt('mon\\upload_all.mon')
    upload_maps = list_from_txt('mon\\upload_only_maps.mon')
    upload_historical = list_from_txt('mon\\upload_only_historical.mon')
    upload_images = list_from_txt('mon\\upload_only_images.mon')

    to_update_mon = [mon for mon in recent_mon_ids if mon in uploaded and mon not in upload_all and mon not in upload_maps and mon not in upload_historical and mon not in upload_images]

    #print("Number of those monuments already uploaded to HeidIcon that are not marked for upload: {}".format(len(to_update_mon)))

    file = open("mon\\recently_changed.mon", 'w')
    for mon_id in to_update_mon:
        file.write(mon_id+"\n")
    file.close()


def prepare_metadata_from_mon(danam_df,year,month,date,ready_all,ready_maps,ready_historical,ready_images,ready_recent):
    upload_all = prepare_metadata(danam_df,
                    "mon/upload_all.mon",
                    "fixes\\all.fix",
                    ready_all,
                    label = "ALL"
                    )

    upload_maps = prepare_metadata(danam_df,
                        "mon/upload_only_maps.mon",
                        "fixes\\maps.fix",
                        ready_maps,
                        query="df['filename'].str.contains('_D_')",
                        label = "MAPS"
                        )

    upload_historical = prepare_metadata(danam_df,
                        "mon/upload_only_historical.mon",
                        "fixes\\historical.fix",
                        ready_historical,
                        query="df['filename'].str.contains('_H_')",
                        label = "HISTORICAL"
                        )
                
    upload_images = prepare_metadata(danam_df,
                        "mon/upload_only_images.mon",
                        "fixes\\images.fix",
                        ready_images,
                        query="df['filename'].str.contains('_D_') == False",
                        label = "ONLY PHOTOGRAPHS"
                        )

    get_recent_changes(danam_df,year,month,date)

    upload_recent_changes = prepare_metadata(danam_df,
                        "mon\\recently_changed.mon",
                        "fixes\\recent.fix",
                        ready_recent,
                        query=f"df['lastModified'] > datetime({year}, {month}, {date})",
                        label = 'RECENT CHANGES'
                        )
    return upload_all,upload_historical,upload_images,upload_maps,upload_recent_changes

