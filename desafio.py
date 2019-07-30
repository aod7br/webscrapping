#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
14062016
aod7br@gmail.com 

Crawler para o desafio da Sieve

    O programa le as URLs que ira percorrer de uma fila 
e dispara threads que consomem esta fila
as threads fazerm o parse das URLs , marcam as ja parseadas,
e adicionam os links nao visitados da pagina à fila de input.
Se uma pagina é do padrao de produto, ao inves de 
adicionar os links na fila, a thread extrai informacoes 
do produto e coloca as informacoes em uma outra fila, 
de output. Posteriormente o thread-control faz
o flush da fila para STDOUT (que pode ser redirecionado
para um CSV)
"""

from multiprocessing import Process, Queue, Manager
from time import sleep
from random import randint as rand
import sys
from bs4 import BeautifulSoup
import urllib2
import re

root_url="http://www.epocacosmeticos.com.br" # adhoc
pattern=re.compile( '^%s/.+/p$' % root_url ) # adhoc 

max_urls=1000 # tweak
(n_workers, slice_size)=(4, 100) # tweak

def parser( name, root_url, pattern, slice_size, inputq, outputq, hit_table ):
    url_format = re.compile( r"^http(s*)://" )
    root_url_format = re.compile( r"^%s/\w+" % root_url )

    run=True
    n=0
    while (n<slice_size and run):
        try:
            url=inputq.get_nowait()
            #print name, url
            n+=1
            if ( not hit_table.get( url ) ):
                resp = urllib2.urlopen( url )
                soup = BeautifulSoup( resp, 'lxml', 
                                      from_encoding=resp.info().getparam('charset') )

                if re.search( pattern, url ):
                    titulo=soup.html.head.title.string.encode('utf-8') # adhoc
                    nome=titulo.split('-')[0].strip().encode('utf-8') # adhoc
                    outputq.put( ( nome, titulo, url ) ) # adhoc

                else:
                    for link in soup.find_all('a', href=True):
                        target=link['href'].replace("\s\t\n\r", "").strip(" /")
                        if ( target and len(target)>1 ):
                            # do not crawl outside links
                            if  ( re.search( url_format, target )  ):
                                if ( re.search( root_url_format, target ) and 
                                     not hit_table.get( target ) ):
                                        inputq.put( target )
                            # skip invalid local links and convert local to universal
                            elif ( not re.search("^(#|mailto:)", target ) ): 
                                fixed_target=root_url+"/"+target.strip(' /')
                                if (not hit_table.get( fixed_target ) ):
                                    inputq.put( fixed_target )

                hit_table[ url ]=1
        except Queue.Empty :
            run=False
        except Exception, e:
            #something else broke parsing
            sys.stderr.write( "Excecao %s " % e )
            run=False


# ============================================================== thread control 
if __name__ == '__main__':

    mgr=Manager()
    hit_table=mgr.dict()
    output_queue=mgr.Queue()
    input_queue=mgr.Queue()
    input_queue.put( root_url.strip(" /") )

    available_workers=[]
    for n in range(n_workers):
        available_workers.append("p%s" % n)

    total=0
    found=0
    running_workers=[]
    while( not input_queue.empty() and total < max_urls or running_workers ):
        #print "%s running" % running_workers 
        if ( available_workers and not input_queue.empty() and total < max_urls ):
            w=available_workers.pop()
            p=Process( target=parser, name=w,
                       args=( w, root_url, pattern, slice_size, 
                             input_queue, output_queue, hit_table) )
            p.start()
            running_workers.append(p)
        else:
            #flush
            while ( not output_queue.empty() ):
                found+=1
                print "'%s', '%s', '%s'" % output_queue.get(True,1) # adhoc

            if ( running_workers ):
                w=running_workers.pop()
                # ao inves de timeout de 50s eu poderia tambem fazer o join por 1s 
                # e se nao tiver resposta, por a url de volta na fila de running workers
                w.join(50) 
                available_workers.append( w.name )

        total=len(hit_table)

    sys.stderr.write( "found %s products in %s urls crawled" % (found, total) )


