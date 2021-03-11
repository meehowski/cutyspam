import pickle
import random
import string
import time
import os
import yaml
import argparse
import sys
import urllib.parse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
from random import choice
from random import randint
from time import sleep
from pyvirtualdisplay import Display

args_faster = False

def magick_click(driver, element):
    try:
        element.click()
        return
    except:
        pass

    try:
        js = 'arguments[0].click();'
        driver.execute_script(js, element)
    except:
        pass


def driver_save_html(driver, filename):
    html = driver.execute_script("return document.body.innerHTML;")
    with open(filename,"w") as f:
        f.write(html)

def driver_save_inf(driver, path):
    with open(path + '/cookies.txt', 'wb') as fhandle:
        pickle.dump(driver.get_cookies(), fhandle, protocol=0)

    print("Cookies are saved")
    return

    with open(path + '/local_storage.txt', 'wb') as fhandle:
        #pickle.dump(driver.execute_script('return window.localStorage;'), fhandle, protocol=0)
        pickle.dump(driver.execute_script('var s = window.localStorage, items = {}; ' \
            'for (var i = 0; i < s.length; ++i) ' \
            'items[k = s.key(i)] = s.getItem(k); ' \
            'return items;'), fhandle, protocol=0)

    with open(path + '/session_storage.txt', 'wb') as fhandle:
        #pickle.dump(driver.execute_script('return Storage.sessionStorage;'), fhandle, protocol=0)
        pickle.dump(driver.execute_script('var s = Storage.sessionStorage, items = {}; ' \
            'for (var i = 0; i < s.length; ++i) ' \
            'items[k = s.key(i)] = s.getItem(k); ' \
            'return items;'), fhandle, protocol=0)

def driver_load_inf(driver, path):
    try:
        with open(path + '/cookies.txt', 'rb') as fhandle:
            items = pickle.load(fhandle)
            for item in items:
                #print("Cookie", item)
                driver.add_cookie(item)

        print("Loaded cookies")
        return

        with open(path + '/local_storage.txt', 'rb') as fhandle:
            items = pickle.load(fhandle)
            for [item, value] in items:
                #print("ls", item)
                driver.execute_script('window.localStorage.setItem("' + item + '", "' + value + '");')

        with open(path + '/session_storage.txt', 'rb') as fhandle:
            items = pickle.load(fhandle)
            for [item, value] in items:
                #print("ss", item)
                driver.execute_script('Storage.sessionStorage.setItem("' + item + '", "' + value + '");')
    except Exception as ex:
        print("Unable to load cookies", ex)
        #print(ex)

def spam_start(args):
    if args.virtual == True:
        virtual_display = Display(visible=0, size=(800, 600))
        virtual_display.start()

        print('Starting virtual Webdriver')
    else:
        print('Starting Webdriver')

    user_agents = [
        # Random list of top UAs for mac and windows/ chrome & FF
        #'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        #'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        #'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/74.0',
        #'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/74.0',
        #'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:75.0) Gecko/20100101 Firefox/75.0'
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'
    ]

    user_agent = choice(user_agents)
    print("User agent:", user_agent)

    browser = 'chrome'

    if browser == 'firefox':
        # firefox
        profile = webdriver.FirefoxProfile()
        session_ua = choice(user_agents)
        profile.set_preference('general.useragent.override', session_ua)
        driver = webdriver.Firefox(profile)
    elif browser == 'chrome':
        # chrome
        options = webdriver.ChromeOptions() 
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome('/usr/local/bin/chromedriver')

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""})
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": user_agent}})

    else:
        raise Exception('Browser not specified')

    driver.maximize_window()
    driver.set_window_size(1024, 768)
    #driver.get('https://www.google.com/search?hl=en&as_q=%22request+callback%22&cr=countryCA&as_qdr=all&start=' + str(random.randint(1,50)))
    #driver.get('https://duckduckgo.com/?q=%22request+callback%22+%22phone+number%22&ia=web&res=' + str(random.randint(1,50)))
    driver.get('https://duckduckgo.com/?q=%22request+callback%22+%22phone+number%22+submit&t=h_&ia=web&res=' + str(random.randint(1,50)))
    #driver.get('https://www.google.com/search?hl=en&as_q=%22phone+number%22+%22request+callback%22&cr=countryUS&as_qdr=all&start=' + str(random.randint(1,100)))

    #driver.get('http://www.google.com')
    #element = driver.find_element_by_name('q')
    #element.send_keys('"request callback" "phone number" "canada"')
    #element.submit()

    #random_sleep()

    driver_load_inf(driver, '.')
    print('Webdriver started')
    return(driver)

