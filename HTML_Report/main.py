from makeReport import create_final_html_report
import pickle
import os
from numpy import nan


def main():

    exp_param_d = {'edit_section': {'title': 'Editing Activity', 'editing_activity': {'plot_path': 'crispector_output/editing_activity.png', 'pdf_path': 'crispector_output/editing_activity.pdf', 'title': 'Editing Activity with 95.0 % CI above 0.1%', 'width': 6000, 'height': 3600}, 'result_table': {'title': 'Results Table', 'tabular_data': {0: ['SiteName', 'OnTarget', 'Mock number of reads', 'Treatment number of reads', 'Edited reads', 'Editing Activity', 'CI_low', 'CI_high'], 1: ['Rag1_1', True, 33853, 29135, 20031.0, 68.75235970482237, 68.22013749067891, 69.28458191896584], 2: ['Rag1_10', False, 17851, 20914, 5.0, 0.02390743042937745, 0.002954533869533156, 0.044860326989221745], 3: ['Rag1_11', False, 3935, 1846, 0.0, 0.0, 0.0, 0.0], 4: ['Rag1_12', False, 41391, 52338, 7.0, 0.013374603538537965, 0.003467403234859585, 0.023281803842216342], 5: ['Rag1_13', False, 17513, 22927, 3.0, 0.013085008941422777, 0.0, 0.027890849621933934], 6: ['Rag1_14', False, 3199, 2819, 4.0, 0.1418942887548776, 0.002939130724494382, 0.2808494467852608], 7: ['Rag1_15', False, 10164, 19766, 3.0, 0.015177577658605687, 0.0, 0.03235100461144022], 8: ['Rag1_16', False, 8300, 7982, 1.0, 0.012528188423953897, 0.0, 0.0370814483425703], 9: ['Rag1_17', False, 6250, 6691, 3.0, 0.044836347332237333, 0.0, 0.0955611429433317], 10: ['Rag1_19', False, 18340, 16486, 16.0, 0.09705204415868009, 0.04952049833535293, 0.14458358998200727], 11: ['Rag1_2', False, 1184, 984, 3.0, 0.3048780487804878, 0.0, 0.6493473899527277], 12: ['Rag1_20', False, 10523, 5031, 71.0, 1.4112502484595508, 1.085311024161772, 1.7371894727573298], 13: ['Rag1_21', False, 23127, 18812, 24.0, 0.1275781416117372, 0.07656976140732748, 0.17858652181614687], 14: ['Rag1_22', False, 10282, 5599, 2.0, 0.03572066440435792, 0.0, 0.08521722719107422], 15: ['Rag1_23', False, 5834, 5301, 0.0, 0.0, 0.0, 0.0], 16: ['Rag1_24', False, 13342, 22009, 13.0, 0.05906674542232723, 0.02696777097443606, 0.0911657198702184], 17: ['Rag1_25', False, 9900, 11550, 13.0, 0.11255411255411256, 0.05140456653336104, 0.17370365857486406], 18: ['Rag1_26', False, 10961, 14432, 5.0, 0.03464523281596452, 0.004283166200601783, 0.06500729943132727], 19: ['Rag1_27', False, 15161, 12912, 0.0, 0.0, 0.0, 0.0], 20: ['Rag1_28', False, 5891, 4773, 2.0, 0.04190236748376283, 0.0, 0.09996285064610552], 21: ['Rag1_29', False, 3320, 2919, 0.0, 0.0, 0.0, 0.0], 22: ['Rag1_3', False, 54305, 65811, 23.0, 0.03494856482958776, 0.020668255465713603, 0.04922887419346192], 23: ['Rag1_30', False, 0, 0, nan, nan, nan, nan], 24: ['Rag1_31', False, 46592, 73153, 23.0, 0.03144095252416169, 0.018593660855206216, 0.04428824419311716], 25: ['Rag1_32', False, 21337, 27378, 5.0, 0.01826283877565929, 0.0022565107390479077, 0.03426916681227067], 26: ['Rag1_33', False, 17940, 18947, 5.0, 0.026389402016150313, 0.0032615485718862454, 0.04951725546041438], 27: ['Rag1_34', False, 28168, 31534, 2.0, 0.006342360626625229, 0.0, 0.015131983726413126], 28: ['Rag1_35', False, 8688, 5013, 3.0, 0.059844404548174746, 0.0, 0.12754321292825596], 29: ['Rag1_36', False, 4336, 4525, 15.0, 0.3314917127071823, 0.16401512017761538, 0.49896830523674923], 30: ['Rag1_37', False, 0, 0, nan, nan, nan, nan], 31: ['Rag1_38', False, 5639, 3517, 0.0, 0.0, 0.0, 0.0], 32: ['Rag1_39', False, 849, 546, 2.0, 0.3663003663003663, 0.0, 0.8730268169424692], 33: ['Rag1_4', False, 13179, 10124, 3.0, 0.029632556301856974, 0.0, 0.06315936574765064], 34: ['Rag1_40', False, 26189, 40988, 0.0, 0.0, 0.0, 0.0], 35: ['Rag1_41', False, 11815, 11816, 0.0, 0.0, 0.0, 0.0], 36: ['Rag1_42', False, 32797, 33207, 0.0, 0.0, 0.0, 0.0], 37: ['Rag1_43', False, 4361, 3068, 0.0, 0.0, 0.0, 0.0], 38: ['Rag1_44', False, 16363, 20094, 7.0, 0.034836269533193985, 0.009034169542051449, 0.06063836952433653], 39: ['Rag1_45', False, 18098, 14583, 3.0, 0.02057189878625797, 0.0, 0.043848371399989254], 40: ['Rag1_46', False, 14779, 16379, 0.0, 0.0, 0.0, 0.0], 41: ['Rag1_47', False, 13217, 10591, 8.0, 0.07553583231045227, 0.023212905354575666, 0.12785875926632886], 42: ['Rag1_48', False, 13553, 20408, 0.0, 0.0, 0.0, 0.0], 43: ['Rag1_49', False, 12332, 10170, 12.0, 0.11799410029498525, 0.05127327818146883, 0.18471492240850168], 44: ['Rag1_5', False, 14661, 15404, 157.0, 1.0192157881069852, 0.8606023962194055, 1.177829179994565], 45: ['Rag1_50', False, 13001, 8837, 0.0, 0.0, 0.0, 0.0], 46: ['Rag1_51', False, 9034, 5951, 0.0, 0.0, 0.0, 0.0], 47: ['Rag1_52', False, 12275, 8790, 0.0, 0.0, 0.0, 0.0], 48: ['Rag1_53', False, 12513, 7358, 0.0, 0.0, 0.0, 0.0], 49: ['Rag1_54', False, 9892, 7774, 12.0, 0.15436068947774634, 0.06709194481501857, 0.2416294341404741], 50: ['Rag1_55', False, 30353, 23835, 0.0, 0.0, 0.0, 0.0], 51: ['Rag1_56', False, 19002, 25466, 3.0, 0.011780413099819366, 0.0, 0.025110175285196393], 52: ['Rag1_57', False, 17614, 19085, 0.0, 0.0, 0.0, 0.0], 53: ['Rag1_58', False, 12745, 6374, 7.0, 0.10982114841543772, 0.02851068294202827, 0.19113161388884717], 54: ['Rag1_59', False, 8240, 7565, 1.0, 0.013218770654329148, 0.0, 0.03912537261978597], 55: ['Rag1_6', False, 3763, 2709, 9.0, 0.33222591362126247, 0.1155364870656751, 0.5489153401768498], 56: ['Rag1_60', False, 5470, 5614, 3.0, 0.053437833986462416, 0.0, 0.11389116563343774], 57: ['Rag1_61', False, 4108, 3845, 3.0, 0.07802340702210664, 0.0, 0.16627913111018927], 58: ['Rag1_62', False, 2131, 1514, 2.0, 0.13210039630118892, 0.0, 0.3150578770962337], 59: ['Rag1_63', False, 15656, 20857, 0.0, 0.0, 0.0, 0.0], 60: ['Rag1_64', False, 5466, 5477, 0.0, 0.0, 0.0, 0.0], 61: ['Rag1_65', False, 18114, 13827, 2.0, 0.014464453605265059, 0.0, 0.034509345324612424], 62: ['Rag1_66', False, 7666, 6900, 0.0, 0.0, 0.0, 0.0], 63: ['Rag1_67', False, 10773, 8271, 3.0, 0.03627130939426913, 0.0, 0.07730796137041795], 64: ['Rag1_68', False, 3835, 2113, 2.0, 0.09465215333648841, 0.0, 0.2257688381604634], 65: ['Rag1_69', False, 8067, 7176, 2.0, 0.027870680044593088, 0.0, 0.06649137905464902], 66: ['Rag1_7', False, 9406, 7472, 1.0, 0.013383297644539615, 0.0, 0.03961232369171163], 67: ['Rag1_70', False, 6205, 3514, 0.0, 0.0, 0.0, 0.0], 68: ['Rag1_71', False, 10765, 7861, 1.0, 0.012721027859051012, 0.0, 0.03765219840723728], 69: ['Rag1_72', False, 24449, 23698, 0.0, 0.0, 0.0, 0.0], 70: ['Rag1_73', False, 0, 0, nan, nan, nan, nan], 71: ['Rag1_75', False, 15789, 22709, 5.0, 0.022017702232595006, 0.002720814650512902, 0.04131458981467711], 72: ['Rag1_77', False, 8125, 8871, 2.0, 0.022545372562281594, 0.0, 0.05378756818741582], 73: ['Rag1_78', False, 10751, 9793, 3.0, 0.030634126416828344, 0.0, 0.06529395675782054], 74: ['Rag1_79', False, 0, 0, nan, nan, nan, nan], 75: ['Rag1_8', False, 10692, 9322, 87.0, 0.9332761210040764, 0.7380838938938536, 1.1284683481142992], 76: ['Rag1_80', False, 13396, 10840, 0.0, 0.0, 0.0, 0.0], 77: ['Rag1_81', False, 29261, 36089, 0.0, 0.0, 0.0, 0.0], 78: ['Rag1_83', False, 0, 0, nan, nan, nan, nan], 79: ['Rag1_84', False, 30309, 37244, 0.0, 0.0, 0.0, 0.0], 80: ['Rag1_85', False, 3840, 4957, 2.0, 0.0403469840629413, 0.0, 0.09625274201917973], 81: ['Rag1_86', False, 20633, 18355, 1.0, 0.005448106782892944, 0.0, 0.016125908980372923], 82: ['Rag1_87', False, 36091, 56763, 6.0, 0.010570265842185931, 0.0021128940769756157, 0.019027637607396248], 83: ['Rag1_88', False, 24105, 21170, 2.0, 0.00944733112895607, 0.0, 0.022539804981971775], 84: ['Rag1_89', False, 27796, 37720, 0.0, 0.0, 0.0, 0.0], 85: ['Rag1_9', False, 7275, 7023, 2.0, 0.028477858465043433, 0.0, 0.06793981126109919], 86: ['Rag1_90', False, 2572, 1693, 0.0, 0.0, 0.0, 0.0], 87: ['Rag1_91', False, 13039, 13693, 0.0, 0.0, 0.0, 0.0], 88: ['Rag1_92', False, 20813, 17343, 2.0, 0.01153203021391916, 0.0, 0.027513393422381512], 89: ['Rag1_93', False, 4991, 9656, 0.0, 0.0, 0.0, 0.0], 90: ['Rag1_94', False, 50889, 57896, 1.0, 0.001727235042144535, 0.0, 0.005112524281253602]}}}, 'reading_statistics': {'fastp_tx_path': '','fastp_mock_path': '', 'title': 'Reading Statistics', 'mapping_stats': {'plot_path': 'crispector_output/mapping_statistics.png', 'pdf_path': 'crispector_output/mapping_statistics.pdf', 'title': 'Mapping Statistics', 'width': 2800, 'height': 1600}, 'mapping_per_site': {'plot_path': 'crispector_output/number_of_aligned_reads_per_site.png', 'pdf_path': 'crispector_output/number_of_aligned_reads_per_site.pdf', 'title': 'Number Of Aligned Reads Per Site', 'width': 2800, 'height': 1600}, 'discarded_sites': '5 sites were discarded due to low number of reads (below 500):\nRag1_30 - Treatment reads - 0. Mock reads - 0.\nRag1_37 - Treatment reads - 0. Mock reads - 0.\nRag1_73 - Treatment reads - 0. Mock reads - 0.\nRag1_79 - Treatment reads - 0. Mock reads - 0.\nRag1_83 - Treatment reads - 0. Mock reads - 0.\n'}, 'translocations': {'title': 'Translocations', 'tx_translocations_path': 'crispector_output/tx_translocations_reads.csv', 'mock_translocations_path': 'crispector_output/mock_translocations_reads.csv', 'translocations_heatmap_tab': {'title': '', 'plot_path': '', 'pdf_path': '', 'width': '', 'height': ''}, 'translocations_results_tab': {'title': 'Translocations results sorted by FDR value', 'tabular_data': {0: ['site_A', 'site_B', 'treatment_reads', 'mock_reads', 'p_value', 'FDR'], 1: ['Rag1_1', 'Rag1_49', 5, 0, 0.019981508478723972, 0.15985206782979178], 2: ['Rag1_1', 'Rag1_20', 4, 2, 0.16668376796685697, 0.47349018942092175], 3: ['Rag1_1', 'Rag1_36', 2, 0, 0.23674509471046087, 0.47349018942092175], 4: ['Rag1_1', 'Rag1_8', 2, 0, 0.21543825721883852, 0.47349018942092175], 5: ['Rag1_1', 'Rag1_58', 1, 0, 0.39615795960336064, 0.633852735365377], 6: ['Rag1_1', 'Rag1_21', 0, 3, 1.0, 1.0], 7: ['Rag1_1', 'Rag1_25', 0, 2, 1.0, 1.0], 8: ['Rag1_1', 'Rag1_54', 0, 3, 1.0, 1.0]}}}, 'site_names': ['Rag1_30', 'Rag1_37', 'Rag1_73', 'Rag1_79', 'Rag1_83'], 'log_path': 'crispector_output crispector_main.log'}

    site_param_d = {'Rag1_30': {'title': 'Rag1_30', 'editing_activity': {'plot_path': 'crispector_output/Rag1_30/site_editing_activity.png', 'pdf_path': 'crispector_output/Rag1_30/site_editing_activity.pdf', 'title': 'Editing Activity', 'width': 800, 'height': 800}, 'modification_section': {'title': 'Modifications', 'edit_distribution': {'plot_path': 'crispector_output/Rag1_30/distribution_of_edit_events.png', 'pdf_path': 'crispector_output/Rag1_30/distribution_of_edit_events.pdf', 'title': 'Edited Events Distribution', 'width': 1600, 'height': 900}, 'modification_distribution': {'plot_path': 'crispector_output/Rag1_30/distribution_of_all_modifications.png', 'pdf_path': 'crispector_output/Rag1_30/distribution_of_all_modifications.pdf', 'title': 'All Modifications Distribution', 'width': 3200, 'height': 1800}, 'edit_size_distribution': {'plot_path': 'crispector_output/Rag1_30/distribution_of_edit_events_size.png', 'pdf_path': 'crispector_output/Rag1_30/distribution_of_edit_events_size.pdf', 'title': 'Edit Event Size Distribution', 'width': 1600, 'height': 600}}, 'classifier_results_section': {'title': 'Classifier Results', 'classifier_results_del': {'plot_path': 'crispector_output/Rag1_30/classifier_results_by_position_del.png', 'pdf_path': 'crispector_output/Rag1_30/classifier_results_by_position_del.pdf', 'title': 'deletions', 'width': 2400, 'height': 1600}, 'classifier_results_ins': {'plot_path': 'crispector_output/Rag1_30/classifier_results_by_position_ins.png', 'pdf_path': 'crispector_output/Rag1_30/classifier_results_by_position_ins.pdf', 'title': 'Insertions', 'width': 2400, 'height': 1600}, 'classifier_results_mix': {'plot_path': 'crispector_output/Rag1_30/classifier_results_by_position_mix_and_sub.png', 'pdf_path': 'crispector_output/Rag1_30/classifier_results_by_position_mix_and_sub.pdf', 'title': 'Mixed & Substitutions', 'width': 2400, 'height': 1600}}, 'read_section': {'title': 'Reads', 'edited_reads': 'crispector_output/Rag1_30/edited_reads_table.html', 'treatment_aligned_reads': 'crispector_output/Rag1_30/treatment_aligned_reads.csv.gz', 'mock_aligned_reads': 'crispector_output/Rag1_30/mock_aligned_reads.csv.gz'}}, 'Rag1_37': {'title': 'Rag1_37', 'editing_activity': {'plot_path': 'crispector_output/Rag1_37/site_editing_activity.png', 'pdf_path': 'crispector_output/Rag1_37/site_editing_activity.pdf', 'title': 'Editing Activity', 'width': 800, 'height': 800}, 'modification_section': {'title': 'Modifications', 'edit_distribution': {'plot_path': 'crispector_output/Rag1_37/distribution_of_edit_events.png', 'pdf_path': 'crispector_output/Rag1_37/distribution_of_edit_events.pdf', 'title': 'Edited Events Distribution', 'width': 1600, 'height': 900}, 'modification_distribution': {'plot_path': 'crispector_output/Rag1_37/distribution_of_all_modifications.png', 'pdf_path': 'crispector_output/Rag1_37/distribution_of_all_modifications.pdf', 'title': 'All Modifications Distribution', 'width': 3200, 'height': 1800}, 'edit_size_distribution': {'plot_path': 'crispector_output/Rag1_37/distribution_of_edit_events_size.png', 'pdf_path': 'crispector_output/Rag1_37/distribution_of_edit_events_size.pdf', 'title': 'Edit Event Size Distribution', 'width': 1600, 'height': 600}}, 'classifier_results_section': {'title': 'Classifier Results', 'classifier_results_del': {'plot_path': 'crispector_output/Rag1_37/classifier_results_by_position_del.png', 'pdf_path': 'crispector_output/Rag1_37/classifier_results_by_position_del.pdf', 'title': 'deletions', 'width': 2400, 'height': 1600}, 'classifier_results_ins': {'plot_path': 'crispector_output/Rag1_37/classifier_results_by_position_ins.png', 'pdf_path': 'crispector_output/Rag1_37/classifier_results_by_position_ins.pdf', 'title': 'Insertions', 'width': 2400, 'height': 1600}, 'classifier_results_mix': {'plot_path': 'crispector_output/Rag1_37/classifier_results_by_position_mix_and_sub.png', 'pdf_path': 'crispector_output/Rag1_37/classifier_results_by_position_mix_and_sub.pdf', 'title': 'Mixed & Substitutions', 'width': 2400, 'height': 1600}}, 'read_section': {'title': 'Reads', 'edited_reads': 'crispector_output/Rag1_37/edited_reads_table.html', 'treatment_aligned_reads': 'crispector_output/Rag1_37/treatment_aligned_reads.csv.gz', 'mock_aligned_reads': 'crispector_output/Rag1_37/mock_aligned_reads.csv.gz'}}, 'Rag1_73': {'title': 'Rag1_73', 'editing_activity': {'plot_path': 'crispector_output/Rag1_73/site_editing_activity.png', 'pdf_path': 'crispector_output/Rag1_73/site_editing_activity.pdf', 'title': 'Editing Activity', 'width': 800, 'height': 800}, 'modification_section': {'title': 'Modifications', 'edit_distribution': {'plot_path': 'crispector_output/Rag1_73/distribution_of_edit_events.png', 'pdf_path': 'crispector_output/Rag1_73/distribution_of_edit_events.pdf', 'title': 'Edited Events Distribution', 'width': 1600, 'height': 900}, 'modification_distribution': {'plot_path': 'crispector_output/Rag1_73/distribution_of_all_modifications.png', 'pdf_path': 'crispector_output/Rag1_73/distribution_of_all_modifications.pdf', 'title': 'All Modifications Distribution', 'width': 3200, 'height': 1800}, 'edit_size_distribution': {'plot_path': 'crispector_output/Rag1_73/distribution_of_edit_events_size.png', 'pdf_path': 'crispector_output/Rag1_73/distribution_of_edit_events_size.pdf', 'title': 'Edit Event Size Distribution', 'width': 1600, 'height': 600}}, 'classifier_results_section': {'title': 'Classifier Results', 'classifier_results_del': {'plot_path': 'crispector_output/Rag1_73/classifier_results_by_position_del.png', 'pdf_path': 'crispector_output/Rag1_73/classifier_results_by_position_del.pdf', 'title': 'deletions', 'width': 2400, 'height': 1600}, 'classifier_results_ins': {'plot_path': 'crispector_output/Rag1_73/classifier_results_by_position_ins.png', 'pdf_path': 'crispector_output/Rag1_73/classifier_results_by_position_ins.pdf', 'title': 'Insertions', 'width': 2400, 'height': 1600}, 'classifier_results_mix': {'plot_path': 'crispector_output/Rag1_73/classifier_results_by_position_mix_and_sub.png', 'pdf_path': 'crispector_output/Rag1_73/classifier_results_by_position_mix_and_sub.pdf', 'title': 'Mixed & Substitutions', 'width': 2400, 'height': 1600}}, 'read_section': {'title': 'Reads', 'edited_reads': 'crispector_output/Rag1_73/edited_reads_table.html', 'treatment_aligned_reads': 'crispector_output/Rag1_73/treatment_aligned_reads.csv.gz', 'mock_aligned_reads': 'crispector_output/Rag1_73/mock_aligned_reads.csv.gz'}}, 'Rag1_79': {'title': 'Rag1_79', 'editing_activity': {'plot_path': 'crispector_output/Rag1_79/site_editing_activity.png', 'pdf_path': 'crispector_output/Rag1_79/site_editing_activity.pdf', 'title': 'Editing Activity', 'width': 800, 'height': 800}, 'modification_section': {'title': 'Modifications', 'edit_distribution': {'plot_path': 'crispector_output/Rag1_79/distribution_of_edit_events.png', 'pdf_path': 'crispector_output/Rag1_79/distribution_of_edit_events.pdf', 'title': 'Edited Events Distribution', 'width': 1600, 'height': 900}, 'modification_distribution': {'plot_path': 'crispector_output/Rag1_79/distribution_of_all_modifications.png', 'pdf_path': 'crispector_output/Rag1_79/distribution_of_all_modifications.pdf', 'title': 'All Modifications Distribution', 'width': 3200, 'height': 1800}, 'edit_size_distribution': {'plot_path': 'crispector_output/Rag1_79/distribution_of_edit_events_size.png', 'pdf_path': 'crispector_output/Rag1_79/distribution_of_edit_events_size.pdf', 'title': 'Edit Event Size Distribution', 'width': 1600, 'height': 600}}, 'classifier_results_section': {'title': 'Classifier Results', 'classifier_results_del': {'plot_path': 'crispector_output/Rag1_79/classifier_results_by_position_del.png', 'pdf_path': 'crispector_output/Rag1_79/classifier_results_by_position_del.pdf', 'title': 'deletions', 'width': 2400, 'height': 1600}, 'classifier_results_ins': {'plot_path': 'crispector_output/Rag1_79/classifier_results_by_position_ins.png', 'pdf_path': 'crispector_output/Rag1_79/classifier_results_by_position_ins.pdf', 'title': 'Insertions', 'width': 2400, 'height': 1600}, 'classifier_results_mix': {'plot_path': 'crispector_output/Rag1_79/classifier_results_by_position_mix_and_sub.png', 'pdf_path': 'crispector_output/Rag1_79/classifier_results_by_position_mix_and_sub.pdf', 'title': 'Mixed & Substitutions', 'width': 2400, 'height': 1600}}, 'read_section': {'title': 'Reads', 'edited_reads': 'crispector_output/Rag1_79/edited_reads_table.html', 'treatment_aligned_reads': 'crispector_output/Rag1_79/treatment_aligned_reads.csv.gz', 'mock_aligned_reads': 'crispector_output/Rag1_79/mock_aligned_reads.csv.gz'}}, 'Rag1_83': {'title': 'Rag1_83', 'editing_activity': {'plot_path': 'crispector_output/Rag1_83/site_editing_activity.png', 'pdf_path': 'crispector_output/Rag1_83/site_editing_activity.pdf', 'title': 'Editing Activity', 'width': 800, 'height': 800}, 'modification_section': {'title': 'Modifications', 'edit_distribution': {'plot_path': 'crispector_output/Rag1_83/distribution_of_edit_events.png', 'pdf_path': 'crispector_output/Rag1_83/distribution_of_edit_events.pdf', 'title': 'Edited Events Distribution', 'width': 1600, 'height': 900}, 'modification_distribution': {'plot_path': 'crispector_output/Rag1_83/distribution_of_all_modifications.png', 'pdf_path': 'crispector_output/Rag1_83/distribution_of_all_modifications.pdf', 'title': 'All Modifications Distribution', 'width': 3200, 'height': 1800}, 'edit_size_distribution': {'plot_path': 'crispector_output/Rag1_83/distribution_of_edit_events_size.png', 'pdf_path': 'crispector_output/Rag1_83/distribution_of_edit_events_size.pdf', 'title': 'Edit Event Size Distribution', 'width': 1600, 'height': 600}}, 'classifier_results_section': {'title': 'Classifier Results', 'classifier_results_del': {'plot_path': 'crispector_output/Rag1_83/classifier_results_by_position_del.png', 'pdf_path': 'crispector_output/Rag1_83/classifier_results_by_position_del.pdf', 'title': 'deletions', 'width': 2400, 'height': 1600}, 'classifier_results_ins': {'plot_path': 'crispector_output/Rag1_83/classifier_results_by_position_ins.png', 'pdf_path': 'crispector_output/Rag1_83/classifier_results_by_position_ins.pdf', 'title': 'Insertions', 'width': 2400, 'height': 1600}, 'classifier_results_mix': {'plot_path': 'crispector_output/Rag1_83/classifier_results_by_position_mix_and_sub.png', 'pdf_path': 'crispector_output/Rag1_83/classifier_results_by_position_mix_and_sub.pdf', 'title': 'Mixed & Substitutions', 'width': 2400, 'height': 1600}}, 'read_section': {'title': 'Reads', 'edited_reads': 'crispector_output/Rag1_83/edited_reads_table.html', 'treatment_aligned_reads': 'crispector_output/Rag1_83/treatment_aligned_reads.csv.gz', 'mock_aligned_reads': 'crispector_output/Rag1_83/mock_aligned_reads.csv.gz'}}}

    #report_output = "crispector_output/"
    #with open(os.path.join(report_output, "crispector_output/exp_param_d.pkl"), "rb") as file:
    #    exp_param_d = pickle.load(file)

    #site_output = "crispector_output/"
    #with open(os.path.join(site_output, "crispector_output/site_param_d.pkl"), "rb") as file_site:
    #    site_param_d = pickle.load(file_site)
    #    print(site_param_d)

    create_final_html_report(exp_param_d, site_param_d)

if __name__ == '__main__':
    main()