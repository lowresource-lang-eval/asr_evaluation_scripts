#!/usr/bin/python
# -*- coding: utf-8 -*
import sys
import os

USAGE_EXAMPLE = 'usage: evaluate <task N> <test path> <golden file path>'
DELIMITER = '\t'
LANGUAGE_UNKNOWN = 'X'


def main():
    if len(sys.argv) < 4:
        print(USAGE_EXAMPLE)
        return
    if not sys.argv[1].isnumeric():
        print(USAGE_EXAMPLE)
        return
    task_number = int(sys.argv[1])
    filename_test = sys.argv[2]
    filename_golden = sys.argv[3]
    filename_results = filename_test + '_out.txt'
    if not os.path.exists(filename_test):
        print(filename_test + ' does not exist. ' + USAGE_EXAMPLE)
        return
    if not os.path.exists(filename_golden):
        print(filename_golden + ' does not exist. ' + USAGE_EXAMPLE)
        return
    try:
        test_data = read_file(filename_test)
        golden_data = read_file(filename_golden)
    except Exception as e:
        print(e)
        return
    if task_number == 1:
        process_task_language_detection(filename_results, test_data, golden_data)
        print('Written results to ' + filename_results)
    #TODO
    else:
        print('Unknown task number ' + str(task_number) + '. ' + USAGE_EXAMPLE)
        return

    #TODO

def process_task_language_detection(filename_results, test_data, golden_data):
    results, errors = evaluate_language_detection(test_data, golden_data)
    with open(filename_results, 'w', encoding='utf-8', newline='') as fout:
        if errors:
            fout.write('ERRORS\n')
            for error in errors:
                fout.write(error + '\n')
        else:
            fout.write('language total: %s\n' %  results['language_total'])
            fout.write('group total: %s\n' % results['group_total'])
            fout.write('family total: %s\n' % results['family_total'])

            fout.write('language known: %s\n' % results['language_known'])
            fout.write('group known: %s\n' % results['group_known'])
            fout.write('family known: %s\n' % results['family_known'])

            if 'language_surprise' in results:
                fout.write('language surprise: %s\n' % results['language_surprise'])
                fout.write('group surprise: %s\n' % results['group_surprise'])
                fout.write('family surprise: %s\n' % results['family_surprise'])


def evaluate_language_detection(test_data, golden_data):
    results = []
    errors = []
    total = len(test_data)
    total_surprise = 0

    language_correct_known = 0
    language_correct_surprise = 0

    group_correct_known = 0
    group_correct_surprise = 0

    family_correct_known = 0
    family_correct_surprise = 0

    if total != len(golden_data):
        errors.append('The test data length (%s) does not match the golden data length (%s)' %
                      (len(test_data), len(golden_data)))
        return results, errors

    for i, (test_data_part, golden_data_part) in enumerate(zip(test_data, golden_data)):
        test_id = test_data_part['id']
        golden_id = golden_data_part['id']
        if test_id != golden_id:
            errors.append('Line %s: utterance ids do not match (%s and %s)' % (i, test_id, golden_id))
        else:
            test_language = test_data_part['language']
            test_group = test_data_part['group']
            test_family = test_data_part['family']

            golden_language = golden_data_part['language']
            golden_group = golden_data_part['group']
            golden_family = golden_data_part['family']


            #we only check the lower levels of the hierarchy when the higher levels have been checked
            if golden_language == LANGUAGE_UNKNOWN:
                total_surprise += 1
                if test_family == golden_family:
                    family_correct_surprise += 1
                    if test_group == golden_group:
                        group_correct_surprise += 1
                        if test_language == golden_language:
                            language_correct_surprise += 1
            else:
                if test_family == golden_family:
                    family_correct_known += 1
                    if test_group == golden_group:
                        group_correct_known += 1
                        if test_language == golden_language:
                            language_correct_known += 1





    total_known = total - total_surprise

    language_total_correct = language_correct_surprise + language_correct_known
    group_total_correct = group_correct_surprise + group_correct_known
    family_total_correct = family_correct_surprise + family_correct_known




    results = {'language_total' : language_total_correct / total,
               'group_total': group_total_correct / total,
               'family_total': family_total_correct / total,

               'language_known': language_correct_known / total_known,
               'group_known': group_correct_known / total_known,
               'family_known': family_correct_known / total_known,
               }

    if total_surprise > 0:
        results.update({'language_surprise': language_correct_surprise / total_surprise,
               'group_surprise': group_correct_surprise / total_surprise,
               'family_surprise': family_correct_surprise / total_surprise})
    return results, errors


def read_file(filename):
    erroneous_lines = []
    file_data = []
    with open(filename, 'r', encoding='utf-8') as fin:
        for index, line in enumerate(fin):
            if index == 0:
                #the first line is a header
                continue
            line = line.strip()
            line_parts = line.split(DELIMITER)
            if len(line_parts) < 5:
                erroneous_lines.append(str(index))
            else:
                file_data_part = {'id' : line_parts[0],
                                  'text': line_parts[1],
                                  'language': line_parts[2],
                                  'group': line_parts[3],
                                  'family': line_parts[4]
                                  }

                if len(line_parts) >= 6:
                    file_data_part['comment'] = line_parts[5]
                file_data.append(file_data_part)

    if erroneous_lines:
        raise Exception('Errors when reading ' + filename +
                        ' : wrong number of parts in line(s): ' +
                        ','.join(erroneous_lines))
    return file_data


if __name__ == "__main__":
    main()