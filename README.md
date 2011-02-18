## Publication
-----------------
* Gollapudi, R., Revanna, K.V., Hemmerich, C., Schaack, S. & Dong, Q. (2008) BOV- A Web-based BLAST Output Visualization Tool. BMC Genomics 9, 414. This little toy was ranked as a "Highly accessed" paper by BioMed Central.
* [PUBMED](http://www.ncbi.nlm.nih.gov/pubmed/18793422)

## Setup
-----------------

#### Supported Operating Systems
* Linux, Solaris (untested on other Unix flavors)

#### Supported Browsers
* Mozilla Firefox 2 or higher
* Internet Explorer 6 or higher
* Safari
* Opera

#### Prequisites
* [Apache 1.3 or 2.0]( http://www.apache.org )
* [MySQL Database]( http://dev.mysql.com/ )
* [BioPerl 1.5.2 or higher]( http://www.bioperl.org/ )

#### CPAN Perl Modules (can be downloaded from CPAN archive at http://www.cpan.org)
* [DBI](http://search.cpan.org/~timb/DBI-1.616/DBI.pm)
* [DBD::mysql](http://search.cpan.org/~capttofu/DBD-mysql-4.018/lib/DBD/mysql.pm)
* [HTML::Template](http://search.cpan.org/~samtregar/HTML-Template-2.9/Template.pm)
* [GD](http://search.cpan.org/~lds/GD-2.45/GD.pm)
* [CGI::Ajax](http://search.cpan.org/~bpederse/CGI-Ajax-0.707/lib/CGI/Ajax.pm)

#### Core Perl Modules
* [CGI](http://search.cpan.org/~markstos/CGI.pm-3.52/lib/CGI.pm)
* [CGI::Carp](http://search.cpan.org/~markstos/CGI.pm-3.52/lib/CGI/Carp.pm)
* [Data::Dumper](http://search.cpan.org/~smueller/Data-Dumper-2.128/Dumper.pm)
* [Digest::MD5](http://search.cpan.org/~gaas/Digest-MD5-2.51/MD5.pm)
* [Math::Round](http://search.cpan.org/~grommel/Math-Round-0.06/Round.pm)
* [File::stat](http://search.cpan.org/~makoto/File-Stat-0.01/Stat.pm)
* POSIX
* [Storable](http://search.cpan.org/~ams/Storable-2.25/Storable.pm)

#### Database Setup 
BOV requires a MySQL database to store data and generate results. By default, BOV will connect to MySQL installed on the local machine, using the username bov, and the database name microbial. To setup BOV with these default settings, issue the following commands from the unix command prompt.

To create the username bov, without password

> mysql -uroot -p password -e 'create user bov@localhost'

With password

> mysql -uroot -p password -e 'create user bov@localhost identified by password'

To create the database and give permissions to your user
    
> mysql -uroot -p password -e 'create database microbial'
> mysql -uroot -p password -e 'grant select,insert,create,drop on microbial.* to bov@localhost'

If you want to use different database settings, reference the MySQL documentation for instructions on how to configure the database.


## Installation
------------

Download BOV from http://cgb.indiana.edu/files/downloads/Blast_Output_Viewer.tar.gz

Uncompress BOV using the command 

> tar -zxvf Blast_Output_Viewer.tar.gz

Edit the setup.sh to customize BOV for your location. You must set the parameters under "REQUIRED PARAMETERS". If you did not use the default database settings, you must also define the connection information under "OPTIONAL PARAMETERS".


Execute the setup command to configure BOV, this creates two folders in the same 
directory called 'cgi-bin' and 'htdocs'

> setup.sh

If you have set the 'lifetime' value in setup.sh for automatic expiration of results, a shell script will be created in

> bin/clean_database.sh

To have this command executed automatically, you need to add the following entry to your crontab.

> &#042; 0 * * * sh /PATH/TO/clean_database.sh
       
Rename the htdocs directory to BOV and copy it to the directory your apache installation uses for html files. This directory is defined in your apache configuration file as 'DocumentRoot'. So if your apache configuration includes

> DocumentRoot "/var/www/htdocs"

you would execute

> cp -rp htdocs /var/www/htdocs/BOV

Rename the cgi-bin directory to BOV and copy it to the directory your apache installation uses for cgi-bin executables. This may be defined as 'ScriptAlias' in your apache configuration.

> ScriptAlias /cgi-bin/ "/var/www/cgi-bin"

in which case you would execute

> cp -rp cgi-bin /var/www/cgi-bin/BOV

If your apache configuration does not include ScriptAlias, then append cgi-bin to the DocumentRoot, e.g.

> cp -rp cgi-bin /var/www/htdocs/cgi-bin/BOV

## Authors
-----------
* Rajesh Gollapudi
* Kashi Vishwanath Revanna
* Chris Hemmerich
* Sarah Schaack
* Qunfeng Dong
