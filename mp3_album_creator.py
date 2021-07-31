#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script generates mp3-files with metadata that "simulate" music albums. 
It was developed for testing purposes of media player software. 

The script parses a descriptor file goven as first argument (see below for format). 
According to this file it generates a folder for each album. In each of these albumfolders 
it creates an audiofile per track. The created tracks contain synthesized (text to spech) 
audio telling the name of the album, tracknumber and other details. Also mp3-metadata
is added to each track. 

*********************************
title: my Album title
artist: my band name
year: 1992
genre: House
track: track number one
track: track number two
track: ok this is enough
*********************************
title: album title 
artist: band name
year: 2020
track: my track 
track: party at my house
track: ...
<further tracks>
*********************************
<further album(s)>
*********************************

DEPENDENCIES: 
- ffmpeg needs to be installed on your system for this to work. 
- currently only for MAC since we are using NSSpeechSynthesizer. 

TODO: 
- Include automatic creation of an albumcover
- extend it to run on windows too
"""

__author__ = "Tom orr"
__version__ = "0.1.0"
__license__ = "MIT"

from  AppKit import NSSpeechSynthesizer
import Foundation
import os, time, sys, subprocess

ALBUMKEYS = ["title", "artist", "year", "genre", "track"]

##################################
# PARSER
def parse_file(filename, keys):
	# open file and parse
	albums = []
	album = {}
	album_cnt = 0
	track_cnt = 0

	file = open(filename, 'r')
	lcnt = 1 # line counter
	for line in file.readlines():
		l = line.strip()
		
		# differentiate between the line-types.
		# lines with at least five * start new album: 
		if "*****" in l: 
			album_cnt = album_cnt + 1
			if (bool(album) == True):
				# todo: make sure all the albumkeys where used!! otherwise throw error
				albums.append(album)
			album = {}
			track_cnt = 0

		# ignore empty lines
		elif l.isspace() or l is "": 
			pass

		# everything else
		else:
			try: 
				# parse lines with "<key/tag>: <data>"
				tagval = l.split(": ") 
				tag = tagval[0]
				value = tagval[1].strip()
				if tag in keys:
					if tag == "track":
						track_cnt = track_cnt + 1
						album[tag + " " + str(track_cnt)] = value
					else: 
						album[tag] = value
				else: 
					raise IOError()

			except: 
				raise IOError('Parser error in line ' + str(lcnt) + ' of file ' + filename + '.')

		lcnt = lcnt+1 # increase the line counter

	return albums


##################################
# WORKHORSE
def create_album (target_dir, album_dict):
	albumtitle = album_dict["title"]
	artist = album_dict["artist"]
	year = album_dict["year"]
	genre = album_dict["genre"]
	
	#setup track indices and names
	tracks = {}
	for key in album_dict: 
		if key.startswith("track "):
			idx = int(key.split(" ")[1])
			title = album_dict[key]
			tracks[idx] = title
	
	#create a folder at target_dir named "<artist> - <albumtitle> (<year>)"
	foldername = artist + " - " + albumtitle + " (" + year + ")"
	folderpath = target_dir + "/" + foldername
	os.mkdir(folderpath)

	#create a wav files with TextToSpeach in that folder: 
	for idx in tracks:
		filepath = folderpath + "/" + str(idx) + " - " + tracks[idx] + ".aiff"
		text = "This is track " + str(idx) + " named " + tracks[idx] + ". It is on the album " + albumtitle + " by " + artist + ". The genre is " + genre + "."
		text_to_wav(filepath, text)
		wav_to_mp3(filepath, {'title':tracks[idx], 'track':str(idx), 'album':albumtitle, 'artist':artist, 'genre':genre } )
		os.remove(filepath)


##################################
# HELPERS
def text_to_wav (filepath, text):
	nssp = NSSpeechSynthesizer
	ve = nssp.alloc().init()
	ve.setRate_(200)
	url = Foundation.NSURL.fileURLWithPath_( unicode(filepath, "utf-8"))
	ve.startSpeakingString_toURL_(text, url)
	ve.stopSpeaking()

def wav_to_mp3(filepath, metadata):
	in_file = filepath
	out_file = os.path.splitext(filepath)[0] + '.mp3'
	sub_cmd = ['ffmpeg', '-i', in_file, '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k']
	for key in metadata: 
		sub_cmd += ['-metadata', key + '=' + metadata[key]]
	sub_cmd += [out_file]
	with open(os.devnull, 'wb') as quiet: 
		ret = subprocess.call(sub_cmd, stdout=quiet, stderr=quiet)


######################################
######################################
# MAIN
def main():
	if (len(sys.argv) < 2): 
		print "No descriptor file."
		exit()
	else:
		file = sys.argv[1]
		# todo: check if file exits

	albums = parse_file(file, ALBUMKEYS)

	output_dir = os.path.dirname(os.path.realpath(__file__))

	for album in albums:
		create_album(output_dir, album)

	# todo: add progessbar for creating albums

######################################
if __name__ == "__main__":
    main()