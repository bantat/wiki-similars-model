# Wikipedia Artist Similarity Model

This repository is a basic version of a musical artist similarity model which utilizes Wikipedia data. The model operates on artist data queried from WDQS (The WikiData Query Service) which can be hosted locally using data dumps provided by WikiMedia, and analyzes a subgraph of Wikipedia composed of entities identified as musicians/bands to produce a table of ordered similars for each given source artist.

> This model requires entity QIDs/Wikipedia URLs queried from WDQS to base the model dataset on.

## Running
- Build artist dataset
    - Create local instance of WDQS
    - Query QIDs, URLs of artists based on SPARQL definition
- Load artist data using `data_manager.py`
- Generate artist data based on Wikipedia article titles using `wiki_data_gen.py`, which queries and parses wikitext from the Wikipedia API
- Create a WikiNetworkModel object using the data generated
- Use the model to generate artist similars for a single musician/group (`get_artist_similars()`) or generate similars for the complete dataset (`generate_similars()`)

### Creating and querying instance of WDQS

- Create EC2 Instance
    - AMI: Ubuntu Server
    - Instance Type: r4.4xlarge
    - Configuration Details:
        - Storage: 1000Mib/1Tb
        - Security Group Configuration
            - Set inbound rules based on public IP of work machine/space, use CIDR block calculator to convert address
            - Use ssh private key for remote access
- Install Prerequisite Software
Note: Be sure to use sudo (super user do) for install/exec on remote
    - Java 8: https://www.digitalocean.com/community/tutorials/how-to-install-java-with-apt-get-on-ubuntu-16-04
    - Unzip: apt-get install unzip
    - Python Packages:
        - Pip3: apt-get install python3-pip
        - Ujson: pip3 install ujson
- Install and Launch Wikidata Query Service
    - Download/Install service package from Maven Central
group ID org.wikidata.query.rdf and artifact ID "service"
        - Find url by going to maven.org, search ‘g:"org.wikidata.query.rdf" AND a:"service"’ (tested with V0.2.5)
        - Use wget on remote command line to download
        - Use unzip on remote command line to decompress
    - Download requisite data
        - Use mkdir to create directory ‘data’ at the top level of service package subdirectories
        - Find download url on https://dumps.wikimedia.org/wikidatawiki/entities/
        - Select most recently dated directory that is populated
        - Copy url for dump file ending in .ttl.qz, use wget to download to ‘data’ directory
    - Pre-process the data dump
Note: This step may take 12-24 hours to complete
        - Use mkdir to create directory ‘split’ within the ‘data’ directory to contain processed portions of the complete wikidata dump
        - Run ./munge.sh with the following arguments to process data:
-f filepath/name of data dump (data/wikidata-dateofdump-all-BETA.ttl.gz)
-d filepath of directory to contain processed portions of data (data/split)
-l languages to be included in processed data (en,es,zh), check .py query script to verify which tags are being queried
    - Launch and load to the Wikidata Query Service instance
Note: This step may take 48+ hours to complete
        - Create a window in tmux which will contain shells running server processes - https://robots.thoughtbot.com/a-tmux-crash-course
         - Start the blazegraph using ./runBlazegraph.sh
        - Open a new tab/pane to run the script which builds the graph
        - Load the split data using ./loadRestAPI.sh -n wdq -d `pwd`/data/split



The remote instance of the Wikidata Query Service is now operational, and can be accessed via the exposed endpoint ‘http://localhost:9999/bigdata/namespace/wdq/sparql’ Run the wikidata query script to match artist names to wiki entities classified as bands and musicians, and query their english wikipedia article titles and birth/inception years for use in the wiki similarity model.

Resource: https://www.mediawiki.org/wiki/Wikidata_query_service/User_Manual