def load_yml(path):
    with open(path, 'r') as fhandle:
        #data = yaml.load(fhandle, Loader=yaml.FullLoader)
        data = yaml.load(fhandle)

    for item, value in data.items():
        try:
            value = value.strip(' ')
            value = value.replace('\\n', '\n')
            value = value.replace('/n', '\n')
            data[item] = value
            #print(item, data[item])
        except:
            pass

    print(data)

    return [data]

def random_sleep(delay_min=1, delay_max=5):
    if args_faster == True:
        delay_min = round(delay_min / 10)
        delay_max = round(delay_max / 10)

    time.sleep(randint(delay_min, delay_max))

def driver_find(driver, item, value):
    element = None
    set_flag = False
    element_type = None

    try:
        if element == None and set_flag == False:
            element = driver.find_element_by_xpath('//input[@name="' + item + '" and @type="checkbox" and @value="' + value +'"]')
            set_flag = True
            element_type = 'checkbox'
    except:
        pass

    try:
        if element == None and set_flag == False:
            element = driver.find_element_by_xpath('//input[@id="' + item + '" and @type="checkbox" and @value="' + value +'"]')
            set_flag = True
            element_type = 'checkbox'
    except:
        pass

    try:
        if element == None and set_flag == False:
            element = driver.find_element_by_xpath('//input[@name="' + item + '" and @type="radio" and @value="' + value +'"]')
            set_flag = True
            element_type = 'radio'
    except:
        pass

    try:
        if element == None and set_flag == False:
            element = driver.find_element_by_xpath('//input[@id="' + item + '" and @type="radio" and @value="' + value +'"]')
            set_flag = True
            element_type = 'radio'
    except:
        pass

    try:
        if element == None and set_flag == False:
            element = driver.find_element_by_xpath('//textarea[@id="' + item + '"]')
            set_flag = True
            element_type = 'textarea'
    except:
        pass

    try:
        if element == None and set_flag == False:
            element = driver.find_element_by_xpath('//input[@id="' + item + '"]')
            set_flag = True
            element_type = 'input'
    except:
        pass

    try:
        if element == None and set_flag == False:
            element = driver.find_element_by_xpath('//textarea[@name="' + item + '"]')
            set_flag = True
            element_type ='textarea'
    except:
        pass

    try:
        if element == None and set_flag == False:
            element = driver.find_element_by_xpath('//input[@name="' + item + '"]')
            set_flag = True
            element_type = 'input'
    except:
        pass

    try:
        if element == None and set_flag == False:
            element = driver.find_element_by_xpath('//select[@id="' + item + '"]')
            set_flag = True
            element_type = 'select'
    except:
        pass

    try:
        if element == None and set_flag == False:
            element = driver.find_element_by_xpath('//select[@name="' + item + '"]')
            set_flag = True
            element_type = 'select'
    except:
        pass

    return element, element_type

def driver_set(driver, element, element_type, value):
    set_flag = False

    if element_type == 'checkbox' or element_type == 'radio':
        try: # radio boxes
            element.send_keys(Keys.SPACE)
            set_flag = True
        except:
            pass
    else: # input fields
        try: # un-hide
            js = 'arguments[0].setAttribute("type", "text");'
            driver.execute_script(js, element)
        except:
            pass

        try: # clear content
            element.clear()
            #element.send_keys(Keys.CONTROL + 'a')
        except:
            pass

        try: # populate
            element.send_keys(value)
            set_flag = True
        except:
            pass

    #try:
    #    magick_click(element)
    #    set_flag = True
    #except:
    #    pass

    return set_flag

