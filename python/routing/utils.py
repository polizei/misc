# encoding: utf-8
# vim: ts=4 noexpandtab

def singleton(klass):
    instances = {}

    def get_instance():
        if not klass in instances:
            instances[klass] = klass()

        return instances[klass]

    return get_instance
