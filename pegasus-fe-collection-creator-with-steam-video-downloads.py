#!/usr/bin/env python3

import os
import tkinter as tk
from tkinter import filedialog, messagebox, Menu, Label, Entry, Button, Text
import requests
from bs4 import BeautifulSoup
import re
import json
import string
from datetime import datetime
from urllib.parse import urlparse, urljoin

lutris_path = "/usr/bin/prime-run /usr/bin/lutris"

class PegasusApp:
    ALLOWED_IMAGE_FORMATS = (".jpg", ".png", ".bmp", ".webp")
    ALLOWED_VIDEO_FORMATS = ("mp4")
    IMAGE_CATEGORIES_COMMON = {
        "clearlogo": "logo",
        "fanart": "background",
        "boxart/front": "boxFront",
        "boxart/back": "boxBack",
        "screenshot": "screenshot",
        "video": "video"
    }

    IMAGE_CATEGORIES_STEAM = {
        "boxart/front": "img.game_header_image_full",
        "fanart": 'a[data-fancybox="fanarts"]',
        "clearlogo": 'a[data-fancybox="clearlogos"]',
        # "boxart/back": 'a.fancybox-thumb[data-fancybox="cover"][data-caption="Back Cover"]',
        "screenshot": "a.highlight_screenshot_link",
    }

    VIDEO_CATEGORIES_STEAM = {
        "video": "div.highlight_player_item.highlight_movie",
    }

    IMAGE_CATEGORIES_THEGAMESDB = {
        "boxart/front": 'a.fancybox-thumb[data-fancybox="cover"][data-caption="Front Cover"]',
        "fanart": 'a[data-fancybox="fanarts"]',
        "clearlogo": 'a[data-fancybox="clearlogos"]',
        "boxart/back": 'a.fancybox-thumb[data-fancybox="cover"][data-caption="Back Cover"]',
        "screenshot": 'a[data-fancybox="screenshots"]'
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Pegasus FE Collection Creator")
        self.root.geometry("800x800")
        self.parent_directory = None
        self.config_file = "config.json"

        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.script_dir, "config.json")

        self.default_games_directory = self.load_default_directory("default_games_directory")
        self.default_collections_directory = self.load_default_directory("default_collections_directory")

        # self.load_default_collections_directory()
        self.create_widgets()
        self.set_icon()
        self.soup = None  # Initialize soup to None
        self.updated_details = None # Initialize updated_details to None.
        self.platform = None # Initialize platform to None.

    def set_icon(self):
        self.root.iconphoto(False, tk.PhotoImage(file=os.path.join(self.script_dir, "pegasus.png")))

    def load_default_directory(self, key):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get(key, "")
        return ""

    def save_default_directory(self, key, directory):
        config = {}
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        config[key] = directory
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    def save_config(self):
        config = {
            "default_games_directory": self.default_games_directory,
            "default_collections_directory": self.default_collections_directory
        }
        print(f"Saving config: {config}")  # Debugging message
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Config saved successfully to {self.config_file}")  # Debugging message

    def set_default_games_directory(self):
        default_games_directory = filedialog.askdirectory(title="Select Default Games Directory")
        if default_games_directory:
            self.default_games_directory = default_games_directory
            self.save_default_directory("default_games_directory", default_games_directory)
            messagebox.showinfo("Success", "Default games directory set successfully.")

    def set_default_collections_directory(self):
        default_collections_directory = filedialog.askdirectory(title="Select Default Collections Directory")
        if default_collections_directory:
            self.default_collections_directory = default_collections_directory
            self.save_default_directory("default_collections_directory", default_collections_directory)
            messagebox.showinfo("Success", "Default collections directory set successfully.")

    def create_widgets(self):
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        menubar = Menu(self.root)

        # File Menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New Collection", command=self.prompt_collection_choice, underline=0)
        filemenu.add_command(label="Open Existing Collection", command=self.open_existing_collection, underline=0)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit, underline=1)
        menubar.add_cascade(label="File", menu=filemenu, underline=0)

        # Configuration Menu
        configmenu = Menu(menubar, tearoff=0)
        configmenu.add_command(label="Set Default Games Directory", command=self.set_default_games_directory, underline=12)
        configmenu.add_command(label="Set Default Collections Directory", command=self.set_default_collections_directory, underline=12)
        menubar.add_cascade(label="Configuration", menu=configmenu, underline=0)


        # Help Menu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about, underline=0)
        menubar.add_cascade(label="Help", menu=helpmenu, underline=0)

        self.root.config(menu=menubar)

        self.show_welcome_message()

    def show_welcome_message(self):
        welcome_label = Label(self.content_frame, text="Welcome to Pegasus FE Collection Creator!\n"
                                                       "To get started, please use the File menu to create a new collection or open an existing one.",
                              wraplength=400, justify="center")
        welcome_label.pack(pady=50)

    def set_default_games_directory(self):
        default_games_directory = filedialog.askdirectory(title="Select Default Games Directory")
        if default_games_directory:
            self.default_games_directory = default_games_directory
            self.save_default_directory("default_games_directory", default_games_directory)
            #self.set_default_games_directory()
            messagebox.showinfo("Success", "Default games directory set successfully.")

    def set_default_collections_directory(self):
        default_collections_directory = filedialog.askdirectory(title="Select Default Collections Directory")
        if default_collections_directory:
            self.default_collections_directory = default_collections_directory
            self.save_default_directory("default_collections_directory", default_collections_directory)
            messagebox.showinfo("Success", "Default collections directory set successfully.")

    def prompt_collection_choice(self):
        self.clear_content_frame()

        self.collection_name_label = Label(self.content_frame, text="Enter the collection name:")
        self.collection_name_label.pack(pady=10)

        self.collection_name_entry = Entry(self.content_frame, width=50)
        self.collection_name_entry.pack(pady=10)

        self.collection_create_button = Button(self.content_frame, text="Create Collection", command=self.create_collection)
        self.collection_create_button.pack(pady=10)

    def open_existing_collection(self):
        self.clear_content_frame()

        self.file_path = filedialog.askopenfilename(initialdir=self.default_collections_directory, title="Select the existing collection file", filetypes=[("Text files", "*.txt")])
        if self.file_path:
            self.collection_name = os.path.basename(self.file_path).split('games.metadata.pegasus.txt')[0]
            self.start_adding_games()
        else:
            messagebox.showerror("Error", "File does not exist or no file selected. Please try again.")

    def create_collection(self):
        self.collection_name = self.collection_name_entry.get().strip()
        if self.collection_name:
            collection_name_lower = self.collection_name.lower()
            file_name = f"{collection_name_lower}games.metadata.pegasus.txt"
            self.file_path = os.path.join(self.default_collections_directory, file_name)
            if not os.path.isfile(self.file_path):
                with open(self.file_path, "w") as f:
                    f.write(f"# Collection of {self.collection_name} Games\n")
                    f.write(f"collection: {self.collection_name} Games\n")
                    f.write(f"shortname: {self.collection_name}\n\n")
            self.start_adding_games()
        else:
            messagebox.showerror("Error", "Collection name cannot be empty.")

    def read_games_from_file(self):
        games = []
        if self.file_path and os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                for line in f:
                    if line.startswith("game: "):
                        game_name = line[len("game: "):].strip()
                        games.append(game_name)
        return games

    def update_game_list(self):
        games = self.read_games_from_file()
        self.game_listbox.delete(0, tk.END)
        for game in games:
            self.game_listbox.insert(tk.END, game)



    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_about(self):
        messagebox.showinfo("About", "Pegasus FE Collection Creator\nVersion 0.99a\n\n\u00A9 2024 LSP\n\nCreated with the assistance of LLM AI")

    def start_adding_games(self):
        self.clear_content_frame()

        self.url_label = Label(self.content_frame, text="Enter the URL of the game's page on thegamesdb.net:")
        self.url_label.pack(pady=10)

        self.url_entry = Entry(self.content_frame, width=50)
        self.url_entry.pack(pady=10)

        self.scrape_button = Button(self.content_frame, text="Scrape Game Details", command=self.scrape_game_details)
        self.scrape_button.pack(pady=10)


        self.game_list_label = Label(self.content_frame, text="Current games in the collection:")
        self.game_list_label.pack(pady=10)

        self.game_listbox = tk.Listbox(self.content_frame, width=50, height=10)
        self.game_listbox.pack(pady=10)

        self.update_game_list()

    def check_url(self, url):
        if "thegamesdb.net" in url:
            return "thegamesdb"
        elif "store.steampowered.com" in url:
            return "steampowered"
        else:
            return "unsupported"

    def scrape_game_details(self):
        self.url = self.url_entry.get().strip()
        if not self.url:
            messagebox.showerror("Error", "URL cannot be empty.")
            return

        media_directory = filedialog.askdirectory(initialdir=self.default_games_directory, title="Select the base media directory")
        if not media_directory:
            messagebox.showerror("Error", "Media directory cannot be empty.")
            return


        #media_directory = filedialog.askdirectory(title="Select the base media directory")
        #if not media_directory:
        #    messagebox.showerror("Error", "Media directory cannot be empty.")
        #    return

        self.media_dir = media_directory  # Store media_dir as an instance variable

        self.url_type = self.check_url(self.url)
        if self.url_type == "unsupported":
            messagebox.showerror("Error", "That URL is not supported. Please try again.")
            return

        game_details = self.fetch_game_details(self.url, media_directory, self.url_type)
        if not game_details:
            return

        self.show_game_details(game_details)

    def fetch_game_details(self, url, media_directory, url_type):
        if self.url_type == "thegamesdb":
            return self.fetch_game_details_from_thegamesdb(url, media_directory)
        elif self.url_type == "steampowered":
            return self.fetch_game_details_from_steampowered(url, media_directory)

    def fetch_game_details_from_thegamesdb(self, url, media_dir):
        response = requests.get(url)
        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to fetch TheGamesDB. \n\n {response.status_code} \n\n Please check the URL and try again.")
            return None

        self.soup = BeautifulSoup(response.content, 'html.parser')

        game_details = {
            "title": "N/A",
            "lutris_id": "Enter Lutris ID",
            "description": "N/A",
            "platform": "N/A",
            "developer": "N/A",
            "publisher": "N/A",
            "release_date": "N/A",
            "game_genre": "N/A",
            "asset_video": "Enter path to video file",
            "assets": {}
        }

        # Scrape the game title
        title_tag = self.soup.find("h1")
        game_details["title"] = title_tag.get_text(strip=True) if title_tag else "N/A"
        sanitized_title = re.sub(r'[:\/\\]', '-', game_details["title"])
        game_details["title"] = sanitized_title

        # Scrape the description
        description_tag = self.soup.find("p", class_="game-overview")
        raw_description = description_tag.get_text(strip=True) if description_tag else "N/A"

        # Function to remove non-printable characters
        def remove_nonprintable(text):
            printable = set(string.printable)
            return ''.join(filter(lambda x: x in printable, text))

        # Get the raw description
        raw_description = remove_nonprintable(raw_description)

        # Split the description into paragraphs
        paragraphs = raw_description.split('\n\n')

        # Process each paragraph
        processed_paragraphs = []
        for paragraph in paragraphs:
            lines = paragraph.split('\n')
            processed_lines = []

            for line in lines:
                line = line.strip()

                if line:
                    processed_lines.append(f' {line}')
                else:
                    processed_lines.append(' .')

            processed_paragraphs.append('\n'.join(processed_lines))

        # Join the processed paragraphs
        processed_description = '\n\n'.join(processed_paragraphs)
        game_details["description"] = processed_description

        # Scrape the genre
        genre_paragraph = self.soup.find('p', string=lambda x: x and "Genre(s):" in x)
        if genre_paragraph:
            game_genre_scraped = genre_paragraph.string.split("Genre(s):")[1].strip()
            game_details["game_genre"] = game_genre_scraped

        # Locate the correct card-body div by searching for the one that contains the developer info
        card_body_div = None
        card_body_divs = self.soup.find_all("div", class_="card-body")
        for div in card_body_divs:
            if "Developer(s):" in div.get_text() or "Publisher(s):" in div.get_text():
                card_body_div = div
                break

        if card_body_div:
            paragraphs = card_body_div.find_all("p")
            for p in paragraphs:
                text = p.get_text()
                if "Platform:" in text:
                    game_details["platform"] = p.find("a").get_text(strip=True) if p.find("a") else text.split(":")[1].strip()
                elif "Developer(s):" in text:
                    game_details["developer"] = p.find("a").get_text(strip=True) if p.find("a") else text.split(":")[1].strip()
                elif "Release Date:" in text or "ReleaseDate:" in text:
                    game_details["release_date"] = text.replace("Release Date:", "").replace("ReleaseDate:", "").strip()

        # Find the tag containing "Publishers(s):"
        publishers_tag = self.soup.find(string=re.compile(r"Publishers\(s\):", re.IGNORECASE))
        if publishers_tag:
            # Get the parent paragraph tag and then find the anchor tag within it
            publisher_paragraph = publishers_tag.find_parent("p")
            if publisher_paragraph:
                publisher_anchor = publisher_paragraph.find("a")
                if publisher_anchor:
                    game_details["publisher"] = publisher_anchor.get_text(strip=True)
                else:
                    game_details["publisher"] = publisher_paragraph.get_text(strip=True).split("Publishers(s):")[1].strip()
            else:
                game_details["publisher"] = "N/A"
        else:
            game_details["publisher"] = "N/A"

        # return game_details

        # Scrape and download media files
        # self.scrape_and_download_media_thegamesdb(soup, game_details, media_dir)

        return game_details


    def fetch_game_details_from_steampowered(self, url, media_dir):
        response = requests.get(url)
        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to fetch Steam game page. \n\n {response.status_code} \n\n Please check the URL and try again.")
            return None

        self.soup = BeautifulSoup(response.content, 'html.parser')

        game_details = {
            "title": "N/A",
            "lutris_id": "Enter Lutris ID",
            "description": "N/A",
            "platform": "PC",
            "developer": "N/A",
            "publisher": "N/A",
            "release_date": "N/A",
            "game_genre": "N/A",
            "asset_video": "Enter path to video file",
            "assets": {}
        }

        # Find the details block
        details_block = self.soup.find('div', {'class': 'details_block'})

        if details_block:
            details_text = details_block.get_text(separator="\n")

            # Extract the title
            title_match = re.search(r'Title:\s*(.*)', details_text)
            if title_match:
                game_details["title"] = title_match.group(1).strip()

           # Extract the genre
            genre_block = details_block.find('b', text="Genre:")
            if genre_block:
                genre_span = genre_block.find_next('span', {'data-panel': '{"flow-children":"row"}'})
                if genre_span:
                    genres = [a.get_text().strip() for a in genre_span.find_all('a')]
                    game_details["game_genre"] = ", ".join(genres)

            # Extract the developer
            developer_block = details_block.find('b', text="Developer:")
            if developer_block:
                developer = developer_block.find_next('a')
                if developer:
                    game_details["developer"] = developer.get_text().strip()

            # Extract the publisher
            publisher_block = details_block.find('b', text="Publisher:")
            if publisher_block:
                publisher = publisher_block.find_next('a')
                if publisher:
                    game_details["publisher"] = publisher.get_text().strip()

            # Extract the franchise
            franchise_block = details_block.find('b', text="Franchise:")
            if franchise_block:
                franchise = franchise_block.find_next('a')
                if franchise:
                    game_details["franchise"] = franchise.get_text().strip()

            # Extract the release date
            release_date_match = re.search(r'Release Date:\s*(.*)', details_text)
            if release_date_match:
                release_date_string = release_date_match.group(1).strip()

        # Define a function to transform the date format
        def transform_date_format(date_str):
            # Parse the date string into a datetime object
            date_obj = datetime.strptime(date_str, "%b %d, %Y")

            # Format the datetime object into the desired string format
            formatted_date = date_obj.strftime("%Y-%m-%d")

            return formatted_date

        # Transform the release date string
        formatted_release_date = transform_date_format(release_date_string)
        print("Formatted Release Date:", formatted_release_date)

        # Add the formatted release date to the game_details dictionary
        game_details["release_date"] = formatted_release_date

        # Scrape the description
        description_div = self.soup.find('div', {'id': 'aboutThisGame'})
        if description_div:
            description_tag = description_div.find('div', {'class': 'game_area_description'})
            if description_tag:
                raw_description = description_tag.get_text(separator="\n", strip=True)
                print("Raw Description:", raw_description)

                # Function to remove non-printable characters
                def remove_nonprintable(text):
                    printable = set(string.printable)
                    return ''.join(filter(lambda x: x in printable, text))

                # Get the raw description
                raw_description = remove_nonprintable(raw_description)
                # Split the description into paragraphs by double line breaks
                # paragraphs = raw_description.split('\n\n')
                paragraphs = raw_description.split('\n\n')

                # Process each paragraph
                processed_paragraphs = []
                for paragraph in paragraphs:
                    lines = paragraph.split('\n')
                    processed_lines = []

                    for line in lines:
                        line = line.strip()
                        if line:
                            processed_lines.append(f' {line}\n .')
                        else:
                            processed_lines.append(' .')

                    processed_paragraphs.append('\n'.join(processed_lines))

                    # Join the processed paragraphs with double line breaks
                    processed_description = '\n\n'.join(processed_paragraphs)
                    print("Processed Description:", processed_description)
                    game_details["description"] = processed_description

                    # Define game_details and ensure 'platform' key is set
                    # game_details = {}
                    # game_details["platform"] = "PC"  # Ensure this is set properly based on your data


                    # Debugging prints to ensure everything is set correctly
                    print("Game Details:", game_details)

                    # Scrape and download media files (make sure this function exists)
                    # self.scrape_and_download_media_steampowered(soup, game_details, self.media_dir)

                    return game_details


    def scrape_and_download_media_thegamesdb(self, soup, game_details, media_dir, platform):
        title = game_details["title"]
        print("title:", title)
        print("self.platform:", self.platform)
        print("platform:", platform)

        # Ensure platform is a string
        if isinstance(platform, set):
            platform = next(iter(platform))
        print(f"Processed Platform: {platform} (type: {type(platform)})")

        platform_dir = os.path.join(media_dir, platform)
        os.makedirs(platform_dir, exist_ok=True)

        # Add downloaded images to metadata.txt file
        downloaded_files = set()

        for category, selector in self.IMAGE_CATEGORIES_THEGAMESDB.items():
            subfolder = self.IMAGE_CATEGORIES_COMMON[category]
            category_dir = os.path.join(platform_dir, subfolder)
            os.makedirs(category_dir, exist_ok=True)
            image_tags = soup.select(selector)

            for index, tag in enumerate(image_tags):
                image_url = tag.get('href')
                if image_url and image_url.lower().endswith(self.ALLOWED_IMAGE_FORMATS):
                    # Modify the image name to include the index
                    image_name = f"{title}_{index + 1}.jpg"
                    image_path = os.path.join(category_dir, image_name)
                    self.download_image(image_url, image_path)
                    if image_path and image_path not in downloaded_files:
                        downloaded_files.add(image_path)
                        if "assets" not in game_details:
                            game_details["assets"] = {}
                        if subfolder not in game_details["assets"]:
                            game_details["assets"][subfolder] = []
                        game_details["assets"][subfolder].append(image_path)

        print(f"Downloaded files: {downloaded_files}")
        return downloaded_files



    def scrape_and_download_media_steampowered(self, soup, game_details, media_dir, platform):
        title = game_details["title"]
        print("title:", title)
        print("self.platform:", self.platform)
        print("platform:", platform)

        # Ensure platform is a string
        if isinstance(platform, set):
            platform = next(iter(platform))
        print(f"Processed Platform: {platform} (type: {type(platform)})")

        platform_dir = os.path.join(media_dir, platform)
        os.makedirs(platform_dir, exist_ok=True)

        # Add downloaded images to metadata.txt file
        downloaded_files = set()

        # Process images
        for category, selector in self.IMAGE_CATEGORIES_STEAM.items():
            subfolder = self.IMAGE_CATEGORIES_COMMON.get(category)
            if not subfolder:
                continue
            category_dir = os.path.join(platform_dir, subfolder)
            os.makedirs(category_dir, exist_ok=True)
            image_tags = soup.select(selector)

            print(f"Category: {category}, Selector: {selector}, Found Tags: {len(image_tags)}")

            for index, tag in enumerate(image_tags):
                if category == "boxart/front":
                    image_url = tag.get('src')
                elif category == "screenshot":
                    image_url = tag.get('href')
                elif category == "fanart":
                    image_url = tag.get('href')
                elif category == "clearlogo":
                    image_url = tag.get('href')
                else:
                    image_url = None

                print(f"Extracted Image URL: {image_url}")

                if image_url:
                    # Remove query parameters for extension check
                    image_url_no_query = urljoin(image_url, urlparse(image_url).path)
                    if image_url_no_query.lower().endswith(self.ALLOWED_IMAGE_FORMATS):
                        # Modify the image name to include the index
                        image_name = f"{title}_{category.replace('/', '_')}_{index + 1}.jpg"
                        image_path = os.path.join(category_dir, image_name)
                        if self.download_image(image_url, image_path):
                            downloaded_files.add(image_path)
                            if "assets" not in game_details:
                                game_details["assets"] = {}
                            if subfolder not in game_details["assets"]:
                                game_details["assets"][subfolder] = []
                            game_details["assets"][subfolder].append(image_path)

        # Process videos
        for category, selector in self.VIDEO_CATEGORIES_STEAM.items():
            subfolder = "video"
            category_dir = os.path.join(platform_dir, subfolder)
            os.makedirs(category_dir, exist_ok=True)
            video_tags = soup.select(selector)

            print(f"Category: {category}, Selector: {selector}, Found Tags: {len(video_tags)}")

            for idx, tag in enumerate(video_tags):
                print(f"Video Tag Found: {tag}")
                video_sources = {
                    "hd": tag.get('data-mp4-hd-source'),
                    "sd": tag.get('data-mp4-source'),
                    "webm_hd": tag.get('data-webm-hd-source'),
                    "webm_sd": tag.get('data-webm-source')
                }

                for quality, video_url in video_sources.items():
                    if video_url:
                        video_url = urljoin(self.url, video_url)
                        video_extension = urlparse(video_url).path.split('.')[-1]
                        print(f"Video url: {video_url}\nVideo Extension: {video_extension}")
                        if video_extension in self.ALLOWED_VIDEO_FORMATS:
                            print("Video extension IS an allowed format...continuing.")
                            video_name = f"{title}_{category}_{idx+1}_{quality}.{video_extension}"
                            video_path = os.path.join(category_dir, video_name)
                            print(f"video name: {video_name} | video path: {video_path}")
                            if self.download_video(video_url, video_path):
                                downloaded_files.add(video_path)
                                print("The download_video function should have just been called, and it should be downloading videos based on the assets folder.")
                                if "assets" not in game_details:
                                    game_details["assets"] = {}
                                if subfolder not in game_details["assets"]:
                                    game_details["assets"][subfolder] = []
                                game_details["assets"][subfolder].append(video_path)

        print(f"Downloaded files: {downloaded_files}")
        return downloaded_files

    def download_image(self, url, path):
        print(f"Downloading image from {url} to {path}")
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code.
            with open(path, 'wb') as file:
                file.write(response.content)
            print(f"Image successfully downloaded to {path}")
            return True
        except Exception as e:
            print(f"Failed to download image from {url}. Error: {e}")
            return False


    def download_video(self, url, path):
        print(f"Attempting to download video from {url} to {path}")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Check for HTTP errors
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Video successfully downloaded to {path}")
                return True
            else:
                print(f"Failed to download video: {url} with status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error downloading video from {url}. Error: {e}")
            return False





    def show_game_details(self, game_details):
        self.clear_content_frame()

        self.entries = {}

        for field, label_text in [("title", "Title:"), ("description", "Description:"), ("platform", "Platform:"),
                                  ("developer", "Developer:"), ("publisher", "Publisher:"), ("release_date", "Release Date:"),("game_genre", "Genre:"),("lutris_id", "Lutris Internal ID:"),("asset_video","Path to Video File:")]:
            label = Label(self.content_frame, text=label_text)
            label.pack(anchor="w", padx=10)
            if field == "description":
                text_field = Text(self.content_frame, height=6, wrap=tk.WORD)
                text_field.insert(tk.END, game_details[field])
                text_field.pack(fill=tk.BOTH, padx=10, pady=5)
                self.entries[field] = text_field
            else:
                entry = Entry(self.content_frame, width=50)
                entry.insert(0, game_details[field])
                entry.pack(padx=10, pady=5)
                self.entries[field] = entry

        save_button = Button(self.content_frame, text="Save Game Details", command=lambda: self.save_game_details(game_details))
        save_button.pack(pady=10)

    def save_game_details(self, game_details):
        if not self.file_path:
            messagebox.showerror("Error", "No collection file specified.")
            return

        self.updated_details = {field: self.entries[field].get("1.0", tk.END).strip() if field == "description" else self.entries[field].get()
                           for field in ["title", "description", "platform", "developer", "publisher", "release_date", "game_genre", "lutris_id", "asset_video"]}

        # With the values confirmed, download the images, videos, and media.
        url = self.url_type
        platform = {self.updated_details['platform']}
        media_dir = self.media_dir
        # Debug statements to see the values
        print(f"Value of url: {url}")
        print(f"Value of self.url: {self.url}")
        print(f"Value of media_dir: {media_dir} (type: {type(media_dir)})")
        print(f"Value of self.media_dir: {self.media_dir}")
        print(f"Retrieved Platform: {platform} (type: {type(platform)})")

        # Ensure platform is a string
        if isinstance(platform, set):
            platform = next(iter(platform))
        print(f"Processed Platform: {platform} (type: {type(platform)})")

        # Convert media_dir to string if it's not already
        if not isinstance(media_dir, str):
            media_dir = str(media_dir)
        print(f"Processed media_dir: {media_dir} (type: {type(media_dir)})")


        # Update game_details with the processed platform
        game_details['platform'] = platform
        print(f"game_details['platform']: {game_details['platform']}")

        # Debug statements to ensure the correct type of platform
        # print(f"self.platform: {self.platform_entry.get()}")
        print(f"platform: {platform}")

        # Ensure soup is not None before proceeding
        if self.soup:
            # self.scrape_and_download_media_steampowered(self.soup, game_details, media_dir, platform)
            if url == "thegamesdb":
                self.scrape_and_download_media_thegamesdb(self.soup, game_details, media_dir, platform)
            elif url == "steampowered":
                self.scrape_and_download_media_steampowered(self.soup, game_details, media_dir, platform)
            else:
                messagebox.showerror("Error", "Unsupported URL detected.")
        # else:
          #  messagebox.showerror("Error", "Failed to load page content.")

        # with open(self.file_path, "a") as f:
        with open(self.file_path, "a") as f:
            f.write(f"# {self.updated_details['title']}\n\n")
            f.write(f"game: {self.updated_details['title']}\n")
            f.write(f"launch: /usr/bin/prime-run /usr/bin/lutris lutris:rungameid/{self.updated_details['lutris_id']}\n")
            # f.write(f"launch: {self.lutris_path} lutris:rungameid/{self.updated_details['lutris_id']}\n")
            f.write(f"file: lutris:rungameid/{self.updated_details['lutris_id']}\n")
            f.write(f"description: {self.updated_details['description']}\n")
            f.write(f"platform: {self.updated_details['platform']}\n")
            f.write(f"developer: {self.updated_details['developer']}\n")
            f.write(f"publisher: {self.updated_details['publisher']}\n")
            f.write(f"release: {self.updated_details['release_date']}\n")
            f.write(f"genre: {self.updated_details['game_genre']}\n")
            # Remove the below line when you can properly scrape videos.
            f.write(f"assets.video: \n")
            f.write(f"assets.video: {self.updated_details['asset_video']}\n")
            f.write(f"assets.grid: \n")
            for asset_type, paths in game_details["assets"].items():
                for path in paths:
                    f.write(f"assets.{asset_type}: {path}\n")
            f.write("\n\n")

        messagebox.showinfo("Success", "Game details saved successfully.")
        # self.update_game_list()
        self.start_adding_games()
        self.update_game_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = PegasusApp(root)
    root.mainloop()
