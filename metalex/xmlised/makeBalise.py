#! usr/bin/env python
# coding: utf8

"""
    metalex is general tool for lexicographic and metalexicographic activities
    Copyright (C) 2017  by Elvis MBONING

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
    Contact : levismboning@yahoo.fr
    
    ---------------------------------------------------------------------------
    
    makeBalise transform extracted articles into  well formed xml file.
    It can also generate HTML file for article edition
    
    Packages:
        >>> sudo apt-get install python-html5lib
        >>> sudo apt-get install python-lxml
        >>> sudo apt-get install python-bs4
    
    Usage:
        >>> from metalex.dicXmilised import *
        >>> dicoHtml(save=True)
"""

# ----Internal Modules------------------------------------------------------

import metalex
from composeArticle import *
from dicXmlTool import *

# ----External Modules------------------------------------------------------

import re
import sys
import codecs
import os
from bs4 import BeautifulSoup
from random import sample
from shutil import copyfile
from lxml import etree
from termcolor import colored

# -----Exported Functions-----------------------------------------------------

__all__ = ['BaliseXML', 'dico_html']

# -----Global Variables-----------------------------------------------------

components = {
    u'xml'  :   {
                  u'metalexMetadata'  : [u'metalexMetadata', u'projectName', u'author', u'dateCreation', u'comment', u'contributors', u'candidate'],
                  u'metalexContent'   : [u'article', u'definition', u'example', u'figured', u'contrary',
                                         u'entry', u'flexion', u'category', u'gender', u'rection', u'phonetic',
                                         u'identificationComponent', u'treatmentComponent', u'cte_cat', u'cte_gender',
                                         u'processingUnit', u'cgr_pt', u'cgr_vrg', u'cgr_fpar', u'cgr_opar',
                                         u'cgr_ocrch', u'cgr_fcrch', u'metalexContent', u'metalexResultDictionary']
                },
    u'tei'  :   {
                  u'teiHeader'      : [u'teiHeader', u'text', u'TEI', u'fileDesc', u'titleStmt', u'title', u'publicationStmt', u'p', u'sourceDesc', u'author'],
                  u'text'           : [u'body', u'head', u'entry', u'form', u'orth', u'gramGrp', u'sense', 
                                       u'def', u'cite', u'quote', u'span', u'usg', u'bibl', u'pos', u'genre', u'number',
                                       u'pron', u'etym']
                },
    u'lmf'  :   {
                  u'GlobalInformation'  : [u'LexicalResource', u'feat', u'p', u'GlobalInformation'],
                  u'Lexicon'            : [u'Lexicon', u'feat', u'LexicalEntry', u'WordForm', u'Definition', u'Sense', u'Lexicon']
                },
    u'dtd'  :   [u'ELEMENT', u'ATTRIBUTE', u'PCDATA', u'CDATA', u'REQUIRED', u'IMPLIED'],
    u'xsd'  :   []
}

codifArticles   = []

# ----------------------------------------------------------

def dico_html(save=False) :
    """Build HTML editor file of the all articles 
    
    :return file: metalexViewerEditor.html
    """
    print  u'\n --- %s ---------------------------------------------------- \n\n' %colored('Part 4 : Generate Output formats', attrs=['bold'])
    
    metalex.plugins
    instanceHtml = BaliseHTML()
    filepath     = sys.path[-1]+u'/metalex-template.html'
    metalex.project.create_temp()
    if metalex.project.in_dir('CopymetalexTemplate.html') :
        copyfile(filepath, 'CopymetalexTemplate.html')
        souphtl = instanceHtml.html_inject('CopymetalexTemplate.html')
        if save : 
            with codecs.open('metalexViewerEditor.html', 'w') as htmlresult :
                htmlresult.write(souphtl)
            os.remove('CopymetalexTemplate.html')
            message = u"'metalexViewerEditor.html' has correctly been generated > Saved in dicTemp folder" 
            metalex.logs.manageLog.write_log(message)
    else :
        souphtl = instanceHtml.html_inject('CopymetalexTemplate.html')
        if save : 
            with codecs.open('metalexViewerEditor.html', 'w') as htmlresult :
                htmlresult.write(souphtl)
            os.remove('CopymetalexTemplate.html')
            message = u"'metalexViewerEditor.html' has correctly been generated > Saved in dicTemp folder" 
            metalex.logs.manageLog.write_log(message)
    
    print  u'\n\n --- %s --------------- \n\n' %colored('MetaLex Processes was ended : consult results data in "dicTemp" folder', 'green', attrs=['bold'])
      
 
