import codecs
import argparse
import html, json
import re, os, ast
from datetime import datetime

from scripts.caption_processing import metadata_from_caption, valid_caption

'''
exports image array as a json file that can easily be re-imported into python and used again for other scripts. JSON is named
    'danam_metadata_<export date>_<export time>.json'
'''
def write_json(array, dir="json/cleaned-metadata/"):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    #filename = "danam_metadata_{}.json".format(now)
    filename = "{}.json".format(now)
    with open(dir+filename, 'w') as file:
        json.dump(array, file)

'''
reads danam json export and extract only the images
input: danam json export file
output: array of dictionaries of all images in danam
'''
def read_danam_export(danam_export):
   
    source_json = json.load(codecs.open(danam_export, 'r', 'utf-8'))

    res = []
    for object in source_json["business_data"]["resources"]:
        #danam_id = object['resourceinstance']['resourceinstanceid']
        mon_ids = [tile["data"]["28294784-9323-11e9-bf23-0242ac120006"]["en"]["value"].strip() for tile in object['tiles'] if '28294784-9323-11e9-bf23-0242ac120006' in tile['data'].keys() and tile["data"]["28294784-9323-11e9-bf23-0242ac120006"] is not None]
        nepali_mon_id = [tile['data']['27b69ca2-9323-11e9-a015-0242ac120006']["en"]["value"].strip() for tile in object['tiles'] if '27b69ca2-9323-11e9-a015-0242ac120006' in tile['data'].keys() and tile['data']['27b69ca2-9323-11e9-a015-0242ac120006'] is not None]
        #editorials= [tile["data"]["66fd9c70-ce1b-11e9-b993-0242ac140002"] for tile in object['tiles'] if '66fd9c70-ce1b-11e9-b993-0242ac140002' in tile['data'].keys()]

        for tiles in object['tiles']:
            if "'type': 'image/" in str(tiles.get('data')) or "'type': 'application/pdf" in str(tiles.get('data')):

                #clean string from html tags
                jsonstr = str(tiles.get('data'))
                jsonstr = jsonstr.replace("</p>", "")
                jsonstr = jsonstr.replace("<p>", "")
                jsonstr = jsonstr.replace("&nbsp;", " ")

                pos = jsonstr.find("[{")
                reptext =jsonstr[pos-39:pos-3].strip()
                jsonstr = jsonstr.replace(reptext, "imagedata")

                TAG_RE = re.compile('<[^>]+>')
                jsonstr = TAG_RE.sub('', jsonstr)

                jsonrawdata = ast.literal_eval(jsonstr)
                #jsonrawdata['danam_id'] = danam_id
                jsonrawdata['mon_ids'] = mon_ids
                jsonrawdata['nepali_mon_id'] = nepali_mon_id
                #jsonrawdata['editorials'] = editorials
                res.append(jsonrawdata)

    return res


