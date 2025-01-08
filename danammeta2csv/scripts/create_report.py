import os
import time
import json
import shutil
import getpass
from textwrap import dedent

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#from scripts.write_csv import list_from_txt


## CONSTANT DEFINITION
url = "https://danam.cats.uni-heidelberg.de/report/"

username = getpass.getuser()

if os.name == "posix": #LINUX
    download = "/home/{}/Downloads/".format(username)   
    save_folder = "/home/{}/Documents/DANAM Reports/".format(username)   

else: #WINDOWS
    download = "C:\\Users\\{}\\Downloads\\".format(username) 
    save_folder = "C:\\Users\\{}\\Seafile\\Transfers\\".format(username) 




'''
from https://gist.github.com/munro/7f81bd1657499866f7c2
'''
def wait_until_images_loaded(driver, timeout=30):
    """Waits for all images & background images to load."""
    driver.set_script_timeout(timeout)
    driver.execute_async_script(dedent('''
        function extractCSSURL(text) {
            var url_str = text.replace(/.*url\((.*)\).*/, '$1');
            if (url_str[0] === '"') {
                return JSON.parse(url_str);
            }
            if (url_str[0] === "'") {
                return JSON.parse(
                    url_str
                        .replace(/'/g, '__DOUBLE__QUOTE__HERE__')
                        .replace(/"/g, "'")
                        .replace(/__DOUBLE__QUOTE__HERE__/g, '"')
                );
            }
            return url_str;
        }
        function imageResolved(url) {
            return new $.Deferred(function (d) {
                var img = new Image();
                img.onload = img.onload = function () {
                    d.resolve(url);
                };
                img.src = url;
                if (img.complete) {
                    d.resolve(url);
                }
            }).promise();
        }
        var callback = arguments[arguments.length - 1];
        $.when.apply($, [].concat(
            $('img[src]')
                .map(function (elem) { return $(this).attr('src'); })
                .toArray(),
            $('[style*="url("]')
                .map(function () { return extractCSSURL($(this).attr('style')); })
                .toArray()
                .map(function (url) { return imageResolved(url); })
        )).then(function () { callback(arguments); });
        return undefined;
    '''))


'''
start chromedriver with setting for printing to pdf
'''
def chromedriver_init(chromedriverpath = 'chromedriver'):

    if os.name == "posix":
        CHROMEDRIVER_PATH = './{}'.format(chromedriverpath)
    else:
        CHROMEDRIVER_PATH = './{}.exe'.format(chromedriverpath)
        
    options = Options()
    appState = {
        "recentDestinations": [
            {
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }
        ],
        "selectedDestinationId": "Save as PDF",
        "version": 2
        }

    profile = {'printing.print_preview_sticky_settings.appState': json.dumps(appState)}
    profile = {'printing.print_preview_sticky_settings.appState':json.dumps(appState),'download.default_directory':download}
    options.add_experimental_option('prefs', profile)
    options.add_argument('--kiosk-printing')
    #options.add_argument('--headless')

    driver = webdriver.Chrome(options=options, executable_path=CHROMEDRIVER_PATH)
    return driver

'''
get reports from id
'''
def get_reports(df_iterrows, driver):
    for mon in df_iterrows:
        try:
            url_id = mon[1]['danam_url']
            mon_id = mon[1]['mon_id']
            driver.get(url+url_id)
            print(driver.title + " loaded.")
            
            time.sleep(30)
            wait_until_images_loaded(driver)
            driver.execute_script('window.print();')
            
            filename = "DANAM_report_{}.pdf".format(mon_id)
            shutil.move(download+driver.title+".pdf", save_folder+filename)
            print(filename + " downloaded.")
            #break
            
        except:
            continue

    driver.quit()

