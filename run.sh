#!/bin/bash
gcc *.c -o serwer -pthread
echo "Kompilacja OK"
if [ "$1" == "debug" ]; then
  exit
fi
echo "Startowanie serwera..."
./serwer
