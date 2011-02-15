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
## Declaration of modules used
use CGI;
use DBI;
use Storable qw(freeze thaw);
use CGI::Carp qw(fatalsToBrowser);
use Data::Dumper;

my $cgi = new CGI;
#------------------------------------------------------
#   Connect to the database
#------------------------------------------------------
_____DATABASE_____
  or die( "unable to connect to the database" . $DBI::errstr );


#############################################################################
## Read parameters
my $hitid=$cgi->param('hit_id');
my $hash=$cgi->param('hash');
my $query_name=$cgi->param('query_name');

## Access database
my $query = qq{ SELECT BOV_hsp.id,BOV_hsp.rank,BOV_hsp.object from BOV_hsp,BOV_hit,BOV_project, BOV_result 
		where BOV_hsp.hit_id = BOV_hit.id
		and BOV_hit.result_id = BOV_result.id
		and BOV_result.project_id = BOV_project.id
		and BOV_hsp.hit_id=? and BOV_project.hash=?};
my $sth = $dbh->prepare($query) or die "error in query".$DBI::errstr;
$sth->execute($hitid,$hash) or die $DBI::errstr or die "error in query".$DBI::errstr;

my $hsp;
my $rank;

## To get the ranks form the database
while(my @ary = $sth->fetchrow_array()){
        $hsp = thaw($ary[2]);
	$rank.='&rank='.$ary[1];
}

## Redirect the page to genImage file.
my $location ='genImage.cgi?filter_evalue=&hash='.$hash.$rank.'&hit_id='.$hitid.'&query_start=0&hit_start=0&query_length='.$hsp->{'QUERY_LENGTH'}.'&query_constant='.$hsp->{'QUERY_LENGTH'}.'&hit_length='.$hsp->{'HIT_LENGTH'}.'&hit_constant='.$hsp->{'HIT_LENGTH'}.'&query_name='.$query_name.'&hit_name='.$hsp->{'HIT_NAME'};
print $cgi->redirect($location);
exit 0;

### EOF ######################################################################
