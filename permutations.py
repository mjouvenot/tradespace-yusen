# Let's assume the csv rows are structured as decision,choice,choice,choice,etc.
import itertools
import csv


def check_feasible(option_dict):
    """
    Check if a combination (given as a dict) is feasible
    :param option_dict: 
    :return: boolean (True if feasible, False if not) 
    """

    unfeasible_combinations = []
    unfeasible_combinations += [{'Interfaces': 'Proprietary', 'Marketplace Transparency': 'Open'}]
    unfeasible_combinations += [{'Trading Platform Enrollment': 'No restriction', 'Marketplace Transparency': 'Closed'}]

    for unfeasible in unfeasible_combinations:
        is_unfeasible = True
        for key, value in unfeasible.items():
            is_unfeasible = is_unfeasible and key in option_dict and option_dict[key] == value
        if is_unfeasible:
            print('unfeasible because of {0}: {1}'.format(unfeasible, option_dict))
            return False

    return True


def extract_morphological_matrix(input_file_name):
    """
    Extract the elements of a morphological matrix from a csv file
    :param input_file_name: 
    :return: tuple (list: row names, list: matrix)
    """
    matrix = []
    columns = []
    with open(input_file_name,"r") as morph_matrix:
        for row in morph_matrix:
            print(row)
            row = row.strip('\n').strip("\r")
            fields = row.split(",")
            print(fields)
            matrix.append([fields[i] for i in range(1, len(fields))])
            columns.append(fields[0])

    return columns, matrix


def generate_permutations(col_names, matrix):
    """
    Generator of all possible concepts
    :param col_names: 
    :param matrix: 
    :return: iterator on list of dict (concepts)
    """
    permutations = list(itertools.product(*matrix))

    for option in permutations:
        concept = dict((col_names[i], option[i]) for i in range(len(option)))
        if check_feasible(concept):
            yield concept


def generate_and_export_permutations(input_filename, output_filename):
    with open(output_filename, "w") as concepts:
        (attributes, design_choices) = extract_morphological_matrix(input_filename)
        writer = csv.DictWriter(f=concepts, fieldnames=attributes)
        # write in output file
        writer.writerow(dict((attribute, attribute) for attribute in attributes))
        for element in generate_permutations(attributes, design_choices):
            writer.writerow(element)


if __name__ == "__main__":
    generate_and_export_permutations("morph_matrix.csv", "concepts.csv")
