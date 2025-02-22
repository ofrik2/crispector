import gzip
import os
import subprocess
from crispector.utils.exceptions import FastpRunTimeError, SgRNANotInReferenceSequence
from crispector.utils.constants_and_types import AmpliconDf, ReadsDict, ExpType, ReadsDf, Path, DNASeq, FASTP_DIR, \
    READ, ALIGNMENT_W_INS, ALIGNMENT_W_DEL, CIGAR, ALIGN_SCORE, FREQ, REFERENCE, SGRNA, SITE_NAME, CUT_SITE, REVERSED, \
    L_SITE, L_REV, R_SITE, R_REV, L_READ, R_READ, PRIMER_LEN, TransDf, TRANS_NAME, BAD_AMPLICON_THRESHOLD, CIGAR_LEN, \
    CIGAR_LEN_THRESHOLD, MAX_SCORE, F_PRIMER, R_PRIMER, SGRNA_REVERSED, \
    NORM_SCORE, TX_IN2, TX_IN1, MOCK_IN1, TX_MERGED, MOCK_MERGED, MOCK_IN2, DONOR, ON_TARGET, \
    UNMATCHED_PATH
from crispector.input_processing.alignment import Alignment
from crispector.input_processing.utils import reverse_complement, parse_fastq_file
from crispector.utils.logger import LoggerWrapper
from crispector.utils.configurator import Configurator
from typing import List, Tuple, Dict
import pandas as pd
from collections import defaultdict
import json
import edlib


