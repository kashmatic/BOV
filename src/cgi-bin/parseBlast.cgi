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

#########################################################################################
## Declaration of modules used for this program
use strict;
use warnings;
use CGI;
use DBI;
use CGI::Carp qw(fatalsToBrowser);
use Bio::SearchIO;
use Data::Dumper;
use Digest::MD5;
use HTML::Template;
use File::stat;
use Storable qw(freeze thaw);
use IO::Handle;

#########################################################################################
#------------------------------------------------------
#   Connect to the database
#------------------------------------------------------
_____DATABASE_____
	or die("unable to connect to the database" . $DBI::errstr);

$dbh->{AutoCommit} = 0;
#------------------------------------------------
#	Initialize web script headers
#------------------------------------------------
$Storable::forgive_me = 1;
my $cgi = new CGI;
## Read in the user parameters
my ($file_size, $created_on);
my $file  = $cgi->param('uploadfile');
my $email = $cgi->param('email');
my $fh    = $cgi->upload('uploadfile');

if($cgi->param('email')){
	$email = $cgi->param('email');
}else{
	$email = 'dummy@bov.bov';
}

#------------------------------------------------
#	Initialize global variables
#------------------------------------------------
my $hash;
my $blast;
my $project_id;
my $des_email = crypt($email, "_____VARIABLE_____");


#------------------------------------------------
#	Upload the file
#	generate a hash value for it
#	Parse the BLAST output file
#------------------------------------------------
if ($file)
{    ## Check whether the file has been uploaded
	## Upload the file
	my ($hash, $file_size) = upload_file(\$fh);
	if ($hash eq 1)
	{  
		print $cgi->redirect("error.cgi");
		exit;
	}    ## ENDif hash
	my ($count) =
	$dbh->selectrow_array(
	"SELECT count(*) AS count FROM BOV_project WHERE hash='$hash'");
	if ($count)
	{ # If the same file is already uploaded into the system (either by the same or different user)
		my ($count) =
		$dbh->selectrow_array(
		"SELECT count(*) AS count FROM BOV_project WHERE hash='$hash' and email='"
		. $des_email
		. "'");
		if (!$count)
		{ # if the current user hasn't uploaded the previous blast output then send him an email (fake the user that we are using the file submitted by him)
			my $sth_project =
			$dbh->prepare(
			"INSERT INTO BOV_project(id,hash,file_size,created_on,email) VALUES('',?,?,null,?) "
			);
			$sth_project->execute($hash, $file_size, $des_email)
			or die "error in query " . $dbh->errstr;
			send_mail($email, $des_email, $hash);
		}
		my $location =
		'viewhits.cgi?hash='
		. $hash;
		$dbh->commit or die $dbh->errstr if(!$@ and !$dbh->errstr);
		print $cgi->redirect("$location");
		exit 0;
	}    ## ENDif count
	else
	{
		my $sth_project =
		$dbh->prepare(
		"INSERT INTO BOV_project(id,hash,file_size,created_on,email) VALUES('',?,?,null,?) "
		);
		$sth_project->execute($hash, $file_size, $des_email)
		or die "error in query " . $dbh->errstr;
		## Parse the Blast Output file
		parseBlast($hash,$fh)
		;    ## calling subroutine parseblast to parse the blast output
		if (!($@) and !($dbh->errstr))
		{ # If no errors are found, COMMIT the changes to the database and redirect to viewhits.cgi
			$dbh->commit or die $dbh->errstr;
			
			send_mail($email, $des_email, $hash)
			;    # This functions send an email to the specified address
			
			my $location =
			'viewhits.cgi?hash='
			. $hash;
			print $cgi->redirect($location);
			exit 0;
		}    ## ENDif no errors
	}    ## ENDelse count
}    ## ENDif file
$dbh->disconnect;
exit;
## Termination Of the main program ##################################################

