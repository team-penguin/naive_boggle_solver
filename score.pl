#!/usr/bin/perl
use strict;
use warnings;
use Data::Dumper;
$Data::Dumper::Indent = 1;
$Data::Dumper::Sortkeys = 1;

# my $argc = $#ARGV + 1;
# if ($argc == 0) {
# 	exit(127);
# }

my $boggle_file = './cubes.txt';
my $word_file = './words.txt';
# my ($boggle_file, $word_file) = @ARGV;

if ( ! -e $boggle_file ) {
	die "Error: Could not read the cubes file\n";
}
if ( ! defined $word_file ) {
	exit(127);
}

my @words;
open my $dictionary, '<', $word_file or die "Error: Could not open $ARGV[1].\n";
while (my $word = <$dictionary>) {
	if ( lc($word) =~ /^[a-z]+$/ ) {
		push @words, lc($word);
	}
}
my @valid_words = uniq(@words);
chomp @valid_words;

sub uniq {
	my %seen;
	grep !$seen{$_}++, @_;
}

## Move the longest words to the top of the list.
## If solved, this is a cheap way to seed the word cache.
## UPDATE:
## My word cache idea needs some work, slows things down by 4 seconds on the 1st board.
## Commented word cache stuff for now.
my @sorted = sort { length($b) <=> length($a) } @valid_words;

## https://github.com/bdrupieski/BoggleSolver/blob/master/BoggleSolver/BoggleSolver.cs
## x,y,z representation of neighboring cubies (voxels)
my @voxel_neighbors = ( '-1,-1,-1','0,-1,-1','1,-1,-1',
 			'-1, 0,-1','0, 0,-1','1, 0,-1',
 			'-1, 1,-1','0, 1,-1','1, 1,-1',
 			'-1,-1, 0','0,-1, 0','1,-1, 0',
 			'-1, 0, 0',          '1, 0, 0',
 			'-1, 1, 0','0, 1, 0','1, 1, 0',
 			'-1,-1, 1','0,-1, 1','1,-1, 1',
 			'-1, 0, 1','0, 0, 1','1, 0, 1',
 			'-1, 1, 1','0, 1, 1','1, 1, 1' );

sub find_neighbors {
	my $cube_ref = $_[0];
	# print Dumper($cube_ref);
	my $voxel_ref = $_[1];
	my @voxel = split(/,/,${$voxel_ref});
	my @neighbors;
	my @neighbor;
	my @voxel_neighbor;
	foreach my $voxel_transform (@voxel_neighbors) {
		@neighbor = split(/,/, $voxel_transform);
		@voxel_neighbor =  map { $voxel[$_] + $neighbor[$_] } 0..2;
		push @neighbors, join(',', @voxel_neighbor);
	}
	my @neighboring_letters;
	foreach (@neighbors) {
		push @neighboring_letters, ${$cube_ref}{$_};
	}
	my %neighboring_cubies;
	## Assign letters to the neighboring cubies, even if the assignment is undefined.
	@neighboring_cubies{@neighbors} = @neighboring_letters;
	# print Dumper(\%neighboring_cubies);
	## Reconcile the neighborhood to valid cubies.
	foreach (keys %neighboring_cubies) {
		if ( ! defined $neighboring_cubies{$_} ) {
			delete $neighboring_cubies{$_};
		}
	}
	# print Dumper(\%neighboring_cubies);
	return %neighboring_cubies;
}

sub arr2word {
	my %cube_ref = %{$_[0]};
	my $arr_ref = $_[1];
	my $word;
	foreach (@{$arr_ref}) {
		$word .= $cube_ref{$_};
	}
	return $word;
}