class BaliseHTML () :
    
    def __init__(self) :
        self.resultHtml = ''
        
    def html_inject(self, template):
        """Create prettify HTML file all previous data generated 
        
        :return str: html (prettify by BeautifulSoup)
        """
        instanceXml    = BaliseXML()
        contentxml     = instanceXml.put_xml(typ=u'xml', save=True)
        metalex.project.create_temp()
        soupXml        = BeautifulSoup(contentxml, "html.parser")
        projectconf    = metalex.project.read_conf()
        Hauthor, Hname, Hdate, Hcomment, Hcontrib = projectconf['Author'], projectconf['Projectname'], projectconf['Creationdate'], projectconf['Comment'], projectconf['Contributors']
        filetemplate   = codecs.open(template, 'r', 'utf-8')
        souphtml       = BeautifulSoup(filetemplate, "html5lib")
        content        = souphtml.find(u'div', attrs={'id': u'all-articles'}) 
        author         = content.find(u'h3', attrs={'id': u'author'})
        author.string  = 'main : '+Hauthor
        date           = content.find(u'h5', attrs={'id': u'date'})
        date.string    = Hdate
        descipt        = content.find(u'p', attrs={'id': u'description'})
        descipt.string = Hcomment
        contrib        = content.find(u'h4', attrs={'id': u'contributors'})
        contrib.string = 'contributors : '+Hcontrib
        project        = content.find(u'h4', attrs={'id': u'projetname'})
        project.string = Hname
        articlesxml    = soupXml.findAll(u'article')
        articleshtml   = souphtml.find(u'div', attrs={'id': u'mtl:articles'})
        for x in articlesxml : 
            elementart = BeautifulSoup(u'<article id=""></article>', 'html5lib')
            idart   = x.get('id')
            artlem  = x.get_text()
            elementart.article.append(artlem)
            elementart.article['id'] = idart
            articleshtml.append(elementart.find(u'article'))  
        listlemme   = souphtml.find(u'ul', attrs={'id': u'list-articles'})
        for x in articlesxml :
            art     = x.get_text()
            idart   = x.get('id')
            lem     = x.find('entry').get_text()
            lemme   = BeautifulSoup(u'<li class="w3-hover-light-grey"><span class="lemme" onclick="changeImage('+
                                    u"'"+idart+u"'"+u')">'+lem+u'</span><span class="fa fa-plus w3-closebtn" onclick="add('+
                                    u"'"+idart+u"'"+u')"/></li>', 'html5lib')
            listlemme.append(lemme.find(u'li'))
            
        filetemplate.close()
        self.resultHtml = souphtml.prettify('utf-8')
        return self.resultHtml
    
     

