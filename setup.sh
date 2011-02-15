#!/bin/sh

#########################################################
## Copyright 2008 The Trustees of Indiana University
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
#########################################################


############################################################
##
## REQUIRED PARAMETERS
##
## These parameters must be set by the user before installation will proceed.
##
##
############################################################

## Support e-mail address
#
# BOV advertises an address that BOV users may contact for help. This
# allows your users questions to be directed to your support
# group. This may be the same as sender_email.
#
# e.g. support_email="help@myorg.org"
#
support_email="kashi.revanna@unt.edu"

## Sendmail 
#
# Enter the location of the binary file for sendmail 
#
# e.g. sendmail_path="/usr/sbin/sendmail"
#
sendmail_path="/usr/sbin/sendmail"

## Email Encryption
#
# To ensure that a user's results are kept private, a hashed version 
# of their email address is used to access stored results. This private
# string is added to the e-mail address to ensure that no one else can 
# duplicate the results.
#
# e.g. email_variable="2H5TQY"
#
email_variable="P82KNT"

## Base Apache URI
#
# Enter the base URI for the machine that will host BOV. This variable is
# used to create the e-mail that is sent to users.
#
# e.g. apache_uri = "http://www.myorg.org"
#
apache_uri="http://bioinfo.cas.unt.edu"

############################################################
##
## OPTIONAL PARAMETERS
##
## These parameters have default values that will work if you follow
## the basic INSTALL steps. If you wish to connect to an existing
## database server, or specify a custom lifetime for results you may
## edit them below.
##
############################################################

## Database Username
#
# This is the username you use to connect to MySQL. The INSTALL doc
# gives instructions for creating a bov username.
#
database_username="bov"

## Database Password
#
# This is the password used to connecto to MySQL. If left blank, no
# password will be used. 
#
database_password=""

## Database Name
#
# This is the name of the MySQL database BOV will connect to. The
# INSTALL doc gives instructions for creating a database named
# microbial.
#
database_name="microbial"

## Database Host
#
# The hostname of the machine where the database is located. By
# default this is the same machine where apache will run.
#
database_host="localhost"


## Results Lifetime
#
# This is the number of days results will be kept on the server. After
# this time, they will be deleted to save space. To never delete
# results, set this variable to 0. If the variable is not set to 0, 
# A cronjob will be created in the home directory, to delete the records from
# the database.
#
lifetime=60


#####################  DO NOT EDIT BELOW THIS LINE!!!!!! ######################
###############################################################################

## Check for Required Parameters
if [ ! $support_email ] || [ ! $sendmail_path ] || [ ! $email_variable ] || [ ! $apache_uri ]
then
        echo ".. Error: Required parameters are not provided."
	exit 1
fi

## Strings present in source files
olduser="_____DATABASE_____"
oldemail="_____EMAIL_____"
olduri="_____URI_____"
oldlifetime="_____LIFETIME_____"
oldmail="_____SENDMAIL_____"
oldvariable="_____VARIABLE_____"

printf "\n.. The program is running....... Please wait.\n"

## Cleanup these directories, if present
rm -rf cgi-bin
rm -rf htdocs
rm -rf bin

## Copy these directories from the src
cp -rp src/cgi-bin cgi-bin
cp -rp src/htdocs htdocs
cp -rp src/bin bin

## Search and replace strings in the cgi-bin and htdocs directory.
find bin/ -type f | while read file
do
	sed s#$oldlifetime#$lifetime#g $file > $file.$$
	mv $file.$$ $file
done

find cgi-bin/ -type f | while read file
do
	sed s#$oldemail#$support_email#g $file > $file.$$
	mv $file.$$ $file
	sed s#$olduri#$apache_uri#g $file > $file.$$
	mv $file.$$ $file
	sed s#$oldlifetime#$lifetime#g $file > $file.$$
	mv $file.$$ $file
	sed s#$oldmail#$sendmail_path#g $file > $file.$$
	mv $file.$$ $file
	sed s#$oldvariable#$email_variable#g $file > $file.$$
	mv $file.$$ $file
	if [ $database_host != "localhost" ]
	then
		sed s#$olduser#my\ \$dbh\ =\ DBI\-\>connect\(\'DBI\:mysql\:$database_name\:$database_host\:3306\'\,\'$database_username\'\,\'$database_password\'\)#g $file > $file.$$
		mv $file.$$ $file
	else
		sed s#$olduser#my\ \$dbh\ =\ DBI\-\>connect\(\'DBI\:mysql\:$database_name\'\,\'$database_username\'\,\'$database_password\'\)#g $file > $file.$$
		mv $file.$$ $file
	fi
done

echo ".. The path has been updated."

## Create tables within the database
if [ $database_password ]
then
	mysql -h $database_host -u $database_username -p $database_password -D $database_name < bin/create_tables.sql
else
	mysql -h $database_host -u $database_username $database_name < bin/create_tables.sql
fi

echo ".. The database access details has been updated."
echo ".. The tables have been created in the database."

if [ $lifetime -gt 0 ]
then 
	if [ $database_password ]
	then
		echo "mysql -h $database_host -u $database_username -p $database_password -D $database_name < /usr/bin/BOV/manageBOV.sql" > bin/clean_database.sh
	else
		echo "mysql -h $database_host -u $database_username $database_name < /usr/bin/BOV/manageBOV.sql" > bin/clean_database.sh
	fi
fi

chmod -R 755 cgi-bin
chmod -R 755 htdocs
chmod -R 755 bin

echo ".. Installation Complete"

## EOF #######################################
