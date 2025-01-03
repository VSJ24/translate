from googletrans import Translator
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import os
from collections import Counter
import re

# translate es to en
def translate_text(text):
    translator = Translator()
    try:
        translation = translator.translate(text, src='es', dest='en')
        return translation.text
    except Exception as error:
        print(f'Translation error: {error}')
        return text


# # RapidAPI details
# RAPIDAPI_HOST = "rapid-translate-multi-traduction.p.rapidapi.com"
# RAPIDAPI_KEY = "67f8554ffcmshdf380888f70276fp13e88ajsnd9c21e258df9"  # Replace with your actual RapidAPI key

# # function to translate using rapid API
# def translate_text(text, target_language="en"):
#     url = f"https://{RAPIDAPI_HOST}/t"
#     payload = {
#         "from": "es",  # Source language (Spanish)
#         "to": target_language,
#         "text": text,
#     }
#     headers = {
#         "content-type": "application/json",
#         "X-RapidAPI-Host": RAPIDAPI_HOST,
#         "X-RapidAPI-Key": RAPIDAPI_KEY,
#     }
#     response = requests.post(url, json=payload, headers=headers)
    
#     if response.status_code == 200:
#         try:
#             # Assuming response is a list of translations
#             translated_data = response.json()
#             if isinstance(translated_data, list) and len(translated_data) > 0:
#                 return translated_data[0]  # Get the first item
#             else:
#                 return "Translation failed: Unexpected response structure"
#         except Exception as e:
#             return f"Translation failed: {e}"
#     else:
#         return f"Error: {response.status_code} - {response.text}"


# Setup the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Function to scrape articles
def scrape_articles():
    driver.get("https://elpais.com/")   
    
    lang = driver.find_element(By.TAG_NAME, 'html').get_attribute('lang')

    # Check if the language is Spanish
    if lang == 'es':
        print("The website is in Spanish.")
    else:
        print(f"The website is in {lang}.")
    
    # Ensure the website is in Spanish (this might require adjusting the language settings if necessary)
    time.sleep(3)
    
    try:
        # Handle cookie popup if it appears
        cookie_accept = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="didomi-notice-agree-button"]'))
        )
        cookie_accept.click()
    except Exception as e:
        print("Cookie popup not found or couldn't be clicked:", e)

    try:
        # Navigate to the Opinion section
        opinion_section = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="csw"]/div[1]/nav/div/a[2]'))
        )
        opinion_section.click()
    except Exception as e:
        print("Opinion section not found or couldn't be clicked:", e)

    time.sleep(3)  # Wait for the Opinion section to load

    # Fetch the first 5 articles
    articles = driver.find_elements(By.XPATH, '//article')[:5]
    
    article_data = []
    
    for article in articles:
        try:
            title = article.find_element(By.TAG_NAME, 'h2').text
            content = article.find_element(By.TAG_NAME, 'p').text
            img_url = None
            try:
                img_element = article.find_element(By.CSS_SELECTOR, 'img')
                img_url = img_element.get_attribute('src')
            except Exception:
                print("Image not found for this article")
            
            # Save article data
            article_data.append({'title': title, 'content': content, "img_url": img_url})
            
            # Download image
            if img_url:
                img_data = requests.get(img_url).content
                img_name = f"{title[:30].replace(' ', '_')}.jpg"
                with open(os.path.join('images', img_name), 'wb') as f:
                    f.write(img_data)
        except Exception as e:
            print(f"Error extracting data from article: {e}")
    
    return article_data

# Ensure the 'images' folder exists
if not os.path.exists('images'):
    os.makedirs('images')

# Scrape articles
articles = scrape_articles()


# Print titles and content of scraped articles
for article in articles:
    print(f"Title (Spanish): {article['title']}")
    print(f"Content: {article['content']}")
    print(f"Image saved at: {article.get('img_url')}")
    print("\n---\n")
article_titles = []
    
for article in articles:
    try:
        title = article['title']
        print(title)
        article_titles.append(title)
    except Exception as e:
        print(f"Error extracting title: {e}")

# Translate titles
translated_titles = []
for title in article_titles:
    translated_title = translate_text(title)
    translated_titles.append(translated_title)
    
# Print the results
for original, translated in zip(article_titles, translated_titles):
    print(f"Original Title (Spanish): {original}")
    print(f"Translated Title (English): {translated}")
    print("\n---\n")

# Analyze repeated words in translated titles
def analyze_repeated_words(translated_titles):
    word_count = Counter()
    
    for title in translated_titles:
        words = re.findall(r'\w+', title.lower())  
        word_count.update(words)
    
    repeated_words = {word: count for word, count in word_count.items() if count > 2}
    
    return repeated_words

# Print repeated words with their counts
repeated_words = analyze_repeated_words(translated_titles)
for word, count in repeated_words.items():
    print(f"Word: '{word}' - Occurrences: {count}")


# Quit the driver
driver.quit()
