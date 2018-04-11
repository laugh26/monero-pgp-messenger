#!/usr/bin/env python3
#-*-coding:utf-8-*-
import api
from flask import Flask, render_template


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.dev')

    app.register_blueprint(api.create_blueprint(), url_prefix='/api/')

    @app.route('/')
    def home():
        return render_template('home.html')

    return app


if __name__ == '__main__':
    create_app().run()
