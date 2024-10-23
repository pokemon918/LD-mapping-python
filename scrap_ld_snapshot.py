import os
import plistlib
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Constants for file and folder paths, and wait times
WEBLOCS_FOLDER = "link/autism"  # Path to the folder containing .webloc files
# WEBLOCS_FOLDER = "link/dyslexia" # Alternative folder path
DOWNLOAD_WAIT_TIME = 5  # Seconds to wait for downloads - increased for reliability

# Function to extract URL from a .webloc file
def extract_link_from_webloc(webloc_file):
    """Extracts the URL from a .webloc file.

    Args:
        webloc_file (str): The path to the .webloc file.

    Returns:
        str or None: The URL string if successful, None otherwise.
    """
    try:
        with open(webloc_file, 'rb') as f:
            plist = plistlib.load(f)
        return plist['URL']
    except (plistlib.InvalidPlistException, KeyError, FileNotFoundError) as e:  # More specific exception handling
        print(f"Error processing {webloc_file}: {e}")
        return None

# Function to extract URLs from all .webloc files in a folder
def extract_links_from_webloc_folder(folder_path):
    """Extracts URLs from all .webloc files in a given folder.

    Args:
        folder_path (str): The path to the folder.

    Returns:
        list: A list of extracted URLs.
    """
    links = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".webloc"):
            file_path = os.path.join(folder_path, filename)
            link = extract_link_from_webloc(file_path)
            if link:
                links.append(link)
    return links

# Function to download LD data from a given URL
def get_ld_snapshot(driver, link):
    """Navigates to a page, clicks the LD button, takes a screenshot, and potentially downloads data.

    Args:
        driver: The Selenium WebDriver instance.
        link (str): The URL to navigate to.
    """
    try:
        driver.get(link)
        wait = WebDriverWait(driver, 1000) # More reasonable wait time - adjust as needed
        
        # Locate and click the LD button
        ld_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Linkage disequilibrium (LD)']")))
        ld_button.click()

        # Wait for the LD container to be visible
        ld_container = wait.until(EC.visibility_of_element_located((By.ID, 'container_svg')))
        driver.execute_script("arguments[0].scrollIntoView();", ld_container)  # Scroll into view

        # Extract variant ID for screenshot filename
        variant_id = link.split('/')[-1]  # Handle both with and without trailing '/'
        driver.save_screenshot(f"{variant_id}.png")

        #  Add any download logic here if necessary. The original code didn't have specific download handling.


    except Exception as e:
        print(f"Error downloading LD data from {link}: {e}")


# Main script execution block
if __name__ == "__main__":
    current_directory = os.getcwd() # Simpler way to get the current directory

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--window-size=1200,1200") # Set window size for consistency even in headless mode

    prefs = {
        'download.default_directory': current_directory,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True   # Keep safebrowsing enabled unless there's a compelling reason to disable it
    }
    chrome_options.add_experimental_option('prefs', prefs)

    with webdriver.Chrome(options=chrome_options) as driver:
        links = extract_links_from_webloc_folder(WEBLOCS_FOLDER)
        for link in links:
            get_ld_snapshot(driver, link)

        time.sleep(DOWNLOAD_WAIT_TIME) # Wait for potential downloads to complete – consider a more robust solution for large downloads