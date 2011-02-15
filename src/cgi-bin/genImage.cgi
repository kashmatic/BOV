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

#########################################################
## Declaring the required packages 
use strict;
use Data::Dumper;
use Storable qw(freeze thaw);
use CGI::Carp qw(fatalsToBrowser);
use lib qw(BOVModules);
use BOVM qw(demo drawhsp showControlPanel );
use GD;
use POSIX qw(floor);
use CGI::Ajax;
use CGI;
use DBI;
use Bio::Search::HSP::GenericHSP;
use HTML::Template;
#########################################################

#########################################################
## Parameters
my $cgi = new CGI;


# open the html template
my $template =
  HTML::Template->new( filename =>
	  "templates/new_header.tmpl" );

#------------------------------------------------------
#   Connect to the database
#------------------------------------------------------
_____DATABASE_____
  or die( "unable to connect to the database" . $DBI::errstr );

#------------------------------------------------------
#   Declare the global parameters
#------------------------------------------------------

my $query  = $cgi->param('query_name');
my $hit    = $cgi->param('hit_name');
my $hash   = $cgi->param('hash');
my $hit_id = $cgi->param('hit_id');
my $filter_evalue = $cgi->param('filter_evalue');

#------------------------------------------------------
#   Get the parameters
#------------------------------------------------------
my @highlight = ( $cgi->param('highlight') ) ? ($cgi->param('highlight')) : ();

my @rank      = $cgi->param('rank');

## Error checking Query start
my $query_start =
  ( $cgi->param('query_start') > 0 ) ? $cgi->param('query_start') : 0;
my $query_end = $cgi->param('query_end') || $cgi->param('query_length') || 0;

my $query_constant=$cgi->param('query_constant');

if ( $query_end > $query_constant) { $query_end = $query_constant; }

$query_start = ($query_start > $query_end-50) ? 0 : $query_start;

my $query_length = ( $query_end - $query_start )
  || $cgi->param('query_length')
  || 0;


my $hit_start = 
  ( $cgi->param('hit_start') > 0 )  ? $cgi->param('hit_start') : 0;
my $hit_end = $cgi->param('hit_end') || $cgi->param('hit_length') || 0;

my $hit_constant=$cgi->param('hit_constant');

if ( $hit_end > $hit_constant) { $hit_end = $hit_constant; }
$hit_start = ($hit_start > $hit_end-50) ? 0 : $hit_start;

my $hit_length = ( $hit_end - $hit_start ) || $cgi->param('hit_length') || 0;


#########################################################
## Draw the image. Calls for subroutine 'drawimage'
my ( $baseimagefile, $imagemap );

## create link for image
my $link = "image.cgi?hash=$hash&hit_id=$hit_id&query_length=$query_length&hit_length=$hit_length&query_start=$query_start&query_end=$query_end&hit_start=$hit_start&hit_end=$hit_end";
$link .= "&highlight=$_" for @highlight;
$link .= "&rank=$_" for @rank;

#########################################################
## contents to be printed below the image, download and summary option
my $content;
$content = qq{
	<h5>
	<a href='viewhits.cgi?hash=$hash' target='_self'>$query</a> ::
	<a href='viewhits.cgi?hash=$hash&query=$query#hit_table' target='_self'>$hit</a> ::
	HSP Image
	</h5>
	<img name='hspimage' src='$link' usemap='#imagemap' border=0px bgcolor='white' >
	<h5><a href='$link' target='_blank'>Download Image</a>
};	## ENDcontent

#########################################################
## Contents of the HELP div, describing how to..
my $help = "<h3>Description</h3>"
	."<p class='bodypara'>The image on the left shows the alignment between the selected query sequence and the selected hit sequence. The name of the query sequence and hit sequence is displayed in the image.</p>"
	."<h4>Tab field - HSP Select</h4>"
	."<p class='bodypara'>The table contains all the hits sequences, but only those hits selected on the previous page are displayed. You can again choose to select any hit sequence and click on 'Display Selected HSP' to display the selected hits. The HSPs can also be filtered by E-value. By clicking on 'Display Selected HSP' the image modifies to display the selected HSP.<br />"
	."Highlight the matching subsequence by clicking on 'view' in the 'Highlight' column or view the alignment in a new window by clicking 'view' in the 'Alignment' column.</p>"
	."<h4>Tab field - Zoom</h4>"
	."<p class='bodypara'>This tool allows you to zoom into a particular region of the query sequence or hit sequence. The zoom parameters can be reset by clicking on 'reset zoom values'.</p>";

