import functools
import json
import operator

class DockerRegistrySchema1Manifest:
    def __init__(self, content):
        self._content = content

    def return_check(self, stmt):
        if stmt is None:
            return 'null'
        else:
            return stmt

    def __get_sorted_history(self):
        history = []

        for entry in self._content['history']:
            history.append(json.loads(entry['v1Compatibility']))

        history.sort(key=lambda x: x['created'], reverse=True)
        return history

    def __get_first_value(self, *keys):
        for entry in self.__get_sorted_history():
            try:
                return functools.reduce(operator.getitem, keys, entry)
            except KeyError:
                pass
        return None

    def get_created_date(self):
        return self.return_check(self.__get_first_value('created'))

    def get_docker_version(self):
        return self.return_check(self.__get_first_value('docker_version'))

    def get_entrypoint(self):
        return self.return_check(self.__get_first_value('config', 'Entrypoint'))

    def get_exposed_ports(self):
        return self.return_check(self.__get_first_value('config', 'ExposedPorts'))

    def get_layer_ids(self):
        layer_ids = []

        for layer in self._content['fsLayers']:
            layer_ids.append(layer['blobSum'])

        return set(layer_ids)

    def get_volumes(self):
        return self.return_check(self.__get_first_value('config', 'Volumes'))


def make_manifest(content):
    if content['schemaVersion'] == 1:
        return DockerRegistrySchema1Manifest(content)
    else:
        raise ValueError