'''
captions are stored as various nodes (e.g "fa9e551a-b100-11e9-b84d-0242ac120006")
these should just be combined together into one string. Moreover, unecessary texts, such as the standard copyright text on primary images, also need to be removed
input: an image dictionary
output: caption as one string variable, textfield
'''
def get_caption(image):
    keys = list(image.keys())
    keys.remove('imagedata')
    #keys.remove('danam_id')
    keys.remove('mon_ids')
    keys.remove('nepali_mon_id')
    #keys.remove('editorials')
    
    try: 
        keys.remove("4b84bd80-9eea-11e9-8b93-0242ac120006")
        keys.remove('4b84aa48-9eea-11e9-8b93-0242ac120006')
        keys.remove('0266d44a-9ee9-11e9-98a0-0242ac120006')
        keys.remove('0266d44a-9ee9-11e9-98a0-0242ac120006')
        #keys.remove("ff59de54-a321-11e9-8e7b-0242ac140004")
        #keys.remove("ff59be60-a321-11e9-8e7b-0242ac140004")
        #keys.remove("39e9bb98-b100-11e9-a7ae-0242ac120006 ")
    except:
        pass

    textfield = ""
    notes = ""
    for key in keys:
        if image[key] is not None:
            if textfield == "":
                textfield += str(image[key]) + " "
            else:
                notes = image[key]
                textfield += "; " + str(image[key]) + " "


    danam_tags = re.compile('\\w{8}-\\w{4}-\\w{4}-\\w{4}-\\w{12}')
    if danam_tags.search(textfield) is not None:
        textfield = danam_tags.sub('', textfield)
    
    textfield.replace("&nbsp;", " ")
    textfield = html.unescape(textfield)

    #'''
    #check if copyright text is included, this need to be removed
    copyright_text = "The latest report will always be available in DANAM (this page).\n\n"
    if copyright_text in textfield:
        textfield_paragraph = textfield.split(copyright_text)
        text_index = 0
        for index in range(len(textfield_paragraph)):
            if "If not otherwise stated" not in textfield_paragraph[index]:
                text_index = index
        textfield = textfield_paragraph[text_index]
    
    to_remove = "If not otherwise stated, all images and texts in this monument folder are published under Creative Commons Attribution 4.0 License (CC BY-SA 4.0), and the copyright lies with NHDP. All visuals of this monument folder and more are (or will be) also stored in heidICON, the object and multimedia database of Heidelberg University. (Type the ID-number or key words in the first line and click the search field.) You will also find the initial report there. The latest report will always be available in DANAM (this page)."

    textfield = textfield.replace(to_remove, "")

    to_remove = "If not otherwise stated, all images and texts in this folder are published under Creative Commons Attribution 4.0 License (CC BY-SA 4.0), and the copyright lies with NHDP. All visuals of this monument folder and more are (or will be) also stored in heidICON, the object and multimedia database of Heidelberg University (type the ID-number or key words in the first line and click the search field). You will also find the initial report there. The latest report will always be available in DANAM (this page)."

    textfield = textfield.replace(to_remove, "")
    textfield = textfield.replace("\n", " ")

    fixes = [
           
            "{'de': {'direction': 'ltr', 'value': ''}, 'dev': {'direction': 'ltr', 'value': ''}, 'en': {'direction': 'ltr', 'value': '"
            ,"Attribution 4.0 License (CC BY-SA 4.0), . (Type the ID-number or key words in the first line and click the search field.) . The latest report will always be available in DANAM (this page).; "
            ,"{'de': {'direction': 'ltr', 'value': ''}, 'dev': {'direction': 'ltr', 'value': ''}, 'en': {'direction': 'ltr', 'value': None}, 'en-US': {'direction': 'ltr', 'value': ''}} " 
            ,"{'de': {'direction': 'ltr', 'value': ''}, 'dev': {'direction': 'ltr', 'value': ''}, 'en': {'direction': 'ltr', 'value': '"
            ,"\\n'}, 'en-US': {'direction': 'ltr', 'value': ''}} "
            ,"{'de': {'direction': 'ltr', 'value': ''}, 'dev': {'direction': 'ltr', 'value': ''}, 'el': {'direction': 'ltr', 'value': ''}, 'en': {'direction': 'ltr', 'value': '"
            ,"\\n'}} "
            ,"'en-US': {'direction': 'ltr', 'value': ''}, 'fr': {'direction': 'ltr', 'value': ''}, 'pt': {'direction': 'ltr', 'value': ''}, 'ru': {'direction': 'ltr', 'value': ''}, 'zh': {'direction': 'ltr', 'value': ''}}"
            ,"\\n'}, '},"
            ," None}, 'en-US': {'direction': 'ltr', 'value': ''}}"
            ,"{'de': {'direction': 'ltr', 'value': ''}, 'dev': {'direction': 'ltr', 'value': ''}, 'en': {'direction': 'ltr', 'value': "
            ,"{'de': {'direction': 'ltr', 'value': ''}, 'dev': {'direction': 'ltr', 'value': ''}, 'en': {'direction': 'ltr', 'value': None}, 'en-US': {'direction': 'ltr', 'value': ''}}"
            ,"{'en': {'direction': 'ltr', 'value': '"
            ,"’\\n\\n \\n'}}"
            ,"’\\n\\n"
            ,"\\n\\n"
            ,"''}, 'en-US': {'direction': 'ltr', 'value': ''}}'"
            ,"{'en': {'direction': 'ltr', 'value': "
            ,"{'de': {'direction': 'ltr', 'value': ''}, 'dev': {'direction': 'ltr', 'value': ''}, 'en': {'direction': 'ltr', 'value': None}, 'en-US': {'direction': 'ltr', 'value': ''}} ; {'de': {'direction': 'ltr', 'value': ''}, 'dev': {'direction': 'ltr', 'value': ''}, 'en': {'direction': 'ltr', 'value': '"
            ," ''}, 'en-US': {'direction': 'ltr', 'value': ''}}"
            ,"{'de': {'direction': 'ltr', 'value': ''}, 'dev': {'direction': 'ltr', 'value': ''}, 'en': {'direction': 'ltr', 'value': '"
            ,"{'de': {'direction': 'ltr', 'value': ''}, 'dev': {'direction': 'ltr', 'value': ''}, 'en': {'direction': 'ltr', 'value': '\n\n'}, 'en-US': {'direction': 'ltr', 'value': ''}} ; {'de': {'direction': 'ltr', 'value': ''}, 'dev': {'direction': 'ltr', 'value': ''}, 'en': {'direction': 'ltr', 'value': '"
            ,"'\\n; "
            ,"\\n; "
            ,"'}, 'en-US': {'direction': 'ltr', 'value': ''}}"
            ,"{'en': {'direction': 'ltr', 'value': '"
            ,"\\n"
            ,"If not otherwise stated, all images and texts in this folder are published under Creative Commons"
            , "If not otherwise stated, all images and texts in this monument folder are published under Creative Commons"
            , "Attribution 4.0 License \(CC BY-SA 4.0\),"
            , "Attribution 40 License \(CC BY-SA 40\),"
            , "and the copyright lies with NHDP. All visuals of this monument folder"
            ," and more are \(or will be\) also stored in heidICON," 
            , "and more are also stored in heidICON,"
            , "the object and multimedia database of Heidelberg University" 
            , "\(Type the ID-number or key words in the first line and click the search field.\)" 
            , "\(type the ID-number or key words in the first line and click the search field.\)" 
            , "\(type the ID-number or key words in the first line and click the search field\)" 
            , "\(type the ID-number or keywords in the first line and click the search field\)." 
            , "You will also find the initial report there"
            , "The latest report will always be available in DANAM \(this page\)."
            , "You will also find the initial report there. The latest report will always be available in DANAM \(this page\)."
            #, "."
            , "Attribution 40 License \(CC BY-SA 40\),  and more are \(or will be\) also stored in heidICON,  \(Type the ID-number or key words in the first line and click the search field\)  The latest report will always be available in DANAM \(this page\)"
            ]
    
    for fix in fixes:
        textfield = textfield.replace(fix, "")

    #'''

    if "(CC BY-SA 4.0)." in textfield:
        textfield = textfield.split('(CC BY-SA 4.0).')[1].strip()

    if textfield.strip().startswith("; "):
        textfield = textfield.split("; ", 1)[1]
    if textfield.strip().endswith(";"):
        textfield = textfield.rsplit(";", 1)[0]
    return textfield

