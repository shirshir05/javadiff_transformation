class LineExtraction:
    def __init__(self, line, extractors):
        self.line = line
        self.extractors = extractors
        self.metrics = {}

    def get_id(self):
        pass

    def add_metrics(self, name, metrics_dict):
        self.metrics[name] = metrics_dict

    def get_metrics(self, name):
        return self.metrics.get(name)

    def export(self):
        ans = {'id': self.get_id()}
        for extractor_name in self.metrics:
            for key in self.metrics[extractor_name]:
                ans[f'{extractor_name}_{key}'] = self.metrics[extractor_name][key]
        return ans


class MethodExtraction:
    def __init__(self, method, extractors):
        self.method = method
        self.extractors = extractors
        self.line_extractions = []
        self.metrics = {}

    def add(self, le):
        self.line_extractions.append(le)

    def get_id(self):
        pass

    def add_metrics(self, name, metrics_dict):
        self.metrics[name] = metrics_dict

    def get_metrics(self, name):
        return self.metrics.get(name)

    def export(self):
        ans = {'id': self.get_id()}
        for extractor_name in self.metrics:
            for key in self.metrics[extractor_name]:
                ans[f'{extractor_name}_{key}'] = self.metrics[extractor_name][key]
        return ans


class FileExtraction:
    def __init__(self, source_file, extractors):
        self.source_file = source_file
        self.extractors = extractors
        self.methods_extractions = []
        self.metrics = {}

    def add(self, me):
        self.methods_extractions.append(me)

    def get_id(self):
        pass

    def add_metrics(self, name, metrics_dict):
        self.metrics[name] = metrics_dict

    def get_metrics(self, name):
        return self.metrics.get(name)

    def export(self):
        ans = {'id': self.get_id()}
        for extractor_name in self.metrics:
            for key in self.metrics[extractor_name]:
                ans[f'{extractor_name}_{key}'] = self.metrics[extractor_name][key]
        return ans


class FileDiffExtraction:
    def __init__(self, file_diff, extractors):
        self.file_diff = file_diff
        self.extractors = extractors
        self.before_file = None
        self.after_file = None
        self.metrics = {}

    def add_source(self, source_type, fe):
        if source_type == 'before':
            self.before_file = fe
        if source_type == 'after':
            self.after_file = fe

    def get_id(self):
        pass

    def add_metrics(self, name, metrics_dict):
        self.metrics[name] = metrics_dict

    def get_metrics(self, name):
        return self.metrics.get(name)

    def export(self):
        ans = {'id': self.get_id()}
        for extractor_name in self.metrics:
            for key in self.metrics[extractor_name]:
                ans[f'{extractor_name}_{key}'] = self.metrics[extractor_name][key]
        return ans


class CommitExtraction:
    def __init__(self, commit, extractors):
        self.commit = commit
        self.extractors = extractors
        self.file_diff_extractions = []
        self.metrics = {}

    def add(self, fde):
        self.file_diff_extractions.append(fde)

    def get_id(self):
        pass

    def add_metrics(self, name, metrics_dict):
        self.metrics[name] = metrics_dict

    def get_metrics(self, name):
        return self.metrics.get(name)

    def export(self):
        ans = {'id': self.get_id()}
        for extractor_name in self.metrics:
            for key in self.metrics[extractor_name]:
                ans[f'{extractor_name}_{key}'] = self.metrics[extractor_name][key]
        return ans
