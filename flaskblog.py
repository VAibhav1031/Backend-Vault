from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "df81e3d4e2916edb1677ad7854d6f84e"
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


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", title="Login", form=form)


if __name__ == "__main__":
    app.run(debug=True)
