import pandas as pd
import os
import eyed3
import shutil
import urllib.parse
import pygame
import natsort
from colorama import init, Fore, Style

RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
RESET = ""

dirNewSongs = os.path.join("..", "New Songs")
dirPlaylist = os.path.join("..", "..")
pathSpreadsheet = 'selection.xlsx'
dataNewSongs = []
dataPlaylists = {}


def Debug_DisplayVariables():
  print("\n=== Current Variables ===\n")

  print("1. New Songs Data:")
  if dataNewSongs:
    for i, song in enumerate(dataNewSongs, start=1):
      print(f"  {i}. Name: {song['name']}")
      print(f"     Artist: {song['artist']}")
      print(f"     Album: {song['album']}")
      print(f"     Filename: {song['filename']}")
      print(
          f"     Playlists: {', '.join(song['playlists']) if song['playlists'] else 'None'}"
      )
      print()
  else:
    print("  No new songs available.\n")

  print("2. Playlists Data:")
  if dataPlaylists:
    for playlistName, _ in dataPlaylists.items():
      print(f"  - {playlistName}")
  else:
    print("  No playlists available.\n")

  print("=========================\n")


def Menu_Main():
  print("=== Main Menu ===")
  print("[1] Generate Spreadsheet")
  print("[2] Process Playlists")
  print("[0] Exit")


def Init_ReadPLaylists():
  print(f"Reading Playlists from {dirPlaylist}")
  global dataPlaylists
  m3u8Files = sorted(
      [f for f in os.listdir(dirPlaylist) if f.endswith(".m3u8")])
  dataPlaylists = {fileName: None for fileName in m3u8Files}


def Helper_ExtractMetadata(filePath):
  try:
    audioFile = eyed3.load(filePath)
    songData = {
        'name': audioFile.tag.title if audioFile.tag.title else "",
        'artist': audioFile.tag.artist if audioFile.tag.artist else "",
        'album': audioFile.tag.album if audioFile.tag.album else "",
        'filename': os.path.basename(filePath)
    }
    return songData
  except Exception as e:
    print(f"{RED}ERROR Could not extract metadata from {filePath}: {e}{RESET}")
    return None


def Init_ReadSongs():
  print(f"Reading Songs from {dirNewSongs}")
  global dataNewSongs
  songCount = 0
  songFiles = sorted(os.listdir(dirNewSongs))
  for songFile in songFiles:
    songPath = os.path.join(dirNewSongs, songFile)
    if os.path.isfile(songPath):
      songData = Helper_ExtractMetadata(songPath)
      if songData:
        songData['playlists'] = []
        dataNewSongs.append(songData)
        songCount += 1
  print(f"\n{songCount} songs read from the directory.")


def M1_GenerateSpreadsheet():
  print(f"{YELLOW}ACHTUNG! THIS WILL OVERWRITE THE EXISTING SPREADSHEET!...{RESET}")
  input("Press any key to proceed...")
  if not dataNewSongs or not dataPlaylists:
    print(f"{RED}ERROR: No songs or playlists data available!{RESET}")
    return
  print(f"Generating spreadsheet from {pathSpreadsheet}")
  songNames = natsort.natsorted([song['filename'] for song in dataNewSongs])
  playlistNames = list(dataPlaylists.keys())
  df = pd.DataFrame(0, index=playlistNames, columns=songNames)
  try:
    df.to_excel(pathSpreadsheet, index=True)
    print(f"Spreadsheet generated: {pathSpreadsheet}")
  except Exception as e:
    print(f"{RED}ERROR while generating the spreadsheet: {e}{RESET}")


def M2_CopySongs():
  print(f"{GREEN}----------Copying songs...{RESET}")
  if not dataNewSongs:
    print(f"{RED}ERROR: No songs to copy. Check New Songs directory.{RESET}")
    return
  for song in dataNewSongs:
    songPath = os.path.join("..", "New Songs", song['filename'])
    albumFolder = os.path.join("..", "..", "Music", song['album'])
    if not os.path.exists(albumFolder):
      print(
          f"{YELLOW}ACHTUNG: directory does not exist! Creating folder...{RESET}"
      )
      os.makedirs(albumFolder)
      print(
          f"{YELLOW}Created new folder: {albumFolder} CHECK DIRECTORY{RESET}")
      input("Press any key to proceed...")
    destinationPath = os.path.join(albumFolder, song['filename'])
    if os.path.exists(destinationPath):
      print(f"{YELLOW}WARNING: File '{song['filename']}' already exists in {albumFolder}. Overwriting...{RESET}")
      input("Press any key to proceed...")
    try:
      shutil.copy(songPath, destinationPath)
      print(f"Copied song {song['filename']} to {albumFolder}")
    except Exception as e:
      print(f"{RED}ERROR: Failed to copy song {song['filename']}: {e}{RESET}")


def M2_AssignPlaylists():
  print(f"{GREEN}----------Assigning playlists to dataNewSongs...{RESET}")
  if not os.path.exists(pathSpreadsheet):
    print(f"{RED}ERROR: Spreadsheet {pathSpreadsheet} not found!{RESET}")
    return

  df = pd.read_excel(pathSpreadsheet, index_col=0)
  print(f"Loaded spreadsheet from {pathSpreadsheet}")

  for playlistName in df.index:
    for songName in df.columns:
      if df.loc[playlistName, songName] == 1:
        for song in dataNewSongs:
          if song['filename'] == songName:
            song['playlists'].append(playlistName)
            print(f"Assigned song '{songName}' to playlist '{playlistName}'")
            break
  print("Playlists assigned to songs based on the spreadsheet.")


def M2_AssignM3u8():
  print(f"{GREEN}----------Editing m3u8 playlists...{RESET}")
  global dataNewSongs
  pygame.mixer.init()
  for song in dataNewSongs:
    song_path = os.path.join("..", "New Songs", song['filename'])
    if song['playlists']:
      try:
        encoded_duration = int(pygame.mixer.Sound(song_path).get_length())
      except Exception as e:
        print(f"{RED}ERROR processing {song['filename']}: {e}{RESET}")
        continue
      encoded_album = urllib.parse.quote(song['album'])
      encoded_filename = urllib.parse.quote(song['filename'])
      m3u8_line = f"#EXTINF:{encoded_duration},{song['artist']} - {song['name']}\n"
      m3u8_line += f"Music/{encoded_album}/{encoded_filename}"
      for playlist in song['playlists']:
        m3u8_file_path = os.path.join("..", "..", playlist)
        if os.path.exists(m3u8_file_path):
          with open(m3u8_file_path, 'a', encoding='utf-8') as playlist_file:
            playlist_file.write(m3u8_line + '\n')
            print(f"Added {song['artist']} - {song['name']} to {playlist}")
        else:
          print(
              f"{RED}ERROR Playlist file {playlist} not found in the directory!{RESET}"
          )


def main():
  Init_ReadPLaylists()
  Init_ReadSongs()
  while True:
    Menu_Main()
    choice = input("\n>> ")
    if choice == '1':
      M1_GenerateSpreadsheet()
    elif choice == '2':
      M2_CopySongs()
      M2_AssignPlaylists()
      M2_AssignM3u8()
    elif choice == '0':
      print("YOU HAVE BEEN TERMINATED")
      break
    else:
      print(f"{RED}Invalid choice. Please try again.{RESET}")


if __name__ == "__main__":
  init(autoreset=True)
  try:
    main()
  except Exception as e:
    print(f"{RED}FATAL ERROR: {e}{RESET}")
    input("Press Enter to exit...")
