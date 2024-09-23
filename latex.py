def generate_latex(project_name, description, photos):
    #photos_list = photos.rsplit(',')
    photos_str = '\n'.join(
        [f'\\includegraphics[width=0.8\\textwidth]{{static/photos/{photo.strip()}}} \\\\' for photo in photos])

    latex_code = f"""
\\documentclass[a4paper,12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{graphicx}}
\\usepackage{{fancyhdr}}
\\usepackage{{lipsum}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{Проект: {project_name}}}
\\fancyfoot[C]{{Страница \\thepage}}

\\begin{{document}}

\\begin{{center}}
    \\huge \\textbf{{{project_name}}} \\\\
    \\vspace{{0.5cm}}
    \\large \\textit{{Описание}} \\\\
    \\vspace{{0.5cm}}
    {description} \\\\
\\end{{center}}

\\vspace{{1cm}}

\\begin{{center}}
    \\textbf{{Фотографии}}:
    \\begin{{figure}}[h]
        \\centering
        {photos_str}
    \\end{{figure}}
\\end{{center}}

\\vspace{{1cm}}

\\begin{{center}}
    \\textit{{Сделано в сотрудничестве с жителями города.}}
\\end{{center}}

\\end{{document}}
"""

    return latex_code
