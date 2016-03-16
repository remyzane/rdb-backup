
class Processor():
    pass


class Mysql(Processor):
    pass


class Postgres(Processor):
    pass


processor_classes = {
    'mysql': Mysql,
    'postgresql': Postgres
}
