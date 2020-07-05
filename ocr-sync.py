import argparse
import datetime
from html.parser import HTMLParser
import urllib
import urllib.request
import os
import shutil
import time


V = 0


class HTMLLinkCollector(HTMLParser):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.links = []

	def handle_starttag(self, tag, attrs):		
		if tag != 'a': return
		
		for attr in attrs:
			if attr[0] != 'href': continue
			self.links.append(attr[1])
			break


def downloadImage(url, save_dir, overwrite=False):
	filename = url.split('/')[-1]
	out = os.path.join(save_dir, filename)
	
	if os.path.exists(out) and not overwrite:
		if V: print('Skipping "{0}" (file already exists)'.format(out))
		return 1
		
	print('Saving "{0}"... '.format(out), end='')
	
	with urllib.request.urlopen(url) as resp, open(out, 'wb') as out_file:		
		shutil.copyfileobj(resp, out_file)
	
	print('Done')
	
	return 0


def getImageUrls(url):
	print('Attempting to retrieve images from "{0}"... '.format(url), end='')
	
	with urllib.request.urlopen(url) as resp:
		html = resp.read().decode('utf-8')

	collector = HTMLLinkCollector()
	collector.feed(html)
	images = [url+filename for filename in collector.links]
	
	print('Found {0} images'.format(len(images)))
	
	return images


def getTimestamp():
	return str(datetime.datetime.now())


def init(save_dir):
	if not os.path.exists(save_dir):
		if V: print('Creating save dir: "{0}"'.format(save_dir))
		os.mkdir(save_dir)


def parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('url')
	parser.add_argument('--save-dir', default=os.getcwd())
	parser.add_argument('--live', type=bool, default=True)
	parser.add_argument('--sync-interval', type=int, default=10)
	parser.add_argument('--verbose', type=bool, default=False)
	
	return parser.parse_args()


def sync(url, save_dir):
	print('\n{0}'.format(getTimestamp()))	
	print('Starting sync')
	count = [0, 0, 0]	# [0]: downloaded, [1]: skipped, [2]: failed
	
	try:
		img_urls = getImageUrls(args.url)
	except urllib.error.URLError as urlErr:
		print('[!] Sync failed due to url error')
		return
	
	for img_url in img_urls:
		try:
			result = downloadImage(img_url, args.save_dir)
		except urllib.error.HTTPError as httpErr:
			print(httpErr)
			result = 2
		finally:
			count[result] += 1
	
	print('{0} downloaded | {1} skipped (file exists) | {2} failed'.format(*tuple(count)))
	
	


if __name__ == '__main__':
	args = parseArgs()
	V = args.verbose
	init(args.save_dir)
	sync(args.url, args.save_dir) # first sync
	
	while args.live:
		time.sleep(args.sync_interval)
		sync(args.url, args.save_dir)
			
	
	
	
	
	
