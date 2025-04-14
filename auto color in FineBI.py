#!/usr/bin/env python
# coding: utf-8

# In[69]:


# импорт модулей
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import ctypes
import openpyxl
import pandas as pd


# In[70]:


# RGB to HEX
def rgb_to_hex(r, g, b):
  return ('{:02X}' * 3).format(r, g, b)

# перевод цвета, полученного с помощью атрибута background_color, в HEX
def css_color_to_hex(css_color):
    list_rgb = ['', '', '']
    i = 0
    
    for char in css_color:
        if char.isdigit():
            list_rgb[i] = list_rgb[i] + char
        elif char == ',':
            i += 1
        elif i == 3:
            break
    
    list_rgb_int = []
    for item in list_rgb:
        list_rgb_int.append(int(item))

    result = rgb_to_hex(list_rgb_int[0], list_rgb_int[1], list_rgb_int[2]).lower()

    return result


# In[71]:


indicators_of_page[count_page]


# In[72]:


# инициализация запуска ChromeDrive
driver = webdriver.Chrome()

try:
    # логин и пароль к аккаунту в FineBI
    # хранятся в файле settings.txt в формате логин:пароль
    file_with_credits = open('settings.txt', 'r')
    credits = file_with_credits.readline()
    file_with_credits.close()
    credits = credits.split(':')
    login = credits[0]
    password = credits[1]
    
    # список страниц на визы, в которых нужно поменять цвета
    # лежат в xlsx-файле list of components.xlsx списком в первом столбце. Первая строка - заголовок, который не трогается
    import_urls = pd.read_excel('list of components.xlsx')
    urls_of_page = [import_urls.loc[count].values[0] for count in range(0, len(import_urls))]
    indicators_of_page = [str(import_urls.loc[count].values[1]) for count in range(0, len(import_urls))]
    
    
    # заданные заказчиком цвета категорий
    # лежат в xlsx-файле list of colors.xlsx двумя столбцами, где первый - список категорий, второй - список цветов. Первая строка - заголовок, который не трогается
    dict_of_category_and_colors = {}
    import_colors = pd.read_excel('list of colors.xlsx')
    for count in range(0, len(import_colors)):
        dict_of_category_and_colors.update({str(import_colors['Категория'].loc[count]) : str(import_colors['Цвет'].loc[count])})




    
    for count_page in range(0, len(urls_of_page)):
        # переход на нужную страницу
        driver.get(urls_of_page[count_page])
        # ожидание загрузки страницы
        driver.implicitly_wait(5)
    
        
        # если это окно авторизации, то авторизуйся
        if driver.current_url.find('login') != -1:
            # авторизация
            input_login = driver.find_elements(By.CLASS_NAME, 'bi-input display-block overflow-dot'.replace(' ', '.'))
            input_login[0].clear()
            input_login[0].send_keys(login)
            
            input_login[1].clear()
            input_login[1].send_keys(password)
            
            button_login = driver.find_element(By.CLASS_NAME, 'bi-label bi-f-c bi-f-h v-middle h-center f-s-n c-e f-c l-c'.replace(' ', '.'))
            button_login.click()
    
        
        # ожидание загрузки страницы
        driver.implicitly_wait(5)
        time.sleep(2)

        # если в исходных данных указан конкретный индикатор, в котором нужно изменить цвет, то
        if indicators_of_page[count_page] != 'nan':
            # найди все возможные варианты выборов индикаторов в окне Graphic Property
            need_indicator_main = driver.find_elements(By.CLASS_NAME, 'bi-chart-shape-conf-expander bi-expander bi-v'.replace(' ', '.'))
            for count_main in range(0, len(need_indicator_main)):
                # ищем тот индикатор, название которого совпадает с заданным
                need_indicator = need_indicator_main[count_main].find_element(By.CLASS_NAME, 'bi-text f-auto c-e f-c l-c'.replace(' ', '.'))
                if need_indicator.text == indicators_of_page[count_page]:
                    # когда нашли, кликаем на индикатор, раскрываем его опции
                    need_indicator.click()
                    # и ищем там кнопку Color
                    button_color = need_indicator_main[count_main].find_element(By.CLASS_NAME, 'bi-f-v-c cursor-pointer attr-setting-font icon-size-12 bi-f-h v-middle h-left f-s-n c-e f-c l-c'.replace(' ', '.'))
                    needed_driver = need_indicator_main[count_main]
                    break
        else:
                # если конкретное название индикатора не задано, сразу ищем первую кнопку Color в окне Graphic Property
            button_color = driver.find_element(By.CLASS_NAME, 'bi-f-v-c cursor-pointer attr-setting-font icon-size-12 bi-f-h v-middle h-left f-s-n c-e f-c l-c'.replace(' ', '.'))
            needed_driver = driver
                
        # кликаем на нее
        button_color.click()
        # поиск родительского объекта, в котором находится список категорий и цветов
        parent_for_names_color = needed_driver.find_element(By.CLASS_NAME, 'bi-list-view bi-border bi-v'.replace(' ', '.'))
    
    
        # крутим скролл в окне с категориями и цветами вниз, пока не перестанут появляться новые элементы
        count_elements_in_list = 0
        repeater = 1
        while True:
            
            # опускаем скролл в этом окне в самый низ
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", parent_for_names_color)
        
            # получение объектов, в которых находятся имена категорий
            names_color = parent_for_names_color.find_elements(By.CLASS_NAME, 'bi-text f-auto c-e f-c l-c'.replace(' ', '.'))
        
            # если число элементов после скролла равно числу элементов до скролла, то
            # в этом случае крутани скролл еще 20 раз на всякий случай, и только потом прерывай цикл
            if len(names_color) == count_elements_in_list:
                if repeater%20 == 0:
                    break
                else:
                    repeater += 1
            else:
                count_elements_in_list = len(names_color)
    
    
        # получение списка объектов-имен, в которых находятся имена категорий
        names_color = parent_for_names_color.find_elements(By.CLASS_NAME, 'bi-text f-auto c-e f-c l-c'.replace(' ', '.'))
        
        # создадим список с названиями из names_color
        list_names_color = []
        for i in range(0, len(names_color)):
            list_names_color.append(names_color[i].text)
    
    
        
        # непосредственное изменение цветов, идем по каждой категории отдельно
        for iterator in range(0, len(list_names_color)):
            
        # проверяем, что категория в списке с порядковым номером iterator есть в нашем словаре
        # иначе не трогаем эту категорию
            if list_names_color[iterator] in dict_of_category_and_colors.keys():
                # после каждого изменения цвета скролл в окне с выбором цвета сбрасывается
                # поэтому перед тем, как попытаться обратиться к следующему элементу, проверяем его доступность
                # если не видим его, то крутим скроллом вниз, пока не найдем
                while True:
                    try:
                        current_color = parent_for_names_color.find_elements(By.CLASS_NAME, 'color-chooser-trigger-content'.replace(' ', '.'))[iterator].value_of_css_property('background-color')
                    except:
                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", parent_for_names_color)
                    else:
                        break
                # проверяем, что текущий цвет категории не совпадает с тем, который нам нужен,
                # иначе не трогаем эту категорию
                if css_color_to_hex(current_color) != dict_of_category_and_colors.get(list_names_color[iterator]):
                    # получение списка объектов-кнопок, по нажатии на которые всплывает окно с выбором цвета
                    buttons_color = parent_for_names_color.find_elements(By.CLASS_NAME, 'bi-trigger cursor-pointer bi-color-chooser-trigger bi-focus-shadow bi-border bi-border-radius bi-abs'.replace(' ', '.'))
                   
                    # кликаем на кнопку выбора цвета категории с порядковым номером iterator
                    buttons_color[iterator].click()
                    
                    # поиск родительского объекта, в котором находятся поля для ввода цветов
                    parent_for_input_fields = needed_driver.find_element(By.CLASS_NAME, 'bi-color-chooser-popup bi-v bi-abs'.replace(' ', '.'))
                    # получение объектов ввода текста в родительском объекте
                    input_field = parent_for_input_fields.find_elements(By.CLASS_NAME, 'bi-input display-block overflow-dot'.replace(' ', '.'))
                
                    # вводим в это поле значение цвета, который соответствует указанной категории в нашем словаре цветов
                    input_field[0].clear()
                    input_field[0].send_keys(dict_of_category_and_colors.get(list_names_color[iterator]).lower())
                    # немного ждем, пока введенный нам цвет не появится на палитре
                    time.sleep(0.3)
                    
                    # после выбора цвета закрываем окно путем клика на появившийся введенный нами цвет (первый по счету цвет в ранее использованных)
                    # выход из этого окна иным способом может привести к незакрытию этого фрейма в коде страницы и нарушению работы алгоритма
                    button_close_color = parent_for_input_fields.find_element(By.CLASS_NAME, 'color-picker-button-mask'.replace(' ', '.'))
                    button_close_color.click()
        print('Everything is done')
except Exception as e:
    ctypes.windll.user32.MessageBoxW(0, "Что-то пошло не так. Проверьте ошибки в интерпретаторе", "Автоматизация раскраски в FineBI", 1) 
    print(f"Произошла ошибка: {e}")
    traceback.print_exc()
else:
    ctypes.windll.user32.MessageBoxW(0, "Раскраска выполнена успешно", "Автоматизация раскраски в FineBI", 1)


# In[ ]:




