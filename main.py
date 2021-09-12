# Importing relevant audio libraries
import pyaudio
import wave
import os
import urllib
import urllib.request
import re
import json
from youtube_dl import YoutubeDL
from moviepy.editor import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydub import AudioSegment
import subprocess
from tkinter import *
import pygame
import lyricsgenius


# Initizializing GUI
root = Tk()
root.title("Secret Superstar")
root.geometry("1000x800")
root.configure(bg="#A366E6")
appName = Label(root, text="Secret Superstar", font=("helvetica",'20','bold'), bg = "#A366E6", fg='#FFFFFF')
topText = Label(root, text="Please enter the name of the artist: ", bg="#A366E6", fg="#FFFFFF", font=("helvetica",'10','normal'))
entry1 = Entry(root)
secondText = Label(root, text="Please enter the nane of the song you want to sing: ", font=("helvetica",'10','normal'), bg="#A366E6", fg="#FFFFFF")
root.iconbitmap("icon.ico")
entry2 = Entry(root)
appName.pack()

topText.pack()

entry1.pack()

secondText.pack()

entry2.pack()


# Get Youtube API Key from Google Developers and put in variable (USER NEEDS TO DO)
api_key = 'AIzaSyBHTYoNhCHQlkRPO7IICt0U6aVgqOekewE'
# Get Genius API
genius = lyricsgenius.Genius("5u2WFz0UZRo2uy0CkPWczPOeYTIqTgzbkvJAdu85YLcfTuzYXuEBFcazqEWXbuUU")



total_time = 0
artist_name = ''
song_name = ""
# Allow user to input song they want, and adds "instrumental" to end of Youtube
#search_keyword = input("Enter the name of the song you want: ").split()
#search_keyword = "+".join(search_keyword) + "instrumental"

def storeData():
    global artist_name
    global song_name
    artist_name = entry1.get()
    song_name = entry2.get()
    search_keyword = "+".join(entry1.get().split()) + "+" +"+".join(entry2.get().split()) + "instrumental"

    # Opens the Youtube link where the song is being searched based on the user input
    html  = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_keyword)
    # Users regex to find all videos based on what the user is searching for
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    # gets the first video on the Youtube search page
    video_id = video_ids[0]

    # Gets all the data regarding the specific video that is being used for the background music
    search_url = 'https://www.googleapis.com/youtube/v3/videos?id='+video_id+"&key="+api_key+"&part=contentDetails"
    req = urllib.request.Request(search_url)
    response = urllib.request.urlopen(req).read().decode('utf-8')
    data = json.loads(response)
    all_data = data['items']

    # Based on data from Youtube API, calculates total time in seconds of the video using its duration attribute
    minutes = 0
    global total_time
    total_time = 0
    duration = all_data[0]['contentDetails']['duration']
    if "M" in duration:
      minutes = int(duration[2:].split('M')[0])
      m_index = duration.find("M")
      seconds = int(duration[m_index+1:-1])
      total_time += minutes*60
      total_time += seconds
    else:
      seconds = int(duration[2:].split("S")[0])
      total_time = seconds

    # creates the final video link, which follows the standard Youtube video URL and the video ID
    final_link = "https://www.youtube.com/watch?v=" + video_id

    # Downloading the Youtube video to the system after finding it, as an .mp4 file
    audio_downloader = YoutubeDL({'format':'mp4'}) 
    # gets the data of the video that was downloaded
    video = audio_downloader.extract_info(final_link)  
    # gets the title of the video 
    download_name = video["title"]

    # Inputs location of directory where the recordings are saved (CHANGES BASED ON USER)
    inputdir = "C:\\Users\\14694\\Desktop\\HowdyHack2021"

    # Looks through entire folder to find files of type .mp4
    for filename in os.listdir(inputdir):
        actual_filename = filename[:-4]
        if(filename.endswith(".mp4")):
            # if a file ends in .mp4, changes file type to .mp3
            os.rename(filename, "song.mp3")
        else:
            continue

    # Beginning process to convert from .mp3 to .wav file
    # indicates the source file, which is the .mp3 file                                                                       
    src = "song.mp3"

    # convert .mp3 to .wav file called "sound.wav"                                                            
    subprocess.call(['ffmpeg', '-i', 'song.mp3','sound.wav'])

    # lowers sound of the background music by 10 dB
    song_wav = AudioSegment.from_wav('sound.wav')
    background_sound = song_wav - 10
    background_sound.export("final_sound.wav", "wav")

    artist = genius.search_artist(artist_name, max_songs=1, sort="title", include_features=True)
    song = genius.search_song(song_name, artist.name)
    lyrics = (song.lyrics)
    lyrics_start_label = Label(root, text = f'Lyrics for {artist_name} - {song_name}',font =("Helvetica", 10), bg="#A366E6", fg="#FFFFFF")
    #lyrics_label = Label(root, text=lyrics, font=("Helvetica",14), bg="#A366E6", fg="#FFFFFF")
    lyrics_start_label.pack()
 

    lyrics_label = Text(root)
    lyrics_label.pack()
    lyrics_label.insert(END, lyrics)

    startButton = Button(root, text="Start Singing!", command=start_recording, font=("helvetica",'15','bold'), fg="#FFFFFF", bg="#BC96E6", activeforeground="#BC96E6", activebackground="#FFFFFF",height=1, width=20)    
    startButton.pack(pady=30)
    

def start_recording():

  play()

  # T = Text(root, height = 5, width = 52)  

  # T.insert(END, lyrics)
  

  # Start Recording of the vocals once video downloading is done
  chunk = 1024  # Record in chunks of 1024 samples
  sample_format = pyaudio.paInt16  # 16 bits per sample
  channels = 1 # can vary based on input mic, USER SHOULD UPDATE
  freq = 22050  # Record at 22050 samples per second, based on input mic, USER SHOULD UPDATE
  secs = total_time # takes total length of video and saves to seconds of recording
  file_name = "output.wav" # recording is saved to a file called "output.wav"
  interface = pyaudio.PyAudio()  # Create an interface to PortAudio

  print('Status: Recording') # Notifies user that it starts recording the audio file

  stream = interface.open(format=sample_format,
                  channels=channels,
                  rate=freq,
                  frames_per_buffer=chunk,
                  input=True)

  frames = []  # Initialize array to store frames

  # Store data in chunks for duration of video
  for i in range(0, int(freq / chunk * secs)):
      data = stream.read(chunk)
      frames.append(data)

  # Stop and close the stream 
  stream.stop_stream()
  stream.close()
  # Terminate the PortAudio interface
  interface.terminate()

  print('Status: Finished Recording') # Notifying user that the audio file 

  # Save the recorded data as a WAV file
  wav_file = wave.open(file_name, 'wb')
  wav_file.setnchannels(channels)
  wav_file.setsampwidth(interface.get_sample_size(sample_format))
  wav_file.setframerate(freq)
  wav_file.writeframes(b''.join(frames))
  wav_file.close()

  # Taking both .wav files and combining them into a single file called "combined.wav"
  sound1 = AudioSegment.from_file("output.wav") # voice file
  sound2 = AudioSegment.from_file("final_sound.wav") # instrumental file
  combined = sound1.overlay(sound2)
  combined.export("combined.wav", format='wav')

  finalButton = Button(root, text="Play final product!",command=play_final, font=("helvetica",'15','bold'), fg="#FFFFFF", bg="#BC96E6", activeforeground="#BC96E6", activebackground="#FFFFFF",height=1, width=20)
  finalButton.pack(pady=20)
  stopButton = Button(root, text="Stop", command=stop, font=("helvetica",'15','bold'),fg="#FFFFFF", bg="#BC96E6")
  stopButton.pack(pady=20)
  


# CREATING THE GUI
# root = Tk()
# root.title("Secret Superstar")
# root.geometry("500x400")
# root.configure(bg="#A366E6")

pygame.mixer.init()

def play():
    pygame.mixer.music.load("final_sound.wav")
    pygame.mixer.music.play(loops=0)

def stop():
    pygame.mixer.music.stop()

def play_final():
  pygame.mixer.music.load("combined.wav")
  pygame.mixer.music.play(loops=0)

# appName = Label(root, text="Secret Superstar", font=("helvetica",'20','bold'), bg = "#A366E6", fg='#FFFFFF')
# # topText = Label(root, text="Please enter the name of the artist: ", bg="#A366E6", fg="#FFFFFF", font=("helvetica",'10','normal'))
# # entry1 = Entry(root)
# # secondText = Label(root, text="Please enter the nane of the song you want to sing: ", font=("helvetica",'10','normal'), bg="#A366E6", fg="#FFFFFF")
# # entry2 = Entry(root)
# # appName.pack()
# # topText.pack()
# # entry1.pack()
# # secondText.pack()
# # entry2.pack()

downloadButton = Button(root, text="Get your music!", command=storeData, font=("helvetica",'15','bold'), fg="#FFFFFF", bg="#BC96E6", activeforeground="#BC96E6", activebackground="#FFFFFF",height=1, width=20)
downloadButton.pack(pady=30)



#stopButton = Button(root, text="Stop", command=stop, font=("helvetica",'15','bold'),fg="#FFFFFF", bg="#BC96E6")
#stopButton.pack(pady=20)


root.mainloop()

# Removes the separate files of audio that are unneeded once the final combined audio is created
os.remove("final_sound.wav")
os.remove("output.wav")
os.remove("song.mp3")
os.remove("sound.wav"
)