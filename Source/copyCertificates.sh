#!/bin/bash

#cp ../../Certificates/* ./
echo "Copying certificates from /home.pi/Certificates to Certificates directory"

cp /home/pi/Certificates/*.pem.crt ../Certificates/device-certificate.pem.crt
cp /home/pi/Certificates/*private.pem.key ../Certificates/device-private.pem.key
cp /home/pi/Certificates/*public.pem.key ../Certificates/device-public.pem.key
cp /home/pi/Certificates/*CA.crt ../Certificates/root-CA.crt

if [ "$?" = "0" ]; then
	echo "Copy Successful"
else
  echo "Something went wrong"
	exit 1
fi

exit 1