'''
get metadata only available through danam exporrt, such as image filename, mon_id, classification(?), and notes
input:
image_json - image dictionary from danam
image_metadata - metadata dictionary
'''
def metadata_from_json(image_json, image_metadata):


    #image_metadata['danam_id'] = image_json['danam_id']
    #get filename
    #separates name and file extension, but file extension remains.
    image_metadata['filename_danam'] = os.path.splitext(image_json['imagedata'][0]['name'])[0].replace(' ', '_')
    image_metadata['filetype'] = os.path.splitext(image_json['imagedata'][0]['name'])[1].replace(' ', '_')


    image_metadata['filename_danam_2'] = image_json['imagedata'][0]['url'].replace('/files/uploadedfiles/', '')
    image_metadata['filetype_2'] = os.path.splitext(image_metadata['filename_danam_2'])[1].replace('.','')
    
    if image_metadata['filename_danam_2'] != "LAL0880_JTohn1F.jpg":
        image_metadata['filename_danam_2'] = re.sub('_[a-zA-Z0-9]{7}.[a-zA-Z]{3}', "", image_metadata['filename_danam_2'])
    image_metadata['filename_danam_2'] = os.path.splitext(image_metadata['filename_danam_2'])[0]
    
    
    if image_metadata['filetype_2'].strip() == "":
        image_metadata['filename'] = image_metadata['filename_danam']
    else:
        image_metadata['filename'] = image_metadata['filename_danam_2']


    #delete weird filename ending from DANAM
    #filename_ending = re.compile('\_(?!section)(?!Section)[a-zA-Z0-9]{7}\\b')
    #if filename_ending.search(image_metadata['filename']) == '_section'== True:
    #    image_metadata['filename'] = image_metadata['filename']
    #else:
    #    image_metadata['filename'] = filename_ending.sub('', image_metadata['filename'])


    #get mon_id
    image_metadata['mon_id'] = ""

    for mon_id in [i for i in image_json['mon_ids'] if i is not None]:
        regex_search = re.search('[A-Z]{3}[0-9]{3,4}', mon_id)
        if regex_search != None:
            image_metadata['mon_id'] = mon_id
 
    if image_metadata['mon_id'] == "":
        """    
        fname = image_metadata['filename']
        #print(fname)
        regex_search = re.search('[A-Z]{3}[0-9]{3,4}', fname)
        if regex_search == None:
            mon_id = ""
        else:
            mon_id = regex_search.group(0)
        image_metadata['mon_id'] = mon_id 
        """
        #print(image_json['nepali_mon_id'])
        if len(image_metadata['nepali_mon_id']) > 0:
            if "||" in image_json['nepali_mon_id'][0]:
                mon_id = image_json['nepali_mon_id'][0].split("||")[1].strip()
                image_metadata['mon_id'] = mon_id
 
    #try to get image classification - will be overwritten later, not sure if still needed? maybe for social/historical photograph???
    classification="architectural photograph"
    if "fb0a532e-b8f7-11e9-b8a9-0242ac120007" in image_json.keys():
        classification = "photo"
    elif "1aed634a-c332-11e9-af2c-0242ac140003" in image_json.keys():
        classification = "inscription"
    elif "0266d2a6-9ee9-11e9-98a0-0242ac120006" in image_json.keys():
        classification = "architectural drawing"
    image_metadata['classification'] = classification

    #try to get extra notes about image from danam
    notes= ""
    try:
        notes= image_json['e02c2194-b100-11e9-87e2-0242ac120006'].strip().replace('&nbsp;', ' ')
    except Exception as e:
        pass
    try:
        notes= image_json['fa9e551a-b100-11e9-b84d-0242ac120006'].strip().replace('&nbsp;', ' ')
    except Exception as e:
        pass
    try:
        notes= image_json['4b84b47a-9eea-11e9-8b93-0242ac120006'].strip().replace('&nbsp;', ' ')
    except Exception as e:
        pass
    image_metadata['notes'] = notes

    image_metadata['heidoc']=''
    image_metadata['heidata']=''

