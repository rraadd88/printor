#!usr/bin/python

# Copyright 2018, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

import sys
from os.path import exists,splitext,dirname,splitext,basename
from os import makedirs
import argparse
import pkg_resources
import logging

from os.path import exists,abspath,basename,dirname,splitext
from os import makedirs,system
import re

from IPython import nbformat
import sys
import io
import os

# GET INPTS    
def main():
    """
    DOES STUFF
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("fp", help="path to project directory", 
                        action="store", default=False)    
    parser.add_argument("--title", help="", dest='title',
                        action="store", default=None)  

    
    args = parser.parse_args()
    logging.info("start")
    slides2pdf(fp=args.fp,title=args.title)

def copyfilechangesrc(src):
    possini=[m.start()+2 for m in re.finditer(']\(', src)]
    possend=[m.start() for m in re.finditer('\)', src)]

    possiniend=[]
    for posini in possini:
        for posend in possend:
            if posend>posini:
                possiniend.append((posini,posend))
                break
    #         break
    #     break

    fps=[]
    for pini,pend in possiniend:
        fp=src[pini:pend]
        if exists(fp):
#             print(fp)
            fps.append(fp)
        else:
            print('ERROR: {}'.format(fp))

    for fp in fps:
        fp_=fp
        if ('.svg' in fp) or ('.pdf' in fp):
            system('convert -density 300 {} {}'.format(fp,fp+'.png'))
            fp_=fp+'.png'
        fpdest='figs/'+abspath(fp_).split('/prjs/')[1]
        if not exists(fpdest):
            makedirs(dirname(fpdest), exist_ok=True)
            system('cp {} {}'.format(fp_,fpdest))
#         print(fp,fpdest)
        src=src.replace(fp,fpdest)
    return src

def cleanslideshtml(fp):
    import bs4
    # load the file
    with open(fp) as f:
        soup = bs4.BeautifulSoup(f.read(),features="html5lib")
    for div in soup.findAll('div', class_="input"): 
        div.decompose()
    for div in soup.findAll('div', class_="prompt output_prompt"): 
        div.decompose()
    with open(f"{fp}.cleaned.html", "w") as outf:
        print(f"{fp}.cleaned.html")
        outf.write(str(soup))

def slides2pdf(fp,title=None,test=False):       
#    fp='group_meet_gened_b180605_v02_pdf_friendly.ipynb'
    nb=nbformat.read(fp,as_version=nbformat.NO_CONVERT)
    cells=[]
    for cell in nb.cells:
        if cell['metadata']!={}:
            if 'slideshow' in cell['metadata']:
                if cell['metadata']['slideshow']['slide_type']!="skip":
                    if cell['cell_type']=='markdown':
                        if 'source' in cell:
                            if '](' in cell['source']:
                                src=cell['source']
                                cell['source']=copyfilechangesrc(src)
                                if test:
                                    if 'gene_exp_estradiol/sys.png' in src:
                                        print(src)
                                        print('\n')
                                        print(copyfilechangesrc(src))
                    #                     break
                    if cell['cell_type']=='code':
                        if 'source' in cell: 
#                             print(cell['source'].keys())
                            cell['source']=''
#                             del cell['source']
                    cells.append(cell)
            #             break
    # remo
    cells_=[]
    for cell in cells:
        if 'source' in cell:
            if not (('thank you for your kind attention' in cell['source']) or ('#### Rohan Dandage'  in cell['source'])):
                cells_.append(cell) 
        else:
            cells_.append(cell) 

    #     break
    nb['cells']=cells_
#     import datetime
    
    # if title is None:
    #     fpout=fp+'.slides2.pdf'
    # else:
    #     fpout='{}_{}.ipynb'.format(datetime.datetime.today().strftime('%y%m%d'),title.replace(' ','_'))
    fpout=f"{fp}.cleaned.ipynb"
    nbformat.write(nb,fpout)
    system(f"source activate pre; jupyter nbconvert {fpout} --to slides --reveal-prefix reveal.js-3.1.0")
    cleanslideshtml(fp=f"{splitext(fpout)[0]}.slides.html")
    system(f"source activate pre; jupyter nbconvert {fpout} --to html")
    cleanslideshtml(fp=f"{splitext(fpout)[0]}.html")
    system(f"wkhtmltopdf {splitext(fpout)[0]}.html.cleaned.html {splitext(fpout)[0]}.html.cleaned.html.pdf")
    logging.shutdown()

if __name__ == '__main__':
    main()
