import os
import pandas as pd

root_uploaded = '\\Already uploaded to HeidICON\\'

root_not_uploaded = '\\Not yet uploaded to HeidICON\\'

def get_images(root_dir, mon_id):
    images = set()
    for _, _, files in os.walk(root_dir+root_uploaded+mon_id.upper()):
        for file in files:
            if not (file.endswith('.DS_Store') or file.endswith('.docx') or file.endswith('.doc') or file.endswith('.xlsx') or file.endswith('.db')):
                images.add(file)

    for _, _, files in os.walk(root_dir+root_not_uploaded+mon_id.upper()):
        for file in files:
            if not (file.endswith('.DS_Store') or file.endswith('.docx') or file.endswith('.doc') or file.endswith('.xlsx') or file.endswith('.db')):
                images.add(file)

    if len(images) == 0:
        #print(f"No images found for monument {mon_id}")
        return -1
    
    else:
        cleaned_info = []

        for img in images:
            info = {}
            info['filename'] = img.split(".")[0]
            info['filetype'] = img.split(".")[1]
            if "_D_" in img:
                info['image_type'] = 'drawing'
            elif "_P_" in img:
                info['image_type'] = 'photograph'
            elif "_H_" in img:
                info['image_type'] = 'historical image'
            elif "_I_" in img:
                info['image_type'] = 'inscription'
            cleaned_info.append(info)
        
    sds_df = pd.DataFrame(cleaned_info)
    sds_df = pd.DataFrame(cleaned_info)
    sds_df_grouped = sds_df.groupby('filename')['filetype'].apply(' '.join).reset_index()
    sds_df = sds_df_grouped.join(sds_df, lsuffix='filename', rsuffix='filename')
    sds_df.set_axis(['filename', 'filetypes', 'filename_dup', 'filetype_dup', 'image_type'], axis=1, inplace=True)
    sds_df.drop(['filename_dup', 'filetype_dup'], axis=1, inplace=True)

    return sds_df
