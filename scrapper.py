# @dev: @ghooost0x2a
from selenium import webdriver
from selenium.webdriver.common.by import By
from pprint import pprint
import clipboard as cb
import time, sys, json, shutil, requests, os, csv

# UPDATE THESE VARIABLES FOR YOUR NEEDS/COLLECTION
# URL of the main collection page, make sure they are sorted by CREATED_DATE (ascending) to get them in order
COLLECTION_URL = "https://opensea.io/collection/newman-nfts?search[sortAscending]=true&search[sortBy]=CREATED_DATE"
NFT_URL_LIST_FILE = "./urls.txt"  # text file with line by line ordered list of OS urls for each NFT in the collection
SNAPSHOT_FILE = "./snapshot.txt"  # json dump with dict for each NFT in the collection
CSV_OWNER_FILE = "./owners.csv"
CSV_NFT_URLS = "./nfts_urls.csv"
IMGS_DIR = "./imgs/"
CURRENT_COLLECTION_SIZE = 200  # needed for the loop, please be accurate
DEBUGG = False

# XPATHS (might require update)
OWNER_XPATH = (
    "//*[@id='main']/div/div/div/div[1]/div/div[1]/div[2]/section[2]/div/div/a"
)
NFT_NAME_XPATH = "//*[@id='main']/div/div/div/div[1]/div/div[1]/div[2]/section[1]/h1"
NFT_IMG_XPATH = (
    "//*[@id='main']/div/div/div/div[1]/div/div[1]/div[1]/article/div/div/div/div/img"
)
COLLECTION_PAGE_GRID_BTN_XPATH = "/html/body/div[1]/div/main/div/div/div[3]/div/div/div/div[3]/div[1]/div[2]/div[4]/div/button[2]"

COPY_ADDRESS_BUTTON_XPATH = (
    "//*[@id='main']/div/div/div[1]/div[3]/div[3]/div/button/div"
)


def main():
    global CURRENT_COLLECTION_SIZE, DEBUGG
    if "debug" in sys.argv or DEBUGG:
        CURRENT_COLLECTION_SIZE = 50
    if "coll" in sys.argv:
        get_nft_urls_from_collection()
    elif "nft" in sys.argv:
        get_nfts_info()
    elif "csv" in sys.argv:
        compile_csv()
    elif "imgs" in sys.argv:
        print(os.path.isdir(IMGS_DIR))
        if not os.path.isdir(IMGS_DIR):
            os.mkdir(IMGS_DIR)
        download_images()


# sets view to grid, then scrolls through the collection (hopefully in the right order)
# copies the url of each NFT and stores it in the list (if not in it already)
# produces a file NFT_URL_LIST_FILE with an ordered list of OS urls to each NFT in the collection
def get_nft_urls_from_collection():
    NFT_URL_LIST = []
    browser = webdriver.Chrome()
    browser.get(COLLECTION_URL)
    browser.maximize_window()
    browser.execute_script("window.scrollBy(0,150)", "")
    grid_btn = browser.find_element(
        By.XPATH,
        COLLECTION_PAGE_GRID_BTN_XPATH,
    )
    grid_btn.click()
    time.sleep(6)  # to make sure page is fully loaded
    for i in range(0, CURRENT_COLLECTION_SIZE * 2):
        elems = browser.find_elements_by_class_name("Asset--anchor")
        if len(NFT_URL_LIST) >= CURRENT_COLLECTION_SIZE:
            break
        print(elems)
        for e in elems:
            if len(NFT_URL_LIST) >= CURRENT_COLLECTION_SIZE:
                break
            else:
                try:
                    href = e.get_attribute("href")
                    print(e)
                    print(href)
                    if href not in NFT_URL_LIST:
                        NFT_URL_LIST.append(href)
                    # print(NFT_URL_LIST)
                except:
                    print("Exception")
        print(len(NFT_URL_LIST))
        browser.execute_script("window.scrollBy(0,300)", "")
        time.sleep(3)  # important to let the new NFTs load
    NFT_URL_LIST = sort_url_list(NFT_URL_LIST)
    print(len(NFT_URL_LIST))
    print(NFT_URL_LIST)
    f = open(NFT_URL_LIST_FILE, "w")
    for e in NFT_URL_LIST:
        f.write(str(e) + "\n")
    f.close()

    time.sleep(4)


