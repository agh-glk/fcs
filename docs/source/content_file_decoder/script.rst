Crawling results decoder (fcs.content_file_decoder)
======================================================

Script unpacking `*`.dat files, results of crawling. Proper usage:

    ``python script.py <file_location> <unpacked_directories_structure_location>``

Script creates tree of directories. In every leaf directory there are two files - *url_links.txt* (page URL
in first line, extracted links separated with whitespace in second) and *content.dat* containing
decoded from Base64 resource. At higher level directories with names of integers are stored. Additionally, file
*index.txt* links directory name with page URL.