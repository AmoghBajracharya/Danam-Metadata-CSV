import pandas as pd

from scripts.SDS import *
from scripts.clean_json import clean_json


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def load_data(heidicon_export, danam_export):
    # read heidicon export
    heidicon_df = pd.read_excel(heidicon_export, engine='openpyxl')

    # read danam export
    danam_export = danam_export
    danam_images = clean_json(danam_export)
    danam_df = pd.DataFrame(danam_images)

    return heidicon_df, danam_df

def get_info_for_monument(mon_id, heidicon_df, danam_df, root="Z:\\Data\\Monuments"):

    res = {}
    res['mon_id'] = mon_id
    sds_df = get_images(root, mon_id)

    ###
    heidicon_mon = heidicon_df.loc[(heidicon_df['obj_systematik']==mon_id) | (heidicon_df['obj_systematik']==mon_id.upper())]
    heidicon_mon_nometa = heidicon_df.loc[ heidicon_df["_standard#de-DE"] == mon_id.upper()]

    res['heidicon_img'] = heidicon_mon.shape[0] + heidicon_mon_nometa.shape[0]
    res['heidicon_nometa'] = heidicon_mon_nometa.shape[0]

    danam_mon = danam_df.loc[(danam_df['mon_id']==mon_id) | (danam_df['mon_id']==mon_id.upper())]
    res['danam_img'] = danam_mon.shape[0]

    res['danam_nometa'] = danam_mon.loc[~(danam_mon['validCaption'])].shape[0]

    if str(type(sds_df)) == "<class 'pandas.core.frame.DataFrame'>":
        res['sds_img'] = sds_df.shape[0]
    else:
        res['sds_img'] = 0

    ###

    mon_files = file_comparison(mon_id, sds_df, heidicon_df, danam_df)
    res['files'] = mon_files

    # elements of ps1 that is not in ps2
    #ps1[~ps1.isin(ps2)]

    # files missing in DANAM that are in HeidICON
    res['missing_danam'] = list(mon_files['heidicon'][~mon_files['heidicon'].isin(mon_files['danam'])].dropna())
    res['count_missing_danam'] = len(res['missing_danam'])

    # files missing in HeidICON that are in DANAM
    res['missing_heidicon'] = list(mon_files['danam'][~mon_files['danam'].isin(mon_files['heidicon'])].dropna())
    res['count_missing_heidicon'] = len(res['missing_heidicon'])

    return res


def file_comparison(mon_id, sds_df, heidicon_df, danam_df):
    if str(type(sds_df)) == "<class 'pandas.core.frame.DataFrame'>":
        sds_files = sds_df["filename"].reset_index()
        sds_files = sds_files['filename'].str.replace(" ", "_").sort_values()

    danam_mon = danam_df.loc[(danam_df['mon_id']==mon_id) | (danam_df['mon_id']==mon_id.upper())]
    danam_files = danam_mon['filename'].str.replace(" ", "_").sort_values().reset_index().drop(['index'], axis=1)

    heidicon_mon = heidicon_df.loc[(heidicon_df['obj_systematik']==mon_id) | (heidicon_df['obj_systematik']==mon_id.upper())]
    heidicon_mon_nometa = heidicon_df.loc[ heidicon_df["_standard#de-DE"] == mon_id.upper()]
    heidicon_mon = pd.concat([heidicon_mon, heidicon_mon_nometa])
    heidicon_files = heidicon_mon['ressourcen:lk_objekt_id[].asset#original_filename'].str.replace(" ", "_").str.replace(".CR2", "").str.replace(".TIF", "").str.replace(".ARW", "").str.replace(".dng", "")

    heidicon_files = heidicon_files.str.replace(".jpg", '').str.replace(".JPG", '').str.replace(".pdf", '').str.replace(".html", '')
    heidicon_files = heidicon_files.sort_values().reset_index().drop(['index'], axis=1)

    if str(type(sds_df)) == "<class 'pandas.core.frame.DataFrame'>":
        mon_files = pd.concat([sds_files, danam_files, heidicon_files], axis = 1)
        mon_files.columns = ['sds', 'danam', 'heidicon']
    else:
        mon_files = pd.concat([danam_files, heidicon_files], axis = 1)
        mon_files.columns = ['danam', 'heidicon']    

    return mon_files


    