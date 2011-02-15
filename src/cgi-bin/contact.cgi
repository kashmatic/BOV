#! /usr/bin/perl -w
use strict;
use warnings;
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


#########################################################################
## Declaration of Modules required for this program
use CGI;
use HTML::Template;

##########################################################################
## Declaration of variables
my $cgi = new CGI;
my $content;

my $template = HTML::Template->new(
	filename => "templates/main.tmpl");

print $cgi->header;

$content = '<h3>Contact Details</h3>'
	.'<p class="bodypara">Please send comments and suggestions to : '
	.'<a href="mailto:_____EMAIL_____">_____EMAIL_____</a></p>';

my $banner = HTML::Template->new(
        filename => "templates/banner.tmpl");
my $footer = HTML::Template->new(
	filename => "templates/footer.tmpl");

## Display the page
$template -> param (TITLE => 'Contact');
$template -> param (SCRIPT => '');
$template -> param (BANNER => $banner->output);
$template -> param (FOOTER => $footer->output);
$template -> param (CONTENT => $content );

print $template->output;
print $cgi->end_html();
0;

## EOF ###################################################################
