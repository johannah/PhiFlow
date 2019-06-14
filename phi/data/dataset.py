from .source import *
from weakref import WeakSet


class Dataset(object):

    def __init__(self, name):
        self.name = name
        self.sources = []
        self._observers = WeakSet()

    def __repr__(self):
        return self.name

    def add(self, datasource):
        if isinstance(datasource, DataSource):
            self.sources.append(datasource)
        else:
            for source in datasource:
                self.add(source)
        for o in self._observers: o(self)

    def remove(self, datasource):
        self.sources.remove(datasource)
        for o in self._observers: o(self)

    def count(self, lookup_unknown=True):
        total = 0
        for datasource in self.sources:
            s = datasource.size(lookup=lookup_unknown)
            if s is not None:
                total += s
        return total

    def on_change(self, callback):
        self._observers.add(callback)

    def remove_on_change(self, callback):
        self._observers.remove(callback)

    def __iadd__(self, other):
        if isinstance(other, DataSource):
            self.add(other)
        if isinstance(other, Dataset):
            self.sources = self.sources + other.sources
            for o in self._observers: o(self)
        return self

    def __add__(self, other):
        newset = Dataset("%s + %s" % (self.name, other.name))
        if isinstance(other, DataSource):
            newset.add(other)
        if isinstance(other, Dataset):
            newset.sources = self.sources + other.sources
        return newset

    @staticmethod
    def load(directory, dataset_name=None, indices=None, max_scenes=None, assume_same_frames=True, assume_same_shapes=True):
        import os
        from .fluidformat import Scene

        if dataset_name is None:
            dataset_name = os.path.basename(directory)

        dataset = Dataset(dataset_name)

        shape_map = dict() if assume_same_shapes else None
        frames = None

        indexfilter = None if indices is None else lambda i: i in indices
        scene_iterator = Scene.list(directory, max_count=max_scenes, indexfilter=indexfilter)

        for scene in scene_iterator:
            if assume_same_frames and frames is None:
                frames = scene.frames
            dataset.add(SceneSource(scene, frames=frames, shape_map=shape_map))

        return dataset


# def split():
#     def need_factor(self, total_size, add_count):
#         if isinstance(self.target_size, float):
#             if not self.sources:
#                 return self.target_size
#             else:
#                 return self.target_size - (self.size+add_count) / float(total_size)
#         else:
#             raise NotImplementedError()

