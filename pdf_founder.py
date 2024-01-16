import os
try:
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse, urljoin
except ImportError:
    os.system("pip install requests beautifulsoup4")

import time

os.makedirs("crawled_url", exist_ok=True)
pt = time.time()

def get_recursive_pdf_urls(base_url, max_depth=3, current_depth=1, visited_urls=None):
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

    recursive_pdf_urls = set()

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        absolute_url = urljoin(base_url, href)
        parsed_url = urlparse(absolute_url)

        # Check if the URL is from the same domain
        if parsed_url.netloc == urlparse(base_url).netloc:
            if absolute_url.lower().endswith('.pdf'):
                recursive_pdf_urls.add(absolute_url)
                print(f"{round(time.time() - pt, 4)} \t: Found PDF :: {absolute_url}")
            else:
                recursive_pdf_urls.update(get_recursive_pdf_urls(absolute_url, max_depth, current_depth + 1, visited_urls))

    return list(recursive_pdf_urls)

def save_urls_to_file(urls, file_path='pdf_urls.txt'):
    with open(f"crawled_url/{file_path}", 'w') as file:
        for url in urls:
            file.write(url + '\n')

# Example usage
website_url = input("Enter Website URL: ")
recursive_pdf_urls = get_recursive_pdf_urls(website_url)

save_urls_to_file(recursive_pdf_urls, file_path=f"{website_url.split('/')[2]}_pdf_urls.txt")
print(f"Number of PDF URLs found: {len(recursive_pdf_urls)}")
print(f"PDF URLs saved to '{website_url.split('/')[2]}_pdf_urls.txt'")
