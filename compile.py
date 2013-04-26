#!/usr/bin/python
# -*- coding: utf8
import sys, os, re

BLIST = { '*' : r"\begin{itemize}", '#' : r"\begin{enumerate}" }
ELIST = { '*' : r"\end{itemize}", '#' : r"\end{enumerate}" }

BCOMMENT = "<<comment"
ECOMMENT = "comment>>"
BPYTHON = "<<python"
EPYTHON = "python>>"

def next():
    global L, l, ls, i
    i += 1
    if i < len(L):
        l = L[i]
        ls = l.strip()
    else:
        l, ls = '', ''

def digit(c): return c in '0123456789'

def parse_fig(s):
    if s.find('|') == -1:
        caption = ''
    else:
        s, caption = s.split('|',2)
    s = s.strip()
    if s and s[-1] == ')':
        p = s.rfind('(')
        figure = s[:p]
        scale = s[p+1:-1]
        if scale.find('=') == -1:
            if scale[0] == 'w':
                scale = 'width='+scale[1:] + (r'\textwidth' if digit(scale[-1]) else '')
            elif scale[0] == 'h':
                scale = 'height='+scale[1:] + (r'\textheight' if digit(scale[-1]) else '')
            elif scale[0] == 's':
                scale = 'scale='+scale[1:]
    else:
        figure = s
        scale = r"height=0.6\textheight"
    return r"\includegraphics["+scale+"]{" + figure + "}", caption

def item_line(ls):
    return ls and (ls[0] in '*#' or ls[:2] in ('-*','-#'))

def replace_all(text, rl):
    for i, j in rl:
        text = text.replace(i, j)
    return text

def subst(l):
  return replace_all(l, [('<--->', r'$\longleftrightarrow$'), ('--->', r'$\longrightarrow$'), ('<---', r'$\longleftarrow$'),
                         ('<-->', r'$\leftrightarrow$'), ('-->', r'$\to$'), ('<--', r'$\gets$'),
                         #('~~>', r'$\to$'),
                         ('<===>', r'$\Longleftrightarrow$'), ('===>', r'$\Longrightarrow$'), ('<===', r'$\Longleftarrow$'),
                         ('<==>', r'$\Leftrightarrow$'), ('==>', r'$\Rightarrow$'), ('<==', r'$\Leftarrow$'),
                         (':-)', r'\smiley{}'), (':-(', r'\frownie{}')])

OPTIONS_RE = re.compile(r"(((\[[^\]]*\])|({[^}]*}))*)([^\[{].*)")
def option_list(l):
    M = OPTIONS_RE.match(l+' ')
    return M.group(1), M.group(5) # options & rest of the line

if len(sys.argv) < 2:
    fn = raw_input("Input file:")
else:
    fn = sys.argv[1]
f = open(fn, 'r')
sys.stdout = open(fn+'.tex', 'w')
stderr = sys.stderr

SINGLE_SLIDE = False

L = []
ENV = {}
line = f.readline()
while len(line) > 0:
    if line[:4] == '!===':
        L = L[:4]
        line = line[1:]
        SINGLE_SLIDE = True
        L.append(line)
        line = f.readline()
    elif SINGLE_SLIDE and line[:3] == '===':
        break
    elif line[:len(BPYTHON)] == BPYTHON:
        line = f.readline()
        P = ""
        ENV['R'] = ''
        while line and line[:len(EPYTHON)] != EPYTHON:
            P += line
            line = f.readline()
        exec P in ENV
        L.extend(ENV['R'].split('\n'))
        line = f.readline()
    else:
        L.append(line)
        line = f.readline()
f.close()
L.append(r"\bye")

i, l, ls = -1, '', ''
next()
title = ls
next()
author = ls
next()
inst = ls
next()
date = ls
next()

#\documentclass[english]{beamer}
print r"""
\documentclass[slovak]{beamer}
\usepackage[utf8]{inputenc}
\usepackage[slovak]{babel}
\usepackage{graphicx, subfigure, amssymb, wasysym, amsmath, mathptmx}

\usetheme{Warsaw}
\setbeamercovered{transparent}
\setbeamertemplate{footline}[page number] 

\newtheorem{veta}{Veta}[section]
\newtheorem{lema}{Lema}[section]
\newtheorem{dosl}{Dôsledok}[section]
\newtheorem{df}{Definícia}[section]
\newtheorem{probl}{Problém}[section]
\newtheorem{otv}{Otvorený problém}[section]
\makeatletter
\newenvironment<>{proofs}[1][\proofname]%%
  {\par\def\insertproofname{#1\@addpunct{.}}%%
   \usebeamertemplate{proof begin}#2}
  {\usebeamertemplate{proof end}}
\newenvironment<>{proofc}[1][\proofname]%%
  {\par\pushQED{\qed}\def\insertproofname{#1 (pokračovanie)\@addpunct{.}}%%
   \usebeamertemplate{proof begin}#2}
  {\usebeamertemplate{proof end}}
\newenvironment<>{proofe}[1][\proofname]%%
  {\par\pushQED{\qed}\def\insertproofname{#1 (pokračovanie)\@addpunct{.}}%%
  %%{\par\pushQED{\qed}\setbeamertemplate{proof begin}{\begin{block}{}}
   \usebeamertemplate{proof begin}#2}
  {\popQED\usebeamertemplate{proof end}}
\makeatother

\def\N{\mathbb{N}}
\def\Z{\mathbb{Z}}
\def\Q{\mathbb{Q}}
\def\R{\mathbb{R}}
\def\C{\mathbb{C}}
\def\F{\mathbb{F}}
\def\Prv{\mathbb{P}}
\def\E{\mathop{\mathsf{E}}}

\begin{document}

\catcode`\"=\active
\def "{\begingroup\clqq\def "{\endgroup\crqq}}

\title{%s}
\author{%s}
\institute{%s}
\date{%s}
\frame{\maketitle}
""" % (title, author, inst, date)


