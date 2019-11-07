import os
import tarfile
import tempfile
import json
import logging
import tqdm
from dxf import hash_file

LOGGER = logging.getLogger(__name__)

# WARNING: example function
bars = {}


def progress(dgst, chunk, size):
    if dgst not in bars:
        bars[dgst] = tqdm.tqdm(desc=dgst[0:8], total=size, leave=True)
    if chunk:
        bars[dgst].update(len(chunk))
    if bars[dgst].n >= bars[dgst].total:
        bars[dgst].close()
        del bars[dgst]


# REMOVE LATER


class DockerTarUploader:
    def __init__(self, dxf):
        self._dxf = dxf

    @staticmethod
    def _get_json_from_file(file):
        with open(file, 'r', encoding='utf-8') as fp:
            return json.load(fp)

    @staticmethod
    def _extract_tar_file(tar, path):
        with tarfile.open(tar) as tar_file:
            tar_file.extractall(path)

    @staticmethod
    def _create_manifest(conf_path, layer_paths):
        def _get_size_of(path):
            return os.path.getsize(path)

        result = dict()
        result["schemaVersion"] = 2
        result["mediaType"] = "application/vnd.docker.distribution.manifest.v2+json"
        result["config"] = dict()
        result["config"]["mediaType"] = "application/vnd.docker.container.image.v1+json"

        result["config"]["size"] = _get_size_of(conf_path)
        result["config"]["digest"] = hash_file(conf_path)

        result["layers"] = []
        for layer in layer_paths:
            layer_dict = dict()
            layer_dict["mediaType"] = "application/vnd.docker.image.rootfs.diff.tar"
            layer_dict["size"] = _get_size_of(layer)
            layer_dict["digest"] = hash_file(layer)
            result["layers"].append(layer_dict)

        return json.dumps(result)

    def upload_tar(self, file_name, on_progress=None, check_exists=False):
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                self._extract_tar_file(file_name, tmp_dir)
                manifest = self._get_json_from_file(os.path.join(tmp_dir, 'manifest.json'))[0]
                repo_tags = manifest['RepoTags']
                config_path = os.path.join(tmp_dir, manifest['Config'])
                for repo in repo_tags:
                    image, tag = tuple(repo.split(':'))
                    LOGGER.info("Extracting docker tar image %s:%s", image, tag)
                    layers = manifest['Layers']
                    formatted_layers = []
                    for layer in layers:
                        LOGGER.info("Start pushing layer " + str(layer))
                        layer_path = os.path.join(tmp_dir, layer)
                        self._dxf.push_blob(layer_path, progress=on_progress, check_exists=check_exists)
                        formatted_layers.append(layer_path)
                    self._dxf.push_blob(config_path, check_exists=check_exists)
                    LOGGER.info("Pushing manifest for %s:%s", image, tag)
                    registry_manifest = self._create_manifest(config_path, formatted_layers)
                    self._dxf.set_manifest(tag, registry_manifest)
                    LOGGER.info("Pushing image succeeded %s:%s", image, tag)
            return True
        except Exception as ex:
            LOGGER.exception(ex)
            return False