class InputProcessing:
    """
    A helper class with all relevant functions to process crispector input.
    """
    def __init__(self, ref_df: AmpliconDf, output: Path, min_alignment_score: float, min_trans_alignment_score: float,
                 min_read_length_without_primers: int, cut_site_position: int, disable_translocations: bool, fastp_options_string: str,
                 keep_intermediate_files: bool, max_edit_distance_on_primers: int):
        """
        :param ref_df: AmpliconDf type
        :param output: output path
        :param min_alignment_score: user min alignment score (0-100)
        :param min_read_length_without_primers:  minimum read length without primers
        :param cut_site_position: position relative to the PAM
        :param disable_translocations : Flag
        :param fastp_options_string: string
        :return:
        """
        self._ref_df = ref_df
        self._output = output
        self._min_trans_score = min_trans_alignment_score
        self._cut_site_pos = cut_site_position
        self._fastp_options = fastp_options_string
        self._dis_trans = disable_translocations
        self._keep_fastp = keep_intermediate_files

        # Set logger
        logger = LoggerWrapper.get_logger()
        self._logger = logger

        # Get config
        self._cfg = Configurator.get_cfg()

        self._max_error_on_primer = max_edit_distance_on_primers

        # create alignment instance
        self._aligner = Alignment(self._cfg["alignment"], min_alignment_score, min_read_length_without_primers,
                                  self._cfg["NHEJ_inference"]["window_size"])

        # Add max_score column to ref_df
        max_score_list = []
        for _, row in self._ref_df.iterrows():
            reference = row[REFERENCE]

            _, _, _, _, max_score = self._aligner.needle_wunsch_align(reference=reference, read=reference)
            max_score_list.append(max_score)
        self._ref_df[MAX_SCORE] = max_score_list

        # Add primers where values are None
        self._ref_df.loc[self._ref_df[F_PRIMER].isna(), F_PRIMER] = self._ref_df.loc[self._ref_df[F_PRIMER].isna(),
                                                                                     REFERENCE].str[0:PRIMER_LEN]

        self._ref_df.loc[self._ref_df[R_PRIMER].isna(), R_PRIMER] = self._ref_df.loc[self._ref_df[R_PRIMER].isna(),
                                                                                     REFERENCE].apply(reverse_complement).str[0:PRIMER_LEN]
        # Find expected cut-site position
        self._convert_sgRNA_to_cut_site_position()

        # Prepare donor experiment variables
        self._donor = self._ref_df[DONOR].notnull().any()
        if self._donor:
            self._donor_list = self._ref_df.loc[~self._ref_df[DONOR].isna(), DONOR].values
            self._donor_names = self._ref_df.loc[~self._ref_df[DONOR].isna(), SITE_NAME].values + "_donor"

        # Reads numbers for statistics
        self._input_n = dict()
        self._input_n[ExpType.TX] = 0
        self._input_n[ExpType.MOCK] = 0

        self._merged_n = dict()
        self._merged_n[ExpType.TX] = 0
        self._merged_n[ExpType.MOCK] = 0

        self._aligned_n = dict()
        self._aligned_n[ExpType.TX] = 0
        self._aligned_n[ExpType.MOCK] = 0

    # -------------------------------#
    ######### Public methods #########
    # -------------------------------#
    def run(self, tx_in1: Path, tx_in2: Path, mock_in1: Path, mock_in2: Path):
        # Input is a multiplexed FASTQ file
        demultiplexed_input = not tx_in1 is None

        # Demultiplexed input
        if demultiplexed_input:
            override_fastp = tx_in2 is None

            # Filter low quality reads and merge pair-end reads with fastp
            if not override_fastp:
                tx_merged, tx_read_n, tx_merged_n = self._fastp(tx_in1, tx_in2, self._output, ExpType.TX)
                mock_merged, mock_read_n, mock_merged_n = self._fastp(mock_in1, mock_in2, self._output, ExpType.MOCK)
                self._input_n[ExpType.TX] += tx_read_n
                self._merged_n[ExpType.TX] += tx_merged_n
                self._input_n[ExpType.MOCK] += mock_read_n
                self._merged_n[ExpType.MOCK] += mock_merged_n
            # Skip merge
            else:
                self._logger.info("Skip merging with fastp and read merged files from input.")
                tx_merged, mock_merged = tx_in1, mock_in1

            # Demultiplexing reads
            tx_reads, tx_trans_df = self._demultiplex_reads(tx_merged, ExpType.TX)
            mock_reads, mock_trans_df = self._demultiplex_reads(mock_merged, ExpType.MOCK)

            # Split read_df to all the different sites
            tx_reads_d: ReadsDict = dict()
            mock_reads_d: ReadsDict = dict()
            for _, row in self._ref_df.iterrows():
                site = row[SITE_NAME]
                if self._donor and row[ON_TARGET]:
                    tx_reads_d[site] = pd.DataFrame(columns=[READ, FREQ])
                    mock_reads_d[site] = pd.DataFrame(columns=[READ, FREQ])
                    continue
                tx_reads_d[site] = tx_reads.loc[tx_reads[SITE_NAME] == site].sort_values(by=[FREQ],
                                                                                         ascending=False).reset_index(drop=True)
                mock_reads_d[site] = mock_reads.loc[mock_reads[SITE_NAME] == site].sort_values(by=[FREQ],
                                                                                               ascending=False).reset_index(drop=True)
                tx_reads_d[site].drop(columns=[SITE_NAME], inplace=True)
                mock_reads_d[site].drop(columns=[SITE_NAME], inplace=True)

            # Remove fastp files
            if not override_fastp and not self._keep_fastp:
                if os.path.exists(tx_merged):
                    os.remove(tx_merged)
                if os.path.exists(mock_merged):
                    os.remove(mock_merged)

        # Multiplexed input
        else:
            override_fastp = self._ref_df[TX_IN2].isna().all()

            # Filter low quality reads and merge pair-end reads with fastp
            if not override_fastp:
                tx_merged_l = []
                mock_merged_l = []
                for _, row in self._ref_df.iterrows():
                    self._logger.info("fastp for {} - May take a few minutes.".format(row[SITE_NAME]))
                    site_output = os.path.join(self._output, row[SITE_NAME])
                    tx_merged, tx_read_n, tx_merged_n = self._fastp(row[TX_IN1], row[TX_IN2], site_output, ExpType.TX)
                    mock_merged, mock_read_n, mock_merged_n = self._fastp(row[MOCK_IN1], row[MOCK_IN2], site_output,
                                                                          ExpType.MOCK)
                    tx_merged_l.append(tx_merged)
                    mock_merged_l.append(mock_merged)
                    self._input_n[ExpType.TX] += tx_read_n
                    self._merged_n[ExpType.TX] += tx_merged_n
                    self._input_n[ExpType.MOCK] += mock_read_n
                    self._merged_n[ExpType.MOCK] += mock_merged_n

                self._ref_df[TX_MERGED] = tx_merged_l
                self._ref_df[MOCK_MERGED] = mock_merged_l
            # Skip merge
            else:
                self._logger.info("Skip merging with fastp and read merged files from input.")
                self._ref_df[TX_MERGED] = self._ref_df[TX_IN1]
                self._ref_df[MOCK_MERGED] = self._ref_df[MOCK_IN1]

            # No demultiplexing
            tx_trans_df, mock_trans_df = pd.DataFrame(), pd.DataFrame()

            # Split read_df to all the different sites
            tx_reads_d: ReadsDict = dict()
            mock_reads_d: ReadsDict = dict()
            for _, row in self._ref_df.iterrows():
                for reads_d, merged_fastq, exp_type in zip([tx_reads_d, mock_reads_d],
                                                           [row[TX_MERGED], row[MOCK_MERGED]],
                                                           [ExpType.TX, ExpType.MOCK]):
                    if self._donor and row[ON_TARGET]:
                        reads_d[row[SITE_NAME]] = pd.DataFrame(columns=[READ, FREQ])
                        continue
                    reads = parse_fastq_file(merged_fastq)
                    reads_df = pd.DataFrame(data=reads, columns=[READ])
                    # Group identical reads together
                    reads_df = reads_df.groupby(READ).size().to_frame(FREQ).reset_index()
                    reads_d[row[SITE_NAME]] = reads_df

                    if override_fastp:
                        self._input_n[exp_type] += reads_df[FREQ].sum()
                        self._merged_n[exp_type] += reads_df[FREQ].sum()

            # Remove fastp files
            if not override_fastp and not self._keep_fastp:
                for _, row in self._ref_df.iterrows():
                    if os.path.exists(row[TX_MERGED]):
                        os.remove(row[TX_MERGED])
                    if os.path.exists(row[MOCK_MERGED]):
                        os.remove(row[MOCK_MERGED])

        # Align reads
        self._logger.debug("Alignment - Start alignment for all reads")
        for _, row in self._ref_df.iterrows():
            site_output = os.path.join(self._output, row[SITE_NAME])
            primers_len = len(row[F_PRIMER]) + len(row[R_PRIMER])

            # Align Treatment
            reads_df = tx_reads_d[row[SITE_NAME]]
            exp_name = "{}_{}".format(row[SITE_NAME], ExpType.TX.name)
            reads_df = self._aligner.align_reads(reads_df, row[REFERENCE], row[CUT_SITE], primers_len, site_output,
                                                 exp_name, ExpType.TX)
            tx_reads_d[row[SITE_NAME]] = reads_df
            self._aligned_n[ExpType.TX] += reads_df[FREQ].sum()

            # Align Mock
            reads_df = mock_reads_d[row[SITE_NAME]]
            exp_name = "{}_{}".format(row[SITE_NAME], ExpType.MOCK.name)
            reads_df = self._aligner.align_reads(reads_df, row[REFERENCE], row[CUT_SITE], primers_len, site_output,
                                                 exp_name, ExpType.MOCK)
            mock_reads_d[row[SITE_NAME]] = reads_df
            self._aligned_n[ExpType.MOCK] += reads_df[FREQ].sum()

        # Warning if the number of reads isn't balanced
        if (self._aligned_n[ExpType.TX] > 3 * self._aligned_n[ExpType.MOCK]) or \
           (self._aligned_n[ExpType.MOCK] > 3 * self._aligned_n[ExpType.TX]):
            self._logger.warning("Number of reads (Tx={:,}, Mock={:,}) is highly unbalanced! CRISPECTOR wasn't tested"
                                 "in these scenarios. Consider to retake the experiments")

        return tx_reads_d, mock_reads_d, tx_trans_df, mock_trans_df

    #-------------------------------#
    ######### Private methods #######
    #-------------------------------#
    ######### Merging ###########
    def _fastp(self, in1: Path, in2: Path, output: Path, exp_type: ExpType) -> Tuple[Path, int, int]:
        """
        Wrapper for fastp SW.
        :param in1: read1 input
        :param in2: read2 input
        :param output: output directory
        :param exp_type
        :return: path to merged fastq file, reads_numbers, reads_merged_numbers
        """
        # Create output folder
        fastp_output = os.path.join(output, FASTP_DIR[exp_type])
        if not os.path.exists(fastp_output):
            os.makedirs(fastp_output)

        if not os.path.exists(fastp_output):
            os.makedirs(fastp_output)

        merged_path = os.path.join(fastp_output, "merged_reads.fastq")

        command = ["fastp", "-i", in1, "-I", in2, "-o", os.path.join(fastp_output, "r1_filtered_reads.fastq"),
                   "-O", os.path.join(fastp_output, "r2_filtered_reads.fastq"), "-m", "--merged_out", merged_path,
                   "-j", os.path.join(fastp_output, "fastp.json"), "-h", os.path.join(fastp_output, "fastp.html"),
                   "--length_required {}".format(2*PRIMER_LEN),
                   self._fastp_options, ">> {} 2>&1".format(LoggerWrapper.get_log_path())]

        command = " ".join(command)

        self._logger.debug("fastp for {} - Command {}".format(exp_type.name, command))
        self._logger.info("fastp for {} - Run (may take a few minutes).".format(exp_type.name))
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError:
            raise FastpRunTimeError()

        # Get the number of reads in the input
        fastp_summary_path = os.path.join(fastp_output, "fastp.json")
        if os.path.isfile(fastp_summary_path):
            with open(fastp_summary_path) as json_file:
                summary = json.load(json_file)
                reads_in_input_num = summary["summary"]["before_filtering"]["total_reads"] // 2
                merged_reads_num = summary["summary"]["after_filtering"]["total_reads"]
        else:
            reads_in_input_num = -1
            merged_reads_num =-1

        self._logger.info("fastp for {} - Done.".format(exp_type.name))

        return merged_path, reads_in_input_num, merged_reads_num

    ######### Demultiplex ###########
    def _demultiplex_reads(self, merged_fastq: Path, exp_type: ExpType) -> Tuple[ReadsDf, TransDf]:
        """
        Demultiplex reads using edit distance on primers.
        For ambiguous matching - search for correct matching or translocation by full alignment
        :param merged_fastq: fastp merged fastq file
        :param exp_type: ExpType
        :return: Tuple ReadsDf & translocation df
        """
        reads = parse_fastq_file(merged_fastq)
        reads_df = pd.DataFrame(data=reads, columns=[READ])

        # Prepare primers for match
        references = self._ref_df[REFERENCE].str
        left_primers = list(references[:PRIMER_LEN]) + list(references[-PRIMER_LEN:].apply(reverse_complement))
        right_primers = list(references[-PRIMER_LEN:]) + list(references[:PRIMER_LEN].apply(reverse_complement))
        primers_names = 2 * list(self._ref_df[SITE_NAME])
        primers_rev = self._ref_df.shape[0] * [False] + self._ref_df.shape[0] * [True]

        # find donor reads in order to remove them
        if self._donor:
            left_primers += [seq[:PRIMER_LEN] for seq in self._donor_list]
            left_primers += [reverse_complement(ref[-PRIMER_LEN:]) for ref in self._donor_list]
            right_primers += [seq[-PRIMER_LEN:] for seq in self._donor_list]
            right_primers += [reverse_complement(ref[:PRIMER_LEN]) for ref in self._donor_list]
            primers_names += 2*list(self._donor_names)
            primers_rev += len(self._donor_names) * [False] + len(self._donor_names) * [True]

        # Group identical reads together
        reads_df = reads_df.groupby(READ).size().to_frame(FREQ).reset_index()
        total_read_n = reads_df[FREQ].sum()

        # Update number of reads in input (relevant when input is already merged)
        if self._input_n[exp_type] == 0:
            self._input_n[exp_type] += total_read_n
            self._merged_n[exp_type] += total_read_n

        # Create temporary columns for read start and end
        reads_df[L_READ] = reads_df[READ].str[0:PRIMER_LEN]
        reads_df[R_READ] = reads_df[READ].str[-PRIMER_LEN:]

        self._logger.info("Assigning reads to target amplicons for {} - Start assigning {:,} reads - May take a few "
                          "minutes".format(exp_type.name, total_read_n))

        # Find a match for left and right parts of the read
        l_match = self._compute_read_primer_matching(reads_df[L_READ].unique(), left_primers, primers_rev,
                                                     primers_names, self._max_error_on_primer)
        r_match = self._compute_read_primer_matching(reads_df[R_READ].unique(), right_primers, primers_rev,
                                                     primers_names, self._max_error_on_primer)

        reads_df[[L_SITE, L_REV]] = reads_df.apply((lambda row: l_match[row[L_READ]]), axis=1, result_type='expand')
        reads_df[[R_SITE, R_REV]] = reads_df.apply((lambda row: r_match[row[R_READ]]), axis=1, result_type='expand')

        unmatched_df = reads_df.loc[(reads_df[L_SITE] != reads_df[R_SITE]) | (reads_df[L_REV] != reads_df[R_REV])].copy()
        reads_df.drop(index=unmatched_df.index, inplace=True)

        # Find translocations or match ambiguous reads
        trans_df, re_matched_df = self._find_translocations_or_new_matching(unmatched_df)

        # Add re matched reads to reads pool
        # reads_df = pd.concat([reads_df, re_matched_df])
        reads_df[SITE_NAME] = reads_df[L_SITE]
        reads_df[REVERSED] = reads_df[L_REV]
        reads_df.drop(columns=[L_SITE, L_REV, R_SITE, R_REV, R_READ, L_READ], inplace=True)
        reads_df.reset_index(drop=True, inplace=True)

        self._dump_unmatched_reads(unmatched_df, total_read_n, self._output, exp_type)

        # Detect bad amplicons (search for high frequency reads without a matched site)
        if self._donor:
            sites = list(self._ref_df.loc[self._ref_df[ON_TARGET], SITE_NAME]) + list(self._donor_names)
            # No on_target or donor
            detect_unmatched_df = unmatched_df.loc[~unmatched_df[L_SITE].isin(sites) | ~unmatched_df[R_SITE].isin(sites)]
        else:
            detect_unmatched_df = unmatched_df

        self._detect_bad_amplicons(detect_unmatched_df)

        self._logger.info("Assigning reads to target amplicons for {} - Done".format(exp_type.name))

        return reads_df, trans_df

    def _compute_read_primer_matching(self, reads: List[DNASeq], primers: List[DNASeq], primers_revered: List[bool],
                                          primers_names: List[str], max_edit_distance: int) -> Dict[DNASeq, Tuple[str, bool]]:
        """
        Create a dictionary with a match between each possible read (key) and a primer (val).
        :param reads:  partial (left or right) reads
        :param primers: List of primers sequences
        :param primers_revered: List that indicates if primers reversed or not
        :param primers_names: primers names
        :param max_edit_distance: Max edit distance to account as a match
        :return: Dict[read, Tuple[site_name, reversed_flag]]
        """
        match = dict()
        for read in reads:
            match[read] = self._match_by_edit_distance(read, primers, primers_revered, primers_names, max_edit_distance)

        return match

    @staticmethod
    def _match_by_edit_distance(read: DNASeq, primers: List[DNASeq], primers_revered: List[bool],
                                primers_names: List[str], max_edit_distance: int) -> Tuple[str, bool]:
        """
        Find for every read the most similar sequence (primer).
        If the minimum edit distance is above DNASeq, no primer is matched.
        :param read:  reads
        :param primers: List of primers sequences
        :param primers_revered: List that indicates if primers reversed or not
        :param primers_names: primers names
        :param max_edit_distance: Max edit distance to account as a match
        :return: site_name, reversed flag
        """
        min_name = None
        min_dist = max_edit_distance + 1
        min_reversed = False

        for primer, reverse, name  in zip(primers, primers_revered, primers_names):
            d = edlib.align(read, primer, k=min_dist)['editDistance']
            if d < min_dist and d != -1:
                min_dist = d
                min_name = name
                min_reversed = reverse

        return min_name, min_reversed

    def _detect_bad_amplicons(self, unmatched_df: ReadsDf):
        """
        - detect unmatched reads with large frequency and warn user from bad amplicon.
        :param unmatched_df:
        :return:
        """
        # prepare reference list and names
        references = list(self._ref_df[REFERENCE].values)
        names = list(self._ref_df[SITE_NAME].values)
        references += list(self._ref_df[REFERENCE].apply(reverse_complement))
        names += ["{}_reversed".format(name) for name in names]
        ref_rev = self._ref_df.shape[0]*[False] + self._ref_df.shape[0]*[True]
        ref_scores = list(self._ref_df[MAX_SCORE].values) + list(self._ref_df[MAX_SCORE].values)

        high_freq_df = unmatched_df.loc[unmatched_df[FREQ] > BAD_AMPLICON_THRESHOLD].copy()
        high_freq_df.sort_values(by=[FREQ], ascending=False, inplace=True)

        for _, row in high_freq_df.iterrows():
            site_name,_,_ = self._aligner.match_by_full_alignment(row[READ], references, names, ref_rev, ref_scores)
            self._logger.warning("The following read has {} repetitions, but it doesn't match any site!"
                                 "This read is most similar to reference site {}. Please check amplicon sequences "
                                 "correctness. read={}".format(row[FREQ], site_name, row[READ]))

    ######### Translocations ########
    def _get_translocation_reference(self, l_name: str, l_rev: bool, r_name: str, r_rev: bool) -> Tuple[DNASeq, int, float]:
        """
        Compute possible translocation for between left site and right site
        :param l_name: left site match
        :param l_rev: left site reversed flag
        :param r_name: right site match
        :param r_rev: right site reversed flag
        :return: reference sequence, expected_cut_site and max alignment score
        """
        # Left part of the reference
        l_ref = self._ref_df[REFERENCE][l_name]
        l_cut_site = self._ref_df[CUT_SITE][l_name]
        l_ref = reverse_complement(l_ref[l_cut_site:]) if l_rev else l_ref[:l_cut_site]

        # Right part of the reference
        r_ref = self._ref_df[REFERENCE][r_name]
        r_cut_site = self._ref_df[CUT_SITE][r_name]
        r_ref = reverse_complement(r_ref[:r_cut_site]) if r_rev else r_ref[r_cut_site:]

        reference = l_ref + r_ref
        _, _, _, _, max_score = self._aligner.needle_wunsch_align(reference=reference, read=reference)

        return reference, l_cut_site, max_score

    def _find_translocations_or_new_matching(self, unmatched_df: ReadsDf) -> Tuple[TransDf, ReadsDf]:
        """
        For every non None match, find the best alignment between: left site, right site and translocation between
        left & right.
        :param unmatched_df: unmatched reads
        :return:
        """
        trans_d = defaultdict(list)
        trans_idx_list = []  # list of matched translocation
        re_matched_idx_list = []  # list of re matched indexes (initial bad demultiplexing)
        # trans_ref dict - Key is translocation ID and value is reference, cut_site & max alignment score
        trans_ref_d: Dict[Tuple[str, bool, str, bool], Tuple[DNASeq, int, float]] = dict()

        possible_trans_df = unmatched_df.loc[unmatched_df[L_SITE].notnull() & unmatched_df[R_SITE].notnull()]
        if self._donor:
            sites = list(self._ref_df.loc[self._ref_df[ON_TARGET], SITE_NAME]) + list(self._donor_names)
            # No on_target or donor
            possible_trans_df = possible_trans_df.loc[~possible_trans_df[L_SITE].isin(sites) &
                                                      ~possible_trans_df[R_SITE].isin(sites)]

        def get_trans_name(name, rev, left):
            if left:
                direction = 'L' if not rev else 'R'
                return name + "_" + direction
            else:
                direction = 'R' if not rev else 'L'
                return name + "_" + direction

        if not self._dis_trans:
            self._logger.debug("Search possible Translocations for {:,} reads. May take a few minutes".format(
                unmatched_df[FREQ].sum()))
        else:
            self._logger.debug("Find site matching for {:,} ambiguous reads. May take a few minutes".format(
                unmatched_df[FREQ].sum()))

        for idx, row in possible_trans_df.iterrows():
            # Compute translocation reference, cut-site & max alignment score
            l_name, l_rev, r_name, r_rev = row[[L_SITE, L_REV, R_SITE, R_REV]]
            if (l_name, l_rev, r_name, r_rev) in trans_ref_d:
                reference, cut_site, max_score = trans_ref_d[(l_name, l_rev, r_name, r_rev)]
            else:
                reference, cut_site, max_score = self._get_translocation_reference(l_name, l_rev, r_name, r_rev)
                trans_ref_d[(l_name, l_rev, r_name, r_rev)] = reference, cut_site, max_score

            # Compute alignment
            ref_w_ins, read_w_del, cigar, cigar_len, align_score = \
                self._aligner.needle_wunsch_align(reference=reference, read=row[READ])
            normalized_score = align_score / max_score

            # Compute left site and right site alignment score - to verify that the highest is the translocation
            l_ref = reverse_complement(self._ref_df[REFERENCE][l_name]) if l_rev else self._ref_df[REFERENCE][l_name]
            _, _, _, _, l_align_score = self._aligner.needle_wunsch_align(reference=l_ref, read=row[READ])
            l_normalized_score = l_align_score / self._ref_df[MAX_SCORE][l_name]

            r_ref = reverse_complement(self._ref_df[REFERENCE][r_name]) if r_rev else self._ref_df[REFERENCE][r_name]
            _, _, _, _, r_align_score = self._aligner.needle_wunsch_align(reference=r_ref, read=row[READ])
            r_normalized_score = r_align_score / self._ref_df[MAX_SCORE][r_name]

            # Check if left or right sites have better alignment than the translocation
            if (r_normalized_score > normalized_score) or (l_normalized_score > normalized_score):
                if r_normalized_score > l_normalized_score:
                    unmatched_df.at[idx, L_SITE] = row[R_SITE]
                    unmatched_df.at[idx, L_REV] = row[R_REV]
                else:
                    unmatched_df.at[idx, R_SITE] = row[L_SITE]
                    unmatched_df.at[idx, R_REV] = row[L_REV]
                re_matched_idx_list.append(idx)
            # If read has high quality alignment, consider it as translocation
            elif (not self._dis_trans) and (align_score > (self._min_trans_score / 100) * max_score) or \
                    (cigar_len < CIGAR_LEN_THRESHOLD):
                trans_idx_list.append(idx)
                trans_d[TRANS_NAME].append(get_trans_name(l_name, l_rev, True) + "_" + get_trans_name(r_name, r_rev, False))
                trans_d[FREQ].append(row[FREQ])
                trans_d[R_SITE].append(r_name)
                trans_d[L_SITE].append(l_name)
                trans_d[REFERENCE].append(reference)
                trans_d[READ].append(row[READ])
                trans_d[ALIGNMENT_W_INS].append(ref_w_ins)
                trans_d[ALIGNMENT_W_DEL].append(read_w_del)
                trans_d[CUT_SITE].append(cut_site)
                trans_d[CIGAR].append(cigar)
                trans_d[CIGAR_LEN].append(cigar_len)
                trans_d[ALIGN_SCORE].append(align_score)
                trans_d[NORM_SCORE].append(normalized_score)

        # Convert translocation dictionary to translocation pandas
        self._logger.debug("Site matching for ambiguous reads and Translocations Search - Done.")
        trans_df = pd.DataFrame.from_dict(trans_d, orient='columns')

        # Remove translocation from unmatched reads
        unmatched_df.drop(index=trans_idx_list, inplace=True)

        # Create new df for re matched reads
        re_matched_df = unmatched_df.copy()
        unmatched_df.drop(index=re_matched_idx_list, inplace=True)
        re_matched_df.drop(index=unmatched_df.index, inplace=True)

        return trans_df, re_matched_df

    ######### General ###############
    def _convert_sgRNA_to_cut_site_position(self):
        self._ref_df[[CUT_SITE, SGRNA_REVERSED]] = self._ref_df.apply(lambda row: self._get_expected_cut_site(row[REFERENCE],
                                                   row[SGRNA], self._cut_site_pos, row[SITE_NAME]), axis=1, result_type='expand')

    @staticmethod
    def _get_expected_cut_site(reference: DNASeq, sgRNA: DNASeq, cut_site_position: int, site_name: str = '') \
        -> Tuple[int, bool]:
        """
        Find sgRNA (or the reverse complement) inside the reference and return the expected cut-site.
        The cut-site is LEFT to returned index
        :param reference: reference sequence
        :param sgRNA: sgRNA sequence
        :param cut_site_position: position relative to the PAM
        :param site_name: site name
        :return: expected cut-site, reversed sgRNA or not
        """
        reverse = False
        sgRNA_start_idx = reference.find(sgRNA)
        if sgRNA_start_idx == -1:
            sgRNA_start_idx = reference.find(reverse_complement(sgRNA))
            if sgRNA_start_idx == -1:
                raise SgRNANotInReferenceSequence(site_name)
            else:
                cut_site = sgRNA_start_idx - cut_site_position
                reverse = True
        else:
            cut_site = sgRNA_start_idx + len(sgRNA) + cut_site_position

        return cut_site, reverse

    def _dump_unmatched_reads(self, unmatched_df: ReadsDf, total_read_n: int, output: Path, exp_name: ExpType):
        """
        - Dump unmatched reads
        - Store all unaligned reads in a fasta format.
        :param unmatched_df: aligned reads df.
        :param total_read_n:
        :param output: output path for filtered reads
        :param exp_name: experiment name
        :return:
        """
        unmatched_reads_num = unmatched_df[FREQ].sum()

        self._logger.info("Assigning reads to target amplicons for {} - {:,} reads weren't matched ({:.2f}% of all"
                          " reads)".format(exp_name.name, unmatched_reads_num, 100*unmatched_reads_num/total_read_n))

        file = gzip.open(os.path.join(output, UNMATCHED_PATH[exp_name]), 'wt')
        for _, row in unmatched_df.iterrows():
            file.write("> unaligned read with {} copies in the original fastq file.\n".format(row[FREQ]))
            file.write("{}\n".format(row[READ]))
        file.close()

    ######### Getters ###########
    def read_numbers(self, exp_type: ExpType) -> Tuple[int, int, int]:
        """
        return a tuple of number of input, merged & aligned
        :param exp_type:
        :return:
        """
        return self._input_n[exp_type], self._merged_n[exp_type], self._aligned_n[exp_type]
