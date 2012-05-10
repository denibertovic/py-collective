def get_config():
    watched = {}
    folders = []
    cfg = open('harvester.conf.example', 'r')
    for line in cfg.readlines():
        if not line.startswith('#'):
            watched[line.split(':')[1].strip()] = line.split(':')[0].strip()
            folders.append('/'.join(line.split(':')[1].strip().split('/')[:-1]))
    folders = dict.fromkeys(folders).keys()
    return watched, folders

