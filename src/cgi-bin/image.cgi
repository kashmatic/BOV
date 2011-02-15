#! /usr/bin/perl 
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

use CGI;
use GD;

my $cgi = new CGI;

use lib qw(BOVModules);
use BOVM qw( drawhsp genTemplate );

_____DATABASE_____
  or die("unable to connect to the database" . $DBI::errstr);

print "Content-type: image/png\n\n";

my $hit_id = $cgi->param('hit_id');
my $query_length = $cgi->param('query_length');
my $hit_length = $cgi->param('hit_length');
my $query_start = $cgi->param('query_start');
my $query_end = $cgi->param('query_end');
my $hit_start = $cgi->param('hit_start');
my $hit_end = $cgi->param('hit_end');
my @highlight = $cgi->param('highlight');
my @rank      = $cgi->param('rank');
my $hash = $cgi->param( 'hash' );

my $im = 
 genTemplate($query_length, $hit_length, $query_start, $hit_start, $hash);

my @colors;
$colors[0]  = $im->colorAllocate(138, 43,  226);    ## Blue purple
$colors[1]  = $im->colorAllocate(165, 42,  42);     ## Brown
$colors[2]  = $im->colorAllocate(237, 164, 61);     ## Crimson
$colors[3]  = $im->colorAllocate(0,   0,   139);    ## Dark Blue
$colors[4]  = $im->colorAllocate(0,   139, 139);    ## DarkCyan
$colors[5]  = $im->colorAllocate(0,   100, 0);      ## DarkGreen
$colors[6]  = $im->colorAllocate(139, 0,   139);    ## DarkMagenta
$colors[7]  = $im->colorAllocate(85,  107, 47);     ## DarkOliveGreen
$colors[8]  = $im->colorAllocate(153, 50,  204);    ## DarkOrchid
$colors[9]  = $im->colorAllocate(139, 0,   0);      ## DarkRed
$colors[10] = $im->colorAllocate(72,  61,  139);    ## DarkSlateBlue
$colors[11] = $im->colorAllocate(47,  79,  79);     ## DarkSlateGray
$colors[12] = $im->colorAllocate(148, 0,   211);    ## DarkViolet
$colors[13] = $im->colorAllocate(255, 20,  147);    ## DeepPink
$colors[14] = $im->colorAllocate(105, 105, 105);    ## DimGray
$colors[15] = $im->colorAllocate(30,  144, 255);    ## DodgerBlue
$colors[16] = $im->colorAllocate(178, 34,  34);     ## FireBrick
$colors[17] = $im->colorAllocate(34,  139, 34);     ## ForestGreen
$colors[18] = $im->colorAllocate(255, 0,   255);    ## Fuchsia
$colors[19] = $im->colorAllocate(0,   128, 0);      ##Green
$colors[20] = $im->colorAllocate(205, 92,  92);     ##IndianRed
$colors[21] = $im->colorAllocate(75,  0,   130);    ##Indigo
$colors[22] = $im->colorAllocate(128, 0,   0);      ##Maroon
$colors[23] = $im->colorAllocate(0,   0,   205);    ##MediumBlue
$colors[24] = $im->colorAllocate(199, 21,  133);    ##MediumVioletRed
$colors[25] = $im->colorAllocate(25,  25,  112);    ##MidnightBlue
$colors[26] = $im->colorAllocate(0,   0,   128);    ##Navy
$colors[27] = $im->colorAllocate(255, 69,  0);      ##OrangeRed
$colors[28] = $im->colorAllocate(128, 0,   128);    ##Purple
$colors[29] = $im->colorAllocate(65,  105, 225);    ##RoyalBlue
$colors[30] = $im->colorAllocate(139, 69,  19);     ##SaddleBrown
$colors[31] = $im->colorAllocate(46,  139, 87);     ##SeaGreen
$colors[32] = $im->colorAllocate(160, 82,  45);     ##Sienna
$colors[33] = $im->colorAllocate(106, 90,  205);    ##SlateBlue
$colors[34] = $im->colorAllocate(0,   128, 128);    ##Teal
$colors[35] = $im->colorAllocate(238, 213, 210);    ## Pink

my $i = 0;
my %rankHash;
$rankHash{$_} = $i++ for @rank;

foreach my $rank (@rank) {
  my $query =
    "SELECT object from BOV_hsp, BOV_hit, BOV_result, BOV_project
                        WHERE BOV_hsp.rank = $rank
                        and BOV_hit.id = $hit_id
                        and BOV_hsp.hit_id = BOV_hit.id
                        and BOV_hit.result_id = BOV_result.id
                        and BOV_result.project_id = BOV_project.id
                        and BOV_project.hash = 
                        '" . $cgi->param('hash') . "'";
  my ($hsp) = $dbh->selectrow_array($query);
  drawhsp($query_length, $hit_length, $rank, $hash,
          $im, \@highlight, $query_start, $query_end,
          $hit_start, $hit_end, \@colors
         );
}

print $im->png;
