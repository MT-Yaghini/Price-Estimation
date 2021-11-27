import os
import re
import time
import numpy as np
import mysql.connector
from sklearn import tree
from sklearn.preprocessing import OneHotEncoder
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

while True:
    fun = str(input('Browse to add new CARs = "n", Calculate CAR price = "p", Quit = "q": '))
    print()
    if fun == 'n':
        sc = int(input('Number of new CARs = 40 x '))
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        browser = webdriver.Chrome(options=op)
        browser.get("https://divar.ir/s/tehran/car")
        time.sleep(1)

        link = []
        poEl = browser.find_elements_by_class_name("kt-post-card.kt-post-card--outlined")
        link = [post.get_attribute('href') for post in poEl]

        for c in range(sc):
            elem = browser.find_element_by_tag_name('body')
            no_of_pagedowns = 7
            while no_of_pagedowns:
                elem.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)
                no_of_pagedowns-=1

            poEl = browser.find_elements_by_class_name("kt-post-card.kt-post-card--outlined")
            link += [post.get_attribute('href') for post in poEl]

        link = list(set(link))
        print()
        print('Number of new CARs found to add = ',len(link),end='\n\n')

        print('Connecting to Database...',end='\n\n')
        try:
            cnx = mysql.connector.connect(user='root', password='1234', database='jadypython')
            print('Connected!',end='\n\n')
            cursor = cnx.cursor()
            cursor.execute('SELECT ID FROM car ORDER BY ID DESC LIMIT 1')
            lID = [x for x in cursor]
            if len(lID) != 0:
                ID = int(re.findall('(\d+)',str(lID[0]))[0]) + 1
            else:
                ID = 1
            IDE = 0
            dataFile = open('carError.txt','a',encoding='utf-8')
            for li in link:
                try:
                    ElN = {'وضعیت موتور':None,'وضعیت شاسی‌ها':None,'وضعیت بدنه':None,'مهلت بیمهٔ شخص ثالث':None,'گیربکس':None,'قیمت':None}

                    browser.get(li)
                    poEl = browser.find_elements_by_class_name("kt-group-row-item__value")
                    mil = int(re.sub('٫','',poEl[0].text))
                    mod = int(poEl[1].text)
                    col = poEl[2].text
                    poElN = browser.find_elements_by_class_name("kt-base-row__title.kt-unexpandable-row__title")
                    poEl = browser.find_elements_by_class_name("kt-unexpandable-row__action.kt-text-truncate")
                    for b in range(len(poEl)):
                        if poElN[b].text == 'برند و تیپ':
                            brand = poEl[b].text
                    while True:
                        if poElN[0].text == 'برند و تیپ' or poElN[0].text == 'نمایشگاه' or poElN[0].text == 'فروشنده':
                            poElN.remove(poElN[0])
                        else:
                            break
                    poEl = browser.find_elements_by_class_name("kt-unexpandable-row__value")
                    for poN in range(len(poElN)):
                        for k in ElN.keys():
                            if poElN[poN].text == k:
                                ElN[k] = poEl[poN].text

                    ElN['قیمت'] = int(re.sub('تومان','',re.sub('٬','',ElN['قیمت'])).strip())

                    if ElN['مهلت بیمهٔ شخص ثالث'] != None:
                        ElN['مهلت بیمهٔ شخص ثالث'] = int(re.sub('ماه','',ElN['مهلت بیمهٔ شخص ثالث']).strip())

                        insertCode = 'insert into car values (%i,\'%s\',%i,%i,\'%s\',\'%s\',\'%s\',\'%s\',%i,\'%s\',%i)'
                        cursor.execute(insertCode % (ID,brand,mod,mil,col,ElN['وضعیت موتور'] if ElN['وضعیت موتور'] != None else 'NULL',
                                                     ElN['وضعیت شاسی‌ها'] if ElN['وضعیت شاسی‌ها'] != None else 'NULL',
                                                     ElN['وضعیت بدنه'] if ElN['وضعیت بدنه'] != None else 'NULL',
                                                     ElN['مهلت بیمهٔ شخص ثالث'] if ElN['مهلت بیمهٔ شخص ثالث'] != None else 'NULL',
                                                     ElN['گیربکس'] if ElN['گیربکس'] != None else 'NULL',
                                                     ElN['قیمت']))
                    else:
                        insertCode = 'insert into car values (%i,\'%s\',%i,%i,\'%s\',\'%s\',\'%s\',\'%s\',NULL,\'%s\',%i)'
                        cursor.execute(insertCode % (ID,brand,mod,mil,col,ElN['وضعیت موتور'] if ElN['وضعیت موتور'] != None else 'NULL',
                                                     ElN['وضعیت شاسی‌ها'] if ElN['وضعیت شاسی‌ها'] != None else 'NULL',
                                                     ElN['وضعیت بدنه'] if ElN['وضعیت بدنه'] != None else 'NULL',
                                                     ElN['گیربکس'] if ElN['گیربکس'] != None else 'NULL',
                                                     ElN['قیمت']))
                    cnx.commit()
                    ID+=1
                except:
                    print('ERROR<1>!!!',end='\n\n')
                    IDE+=1
                    dataFile.write('\'%i\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\'\n%s\n' % (IDE,brand,mil,mod,col,
                                                                                                                        ElN['وضعیت موتور'],
                                                                                                                        ElN['وضعیت شاسی‌ها'],
                                                                                                                        ElN['وضعیت بدنه'],
                                                                                                                        ElN['مهلت بیمهٔ شخص ثالث'],
                                                                                                                        ElN['گیربکس'],
                                                                                                                        ElN['قیمت'],li))
            dataFile.close()
            cursor.close()
            cnx.close()
            os.startfile('carError.txt')
        except:
            print('ERROR<0>!!!',end='\n\n')
    elif fun == 'p':
        try:
            print('Connecting to Database...',end='\n\n')
            cnx = mysql.connector.connect(user='root', password='1234', database='jadypython')
            print('Connected!',end='\n\n')
            mod = int(input('Model: '))
            mil = int(input('Mileage: '))
            print('\nOther Specifications: BrandAndBrigade,Color,EngineCondition,ChassisCondition,BodyCondition,InsuranceDeadline,GearboxType')
            newData = input('Other Specifications: ').split(',')
            print('\nCalculating...\n')
            ans = []
            for c in range(10):
                x = []
                y = []
        
                cursor = cnx.cursor()
                cursor.execute('select * from car')
                x = [list(car) for car in cursor]
                for c in range(len(x)):
                    y.append(x[c][10])
                    x[c].pop(10)
                    x[c].pop(0)

                xc = [[c[0],c[3],c[4],c[5],c[6],str(c[7]) if c[7] != None else 'NULL',c[8]] for c in x]
                enc = OneHotEncoder(handle_unknown='ignore')
                enc.fit(xc)
                xc = enc.transform(xc).toarray()
                xc = list(map(lambda a: list(a),xc))
                for c in range(len(xc)):
                    xc[c].append(x[c][1])
                    xc[c].append(x[c][2])

                x = [np.array(xc[c]) for c in range(len(xc))]
                clf = tree.DecisionTreeClassifier()
                clf = clf.fit(x,y)
                newDataV = []
                newDataV = list(enc.transform([newData]).toarray()[0])
                newDataV.append(mod)
                newDataV.append(mil)
                newDataV = np.array(newDataV)
                answer = clf.predict([newDataV])
                ans.append(answer[0])

            ans.sort()
            print('Your CAR price = ',ans,end='\n\n')
            cursor.close()
            cnx.close()
        except:
            pass
    elif fun == 'q':
        print('Closed!')
        break
    else:
        print(':|',end='\n\n')
