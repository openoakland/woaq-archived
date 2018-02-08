#!/bin/bash

# create the db
echo "CREATE DATABASE IF NOT EXISTS woiep" | mysql -u root -ppassword

# run the two load scripts
mysql -u root -ppassword woiep < pm.mysql
mysql -u root -ppassword woiep < pmload.mysql
