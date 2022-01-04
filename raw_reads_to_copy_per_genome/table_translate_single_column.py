
# parse input
import argparse

parser = argparse.ArgumentParser(description = "Input specifications ")

parser.add_argument("-i", dest="input_file", required=True, help="input file, single column of template strings", type=str)
parser.add_argument("-c", dest="input_col_obi", required=True, help="input table column to translate, 1-based index", type=int)
parser.add_argument("-d", dest="dictionary_file", required=True, help="dictionary table file, presence of header row is assumed", type=str)
parser.add_argument("-o", dest="output_file", required=True, help="output table of translation(s) from the template column", type=str)
parser.add_argument("--head", dest="input_has_header", required=False, default=False, action="store_true", help="(optional) if input table has header row")
parser.add_argument("--dk", dest="dict_key_obi", required=False, default = 1, help="(optional) 1-based index of the key column in the dictionary table; default = 1", type=int)
parser.add_argument("--dt", dest="dict_trans_obi", required=False, default = 2, help="(optional) 1-based index of the translated values to be put into the output table; default = 2", type=int)
parser.add_argument("--na", dest="na_string", required=False, default = "_ns", help="(optional) translated value for the string not found in the dictionary (default = keep the original value)", type=str)
parser.add_argument("--ex_untranslated", dest="exclude_untranslated_rows", required=False, default = False, action="store_true", help="(optional) use this to remove the rows containing untranslated values from the output")

args = parser.parse_args()

input_file = args.input_file
input_col_obi = args.input_col_obi
dictionary_file = args.dictionary_file
output_file = args.output_file
input_has_header = args.input_has_header
dict_key_obi = args.dict_key_obi
dict_trans_obi = args.dict_trans_obi
na_string = args.na_string
exclude_untranslated_rows = args.exclude_untranslated_rows

input_col_zbi = input_col_obi - 1
dict_key_zbi = dict_key_obi - 1
dict_trans_zbi = dict_trans_obi - 1
untranslated_value_specified = False
if na_string != '_ns':
    untranslated_value_specified = True




# hash memorize the dictionary
dict_trans = {}
fr = open(dictionary_file, "r")
for dline in fr:
    fields = dline.strip().split("\t")
    dict_trans[fields[dict_key_zbi]] = fields[dict_trans_zbi]
fr.close()
print("dictionary hash table size = " + str(len(dict_trans)))


# opening output file 
fw = open(output_file, "w")

# translating w/ writing
count_translated = 0
count_untranslated = 0
fr = open(input_file, "r")
if input_has_header:
    line = fr.readline()
    fw.write(line.strip() + "\n")
for line in fr:
    fields = line.strip().split("\t")
    num_field = len(fields)
    translation_success = False
    target_original = fields[input_col_zbi]
    target_translated = target_original
    if untranslated_value_specified:
        target_translated = na_string
    if target_original in dict_trans:
        target_translated = dict_trans[target_original]
        translation_success = True
        count_translated += 1
    else:
        translation_success = False
        count_untranslated += 1
    #
    if exclude_untranslated_rows and (not translation_success):
        continue
    #
    for col_zbi in range(num_field):
        if col_zbi > 0:
            fw.write("\t")
        original_value = fields[col_zbi]
        translated_value = original_value
        if col_zbi == input_col_zbi:
            translated_value = target_translated
        fw.write(translated_value)
    fw.write("\n")
fr.close()
print("translated templates = " + str(count_translated))
print("untranslated (NA) = " + str(count_untranslated))
# closing output file
fw.close()
