#!/usr/bin/env python3

"""e4sListPage.py: Generates web pages listing e4s products from e4s_products.yaml"""
__author__ = "Wyatt Spear"

import urllib.request
from urllib.request import urlopen
import yaml
import subprocess
import datetime
import html
import sys
import os
import shutil

timestamp='{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

introListBlock='''<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8" />
	<!--[if lt IE 9]><script src="https://cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7.3/html5shiv.min.js"></script><![endif]-->
	<title>E4S Products</title>
	<meta name="keywords" content="" />
	<meta name="description" content="" />
	<link href="style.css" rel="stylesheet">


<style>
.product_button {
  background-color: #777;
  color: white;
  cursor: pointer;
  padding: 18px;
  width: 100%;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
}

.active, .product_button:hover {
  background-color: #555;
}

</style>
</head>

<body>

<script src="jquery.js"></script>
<script>
$(function () {
    $(".load-html").each(function () {
        $(this).load(this.dataset.source);
    });
});
</script>



<div class="wrapper">

	<header class="header">
		<div class="load-html" id="header" data-source="header.html"></div>
	</header><!-- .header-->

	<div class="middle">

		<div class="container">
			<main class="content">
				<H2>E4S Products</h2>

***TIMESTAMP***<br>
<hr>'''

introCloseBlock='''			</main><!-- .content -->
		</div><!-- .container-->

	</div><!-- .middle-->

</div><!-- .wrapper -->
</body>
</html>'''

introHeadingBlock='''<h3>***HEADING***</h3>
'''

introLinkBlock='''<!-- This is a single product entry. To add more copy and edit from here... -->
<button class="product_button"><b><a href="***LOWNAME***.html">***CAPNAME***</a></b>
</button>
<!-- ...to here (product entry end) -->'''


introBlock='''<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8" />

	<title>E4S Products: ***CAPNAME***</title>
  </head>
  <body>
		<h1>***CAPNAME***</h1>

        ***TIMESTAMP***
        <br><br>
'''
spackBlock='''<table>
			<tr>
				<td>Description:</td>
				<td>
                    ***DESCRIPTION***
		        <td>
			</tr>
			<tr>
				<td>Website:</td>
				<td><a href="***SITEADDRESS***">***SITEADDRESS***</a><td>
			</tr>
			<tr>
				<td>Version:</td>
				<td>***SPACKVERSION***<td>
			</tr>
			<tr>
				<td>Spack Hash:</td>
				<td>***SPACKHASH***<td>
			</tr>
		</table>
<hr>'''
endBlock='''
  </body>
</html>	'''

docBlock='''<b>***DOCNAME***</b>
	<br>
<pre>
***DOCTEXT***
</pre>

<a href="***DOCURL***">More...</a>
<hr>
<br>
'''

script_path = os.path.dirname(os.path.abspath( __file__))
browserHeaders={'User-Agent' : "Magic Browser"}
rawSegment='/raw/'
blobSegment='/blob/'
e4sDotYaml='/e4s.yaml'
dotE4s='/.e4s/'
bitbucketRaw='?&raw'

def getSpackInfo(name):
    whichSpack = shutil.which('spack')
    if whichSpack is None:
        return None
    infoBlob = subprocess.run(['spack', 'info', name], stdout=subprocess.PIPE).stdout.decode('utf-8')
    infoBlob
    return infoBlob

def getURLHead(url, numChars=200):
    #masteryaml_url="https://raw.githubusercontent.com/UO-OACISS/e4s/master/docker-recipes/ubi7/x86_64/e4s/spack.yaml"
    #print("Reading URL: "+url)
    #browserHeaders={'User-Agent' : "Magic Browser"}
    req=urllib.request.Request(url,None,browserHeaders)
    with urlopen(req) as f:
        #Read 2x the target number of characters to look for a good breakpoint in the overflow
        head=html.escape(f.read(numChars*2).decode("utf-8"))
        breakpoint=head.find('\n',numChars)
        if breakpoint < numChars:
            breakpoint=head.find(". ",numChars)
        if breakpoint < numChars:
            breakpoint=head.find(' ',numChars);
        if breakpoint < numChars:
            breakpoint=numChars
        #print("Breakpoint: ",breakpoint)            
        head = head[:breakpoint]
        #print("Resulting Head: "+head)
        return head
    #    yamlMap=yaml.safe_load(url)
    #speclist = yamlMap.get('spack').get('specs')

def getRepoName(url):
    #print(url)
    lastblobdex=url.rfind('/blob/')
    if lastblobdex == -1:
        lastblobdex=url.rfind('/src/')
    if lastblobdex == -1:
        lastblobdex=url.rfind('/browse')  #Used in some bitbucket urls
    if lastblobdex == -1:
        print("ERROR PARSING REPO NAME FROM URL: "+url)
        return None
#    print("Name ends at: "+str(lastblobdex))
    firstnamedex=url.rfind('/',0,lastblobdex)