#################################
# Subroutine to send an email : using sendmail unix utility
#################################
sub send_mail
{
	my ($email, $des_email, $hash) = @_;
	if($email ne 'dummy@bov.bov'){
		my $sendmail = "_____SENDMAIL_____ -t"; 
		my $from = '_____EMAIL_____';
		my $send_from = "From: 'BOV Team' <".$from.">\n";
		my $to = $email."\n"; 
		my $send_to = "To: ".$to;
		my $subject = "Subject: Bookmark url from BOV tool\n"; 
		my $content = "Dear User,\n\n"
		. "Thank you for using the BOV tool.\n"
		. "Please use the URL link below to access summary of your BLAST output file:\n "
		. "_____URI_____/cgi-bin/BOV/viewhits.cgi?hash=".$hash."\n\n"
		. "Alternatively, You can get the list of all uploaded files till date with reference to this email address.\n"
		. "_____URI_____/cgi-bin/BOV/userPage.cgi?id="
		. $des_email
		. "\n\nRegards,\nBOV team\n\nP.S. This link is valid for _____LIFETIME_____ days from today.	";
		
		if(!open(SENDMAIL, "|$sendmail")){
			diplayErrorPage("<h5>Error</h5> <p class='bodypara'> Error while sending mail </p>");
			last;
		}
		print SENDMAIL $send_from; 
		print SENDMAIL $send_to; 
		print SENDMAIL $subject;
		print SENDMAIL "Content-type: text/plain\n\n"; 
		print SENDMAIL $content; 
		close(SENDMAIL); 
	}
}

########################################################################################
## Subroutine upload_file, called form the main program to upload the file into designated directory
sub upload_file
{
	my ($fhref) = @_;
	my $fh = $$fhref;
	my $size = -s $fh || 0;
	my $buffer;
	
	# read the blast output into a hash and reset pointer into file
	my $hash = Digest::MD5->new->addfile($fh)->hexdigest;
	seek($fh, 0, 0);
	my $count = (<$fh> =~/^T?BLAST/);
	seek($fh, 0, 0);
	if ($count < 1) { return (1, $size); }
	else{   return ($hash,$size);   }
}
## END of subroutine upload_file ######################################################

########################################################################################
## Subroutine parseblast, called form main program to parse the blast file and update the database,

sub diplayErrorPage{
	## Display error webpage  if the upload file is not a BLAST output file
	print $cgi->header, $cgi->title("Error");
	print $cgi->start_html();
	my $content = shift;
	my $template =	HTML::Template->new(filename =>	"templates/main.tmpl");
	my $banner =	HTML::Template->new(filename =>	"templates/banner.tmpl");
	my $footer =	HTML::Template->new(filename =>	"templates/footer.tmpl");
	$template -> param (CONTENT => $content);
	$template -> param (BANNER => $banner->output);
	$template -> param (FOOTER => $footer->output);

	print $template->output;
	print $cgi->end_html();
	exit;
}

sub parseBlast
{
	my ($hash,$fh) = @_;
	push @Fh::ISA, 'IO::Handle' unless Fh->isa('IO::Handle');
	
	my $in = Bio::SearchIO->new(-fh => $fh, -format => "blast")
	or die "not a valid format";
	my ($query_name, $hit_name, $hit_length, $query_length);
	my $sth_result =
	$dbh->prepare(
	"INSERT INTO BOV_result(id,project_id,query_name,query_description) VALUES ('',?,?,?)"
	);
	my $sth_hit =
	$dbh->prepare(
	"INSERT INTO BOV_hit(id,result_id,hit_name,query_length,hit_length,score,evalue) VALUES ('',?,?,?,?,?,?)"
	);
	my $sth_hsp =
	$dbh->prepare(
	"INSERT INTO BOV_hsp(id,hit_id,rank,object) VALUES ('',?,?,?)");
	my $statement = "SELECT id FROM BOV_project where hash = '$hash'";
	my ($project_id) = $dbh->selectrow_array($statement);
	
	while ($blast = $in->next_result())
	{
		$sth_result->execute($project_id, $blast->{_queryname},
		$blast->{_querydesc})
		or die $sth_result->errstr;
		my $result_id = $dbh->last_insert_id(undef, undef, 'BOV_result', 'id');
		foreach my $hit ($blast->hits)
		{
			
			$sth_hit->execute(
			$result_id,
			$hit->{'_name'},
			$hit->{'_query_length'},
			$hit->length(),
			$hit->bits(),
			$hit->{'_significance'}
			)
			or die $sth_hit->errstr;
			my $hit_id = $dbh->last_insert_id(undef, undef, 'BOV_hit', 'id');
			
			while (my $hsp = $hit->next_hsp())
			{
				foreach (keys %$hsp){	
					# Remove CODE items from the hsp object - These create errors for storing using Storable module
					delete $hsp->{$_} if($_=~/^_/);
				}
				
				my $freezed_hsp = freeze($hsp) or die $@;
				$sth_hsp->execute($hit_id, $hsp->{'RANK'}, $freezed_hsp)
				or die $sth_hsp->errstr;
			}    ## ENDwhile
		}    ## ENDforeach
	}    ## ENDforeach
}    ## ENDsubroutine

# EOF ###########################################################################################

