# Music Organizer & Playlist Manager

A Python-powered tool to organize new songs, extract metadata, generate a playlist assignment spreadsheet, and update `.m3u8` playlists automatically. Designed to work with structured music libraries and custom playlist systems.

---

## Features

- Reads new songs from a designated folder
- Extracts song metadata (title, artist, album) using `eyed3`
- Generates an Excel spreadsheet for playlist assignment
- Copies songs into proper album folders under a central `Music/` directory
- Assigns songs to playlists based on spreadsheet input
- Appends songs to `.m3u8` playlist files with correct formatting

---

## Folder Structure

- The program needs a specific structure to work:
- MyMusicFolder/Autoinserter/New Songs  <- Your new songs go here


## Requirements
Install the dependencies with:

```bash
pip install -r requirements.txt
