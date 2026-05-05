import os

css_path = r'd:\Projects\bao-cao-cuoi-ki-lab-10\5-visualization\assets\custom.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

css = css.replace('--bg-primary:    #0f0a04;', '--bg-primary:    #030b14;')
css = css.replace('--bg-secondary:  #1a1208;', '--bg-secondary:  #08172b;')
css = css.replace('--bg-card:       #221709;', '--bg-card:       #0d213b;')
css = css.replace('--bg-hover:      #2d1f0a;', '--bg-hover:      #132c4d;')
css = css.replace('--text-primary:  #f5dcb8;', '--text-primary:  #e0f2fe;')
css = css.replace('--text-secondary:#c4a882;', '--text-secondary:#bae6fd;')
css = css.replace('--text-muted:    #8a7258;', '--text-muted:    #7dd3fc;')
css = css.replace('--text-accent:   #fbbf24;', '--text-accent:   #38bdf8;')
css = css.replace('--gold-primary:  #f59e0b;', '--gold-primary:  #0ea5e9;')
css = css.replace('--gold-dark:     #d97706;', '--gold-dark:     #0284c7;')
css = css.replace('--brown-primary: #c4822d;', '--brown-primary: #0284c7;')
css = css.replace('--border:        rgba(196, 130, 45, 0.25);', '--border:        rgba(14, 165, 233, 0.25);')
css = css.replace('--shadow-card:   0 4px 16px rgba(138, 83, 27, 0.15);', '--shadow-card:   0 4px 16px rgba(2, 132, 199, 0.15);')
css = css.replace('#2d1f0a 0%, #0f0a04 65%', '#08172b 0%, #030b14 65%')
css = css.replace('#d49c59', '#38bdf8')
css = css.replace('background: #221709', 'background: #0d213b')
css = css.replace('196, 130, 45', '14, 165, 233')
css = css.replace('138, 83, 27', '2, 132, 199')
css = css.replace('245, 158, 11', '14, 165, 233')
css = css.replace('linear-gradient(135deg, #f59e0b 0%, #d97706 60%, #c4822d 100%)', 'linear-gradient(135deg, #38bdf8 0%, #0ea5e9 60%, #0284c7 100%)')

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

py_path = r'd:\Projects\bao-cao-cuoi-ki-lab-10\5-visualization\layouts\main_layout.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

py = py.replace('"bg_main": "#0f0a04"', '"bg_main": "#030b14"')
py = py.replace('"bg_card": "#221709"', '"bg_card": "#0d213b"')
py = py.replace('"text_main": "#f5dcb8"', '"text_main": "#e0f2fe"')
py = py.replace('"text_secondary": "#c4a882"', '"text_secondary": "#bae6fd"')
py = py.replace('"text_muted": "#8a7258"', '"text_muted": "#7dd3fc"')
py = py.replace('"gold": "#f59e0b"', '"gold": "#38bdf8"')
py = py.replace('"brown": "#c4822d"', '"brown": "#0284c7"')
py = py.replace('"border": "rgba(196, 130, 45, 0.25)"', '"border": "rgba(14, 165, 233, 0.25)"')
py = py.replace('rgba(196, 130, 45', 'rgba(14, 165, 233')
py = py.replace('rgba(15, 10, 4', 'rgba(3, 11, 20')

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py)

print('Colors updated successfully')
