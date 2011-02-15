package BOVM;
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


########################################################################
## Modules required
use Data::Dumper;
use DBI;
use CGI;
use strict;
use GD;
use Bio::Search::HSP::GenericHSP;
use Bio::SimpleAlign;
use Storable qw(freeze thaw);
use CGI::Carp qw(fatalsToBrowser);
use POSIX qw(floor ceil);
use Math::Round;

BEGIN
{
	use Exporter ();
	our @ISA       = qw(Exporter);
	our @EXPORT_OK =
	  qw(demo drawhsp drawImage showControlPanel genTemplate);
}
use Storable qw(freeze thaw);
use POSIX qw(floor);

#------------------------------------------------------
#   Connect to the database
#------------------------------------------------------
_____DATABASE_____
  or die("unable to connect to the database" . $DBI::errstr);

#------------------------------------------------------
#	Global variables
#------------------------------------------------------
my $cgi   = new CGI;

#------------------------------------------------------
#   Functions with in the module
#------------------------------------------------------

##########################################################################
## Subroutine 'showControlPanel' - this subroutine is used to display the contents of the
## HSP Select tab. This subroutine is called from genImage.cgi
sub showControlPanel
{

	## Get all the parameters
	my ($hit_id) = $_[0];
	my %hsp = %{$_[1]};
	my (
		$query_length, $hit_length,     $hash,
		$query_start,  $query_end,      $hit_start,
		$hit_end,      $query_constant, $hit_constant,
		$highlightref, $query_name,		$hit_name
	   )
	  = ($_[2], $_[3], $_[4], $_[5], $_[6], $_[7], $_[8], $_[9], $_[10],$_[12],$_[13],$_[14]);

	my @highlight = ($highlightref) ? @{$highlightref} : undef;
	
	## Get the filter_evalue
	my $filter_evalue =
	  defined($cgi->param('filter_evalue')) ? $cgi->param('filter_evalue') : -1;

	if ($filter_evalue eq 0){ $filter_evalue = "0.0" };

	## Connect to Database and execute query
	_____DATABASE_____
	  or die("unable to connect to the database" . $DBI::errstr);
	my $result = "";
	my $query  = "SELECT rank,object from BOV_hsp where hit_id = ?";
	my $sth    = $dbh->prepare($query);
	$sth->execute($hit_id);

	## Content to displayed in this tab
	my $controlPanel = "";
	$controlPanel = qq{
	<!-- <div id='controlPanel'> -->
	<h3> High-Scoring Pair (HSP) View </h3>
   	<form name='hspform' action='genImage.cgi' method='get'>
	filter by E-value: <input type='text' name='filter_evalue' value='' />
	<input type="submit" value="Filter" /><br /><br />
	<input type="submit" value='Refresh the Image'/><br /><br />
   	<table class=\"tab\" width='100%' id=\"list\" >
   	<thead class='tab'>
   		<th  class='tab' width=\"30\" rowspan=\"2\">CheckAll</th> 
		<th  class='tab' width=\"30\" valign=\"top\" rowspan=\"2\"> Highlight</th>
		<th  class='tab' width=\"30\" valign=\"top\" rowspan=\"2\"> Alignment </th>
		<th  class='tab' width=\"30\" valign=\"top\" rowspan=\"2\"> E-Value </th> 
		<th  class='tab' width=\"30\" colspan=\"2\"> Query</th> 
		<th  class='tab' width=\"30\" colspan=\"2\"> Hit</th>
	</thead>
	<thead class='tab'>
		<th class='tab'><input type='checkbox' name='all' onClick='checkAll(document.hspform.rank,this)'></th>
		<th class='tab'></th>
		<th class='tab'></th>
		<th class='tab'></th>
		<th  class='tab' width=\"30\"> Start </th>
		<th  class='tab' width=\"30\"> End </th>
		<th  class='tab' width=\"30\"> Start </th>
		<th  class='tab' width=\"30\"> End </th>
	</thead>
   	};
	foreach (@highlight){
		$controlPanel	.= "<input type=hidden name='highlight' value='$_'/>";
	}
	my @filter_rank;

	## Display search results
	while (my @data = $sth->fetchrow_array())
	{
		my ($rank, $object) = @data;
		my $obj    = thaw($data[1]);
		my $evalue = $obj->{'EVALUE'};
		$evalue = defined($evalue) ? $evalue : '';
		$rank = (defined($rank) and ($rank)) ? $rank : 0;
		my $request_uri = $ENV{'REQUEST_URI'};
		$request_uri =~ s/&{2,}/&/g;
		my $link;
			$link        =
		  ($request_uri =~ s/(highlight\=)$rank//e)
		  ? "<a id='imgID' href=$request_uri> On </a>" 
		  : qq{<a id='imgID' href=$request_uri&highlight=$rank> Off </a> };
		if(($filter_evalue>=$evalue) and ($filter_evalue))
		{
			$controlPanel .=
			"<tr> <td class='tab'   align='center'> <input type='checkbox' name='rank' value=$rank checked onclick='this.form.submit();'/> </td>";
			push(@filter_rank,$rank);
		}
		elsif(($hsp{$data[0]})and(!$filter_evalue))
		{
			$controlPanel .=
			"<tr> <td class='tab'   align='center'> <input type='checkbox' name='rank' value=$rank checked onclick='this.form.submit();'/> </td>";
		}
		elsif(((!$hsp{$data[0]}) and (!$filter_evalue))or $filter_evalue)
		{
			$controlPanel .=
			"<tr> <td class='tab'   align='center'> <input type='checkbox' name='rank' value=$rank onclick='this.form.submit();'/> </td>";
		}

		my $hitseq    = $obj->{'HIT_SEQ'};
		my $queryseq  = $obj->{'QUERY_SEQ'};
		my $a="great";
		
		## Contents to be displayed when cicked on view alignment
		my $alignment = "<pre>"
		  . "Score\t= "
		  . $obj->{'BITS'}
		  . " bits ("
		  . $obj->{'SCORE'}
		  . ")<br/>"
		  . "E-Value\t= "
		  . $obj->{'EVALUE'} . "<br/>"
		  . "Identities\t= "
		  . $obj->{'IDENTICAL'} . "/"
		  . $obj->{'HSP_LENGTH'} . "  ("
		  . floor(($obj->{'IDENTICAL'} / $obj->{'HSP_LENGTH'}) * 100)
		  . "%)<br />";
		
		if ($obj->{'CONSERVED'})
		{
			$alignment .=
			    "Positives\t= "
			  . $obj->{'CONSERVED'} . "/"
			  . $obj->{'HSP_LENGTH'} . "  ("
			  . floor(($obj->{'CONSERVED'} / $obj->{'HSP_LENGTH'}) * 100)
			  . "%)<br />";
		}
		if ($obj->{'QUERY_FRAME'})
		{
			$alignment .= "Frame\t= " . $obj->{'QUERY_FRAME'} . "<br />";
		}
		if ($obj->{'HSP_GAPS'})
		{
			$alignment .= "Gaps\t= "
			  . $obj->{'HSP_GAPS'} . "/"
			  . $obj->{'HSP_LENGTH'} . "  ("
			  . floor(($obj->{'HSP_GAPS'} / $obj->{'HSP_LENGTH'}) * 100)
			  . "%)<br />";
		}
		$alignment .= "Strand\t=";
		$alignment .=
		  ($obj->{'QUERY_START'} < $obj->{'QUERY_END'})
		  ? " Plus /"
		  : " Minus /";
		$alignment .=
		  ($obj->{'HIT_START'} < $obj->{'HIT_END'})
		  ? " Plus<br />"
		  : " Minus<br />";
		$alignment .= "<br />";
		
		my $w    = 0;
		my $qs   = $obj->{'QUERY_START'};
		my $qe   = $obj->{'QUERY_END'};
		my $hs   = $obj->{'HIT_START'};
		my $he   = $obj->{'HIT_END'};
		my $x    = $obj->{'HSP_LENGTH'};
		my $tab;

		if (
		($qs>99999) or
		($qe>99999) or
		($hs>99999) or
		($he>99999))
		{
			$tab = "\t\t";
		}
		else
		{
			$tab = "\t";
		}
		my $htab=$tab;
		my $qtab=$tab;
		
		while ($x >= 0)
		{
			if ($hs>99999){$htab="\t"};
			if ($qs>99999){$qtab="\t"};
			my $q_end = $x < 60 ? $qs + $x - 1 : $qs + 60 - 1;
			my $h_end =
			  $x < 60
			  ? ($he > $hs) ? $hs + $x - 1 : $hs - $x + 1
			  : ($he > $hs)
			  ? $hs + 60 - 1
			  : $hs - 60 + 1;
			my $qdash = (substr($queryseq, $w, 60) =~ tr/-//);
			$q_end -= $qdash;
			my $hdash = (substr($hitseq, $w, 60) =~ tr/-//);
			$h_end = ($he > $hs) ? $h_end - $hdash : $h_end + $hdash;
			$alignment .=
			    "Query   : " . $qs . $qtab
			  . substr($queryseq, $w, 60) . "\t"
			  . $q_end . "<br/>" . "\t"
			  . $tab
			  . substr($obj->{'HOMOLOGY_SEQ'}, $w, 60) . "<br/>"
			  . "Sbjct   : "
			  . $hs
			  . $htab
			  . substr($hitseq, $w, 60) . "\t"
			  . $h_end
			  . "<br/><br/>";
			$x -= 60;
			$w += 60;
			$qs = $q_end + 1;
			$hs = ($he > $hs) ? $h_end + 1 : $h_end - 1;
		}    ##ENDwhile
		
		$alignment .= "</pre>";
		
		$hitseq   =~ s/[\n\s-]//g;
		$queryseq =~ s/[\n\s-]//g;
		my @hitseq   = split(/(\w{50})/, $hitseq);
		my @queryseq = split(/(\w{50})/, $queryseq);
		$hitseq = join "#", @hitseq;
		$hitseq =~ s/#{1,2}\E/\<br\/\>/g;
		$queryseq = join "#", @queryseq;
		$queryseq =~ s/#{1,2}\E/\<br\/\>/g;
		$queryseq = "<pre>" . ">Query sequence segment in the alignment." . $queryseq . "</pre>";
		$hitseq   = "<pre>" . ">Hit sequence segment in the alignment." . $hitseq . "</pre>";
		my $url = "#seq";

		## Display the contents of the table in the HSP tab
		$controlPanel .=
			"<td class='tab' > $link </td>"
		  . "<td class='tab'> <a href='#' onClick='displayText(\"$alignment\",\"$queryseq\",\"$hitseq\")'> View </a> </td>"
		  . "<td  class='tab' > $evalue </td>"
		  . "<td class='tab'> $obj->{'QUERY_START'} </td>"
		  . "<td class='tab' > $obj->{'QUERY_END'}</td>"
		  . "<td class='tab' > $obj->{'HIT_START'} </td>"
		  . "<td class='tab'  >$obj->{'HIT_END'} </td> </tr>";
	}    ## ENDwhile

	$controlPanel .= "</table><br />";
	$controlPanel .=
	    "<input type=hidden name='hit_id' value='$hit_id'>"
	  . "<input type=hidden name='hash' value='$hash'>"
	  . "<input type=hidden name='query_start' value='$query_start'>"
	  . "<input type=hidden name='query_end' value='$query_end'>"
	  . "<input type=hidden name='query_length' value='$query_length'>"
	  . "<input type=hidden name='hit_start' value='$hit_start'>"
	  . "<input type=hidden name='hit_end' value='$hit_end'>"
	  . "<input type=hidden name='hit_length' value='$hit_length'>"
	  . "<input type=hidden name='query_constant' value='$query_constant'>"
	  . "<input type=hidden name='hit_constant' value='$hit_constant'>"
	  . "<input type=hidden name='query_name' value='$query_name'>"
	  . "<input type=hidden name='hit_name' value='$hit_name'>";
	$controlPanel .="<input type=submit value='Refresh the Image'/>";
	$controlPanel .= "</form>";
	$sth->finish();
	$dbh->disconnect();
	my $location;
	if(@filter_rank){
		my $ranks;
		foreach my $ranking(@filter_rank){
			$ranks.="&rank=".$ranking;
		}
		$location="_____URI_____/cgi-bin/BOV/genImage.cgi?filter_evalue=&hit_id=$hit_id&hash=$hash"
			."&query_start=$query_start&query_end=$query_end"
			."&query_length=$query_length&hit_start=$hit_start&hit_end=$hit_end&hit_length=$hit_length"
			."&query_constant=$query_constant&hit_constant=$hit_constant&query_name=$query_name&hit_name=$hit_name"
			."$ranks";
#		print $cgi->redirect($location);
	}
	return ($location,$controlPanel);
}
## ENDsubroutine showControlPanel

#############################################################################
## Subroutine drawhsp - called from drawimage, to draw polygons
sub drawhsp
{
	
	my (
		$query_length, $hit_length,  $rank,      $hash,      $im,
		$highlightref,    $query_start, $query_end, $hit_start, $hit_end,
		$colorref
	   )
	  = @_;
	my @highlight = @{$highlightref};
	my %highlightHash = map { $_ => $_ } @highlight;
	
	my @colors = @{$colorref};
	
	# allocate some colors
	my $white = $im->colorAllocate(255, 255, 255);

	#------------------------------------------------------
	#   Set the global paramaters for the image
	#------------------------------------------------------
	my $width        = 700;
	my $height       = 400;
	my $left         = 0;
	my $right        = $width;
	my $top          = 0;
	my $bottom       = $height;
	my $padding_top  = 25;
	my $padding_side = 30;
	my $scale_height = 20;
	my $ileft        = $left + $padding_side;
	my $iright       = $right - $padding_side;
	my $itop         = $top + $padding_top + 1;
	my $ibottom      = $bottom - $padding_top;

	#	Coordinates on the four sides
	my $iqx_topleft     = $left + $padding_side;
	my $iqy_topleft     = $top + $padding_top;
	my $iqx_topright    = $right - $padding_side;
	my $iqy_topright    = $top + $padding_top;
	my $ihx_bottomleft  = $left + $padding_side;
	my $ihy_bottomleft  = $bottom - $padding_top;
	my $ihx_bottomright = $right - $padding_side;
	my $ihy_bottomright = $bottom - $padding_top;
	my $iwidth = $width - 2 * $padding_side;    #width of the query/hit bar
	my $qscale = $query_length / $iwidth;
	my $hscale = $hit_length / $iwidth;
	my $scale_noof_divisions   = 10;
	my $pixels_per_division    = $iwidth / $scale_noof_divisions;
	my $qresidues_per_division = $query_length / $iwidth;
	my $hresidues_per_division = $hit_length / $iwidth;

	my $colorCount = 0;
	$colorCount = ($rank < 30) ? $rank : $rank % 30;

	my $query = "SELECT object from BOV_hsp, BOV_hit, BOV_result, BOV_project
		WHERE BOV_hsp.rank = $rank 
		and BOV_hsp.hit_id = BOV_hit.id
		and BOV_hit.result_id = BOV_result.id
		and BOV_result.project_id = BOV_project.id
		and BOV_hsp.hit_id= '" . $cgi->param('hit_id') . "'
		and BOV_project.hash = 
		'" . $hash . "'";
	my ($hsp) = thaw($dbh->selectrow_array($query));

	#	print Dumper $hsp;
	my $hsp_qstart = $hsp->{'QUERY_START'};
	my $hsp_qend   = $hsp->{'QUERY_END'};
	my $hsp_hstart = $hsp->{'HIT_START'};
	my $hsp_hend   = $hsp->{'HIT_END'};
	my $hsp_rank   = $hsp->{'RANK'};

	#	print "qstart : $query_start, qend : $query_end\n hstart : $hit_start, hend : $hit_end\n";
	if ($query_start)
	{
		$qscale = ($query_end - $query_start) / $iwidth;
	}
	if ($hit_start)
	{
		$hscale = ($hit_end - $hit_start) / $iwidth;
	}
	$im->string(gdSmallFont,
				$iqx_topleft + 10,  
				$iqy_topleft + 3,  ## originally 5
				"Query : "
				  . $hsp->{'QUERY_NAME'}
				  . "     (total length - "
				  . $hsp->{'QUERY_LENGTH'} . ")",
				$white
			   );
	$im->string(gdSmallFont,
				$ihx_bottomleft + 10,
				$ihy_bottomleft - 17, ## originally 20
				"Hit : "
				  . $hsp->{'HIT_NAME'}
				  . "     (total length - "
				  . $hsp->{'HIT_LENGTH'} . ")",
				$white
			   );

	#draw polygons for each hsp
	my $poly = new GD::Polygon;
	my ($x1, $x2, $x3, $x4, $y1, $y2, $y3, $y4);
	$im->setThickness(2);
	
	if(exists $highlightHash{$rank})
	{
		if (!$query_start and !$query_end)
		{
			$poly->addPt($padding_side + $hsp_qstart / $qscale,
						 $itop + $scale_height + 1);
			$poly->addPt($padding_side + $hsp_qend / $qscale,
						 $itop + $scale_height + 1);
			$poly->addPt($hsp_hend / $hscale + $padding_side,
						 $ibottom - $scale_height - 1);
			$poly->addPt($hsp_hstart / $hscale + $padding_side,
						 $ibottom - $scale_height - 1);
#			$im->filledPolygon($poly, $colors[35]);
			$im->filledPolygon($poly, $colors[$colorCount]);
			$im->line(
					  $padding_side + $hsp_qstart / $qscale,
					  $itop + $scale_height,
					  $hsp_hstart / $hscale + $padding_side,
					  $ibottom - $scale_height - 1,
#					  $colors[35]
					  $colors[$colorCount]
					 );
			$im->line(
					  $padding_side + $hsp_qend / $qscale,
					  $itop + $scale_height,
					  $hsp_hend / $hscale + $padding_side,
					  $ibottom - $scale_height,
#					  $colors[35]
					  $colors[$colorCount]
					 );
			$x1 = $padding_side + $hsp_qstart / $qscale;
			$y1 = $itop + $scale_height;
			$x2 = $padding_side + $hsp_qend / $qscale;
			$y2 = $itop + $scale_height;
			$x3 = $hsp_hend / $hscale + $padding_side;
			$y3 = $ibottom - $scale_height;
			$x4 = $hsp_hstart / $hscale + $padding_side;
			$y4 = $ibottom - $scale_height;
		}    ## ENDif
		else
		{
			$poly->addPt($padding_side + ($hsp_qstart - $query_start) / $qscale,
						 $itop + $scale_height + 1);
			$poly->addPt($padding_side + ($hsp_qend - $query_start) / $qscale,
						 $itop + $scale_height + 1);
			$poly->addPt(($hsp_hend - $hit_start) / $hscale + $padding_side,
						 $ibottom - $scale_height - 1);
			$poly->addPt(($hsp_hstart - $hit_start) / $hscale + $padding_side,
						 $ibottom - $scale_height - 1);
		#	$im->filledPolygon($poly, $colors[35]);
			$im->filledPolygon($poly, $colors[$colorCount]);
			$im->line(
					  $padding_side + ($hsp_qstart - $query_start) / $qscale,
					  $itop + $scale_height,
					  ($hsp_hstart - $hit_start) / $hscale + $padding_side,
					  $ibottom - $scale_height - 1,
					#  $colors[35]
					  $colors[$colorCount]
					 );
			$im->line(
					  $padding_side + ($hsp_qend - $query_start) / $qscale,
					  $itop + $scale_height,
					  ($hsp_hend - $hit_start) / $hscale + $padding_side,
					  $ibottom - $scale_height - 1,
					#  $colors[35]
					  $colors[$colorCount]
					 );
			$x1 = $padding_side + ($hsp_qstart - $query_start) / $qscale;
			$y1 = $itop + $scale_height;
			$x2 = $padding_side + ($hsp_qend - $query_start) / $qscale;
			$y2 = $itop + $scale_height;
			$x3 = ($hsp_hend - $hit_start) / $hscale + $padding_side;
			$y3 = $ibottom - $scale_height;
			$x4 = ($hsp_hstart - $hit_start) / $hscale + $padding_side;
			$y4 = $ibottom - $scale_height;
		}    ## ENDelse
	}    ## ENDif
	else
	{
		my $red = $im->colorAllocate(255,0,0); 
		#		print "color count: $colorCount rank: $rank color value: ";
		#		print Dumper $colors[$colorCount]."<br>";
		#	$im->filledPolygon( $poly, $colors[ int(rand($range) ] );
		if (!$query_start and !$query_end)
		{
		
			#			print "qscale: $qscale , hscale: $hscale\n";
			$im->line(
					  $padding_side + $hsp_qstart / $qscale,
					  $itop + $scale_height,
					  $hsp_hstart / $hscale + $padding_side,
					  $ibottom - $scale_height - 1,
					  $colors[$colorCount]
					 );
			$im->line(
					  $padding_side + $hsp_qend / $qscale,
					  $itop + $scale_height,
					  $hsp_hend / $hscale + $padding_side,
					  $ibottom - $scale_height - 1,
					  $colors[$colorCount]
					 );
			$x1 = $padding_side + ($hsp_qstart / $qscale);
			$y1 = $itop + $scale_height;
			$x2 = $padding_side + ($hsp_qend / $qscale);
			$y2 = $itop + $scale_height;
			$x3 = ($hsp_hend / $hscale) + $padding_side;
			$y3 = $ibottom - $scale_height;
			$x4 = ($hsp_hstart / $hscale) + $padding_side;
			$y4 = $ibottom - $scale_height;

			#			print "<h2><br /><br /><br /><br /><br />hsp-qstart-$hsp_hstart, hsp_qend-$hsp_hend</h2";
		}    ## ENDif
		else
		{
		
			#			print "qscale = $qscale,hscale=$hscale, query_length= $query_length,query_start = ".($cgi->param('query_start'))."\n";
			$im->line(
					  $padding_side + ($hsp_qstart - $query_start) / $qscale,
					  $itop + $scale_height,
					  ($hsp_hstart - $hit_start) / $hscale + $padding_side,
					  $ibottom - $scale_height - 1,
					  $colors[$colorCount]
					 );
			$im->line(
					  $padding_side + ($hsp_qend - $query_start) / $qscale,
					  $itop + $scale_height,
					  ($hsp_hend - $hit_start) / $hscale + $padding_side,
					  $ibottom - $scale_height - 1,
					  $colors[$colorCount]
					 );
			$x1 = $padding_side + ($hsp_qstart - $query_start) / $qscale;
			$y1 = $itop + $scale_height;
			$x2 = $padding_side + ($hsp_qend - $query_start) / $qscale;
			$y2 = $itop + $scale_height;
			$x3 = ($hsp_hend - $hit_start) / $hscale + $padding_side;
			$y3 = $ibottom - $scale_height;
			$x4 = ($hsp_hstart - $hit_start) / $hscale + $padding_side;
			$y4 = $ibottom - $scale_height;
		}    ## ENDelse
	}    ## ENDelse
}
## END of subroutine drawhsp

###########################################################################################
## subroutine gentemplate, called from drawimage.
sub genTemplate
{
	my ($query_length, $hit_length, $query_start, $hit_start, $hash) = @_;

	#------------------------------------------------------
	#   Set the global paramaters for the image
	#------------------------------------------------------
	my $width        = 700;
	my $height       = 400;
	my $left         = 0;
	my $right        = $width;
	my $top          = 0;
	my $bottom       = $height;
	my $padding_top  = 25;
	my $padding_side = 30;
	my $scale_height = 20;
	my $ileft        = $left + $padding_side;
	my $iright       = $right - $padding_side;
	my $itop         = $top + $padding_top;
	my $ibottom      = $bottom - $padding_top;
	## Coordinates on the four sides
	my $iqx_topleft     = $left + $padding_side;
	my $iqy_topleft     = $top + $padding_top;
	my $iqx_topright    = $right - $padding_side;
	my $iqy_topright    = $top + $padding_top;
	my $ihx_bottomleft  = $left + $padding_side;
	my $ihy_bottomleft  = $bottom - $padding_top;
	my $ihx_bottomright = $right - $padding_side;
	my $ihy_bottomright = $bottom - $padding_top;
	my $iwidth = $width - 2 * $padding_side;    #width of the query/hit bar
	my $qscale = $query_length / $iwidth;
	my $hscale = $hit_length / $iwidth;
	my $scale_noof_divisions   = 10;
	my $pixels_per_division    = $iwidth / $scale_noof_divisions;
	my $qresidues_per_division = $query_length / $iwidth;
	my $hresidues_per_division = $hit_length / $iwidth;

	# create a new image
	my $im = new GD::Image($width, $height);

	# allocate some colors
	my $white = $im->colorAllocate(255, 255, 255);
	my $black = $im->colorAllocate(0,   0,   0);
	my $blue  = $im->colorAllocate(0,   0,   255);

	# make the background transparent and interlaced
	$im->transparent($white);
	$im->interlaced('true');

	# Put a black frame around the picture
	#$im->rectangle(0,0,$width,$height,$black);

	# draw the scale bars for both the query and hit
	$im->filledRectangle($iqx_topleft, $iqy_topleft, $iqx_topright,
						 $iqy_topright + $scale_height, $black);
	$im->filledRectangle($ihx_bottomleft, $ihy_bottomleft - $scale_height,
						 $ihx_bottomright, $ihy_bottomright, $black);
	my $imagemap = "";

	# draw scale
	for (my $i = $iqx_topleft ;
		 $i <= $iqx_topright ; $i += $pixels_per_division)
	{
		my $val;
		$val = floor(($i - $padding_side) * $qscale) + $query_start;
		if ($query_start + $query_length - $val <= 1)
		{
			$val = $query_start + $query_length;
		}
		if (!$val or $val == 0) { $val = 1; }
		$im->string(gdSmallFont, $i - 5, $itop - 20, $val, $black);
		$im->line($i,$itop,$i,$itop-5,$black);
	}    ## ENDfor
	for (my $i = $ihx_bottomleft ;
		 $i <= $ihx_bottomright ;
		 $i += $pixels_per_division)
	{
		my $val = floor(($i - $padding_side) * $hscale) + $hit_start;
		if (!$val or $val == 0) { $val = 1; }
		$im->string(gdSmallFont, $i - 5, $ibottom + 7, $val, $black);
		$im->line($i,$ibottom,$i,$ibottom+5,$black);
	}    ## ENDfor
	return $im;
}
## END of subroutine gentemplate 

1;

## ENDof File

