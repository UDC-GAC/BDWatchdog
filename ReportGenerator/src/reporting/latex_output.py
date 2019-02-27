#!/usr/bin/env python


def print_latex_section(section_name, section_label=None):
    if not section_label:
        section_label = section_name.replace(" ", "_")
    print("\\section{" + section_name + "}\label{" + section_label + "}")
    print("")


# def print_latex_vertical_space():
#     print("\\vspace{-0.3cm}")
#     print("")


def print_latex_stress(s):
    # Print the \newline string so that it is detected as a Latex newline
    # print(str + "\\newline")
    # print two additional spaces so that it is detected by markdown and pandoc as a newline
    print("\\textbf{" + s + "}" + "  ")
    print("")


def latex_print(s):
    # Print the \newline string so that it is detected as a Latex newline
    # print(str + "\\newline")
    # print two additional spaces so that it is detected by markdown and pandoc as a newline
    print(s + "  ")
    print("")
