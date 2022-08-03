import abc


class LineLevelExtractor(abc):
    @abc.abstractmethod
    def get_module_name(self):
        pass

    def extract(self, line_extraction):
        line_extraction.add_metrics(self.get_module_name(), self._extract(line_extraction))

    @abc.abstractmethod
    def _extract(self, line_extraction):
        pass


class MethodLevelExtractor(abc):
    @abc.abstractmethod
    def get_module_name(self):
        pass

    def get_line_extractor_module(self, method_extraction):
        return list(map(lambda me: (me.get_id(), me.get_metrics(self.get_module_name())),
                        method_extraction.line_extractions))

    def extract(self, method_extraction):
        method_extraction.add_metrics(self.get_module_name(), self._extract(method_extraction))

    @abc.abstractmethod
    def _extract(self, method_extraction):
        pass


class FileLevelExtractor(abc):
    @abc.abstractmethod
    def get_module_name(self):
        pass

    def get_method_extractor_module(self, file_level_extraction):
        return list(map(lambda me: (me.get_id(), me.get_metrics(self.get_module_name())),
                        file_level_extraction.methods_extractions))

    def extract(self, file_level_extraction):
        file_level_extraction.add_metrics(self.get_module_name(), self._extract(file_level_extraction))

    @abc.abstractmethod
    def _extract(self, file_level_extraction):
        pass


class FileDiffLevelExtractor(abc):
    @abc.abstractmethod
    def get_module_name(self):
        pass

    def get_before_file_extractor_module(self, file_diff_extraction):
        return file_diff_extraction.before_file.get_id(), file_diff_extraction.before_file.get_metrics(
            self.get_module_name())

    def get_after_file_extractor_module(self, file_diff_extraction):
        return file_diff_extraction.after_file.get_id(), file_diff_extraction.after_file.get_metrics(
            self.get_module_name())

    def extract(self, file_diff_extraction):
        file_diff_extraction.add_metrics(self.get_module_name(), self._extract(file_diff_extraction))

    @abc.abstractmethod
    def _extract(self, file_diff_extraction):
        pass


class CommitLevelExtractor(abc):
    @abc.abstractmethod
    def get_module_name(self):
        pass

    def get_file_diff_extractor_module(self, commit_extraction):
        return list(map(lambda fd: (fd.get_id(), fd.get_metrics(self.get_module_name())),
                        commit_extraction.file_diff_extractions))

    def extract(self, commit_extraction):
        commit_extraction.add_metrics(self.get_module_name(), self._extract(commit_extraction))

    @abc.abstractmethod
    def _extract(self, commit_extraction):
        pass
