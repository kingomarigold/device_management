import base64
import zlib
import os
import shutil

def read_in_chunks(file, chunk_size):
    while True:
        data = file.read(chunk_size)
        if not data:
            break
        yield {'data': data, 'crc': zlib.crc32(data)}

def create_dir(name):
    print('Creating dir: ', name)
    dir_name = get_dir_name(name)
    print('Actual directory name: ', dir_name)
    if os.path.exists(dir_name):
        print('Removing directory: ', dir_name)
        shutil.rmtree(dir_name)
        print('Removed directory')
    print('Creating directory with name: ', dir_name)
    os.makedirs(dir_name)
    print('Created directory with name: ', dir_name)

def get_dir_name(name):
    return 'dir_' + os.path.splitext(os.path.basename(name))[0]


def write_in_chunks(name, index, payload):
    dir_name = get_dir_name(name)
    my_data = payload['data']
    my_crc = payload['crc']
    act_crc = zlib.crc32(my_data)
    print('Expected CRC: ', my_crc)
    print('Actual CRC: ', act_crc)
    if  act_crc == my_crc:
        print('Crc Matches for Chunk with index: ', index, ' and file name: ', name)
        with open(os.path.join(dir_name, str(index)), 'wb') as my_file:
            my_file.write(my_data)
        return True
    print('Crc does not match for Chunk with index: ', index, ' and file name: ', name)
    return False

def merge_chunks(name, total_chunks):
    dir_name = get_dir_name(name)
    ret_val = True
    for index in range(1, total_chunks + 1):
        file_name = os.path.join(dir_name, str(index))
        if os.path.isfile(file_name):
            print('Chunk with index: ', index, ' found in directory: ', dir_name)
            with open(file_name, 'rb') as my_file:
                with open(name, 'ab') as write_file:
                    write_file.write(my_file.read())
        else:
            print('Chunk with index: ', index, ' is missing from directory: ', dir_name)
            ret_val = False
        
    return ret_val
            
