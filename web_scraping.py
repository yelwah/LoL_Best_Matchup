from global_logger import logger
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager as chromeMgr
import time
from util import (
    needsUpdate,
    getMatchupHTMLSavePath,
    getSynergyHTMLSavePath,
    getSynergyCSVPath,
    getMatchupCSVPath,
    cleanString,
)


def getLolalyticsUrl(role: str, champ: str):
    return (
        "https://lolalytics.com/lol/"
        + champ
        + "/build/?lane="
        + role 
    )


def webToHtmlFile(
    urls: list[str],
    matchup_save_paths: list[str],
    synergy_save_paths: list[str],
):
    # get url for a specific game, creating url that looks like this:
    # https://www.pro-football-reference.com/boxscores/202109190phi.htm
    if len(urls) != len(matchup_save_paths) or len(urls) != len(
        synergy_save_paths
    ):
        print("webToHtmlFile: ERROR lists different sizes")
        exit(0)
 
    options = ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ['enable-logging'])

    service = Service(chromeMgr().install())
    driver = webdriver.Chrome(service=service, options=options)
    for index in range(len(urls)):
        logger.info("Scraping " + urls[index])
        driver.get(urls[index])
        # sometimes driver.get moves too fast and pulls in the partially loaded webpage
        time.sleep(2.5)  
        actions = ActionChains(driver)

        try:
            matchups_html: str = scrapeMatchup(driver, actions)
        except AssertionError as e:
            logger.error(f"{e}: Failed to scrape data for {urls[index]}")
            continue
        matchup_soup = BeautifulSoup(matchups_html, "lxml")
        with open(matchup_save_paths[index], "w", encoding="utf-8") as file:
            file.write(str(matchup_soup.prettify()))

        synergies_html: str = scrapeSynergy(driver, actions)
        synergy_soup = BeautifulSoup(synergies_html, "lxml")

        with open(synergy_save_paths[index], "w", encoding="utf-8") as file:
            file.write(str(synergy_soup.prettify()))

        logger.info("Successfully loaded " + urls[index])

    driver.close()
    driver.quit()


def scrapeMatchup(driver: WebDriver, actions):
    # Find all Counters panels (We expect 5)
    elements: list[WebElement] = driver.find_elements(
        By.CLASS_NAME, "CountersPanel_counters__U8zc5"
    )
    assert len(elements) == 5

    # Initialize our HTML string that will store all our scraped data
    html: str = ""

    # Loop through the counter panels on the site corresponding to each role
    for element in elements:
        # Move web page to the current counter panel
        actions.move_to_element(element).perform()

        # Get the scrollbar element in the panel so we can scroll right to get all the data
        scrollbar = element.find_element(By.CLASS_NAME, "Panel_data__dtE8F")

        # Get the add the initial scroll position to the final html
        html += element.get_attribute("innerHTML")

        # Move by right by 900 pixels 5 times, appending the html each time to scrape all the matchup data
        move_offset = -900
        for rep in range(0, 7):
            actions.click_and_hold(scrollbar).move_by_offset(
                move_offset, 0
            ).release().perform()
            html += element.get_attribute("innerHTML")

    return html


def scrapeSynergy(driver: WebDriver, actions):
    # Find the Table of buttons that controls the Counters and Synergies Section, Move into View
    buttonTable: WebElement = driver.find_element(
        By.CLASS_NAME, "CounterButtons_set__99iaF"
    )
    actions.move_to_element(buttonTable).perform()

    # Click the "Common Teammates" button to switch the page to display synergies
    buttonTable.find_element(By.CSS_SELECTOR, "[data-id='4']").click()

    # Find all Synergy panels (We expect 4)
    elements: list[WebElement] = driver.find_elements(
        By.CLASS_NAME, "CountersPanel_counters__U8zc5"
    )
    assert len(elements) == 4

    # Initialize our HTML string that will store all our scraped data
    html: str = ""

    # Loop through the synergy panels on the site corresponding to each role (besides our own)
    for element in elements:
        # Move web page to the current counter panel
        actions.move_to_element(element).perform()

        # Get the scrollbar element in the panel so we can scroll right to get all the data
        scrollbar = element.find_element(By.CLASS_NAME, "Panel_data__dtE8F")

        # Get the add the initial scroll position to the final html
        html += element.get_attribute("innerHTML")

        # Move by right by 900 pixels 5 times, appending the html each time to scrape all the matchup data
        move_offset = 900
        for rep in range(0, 7):
            actions.click_and_hold(scrollbar).move_by_offset(
                move_offset, 0
            ).release().perform()
            html += element.get_attribute("innerHTML")
    return html


def fetchLolalytics(pool: dict[str, list[str]], force: bool = False):
    """
    Fetches matchup stats for all given champsions and saves the matchup data
      per champion

    Parameters:
      champions (list[str]): List of strings of champion names that will have
          their matchup stats fetched from lolalytics.com and saved

    Returns:
      (None)
    """
    print("\nScraping updated matchup data from Lolalytics\n" + ("*" * 80))
    urls = []
    matchup_csvs = []
    synergies_csvs = []
    for my_role, champs in pool.items():
        for champ in champs:
            matchups_path = getMatchupHTMLSavePath(my_role, champ)
            synergies_path = getSynergyHTMLSavePath(my_role, champ)
            if (
                needsUpdate(getMatchupCSVPath(my_role, champ), 3)
                or needsUpdate(getSynergyCSVPath(my_role, champ), 3)
                or force
            ):
                # Fix up the string to be all lower no apostophes
                cleanString(champ)
                champion_url = getLolalyticsUrl(my_role, champ)
                urls.append(champion_url)
                matchup_csvs.append(matchups_path)
                synergies_csvs.append(synergies_path)
            else:
                print(
                    "Matchup & Synergy data for "
                    + champ.capitalize()
                    + " "
                    + my_role
                    + " is already up-to-date"
                )

    if len(urls) != 0:
        webToHtmlFile(urls, matchup_csvs, synergies_csvs)

    print("\nScraping complete.\n")
