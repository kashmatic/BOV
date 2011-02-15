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
use DBI;
use CGI::Carp qw(fatalsToBrowser);
use HTML::Template;

##########################################################################
## Declaration of variables
my $cgi = new CGI;
_____DATABASE_____
  or die( "unable to connect to the database" . $DBI::errstr );
my $hash = $cgi->param('hash');
my $query = $cgi->param('query');
my $email = $cgi->param('email');
my $file_size = $cgi->param('hash');
my $content;

##########################################################################
## Setup the header, title for the webpage
print $cgi->header;
#print $cgi->title("Alignment List");
#print $cgi->start_html();

my $script = "
<script type='text/javascript'>

window.onload = function(){
	ConvertRowsToLinks('tablist');
	ConvertRowsToLinks('list');
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

</script>
";

my $template = HTML::Template->new(
	filename => "templates/main.tmpl");

##########################################################################
## Access database 

my $summary;
my $sth_proj = $dbh->prepare("SELECT hash from BOV_project where hash=?");
$sth_proj->execute($hash) or die $DBI::errstr;
my ($hashCount) = $sth_proj->fetchrow_array();
if(!$hashCount){
	$content .= "The BLAST results you are trying to access could not be found. If the results are older than 60 days, they have been automatically removed from the system. Otherwise make sure that you have the correct and complete address for the results you are looking for.";
#	print $summary;
}
else{
my $sth_sum = $dbh->prepare("SELECT count(distinct(BOV_result.query_name)) from BOV_result,BOV_project where BOV_project.id = BOV_result.project_id and BOV_project.hash=?");
$sth_sum->execute($hash) or die $DBI::errstr;
my ($queryCount) = $sth_sum->fetchrow_array();

##########################################################################
## Display list of Queries with number of hits
$sth_sum = $dbh->prepare(qq{
SELECT BOV_result.query_name as query_name,count(BOV_hit.id) as hitCount from BOV_result, BOV_project, BOV_hit where BOV_hit.result_id = BOV_result.id 
and BOV_result.project_id = BOV_project.id
and BOV_project.hash=?
GROUP BY BOV_result.query_name
});

$sth_sum->execute($hash) or die $DBI::errstr;
my $Count;
$summary .= "<table class=\"tab\" id=\"tablist\" ><tr class=\"tab\"><th class=\"tab\"width=\"200\">Name of the Query sequence</th><th width=\"50\" class=\"tab\">No. of Hits</th></tr>";

## Fill in the List of Queries table
while(my ($query_name,$hitCount) = $sth_sum->fetchrow_array()){
	$summary .= "<tr class=\"tab\"><td class=\"tab\"><a href=\"viewhits.cgi?hash=".$hash."&query=".$query_name."#hit_table\" > $query_name </a></td><td class=\"tab\">$hitCount </td></tr>";
	$Count++;
}
$summary.="</table>";

##########################################################################
## Display the desciption of the page
$content.="<h3>Summary of BLAST output file</h3>"
	."<p class=\"bodypara\">"
	."The table below shows all query sequences and the number of hits for each query."
	."Click on the query sequence you are interested in to display the list of hits in a new table."
	."</p>";
$content .= "<p><b>Number of Queries found in the BLAST output file with Hits: ".$Count."<br />"
	.$summary;

##########################################################################
## Display the second table
if ($query){

## Access database
my $statement = "select distinct BOV_result.query_name,BOV_hit.hit_name, BOV_hit.id, BOV_hit.score, BOV_hit.evalue from BOV_hit,BOV_result,BOV_project where BOV_result.id = BOV_hit.result_id and BOV_project.id = BOV_result.project_id and BOV_project.hash=? and BOV_result.query_name=?";
my $sth = $dbh->prepare($statement) or die "error in query".$DBI::errstr;
#print $statement;
$sth->execute($hash,$query) or die $DBI::errstr;

my $pre;
while(my @ary = $sth->fetchrow_array()){
	if ($pre ne $ary[0]){
		if ($pre){$content.="</table>"};
		$content.="<p>List of Hits for query sequence '$ary[0]'.<br />"
			." The table below provides the Score and E-value for each hit."
			." Click on the hit sequence of interest to display details."
			."<a name=\"hit_table\" ></a></p>";
		$content.="<table  class=\"tab\" id=\"list\" >";
		$content.="<tr class=\"tab\"><th class=\"tab\" width=\"300\" align=\"left\" >Hit Sequences</th>"
			."<th  class=\"tab\" width=\"100\" >Score</th>"
			."<th  class=\"tab\" width=\"100\" >E Value</th></tr>";
		$pre=$ary[0];
	}
	$content.=qq{
		<tr class=\"tab\">
		<td class=\"tab\" text-align=\"left\"><a href=viewhsps.cgi?hit_id=$ary[2]&hash=$hash&query_name=$query>$ary[1]</a></td>
		<td class=\"tab\">$ary[3]</td>
		<td class=\"tab\">$ary[4]</td>
	</tr>
	};
} ## ENDwhile
$content.="</table>";
$content.="<p><b><a href=\"#top\">TOP</a></b></p>";

} ## ENDif
}
my $banner = HTML::Template->new(
	filename => "templates/banner.tmpl");
my $footer = HTML::Template->new(
        filename => "templates/footer.tmpl");

$template -> param (BANNER => $banner->output);
$template -> param (FOOTER => $footer->output);
$template -> param (SCRIPT => $script );
$template -> param (TITLE => 'Summary');
$template -> param (CONTENT => $content );

print $template->output;
print $cgi->end_html();
0;

## EOF ########################################################################
