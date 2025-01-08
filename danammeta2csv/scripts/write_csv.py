import json
import codecs
import argparse

from datetime import datetime
#from create_report_csv import write_csv_report_metadata



def one_line(text):
    return text.replace("\n", "").strip()

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


'''
exports pre-processed image metadata array into csv file for importing DANAM metadata into HeidIcon. csv file is named
    'danam_metadata_<export date>_<export time>.csv'
if optional parameter dir is not given, the csv will be written in the same folder as the python script
'''
def write_csv(metadata, logfile, dir="csv/", ids=[]):
    
    using_mon_ids = (len(ids)>0)
   
    csv_file_content = ""
    headers = "Filename; Title/caption;	Date inscription/object;	Date photo/drawing text;	Date photo/drawing Y-M-D;	Date photo/drawing to;	Agent 1;	Role of Agent 1;	Agent 2;	Role of Agent 2;	Owner;	References;   ;  Notes;   monument-id;	classification-id;	classification-text;	Agent 3;	Date scan/digitization;	image-licence;	image-right-url;	image-rights-text;	heiDATA-link;	heiDOK-link;\n"
   
    csv_file_content += headers
    for item in metadata:
        try:
            
            # if we are getting only a few monuments based on mon_ids.txt, and item's mon_id is not in mon_ids, skip
            if using_mon_ids and item['mon_id'] not in ids:
                logfile.write("Skipping this item because {} is not in mon_ids.txt.\n".format(item['mon_id']))
                continue
            
            csv_file_content += '\"'+item['filename']+'\"'+";" + '\"'+item['caption']+'\"'+";" + '\"'+item['date1']+'\"'+";" + '\"'+item['date2']+'\"'+";"
            csv_file_content += '\"'+item['date']+'\"'+";" + '\"'+item['date3']+'\"'+";" + '\"'+item['agent']+'\"'+";" + '\"'+item['role']+'\"'+";"
            csv_file_content += '\"'+item['agent2']+'\"'+";" + '\"'+item['role2']+'\"'+";" + '\"'+one_line(item['copyright'])+'\"'+";" + '\"'+one_line(item['source'])+'\"'+";"
            csv_file_content += '\"\"'+";" +'\"'+one_line(item['notes'])+'\"'+";" + '\"'+item['mon_id']+'\"'+";" + '\"'+item['class_code']+'\"'+";" + '\"'+item['classification']+'\"'+";"
            csv_file_content += '\"'+item['agent3']+'\"'+";" + '\"'+item['date_scan']+'\"'+";" + '\"'+item['license']+'\"'+";" + '\"'+item['url']+'\"'+";" + '\"'+item['rights_text']+'\"'+";"
            csv_file_content += '\"'+item['heidata']+'\"'+";" + '\"'+item['heidoc']+'\"'
            
        except Exception as e:
            logfile.write("Key Error! Image entry \'{}\' only has the following keys:\n{}".format( item['filename'],'\n'.join(item.keys())))
            pass

        csv_file_content += "\n"


    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    if using_mon_ids:
        filename = "image_metadata_select_{}.csv".format(now)
    else:
        filename = "image_metadata_all_{}.csv".format(now)
        
    file = codecs.open(dir+filename, 'w', 'utf-8')
    file.write(csv_file_content)
    file.close()

'''
creates a HeidIcon compatible CSV file out of DANAM json export file
input:
    danam_export - DANAM json export
    json_export - if True, will also write a json output in addition to a csv output.
output:

'''
def danam_to_csv(filename, dir="csv/", report=False, ids=[]):

    log = "log/writecsv.log"
    logfile = codecs.open(log, 'w', 'utf-8')
    
    image_metadata = json.load(open(filename))
    report_metadata = json.load(open(filename.replace("image_", "report_")))

    if not report:
        if len(ids) > 0:
            write_csv(image_metadata, logfile, dir, ids)
        else:
            write_csv(image_metadata, logfile, dir)
        
        
    if report:
        if len(ids) > 0:
            write_csv_report_metadata(report_metadata, logfile, dir, ids)
        else:
            write_csv_report_metadata(report_metadata, logfile, dir)
    
    
    logfile.close()

if __name__ == "__main__":

    '''
    use argparser to create a command promt tool
    '''
    argparser = argparse.ArgumentParser(description="convert DANAM JSON export into HeidIcon CSV")

    argparser.add_argument("-f", "--file", required=True, help="Cleaned DANAM json dump")
    argparser.add_argument("-v", "--verbose", dest='verbose', required=False, action="store_true", help="output logs in command line")
    argparser.add_argument("-ids", required=False, type=str, help="export CSV only for monuments in a given txt file")
    argparser.add_argument("-report", "--report-meta", dest='reportmeta', required=False, action="store_true", help="export report metadata as well as image metadata")
    argparser.add_argument("-no-fix", required=False, dest='nofix', action="store_false", help="set to not fix possible mistakes in the caption")
    args = argparser.parse_args()
    
    ids = []
    if args.ids != None:
        print("Reading Monument IDs from "+args.ids)
        ids = list_from_txt(args.ids)
        print("Exporting CSV Metadata for the following monuments:\n")
        print(ids)
        
    else:
        print("Exporting CSV Metadata for all monuments in JSON")
        
    danam_to_csv(args.file, report=args.reportmeta, ids=ids)

