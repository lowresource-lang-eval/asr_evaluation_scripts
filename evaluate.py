#!/usr/bin/python
# -*- coding: utf-8 -*
import sys
import os
import subprocess



USAGE_EXAMPLE = 'usage: evaluate <test files path> <golden file path>'
DELIMITER = '\t'
LANGUAGE_UNKNOWN = 'X'


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('python-Levenshtein')
import Levenshtein


def main():

    if len(sys.argv) < 3:
        print(USAGE_EXAMPLE)
        return

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    submit_dir = os.path.join(input_dir, 'res')
    truth_dir = os.path.join(input_dir, 'ref')

    if not os.path.isdir(submit_dir):
        raise Exception("%s doesn't exist" % submit_dir)

    if not os.path.isdir(truth_dir):
        raise Exception("%s doesn't exist" % truth_dir)

    if not os.path.exists(output_dir):
         os.makedirs(output_dir)

    filename_task1 = os.path.join(submit_dir, 'input_task1.tsv')
    filename_task2 = os.path.join(submit_dir, 'input_task2.tsv')
    filename_task3 = os.path.join(submit_dir, 'input_task3.tsv')
    filename_task4 = os.path.join(submit_dir, 'input_task4.tsv')
    filename_golden_main1 = os.path.join(truth_dir, 'test.tsv')
    filename_golden_main2 = os.path.join(truth_dir, 'test.tsv')
    filename_golden_main3 = os.path.join(truth_dir, 'ortho_test.tsv')
    filename_golden_main4 = os.path.join(truth_dir, 'speakers_test.tsv')
    filename_results = os.path.join(output_dir, 'scores.txt')

    if not os.path.exists(filename_golden_main1):
        raise Exception(filename_golden_main1 + ' does not exist. ' + USAGE_EXAMPLE)

    if not os.path.exists(filename_golden_main2):
        raise Exception(filename_golden_main2 + ' does not exist. ' + USAGE_EXAMPLE)

    if not os.path.exists(filename_golden_main3):
        raise Exception(filename_golden_main3 + ' does not exist. ' + USAGE_EXAMPLE)

    with open(filename_results, 'w', encoding='utf-8', newline='') as fout:
        fout.write('')

    if not os.path.exists(filename_task1) \
            and not os.path.exists(filename_task2) \
            and not os.path.exists(filename_task3) \
            and not os.path.exists(filename_task4):
        raise Exception('No input files: ' + USAGE_EXAMPLE)

    if os.path.exists(filename_task1):
        try:
            test_data = read_file(filename_task1)
            golden_data = read_file(filename_golden_main1)
        except Exception as e:
            print(e)
            return
        process_task_language_detection(filename_results, test_data, golden_data, input_dir)
    else:
        with open(filename_results, 'a', encoding='utf-8', newline='') as fout:
            fout.write('language_total: -1\n')
            fout.write('group_total: -1\n')
            fout.write('family_total: -1\n')

            fout.write('language_known: -1\n')
            fout.write('group_known: -1\n')
            fout.write('family_known: -1\n')

    if os.path.exists(filename_task2):
        try:
            test_data2 = read_file(filename_task2)
            golden_data2 = read_file(filename_golden_main2)
        except Exception as e:
            print(e)
            return
        process_task_transcription(filename_results, test_data2, golden_data2, input_dir, 'IPA')
    else:
        with open(filename_results, 'a', encoding='utf-8', newline='') as fout:
            fout.write('character_error_rateIPA: -1\n')

    if os.path.exists(filename_task3):
        try:
            test_data3 = read_file(filename_task3)
            golden_data3 = read_file(filename_golden_main3)
        except Exception as e:
            print(e)
            return
        process_task_transcription(filename_results, test_data3, golden_data3, input_dir, 'ortho')
    else:
        with open(filename_results, 'a', encoding='utf-8', newline='') as fout:
            fout.write('character_error_rateortho: -1\n')

    if os.path.exists(filename_task4):
        try:
            test_data4 = read_file(filename_task4)
            golden_data4 = read_file(filename_golden_main4)
        except Exception as e:
            print(e)
            return
        process_task_num_speakers(filename_results, test_data4, golden_data4, input_dir)
    else:
        with open(filename_results, 'a', encoding='utf-8', newline='') as fout:
            fout.write('num_speakers: -1\n')