'''
get DANAM metadata, both from caption and DANAM json export
input:
    image - partial json from DANAM
    caption_parts - caption split by ";"
output:
    dictionary image_metadata
'''
def get_metadata(image, caption_parts):
    image_metadata = {}
    metadata_from_json(image, image_metadata)
    metadata_from_caption(caption_parts, image_metadata)
    return image_metadata


'''
replace text using rules in a dictionary
input:
    text - text where substrings need to be replacedd
    dict - dictionary
    strip - Bool value, False does not strip white spaces in dict keys
output:
    none
'''
def replace_w_json(text, dict, strip=False):
    for key in dict.keys():
        if strip:
            text = text.replace(key.strip(), dict[key])
        else:            
            text = text.replace(key, dict[key])
    
    return text
        
        
'''
creates a HeidIcon compatible CSV file out of DANAM json export file
input:
    danam_export - DANAM json export
    json_export - if True, will also write a json output in addition to a csv output.
output:

'''
def clean_json_old(danam_export, verbose=False, fix=True):
    images = read_danam_export(danam_export)
    metadata = []
    metadata_report = []
        
    log = "log/cleanup.log"
    logfile = codecs.open(log, 'w', 'utf-8')

    prev_mon_id = "ABCDE"

    for image in images:

        caption = get_caption(image)
    
        if fix:
            fixes = json.load(open('json/dict/fixes.json'))[0]
            caption = replace_w_json(caption, fixes)
            caption = re.sub(r': ([0-9]{4}-[0-9]{2}-[0-9]{2})', r'; \1 ;', caption)

        parts = caption.split(';')

        if not valid_caption(caption) or len(parts) < 3:
            logfile.write("\"{}\"\n is not a valid caption!\n".format(caption.replace("\n", "")))
            if verbose:
                print("\"{}\"\n is not a valid caption!\n".format(caption))
            
            image_metadata = {}
            metadata_from_json(image, image_metadata)
            
                
        else:
            #logfile.write("Caption is correct and is being processed...\n")
            #if verbose:
            #    print("Caption is correct and is being processed...\n")
      
            image_metadata = get_metadata(image, parts)
            mon_id = image_metadata['mon_id']
            metadata.append(image_metadata)
            if prev_mon_id != mon_id:
                prev_mon_id = mon_id
                metadata_report.append(image_metadata)
    
    write_json(metadata, dir="json/cleaned-metadata/image_") 
    write_json(metadata_report, dir="json/cleaned-metadata/report_")

            
    logfile.write("Images from DANAM: {}\nImages exported to CSV: {}\n".format(len(images), len(metadata)))
    print("Images from DANAM: {}\nImages exported to CSV: {}\n".format(len(images), len(metadata)))
    
    logfile.close()

