# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

# Module 10.5.3 establishing connection
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      "hemisphere": mars_hemisphere(browser)
    }
    # Stop webdriver and return data
    browser.quit()
    return data


# First scrape
# Set up Splinter
# executable_path = {'executable_path': ChromeDriverManager().install()}
# browser = Browser('chrome', **executable_path, headless=False)

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first <a> tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# ## JPL Space Images Featured Image

# Second scrape
def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

# ## Mars Facts

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemisphere(browser):
    # create empty list to format dat within
    hemisphere_image_urls = []
    base_url = 'https://marshemispheres.com/'
    
    # visit the webpage 
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    
    # parse site 
    html = browser.html
    html_soup = soup(html, 'html.parser')
    # creating variable with tag and attribute which contain all full-resolution images and info needed
    mars_image_info = html_soup.select('div.description')

    try: 
        # loop through scraped data, scrape additonal data and format 
        for i in list(range(len(mars_image_info))):
        
            # extracted data and retrieved text header from 'h3'
            header = mars_image_info[i].find('h3').get_text()
    
            # retrieve embedded parital url and convert to full webpage link
            partial_url = mars_image_info[i].find('a').get('href')
    
            # adding the base url with the partial url to make a full link
            full_link = f'{base_url}{partial_url}'
    
            # nested browser visit/clicks on full_link
            browser.visit(full_link)
    
            # parsing html
            html = browser.html
            html_soup = soup(html, 'html.parser')
    
            # retreive full-resolution images within these listed tags
            image_url = html_soup.select_one('ul li a').get('href')
    
            # adding base url to image url to add in dictionary
            full_image_url = f'{base_url}{image_url}'

            # format all data into a dictionary 
            hemisphere_image_urls.append({'img_url':full_image_url,'title':header})

    except AttributeError:
        return None
        
    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())



