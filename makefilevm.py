#Set up enviorment variables needed for autentication
import os

target = open("serverinfo.txt", 'w')
target.truncate()

config = {'username':os.environ['OS_USERNAME'], 
          'api_key':os.environ['OS_PASSWORD'],
          'project_id':os.environ['OS_TENANT_NAME'],
          'auth_url':os.environ['OS_AUTH_URL'],
           }
#Set up Nova client
from novaclient.client import Client
nc = Client('2',**config)

import time
 
#Create server
if not nc.keypairs.findall(name="cloudproj"):
    with open(os.path.expanduser('cloudproj.pub')) as fpubkey:
        nc.keypairs.create(name="cloudproj", public_key=fpubkey.read())
image = nc.images.find(name="Ubuntu Server 14.04 LTS (Trusty Tahr)")
flavor = nc.flavors.find(name="m1.medium")
user_data = open("userdata.yml", 'r')
keyname = "cloudproj"
instance = nc.servers.create(name="G6-Project", image=image, flavor=flavor, key_name=keyname, userdata=user_data)
 
 
# Poll at 5 second intervals, until the status is no longer 'BUILD'
status = instance.status
while status == 'BUILD':
    time.sleep(5)
    # Retrieve the instance again so the status field updates
    instance = nc.servers.get(instance.id)
    status = instance.status
print "status: %s" % status

iplist = nc.floating_ips.list()
for ip_obj in iplist:
    if ((getattr(ip_obj,'instance_id')) == None):
        float_ip = getattr(ip_obj, 'ip')
        instance.add_floating_ip(float_ip)
        print "Server can be accessed from floating IP: %s" % float_ip
        break
else:
    print "No floating IP:s available! All are allocated."
    
print "Time out in 90 seconds to give the server a chance to start services and install packages." + "\nWhy don't you get a cup of coffee?"
time.sleep(90)
print "Server should be good to go. Please proceed."

line1 = "IP to server is: " + str(float_ip)
line2 = "SSH key used is: " + keyname

target.write(line1)
target.write("\n")
target.write(line2)
target.write("\n")
target.close()