'''
'''
def clean_json(danam_export):
    # collect only danam images
    danam_images = read_danam_export(danam_export)

    # cleaning and geting metadata
    for image in danam_images:
        image['danam_caption'] = get_caption(image).replace("\n", '')
        
        to_delete = "If not otherwise stated, all images and texts in this monument folder are published under Creative Commons Attribution 4.0 License (CC BY-SA 4.0), and the copyright lies with NHDP. All visuals of this monument folder and more are (or will be) also stored in heidICON, the object and multimedia database of Heidelberg University. (Type the ID-number or key words in the first line and click the search field.) You will also find the initial report there. The latest report will always be available in DANAM (this page)"
        image['danam_caption'] = image['danam_caption'].replace(to_delete, "")
        image['empty_column'] = ""   
        metadata_from_json(image, image)

        if image['filename'] == 'KIR0067_I_003_20210907_01':
            image['filename'] = image['filename'].replace("7_01", "7")
            image['filename_danam'] = image['filename']

        caption = image['danam_caption']
        
        fixes = json.load(open('json/dict/fixes.json'))[0]
        caption = replace_w_json(caption, fixes)
        
        caption = re.sub(r': ([0-9]{4}-[0-9]{2}-[0-9]{2})', r'; \1', caption)
        caption = re.sub(r', ([0-9]{4}-[0-9]{2}-[0-9]{2})', r'; \1', caption)
        caption = re.sub(r'; ([0-9]{4}), courtesy', r'; \1; courtesy', caption)
        
        image['validCaption'] = valid_caption(caption)
        #image['old_validCaption'] = valid_caption(caption)

        parts = caption.split(';')

        if image['validCaption'] and len(parts)>=3:
            metadata_from_caption(parts, image)
        else:
            image['validCaption'] = False     
    
            
        image['lastModified'] = image['imagedata'][0]['lastModified']
        timestamp = int(image['lastModified'])
        image['lastModified'] = datetime.fromtimestamp(timestamp/1000)
        
        try:
            del image['imagedata']
            #del image['editorials']
            del image['mon_ids']
        except: 
            pass
        
        dels = [key for key in image.keys() if image[key]==None]
        for i in dels:
            del image[i]

    return danam_images

if __name__ == "__main__":

    '''
    use argparser to create a command promt tool
    '''
    argparser = argparse.ArgumentParser(description="convert DANAM JSON export into HeidIcon CSV")

    argparser.add_argument("-f", "--file", required=True, help="DANAM json dump")
    argparser.add_argument("-v", "--verbose", dest='verbose', required=False, action="store_true", help="output logs in command line")
    argparser.add_argument("-no-fix", required=False, dest='nofix', action="store_false", help="set to not fix possible mistakes in the caption")
    args = argparser.parse_args()
    
    print("Cleaning DANAM JSON metadata...\n")
        
    clean_json(args.file, verbose=args.verbose, fix=args.nofix)
    print("Complete!")