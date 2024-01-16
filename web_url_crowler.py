import os
try:
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse, urljoin
except:
    os.system("pip install requests beautifulsoup4")

import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


pt = time.time()
def get_recursive_urls(base_url, max_depth=3, current_depth=1, visited_urls=None):
    if visited_urls is None:
        visited_urls = set()

    if current_depth > max_depth or base_url in visited_urls:
        return []

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        visited_urls.add(base_url)
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {base_url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    recursive_urls = set()

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        absolute_url = urljoin(base_url, href)
        parsed_url = urlparse(absolute_url)

        # Check if the URL is from the same domain
        if parsed_url.netloc == urlparse(base_url).netloc:
            recursive_urls.add(absolute_url)
            print(f"{round(time.time() - pt, 4)} \t: Runing...: {absolute_url}")
            recursive_urls.update(get_recursive_urls(absolute_url, max_depth, current_depth + 1, visited_urls))

    return list(recursive_urls)

def save_urls_to_file(urls, file_path='recursive_urls_2_gfg.txt'):
    with open(f"recursive_urls_{file_path}.txt", 'w') as file:
        for url in urls:
            file.write(url + '\n')

# Example usage
website_url = "https://www.geeksforgeeks.org/"
website_url = input("Enter Website URL: ")
recursive_urls = get_recursive_urls(website_url)

save_urls_to_file(recursive_urls, file_path=website_url.split("/")[1])
print(f"Recursive URLs saved to 'recursive_urls.txt'")

# print(f"Recursive URLs on {website_url}:")
# for url in recursive_urls:
#     print(url)

