#! /usr/bin/perl -w
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

use strict;
use warnings;

#########################################################################
## Declaration of Modules required for this program
use CGI;
use DBI;
use CGI::Carp qw(fatalsToBrowser);
use HTML::Template;

##########################################################################
## Declaration of variables
my $cgi = new CGI;

_____DATABASE_____
        or die("unable to connect to the database" . $DBI::errstr);

my $email = $cgi->param('id');

my $content;

##########################################################################
## Setup the header, title for the webpage
print $cgi->header;

print "<html><head>
	<script type='text/javascript'>

	window.onload = function(){
		ConvertRowsToLinks('tab');
	}

	function ConvertRowsToLinks(xTableId){
		var rows = document.getElementById(xTableId).getElementsByTagName('tr');
		for(i=0;i<rows.length;i++){
			var link = rows[i].getElementsByTagName('a')
			if(link.length == 1){
				rows[i].onclick = new Function(\"document.location.href='\" + link[0].href + \"'\");
				rows[i].onmouseover = new Function(\"this.className='highlight'\");
				rows[i].onmouseout = new Function(\"this.className=''\");	
			}
		}
	}
	</script>";

my $template = HTML::Template->new(
	filename => "templates/main.tmpl");

##########################################################################
## Access database 

my $summary;
my $statement = "SELECT hash,file_name,created_on from BOV_project where email =?" ;

my $sth = $dbh->prepare($statement);
$sth->execute($email) or die $DBI::errstr;

## Display information 
$summary.="<table class=\"tab\" id=\"tab\" ><table class=<tr class=\"tab\"><th class=\"tab\"width=\"200\">No.</th><th class=\"tab\"width=\"200\">Date of creation</th><th class=\"tab\"width=\"200\">View</a></th></tr>";


my $count =0;
while(my ($hash,$filename, $createdon) = $sth->fetchrow_array()){
        $summary.="<tr class=\"tab\"><td class=\"tab\"width=\"200\">".++$count."</td><td class=\"tab\"width=\"200\">$createdon</td><td class=\"tab\"width=\"200\"><a href='viewhits.cgi?hash=$hash'> Link </a></td></tr>";
}

$summary.="</table>";

$content.="<h3>List of previous BLAST output file submissions</h3>"
	."<p class=\"bodypara\">The list below provides a summary of all previous BLAST output files submitted by the user, with reference to the email address. These files will be stored in our database for a period of _____LIFETIME_____ days. Please follow the link provided to view the previous submissions.</p>"
	."<p class=\"bodypara\">Please Note:"
	."<ol><li>"
	."If the file is not present in the designated field below, the reason could be that the file name was not provided while submitting this file."
	."</li><li>"
	."If the concerned file is absent in the table, the reason could be the file was submitted more than _____LIFETIME_____ days ago. The file has been removed from the database."
	."</li><li>"
	."If the file is not present in the database, do contact us."
	."</li></p>"
	."<h4>List of files</h4>"
	."<b> ".$summary."</b>";

$content.="<p><b><a href=\"#top\">TOP</a></b></p>";
my $banner = HTML::Template->new(
        filename => "templates/banner.tmpl");
my $footer = HTML::Template->new(
        filename => "templates/footer.tmpl");

## Display the page
$template -> param (CONTENT => $content );
$template -> param (TITLE => "HISTORY" );
$template -> param (BANNER => $banner->output );
$template -> param (FOOTER => $footer->output );

print $template->output;
print $cgi->end_html();
0;

## EOF ###################################################################
