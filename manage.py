from flask_script import Manager

from app import app

if __name__ == '__main__':
    manager = Manager(app)

    @manager.command
    def runserver():
        app.run(debug=True, host='0.0.0.0')

    manager.run()

