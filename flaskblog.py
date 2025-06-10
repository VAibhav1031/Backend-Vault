from flask import Flask, render_template, url_for

app = Flask(__name__)

posts = [
    {
        "author": "Vaibhav Tiwari",
        "title": "Blog Post 1",
        "content": "First Post content",
        "date_posted": "April 21, 2025",
    },
    {
        "author": "Corey scaffer",
        "title": "Blog Post 2",
        "content": "Second Post content",
        "date_posted": "May 5, 2025",
    },
]


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


if __name__ == "__main__":
    app.run(debug=True)
