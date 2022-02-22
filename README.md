# Quantify
## Setup

### Install Quantify

#### - If you are developing Quantify
- Clone Quantify and install it in developer mode
~~~shell
foo@bar:~$ git clone https://github.com/GreenPlanet-Capital/Quantify
foo@bar:~$ cd Quantify
foo@bar:~$ pip3 install -e .
~~~
- Create a virtual environment (highly recommended)
~~~shell
foo@bar:~$ python3 -m venv env
foo@bar:~$ source env/bin/activate 
~~~

#### - If you are using Quantify as an app
- Create a virtual environment (highly recommended)
~~~shell
foo@bar:~$ python3 -m venv env
foo@bar:~$ source env/bin/activate 
~~~
- Install Quantify
~~~shell
foo@bar:~$ pip3 install git+https://github.com/GreenPlanet-Capital/Quantify@main
~~~

### Setup your API Keys
~~~shell
foo@bar:~$ datamgr set api-keys Alpaca AlpacaKey <public-key-here> AlpacaSecret <private-key-here>
~~~

### Quantify App
~~~shell
foo@bar:~$ quantify # opens a shell for Quantify
Quantify 0.0.0

(q)>
~~~

~~~shell
Quantify 0.0.0

(q)> help
Commands:
======================
run  set  show  track  untrack
~~~
