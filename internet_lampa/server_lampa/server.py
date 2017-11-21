from tornado import web, ioloop, options
import handlers
import os

class App(web.Application):
    def __init__(self):
        h = [
            (r"/mobile", handlers.MobileClient),
            (r"/controller", handlers.ControllerClient),
        ]
        settings = {
            'cookie_secret': '__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__',
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'login_url': '/login',
            'xsrf_cookies': True,
            'debug': True,
            'autoreload': True,
            'server_traceback': True,
        }
        super(App, self).__init__(handlers=h, **settings)

def main():
    #options.parse_command_line()
    app = App()
    app.listen(8888)
    ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
