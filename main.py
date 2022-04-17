import requests
from bs4 import BeautifulSoup
import datetime as dt
from tkinter import *
from tkcalendar import Calendar
from tkinter import messagebox
import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth



formatted_date = ""
billboard_top_endpoint = "https://www.billboard.com/charts/hot-100/"

def set_date():
    global formatted_date
    formatted_date = calendar.get_date()
    messagebox.showinfo(title="Date Received", message=f"Collecting the top 100 songs from {formatted_date}")
    quit_tk()

def quit_tk():
    main_root.destroy()


main_root = Tk()
main_root.geometry("400x400")

calendar = Calendar(main_root, selectmode="day",
                    year=dt.datetime.today().year,
                    month=dt.datetime.today().month,
                    day=dt.datetime.today().day,
                    date_pattern="y-mm-dd")

calendar.pack()
select_button = Button(text="Select", command=set_date)
select_button.pack()
main_root.mainloop()


user_pick_endpoint = f"{billboard_top_endpoint}{formatted_date}"
print(user_pick_endpoint)
with requests.get(user_pick_endpoint, "r") as file:
    top_list_source = file.text

soup = BeautifulSoup(top_list_source, "html.parser")
song_list = soup.select(selector="li #title-of-a-story")
song_titles = [song.get_text().strip() for song in song_list]

print(song_titles)
auth_manager = SpotifyOAuth(client_id=config.SPOTIFY_CLIENT_ID,
                            scope="playlist-modify-private",
                            client_secret=config.SPOTIFY_CLIENT_SECRET,
                            redirect_uri=config.REDIRECT_URI,
                            cache_path="./.cache")
auth_manager.get_auth_response()
sp = spotipy.Spotify(auth_manager=auth_manager)

song_uri_list = []
uri_year = formatted_date.split("-")[0]

for song in song_titles:
    uri_request = sp.search(q=f"track:{song} year:{uri_year}", type="track")
    try:
        uri = uri_request["tracks"]["items"][0]["uri"]
        song_uri_list.append(uri)
    except IndexError:
        print(f"Can not find {song} in spotify")

user_id = sp.current_user()["id"]
my_playlist = sp.user_playlist_create(user=user_id,
                                      name=f"{formatted_date} Billboard Top 100",
                                      public=False)
# print(my_playlist)
playlist_id = my_playlist["id"]
sp.playlist_add_items(playlist_id=playlist_id, items=song_uri_list)
print("Finished")