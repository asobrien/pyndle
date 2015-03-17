pyndle
======
An ebook server to that interfaces with [Calibre][CalibreProject].

I wrote and small program using the [web.py][webpyProject] framework in order to serve up books in my [Calibre][CalibreProject] library that I could download using my kindle. Calibre uses a sqlite as database to manage content, and *pyndle* interfaces with the native Calibre sqlite database to serve up contnent.

While *pyndle* is fully functional, it is spartan---no css, for instance!

##### ~~Check out a live demo of *pyndle* here: [http://pyndle.bearonis.com](http://pyndle.bearonis.com)~~ #####


***********


Trying Out Pyndle
-----------------
Getting *pyndle* to run on your own server in a production-like environment is a little more involved than just trying out the program. If you want to try out the program on your own computer or develop the program any further then you'll need [web.py][webpyProject].


### Install webpy ###
Install via `pip`:

	pip install web.py

or, download web.py from [here](http://webpy.org/static/web.py-0.37.tar.gz) and extract it and install it by running the following from the extracted folder:

	python setup.py install

You may need to run the above as `sudo`. See the [web.py installation instructions](http://webpy.org/install#macosx) if you have a problem.


### Download pyndle ###
Go ahead and grab *pyndle* from [github][pyndleProject]. You can download the latest stable version as zipped archive directly from right [here][pyndleArchive].


### Link a Demo Calibre Library ###
Grab a copy of a demo `Calibre library` from [here][demoCalibreLibrary]. It's filled with a few random books from [Project Gutenberg][gutenbergProject]. If you have your own library you can use that, but keep the folder structure consistent (or modify `config.py`).

Unzip `sampleCalLib.zip` and place the `sampleCalLib` folder into `pyndle/content/`. We're about ready to run.

### Verify Your Folder Structure ###
Within your `pyndle` folder you should have the following layout:

	pyndle/
	├── README.md
	├── content
	│   └── sampleCalLib
	│       ├── Calibre Library
	│       │   └── ... lots of books ...
	│       ├── Calibre Librarymetadata.db
	│       └── Calibre\ Librarymetadata.db
	├── fcgi.sh
	├── pyndleNginxConfig.txt
	└── src
	    ├── config.py
	    ├── main.py
	    ├── static -> ../content/sampleCalLib/Calibre\ Library/
	    └── templates
	        ├── authors.html
	        ├── book.html
	        ├── books.html
	        ├── booksbyauthor.html
	        ├── index.html
	        └── recent.html
	        
### Run pyndle ###
Navigate to `pyndle/src` and run the following command:

	python main.py

You should get the following output:

	http://0.0.0.0:8080/

Go ahead and point your browser to the address given from the output and give the site a try!


Running *pyndle* on a Webserver
-----------------------------
While you can quickly try out and demo *pyndle* using the instructions above, if you want to run *pyndle* on webserver. The setup is a bit more involved. Here are instructions for getting *pyndle* running on a Debian distro (RaspberryPi with Raspbian, for instance!) with Nginx.


### Install Nginx ###
web.py works with a variety of servers, but we're going to use nginx here. You can use whatever server but my reasoning for nginx is:

1) It works with a Raspberry Pi
2) It's fast
3) It's a lot smaller than Apache
4) It works

If you're on a Debian distro (Raspbian) you can install nginx with:

	sudo apt-get install nginx

### Install fcgi and Dependencies ###
While we're using the package manager, we might as well install the additional packages required to get web.py running on the server.

Install `spawn-fcgi` if you don't have it. On a Debian Distro run:

	sudo apt-get install spawn-fcgi
	
You'll also need `Flup` if you don't have it already:

	sudo apt-get install python-flup
	

### Setup a Virtual Hosts File ###
Create a virtual hosts file in `/etc/nginx/sites-available/pyndle.website.com`. Copy the contents from the sample config file, but edit it to match your site. Activate the site by creating a symbolic link to `sites-enabled`:

	sudo ln -s /etc/nginx/sites-available/pyndle.website.com /etc/nginx/sites-enabled/pyndle.website.com
	

### Get your Server Ready ###

Setup a user named pyndle to host all the files:

	sudo adduser pyndle

Upload the `src` folder into a directory into the home folder of `pyndle`. We'll use `/home/pyndle/ebook_server` here.

Create a `src` directory and a `content` directory. Copy source files and your `Calibre Library` folder into `src` and `content`, respectively.

The full path to your Calibre Library should be: `/home/pyndle/ebook_server/content/sampleCalLib/Calibre Library`.

Edit `config.py` and enter the correct settings; for example my `config.py` file reads:

	# Site Configuration File

	# /path/to/Calibre Library/
	# Must end with /
	LIBRARY_ROOT = '/home/pyndle/ebook_server/content/sampleCalLib/Calibre Library/'

	# http://books.website.com/
	# Must end with /
	SITE_ROOT = 'http://pyndle.website.com/'

A relative link is included in the package, but if you have any issues just create a symbolic link from your `Calibre Library` to `src/static`:

	ln -s '/home/pyndle/ebook_server/content/sampleCalLib/Calibre Library/' /home/pyndle/ebook_server/src/static
	
Fix ownership and permissions so nginx can serve up content, from within user pyndle's home directory, run the following:

	sudo chown -R www-data:www-data ebook_server/
	sudo chmod 755 ebook_server/

### Edit main.py ###
When using *pyndle* with an fcgi inteface you need to modify `main.py`.

Uncomment the the line in at the bottom of `main.py` inside the `if __name__ == "__main__"` function, like so:

	if __name__ == "__main__":
	    # Uncomment below for NGINX + WSGI website
	    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr) #wsgi setup
	    app = web.application(urls, globals())
	    app.run()


### Spawing fcgi ###

Unlike Apache, fcgi processes must be manually spawned. If you minimally modified the nginx configuration file, you can use the following command to start an fcgi process:

	spawn-fcgi -d /home/pyndle/ebook_server/src -f /home/pyndle/ebook_server/src/main.py -a 127.0.0.1 -p 9009

You may need to update your firewall settings.



### Let's Get This to Run Automagically! ###

1) Copy the `fcgi.sh` script to `/etc/init.d/fcgi`.

2) Make sure the file is executable:
	
	chmod 755 /etc/init.d/fcgi

3) If on Debian you can use the Debian-specific command:

	sudo update-rc.d fcgi defaults

4) If you need to inteact with the `spawn-fcgi` service you can just run, for example:

	sudo service fcgi start
	sudo service fcgi stop
	sudo service fcgi reload

Now if you restart your server, the pyndle server should automatically restart once the server's booted up.


Other Comments
--------------
If you want to protect your site's content then [http auth](http://wiki.nginx.org/HttpAuthBasicModule) is probably the easiest way.

If you want to keep your library up-to-date, consider just `rsycn`ing and `cron` your Calibre library that you maintain.

Enjoy!



[gutenbergProject]: http://www.gutenberg.org
[pyndleProject]: https://github.com/asobrien/pyndle
[CalibreProject]: http://calibre-ebook.com
[webpyProject]: http://webpy.org
[pyndleArchive]: https://github.com/asobrien/pyndle/archive/v1.0.zip
[demoCalibreLibrary]: http://bearonis.com/pub/doc/sampleCalLib.zip


