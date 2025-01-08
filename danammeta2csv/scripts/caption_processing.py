'''
python module that includes all necessary caption processing functions
'''
import json
import re

########### dictionary definitions ###########
with open("json/dict/heidicon_id.json", encoding="utf-8") as f:
    heidicon_id = json.load(f)[0]


gnd_dict = {
            'architekturzeichnung': '4068827-6',
            'architekturfotografie': '4002855-0',
            'fotografie': '4045895-7',
            'skizze': '4181668-7',
            'grafik': '4021845-4',
            'gemälde': '4037220-0',
            'karte': '4029783-4',
            'inschrift': '4027107-9',
            'bericht': '4128022-2',
}

gnd_trans = {
            'architectural drawing':'Architekturzeichnung',
            'architectural photograph': 'Architekturfotografie',
            'photo':'Fotografie',
            'sketch':'Skizze',
            'graphic': 'Grafik',
            'painting': 'Gemälde',
            'location map': 'Karte',
            'inscription':'Inschrift',
            'report': 'Bericht',
}

licence_dict = {
            'CC BY-SA 4.0' : 'https://uni-heidelberg.de/nhdp',
            'Free access - no reuse': '',
}

##############################################
'''
read monument URL id from a simple txt file (one id per line). 
IDs can be commented as follows:

017a4a8f-b183-4e57-9ff9-54ae1145378f #LAL1870
60a8a8e0-e4e8-11e9-b125-0242ac130002 #LAL4250
cfc0099e-f15d-4c3e-8d8f-e048222f7956 #KIR0020

IDs can be commented python-wise with #

'''
def list_from_txt(textfile):
    ids = []

    with open(textfile, 'r', encoding="utf-8") as file:
        for line in file:
            if line[0] == "#" or line.strip() == "" : 
                continue
            id = line.split(" ")[0].strip()
            ids.append(id)

    return ids


#check date format, must follow DANAM guidelines

def isDate(date):
    date_formats = [
        "[0-9]{4}-[0-9]{2}-[0-9]{2}$",     # yyyy-mm-dd
        "[0-9]{4}-[0-9]{2}$",               # yyyy-mm
        "[0-9]{4}$",                        # yyyy
        "[0-9]{4}-1[0-2]$|[0-9]{4}-0[1-9]$", # yyyy-mm (valid months)
        "[0-9]{4}-[0-9]{4}$",               # yyyy-yyyy
        "[0-9]{4}–[0-9]{4}$",               # yyyy–yyyy (en dash)
        "ca\.? ?[0-9]{4}$",                 # ca. yyyy
        "ca [0-9]{4}$"                      # ca yyyy
    ]

    date = date.strip()  # Trim whitespace from the input
    for date_format in date_formats:
        search = re.search(date_format, date)
        if search:
            # If there's a match and it starts at the beginning of the string
            if search.span(0)[0] == 0:
                return True
    return False  # Return False if no pattern matches

#check caption for keywords
def valid_caption(caption):
    keywords = list_from_txt("log/keywords.txt")
    for keyword in keywords:
        pattern_search = re.search(keyword, caption)
        if pattern_search is not None:
            return True
    
    return False

#date processing
def get_date(textfield_part, image_metadata, short_index):
    #date1
    image_metadata['date1'] = ""
    #date2
    image_metadata['date2'] = ""
    #date
    image_metadata['date'] = ""
    #date3
    image_metadata['date3'] = ""

    date = textfield_part.strip()
    date = date.split("\n")[0]
    print(date)

    if isDate(date):
        image_metadata['date'] = date
        short_index = 1

    regex_date_range1 = re.search('[0-9]{4}-[0-9]{4}', date)
    if regex_date_range1 != None:
        image_metadata['date']=date.split("-")[0]
        image_metadata['date3']=date.split("-")[1]
    
    regex_date_range2 = re.search('[0-9]{4}–[0-9]{4}', date)
    if regex_date_range2 != None:
        image_metadata['date']=date.split("–")[0]
        image_metadata['date3']=date.split("–")[1]

    if "ca." in image_metadata['date'] or "ca" in image_metadata['date']: 
         image_metadata['date2'] = image_metadata['date']
         image_metadata['date'] = ""
    
