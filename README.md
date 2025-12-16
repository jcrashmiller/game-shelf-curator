# game-shelf-curator

Game Shelf Curator is a small desktop tool for building and maintaining curated game launcher collections without relying on opaque launchers or manual metadata editing.

It provides a simple GUI for searching public game databases, reviewing scraped metadata, and generating clean, explicit files for use with Pegasus and similar front ends.

## Why this exists

Managing game collections across emulators, front ends, and storage locations often means juggling inconsistent metadata, hidden config files, or heavyweight launchers.

This project was built to:
- Make metadata generation explicit and reviewable
- Reduce manual editing of text and image files
- Keep the user in control of what gets added and how
- Make creating and updating custom game collections easier

## Intended audience

- Users of Pegasus and similar game launcher front ends
- People managing larger retro or mixed-platform collections
- Anyone who prefers simple tools and readable files over all-in-one launchers

# Screenshots

![Search for NCAA 2K2 for Sega Dreamcast](assets/images/screenshots/searching_thegamesdb_ncaa_2k2_dreamcast.png)
![Search resuslts for NCAA 2K2 for Sega Dreamcast](assets/images/screenshots/results_thegamesdb_ncaa_2k2_dreamcast.png)
![NCAA 2K2 added to collection](assets/images/screenshots/NCAA_2K2_added.png)
![Resulting created files](assets/images/screenshots/ncaa_2k2_resulting_files.png)

# Core Features
- Scraping metadata and images from thegamesdb.net, store.steampowered.com
- Download screenshots and box art
   - Automatically add entries for downloaded images to metadata.txt
- Edit scraped metadata before committing
- Lutris game ID for launch command

## How it works (high level)

1. Search supported databases for a game
2. Review and edit scraped metadata before committing
3. Automatically download and incorporate box art, screenshots, and other media
4. Generate launcher-friendly metadata and file structures for use with Pegasus


## Considerations and limitations

- This tool scrapes public websites (TheGamesDB, Steam)
- Requests are intentionally limited to avoid unnecessary load
- Additional sources and launchers can be added, but are currently out of scope


## Project status

The tool is functional and actively used, with ongoing refinements focused on usability, documentation, and workflow clarity.


## Note

Screenshots and metadata from TheGamesDB and NCAA 2K2 are used for demonstration purposes only and are believed to fall under fair use. All trademarks and copyrighted material are the property of their respective owners.


