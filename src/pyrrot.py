import argparse

from _pyrrot.main import create_app


def _create_args():
    parser = argparse.ArgumentParser(description='Foo')
    parser.add_argument('-p', '--port', help='The port of the pyrrot. Defaults to 1234', type=int, default=1234)
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-c', '--conf', help='Directory path to read configurations', required=True)
    return parser.parse_args()


def main(developer_mode=False):
    conf = '../examples'
    port = 1234
    if not developer_mode:
        args = _create_args()
        conf = args.conf
        port = args.port
    app = create_app(debug=True, configuration=conf)
    app.run(port=port)


if __name__ == "__main__":
    main(developer_mode=True)
