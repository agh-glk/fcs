import sys
import json
import os
import shutil


if __name__ == '__main__':
    if len(sys.argv) > 3:
        print 'Required: python script.py <file> <directory>'
        exit(1)
    file_path = sys.argv[1]
    dest_path = os.path.abspath(sys.argv[2])
    dir_path = os.path.join(dest_path, str(os.path.splitext(file_path)[0]))
    shutil.rmtree(dir_path, ignore_errors=True)
    os.mkdir(dir_path)
    counter = 1
    index = []
    with open(file_path) as data_file:
        for line in data_file:
            json_object = json.loads(line)
            inner_dir_path = os.path.join(dir_path, str(counter))
            os.mkdir(inner_dir_path)
            with open(os.path.join(inner_dir_path, 'url_links.txt'), 'w+') as url_links:
                url_links.write(json_object['url']+'\n')
                url_links.write(" ".join(json_object['links']))
                index.append(json_object['url'])
            with open(os.path.join(inner_dir_path, 'content.dat'), 'w+') as content_file:
                content_file.write(json_object['content'].decode('base64'))
            counter += 1
        with open(os.path.join(dir_path, 'index.txt'), 'w+') as index_file:
            iterator = 1
            for entry in index:
                index_file.write('%s : %s\n' % (iterator, entry))
                iterator += 1
    exit(0)










