#! /usr/bin/perl -w
#########################################################
### Copyright 2008 The Trustees of Indiana University
###
### Licensed under the Apache License, Version 2.0 (the "License");
### you may not use this file except in compliance with the License.
### You may obtain a copy of the License at
###
###      http://www.apache.org/licenses/LICENSE-2.0
###
### Unless required by applicable law or agreed to in writing, software
### distributed under the License is distributed on an "AS IS" BASIS,
### WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
### See the License for the specific language governing permissions and
### limitations under the License.
##########################################################

use strict;
use warnings;

#########################################################################
## Declaration of Modules required for this program
use CGI;
use HTML::Template;

##########################################################################
## Declaration of variables
my $cgi = new CGI;

##########################################################################
## Setup the header, title for the webpage
print $cgi->header;

my $banner = HTML::Template->new(
	filename => "templates/banner.tmpl");
my $template = HTML::Template->new(
	filename => "templates/tutorial.tmpl");
my $footer = HTML::Template->new(
	filename => "templates/footer.tmpl");


##########################################################################
## Access database 

$template -> param (TITLE => 'Tutorial');
$template -> param (BANNER => $banner->output);
$template -> param (FOOTER => $footer->output);


#print $banner->output;
print $template->output;
print $cgi->end_html();
0;

## EOF ########################################################################