class BaliseXML ():
    """Build XML file type (xml|tei|lmf) with global metadata of the project
    
    :param typ: str 
  
    :return obj: instance of BaliseXML
    """
    
    def __init__(self, typ="xml") :
        self.typ = typ
        
    def build_structure(self, data, Sfile=None, typ=u'dtd'):
        return False

    def put_xml(self, typ=u'xml', save=False) :
        """Create well formed (xml|tei|lmf) file with metadata and content xml 
        
        :return metalexXml
        """
        metadata   = self.xml_metadata(typ)
        content    = self.xml_content(typ)
        if typ == u'xml' :
            if save :
                name = u'metalex-'+metalex.projectName+u'.xml'
                metalexXml = self.balise(metadata+content, u'metalexResultDictionary', 
                                         attr={'xmlns':'https://www.w3schools.com', 
                                                'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-in', 
                                                'xsi:schemaLocation':'metalexSchemaXML.xsd'})
                metalexXml = u'<?xml version="1.0" encoding="UTF-8" ?>'+metalexXml
                metalexXmlTree = BeautifulSoup(metalexXml, 'xml')
                if metalex.project.in_dir(name) :
                    with codecs.open(name, 'w', 'utf-8') as fle :
                        fle.write(metalexXmlTree.prettify(formatter=None))
                    message = u"'"+name+u"' is created and contain all dictionary articles formated in xml standard format > Saved in dicTemp folder"
                    metalex.logs.manageLog.write_log(message)
                else:
                    message = u"'"+name+u"' is created and contain all dictionary articles formated in xml standard format > Saved in dicTemp folder"
                    metalex.logs.manageLog.write_log(message)
                return metalexXml
            else :
                metalexXml = self.balise(metadata+content, u'metalexResultDictionary', attr={})
                metalexXml = u'<?xml version="1.0" encoding="UTF-8" ?>'+metalexXml
                metalexXmlTree = BeautifulSoup(metalexXml, 'xml')
                print metalexXmlTree.prettify(formatter=None)
        if typ == u'tei' :
            if save :
                name = u'metalex-'+metalex.projectName+u'-TEI.xml'
                metalexXml = self.balise(metadata+content, u'TEI', typ= u'tei')
                metalexXml = u'<?xml version="1.0" encoding="UTF-8" ?>'+metalexXml
                metalexXmlTree = BeautifulSoup(metalexXml, 'xml')
                if metalex.project.in_dir(name) :
                    with codecs.open(name, 'w', 'utf-8') as fle :
                        fle.write(metalexXmlTree.prettify(formatter=None))
                    message = u"'"+name+u"' is created and contain all dictionary articles formated in xml standard format > Saved in dicTemp folder"
                    metalex.logs.manageLog.write_log(message)
                else:
                    message = u"'"+name+u"' is created and contain all dictionary articles formated in xml standard format > Saved in dicTemp folder"
                    metalex.logs.manageLog.write_log(message)
                return metalexXml
            else :
                metalexXml = self.balise(metadata+content, u'TEI', typ= u'tei')
                metalexXml = u'<?xml version="1.0" encoding="UTF-8" ?>'+metalexXml
                metalexXmlTree = BeautifulSoup(metalexXml, 'xml')
                print metalexXmlTree.prettify(formatter=None)
        if typ == u'lmf' :
            if save :
                name = u'metalex-'+metalex.projectName+u'-LMF.xml'
                metalexXml = self.balise(metadata+content, u'LexicalResource', attr={'dtdVersion':'15'}, typ= u'lmf')
                metalexXml = u'<?xml version="1.0" encoding="UTF-8" ?>'+metalexXml
                metalexXmlTree = BeautifulSoup(metalexXml, 'xml')
                if metalex.project.in_dir(name) :
                    with codecs.open(name, 'w', 'utf-8') as fle :
                        fle.write(metalexXmlTree.prettify(formatter=None))
                    message = u"'"+name+u"'  is created and contain all dictionary articles formated in xml standard format > Saved in dicTemp folder"
                    metalex.logs.manageLog.write_log(message)
                else:
                    message = u"'"+name+u"'  is created and contain all dictionary articles formated in xml standard format > Saved in dicTemp folder"
                    metalex.logs.manageLog.write_log(message)
                return metalexXml
            else :
                metalexXml = self.balise(metadata+content, u'LexicalResource', attr={'dtdVersion':'15'}, typ= u'lmf')
                metalexXml = u'<?xml version="1.0" encoding="UTF-8" ?>'+metalexXml
                metalexXmlTree = BeautifulSoup(metalexXml, 'xml')
                print metalexXmlTree.prettify(formatter=None)


    def xml_metadata(self, typ=u'xml'):
        """Create xml metadata file with configuration of the project 
        
        :return str: metadata
        """
        metalex.project.create_temp()
        
        projectconf = metalex.project.read_conf()
        contribtab  = projectconf['Contributors'].split(u',') if projectconf['Contributors'].find(u',') else projectconf['Contributors']
        contrib = ''
        if typ == u'xml' :
            author      = self.balise(projectconf['Author'], u'author', typ)
            name        = self.balise(projectconf['Projectname'].strip(), u'projectName', typ)
            date        = self.balise(projectconf['Creationdate'].strip(), u'dateCreation', typ)
            comment     = self.balise(projectconf['Comment'], u'comment', typ)
            if len(contribtab) > 1 :
                for data in contribtab : contrib += self.balise(data.strip(), u'candidate', typ) 
            else : contrib = self.balise(''.join(contribtab), u'candidate', typ)
            contrib     = self.balise(contrib, u'contributors', typ)
            cont        = name+author+date+comment+contrib
            
            metadataxml = self.balise(cont, u'metalexMetadata', typ) 
            return metadataxml
        if typ == u'tei' :
            if len(contribtab) > 1 :
                for data in contribtab : 
                    if len(data) > 2 : contrib += self.balise(data.strip(), u'span', attr={'content':'contributor'}, typ=u'tei') 
            else : contrib = self.balise(''.join(contribtab), u'span', typ=u'tei')
            author      = self.balise(projectconf['Author'], u'author', typ=u'tei')
            title       = self.balise(projectconf['Projectname'], u'title', typ=u'tei')
            RtitleStmt  = self.balise(title, u'titleStmt', typ=u'tei')
            pdate       = self.balise(projectconf['Creationdate'], u'p', typ=u'tei')
            pcomment    = self.balise(projectconf['Comment'], u'p', typ=u'tei')
            pcontrib    = self.balise(contrib, u'p', attr={'content':'contributors'}, typ=u'tei')
            Rpubli      = self.balise(author+pdate+pcomment+pcontrib, u'publicationStmt', typ=u'tei')
            sourc       = self.balise('TEI metadata for metalex project output', u'p', typ=u'tei')
            Rsourc      = self.balise(sourc, u'sourceDesc', typ=u'tei')
            RfilD       = self.balise(RtitleStmt+Rpubli+Rsourc, u'fileDesc', typ=u'tei')
            metadatatei = self.balise(RfilD, u'teiHeader', typ=u'tei')
            return metadatatei
        if typ == u'lmf' :
            if len(contribtab) > 1 :
                for data in contribtab : 
                    if len(data) > 2 : contrib += data.strip()+', '
            else : contrib = ', '.join(contribtab)
            enc         = self.balise('', u'feat', attr={'att':'languageCoding', 'val':'utf-8'}, typ=u'lmf', sclose=True)
            pauthor     = self.balise('', u'feat', attr={'att':'author', 'val':projectconf['Author'].strip()}, typ=u'lmf', sclose=True)
            pdate       = self.balise('', u'feat', attr={'att':'dateCreation', 'val':projectconf['Creationdate'].strip()}, typ=u'lmf', sclose=True)
            pname       = self.balise('', u'feat', attr={'att':'projectName', 'val':projectconf['Projectname'].strip()}, typ=u'lmf', sclose=True)
            pcomment    = self.balise('', u'feat', attr={'att':'comment', 'val':projectconf['Comment'].strip()}, typ=u'lmf', sclose=True)
            pcontrib    = self.balise('', u'feat', attr={'att':'contributors', 'val':contrib.strip(', ')}, typ=u'lmf', sclose=True)
            meta        = self.balise('', u'p', attr={'att':'meta', 'val':'TEI metadata for metalex project output'}, typ=u'lmf', sclose=True)
            metadatalmf = self.balise(enc+pauthor+pname+meta+pdate+pcomment+pcontrib, u'GlobalInformation', typ=u'lmf')
            return metadatalmf
            
        
    def balise_content_article (self):
        data = get_data_articles(u'text')
        cod  = StructuredWithCodif(data, u'xml')
        resultArticles = []
        for art in  cod.format_articles() :
            article_type_form(art)
            if article_type_form(art) == u'1' :
                partArt = re.search(ur'(([a-zéèàûô]+)\s(<cte_cat>.+</cte_cat>)\s(.+)<cgr_pt>\.</cgr_pt>)', art, re.I)
                if partArt != None :
                    ident, entry, cat, treat = partArt.group(1), partArt.group(2), partArt.group(3), partArt.group(4)
                    id    = generate_id()
                    entry = self.balise(entry, u'entry')
                    ident = self.balise(entry+cat, u'identificationComponent')
                    treat = self.balise(self.balise(treat, u'definition'), u'processingUnit')
                    article = self.balise(ident+self.balise(treat, u'treatmentComponent'), u'article', attr={u'id':id})
                    resultArticles.append(article)     
            if article_type_form(art) == u'2' :
                partArt = re.search(ur'(([a-zéèàûô]+)\s(<cte_cat>.+</cte_cat>\s<cte_gender>..</cte_gender>)\s(.+)<cgr_pt>\.</cgr_pt>)', art, re.I)
                if partArt != None :
                    ident, entry, cat, treat = partArt.group(1), partArt.group(2), partArt.group(3), partArt.group(4)
                    id    = generate_id()
                    entry = self.balise(entry, u'entry')
                    ident = self.balise(entry+cat, u'identificationComponent')
                    if not re.search(ur'(<cgr_pt>\.</cgr_pt>|<cte_cat>.+</cte_cat>|<cgr_vrg>,</cgr_vrg>)', partArt.group(4), re.I) :
                        treat = self.balise(self.balise(treat+u'.', u'definition'), u'processingUnit')
                        article = self.balise(ident+self.balise(treat, u'treatmentComponent'), u'article', attr={u'id':id})
                        resultArticles.append(article)
                    elif partArt.group(4).find(u' et ') != -1 :
                        suite = 'hahaha'
                        #print art+'\n'
        
        return resultArticles
            
           
    def xml_content(self, typ=u'xml', forme=u'text'): 
        """Create xml content file (representing articles) with data articles extracting
        
        :return str: contentXml
        """
        content     = u''
        contentXml  = u''
        data = self.balise_content_article()
        if typ == u'xml' :
            if forme == u'pickle' : 
                data = get_data_articles(u'pickle')
                for dicart in data :
                    for art in dicart.keys() :
                        art = self.balise(dicart[art], u'article', art=True)
                        content += art
                contentXml = self.balise(content, u'metalexContent')
                return contentXml
            else : 
                for art in data :
                    content += art
                contentXml   = self.balise(content, u'metalexContent', attr={'totalArticle': str(len(data))})
                return contentXml
        
        if typ == u'tei' :
            for art in data :
                soupart = BeautifulSoup(art, 'html.parser')
                orth    = soupart.find('entry').getText()
                atOrth  = soupart.find('article').get('id')
                #pron   = soupart.find('cgr_').getText()
                #etym   = soupart.find('cgr_etymon').getText()
                orth    = self.balise(orth, u'orth', {'id': atOrth}, typ=u'tei')
                formB   = self.balise(orth, u'form', attr={'xml:lang':'fr', 'type':'lemma'}, typ=u'tei')
                pos     = soupart.find('cte_cat').getText()
                posB    = self.balise(pos, u'pos', typ=u'tei')
                genB    = u''
                if soupart.find('cte_gender') : genB = soupart.find('cte_gender').getText().strip()
                if genB == u'f.' or genB == u'm.' : genB = self.balise(genB, u'genre', typ=u'tei')
                gramgrp = self.balise(posB+genB, u'gramGrp', typ=u'tei')
                sens    = soupart.find('processingunit').getText().replace(u' .', u'.')
                defi    = self.balise(sens, u'def', typ=u'tei')
                if sens != None : sens  = self.balise(defi, u'sense', typ=u'tei')
                entry   = self.balise(formB+gramgrp+sens, u'entry', typ=u'tei')
                content += entry
            body  = self.balise(content, u'body', typ=u'tei')
            contentXml   = self.balise(body, u'text', attr={'totalArticle': str(len(data))}, typ=u'tei')
            return contentXml
        
        if typ == u'lmf' :
            for art in data :
                soupart = BeautifulSoup(art, 'html.parser')
                orth    = soupart.find('entry').getText()
                atOrth  = soupart.find('article').get('id')
                #pron   = soupart.find('cgr_').getText()
                #etym   = soupart.find('cgr_etymon').getText()
                orth    = self.balise('', u'feat', attr={'att':'writtenForm','val':orth}, typ=u'lmf', sclose=True)
                wordF   = self.balise(orth, u'WordForm', attr={'id': atOrth}, typ=u'lmf')
                pos     = soupart.find('cte_cat').getText()
                posB    = self.balise('', u'feat', attr={'att':'partOfSpeech','val':pos}, typ=u'lmf', sclose=True)
                genB    = u''
                if soupart.find('cte_gender') : genB = soupart.find('cte_gender').getText().strip()
                if genB == u'f.' or genB == u'm.' : genB = self.balise('', u'feat', attr={'att':'grammaticalNumber','val': genB}, typ=u'lmf', sclose=True)
                sens    = soupart.find('processingunit').getText().replace(u' .', u'.')
                sensnb  = self.balise('', u'feat', attr={'att':'sensNumber','val':'1'}, typ=u'lmf', sclose=True)
                definb  = self.balise('', u'feat', attr={'att':'text','val':sens.strip()}, typ=u'lmf', sclose=True)
                defi    = self.balise(definb, u'Definition', typ=u'lmf')
                if sens != None : sens  = self.balise(sensnb+defi, u'Sense', typ=u'lmf')
                entry   = self.balise(wordF+posB+genB+sens, u'LexicalEntry', typ=u'lmf')
                content += entry
            body = self.balise('', u'feat', attr={'att':'language','val':'fra'}, typ=u'lmf', sclose=True)+content
            contentXml   = self.balise(body, u'Lexicon', attr={'totalArticle': str(len(data))}, typ=u'lmf')
            return contentXml
        
        
        
    def balise(self, element, markup, sclose=False, attr=None, typ=u'xml', art=False):
        """Markup data with a specific format type (xml|tei|lmf)
        
        :return str: balised element
        """
        if typ == u'xml' :
            if markup in components[u'xml'][u'metalexContent'] or markup in components[u'xml'][u'metalexMetadata'] :
                if art :
                    element = self.chevron(markup, attr, art=True)+element+self.chevron(markup, attr, False)
                    return element
                else:
                    element = self.chevron(markup, attr)+element+self.chevron(markup, attr, False)
                    return element
        if typ == u'tei' :
            if markup in components[u'tei'][u'text']  or markup in components[u'tei'][u'teiHeader'] :
                if art :
                    element = self.chevron(markup, attr, art=True)+element+self.chevron(markup, attr, False)
                    return element
                else:
                    #print element+'********'
                    element = self.chevron(markup, attr)+element+self.chevron(markup, attr, False)
                    return element
        if typ == u'lmf' :
            if markup in components[u'lmf'][u'GlobalInformation'] \
            or components[u'lmf'][u'Lexicon'] :
                if sclose :
                    #print '111iiiiiii'
                    element = self.chevron(markup, attr, True, sclose=True)
                    return element
                else : 
                    #print '222iiiiiii'
                    element = self.chevron(markup, attr)+element+self.chevron(markup, attr, False)
                    return element
                
    
    
    def chevron(self, el, attr, openchev=True, art=False, sclose=False):
        """Put tag around the data of element
        
        :return str: tagging element 
        """
        idart = generate_id()
        if art and attr == None:
            if openchev     : return u"<"+el+u" id='"+idart+u"' class='data-entry'"+u">"
            if not openchev : return u"</"+el+u">"
            if sclose       : return u"<"+el+u" id='"+idart+u"'/>"
        if art and attr != None :
            allattrib = ''
            for at in attr.keys() :
                allattrib += ' '+at+'="'+attr[at]+'"'
            if openchev  and not sclose   : return u"<"+el+u" id='"+idart+u"' class='data-entry'"+u' '+allattrib+u">"
            if openchev and sclose : return u"<"+el+u" id='"+idart+u"' class='data-entry'"+u' '+allattrib+u"/>"
            if not openchev : return u"</"+el+u">"
        elif art == False and attr != None :
            #print openchev
            allattrib = ''
            for at in attr.keys() :
                allattrib += ' '+at+'="'+attr[at]+'"'
            if openchev  and not sclose   : return u"<"+el+u' '+allattrib+u">"
            if openchev and sclose : return u"<"+el+u' '+allattrib+u"/>"
            if not openchev : return u"</"+el+u">"
        elif art == False and attr == None :
            if openchev     : return u"<"+el+u">"
            if sclose       : return u"<"+el+u"/>"
            if not openchev : return u"</"+el+u">"
        
        
        