def process_task_language_detection(filename_results, test_data, golden_data, input_dir):
    results, errors = evaluate_language_detection(test_data, golden_data)
    with open(filename_results, 'a', encoding='utf-8', newline='') as fout:
        if errors:
            fout.write('ERRORS\n')
            for error in errors:
                fout.write(error + '\n')
        else:
            fout.write('language_total: %s\n' %  results['language_total'])
            fout.write('group_total: %s\n' % results['group_total'])
            fout.write('family_total: %s\n' % results['family_total'])

            fout.write('language_known: %s\n' % results['language_known'])
            fout.write('group_known: %s\n' % results['group_known'])
            fout.write('family_known: %s\n' % results['family_known'])

            if 'language_surprise' in results:
                fout.write('language_surprise: %s\n' % results['language_surprise'])
                fout.write('group_surprise: %s\n' % results['group_surprise'])
                fout.write('family_surprise: %s\n' % results['family_surprise'])


def process_task_transcription(filename_results, test_data, golden_data, input_dir, mode):
    results, errors = evaluate_transcription(test_data, golden_data, mode)
    with open(filename_results, 'a', encoding='utf-8', newline='') as fout:
        if errors:
            fout.write('ERRORS\n')
            for error in errors:
                fout.write(error + '\n')
        else:
            if 'character_error_rate'+mode not in results:
                raise Exception('no character_error_rate in results')
            fout.write('character_error_rate' + mode + ': %s\n' % results['character_error_rate'+mode])


def process_task_num_speakers(filename_results, test_data, golden_data, input_dir):
    results, errors = evaluate_num_speakers(test_data, golden_data)
    with open(filename_results, 'a', encoding='utf-8', newline='') as fout:
        if errors:
            fout.write('ERRORS\n')
            for error in errors:
                fout.write(error + '\n')
        else:
            fout.write('num_speakers_accuracy: %s\n' % results['num_speakers_accuracy'])


def evaluate_language_detection(test_data, golden_data):
    results = []
    errors = []
    total = len(golden_data)
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


def evaluate_transcription(test_data, golden_data, mode):
    results = dict()
    errors = []
    total = len(golden_data)

    if total != len(golden_data):
        errors.append('The test data length (%s) does not match the golden data length (%s)' %
                      (len(test_data), len(golden_data)))
        return results, errors

    cer_total = 0

    for i, (test_data_part, golden_data_part) in enumerate(zip(test_data, golden_data)):
        test_id = test_data_part['id']
        golden_id = golden_data_part['id']
        if test_id != golden_id:
            errors.append('Line %s: utterance ids do not match (%s and %s)' % (i, test_id, golden_id))
        elif test_data_part['text'].strip() == '':
            errors.append('Line %s: empty test' % (i))
        else:
            test_text = test_data_part['text'].strip()
            golden_text = golden_data_part['text'].strip()
            distance = Levenshtein.distance(test_text, golden_text)
            distance_averaged = distance / len(test_text)
            cer_total += distance_averaged

    cer_total = cer_total / len(golden_data)
    results['character_error_rate' + mode] = cer_total
    return results, errors


def evaluate_num_speakers(test_data, golden_data):
    results = []
    errors = []
    total = len(golden_data)
    correct_number = 0

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
            test_num_speakers = test_data_part.get('num_speakers')
            golden_num_speakers = golden_data_part.get('num_speakers')
            if test_num_speakers is None:
                errors.append('Line %s (id %s): empty num_speakers' % (i, test_id))
            elif test_num_speakers == golden_num_speakers:
                correct_number += 1

    num_speakers_accuracy = correct_number / total

    results = {'num_speakers_accuracy' : num_speakers_accuracy,}
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
                file_data_part = {'id': line_parts[0],
                                  'text': line_parts[1],
                                  'language': line_parts[2],
                                  'group': line_parts[3],
                                  'family': line_parts[4]
                                  }

                if len(line_parts) >= 6:
                    file_data_part['probably_repeating'] = line_parts[5]
                    if len(line_parts) >= 7:
                        file_data_part['probably_stimulus'] = line_parts[6]
                        if len(line_parts) >= 8:
                            file_data_part['num_speakers'] = line_parts[7]
                file_data.append(file_data_part)

    if erroneous_lines:
        raise Exception('Errors when reading ' + filename +
                        ' : wrong number of parts in line(s): ' +
                        ','.join(erroneous_lines))
    return file_data



if __name__ == "__main__":
    main()