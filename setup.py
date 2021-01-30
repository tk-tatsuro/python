from flaskPj import create_app
from flask import Flask, request, render_template, redirect

app = create_app()


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)