#    print("Name starts at: "+str(firstnamedex))
    name = url[firstnamedex+1:lastblobdex]
    return name

def readRemoteYaml(yaml_url,name):
    req=urllib.request.Request(yaml_url,None,browserHeaders)
    try:
        response=urlopen(req)
    except urllib.error.URLError as e:
        print("Remote metadata for "+name+": "+e.reason+". "+yaml_url)
        return None
    else:
        try:
            yamlMD = yaml.safe_load(response)
        except:
            print("Remote metadata for "+name+": Invalid yaml url. "+yaml_url)
            return None
        else:
            return yamlMD


def getRepoDocs(url,name):
    yamlMD=None
    #TODO: This should work for github blob urls but may not work for others
    li = url.rsplit(blobSegment, 1)
    raw_url=rawSegment.join(li)
    
    #Check the hidden .e4s directory for e4s.yaml first
    raw_yaml_url=raw_url+dotE4s+e4sDotYaml
    yamlMD=readRemoteYaml(raw_yaml_url,name)
    if yamlMD is not None:
        return yamlMD
    
    #print("Raw URL: "+raw_url)
    raw_yaml_url=raw_url+e4sDotYaml
    #print("Raw E4S "+raw_e4s)
    yamlMD=readRemoteYaml(raw_yaml_url,name)
    
    if yamlMD is not None:
        return yamlMD
    else:
        localFile=script_path+'/../data/'+name+e4sDotYaml
        if os.path.isfile(localFile) is True:
            with open(script_path+'/../data/'+name+e4sDotYaml) as MDFile:
                yamlMD = yaml.safe_load(MDFile)
                return yamlMD
    print("No metadata found for "+name)
    return None;
            
       

def processURL(url):
    repoName=getRepoName(url)
    if repoName is None:
        return None
    yamlMD=getRepoDocs(url,repoName)
    if yamlMD is not None and 'repo_url' not in yamlMD:
        yamlMD[0]['repo_url']=url
    return yamlMD #{'e4s_product':repoName,'docs':docs}

output_prefix=""
if(len(sys.argv)>1):
	if(os.path.isdir(sys.argv[1])):
		output_prefix=sys.argv[1]+"/"
	else:
		print("First argument must be a valid output directory")
		sys.exit(-1)


with open(script_path+'/../data/e4s_products.yaml') as MDlist:
    products = yaml.safe_load(MDlist)

with open(output_prefix+'E4S-Products.html', "a") as listPage:
    print(introListBlock.replace("***TIMESTAMP***",timestamp), file=listPage)

    for urls in products:
#        if "github.com" in urls['repo_url']:
#            continue
#        if "heading" in product:
#            print(introHeadingBlock.replace("***HEADING***",product['heading']), file=listPage)
#            continue
        processedURL=processURL(urls['repo_url'])
        if processedURL is None:
            continue
        product = processedURL[0]
        print ('Generating HTML for: '+product['e4s_product'])
        with open(output_prefix+product['e4s_product'].lower()+".html", "a") as ppage:

            capName=product['e4s_product'].upper()
            lowName=capName.lower()

            print(introLinkBlock.replace("***CAPNAME***",capName).replace("***LOWNAME***", lowName), file=listPage)

            introFix=introBlock.replace("***CAPNAME***",capName).replace("***TIMESTAMP***",timestamp)
            print(introFix, file=ppage)

            spackInfo = getSpackInfo(lowName)
            if spackInfo is not None:
                print(spackInfo)

            appendRaw=""
            rawFileURL = urls['repo_url']
            if 'raw_url' in product:
                rawFileURL = product['raw_url']
			
            if 'bitbucket.' in rawFileURL and '/browse' in rawFileURL:
                appendRaw=bitbucketRaw
                #rawFileURL = product['repo_url']
            else:
                fromRaw="/blob/"
                toRaw="/raw/"
#                if 'raw_replace' in product:
#                    fromRaw=product['raw_replace'][0]
#                    toRaw=product['raw_replace'][1]
                if "bitbucket.org" in rawFileURL:
                    fromRaw="/src/"
                rawFileURL = rawFileURL.replace(fromRaw,toRaw)
            print(rawFileURL)
            for doc in product['docs']:
                docURL=rawFileURL+"/"+doc+appendRaw
                #print(docURL)
                docHead=getURLHead(docURL)
                docFix = docBlock.replace("***DOCNAME***",doc).replace("***DOCTEXT***",docHead).replace("***DOCURL***",product['repo_url']+"/"+doc)
                print(docFix, file=ppage)
            #.replace('***DESCRIPTION***',"N/A").replace("***SITEADDRESS***","N/A").replace("***SPACKVERSION***","N/A")

            print(endBlock, file=ppage)
    print(introCloseBlock.replace("***TIMESTAMP***",timestamp), file=listPage)


#print('\n'.join(speclist))
