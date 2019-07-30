### REGRAS SIEVE ###

Escreva um crawler que visite o site epocacosmeticos.com.br e salve um arquivo .csv com o nome do produto, o título e a url de cada página de produto[1] encontrada. Regras:

  * Esse arquivo não deve conter entradas duplicadas;
  * Não é permitido usar o sitemap para pegar todas as urls do site; o site deve de fato ser visitado e parseado para se obter as informações.
  * Exceto pelo Scrapy, você pode usar os frameworks e bibliotecas que quiser, desde que a linguagem principal usada seja Python (2.7 ou 3.x, tanto faz).

Desenvolva seu código em um local público adicione um arquivo README ou INSTALL explicando como instalar e rodar o programa.

Bonus:
  * Testes unitários;
  * Arquitetura paralela ou distribuida.

[1] Uma página de produto é a que contém as informações (nome, preço, disponibilidade, descrição etc.) de apenas um produto. Home page, páginas de busca ou categoria não são consideradas páginas de produto. 

Exemplo:
 É página de produto: http://www.epocacosmeticos.com.br/hypnose-eau-de-toilette-lancome-perfume-feminino/p
**NÃO** é página de produto: http://www.epocacosmeticos.com.br/cabelos

### MINHA SOLUCAO ###

O script desafio.py foi planejado para rodar em linux. 

Junto com o script esta o arquivo desafio-sample.csv, resultado de um run do programa para 50000 URLs com informacoes de 5442 produtos

As instrucoes de instalação abaixo servem para Ubuntu.

## INSTALL ##

```
#!bash
sudo bash
apt-get install python-dev libxml2-dev libxslt-dev lib32z1-dev
pip install --upgrade requests cssselect lxml
pip install urllib2
pip install bs4
```

## RUNNING ##


```
#!bash
python desafio.py >desafio.csv

```

## ABOUT ##

desafio.py foi implementado com uma arquitetura geral de crawler multiprocessado. 

O programa le as URLs que irá percorrer de uma fila e dispara threads que a consomem.
As threads fazem parse das URLs, marcam as ja parseadas, e adicionam os links nao visitados da pagina, à fila de input.
Se uma pagina é do padrao de produto, ao inves de  adicionar os links na fila, a thread extrai informacoes 
do produto e coloca as informacoes em uma outra fila,  de output. 
Posteriormente o thread-control faz o flush da fila para STDOUT (que pode ser redirecionado para um CSV)


Algumas linhas tem codigo adhoc especifico para o site do desafio, elas estao marcadas com um comentario # adhoc.
Algumas linhas tambem estao marcadas com # tweak, que podem ser mudadas para o numero de processadores da maquina onde vai rodar, em com um limite maximo de URLs a percorrer