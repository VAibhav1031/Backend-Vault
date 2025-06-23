import json
from flaskblog import app, db
from flaskblog.models import Post


def load_all_post(file_path):
    with open(file_path, "r") as f:
        posts = json.load(f)

    with app.app_context():
        for p in posts:
            post = Post(title=p["title"], content=p["content"], user_id=p["user_id"])
            db.session.add(post)

        db.session.commit()
        print(f"{len(posts)} added!!")


if __name__ == "__main__":
    load_all_post("flaskblog/static/posts.json")