nframes = 0
in_list = False
list_index, list_type = [-1], ['x']

# TODO: header
# TODO: adresar na figures
# TODO: subfigures, labels ?
# TODO: in text abbr. poriadne
# TODO: tabulky - separator
# TODO: proof
# TODO: zakomentovanie
# TODO: krajsi vystupny .tex
# TODO: \item[blah] nejak konzistentnejsie
# TODO: \begin{block}{title} ... \end{block}
# TODO: (((footnote))) ?
# TODO: <<env[opt]  .... env>> ...ako presne zistim, co je env?
# TODO: code listings / pseudocode
while i < len(L):
    if in_list:
        if item_line(ls):
            pause = ""
            if ls[0] == '-':
                pause = r"\pause"
                ls = ls[1:]
                l = l[:l.find('-')] + ls
            j = l.find(ls[0])
            if j > list_index[-1]:
                print (list_index[-1]+2)*' ',
                list_index.append(j)
                list_type.append(ls[0])
                print BLIST[ls[0]]
            elif j < list_index[-1]:
                while j < list_index[-1]:
                    list_index.pop()
                    print (list_index[-1]+1)*' ',
                    print ELIST[list_type.pop()]
                if j != list_index[-1]:
                    print >>stderr, 'ERROR [line %d]: bad indentation in list' % i
                    print >>stderr, L[i-2], L[i-1], L[i], L[i+1], L[i+2]
                    sys.exit(0)
            print (list_index[-1]+2)*' ' + pause + r"\item",
            l = ls[1:]
            ls = l.strip()
            o, l = option_list(l)
            print subst(o),
            ls = l.strip()
            #f l and l[0] == '[':
            #   print l[:l.find(']')+1]
            #   l = l[l.find(']')+1:]
            #   ls = l.strip()
        elif not l or l[0] != ' ':
            in_list = False
            while len(list_type) > 1:
                print ELIST[list_type.pop()]
            list_index = [-1]
        else:
            print (list_index[-1]+6)*' ',

    if not ls:
        print
        next()
    elif ls[:4] == r'\bye':
        break
    elif ls[:3] == '===' and (len(ls)<=3 or ls[3] != '>'):
        if nframes > 0:
            print r"\end{frame}" + "\n\n%"+40*'-'+"\n"
        print r"\begin{frame}\frametitle{%s}" % ls.strip('= ')
        nframes += 1
        next()
    elif ls[:3] == '---':
        print r"\pause"
        next()
    elif item_line(ls):
        in_list = True
        continue
    elif ls[0] == '[':
        pos = ls.rfind(']')
        if pos == -1: # subfigures...
            print r"\begin{figure}"
            next()
            while ls[0] != ']' and ls[0] != '|':
                if ls[0] == '[':
                    figure, caption = parse_fig(ls[1:ls.rfind(']')])
                    if caption != '': caption = '[' + caption + ']'
                    print r"  \subfigure" + caption + "{" + figure + r"}"
                else:
                    print ls
                next()
            if ls[0] == '|':
                _, caption = parse_fig(ls[:-1])
                print r"  \caption{" + caption + "}"
            # caption
            print r"\end{figure}"
            next()
        else:
            figure, caption = parse_fig(ls[1:pos])
            if caption != '': caption = r"\caption{" + caption + "}"
            print r"\begin{figure}" + figure + caption + r"\end{figure}"
            next()
    elif ls[:7] == "<<table":
        print r"$$\begin{tabular}{" + ls[7:] + "}"
        next()
        while ls[:7] != "table>>":
            if ls[:3] == '---': print r"\hline"
            else: print ' & '.join(ls.split()), r'\\'
            next()
        print r"\end{tabular}$$"
        next()
    elif ls[:len(BCOMMENT)] == BCOMMENT:
        while ls[:len(ECOMMENT)] != ECOMMENT and l!=r"\bye": next()
        next()
    #elif ls[:2] == "<<proof":
    else:
        print subst(ls)
        next()

print r"""
\end{frame}
\end{document}
"""

sys.stdout.close()
os.system("pdfcslatex %s.tex" % fn)