def sort_url_list(NFT_URL_LIST):
    try:
        NFT_URL_LIST.sort()
    except:
        print("Exc2")
    return NFT_URL_LIST


# loads the file NFT_URL_LIST_FILE and loops through each OS link to scrape NFT and owner data
# produces SNAPSHOT_FILE with dict for each NFT, in order
def get_nfts_info():
    NFTS = {}
    with open(NFT_URL_LIST_FILE) as f:
        NFT_URL_LIST = f.read().splitlines()
    print(len(NFT_URL_LIST))
    browser = webdriver.Chrome()
    browser.maximize_window()
    time.sleep(1)

    for k, u in enumerate(NFT_URL_LIST):
        if k >= CURRENT_COLLECTION_SIZE:
            break
        nft = {}
        print("\n\nFetching NEW NFT: " + str(k))
        print(u)

        if u == "SKIP_THIS_TOKEN":
            nft = {"BURNED": True}
        else:  # get the NFT page
            browser.get(u)
            nft["url"] = u

            # resetting the clipboard
            cb.copy("bebe")
            time.sleep(1)

            # get the URL to the owner's page
            owner = browser.find_element(
                By.XPATH,
                OWNER_XPATH,
            ).get_attribute("href")
            nft["owner_page"] = owner

            # get the NFT title/name
            name = browser.find_element(
                By.XPATH,
                NFT_NAME_XPATH,
            ).get_attribute("title")
            nft["token_name"] = name

            # get the nft img OS link
            img = browser.find_element(
                By.XPATH,
                NFT_IMG_XPATH,
            ).get_attribute("src")
            nft["img"] = img

            # go to this NFT owner's profile page to get address
            browser.get(owner)

            # click on the address button to copy it to clipboard
            addy = browser.find_element(
                By.XPATH,
                COPY_ADDRESS_BUTTON_XPATH,
            ).click()
            # get the address from the clipboard
            addy = cb.paste()
            if addy == "bebe":  # make sure we actually got an address
                raise Exception
            nft["addy"] = addy

            print(addy)
            print(name)
            print(owner)
        # add the NFT ownership to the dictionary
        NFTS[k + 1] = nft

        # write it to file, as json (on each iteration, in case script crashes)
        ff = open(SNAPSHOT_FILE, "w")
        ff.write(
            json.dumps(
                NFTS,
                indent=4,
            )
        )
        ff.close()
        # pprint(NFTS)


# download images to IMGS_DIR
def download_images():
    nft_json_file = open(SNAPSHOT_FILE, "r")
    NFTS_DICT = json.loads(nft_json_file.read())
    pprint(len(NFTS_DICT))

    if len(NFTS_DICT) != CURRENT_COLLECTION_SIZE:
        print(
            "CURRENT_COLLECTION_SIZE doesn't match number of elements in SNAPSHOT_FILE"
        )
        return
    # pprint(NFTS_DICT)
    for ind, nft in NFTS_DICT.items():
        url = nft["img"]
        response = requests.get(url, stream=True)
        with open(f"{IMGS_DIR}/{ind}.png", "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response


def compile_csv():
    nft_json_file = open(SNAPSHOT_FILE, "r")
    NFTS_DICT = json.loads(nft_json_file.read())
    owner_dict = {}
    if len(NFTS_DICT) != CURRENT_COLLECTION_SIZE:
        print(
            "CURRENT_COLLECTION_SIZE doesn't match number of elements in SNAPSHOT_FILE"
        )
        return
    # pprint(NFTS_DICT)
    csv_file_tokens = open(CSV_NFT_URLS, "w")
    csv_writer_tokens = csv.writer(csv_file_tokens)
    csv_writer_tokens.writerow(["address", "tokens"])
    for ind, nft in NFTS_DICT.items():
        ad = nft["addy"]
        if ad not in owner_dict:
            owner_dict[ad] = []
        owner_dict[ad].append(ind)
        csv_writer_tokens.writerow([ind, nft["url"]])

    pprint(owner_dict)

    csv_file = open(CSV_OWNER_FILE, "w")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["address", "tokens"])
    for inn, nft in owner_dict.items():
        csv_writer.writerow([inn, nft])

    csv_file.close()


if __name__ == "__main__":
    main()
