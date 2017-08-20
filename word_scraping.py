from selenium import webdriver

PATH = "C:\Users\mk\Desktop\QA-Interface\chromedriver\chromedriver.exe"
browser = webdriver.Chrome(PATH)
browser.get("https://www.thegamegal.com/word-generator/")

dropdown = browser.find_element_by_id("category")
dropdown.click()

medium = browser.find_element_by_xpath("//option[@value='7']")
medium.click()

file = open("medium.txt", 'w')

for i in range(200):
    new_word_btn = browser.find_element_by_id("newword-button")
    new_word_btn.click()

    word = browser.find_element_by_id("gennedword").get_attribute("innerHTML")
    file.write(word + "\n")