def random_str(enable, length, style):
    if enable == False:
        return ''

    if style == 0: #32 random digit/letters
        dictionary = string.ascii_letters + string.digits
        return '' . join((random.choice(dictionary) for i in range (length)))

    if style == 1: #random space/dots
        dictionary = ' .'
        return '' . join((random.choice(dictionary) for i in range (length)))

    if style == 2: #random number of random space dots
        dictionary = '. ❤✚✓▶'
        length = random.randrange(length) + 1
        return '' . join((random.choice(dictionary) for i in range(length))) 

    if style == 3: #arrows
        dictionary = '>'
        random_str.length = random.randrange(length) + 1
        random_str.index = random.randrange(len(dictionary))
        return '' . join(dictionary[random_str.index] for i in range(random_str.length)) 

    if style == 4: #arrows
        dictionary = '<'
        return '' . join(dictionary[random_str.index] for i in range(random_str.length)) 

    return ''

def spam_fill_empty_fields(driver, text):
    print('Find empty fields')

    elements = []
    elements.extend(driver.find_elements_by_xpath("//input[not(@value)]"))
    elements.extend(driver.find_elements_by_xpath("//textarea[not(@value)]"))

    print("Elements", len(elements))

    for element in elements:
        try:
            if element.get_attribute('value') != '':
                continue

            print('Found empty')
            #driver.execute_script("arguments[0].style.display = 'block';", element)
            #driver.execute_script("arguments[0].style.enabled = 'true';", element)
            #driver.execute_script("arguments[0].style.type = 'text';", element)

            action = ActionChains(driver)
            action.move_to_element(element).click().send_keys(text).perform()

            #driver.execute_script("arguments[0].setAttribute('value', arguments[1]);", element, text)

            #element.send_keys(text)
            #ActionChains(driver).send_keys(text).perform()
            print('Sent', text)
        except Exception as ex:
            print("Error", ex)
            pass


def spam_click(driver, tags):
    print("Find click ", tags)
    for tag in tags:
        elements = []
        elements.extend(driver.find_elements_by_xpath("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '%s')]" % tag))
        for element in elements:
            print('Found', tag, element.text)
            try:
                #element.sendKeys(Keys.ENTER)
                magick_click(driver, element)
                print('Clicked', tag, element.text)
            except Exception as ex:
                print("Error", ex)
                pass

    #element.send_keys('"request callback" "phone number" "canada"')
    #element.submit()

def spam_send(driver, tags, text):
    print("Find send ", tags)
    for tag in tags:
        #elements = driver.find_elements_by_xpath("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '%s')]/following::input[@type='text']" % tag)
        elements = []
        elements.extend(driver.find_elements_by_xpath("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + tag + "')]/*/following::input"))
        elements.extend(driver.find_elements_by_xpath("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + tag + "')]/*/following::textarea"))
        elements.extend(driver.find_elements_by_xpath("//input[contains(translate(@title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + tag + "')]"))
        elements.extend(driver.find_elements_by_xpath("//textarea[contains(translate(@title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + tag + "')]"))
        for element in elements:
            print('Found', tag, element.text)
            try:
                #driver.execute_script("arguments[0].style.display = 'block';", element)
                #driver.execute_script("arguments[0].style.enabled = 'true';", element)
                #driver.execute_script("arguments[0].style.type = 'text';", element)
                #driver.execute_script("arguments[0].setAttribute('value', arguments[1]);", element, text)

                element.send_keys(text)
                #ActionChains(driver).send_keys(text).perform()
                print('Sent', tag, text, element.text)
                return
            except Exception as ex:
                print("Error", ex)
                pass

        #try:
        #    elements = driver.find_elements_by_xpath("//textarea[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '%s')]" % tag)
        #    for element in elements:
        #        print('Found', tag, element.text)
        #        element.send_keys(text)
        #        print('Sent', tag, text, element.text)
        #except Exception as ex:
        #    #print("Error", ex)
        #    pass

def spam_submit(driver, tags):
    print("Find submit ", tags)
    for tag in tags:
        #elements = driver.find_elements_by_xpath("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '%s')]/*/following::submit" % tag)
        elements = []
        elements.extend(driver.find_elements_by_xpath("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '%s')]/*/following::input[@type = 'submit']" % tag))
        #elements.extend(driver.find_elements_by_xpath("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '%s')]" % tag))
        elements.extend(driver.find_elements_by_xpath("//input[@type = 'submit']"))
        elements.extend(driver.find_elements_by_xpath("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '%s')]" % tag))
        for element in elements:
            print('Found', tag, element.text)
            try:
                print('Clicking')
                #driver.execute_script("arguments[0].click();", element)

                #element.sendKeys(Keys.ENTER)
                #element.click()
                magick_click(driver, elements)
                element.submit()
                print('Clicked', tag, element.text)
                #return
            except Exception as ex:
                print("Error", ex)
                pass

def spam_check_robot(driver):
    print('Captcha start')
    try:
        #WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,'//iframe[contains(@src, "recaptcha"]')))
        iframe = driver.find_element_by_xpath("//iframe[contains(@src, 'recaptcha')]")
        driver.switch_to.frame(iframe)
        #captcha = driver.find_element_by_xpath("//*[contains(text(), 'not a robot')]")
        captcha = driver.find_element_by_xpath("//span[@id='recaptcha-anchor']")
        action = ActionChains(driver)
        action.move_to_element_with_offset(captcha, 10, 3).perform()
        time.sleep(1)
        captcha = driver.find_element_by_xpath("//span[@id='recaptcha-anchor-label']")
        action.move_to_element_with_offset(captcha, 30, 10).perform()
        time.sleep(1)
        actions.click_and_hold().move_by_offset(2,3).perform()
        time.sleep(1)
        actions.move_by_offset(2,3).release().move_by_offset(2,3).perform()
        print('Captcha finished')
    except Exception as ex:
        print("Error", ex)

def spam_spam(driver, args, yml_file, links):
    print('Processing ' + yml_file)
    [data] = load_yml(yml_file)
    
    i = len(links)
    r = random.randint(0, i - 1)
    print('Links', i, r)

    cur_win = driver.current_window_handle # get current/main window

    for link in links[r:r + 1]:

        print('>>>>>\n', link.text, '\n<<<<<')
        #ActionChains(driver).move_to_element(link).key_down(Keys.SHIFT).click(link).key_up(Keys.SHIFT).perform()
        magick_click(driver, link)

        #driver.get('http://isostore.com/contact')
        
        time.sleep(10)
        driver.switch_to_window(cur_win) # switch back to main window
        #driver.switch_to.window(driver.window_handles[1])
        #time.sleep(1)

        #spam_click(driver, ['save', 'accept', 'continue'])
        #time.sleep(5)
        #driver.switch_to_window(cur_win) # switch back to main window

        #spam_click(driver, ['submit', 'send', 'callback', 'book', 'request', 'call'])
        #time.sleep(5)
        #driver.switch_to_window(cur_win) # switch back to main window

        driver.switch_to.default_content()

        spam_send(driver, ['first name', 'name'], data['name'])
        spam_send(driver, ['last name', 'surname'], data['surname'])
        spam_send(driver, ['phone number', 'number', 'telephone', 'phone'], data['telephone'])
        spam_send(driver, ['email'], data['email'])
        spam_send(driver, ['city'], data['city'])
        spam_send(driver, ['province'], data['province'])
        spam_send(driver, ['country'], data['country'])
        spam_send(driver, ['street'], data['street'])
        spam_send(driver, ['message'], data['message'])
        spam_send(driver, ['postal code', 'code'], data['code'])
        spam_send(driver, ['organization', 'org'], data['org'])
        spam_send(driver, ['social security', 'ssn'], data['ssn'])
        spam_fill_empty_fields(driver, 'None')
        spam_click(driver, ['consent', 'agree'])
        #spam_check_robot(driver)

        #spam_click(driver, ['agree', 'click here'])
        #driver.switch_to_window(cur_win) # switch back to main window
        spam_submit(driver, ['submit', 'send', 'callback', 'book', 'request', 'call'])
        time.sleep(10)

        #driver.close()
        #time.sleep(1)
        #driver.switch_to.window(driver.window_handles[0])

        # save,accept,yes

    print('Finished spaming')

def spam_stop(driver, args):
    #driver_save_inf(driver, '.')

    if args.pause == True:
        input('Press Any Key To Exit')

    driver.quit()
    if args.virtual == True:
        virtual_display.stop()
    print('Webdriver stopped')

def test_cmd(args):
    #xxx
    print("random_str disabled:", ">", random_str(False, 32, 0), "<")
    print("random_str 0:", ">", random_str(True, 32, 0), "<")
    print("random_str 1:", ">", random_str(True, 32, 1), "<")
    print("random_str 2:", ">", random_str(True, 32, 2), "<")
    print("random_str 3:", ">", random_str(True, 32, 3), "<")
    print("random_str 4:", ">", random_str(True, 32, 4), "<")

def spam_cmd(args):
    driver = spam_start(args)
    try:
        #links = driver.find_elements_by_xpath("//div[@class='g']//div[@class='r']//a[not(@class)]")
        #results = extend(driver.find_element_by_xpath("//div[@class='med']") # google
        results = driver.find_element_by_xpath("//div[@id='links']") # ddgo

        links = []
        #links = results.find_elements_by_xpath("//li/div/div[@class='sbtc']")
        #links.extend(results.find_elements_by_xpath("//div[@class='rc']")) # google
        #links.extend(results.find_elements_by_xpath("//a[contains(@class, 'result')]")) # ddgo
        links.extend(results.find_elements_by_xpath("//span[@class = 'result__url__domain']")) # ddgo

        spam_spam(driver, args, args.yml_filename, links)
    except Exception as ex:
        print("Spam_cmd error", ex)
    spam_stop(driver, args)

def spam_file_cmd(args):
    driver = spam_start(args)
    print('Processing file', args.yml_listname)
    try:
        os.remove('errors.txt')
    except:
        pass

    with open(args.yml_listname) as file:
        filenames = file.read().splitlines()

    for filename in filenames:
        if filename.endswith('.yml'):
            try:
                spam_spam(driver, args, filename)
                random_sleep(30, 90)
            except Exception as ex:
                print(ex)
                print('ERROR spaming', filename, file=sys.stderr)
                with open('errors.txt', "a") as myfile:
                    myfile.write(filename + '\n')
    spam_stop(driver, args)

def spam_dir_cmd(args):
    driver = spam_start(args)
    print('Processing dir', args.yml_directory)
    try:
        os.remove('errors.txt')
    except:
        pass

    dir_list = os.listdir(args.yml_directory)
    random.shuffle(dir_list)

    for filename in dir_list:
        if filename.endswith('.yml'):
            full_filename = os.path.join(args.yml_directory, filename)
            try:
                #print('Posting', full_filename)
                spam_spam(driver, args, full_filename)
                random_sleep(5, 60)
            except Exception as ex:
                print(ex)
                print('ERROR spaming', filename, file=sys.stderr)
                with open('errors.txt', "a") as myfile:
                    myfile.write(full_filename + '\n')
            continue
        else:
            continue
    spam_stop(driver, args)

def main():
    global args_faster

    print("*******************\n" \
          "* Big Bad Spammer *\n" \
          "*******************\n")

    parser = argparse.ArgumentParser(description="Post ads on Kijiji")
    parser.add_argument('-f', '--faster',  action='store_true', dest='faster', help='decrease delays')
    parser.add_argument('-v', '--virtual',  action='store_true', dest='virtual', help='enable virtual display')
    parser.add_argument('-p', '--pause',  action='store_true', dest='pause', help='pause after execution or on error so that the browser can be inspected')
    parser.add_argument('-r', '--randomize',  action='store_true', dest='randomize', help='randomize content')

    subparsers = parser.add_subparsers(help='sub-command help')

    spam_parser = subparsers.add_parser('spam', help='spam a new ad')
    spam_parser.add_argument('yml_filename', type=str, help='.yml file containing details')
    spam_parser.set_defaults(function=spam_cmd)

    spam_dir_parser = subparsers.add_parser('spam_dir', help='spam all ads in a directory')
    spam_dir_parser.add_argument('yml_directory', type=str, help='directory containing .yml files')
    spam_dir_parser.set_defaults(function=spam_dir_cmd)

    spam_file_parser = subparsers.add_parser('spam_file', help='process all ymls listed in a file')
    spam_file_parser.add_argument('yml_listname', type=str, help='filename containing .yml files')
    spam_file_parser.set_defaults(function=spam_file_cmd)

    test_parser = subparsers.add_parser('test', help='test fixture')
    test_parser.set_defaults(function=test_cmd)

    args = parser.parse_args()
    args_faster = args.faster

    try:
        args.function(args)
    #except AttributeError:
    #    parser.error("too few arguments")
    #except argparse.ArgumentError:
    #    parser.print_help()
    except Exception as ex:
        print("Error", ex)

# main
main()