#########################################################
## contents of the ZOOM div
my $value1 = ($query_start<1)?1:$query_start;
my $value2 = ($hit_start<1)?1:$hit_start;
my $zoomForm = qq{
	<!-- <div id='zoom'> -->
  		<h3> Select positions to zoom </h3>
		<form name='hsp_form' action='genImage.cgi' method='get'>
	 	<table border='0px' width='100%'>
	 	<input type=hidden name="hit_id" value='$hit_id' />
	 	<tr><td><label for='query_start'>Query Start:</label></td>
		<td><input type=text name='query_start' value='$value1' size=10></td>
		<td><label for='query_end'> Query End: </label></td>
		<td><input type=text name='query_end' value='$query_end' size=10></td></tr>
	 	<tr><td><label for='hit_start'>Hit Start:</label></td>
	 	<td><input type=text name="hit_start" value='$value2' size=10> </td>
		<td><label for='hit_end'>Hit End: </label></td>
	 	<td><input type=text name='hit_end' value='$hit_end' size=10> </td></tr>
	 };

foreach (@rank) {
	$zoomForm .=
	  "<input type=checkbox name=rank value=$_ checked style='display:none;'>";
} ## ENDforeach

$zoomForm .= qq{
	<input type=hidden name='hash' value='$hash'>
	<input type=hidden name='query_length' value='$query_length'>
	<input type=hidden name='hit_length' value='$hit_length'>
	<input type=hidden name='query_constant' value='$query_constant'>
	<input type=hidden name='hit_constant' value='$hit_constant'>
	<input type=hidden name='query_name' value='$query'>
	<input type=hidden name='hit_name' value='$hit'>
	<input type=hidden name='filter_evalue' value=''>
	<tr><td>
	<input type=submit value='Zoom'>
	</td>
	</form>
	};

$zoomForm .= qq{
	<form name='reset_form' action='genImage.cgi' method='get'>
	<input type=hidden name='hash' value='$hash'>
	<input type=hidden name="hit_id" value='$hit_id' />
	<input type=hidden name='query_start' value='1'>
	<input type=hidden name='query_end' value='$query_constant'>
	<input type=hidden name='query_constant' value='$query_constant'>
	<input type=hidden name='hit_start' value='1'>
	<input type=hidden name='hit_end' value='$hit_constant'>
	<input type=hidden name='hit_constant' value='$hit_constant'>
	<input type=hidden name='query_name' value='$query'>
	<input type=hidden name='hit_name' value='$hit'>
	<input type=hidden name='filter_evalue' value=''>
	};

foreach (@rank) {
        $zoomForm .="<input type=checkbox name=rank value=$_ checked style='display:none;'>";
} ## ENDforeach

$zoomForm .= qq{
	<td></td><td>
	<input type='submit' value='Reset'>
	</td></tr></table>
	</from></div>
	};


#########################################################
## contents of the HSP select div

my %hsp;
foreach ( $cgi->param('rank') ) {
	$hsp{$_} = 1;
}

my ($location,$controlPanel) =
  showControlPanel( $hit_id, \%hsp, $query_length, $hit_length, $hash, $query_start, $query_end, $hit_start, $hit_end, $query_constant, $hit_constant, $filter_evalue,\@highlight, $query, $hit );

if ($location){
	print $cgi->redirect($location);
	exit 0;

}
else{
#########################################################
## Fill the template

my $banner = HTML::Template->new(
        filename => "templates/banner.tmpl");
my $footer = HTML::Template->new(
        filename => "templates/footer.tmpl");

print $cgi->header;
$template->param( TITLE => "Image" );
$template->param( BANNER => $banner->output );
$template->param( FOOTER => $footer->output );
$template->param( IMAGE        => $content );
$template->param( ZOOM         => $zoomForm );
$template->param( CONTROLPANEL => $controlPanel );
$template->param( HELP         => $help);

#########################################################
## Convert template to output page
print $template->output;
}

sub basefilename {
	my $file = $_[0];

	#--------------------------------------------------------------------------
	#   To upload file from any file system, get the base file name as in php.
	#   The following 2 lines have been taken from File::Util
	#--------------------------------------------------------------------------
	my $DIRSPLIT = qr/[\x5C\/\:]/;
	my $basefilename = pop @{ [ '', split( /$DIRSPLIT/, $file ) ] } || '';
	return $basefilename;
}

## ENDof File