#agent, role, and classification processing
def get_agent_role_classification(textfield_part, image_metadata):
    
    
    image_metadata['agent'] = ""
    image_metadata['role'] = ""
    image_metadata['agent2'] = ""
    image_metadata['role2'] = ""
    #classification - auch von node-id
    classification = ""
    agents = []

    classification_and_agent = textfield_part.split('by')

    #falls foto
    if "photo by" in textfield_part or "photography by"  in textfield_part:
        agents = [item.lstrip().strip("&nbsp;") for item in classification_and_agent[1:]]
        
        if len(agents) > 0 :
            try:
                image_metadata['agent'] = heidicon_id[agents[0].strip()]
            except Exception as e:
        
                image_metadata['agent'] = agents[0].strip()
                pass

        #role_agent1
        classification = classification_and_agent[0].strip().lower().lstrip(' ')
        if "photo" in classification:
            role = "photographer"
            classification = "architectural photograph"
        else:
            role = "draftsman"
        image_metadata['role'] = role

        if "inscription" in image_metadata['caption'].lower():
            classification = "inscription"

        #agent 2
        if len(agents) == 2:
            try:
                image_metadata['agent2'] = heidicon_id[agents[1].strip()]
            except Exception as e:
                image_metadata['agent2'] = agents[1].strip()
                pass

            #role_agent2
            image_metadata['role2'] = role

        else:
            image_metadata['agent2'] = ""

            #role_agent2
            image_metadata['role2'] = ""

    #falls nicht foto
    else:
        classification = 'architectural drawing'        
        try:
            agents = classification_and_agent[1].split(',')
        except:
            agents = []

   
        
        try:
            image_metadata['agent'] = heidicon_id[agents[0].strip()]
        except Exception as e:
            if len(agents)<0:
                image_metadata['agent'] = agents[0]
        

        role = "draftsman"
        image_metadata["role"] = role
        #agent 2
        if len(agents) == 2:
            try:
                image_metadata['agent2'] = heidicon_id[agents[1].strip()]
            except Exception as e:
                image_metadata['agent2'] = agents[1]
                pass

            #role_agent2
            image_metadata['role2'] = role

        else:
            image_metadata['agent2'] = ''

            #role_agent2
            image_metadata['role2'] = ''

        caption_extra = classification_and_agent[0].strip()
        image_metadata["caption"] += ", "+caption_extra
        if "map" in image_metadata["caption"]:
            classification = "location map"
        if "sketch" in image_metadata["caption"]:
            classification = "sketch"

            
            
    if classification != "":
        image_metadata['classification'] = classification

#additional informations
def get_copyright_etc(textfield_parts, image_metadata, short_index, classification):
    #owner/copyright
    image_metadata['copyright'] = "Nepal Heritage Documentation Project"

    #references
    image_metadata['source'] = ""

    #license default
    license = "CC BY-SA 4.0"

    agent3 = ''
    update_date = ''
    #nochmal ueberpruefen..
    if len(textfield_parts) > (3 - short_index):
        for part in textfield_parts[(3 - short_index):]:
            if "courtesy of" in part.lower() or "no reuse" in part.lower():
                if image_metadata['copyright'] == "Nepal Heritage Documentation Project":
                    image_metadata['copyright'] = part.strip()
                license = "Free access - no reuse"
            elif "source" in part.lower():
                image_metadata['source'] = part.replace('Source:', '').replace('source:', '')
                image_metadata['source'] = image_metadata['source'].strip()
            elif "updated by" in part:
                try:
                    agent3_and_update_date = part.split(",")
                    agent3 = agent3_and_update_date[0].replace("updated by ", "").strip()
                    update_date = agent3_and_update_date[1].strip()
                except (IndexError, ValueError):
                    pass
    if "free access" in image_metadata["copyright"]:
        image_metadata["copyright"] = ""
    #print(image_metadata['copyright'])
    #class_code
    if classification != "":
        class_code = gnd_dict[gnd_trans[classification].lower()]
    else:
        class_code = ""
    image_metadata['class_code'] = class_code

    #classification
    #
    image_metadata['classification'] = gnd_trans[classification]

    #agent3
    try:
        image_metadata['agent3'] = heidicon_id[agent3.strip()]
    except Exception as e:
        image_metadata['agent3'] = agent3
        pass


    #date_scan
    image_metadata['date_scan'] = update_date.split("\n")[0]

    #licence
    image_metadata['license'] = license

    #right_url
    if license != "":
        url = licence_dict[license]
    else:
        url = ""
    #print("url = ",url)
    image_metadata['url'] = url

    #rights_text
    if license=='CC BY-SA 4.0':
        rights_text="Nepal Heritage Documentation Project"
    else:
        rights_text=""
    image_metadata['rights_text'] = rights_text

'''
get metadata available through captions (most of the metadata)
input:
textfield_parts - the resulting array from splitting the caption by ";"
image_metadata - metadata dictionary
the function is divided into smaller functions
'''
def metadata_from_caption(textfield_parts, image_metadata):

    # Check if textfield_parts[0] is a dictionary or a string
    if isinstance(textfield_parts[0], dict):
        # Extract the danam_caption from the nested JSON structure
        danam_caption = textfield_parts[0].get('en', {}).get('value', '')
    else:
        # If it's a string, use it directly as danam_caption
        danam_caption = textfield_parts[0]

    # Store the extracted danam_caption in the image_metadata dictionary
    image_metadata['caption'] = danam_caption.strip()

    # Process the rest of the metadata
    short_index=0
    get_date(textfield_parts[2], image_metadata, short_index)
    get_agent_role_classification(textfield_parts[1], image_metadata)
    
    classification = image_metadata['classification']
    get_copyright_etc(textfield_parts, image_metadata, short_index, classification)


if __name__ == '__main__':

    captions = ["Kvātha Bāhāḥ, southern side of the Bāhaḥ with a statue of Padmapāṇi Lokeśvara, view from N; photo by Yogesh Budathoki; 2020-08-04", "Kvātha Bāhāḥ, view from NW; photo by Carl Pruscha; ca. 1974; courtesy of Carl Pruscha; free access – no reuse; source: Carl Pruscha, Kathmandu Valley, 1975, vol. II, p. 199 (P-256)"]

    for caption in captions:
        parts = caption.split(';')

        if  not valid_caption(caption) or len(parts) < 3:
            print("Caption\n\n{}\n\nis not valid!".format(caption))

        else:
            print("Caption is correct and is being processed...")
            image_metadata = {}
            metadata_from_caption(parts, image_metadata)
