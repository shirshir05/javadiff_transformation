import os


def java_by_env_var(env_var):
    return os.path.join(os.environ[env_var], os.path.normpath('bin/java.exe'))


def get_java_exe_by_version(version):
    java_home = list(filter(lambda x: 'java_home' in x.lower(), os.environ.keys()))
    java_home_version = list(filter(lambda x: f'_{version}_' in x.lower(), java_home))
    if java_home_version:
        return java_by_env_var(java_home_version[0])
    if java_home:
        return java_by_env_var('JAVA_HOME')
    return 'java'
