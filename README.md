# Death Ray Service
Death Ray Service (DRS) is a service that only turns on the anti-biofouling UVC for 2.5 seconds every minute within a single time during the day, given by the `config.json` file, on the OBSEA ANERIS EMUAS camera.

## Features
- Anti-biofiling UVC light with a $4.2\%$ duty-cycle
- Possibility to diside when to use UVC

## Future work
Implement a driver circuit for the UVC in order to obtain a higher duty-cycle.

## Install
### Step 0: Connect device to your computer
Connect your PC with the Raspberry Pi you intend to use, either by cable or network. Make sure you have an IP on the same interface as the device you intend to work on. Say if your connected to the Pi through ethernet and the Pi's IP is `192.168.1.2`, you can scan the network using `arp` or wireshark and choose an IP on the same subnet that is available. 

Let's say we decide to use `192.168.1.6` (because it's unused) and that we are connected through a network interface on our computer called `en8`, then in order to add the IP to our interface we can use the following command:

**Mac:**
```shell
sudo ifconfig en8 alias 192.168.1.6 255.255.255.0
```
**Linux:**
```shell
sudo ip addr add 192.168.1.6/24 dev en8
```
for Linux `addr add` can be substituted with `a a` if you want to write it quicker.

**Windows:** If you are really using Windows I can't help you...

**NOTE:** If you don't know what network interfaces you have available or want to see what IPs are your computer has on different interfaces, you can check this using `sudo ifconfig` for Mac and 
`sudo ip addr` or `sudo ip a` for Linux.

To verify that we are able to connect to our Raspberry Pi form our PC we can simply use ping:
```shell
ping 192.168.1.2
```
If you get an answer an no packets lost you have successfully connected to the Raspberry Pi! 


### Step 1: Copy or clone repo
There are two ways of getting the DRS on the desired Raspberry Pi: a) clone repo onto your PC and copy it over or b) clone it directly to the Pi.

#### A: Copy over to Pi using scp
If you don't want to log into git on the host device, there is an option to clone this repo onto your personal computer before copying it over afterwards. In order to do this first clone the repo to a fitting place your computer, either with https or ssh:

**https:**
```shell
git clone https://github.com/OsloMet-OceanLab/deathray.git
```

**SSH:**
```shell
git clone git@github.com:OsloMet-OceanLab/deathray.git
```

The difference is that SSH requires a [public key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) while HTTPS requires a [github token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens), please consult the github documentation  [github documentation](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) for more on this.

After cloning the repo, we can then copy over the files using the [Secure Copy Protocol](https://en.wikipedia.org/wiki/Secure_copy_protocol). Assuming that the host IP is `192.168.1.2` and the username is `pi`, the copy command will be:
```shell
scp -r deathray/ pi@192.168.1.2:
```
This will copy the whole deathray directory into the `/home/pi/` directory on the Raspberry Pi.

#### B: git clone directly on the pi
To clone the github repo directly onto the computer you must first log inn using ssh. Assuming that the host IP is `192.168.1.2` and the username is `pi`, the copy command will be:
```shell
ssh pi@192.168.1.2
```
Once you are logged into the Raspberry Pi you are free to choose if you want to clone using https or SSH:

**https:**
```shell
git clone https://github.com/OsloMet-OceanLab/deathray.git
```

**SSH:**
```shell
git clone git@github.com:OsloMet-OceanLab/deathray.git
```

### Step 2: Move shit around
For our service to be in a place where we can't delete it by accident we would like to move it to the `/opt/` directory. On the Raspberry Pi we start by moving the `deathray.service` file first:
```shell
sudo mv deathray/deathray.service /opt/
```
then we move the rest of the directory:
```shell
sudo mv deathray/ /opt/
```

### Step 3: Users, groups and permissions
When all files are in their intended places, we have to set up a user to run the service and add it to the `gpio` group so that our service can actually interact with the GPIO pins on the Pi. First check if the user exists:
```shell
cat /etc/passwd | grep emuas
```
if this yields no printouts, then we have to create the user and add it to correct groups:
```shell
sudo useradd -r -s /usr/sbin/nologin emuas
sudo groupadd emuas
```
Add user to gpio:
```shell
sudo usermod -aG gpio emuas
```
To verify that the user has been created and added to the correct groups simply run:

```shell
groups emuas
```
The printout should then read `emuas : emuas gpio`. With the group in place we can now give it permission to own the `/opt/deathray/` directory and the files containing it. This is easy using:

```shell
sudo chown -R emuas:emuas /opt/deathray/
```
Verify ownership by running
```shell
sudo ls -l /opt/deathray/
```

### Step 4: Register and start service
Now that our user has been set up with the right permissions it is time to actually start the service. First we have to create a symlink from `/opt/deathray.service` to `/etc/systemd/system/deathray.service`, to do this we can run:
```shell
sudo systemctl link /opt/deathray.service
```
we then have to enable the service to let it run and reload the system daemon:
```shell
sudo systemctl enable deathray.service
sudo systemctl daemon-reload
```
When this is done we can start our service
```shell 
sudo systemctl start deathray.service
```
In order to check that the service has started up correctly, the status of the service can be checked using:
```shell 
sudo systemctl status deathray.service
```
If you wish to stop the service this can be done using:
```shell 
sudo systemctl stop deathray.service
```
or restart the service using:
```shell 
sudo systemctl restart deathray.service
```
After all this is done the service should be up and running.