sub find_voxels {
	my %cube_ref = %{$_[0]};
	my $word_ref = $_[1];
	my $index_ref = $_[2];
	my $valid_word_ref = $_[3];
	my $voxel_ref = $_[4];
	my $walkabout_ref = $_[5];
	push @{$walkabout_ref}, ${$voxel_ref};
	${$index_ref}++;
	my $next_letter = eval { @{$word_ref}[${$index_ref}] } || return @{$walkabout_ref};
	my %neighborhood = find_neighbors(\%cube_ref, \${$voxel_ref});
	# print Dumper(\%neighborhood);
	foreach (@{$walkabout_ref}) {
		delete $neighborhood{$_};
	}
	# print Dumper(\%neighborhood);
	my @voxels = grep { $neighborhood{$_} eq $next_letter } keys %neighborhood;
	if (scalar(@voxels)) {
		foreach (@voxels) {
			my @returned = find_voxels(\%cube_ref, \@{$word_ref}, \${$index_ref}, \${$valid_word_ref}, \$_, \@{$walkabout_ref});
			return @returned if (arr2word(\%cube_ref, \@returned) eq ${$valid_word_ref});
			pop @{$walkabout_ref};
			# print "valid: " . ${$valid_word_ref} . " word: " . arr2word(\%cube_ref, \@returned) . " letter: " . @{$word_ref}[${$index_ref}] . " index: " . ${$index_ref} . " returned: ";
			# print("$_ ") foreach @returned;
			# print "\n";
		}
	}
	${$index_ref}--;
	return @{$walkabout_ref};
}

## Left-handed x,y,z representation of the cube (voxels)
our @voxels = ( '0,0,0','0,1,0','0,2,0','0,3,0','1,0,0','1,1,0','1,2,0','1,3,0','2,0,0','2,1,0','2,2,0','2,3,0','3,0,0','3,1,0','3,2,0','3,3,0',
		'0,0,1','0,1,1','0,2,1','0,3,1','1,0,1','1,1,1','1,2,1','1,3,1','2,0,1','2,1,1','2,2,1','2,3,1','3,0,1','3,1,1','3,2,1','3,3,1',
		'0,0,2','0,1,2','0,2,2','0,3,2','1,0,2','1,1,2','1,2,2','1,3,2','2,0,2','2,1,2','2,2,2','2,3,2','3,0,2','3,1,2','3,2,2','3,3,2',
		'0,0,3','0,1,3','0,2,3','0,3,3','1,0,3','1,1,3','1,2,3','1,3,3','2,0,3','2,1,3','2,2,3','2,3,3','3,0,3','3,1,3','3,2,3','3,3,3' );

our @word_count = (0) x 1000;
our $cube_index = 0;

open my $cubes, '<', $boggle_file;
while (<$cubes>) {
	chomp;
	my @letters = split(//,lc($_));
	my %cube;
	@cube{@voxels} = @letters;
	# print Dumper(\%cube);
	my %word_cache;
	my $hitme;
	foreach my $valid_word (@sorted) {
		# ($hitme) = grep { /^$valid_word/ } keys %word_cache;
		# if (length($hitme)) {
			# print "cached: " . $hitme . " word: " . $valid_word . "\n"; 
	 	#	$word_count[$cube_index]++;
	 	#	next;
		# }
		my $index = 0;
		my @word = split(//,$valid_word);
		my $first_letter = $word[$index];
		my @base_voxels;
		if (@base_voxels = grep { $cube{$_} eq $first_letter } keys %cube) {
			foreach my $voxel (@base_voxels) {
				my @walkabout;
				my @returned = find_voxels(\%cube, \@word, \$index, \$valid_word, \$voxel, \@walkabout);
				my $returned_word = arr2word(\%cube, \@returned);
				if ($returned_word eq $valid_word) {
					# if ( ! exists($word_cache{$valid_word}) ) {
					# 	$word_cache{$valid_word} = 1;
					# }
					$word_count[$cube_index]++;
					last;
				}
				# print "valid: " . $valid_word . " returned: " . $returned_word . " voxels: ";
				# print("$_ ") foreach @returned;
				# print "\n";
			}
		}
	}
	print $word_count[$cube_index] . "\n";
	# last;
	$cube_index++
}
# print("$_\n") foreach @word_count;
